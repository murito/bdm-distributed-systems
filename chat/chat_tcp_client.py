import socket
import ssl
import threading
import pickle
import struct
import os
import uuid
import time
from PySide6.QtCore import QObject, Signal
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta

CERTFILE = "client.crt"
KEYFILE = "client.key"
CHUNK_SIZE = 16 * 1024  # 16 KB
DOWNLOADS_DIR = os.path.join(os.getcwd(), "downloads")
CHUNK_SEND_RETRIES = 3
CHUNK_SEND_RETRY_DELAY = 0.05  # segundos entre reintentos
CHUNK_SEND_PAUSE = 0.001  # pequeña pausa entre chunks para aliviar buffers

# Diccionario local por cliente
receiving_files = {}

def generate_self_signed_cert(certfile, keyfile):
    if os.path.exists(certfile) and os.path.exists(keyfile):
        return
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with open(keyfile, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"MX"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Estado"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Ciudad"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"MiCliente"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
    ])
    cert = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer)\
        .public_key(key.public_key()).serial_number(x509.random_serial_number())\
        .not_valid_before(datetime.utcnow()).not_valid_after(datetime.utcnow() + timedelta(days=365))\
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)\
        .sign(key, hashes.SHA256())
    with open(certfile, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


def send_msg(conn, obj):
    data = pickle.dumps(obj)
    length = struct.pack(">I", len(data))
    conn.sendall(length + data)


def recvall(conn, n):
    data = b""
    while len(data) < n:
        try:
            packet = conn.recv(n - len(data))
        except ssl.SSLWantReadError:
            continue
        except ssl.SSLError as e:
            print("SSL error en recv (cliente):", e)
            return None
        except Exception as e:
            print("Error en recv (cliente):", e)
            return None
        if not packet:
            return None
        data += packet
    return data


def recv_msg(conn):
    raw_len = recvall(conn, 4)
    if not raw_len:
        return None
    msg_len = struct.unpack(">I", raw_len)[0]
    data = recvall(conn, msg_len)
    if data is None:
        return None
    return pickle.loads(data)


class ChatTCPClient(QObject):
    connected = Signal()
    disconnected = Signal()
    error = Signal(str)
    users_updated = Signal(list)
    message_received = Signal(dict)
    group_message_received = Signal(dict)
    file_received = Signal(dict)  # when file completed (metadata)
    file_transfer_update = Signal(dict)  # generic: started/progress/completed/file_chunk
    added_to_group = Signal(dict)
    group_created = Signal(dict)

    def __init__(self, username, avatar=b"", host="127.0.0.1", port=8080):
        super().__init__()
        self.username = username
        self.avatar = avatar
        self.host = host
        self.port = port
        self.conn = None
        self.user_id = None
        self.groups = {}  # group_id -> {"name":, "users": []}

        # uploads in flight: client_tag -> {"path":..., "filesize": ..., "file_id": None or str, "lock":Lock, "aborted":bool}
        self.pending_uploads = {}

        # receiving files: file_id -> {"filename":, "path":, "bytes": int, "total": int, "initiator": id}
        self.receiving_files = {}  # file_id -> ReceivingFile

        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        generate_self_signed_cert(CERTFILE, KEYFILE)

    def connect_to_server(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            context.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE)
            self.conn = context.wrap_socket(sock, server_hostname=self.host)
            self.conn.connect((self.host, self.port))

            send_msg(self.conn, {"type": "register", "username": self.username, "avatar": self.avatar})

            msg = recv_msg(self.conn)
            if msg and msg.get("type") == "id_assigned":
                self.user_id = msg["id"]
                print(f"ID asignado por servidor: {self.user_id}")

            threading.Thread(target=self.listen_server, daemon=True).start()
            self.connected.emit()
        except Exception as e:
            self.error.emit(str(e))

    def listen_server(self):
        try:
            while True:
                msg = recv_msg(self.conn)
                if not msg:
                    break
                mtype = msg.get("type")

                # --- Usuarios y chats ---
                if mtype == "users":
                    self.users_updated.emit(msg["users"])
                elif mtype == "chat":
                    self.message_received.emit(msg)
                elif mtype == "group_chat":
                    self.group_message_received.emit(msg)

                # --- Manejo seguro de archivos ---
                elif mtype == "file_started":
                    file_id = msg.get("file_id")
                    filename = msg.get("filename")
                    filesize = msg.get("filesize", 0)
                    initiator = msg.get("initiator")
                    client_tag = msg.get("client_tag")

                    # ✅ El SENDER no crea archivo (ya lo tiene)
                    if initiator == self.user_id:
                        print(f"[CLIENT {self.user_id}] Soy quien envía → NO crear archivo local ({filename})")
                    else:
                        # ✅ Guardar descargas por usuario
                        user_folder = os.path.join("Downloads", self.user_id)
                        os.makedirs(user_folder, exist_ok=True)

                        rf = ReceivingFile(file_id, filename, filesize, initiator, base_folder=user_folder)
                        self.receiving_files[file_id] = rf
                        print(f"[CLIENT {self.user_id}] Guardando en: {rf.path}")

                    # Solo el initiator original dispara el worker de subida
                    if client_tag and client_tag in self.pending_uploads:
                        pu = self.pending_uploads[client_tag]
                        with pu["lock"]:
                            pu["file_id"] = file_id
                            # ❌ Antes se lanzaba en todos los clientes
                            # ✅ Ahora solo el initiator lo sube
                            if not pu.get("uploader_running") and self.user_id == initiator:
                                pu["uploader_running"] = True
                                threading.Thread(target=self._upload_file_worker, args=(client_tag, file_id), daemon=True).start()

                    self.file_transfer_update.emit(msg)

                elif mtype == "file_chunk":
                    file_id = msg.get("file_id")
                    chunk = msg.get("data")
                    initiator = msg.get("initiator")
                    sender = msg.get("sender")
                    seq = msg.get("seq", None)

                    if not file_id or not chunk:
                        continue

                    # ✅ Ignorar si soy el que envía el archivo
                    if initiator == self.user_id:
                        continue

                    if file_id not in self.receiving_files:
                        filename = msg.get("filename", f"{file_id}_file")
                        self.receiving_files[file_id] = ReceivingFile(file_id, filename, None, initiator)

                    rf = self.receiving_files[file_id]
                    written = rf.write_chunk(chunk, seq)

                    # opcional: log detallado para debug (descomentar si necesitas trazas)
                    # print(f"[CLIENT {self.user_id}] recv chunk file={file_id} seq={seq} written={written} total_written={rf.bytes_received}")

                    self.file_transfer_update.emit({
                        "type": "file_chunk",
                        "file_id": file_id,
                        "bytes_received": rf.bytes_received,
                        "filename": rf.filename,
                        "initiator": initiator
                    })

                elif mtype == "file_progress":
                    # Solo actualizar progreso, NO escribir
                    file_id = msg.get("file_id")
                    if file_id in self.receiving_files:
                        rf = self.receiving_files[file_id]
                        rf.total = msg.get("total_bytes", rf.total)
                        rf.bytes_received = msg.get("bytes_transferred", rf.bytes_received)
                    self.file_transfer_update.emit(msg)

                elif mtype == "file_completed":
                    file_id = msg.get("file_id")
                    if file_id in self.receiving_files:
                        rf = self.receiving_files[file_id]

                        completed_evt = {
                            "type": "file_completed",
                            "file_id": file_id,
                            "filename": rf.filename,
                            "local_path": rf.path  # ✅ aseguramos ruta local correcta
                        }

                        # ✅ Esto actualiza la UI para cambiar a estado de completado
                        self.file_transfer_update.emit(completed_evt)

                        # ✅ Esto permite al usuario hacer click para abrir carpeta/archivo
                        self.file_received.emit(completed_evt)

                        # ✅ Eliminamos el registro ya que terminó correctamente
                        del self.receiving_files[file_id]

                # --- Grupos ---
                elif mtype == "group_created":
                    self.group_created.emit(msg)
                elif mtype == "added_to_group":
                    self.groups[msg["group_id"]] = {"name": msg["group_name"], "users": msg.get("users", [])}
                    self.added_to_group.emit(msg)

        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.disconnected.emit()
            try:
                if self.conn:
                    self.conn.close()
            except:
                pass


    # --- Envíos ---
    def send_chat(self, to_id, text):
        if self.conn:
            send_msg(self.conn, {"type": "chat", "to": to_id, "msg": text})

    def send_group_chat(self, group_id, text):
        if self.conn:
            send_msg(self.conn, {"type": "group_chat", "group_id": group_id, "msg": text})

    def send_file(self, target_id=None, group_id=None, file_path=None):
        """
        Inicia el envío: manda file_init con client_tag y guarda pending_uploads[client_tag] = ...
        Además emite un evento local 'file_started' (con client_tag) para que la UI cree la burbuja
        temporal. El uploader comenzará cuando llegue el file_started del servidor con file_id.
        """
        if not self.conn or not file_path or not os.path.exists(file_path):
            return

        filesize = os.path.getsize(file_path)
        client_tag = uuid.uuid4().hex
        lock = threading.Lock()
        self.pending_uploads[client_tag] = {"path": file_path, "filesize": filesize, "file_id": None, "lock": lock, "uploading": False, "aborted": False}

        init_msg = {
            "type": "file_init",
            "client_tag": client_tag,
            "filename": os.path.basename(file_path),
            "filesize": filesize,
            "to": target_id,
            "group_id": group_id
        }
        # send the init to server
        send_msg(self.conn, init_msg)

        # Emit local file_started so UI can create a temporary bubble keyed by client_tag.
        local_started = {
            "type": "file_started",
            "file_id": None,
            "client_tag": client_tag,
            "initiator": self.user_id,
            "filename": os.path.basename(file_path),
            "filesize": filesize,
            "targets": [] if not group_id else [],  # UI can update when server responds with targets
            "group_id": group_id,
            "to": target_id
        }
        self.file_transfer_update.emit(local_started)

    def _upload_file_worker(self, client_tag, file_id):
        """Lee el archivo en chunks y los envía referenciando file_id, con seq por chunk."""
        pu = self.pending_uploads.get(client_tag)
        if not pu:
            return
        # ensure single uploader per pending_upload
        with pu["lock"]:
            if pu.get("aborted") or pu.get("uploader_running") is False:
                return
            pu["uploader_running"] = True

        path = pu["path"]
        filesize = pu["filesize"]
        bytes_sent = 0
        seq = 0
        try:
            with open(path, "rb") as f:
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break

                    msg = {"type": "file_chunk", "file_id": file_id, "data": chunk, "seq": seq}

                    sent_ok = False
                    last_exc = None
                    for attempt in range(CHUNK_SEND_RETRIES):
                        try:
                            send_msg(self.conn, msg)
                            sent_ok = True
                            bytes_sent += len(chunk)
                            break
                        except Exception as e:
                            last_exc = e
                            time.sleep(CHUNK_SEND_RETRY_DELAY)
                    if not sent_ok:
                        self.error.emit(f"Error enviando chunk (client_tag={client_tag}): {last_exc}")
                        with pu["lock"]:
                            pu["aborted"] = True
                        break

                    seq += 1
                    time.sleep(CHUNK_SEND_PAUSE)

        except Exception as e:
            self.error.emit(f"Error leyendo/abriendo archivo para enviar: {e}")
        finally:
            # cleanup
            try:
                with pu["lock"]:
                    pu["uploader_running"] = False
            except:
                pass
            try:
                time.sleep(0.05)
            except:
                pass
            try:
                self.pending_uploads.pop(client_tag, None)
            except:
                pass

    def create_group(self, group_name, user_ids):
        """Envía la solicitud de creación de grupo al servidor."""
        if self.conn:
            send_msg(self.conn, {
                "type": "create_group",
                "group": group_name,
                "users": user_ids
            })




# --------------------------
# Manejo seguro de archivos
# --------------------------
class ReceivingFile:
    """Gestión de una descarga de archivo por file_id"""
    def __init__(self, file_id, filename, total, initiator, base_folder=DOWNLOADS_DIR):
        self.file_id = file_id
        self.filename = filename
        self.total = total  # tamaño total esperado
        self.initiator = initiator
        self.path = os.path.join(base_folder, f"{file_id}_{filename}")
        self.bytes_received = 0
        self.lock = threading.Lock()
        self.seen_seqs = set()  # para evitar escribir dos veces el mismo chunk

        # crear archivo vacío al iniciar
        with open(self.path, "wb") as f:
            pass

    def write_chunk(self, chunk, seq=None):
        with self.lock:
            # si viene seq y ya lo vimos, ignoramos
            if seq is not None:
                if seq in self.seen_seqs:
                    return 0
                self.seen_seqs.add(seq)

            bytes_remaining = self.total - self.bytes_received if self.total is not None else None
            to_write = chunk if bytes_remaining is None else chunk[:bytes_remaining]
            if not to_write:
                return 0
            with open(self.path, "ab") as f:
                f.write(to_write)
            self.bytes_received += len(to_write)
            return len(to_write)

    def is_complete(self):
        return self.total is not None and self.bytes_received >= self.total

