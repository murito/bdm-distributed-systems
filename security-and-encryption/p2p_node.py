"""
Sep 20, 2025
Francisco Javier Alcalá Olivares
--------------------------------------
P2P Node
"""
import datetime
import socket
import threading

import os
import base64
from hashlib import sha256
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

ENCRYPTION_KEY = "HolaMundoEncryption"

# ----------------- Función AES-256 -----------------
def encrypt_aes256(text: str, key) -> str:
    """Encripta texto con AES-256 (CBC). Devuelve Base64 con IV + datos."""
    if isinstance(key, str):
        key_bytes = sha256(key.encode('utf-8')).digest()
    else:
        key_bytes = sha256(key).digest()

    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(text.encode('utf-8')) + padder.finalize()

    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return base64.b64encode(iv + encrypted_data).decode('utf-8')


def decrypt_aes256(encrypted_b64: str, key) -> str:
    """Desencripta texto en Base64 generado por encrypt_aes256."""
    if isinstance(key, str):
        key_bytes = sha256(key.encode('utf-8')).digest()
    else:
        key_bytes = sha256(key).digest()

    # Decodificar base64
    encrypted_data = base64.b64decode(encrypted_b64)

    # Separar IV y datos cifrados
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    # Desencriptar
    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # Quitar padding
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    return plaintext.decode('utf-8')


# Pool for active connections
peers = []

def get_date():
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%a, %d %b %Y %H:%M:%S %Z")

# Manage client connections
def handle_client(conn, addr, on_message=None):
    print(f"[+] Connected with: {addr}")

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break


            RECEIVED_MESSAGE = data.decode()
            if on_message:
                try:
                    on_message(RECEIVED_MESSAGE)
                except Exception:
                    on_message("Error al recibir el mensaje")

            # console log
            print(f"[{get_date()} - {addr}]: {RECEIVED_MESSAGE}")
        except:
            break

    print(f"[-] Disconnected from: {addr}")
    peers.remove(conn)
    conn.close()

# Start main server
def start_server( port, on_message=None ):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', int(port)))
    server.listen()

    print(f"[Server] Listening on 127.0.0.1:{port}")

    while True:
        conn, addr = server.accept()
        peers.append(conn)

        # Start a thread to keep this connection without bocking the main thread
        thread = threading.Thread(target=handle_client, args=(conn, addr, on_message))
        thread.start()

# Client connect to another P2P node
def connect_to_peer(peer_ip, peer_port, on_message=None):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((peer_ip, peer_port))
        peers.append(client)
        print(f"[Client] Connected to {peer_ip}:{peer_port}")

        # Start a thread to keep this connection without bocking the main thread
        thread = threading.Thread(target=handle_client, args=(client, (peer_ip, peer_port), on_message))
        thread.start()
    except Exception as e:
        print(f"[Error] We can't connect to {peer_ip}:{peer_port} - {e}")

# Send message to all the connected nodes
def broadcast_message(message):
    for peer in peers:
        try:
            peer.sendall(message.encode())
        except:
            pass
