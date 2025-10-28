# This Python file uses the following encoding: utf-8
import sys
import os
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
DOWNLOADS_DIR = os.path.join(os.getcwd(), "downloads")

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
            self.tcp_client.file_transfer_update.connect(self.on_file_transfer_update)
            self.tcp_client.added_to_group.connect(lambda msg: self.new_group_added(msg))

            self.tcp_client.connect_to_server()
        else:
            sys.exit(0)

        # --- Diccionario de conversaciones ---
        # { user_id: [ {type: "text"/"file", sender_name:, text:, filename:, file_id:, local_path:, is_sender:bool, client_tag:optional}, ... ] }
        self.chat_history = {}
        self.active_user = None
        self.users_dict = {}

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
        # tcp integration on create group, updates the group id from server
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
                self.users_dict[user['id']] = user['username']

    def receive_message(self, msg):
        if msg['from'] == self.active_user:
            self.ui.active_chat.add_message(self.tcp_client.user_id, msg["username"], msg['msg'], False)
        else:
            if not self.notifications.exists(msg['from']):
                self.notifications.add_notification(msg['avatar'], msg['username'], msg['msg'], today, msg['from'])

        # save and update message
        self.notifications.update_description(msg['from'], msg['msg'])
        self.save_message(msg['from'], msg['username'], msg['msg'])

    def receive_group_message(self, msg):
        if msg['group_id'] == self.active_user:
            self.ui.active_chat.add_message(self.tcp_client.user_id, msg["username"], msg['msg'], False)

        # save and update message
        self.notifications.update_description(msg['group_id'], msg['msg'])
        self.save_message(msg['group_id'], msg['username'], msg['msg'])

    def receive_file(self, msg):
        # legacy handler if needed
        pass

    def new_group_added(self, msg):
        today = date.today().strftime("%m/%d/%y")
        self.notifications.add_notification(
            random.choice(group_images),
            msg['group_name'],
            "New group",
            today,
            msg['group_id']
        )
        self.group_ids.append(msg['group_id'])

    def file_picker(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecciona un archivo", "", "Todos los archivos (*)")
        if file_path:
            # Si no hay chat activo, no enviar
            if not self.active_user:
                QMessageBox.information(self, "Selecciona chat", "Selecciona un chat antes de enviar un archivo.")
                return
            # si active_user es grupo (está en group_ids) enviamos group_id, sino enviamos to
            if self.active_user in self.group_ids:
                self.tcp_client.send_file(target_id=None, group_id=self.active_user, file_path=file_path)
            else:
                self.tcp_client.send_file(target_id=self.active_user, group_id=None, file_path=file_path)

            #  notificación temporal (NO crear burbuja aquí; la UI se creará desde file_started (local o server))
            if not self.notifications.exists(self.active_user):
                self.notifications.add_notification("", "Enviando archivo...", "Preparando...", today, self.active_user)

    # ----------------------------
    # Manejo de grupos / contactos
    # ----------------------------
    def new_group(self, grupo):
        member_ids = [m["id"] for m in grupo["members"]]
        member_ids.append(self.tcp_client.user_id)
        self.tcp_client.create_group(grupo['group_name'], member_ids)

    def contact_clicked(self, data):
        today = date.today().strftime("%m/%d/%y")
        self.notifications.add_notification(
            data['image'],
            data['name'],
            "",
            today,
            data['id']
        )

    # ----------------------------
    # Cambio de chat activo
    # ----------------------------
    def notif_clicked(self, notif):
        self.active_user = notif['id']
        print(f"Chat activo -> {self.active_user}")

        self.disableControls(False)

        self.ui.curent_chat_label.setText(notif['title'])
        pixmap = QPixmap(notif['icon_path']).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.current_chat_icon.setPixmap(pixmap)
        self.ui.current_chat_icon.setFixedSize(48, 48)
        self.ui.current_chat_icon.setStyleSheet("background: transparent;")

        self.ui.active_chat.clear_messages()

        # rebuild from history (including file bubbles)
        if self.active_user in self.chat_history:
            for entry in self.chat_history[self.active_user]:
                if entry["type"] == "text":
                    self.ui.active_chat.add_message(self.tcp_client.user_id, entry["sender_name"], entry["text"], entry["is_sender"])
                elif entry["type"] == "file":
                    # add file bubble and register it under file_id if present
                    fb = self.ui.active_chat.add_message(self.tcp_client.user_id, entry["sender_name"], file_path=None, filename=entry["filename"], file_id=entry.get("file_id"), is_sender=entry["is_sender"])
                    # if we have stored progress, update it
                    if "progress" in entry:
                        self.ui.active_chat.update_progress(entry["file_id"], entry["progress"])
                    # 🔹 restaurar click si ya se descargó
                    if "local_path" in entry and entry["local_path"]:
                        fb.setup_click(entry["local_path"])

    # ----------------------------
    # Envío de mensajes
    # ----------------------------
    def sendMessage(self):
        text = self.ui.chat_text_box.text().strip()
        if not text or not self.active_user:
            return

        text = self.emoji_mapper(text)
        self.ui.chat_text_box.setText("")

        self.ui.active_chat.add_message(self.tcp_client.user_id, "Tú", text, True)
        self.save_message(self.active_user, "Tú", text)

        if self.active_user in self.group_ids:
            self.tcp_client.send_group_chat(self.active_user, text)
        else:
            self.tcp_client.send_chat(self.active_user, text)

    def save_message(self, chat_id, sender_name, message):
        if chat_id not in self.chat_history:
            self.chat_history[chat_id] = []
        self.chat_history[chat_id].append({"type": "text", "sender_name": sender_name, "text": message, "is_sender": sender_name=="Tú"})

    # ----------------------------
    # Recepción y manejo de archivos
    # ----------------------------
    def on_file_transfer_update(self, msg):
        mtype = msg.get("type")

        # ---------- FILE_STARTED ----------
        if mtype == "file_started":
            file_id = msg.get("file_id")            # puede ser None si es local_started
            client_tag = msg.get("client_tag")      # tag temporario generado por el cliente
            filename = msg.get("filename")
            filesize = msg.get("filesize", 0)
            initiator = msg.get("initiator")
            targets = msg.get("targets", [])

            # determinar chat_id donde debe aparecer:
            # si viene group_id -> es chat de grupo; si no, es chat entre usuarios (el otro)
            if msg.get("group_id"):
                chat_id = msg["group_id"]
            else:
                # targets puede contener el id del receptor; si soy yo el iniciador, elegir el primer target distinto de mi id
                if initiator == self.tcp_client.user_id:
                    t = [t for t in targets if t != self.tcp_client.user_id]
                    chat_id = t[0] if t else (targets[0] if targets else None)
                else:
                    chat_id = initiator

            if not chat_id:
                return

            # Si ya existe una entrada temporal creada por client_tag (local_started), NO crear otra; actualizarla.
            # Usamos display_id para la UI: si file_id real no existe y hay client_tag, usaremos client_tag como id temporario.
            display_id = file_id if file_id else client_tag

            # ensure history structure
            if chat_id not in self.chat_history:
                self.chat_history[chat_id] = []

            # buscar existencia previa por client_tag (evitar duplicados)
            existing = None
            for e in self.chat_history[chat_id]:
                # match by client_tag OR by file_id
                if client_tag and e.get("client_tag") == client_tag:
                    existing = e
                    break
                if display_id and e.get("file_id") == display_id:
                    existing = e
                    break

            if existing:
                # Si ya existe y ahora recibimos el file_id real, actualizamos la entrada y remapeamos UI si es necesario
                # actualiza file_id real y remover client_tag flag
                if file_id and existing.get("file_id") != file_id:
                    prev_id = existing.get("file_id")
                    existing["file_id"] = file_id
                    existing.pop("client_tag", None)
                    # actualizar burbuja en UI si está visible y fue registrada con prev_id (por ejemplo client_tag)
                    if chat_id == self.active_user:
                        # remap en ChatArea.file_bubbles si existe
                        try:
                            fa = self.ui.active_chat
                            if prev_id in fa.file_bubbles:
                                fb = fa.file_bubbles.pop(prev_id)
                                fa.file_bubbles[file_id] = fb
                                # si el FileBubble tiene attach_file_id, llamarlo (compatibilidad)
                                if hasattr(fb, "attach_file_id"):
                                    try:
                                        fb.attach_file_id(file_id)
                                    except:
                                        pass
                        except Exception as e:
                            print("Error remapeando burbuja:", e)
                # actualizar metadatos si queremos
                existing["filename"] = filename
                existing["filesize"] = filesize
            else:
                name = self.users_dict[initiator] if initiator in self.users_dict else "Alguien"
                # crear nueva entrada en historial con display_id (puede ser client_tag temporal)
                entry = {
                    "type": "file",
                    "sender_name": ("Tú" if initiator == self.tcp_client.user_id else msg.get("username", name)),
                    "filename": filename,
                    "file_id": display_id,
                    "is_sender": initiator == self.tcp_client.user_id,
                    "progress": 0,
                    "client_tag": client_tag if client_tag else None,
                    "filesize": filesize,
                    "local_path": f"{DOWNLOADS_DIR}/{self.tcp_client.user_id}/"
                }
                self.chat_history[chat_id].append(entry)

                # if chat is active, add bubble (will register in ChatArea.file_bubbles keyed by display_id)
                if chat_id == self.active_user:
                    self.ui.active_chat.add_message(self.tcp_client.user_id, entry["sender_name"], file_path=None, filename=filename, file_id=display_id, is_sender=entry["is_sender"])

        # ---------- FILE_PROGRESS ----------
        elif mtype == "file_progress":
            file_id = msg.get("file_id")
            transferred = msg.get("bytes_transferred", 0)
            total = msg.get("total_bytes", 0)
            percent = (transferred / total * 100) if total else 0

            # update all histories where this file_id appears
            for chat_id, msgs in self.chat_history.items():
                for e in msgs:
                    if e.get("file_id") == file_id:
                        e["progress"] = percent
                        # also set total if present
                        if total:
                            e["filesize"] = total

            # update UI if bubble visible
            self.ui.active_chat.update_progress(file_id, percent)

        # ---------- FILE_CHUNK (dos variantes) ----------
        elif mtype == "file_chunk":
            file_id = msg.get("file_id")
            filename = msg.get("filename", "file")
            initiator = msg.get("initiator")

            if "data" in msg:
                downloads_dir = os.path.join(os.getcwd(), "downloads")
                os.makedirs(downloads_dir, exist_ok=True)
                local_path = os.path.join(downloads_dir, f"{file_id}_{filename}")
                try:
                    with open(local_path, "ab") as f:
                        f.write(msg["data"])
                except Exception as e:
                    print("Error escribiendo chunk (variant data):", e)
                return


            if "bytes_received" in msg:
                bytes_recv = msg.get("bytes_received", 0)
                total_bytes = msg.get("total_bytes", None)

                # update history
                for chat_id, msgs in self.chat_history.items():
                    for e in msgs:
                        if e.get("file_id") == file_id:
                            if total_bytes:
                                e["filesize"] = total_bytes
                                e["progress"] = (bytes_recv / total_bytes) * 100 if total_bytes else e.get("progress", 0)
                            else:
                                # si no hay total, solo actualizar bytes aproximado (sin %)
                                e["progress"] = e.get("progress", 0)

                # update UI
                if total_bytes:
                    percent = (bytes_recv / total_bytes) * 100 if total_bytes else 0
                    self.ui.active_chat.update_progress(file_id, percent)
                else:
                    # fallback: use stored progress if available
                    for chat_id, msgs in self.chat_history.items():
                        for e in msgs:
                            if e.get("file_id") == file_id and e.get("progress") is not None:
                                self.ui.active_chat.update_progress(file_id, e["progress"])
                                break

        # ---------- FILE_COMPLETED ----------
        elif mtype == "file_completed":
            file_id = msg.get("file_id")
            filename = msg.get("filename")
            downloads_dir = os.path.join(os.getcwd(), f"downloads/{self.tcp_client.user_id}")
            local_path = os.path.join(downloads_dir, f"{file_id}_{filename}")

            # mark completed in histories and attach local_path
            for chat_id, msgs in self.chat_history.items():
                for e in msgs:
                    if e.get("file_id") == file_id:
                        e["progress"] = 100
                        e["local_path"] = local_path

            # update UI
            self.ui.active_chat.mark_completed(file_id, local_path)

    # ----------------------------
    # Simulación de recibir mensaje
    # ----------------------------
    def receiveMessage(self, sender_name, text):
        if not self.active_user:
            return
        if self.active_user not in self.chat_history:
            self.chat_history[self.active_user] = []

        text = self.emoji_mapper(text)
        self.chat_history[self.active_user].append((sender_name, text, False))
        self.ui.active_chat.add_message(self.tcp_client.user_id, sender_name, text, False)

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
