import socket
import ssl
import threading
import pickle
import struct
import os
from PySide6.QtCore import QObject, Signal
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta

CERTFILE = "client.crt"
KEYFILE = "client.key"


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
        packet = conn.recv(n - len(data))
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
    return pickle.loads(data)


class ChatTCPClient(QObject):
    connected = Signal()
    disconnected = Signal()
    error = Signal(str)
    users_updated = Signal(list)
    message_received = Signal(dict)
    group_message_received = Signal(dict)
    file_received = Signal(dict)
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
                if mtype == "users":
                    self.users_updated.emit(msg["users"])
                elif mtype == "chat":
                    self.message_received.emit(msg)
                elif mtype == "group_chat":
                    self.group_message_received.emit(msg)
                elif mtype == "file":
                    self.file_received.emit(msg)
                elif mtype == "group_created":  # 🔹 nuevo tipo de mensaje
                    self.group_created.emit(msg)
                elif mtype == "added_to_group":
                    group_id = msg["group_id"]
                    group_name = msg["group_name"]
                    self.groups[group_id] = {"name": group_name, "users": msg["users"]}
                    print(f"📢 Añadido al grupo: {group_name} ({group_id})")
                    self.added_to_group.emit(msg)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.disconnected.emit()
            if self.conn:
                self.conn.close()


    # --- Envíos ---
    def send_chat(self, to_id, text):
        if self.conn:
            send_msg(self.conn, {"type": "chat", "to": to_id, "msg": text})

    def send_group_chat(self, group_id, text):
        if self.conn:
            send_msg(self.conn, {"type": "group_chat", "group_id": group_id, "msg": text})

    def send_file(self, to_id, filename, data):
        if self.conn:
            send_msg(self.conn, {"type": "file", "to": to_id, "filename": filename, "data": data})

    def create_group(self, group_name, user_ids):
        """Envía la solicitud de creación de grupo al servidor."""
        if self.conn:
            send_msg(self.conn, {
                "type": "create_group",
                "group": group_name,
                "users": user_ids
            })

