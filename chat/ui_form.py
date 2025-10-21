# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QLineEdit,
    QPushButton, QScrollArea, QSizePolicy, QWidget)

from chat_area import ChatArea

class Ui_Chat(object):
    def setupUi(self, Chat):
        if not Chat.objectName():
            Chat.setObjectName(u"Chat")
        Chat.resize(1142, 738)
        self.notificationsScroll = QScrollArea(Chat)
        self.notificationsScroll.setObjectName(u"notificationsScroll")
        self.notificationsScroll.setGeometry(QRect(0, 40, 281, 701))
        self.notificationsScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.notificationsScroll.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 279, 699))
        self.notificationsScroll.setWidget(self.scrollAreaWidgetContents)
        self.label = QLabel(Chat)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 10, 58, 16))
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.label.setFont(font)
        self.chat_text_box = QLineEdit(Chat)
        self.chat_text_box.setObjectName(u"chat_text_box")
        self.chat_text_box.setGeometry(QRect(350, 690, 701, 31))
        self.plusButton = QPushButton(Chat)
        self.plusButton.setObjectName(u"plusButton")
        self.plusButton.setGeometry(QRect(290, 690, 51, 31))
        self.emojiButton = QPushButton(Chat)
        self.emojiButton.setObjectName(u"emojiButton")
        self.emojiButton.setGeometry(QRect(1100, 690, 31, 31))
        self.chat_frame = QFrame(Chat)
        self.chat_frame.setObjectName(u"chat_frame")
        self.chat_frame.setGeometry(QRect(280, 40, 861, 631))
        self.chat_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.chat_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.active_chat = ChatArea(self.chat_frame)
        self.active_chat.setObjectName(u"active_chat")
        self.active_chat.setGeometry(QRect(0, 0, 861, 671))
        self.active_chat.setWidgetResizable(True)
        self.sendButton = QPushButton(Chat)
        self.sendButton.setObjectName(u"sendButton")
        self.sendButton.setGeometry(QRect(1060, 690, 31, 32))
        self.newChatBtn = QPushButton(Chat)
        self.newChatBtn.setObjectName(u"newChatBtn")
        self.newChatBtn.setGeometry(QRect(220, 5, 51, 31))
        self.current_chat_icon = QLabel(Chat)
        self.current_chat_icon.setObjectName(u"current_chat_icon")
        self.current_chat_icon.setGeometry(QRect(290, 10, 58, 16))
        self.curent_chat_label = QLabel(Chat)
        self.curent_chat_label.setObjectName(u"curent_chat_label")
        self.curent_chat_label.setGeometry(QRect(360, 10, 761, 16))

        self.retranslateUi(Chat)

        QMetaObject.connectSlotsByName(Chat)
    # setupUi

    def retranslateUi(self, Chat):
        Chat.setWindowTitle(QCoreApplication.translate("Chat", u"Chat", None))
        self.label.setText(QCoreApplication.translate("Chat", u"Chats", None))
        self.plusButton.setText(QCoreApplication.translate("Chat", u"+", None))
        self.emojiButton.setText("")
        self.sendButton.setText("")
        self.newChatBtn.setText("")
        self.current_chat_icon.setText(QCoreApplication.translate("Chat", u"...", None))
        self.curent_chat_label.setText(QCoreApplication.translate("Chat", u"...", None))
    # retranslateUi

