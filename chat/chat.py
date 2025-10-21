# This Python file uses the following encoding: utf-8
import sys
from PySide6.QtWidgets import QApplication, QWidget, QDialog, QMessageBox, QFileDialog

from PySide6.QtGui import QIcon, QPixmap, Qt
from PySide6.QtCore import QSize

import random
from datetime import date
from notification_list_widget import NotificationListWidget
from emoji_popover import EmojiPopover
from contacts_popover import ContactsPopover
from utils import emoji_dict  # Diccionario de emoticon -> emoji
from user_setup_dialog import UserSetupDialog

from ui_form import Ui_Chat
from chat_tcp_client import ChatTCPClient

today = date.today().strftime("%m/%d/%y")
group_images = ["images/group.png", "images/group1.png", "images/group2.png", "images/group3.png"]

class Chat(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Chat()
        self.ui.setupUi(self)

        self.tcp_client = None
        self.group_ids = []

        # --- Mostrar modal al iniciar ---
        setup_dialog = UserSetupDialog(self)
        if setup_dialog.exec() == QDialog.Accepted:
            self.user_name = setup_dialog.nickname
            self.user_image = setup_dialog.image_path

            self.setWindowTitle(f".:: {self.user_name} ::.")

            self.tcp_client = ChatTCPClient(self.user_name, self.user_image)

            # --- Conectar signals ---
            self.tcp_client.connected.connect(lambda: self.ui.curent_chat_label.setText("✅ Conectado al servidor."))
            self.tcp_client.disconnected.connect(lambda: self.ui.curent_chat_label.setText("❌ Desconectado del servidor."))
            self.tcp_client.error.connect(lambda e: QMessageBox.critical(self, "Error", e))
            self.tcp_client.users_updated.connect(self.update_users)
            self.tcp_client.message_received.connect(self.receive_message)
            self.tcp_client.group_message_received.connect(self.receive_group_message)
            self.tcp_client.file_received.connect(self.receive_file)
            self.tcp_client.added_to_group.connect(lambda msg: self.new_group_added(msg))


            self.tcp_client.connect_to_server()
        else:
            sys.exit(0)

        # --- Diccionario de conversaciones ---
        # { user_id: [ (sender_name, text, is_sender), ... ] }
        self.chat_history = {}
        self.active_user = None

        # --- Estilos ---
        with open("chat-item.qss", "r") as f:
            self.setStyleSheet(f.read())

        # --- Botones ---
        self.ui.emojiButton.setIcon(QIcon("images/emoji.png"))
        self.ui.emojiButton.setIconSize(QSize(16, 16))
        self.ui.emojiButton.setFixedSize(32, 32)

        self.ui.sendButton.setIcon(QIcon("images/send.png"))
        self.ui.sendButton.setIconSize(QSize(16, 16))
        self.ui.sendButton.setFixedSize(32, 32)

        self.ui.newChatBtn.setIcon(QIcon("images/new_chat.png"))
        self.ui.newChatBtn.setIconSize(QSize(12, 12))
        self.ui.newChatBtn.setFixedSize(51, 31)

        self.ui.plusButton.clicked.connect(self.file_picker)

        # --- Lista de notificaciones ---
        self.notifications = NotificationListWidget(self.ui.notificationsScroll)

        # --- Popovers ---
        self.emoji_popover = EmojiPopover(self.ui.chat_text_box)
        self.ui.emojiButton.clicked.connect(lambda: self.emoji_popover.show_above_button(self.ui.emojiButton))

        self.contacts_popover = ContactsPopover(self)
        self.contacts_popover.item_clicked.connect(self.contact_clicked)
        self.ui.newChatBtn.clicked.connect(lambda: self.contacts_popover.show_above_button(self.ui.newChatBtn))

        self.contacts_popover.contacts_changed.connect(lambda c: print("Contactos actualizados:", c))
        self.contacts_popover.group_created.connect(self.new_group)
        # tcp integration on create group, updates the griup id from server
        self.tcp_client.group_created.connect(self.contacts_popover.on_group_created_from_server)

        # Chats activos en la barra lateral
        self.notifications.notif_clicked.connect(self.notif_clicked)

        # --- Conexiones ---
        self.ui.sendButton.clicked.connect(self.sendMessage)
        self.ui.chat_text_box.returnPressed.connect(self.sendMessage)
        self.ui.emojiButton.clicked.connect(self.show_emoji_popover)

        # --- Deshabilita caja de texto y botones ---
        self.disableControls(True)

    def disableControls(self, disabled):
        self.ui.chat_text_box.setEnabled(not disabled)
        self.ui.emojiButton.setEnabled(not disabled)
        self.ui.sendButton.setEnabled(not disabled)
        self.ui.plusButton.setEnabled(not disabled)

    # ---------------- TCP Handlers ----------------
    def update_users(self, users):
        for user in users:
            if user['id'] != self.tcp_client.user_id:
                self.contacts_popover.add_contact(user['id'], user['username'], user['avatar'])

    def receive_message(self, msg):
        if msg['from'] == self.active_user:
            self.ui.active_chat.add_message(msg["username"], msg['msg'], False)
        else:
            if not self.notifications.exists(msg['from']):
                self.notifications.add_notification(msg['avatar'], msg['username'], msg['msg'], today, msg['from'])

        # save and update message
        self.notifications.update_description(msg['from'], msg['msg'])
        self.save_message(msg['from'], msg['username'], msg['msg'])

    def receive_group_message(self, msg):
        if msg['group_id'] == self.active_user:
            self.ui.active_chat.add_message(msg["username"], msg['msg'], False)

        # save and update message
        self.notifications.update_description(msg['group_id'], msg['msg'])
        self.save_message(msg['group_id'], msg['username'], msg['msg'])

    def receive_file(self, msg):
        #self.ui.active_chat.add_message("Juan", is_sender=True, file_path="/Users/murito/Documents/UAG/Maestria/SegundoCuatrimestre/SistemasDistribuidos/U1_A1_Socket_UDP/Reporte UDP.pdf")
        """sender = msg["from"]
        filename = msg["filename"]
        data = msg["data"]
        save_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", filename)
        if save_path:
            with open(save_path, "wb") as f:
                f.write(data)
                self.chat_area.append(f"📁 {sender} te envió un archivo: {filename}")"""
        pass

    def new_group_added(self, msg):
        """Remote group notification"""
        today = date.today().strftime("%m/%d/%y")
        self.notifications.add_notification(
            random.choice(group_images),
            msg['group_name'],
            "New group",
            today,
            msg['group_id']
        )

        print(msg['group_id'])

        # Track group ids
        self.group_ids.append(msg['group_id'])


    def file_picker(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecciona un archivo", "", "Todos los archivos (*)")
        if file_path:
            self.ui.chat_text_box.setText(file_path)

    # ----------------------------
    # Manejo de grupos / contactos
    # ----------------------------
    def new_group(self, grupo):
        # TCP create group
        member_ids = [m["id"] for m in grupo["members"]]
        member_ids.append(self.tcp_client.user_id)
        self.tcp_client.create_group(grupo['group_name'], member_ids)

    def contact_clicked(self, data):
        """Cuando el usuario selecciona un contacto desde el popover."""
        today = date.today().strftime("%m/%d/%y")
        self.notifications.add_notification(
            data['image'],
            data['name'],
            "",
            today,
            data['id']  # importante: usamos su id real
        )

    # ----------------------------
    # Cambio de chat activo
    # ----------------------------
    def notif_clicked(self, notif):
        """Cuando haces clic en un chat en la lista de notificaciones."""
        self.active_user = notif['id']
        print(f"Chat activo -> {self.active_user}")

        self.disableControls(False)

        # Cambiar encabezado del chat
        self.ui.curent_chat_label.setText(notif['title'])
        pixmap = QPixmap(notif['icon_path']).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.current_chat_icon.setPixmap(pixmap)
        self.ui.current_chat_icon.setFixedSize(48, 48)
        self.ui.current_chat_icon.setStyleSheet("background: transparent;")

        # Limpiar área de mensajes y recargar historial
        self.ui.active_chat.clear_messages()

        if self.active_user in self.chat_history:
            for sender, text, is_sender in self.chat_history[self.active_user]:
                self.ui.active_chat.add_message(sender, text, is_sender)

    # ----------------------------
    # Envío de mensajes
    # ----------------------------
    def sendMessage(self):
        text = self.ui.chat_text_box.text().strip()
        if not text or not self.active_user:
            return  # No enviar si no hay chat activo o texto vacío

        text = self.emoji_mapper(text)
        self.ui.chat_text_box.setText("")

        # Mostrar en el chat actual
        self.ui.active_chat.add_message("Tú", text, True)

        # Guardar en historial
        self.save_message(self.active_user, "Tú", text)

        # Envio TCP
        print(f"{self.active_user}, {self.group_ids}")
        if self.active_user in self.group_ids:
            self.tcp_client.send_group_chat(self.active_user, text)
            print("Grupal send")
        else:
            self.tcp_client.send_chat(self.active_user, text)

    def save_message(self, id, sender, message):
        # Guardar en historial
        if id not in self.chat_history:
            self.chat_history[id] = []

        self.chat_history[id].append((sender, message, sender == "Tú"))

    def receiveMessage(self, sender_name, text):
        """Simula recibir mensaje del contacto activo."""
        if not self.active_user:
            return
        if self.active_user not in self.chat_history:
            self.chat_history[self.active_user] = []

        text = self.emoji_mapper(text)
        self.chat_history[self.active_user].append((sender_name, text, False))
        self.ui.active_chat.add_message(sender_name, text, False)

    # ----------------------------
    # Emojis
    # ----------------------------
    def show_emoji_popover(self):
        btn_pos = self.ui.emojiButton.mapToGlobal(self.ui.emojiButton.rect().bottomLeft())
        self.emoji_popover.move(btn_pos.x(), btn_pos.y() - self.emoji_popover.height())
        self.emoji_popover.show()

    def emoji_mapper(self, text):
        for emoticon, emoji in emoji_dict.items():
            text = text.replace(emoticon, emoji)
        return text


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Chat()
    widget.show()
    sys.exit(app.exec())
