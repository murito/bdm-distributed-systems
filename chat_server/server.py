# server_fixed.py  -- reemplaza tu server actual por este archivo
import os
import socket
import ssl
import threading
import pickle
import struct
import uuid
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta

HOST = '0.0.0.0'
PORT = 8080
CERTFILE = 'server.crt'
KEYFILE = 'server.key'

clients = {}   # user_id -> {"username":, "conn":, "avatar":}
client_locks = {}  # user_id -> threading.Lock()
groups = {}    # group_id -> {"name":, "users": set()}
# file_transfers maps upload_file_id -> metadata:
# {
#   "initiator": user_id,
#   "total": int,
#   "bytes": int,
#   "targets": { target_uid: download_file_id, ... },
#   "filename": str,
#   "lock": threading.Lock()
# }
file_transfers = {}
lock = threading.Lock()


def generate_self_signed_cert(certfile, keyfile):
    if os.path.exists(certfile) and os.path.exists(keyfile):
        return
    print("Generando certificado autofirmado del servidor...")
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with open(keyfile, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"MX"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Jalisco"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Guadalajara"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"NopalTech"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
    ])
    cert = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer)\
        .public_key(key.public_key()).serial_number(x509.random_serial_number())\
        .not_valid_before(datetime.utcnow()).not_valid_after(datetime.utcnow() + timedelta(days=365))\
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)\
        .sign(key, hashes.SHA256())
    with open(certfile, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    print("Certificado servidor generado.")


def send_msg(conn, obj):
    try:
        data = pickle.dumps(obj)
        length = struct.pack('>I', len(data))
        conn.sendall(length + data)
    except Exception as e:
        print("send_msg fallo (cliente posiblemente desconectado):", e)


def safe_send(uid, obj):
    try:
        with lock:
            client_entry = clients.get(uid)
        if not client_entry:
            return False
        conn = client_entry["conn"]

        cl = client_locks.get(uid)
        if cl is None:
            with lock:
                cl = client_locks.get(uid)
                if cl is None:
                    cl = threading.Lock()
                    client_locks[uid] = cl

        with cl:
            data = pickle.dumps(obj)
            length = struct.pack('>I', len(data))
            conn.sendall(length + data)
        return True
    except Exception as e:
        print(f"safe_send fallo a {uid}: {e}")
        return False


def recvall(conn, n):
    data = b''
    while len(data) < n:
        try:
            packet = conn.recv(n - len(data))
        except ssl.SSLWantReadError:
            continue
        except ssl.SSLError as e:
            print("SSL error en recv:", e)
            return None
        except Exception as e:
            print("Error en recv:", e)
            return None
        if not packet:
            return None
        data += packet
    return data


def recv_msg(conn):
    raw_len = recvall(conn, 4)
    if not raw_len:
        return None
    msg_len = struct.unpack('>I', raw_len)[0]
    data = recvall(conn, msg_len)
    if data is None:
        return None
    return pickle.loads(data)


def broadcast(message, exclude_id=None, targets=None):
    with lock:
        if targets is not None:
            uids = [uid for uid in targets if uid in clients]
        else:
            uids = [uid for uid in clients.keys() if uid != exclude_id]

    dead = []
    for uid in uids:
        ok = safe_send(uid, message)
        if not ok:
            dead.append(uid)

    if dead:
        with lock:
            for uid in dead:
                try:
                    c = clients.get(uid)
                    if c and c.get("conn"):
                        try:
                            c["conn"].close()
                        except:
                            pass
                except:
                    pass
                clients.pop(uid, None)
                client_locks.pop(uid, None)


def handle_client(conn, addr):
    user_id = None
    username = "?"
    try:
        reg_info = recv_msg(conn)
        if not reg_info or reg_info.get("type") != "register":
            conn.close()
            return

        username = reg_info["username"]
        avatar = reg_info.get("avatar", b"")
        user_id = str(uuid.uuid4())

        with lock:
            clients[user_id] = {"username": username, "conn": conn, "avatar": avatar}
            client_locks[user_id] = threading.Lock()

        send_msg(conn, {"type": "id_assigned", "id": user_id})

        print(f"{username} ({user_id}) conectado desde {addr}")

        broadcast({
            "type": "users",
            "users": [{"id": uid, "username": v["username"], "avatar": v["avatar"]}
                      for uid, v in clients.items()]
        })

        while True:
            msg = recv_msg(conn)
            if not msg:
                break

            mtype = msg.get("type")

            if mtype == "chat":
                target_id = msg.get("to")
                if target_id in clients:
                    ok = safe_send(target_id, {
                        "type": "chat",
                        "from": user_id,
                        "username": username,
                        "avatar": avatar,
                        "msg": msg["msg"]
                    })
                    if not ok:
                        print(f"Error enviando chat a {target_id}, limpiando.")
                        with lock:
                            try:
                                clients[target_id]["conn"].close()
                            except:
                                pass
                            clients.pop(target_id, None)
                            client_locks.pop(target_target_id, None)

            elif mtype == "group_chat":
                group_id = msg.get("group_id")
                if group_id in groups:
                    targets = [uid for uid in groups[group_id]["users"] if uid != user_id and uid in clients]
                    broadcast({
                        "type": "group_chat",
                        "from": user_id,
                        "username": username,
                        "avatar": avatar,
                        "group_id": group_id,
                        "group_name": groups[group_id]["name"],
                        "msg": msg["msg"]
                    }, exclude_id=user_id, targets=targets)

            elif mtype == "create_group":
                group_name = msg.get("group")
                users = set(msg.get("users", []))
                group_id = str(uuid.uuid4())

                with lock:
                    groups[group_id] = {"name": group_name, "users": users}

                print(f"📢 Grupo '{group_name}' ({group_id}) creado con usuarios: {users}")

                dead_notify = []
                for uid in users:
                    if uid in clients:
                        ok = safe_send(uid, {
                            "type": "added_to_group",
                            "group_id": group_id,
                            "group_name": group_name,
                            "users": list(users)
                        })
                        if not ok:
                            print(f"Error notificando added_to_group a {uid}")
                            dead_notify.append(uid)

                dead_notify_sender = []
                for uid in groups[group_id]["users"]:
                    if uid in clients:
                        ok = safe_send(uid, {
                            "type": "group_created",
                            "group_id": group_id,
                            "group_name": group_name,
                            "users": list(users)
                        })
                        if not ok:
                            print(f"Error notificando group_created a {uid}")
                            dead_notify_sender.append(uid)

                any_dead = dead_notify + dead_notify_sender
                if any_dead:
                    with lock:
                        for uid in any_dead:
                            try:
                                c = clients.get(uid)
                                if c and c.get("conn"):
                                    try:
                                        c["conn"].close()
                                    except:
                                        pass
                            except:
                                pass
                            clients.pop(uid, None)
                            client_locks.pop(uid, None)


            # --- Inicio de envío de archivo ---
            elif mtype == "file_init":
                client_tag = msg.get("client_tag")
                filename = msg.get("filename")
                filesize = msg.get("filesize", 0)
                to = msg.get("to")
                group_id = msg.get("group_id")
                initiator = user_id

                # determinar targets
                targets = set()
                if group_id and group_id in groups:
                    targets = set([uid for uid in groups[group_id]["users"] if uid in clients])
                elif to and to in clients:
                    targets = {to}

                # quitar al initiador de targets (no enviarle chunks a sí mismo)
                targets.discard(initiator)

                # upload_id: id que el initiator usará para subir
                upload_id = str(uuid.uuid4())

                # crear download ids por cada receptor
                targets_map = {}  # uid -> download_file_id
                for uid in targets:
                    targets_map[uid] = str(uuid.uuid4())

                with lock:
                    file_transfers[upload_id] = {
                        "initiator": initiator,
                        "total": filesize,
                        "bytes": 0,
                        "targets": targets_map.copy(),  # mapping uid -> download_id
                        "filename": filename,
                        "lock": threading.Lock()
                    }

                # Enviar file_started al initiator con upload_id (así inicia upload)
                if initiator in clients:
                    send_msg(clients[initiator]["conn"], {
                        "type": "file_started",
                        "file_id": upload_id,
                        "client_tag": client_tag,
                        "initiator": initiator,
                        "filename": filename,
                        "filesize": filesize,
                        "targets": list(targets),
                        "group_id": group_id,
                        "to": to
                    })

                # Enviar file_started a cada receptor con su download_id
                dead_targets = []
                for uid, download_id in targets_map.items():
                    if uid in clients:
                        info = {
                            "type": "file_started",
                            "file_id": download_id,
                            "client_tag": None,
                            "initiator": initiator,
                            "filename": filename,
                            "filesize": filesize,
                            "targets": [],  # receptor no necesita la lista completa (puede ignorar)
                            "group_id": group_id,
                            "to": to,
                            # opcional: incluir upload_id si quieres (no es necesario)
                            "upload_id": upload_id
                        }
                        if not safe_send(uid, info):
                            dead_targets.append(uid)

                # limpiar targets muertos
                if dead_targets:
                    with lock:
                        for uid in dead_targets:
                            try:
                                clients[uid]["conn"].close()
                            except:
                                pass
                            clients.pop(uid, None)
                            # quitar de la map
                            file_transfers[upload_id]["targets"].pop(uid, None)


            # --- Reenvío de chunks ---
            elif mtype == "file_chunk":
                file_id = msg.get("file_id")  # this is expected to be upload_id
                chunk = msg.get("data")
                if not file_id or file_id not in file_transfers:
                    continue

                ft = file_transfers[file_id]

                sender = user_id  # quien envía este chunk

                # Seguridad: solo el initiator puede subir chunks (upload_id owner)
                if sender != ft["initiator"]:
                    # debug log para ver intentos inválidos
                    print(f"[SERVER] Ignorando chunk de {sender} para {file_id} (solo initiator puede enviar)")
                    continue

                # actualizamos bytes basados en upload
                with ft["lock"]:
                    ft["bytes"] += len(chunk)
                    transferred = ft["bytes"]
                    total = ft["total"]
                    filename = ft["filename"]

                # reenviar a cada receptor, usando su download_id (no el upload_id)
                forward_msg_template = {
                    "type": "file_chunk",
                    "data": chunk,
                    "filename": filename,
                    "initiator": ft["initiator"],
                    "sender": sender
                }

                dead = []
                # snapshot targets items
                targets_items = list(ft["targets"].items())  # list of (uid, download_id)
                for uid, download_id in targets_items:
                    if uid in clients:
                        forward_msg = forward_msg_template.copy()
                        forward_msg["file_id"] = download_id
                        # enviar
                        if not safe_send(uid, forward_msg):
                            dead.append(uid)
                    else:
                        dead.append(uid)

                # progreso: enviarlo a cada receptor con su download_id y también al initiator (upload_id)
                for uid, download_id in targets_items:
                    if uid in clients:
                        progress_msg = {
                            "type": "file_progress",
                            "file_id": download_id,
                            "bytes_transferred": transferred,
                            "total_bytes": total
                        }
                        safe_send(uid, progress_msg)

                # enviar progreso al initiator también (usa upload_id)
                if ft["initiator"] in clients:
                    progress_msg_initiator = {
                        "type": "file_progress",
                        "file_id": file_id,
                        "bytes_transferred": transferred,
                        "total_bytes": total
                    }
                    safe_send(ft["initiator"], progress_msg_initiator)

                # limpieza de targets muertos
                if dead:
                    with lock:
                        for uid in dead:
                            try:
                                clients[uid]["conn"].close()
                            except:
                                pass
                            clients.pop(uid, None)
                            ft["targets"].pop(uid, None)

                # completado: notificar a cada receptor usando su download_id
                if transferred >= total:
                    complete_msg_template = {
                        "type": "file_completed",
                        "filename": filename
                    }
                    for uid, download_id in list(ft["targets"].items()):
                        if uid in clients:
                            cm = {"type": "file_completed", "file_id": download_id, "filename": filename}
                            safe_send(uid, cm)
                    # notificar initiator (upload_id)
                    if ft["initiator"] in clients:
                        safe_send(ft["initiator"], {"type": "file_completed", "file_id": file_id, "filename": filename})
                    with lock:
                        # borrar transferencia
                        if file_id in file_transfers:
                            del file_transfers[file_id]

    except Exception as e:
        print(f"Error cliente {addr}: {e}")
    finally:
        if user_id:
            with lock:
                if user_id in clients:
                    del clients[user_id]
                client_locks.pop(user_id, None)
            broadcast({
                "type": "users",
                "users": [{"id": uid, "username": v["username"], "avatar": v["avatar"]}
                          for uid, v in clients.items()]
            })
        try:
            conn.close()
        except:
            pass
        print(f"{username} ({user_id}) desconectó")


def main():
    generate_self_signed_cert(CERTFILE, KEYFILE)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"Servidor escuchando en {HOST}:{PORT}")

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE)

    try:
        while True:
            conn, addr = sock.accept()
            secure_conn = context.wrap_socket(conn, server_side=True)
            threading.Thread(target=handle_client, args=(secure_conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("Servidor detenido")


if __name__ == "__main__":
    main()
