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
groups = {}    # group_id -> {"name":, "users": set()}
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
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Estado"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Ciudad"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Servidor"),
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
    data = pickle.dumps(obj)
    length = struct.pack('>I', len(data))
    conn.sendall(length + data)


def recvall(conn, n):
    data = b''
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
    msg_len = struct.unpack('>I', raw_len)[0]
    data = recvall(conn, msg_len)
    if data is None:
        return None
    return pickle.loads(data)


def broadcast(message, exclude_id=None, group_id=None):
    with lock:
        if group_id:
            targets = [clients[uid]["conn"] for uid in groups[group_id]["users"]
                       if uid != exclude_id and uid in clients]
        else:
            targets = [v["conn"] for uid, v in clients.items() if uid != exclude_id]

    for conn in targets:
        try:
            send_msg(conn, message)
        except:
            pass


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

        # assign id to the new user
        send_msg(conn, {"type": "id_assigned", "id": user_id})

        print(f"{username} ({user_id}) conectado desde {addr}")

        # notify others that a new ser has joined
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
                    send_msg(clients[target_id]["conn"], {
                        "type": "chat",
                        "from": user_id,
                        "username": username,
                        "avatar": avatar,
                        "msg": msg["msg"]
                    })

            elif mtype == "group_chat":
                print("Broadcast group chat...")
                group_id = msg.get("group_id")
                if group_id in groups:
                    broadcast({
                        "type": "group_chat",
                        "from": user_id,
                        "username": username,
                        "avatar": avatar,
                        "group_id": group_id,
                        "group_name": groups[group_id]["name"],
                        "msg": msg["msg"]
                    }, exclude_id=user_id, group_id=group_id)

            elif mtype == "create_group":
                group_name = msg.get("group")
                users = set(msg.get("users", []))
                group_id = str(uuid.uuid4())

                with lock:
                    groups[group_id] = {"name": group_name, "users": users}

                print(f"📢 Grupo '{group_name}' ({group_id}) creado con usuarios: {users}")

                # Notificar a los miembros
                for uid in users:
                    if uid in clients:
                        try:
                            send_msg(clients[uid]["conn"], {
                                "type": "added_to_group",
                                "group_id": group_id,
                                "group_name": group_name,
                                "users": list(users)
                            })
                        except:
                            pass

                # For the sender
                for uid in groups[group_id]["users"]:
                    if uid in clients:
                        try:
                            send_msg(clients[uid]["conn"], {
                                "type": "group_created",
                                "group_id": group_id,
                                "group_name": group_name,
                                "users": list(users)
                            })
                        except:
                            pass

    except Exception as e:
        print(f"Error cliente {addr}: {e}")
    finally:
        if user_id:
            with lock:
                if user_id in clients:
                    del clients[user_id]
            broadcast({
                "type": "users",
                "users": [{"id": uid, "username": v["username"], "avatar": v["avatar"]}
                          for uid, v in clients.items()]
            })
        conn.close()
        print(f"{username} ({user_id}) desconectó")


def main():
    generate_self_signed_cert(CERTFILE, KEYFILE)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
