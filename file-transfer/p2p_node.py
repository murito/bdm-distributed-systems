"""
Sep 20, 2025
Francisco Javier Alcalá Olivares
--------------------------------------
P2P Node (mejorado con buffer para mensajes completos)
"""
import datetime
import socket
import threading

# Pool for active connections
peers = []

def get_date():
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%a, %d %b %Y %H:%M:%S %Z")

# ------------------------------------------
# Maneja cada conexión (lector con buffer)
# ------------------------------------------
def handle_client(conn, addr, on_message=None):
    print(f"[+] Connected with: {addr}")
    buffer = ""  # Almacena datos incompletos

    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break

            # Decodificar y agregar al buffer
            buffer += data.decode(errors="ignore")

            # Procesar todos los mensajes completos (terminados en '\n')
            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                message = message.strip()
                if message and on_message:
                    try:
                        on_message(message)
                    except Exception as e:
                        print(f"[Error en on_message]: {e}")
                        on_message("Error al recibir el mensaje")

        except ConnectionResetError:
            print(f"[!] Connection reset by {addr}")
            break
        except Exception as e:
            print(f"[!] Error con {addr}: {e}")
            break

    print(f"[-] Disconnected from: {addr}")
    if conn in peers:
        peers.remove(conn)
    conn.close()

# ------------------------------------------
# Servidor principal
# ------------------------------------------
def start_server(port, on_message=None):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', int(port)))
    server.listen()

    print(f"[Server] Listening on 127.0.0.1:{port}")

    while True:
        conn, addr = server.accept()
        peers.append(conn)
        thread = threading.Thread(target=handle_client, args=(conn, addr, on_message), daemon=True)
        thread.start()

# ------------------------------------------
# Cliente (conecta a otro nodo)
# ------------------------------------------
def connect_to_peer(peer_ip, peer_port, on_message=None):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((peer_ip, peer_port))
        peers.append(client)
        print(f"[Client] Connected to {peer_ip}:{peer_port}")

        thread = threading.Thread(target=handle_client, args=(client, (peer_ip, peer_port), on_message), daemon=True)
        thread.start()
    except Exception as e:
        print(f"[Error] No se pudo conectar a {peer_ip}:{peer_port} - {e}")

# ------------------------------------------
# Envía mensaje a todos los nodos conectados
# ------------------------------------------
def broadcast_message(message):
    """
    Envía el mensaje a todos los peers activos.
    Se agrega un '\n' como delimitador para que el receptor pueda separar los mensajes.
    """
    clean_message = message.strip() + "\n"
    for peer in peers:
        try:
            peer.sendall(clean_message.encode())
        except Exception as e:
            print(f"[Error enviando mensaje]: {e}")
