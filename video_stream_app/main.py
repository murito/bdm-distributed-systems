import sys
import socket
import ssl
import threading
import cv2
import numpy as np
import time

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from ui_form import Ui_MainWindow  # generado a partir de form.ui

import os
import subprocess

class VideoStreamApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Auto-generate certificate if not found
        if not os.path.exists("cert.pem") or not os.path.exists("key.pem"):
            subprocess.run([
                "openssl", "req", "-x509", "-newkey", "rsa:2048",
                "-keyout", "key.pem", "-out", "cert.pem",
                "-days", "365", "-nodes", "-subj", "/CN=localhost"
            ])

        self.server_socket = None
        self.client_socket = None
        self.capture = None
        self.running = False
        self.streamming = True

        # Buffer y reproducción
        self.frames_buffer = []
        self.play_index = 0
        self.playing = True
        self.playing_recorded_video = True

        # Botones
        self.ui.btnStartServer.clicked.connect(self.start_server)
        self.ui.btnStartClient.clicked.connect(self.start_client)
        self.ui.stop_play.clicked.connect(self.toggle_streamming)
        self.ui.btnPlayPause.clicked.connect(self.toggle_play)
        self.ui.btnForward.clicked.connect(lambda: self.skip_frames(10))
        self.ui.btnBackward.clicked.connect(lambda: self.skip_frames(-10))

        #sliderProgress
        self.ui.sliderProgress.setMinimum(0)
        self.ui.sliderProgress.setMaximum(0)
        self.ui.sliderProgress.valueChanged.connect(self.slider_moved)
        self.slider_dragging = False

    # Control stream
    def toggle_streamming(self):
        self.streamming = not self.streamming
        self.ui.stop_play.setText("Detener streamming" if self.streamming else "Reanudar streamming")

    def disabledControls(self):
        self.ui.inputServerPort.setEnabled(False)
        self.ui.btnStartServer.setEnabled(False)
        self.ui.inputClientIP.setEnabled(False)
        self.ui.inputClientPort.setEnabled(False)
        self.ui.btnStartClient.setEnabled(False)
        self.ui.btnBackward.setEnabled(False)
        self.ui.btnForward.setEnabled(False)
        self.ui.btnPlayPause.setEnabled(False)

    # ================== SERVER ==================
    def start_server(self):
        port_text = self.ui.inputServerPort.text().strip()
        if not port_text.isdigit():
            QMessageBox.warning(self, "Error", "Puerto inválido.")
            return
        port = int(port_text)
        self.ui.videoLabel.setStyleSheet("border: 2px solid #00ff00; background-color: #202020;")

        # Aqui el thread del servidor
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

                # Local preview
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

    # ================== CLIENT ==================
    def start_client(self):
        host = self.ui.inputClientIP.text().strip()
        port_text = self.ui.inputClientPort.text().strip()

        if not host or not port_text.isdigit():
            QMessageBox.warning(self, "Error", "IP o puerto inválido.")
            return

        port = int(port_text)
        self.ui.videoLabel.setStyleSheet("border: 2px solid #0099ff; background-color: #202020;")

        # Aqui el thread del cliente
        threading.Thread(target=self.client_thread, args=(host, port), daemon=True).start()

        self.ui.statusLabel.setText(f"Conectando a {host}:{port}...")
        self.disabledControls()
        self.ui.stop_play.setEnabled(False)

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
        self.frames_buffer = []
        self.play_index = 0
        self.playing = True
        self.running = True

        while self.running:
            # get the header first
            header = self.recvall(conn, 4)
            if not header:
                break
            size = int.from_bytes(header, "big")

            # then get the data
            data = self.recvall(conn, size)
            if not data:
                break

            # decode the data and get the frame
            frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)

            # Add t othe screen label (Simulated video screen)
            self.display_frame(frame)

            # Store for future playing
            self.frames_buffer.append(frame.copy())

        conn.close()

        self.ui.statusLabel.setText("Conexión terminada. Reproduciendo video grabado...")
        self.play_recorded_video()

    def play_recorded_video(self):
        self.ui.btnBackward.setEnabled(True)
        self.ui.btnForward.setEnabled(True)
        self.ui.btnPlayPause.setEnabled(True)

        self.ui.btnPlayPause.setText("Pause")
        threading.Thread(target=self.replay_buffer, daemon=True).start()

    # ================== UTILS ==================
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

    # Reproducción buffer
    def toggle_play(self):
        if not self.playing_recorded_video:
            self.play_index = 0
            self.playing = True
            self.playing_recorded_video = True
            self.ui.btnPlayPause.setText("Pause")

            self.play_recorded_video()
        else:
            self.playing = not self.playing
            self.ui.btnPlayPause.setText("Pause" if self.playing else "Play")

    def skip_frames(self, n):
        self.play_index = max(0, min(len(self.frames_buffer)-1, self.play_index + n))
        self.display_frame(self.frames_buffer[self.play_index])

    def replay_buffer(self):
        self.ui.statusLabel.setText("Reproduciendo video grabado...")
        while self.play_index < len(self.frames_buffer):
            if self.playing and not self.slider_dragging:
                frame = self.frames_buffer[self.play_index]
                self.display_frame(frame)
                self.play_index += 1
                self.ui.sliderProgress.setMaximum(len(self.frames_buffer)-1)
                self.ui.sliderProgress.setValue(self.play_index)
            time.sleep(1/24) # 24 fps

        self.playing_recorded_video = False
        self.ui.btnPlayPause.setText("Play")
        self.ui.statusLabel.setText("Reproducción finalizada.")

    def slider_moved(self, value):
        self.slider_dragging = True
        if self.frames_buffer:
            self.play_index = value
            self.display_frame(self.frames_buffer[self.play_index])
        self.slider_dragging = False

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
