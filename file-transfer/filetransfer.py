import sys
import threading
import base64
import time

from PySide6.QtWidgets import QApplication, QWidget, QFileDialog
from PySide6.QtCore import Signal, QObject, QThread, Qt

from p2p_node import peers, start_server, connect_to_peer, broadcast_message

CHUNK_SIZE = 64 * 1024  # bytes
OUTPUT_PATH = '/Users/murito/Desktop'

from ui_form import Ui_FileTransfer


def on_app_quit():
    print("Closing connections...")
    for peer in peers:
        if peer:
            peer.close()


# -------------------------------
#  SIGNAL HANDLER
# -------------------------------
class MessageHandler(QObject):
    message_received = Signal(str)


# -------------------------------
#  HILO PARA ENVIAR ARCHIVOS
# -------------------------------
class FileSenderThread(QThread):
    progress = Signal(int)
    status = Signal(str)
    finished = Signal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self._stop_flag = False

    def stop(self):
        """Detiene el hilo limpiamente"""
        self._stop_flag = True

    def run(self):
        try:
            chunks = []
            with open(self.file_path, "rb") as f:
                while True:
                    data = f.read(CHUNK_SIZE)
                    if not data:
                        break
                    chunks.append(data)

            total_chunks = len(chunks)
            filename = self.file_path.split('/')[-1]

            broadcast_message(f"FILE_START::{total_chunks}::{filename}")
            self.status.emit(f"Enviando archivo: {filename}")

            for i, chunk in enumerate(chunks, start=1):
                if self._stop_flag:
                    self.status.emit("Transferencia detenida por el usuario.")
                    self.progress.emit(0)
                    broadcast_message("FILE_ABORT")
                    return

                encoded_chunk = base64.b64encode(chunk).decode()
                broadcast_message(f"FILE_CHUNK::{encoded_chunk}")

                progress = int((i / total_chunks) * 100)
                self.progress.emit(progress)
                self.status.emit(f"Enviando {filename}...\n{i}/{total_chunks} chunks")

                time.sleep(0.001)

            broadcast_message("FILE_END")
            self.progress.emit(100)
            self.finished.emit(f"Archivo enviado: {filename}")

        except Exception as e:
            self.finished.emit(f"Error al enviar archivo: {e}")


# -------------------------------
#  WIDGET PRINCIPAL
# -------------------------------
class FileTransfer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_FileTransfer()
        self.ui.setupUi(self)

        self.file_path = None
        self.received_file_name = None
        self.received_chunks = []
        self.total_chunks_expected = None

        self.handler = MessageHandler()
        self.handler.message_received.connect(self.display_message)

        # Botones
        self.ui.pick_a_file.clicked.connect(self.file_picker)
        self.ui.listen_btn.clicked.connect(self.start_listening)
        self.ui.connect_btn.clicked.connect(self.connect_to_server)
        self.ui.send_file_btn.clicked.connect(self.send_file)
        self.ui.stop_transfer_btn.clicked.connect(self.stop_transfer)  # 🆕 botón detener

        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setMaximum(100)

        self.sender_thread = None

        # Make labels show all the content
        self.ui.receiving_label.setWordWrap(True)
        self.ui.receiving_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

    def start_listening(self):
        port = int(self.ui.listen_port.text())
        thread = threading.Thread(target=start_server, args=(port, self.handler.message_received.emit), daemon=True)
        thread.start()

        self.ui.listen_port.setEnabled(False)
        self.ui.listen_btn.setEnabled(False)
        self.ui.local_server_listening.setStyleSheet("color: green;")
        self.ui.local_server_listening.setText(f"Listening on 127.0.0.1:{port}")
        self.ui.local_server_listening.setEnabled(True)

    def connect_to_server(self):
        ip = self.ui.remote_ip.text()
        port = int(self.ui.remote_port.text())

        connect_to_peer(ip, port, self.handler.message_received.emit)
        self.ui.connect_btn.setEnabled(False)
        self.ui.remote_ip.setEnabled(False)
        self.ui.remote_port.setEnabled(False)
        self.ui.remote_server_connected.setStyleSheet("color: green;")
        self.ui.remote_server_connected.setText(f"Connected with {ip}:{port}")
        self.ui.remote_server_connected.setEnabled(True)

    def file_picker(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Selecciona un archivo", "", "Todos los archivos (*)")
        if self.file_path:
            self.ui.file_chosen.setText(f"Archivo seleccionado:\n{self.file_path}")
        else:
            self.ui.file_chosen.setText("No se seleccionó ningún archivo")

    def send_file(self):
        if not self.file_path:
            self.ui.receiving_label.setText("Selecciona un archivo primero")
            return

        self.ui.send_file_btn.setEnabled(False)
        self.ui.stop_transfer_btn.setEnabled(True)

        self.sender_thread = FileSenderThread(self.file_path)
        self.sender_thread.progress.connect(self.ui.progressBar.setValue)
        self.sender_thread.status.connect(self.ui.receiving_label.setText)
        self.sender_thread.finished.connect(self.transfer_finished)

        self.sender_thread.start()

    def stop_transfer(self):
        if self.sender_thread and self.sender_thread.isRunning():
            self.sender_thread.stop()
            self.sender_thread.wait()
            self.ui.receiving_label.setText("Transferencia detenida por el usuario.")
            self.ui.send_file_btn.setEnabled(True)
            self.ui.stop_transfer_btn.setEnabled(False)

    def transfer_finished(self, message):
        self.ui.receiving_label.setText(message)
        self.ui.send_file_btn.setEnabled(True)
        self.ui.stop_transfer_btn.setEnabled(False)

    def display_message(self, msg):
        if msg.startswith("FILE_START::"):
            parts = msg.split("::", 2)
            self.total_chunks_expected = int(parts[1])
            self.received_file_name = parts[2]
            self.received_chunks = []
            self.ui.progressBar.setValue(0)
            self.ui.receiving_label.setText(f"Recibiendo archivo: {self.received_file_name}")

        elif msg.startswith("FILE_CHUNK::"):
            chunk_data = msg.split("::", 1)[1]
            self.received_chunks.append(base64.b64decode(chunk_data))
            if self.total_chunks_expected:
                progress = int((len(self.received_chunks) / self.total_chunks_expected) * 100)
                self.ui.progressBar.setValue(progress)
                self.ui.receiving_label.setText(
                    f"Recibiendo {self.received_file_name}... {len(self.received_chunks)}/{self.total_chunks_expected} chunks"
                )

        elif msg == "FILE_END":
            output_path = f"{OUTPUT_PATH}/{self.received_file_name or 'archivo_recibido.dat'}"
            with open(output_path, "wb") as f:
                for chunk in self.received_chunks:
                    f.write(chunk)
            self.ui.receiving_label.setText(f"Archivo recibido y guardado en:\n{output_path}")
            self.ui.progressBar.setValue(100)
            self.received_chunks = []
            self.total_chunks_expected = None
            self.received_file_name = None

        elif msg == "FILE_ABORT":
            self.received_chunks = []
            self.ui.receiving_label.setText("Transferencia cancelada por el remitente.")
            self.ui.progressBar.setValue(0)

        else:
            print(msg)


# -------------------------------
#  MAIN
# -------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(on_app_quit)
    widget = FileTransfer()
    widget.show()
    sys.exit(app.exec())
