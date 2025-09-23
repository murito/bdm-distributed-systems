"""
Sep 19, 2025
Francisco Javier Alcalá Olivares
--------------------------------------
TCP client
"""
import socket

class TCPClient:
    def __init__(self, port):
        print("\n:::TCP CLIENT:::\n")
        self.port = port
        # Initialize a socket for IPv4 (AF_INET) and protocol TCP (SOCK_STREAM)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        # Listen on localhost and port
        self.sock.connect(('127.0.0.1', self.port))
        print("Client connected to server on port {}".format(self.port))

    def send_message(self):
        # Request a message and send it
        message = input("\nType your message: ")
        self.sock.send(message.encode())
        print("\nMessage sent to server on port {}".format(self.port))
        print("\nBye.")
        self.sock.close()

if __name__ == '__main__':
    client = TCPClient(8080)
    client.connect()
    client.send_message()
