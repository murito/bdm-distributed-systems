import sys
import socket
import ssl
import threading
import cv2
import numpy as np
import os

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from ui_form import Ui_MainWindow


class VideoStreamApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.server_socket = None
        self.client_socket = None
        self.capture = None
        self.running = False
        self.streamming = True

        # Auto-generate certificate if not found
        if not os.path.exists("cert.pem") or not os.path.exists("key.pem"):
            import subprocess
            subprocess.run([
                "openssl", "req", "-x509", "-newkey", "rsa:2048",
                "-keyout", "key.pem", "-out", "cert.pem",
                "-days", "365", "-nodes", "-subj", "/CN=localhost"
            ])

        # Buttons
        self.ui.btnStartServer.clicked.connect(self.start_server)
        self.ui.btnStartClient.clicked.connect(self.start_client)
        self.ui.stop_play.clicked.connect(self.stop_play)

    def stop_play(self):
        self.streamming = not self.streamming
        self.ui.stop_play.setText("Detener streamming" if self.streamming else "Reanudar streamming")

    def disabledControls(self):
        self.ui.inputServerPort.setEnabled(False)
        self.ui.btnStartServer.setEnabled(False)
        self.ui.inputClientIP.setEnabled(False)
        self.ui.inputClientPort.setEnabled(False)
        self.ui.btnStartClient.setEnabled(False)

    def start_server(self):
        if self.running:
            QMessageBox.information(self, "Servidor activo", "El servidor ya está en ejecución.")
            return

        port_text = self.ui.inputServerPort.text().strip()
        if not port_text.isdigit():
            QMessageBox.warning(self, "Error", "Puerto inválido.")
            return

        port = int(port_text)
        self.ui.videoLabel.setStyleSheet("border: 2px solid #00ff00; background-color: #202020;")
        threading.Thread(target=self.server_thread, args=(port,), daemon=True).start()
        self.ui.statusLabel.setText(f"Servidor escuchando en puerto {port}")
        self.disabledControls()

    def server_thread(self, port):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.set_ciphers("ECDHE+AESGCM")
        context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

        bind_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bind_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        bind_socket.bind(("0.0.0.0", port))
        bind_socket.listen(1)

        with context.wrap_socket(bind_socket, server_side=True) as server:
            self.capture = cv2.VideoCapture(0)
            self.running = True
            self.ui.statusLabel.setText("Esperando conexión de cliente...")

            conn, addr = server.accept()
            self.ui.statusLabel.setText(f"Cliente conectado desde {addr}")

            while self.running:
                ret, frame = self.capture.read()
                if not ret:
                    continue

                self.display_frame(frame)

                _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
                data = buffer.tobytes()
                size = len(data)

                try:
                    if self.streamming:
                        conn.sendall(size.to_bytes(4, "big") + data)
                except:
                    self.ui.statusLabel.setText("Cliente desconectado.")
                    break

            conn.close()
            self.capture.release()

    def start_client(self):
        host = self.ui.inputClientIP.text().strip()
        port_text = self.ui.inputClientPort.text().strip()
        self.ui.stop_play.setEnabled(False)

        if not host or not port_text.isdigit():
            QMessageBox.warning(self, "Error", "IP o puerto inválido.")
            return

        port = int(port_text)
        self.ui.videoLabel.setStyleSheet("border: 2px solid #0099ff; background-color: #202020;")
        threading.Thread(target=self.client_thread, args=(host, port), daemon=True).start()
        self.ui.statusLabel.setText(f"Conectando a {host}:{port}...")
        self.disabledControls()

    def client_thread(self, host, port):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.set_ciphers("ECDHE+AESGCM")
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn = context.wrap_socket(raw_sock, server_hostname=host)

        try:
            conn.connect((host, port))
        except Exception as e:
            self.ui.statusLabel.setText(f"Error de conexión: {e}")
            return

        self.ui.statusLabel.setText("Conectado. Recibiendo video...")
        self.running = True

        while self.running:
            header = self.recvall(conn, 4)
            if not header:
                break
            size = int.from_bytes(header, "big")
            data = self.recvall(conn, size)
            if not data:
                break
            frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            self.display_frame(frame)

        conn.close()
        self.ui.statusLabel.setText("Conexión terminada.")

    def recvall(self, sock, n):
        data = b""
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def display_frame(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        self.ui.videoLabel.setPixmap(pix.scaled(self.ui.videoLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def closeEvent(self, event):
        self.running = False
        if self.capture:
            self.capture.release()
        if self.server_socket:
            self.server_socket.close()
        if self.client_socket:
            self.client_socket.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoStreamApp()
    window.show()
    sys.exit(app.exec())
