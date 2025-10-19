# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
import os

from datetime import date
from notification_list_widget import NotificationListWidget
from emoji_popover import EmojiPopover
from contacts_popover import ContactsPopover

# Diccionario de mapeo de emoticons a emojis
from utils import emoji_dict


current_path = os.path.abspath(__file__)

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_Chat


class Chat(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Chat()
        self.ui.setupUi(self)

        # Cargar hoja de estilos
        with open("chat-item.qss", "r") as f:
           qss = f.read()
           self.setStyleSheet(qss)

        # botones debajo del chat area active_chat
        self.ui.emojiButton.setIcon(QIcon("images/emoji.png"))
        self.ui.emojiButton.setIconSize(QSize(16, 16))
        self.ui.emojiButton.setFixedSize(32, 32)

        self.ui.sendButton.setIcon(QIcon("images/send.png"))
        self.ui.sendButton.setIconSize(QSize(16, 16))
        self.ui.sendButton.setFixedSize(32, 32)

        self.ui.newChatBtn.setIcon(QIcon("images/new_chat.png"))
        self.ui.newChatBtn.setIconSize(QSize(12, 12))
        self.ui.newChatBtn.setFixedSize(51, 31)


        # Crear lista de notificaciones
        self.notifications = NotificationListWidget(self.ui.notificationsScroll)

        # Emoji popover
        self.emoji_popover = EmojiPopover(self.ui.chat_text_box)
        self.ui.emojiButton.clicked.connect(lambda: self.emoji_popover.show_above_button(self.ui.emojiButton))

        self.contacts_popover = ContactsPopover(self)
        self.ui.newChatBtn.clicked.connect(lambda: self.contacts_popover.show_above_button(self.ui.newChatBtn))

        self.contacts_popover.contacts_changed.connect(lambda c: print("Contactos actualizados:", c))
        self.contacts_popover.group_created.connect(lambda g: self.new_group(g))

        # agregar usuarios conectados
        self.contacts_popover.add_contact("Juan", "images/user.png")
        self.contacts_popover.add_contact("María", "images/user.png")
        self.contacts_popover.add_contact("Luis", "images/user.png")

        # Agregar chats a la izquierda
        """for i in range(20):
            self.notifications.add_notification(
                "images/user.png",
                f"WhatsApp {i+1}",
                "New: Schedule your next call 📅 Easily plan meetings with your contacts.",
                "09/10/25"
            )
        """

        self.ui.sendButton.clicked.connect(self.sendMessage)
        self.ui.chat_text_box.returnPressed.connect(self.sendMessage)
        self.ui.emojiButton.clicked.connect(self.show_emoji_popover)

    def new_group(self, grupo):
        self.contacts_popover.add_contact(grupo['group_name'], "images/user.png")

        # Add to active chats
        today = date.today()
        formatted_date = today.strftime("%m/%d/%y")
        notif = self.notifications.add_notification(
            "images/user.png",
            f"{grupo['group_name']}",
            "New group",
            f"{formatted_date}"
        )
        notif.clicked.connect(lambda: print("Notification clicked!"))


    def sendMessage(self):
        self.ui.active_chat.add_message("Tu", self.emoji_mapper(self.ui.chat_text_box.text()), True)
        self.ui.chat_text_box.setText("")
        # add messages to active_chat ChatArea
        #self.ui.active_chat.add_message("Juan", "Hola bro!", False)
        #self.ui.active_chat.add_message("Pedro de la mar", "Qué onda bro!", True)

    def show_emoji_popover(self):
        # Posición justo encima del botón
        btn_pos = self.ui.emojiButton.mapToGlobal(self.ui.emojiButton.rect().bottomLeft())
        self.emoji_popover.move(btn_pos.x(), btn_pos.y() - self.emoji_popover.height())
        self.emoji_popover.show()

    def emoji_mapper(self,text):
        # Reemplaza cada emoticon encontrado en el texto
        for emoticon, emoji in emoji_dict.items():
            text = text.replace(emoticon, emoji)

        return text


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Chat()
    widget.show()
    sys.exit(app.exec())
