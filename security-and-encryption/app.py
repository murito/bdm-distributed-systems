# This Python file uses the following encoding: utf-8
import sys
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Signal, QObject, QTimer

import time
import threading
from p2p_node import start_server, connect_to_peer, peers, broadcast_message, encrypt_aes256, decrypt_aes256, ENCRYPTION_KEY

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_Widget

def encrypt_message(ui):
    ENCRYPTED_TEXT = encrypt_aes256(ui.raw_text.toPlainText(), ENCRYPTION_KEY)
    ui.ecrypted_text.setHtml( ENCRYPTED_TEXT )

def decrypt_messasge(ui):
    ui.raw_text.setHtml( decrypt_aes256(ui.ecrypted_text.toPlainText(), ENCRYPTION_KEY) )

def start_listening(widget):
    port = int(widget.ui.listen_port.text())

    thread = threading.Thread(target=start_server, args=(port, widget.handler.message_received.emit), daemon=True)
    thread.start()

    widget.ui.listen_port.setEnabled(False)
    widget.ui.listen_btn.setEnabled(False)

    widget.ui.local_server_listening.setStyleSheet("color: green;")
    widget.ui.local_server_listening.setText(f"Listening on 127.0.0.1:{port}")
    widget.ui.local_server_listening.setEnabled(True)

def connect_to_server(widget):
    ip = widget.ui.remote_ip.text()
    port = int(widget.ui.remote_port.text())

    connect_to_peer(ip, port, widget.handler.message_received.emit)

    widget.ui.connect_btn.setEnabled(False)
    widget.ui.remote_ip.setEnabled(False)
    widget.ui.remote_port.setEnabled(False)
    widget.ui.remote_server_connected.setStyleSheet("color: green;")
    widget.ui.remote_server_connected.setText(f"Connected with {ip}:{port}")
    widget.ui.remote_server_connected.setEnabled(True)


def clean_after_sent(ui):
    ui.username.setText('')
    ui.password.setText('')
    ui.send_status_lbl.setText("...")
    ui.send_status_lbl.setStyleSheet("")
    ui.send_status_lbl.setEnabled(False)

def send_encrypted_text(ui):
    ENCRYPTED_TEXT = encrypt_aes256(ui.raw_text.toPlainText(), ENCRYPTION_KEY)
    ui.ecrypted_text.setHtml( ENCRYPTED_TEXT )
    broadcast_message( ENCRYPTED_TEXT )

    ui.send_status_lbl.setStyleSheet("color: green;")
    ui.send_status_lbl.setText("Message sent!")
    ui.send_status_lbl.setEnabled(True)

    QTimer.singleShot(3000, lambda: clean_after_sent(ui))


def on_raw_text_change(ui):
    text = ui.raw_text.toPlainText()
    if len(peers) > 0 and len(text) > 0:
        ui.username_lbl.setEnabled(True)
        ui.password_lbl.setEnabled(True)
        ui.username.setEnabled(True)
        ui.password.setEnabled(True)
    else:
        ui.username_lbl.setEnabled(False)
        ui.password_lbl.setEnabled(False)
        ui.username.setEnabled(False)
        ui.password.setEnabled(False)

def on_valid_user_and_pass(ui):
    user = ui.username.text()
    password = ui.password.text()
    if user == 'admin' and password == 'admin':
        ui.send_btn.setEnabled(True)

# Signals
class MessageHandler(QObject):
    message_received = Signal(str)


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        self.setWindowTitle("Security and Encryption v1.0")

        # Handler de mensajes
        self.handler = MessageHandler()
        self.handler.message_received.connect(self.display_message)

        self.ui.encrypt_btn.clicked.connect(lambda: encrypt_message(self.ui))
        self.ui.decryption_btn.clicked.connect(lambda: decrypt_messasge(self.ui))
        self.ui.listen_btn.clicked.connect(lambda: start_listening(self))
        self.ui.connect_btn.clicked.connect(lambda: connect_to_server(self))
        self.ui.raw_text.textChanged.connect(lambda: on_raw_text_change(self.ui))
        self.ui.username.textChanged.connect(lambda: on_valid_user_and_pass(self.ui))
        self.ui.password.textChanged.connect(lambda: on_valid_user_and_pass(self.ui))
        self.ui.send_btn.clicked.connect(lambda: send_encrypted_text(self.ui))

    def display_message(self, msg):
        self.ui.ecrypted_text.setHtml(msg)
        self.ui.raw_text.setHtml( decrypt_aes256(self.ui.ecrypted_text.toPlainText(), ENCRYPTION_KEY) )


def on_app_quit():
    print("Closing connections...")
    for peer in peers:
        if peer:
            peer.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(on_app_quit)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())

