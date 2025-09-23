"""
Sep 19, 2025
Francisco Javier Alcalá Olivares
--------------------------------------
TCP server
"""
import socket

class TCPServer:
    def __init__(self, port):
        print("\n:::TCP SERVER:::\n")
        # Set flag to await for a message
        self.listening = True
        self.port = port
        # Initialize a socket for IPv4 (AF_INET) and protocol TCP (SOCK_STREAM)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def listen(self):
        # Listen on localhost and port
        self.sock.bind(('127.0.0.1', self.port))
        self.sock.listen(1)
        print("Server up and listening on port {}".format(self.port))

        # Await to receive a message
        while self.listening:
            # for TCP, we need to accept connections
            conn, addr = self.sock.accept()

            # Get data from connected client instead of the socket itself
            data = conn.recv(1024)

            if len(data) > 0:
                print("\nReceived: {}".format(data.decode()))
                print("\nFrom: {}".format(addr))
                print("\nBye.")
                conn.close()

if __name__ == '__main__':
    server = TCPServer(8080)
    server.listen()
