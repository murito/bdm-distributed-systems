"""
Sep 19, 2025
Francisco Javier Alcalá Olivares
--------------------------------------
UDP server
"""
import socket

class UDPServer:
    def __init__(self, port):
        print("\n:::UDP SERVER:::\n")
        # Set flag to await for a message
        self.listening = True
        self.port = port
        # Initialize a socket for IPv4 (AF_INET) and protocol UDP (SOCK_DGRAM)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def listen(self):
        # Listen on localhost and port
        self.sock.bind(('127.0.0.1', self.port))
        print("Server up and listening on port {}".format(self.port))

        # Await to receive a message
        while self.listening:
            data, addr = self.sock.recvfrom(1024)

            print("\nReceived: {}".format(data.decode()))
            print("\nFrom: {}".format(addr))
            print("\nBye.")

            self.listening = False
            self.sock.close()

if __name__ == '__main__':
    server = UDPServer(8080)
    server.listen()
