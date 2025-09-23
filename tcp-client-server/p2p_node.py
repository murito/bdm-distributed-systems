"""
Sep 20, 2025
Francisco Javier Alcalá Olivares
--------------------------------------
P2P Node
"""
import datetime
import socket
import threading

# Pool for active connections
peers = []

def get_date():
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%a, %d %b %Y %H:%M:%S %Z")

# Manage client connections
def handle_client(conn, addr):
    print(f"[+] Connected with: {addr}")

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            print(f"[{get_date()} - {addr}]: {data.decode()}")
        except:
            break

    print(f"[-] Disconnected from: {addr}")
    peers.remove(conn)
    conn.close()

# Start main server
def start_server():
    port = int(input("SELF PORT: "))

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', int(port)))
    server.listen()

    print(f"[Server] Listening on 127.0.0.1:{port}")

    while True:
        conn, addr = server.accept()
        peers.append(conn)

        # Start a thread to keep this connection without bocking the main thread
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

# Client connect to another P2P node
def connect_to_peer(peer_ip, peer_port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((peer_ip, peer_port))
        peers.append(client)
        print(f"[Client] Connected to {peer_ip}:{peer_port}")

        # Start a thread to keep this connection without bocking the main thread
        thread = threading.Thread(target=handle_client, args=(client, (peer_ip, peer_port)))
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

# Main thread
def main():
    # Start a server asking for the host port, in a single thread
    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()

    # Select a command to interact with the P2P main server
    while True:
        cmd = input("Type a command: (connect/send/exit): \n").strip()
        if cmd == "connect":
            ip = input("PEER IP: ")
            port = int(input("PEER PORT: "))
            connect_to_peer(ip, port)
        elif cmd == "send":
            msg = input("Message: ")
            broadcast_message(msg)
        elif cmd == "exit":
            print("Closing connections...")
            for peer in peers:
                peer.close()
            break

if __name__ == "__main__":
    main()