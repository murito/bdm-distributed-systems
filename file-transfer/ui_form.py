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
    QProgressBar, QPushButton, QSizePolicy, QWidget)

class Ui_FileTransfer(object):
    def setupUi(self, FileTransfer):
        if not FileTransfer.objectName():
            FileTransfer.setObjectName(u"FileTransfer")
        FileTransfer.resize(800, 600)
        self.label = QLabel(FileTransfer)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(280, 10, 231, 51))
        font = QFont()
        font.setPointSize(30)
        self.label.setFont(font)
        self.line = QFrame(FileTransfer)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(20, 60, 721, 20))
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.listen_btn = QPushButton(FileTransfer)
        self.listen_btn.setObjectName(u"listen_btn")
        self.listen_btn.setGeometry(QRect(30, 140, 111, 32))
        self.listen_port = QLineEdit(FileTransfer)
        self.listen_port.setObjectName(u"listen_port")
        self.listen_port.setGeometry(QRect(30, 110, 113, 31))
        self.label_2 = QLabel(FileTransfer)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(30, 90, 101, 16))
        self.local_server_listening = QLabel(FileTransfer)
        self.local_server_listening.setObjectName(u"local_server_listening")
        self.local_server_listening.setEnabled(False)
        self.local_server_listening.setGeometry(QRect(30, 180, 251, 16))
        self.remote_ip = QLineEdit(FileTransfer)
        self.remote_ip.setObjectName(u"remote_ip")
        self.remote_ip.setGeometry(QRect(390, 110, 113, 31))
        self.label_4 = QLabel(FileTransfer)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(390, 90, 101, 16))
        self.connect_btn = QPushButton(FileTransfer)
        self.connect_btn.setObjectName(u"connect_btn")
        self.connect_btn.setGeometry(QRect(520, 140, 111, 32))
        self.remote_port = QLineEdit(FileTransfer)
        self.remote_port.setObjectName(u"remote_port")
        self.remote_port.setGeometry(QRect(520, 110, 113, 31))
        self.label_5 = QLabel(FileTransfer)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(520, 90, 101, 16))
        self.remote_server_connected = QLabel(FileTransfer)
        self.remote_server_connected.setObjectName(u"remote_server_connected")
        self.remote_server_connected.setEnabled(False)
        self.remote_server_connected.setGeometry(QRect(520, 180, 271, 16))
        self.line_2 = QFrame(FileTransfer)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setGeometry(QRect(20, 220, 721, 20))
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)
        self.progressBar = QProgressBar(FileTransfer)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setEnabled(False)
        self.progressBar.setGeometry(QRect(270, 450, 311, 23))
        self.progressBar.setValue(0)
        self.pick_a_file = QPushButton(FileTransfer)
        self.pick_a_file.setObjectName(u"pick_a_file")
        self.pick_a_file.setGeometry(QRect(33, 300, 100, 32))
        self.receiving_label = QLabel(FileTransfer)
        self.receiving_label.setObjectName(u"receiving_label")
        self.receiving_label.setEnabled(False)
        self.receiving_label.setGeometry(QRect(273, 369, 361, 71))
        self.file_chosen = QLabel(FileTransfer)
        self.file_chosen.setObjectName(u"file_chosen")
        self.file_chosen.setGeometry(QRect(153, 290, 331, 51))
        self.send_file_btn = QPushButton(FileTransfer)
        self.send_file_btn.setObjectName(u"send_file_btn")
        self.send_file_btn.setGeometry(QRect(33, 340, 101, 32))
        self.stop_transfer_btn = QPushButton(FileTransfer)
        self.stop_transfer_btn.setObjectName(u"stop_transfer_btn")
        self.stop_transfer_btn.setGeometry(QRect(623, 300, 100, 32))
        self.receptionfilespath = QLineEdit(FileTransfer)
        self.receptionfilespath.setObjectName(u"receptionfilespath")
        self.receptionfilespath.setGeometry(QRect(170, 240, 291, 32))
        self.label_3 = QLabel(FileTransfer)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(40, 240, 121, 32))
        self.open_folder_btn = QPushButton(FileTransfer)
        self.open_folder_btn.setObjectName(u"open_folder_btn")
        self.open_folder_btn.setGeometry(QRect(470, 240, 100, 32))

        self.retranslateUi(FileTransfer)

        QMetaObject.connectSlotsByName(FileTransfer)
    # setupUi

    def retranslateUi(self, FileTransfer):
        FileTransfer.setWindowTitle(QCoreApplication.translate("FileTransfer", u"FileTransfer", None))
        self.label.setText(QCoreApplication.translate("FileTransfer", u"File Transfer App", None))
        self.listen_btn.setText(QCoreApplication.translate("FileTransfer", u"Listen", None))
        self.listen_port.setText(QCoreApplication.translate("FileTransfer", u"8080", None))
        self.label_2.setText(QCoreApplication.translate("FileTransfer", u"Listen port", None))
        self.local_server_listening.setText(QCoreApplication.translate("FileTransfer", u"Listening: False", None))
        self.remote_ip.setText(QCoreApplication.translate("FileTransfer", u"127.0.0.1", None))
        self.label_4.setText(QCoreApplication.translate("FileTransfer", u"Listen port", None))
        self.connect_btn.setText(QCoreApplication.translate("FileTransfer", u"Connect", None))
        self.remote_port.setText(QCoreApplication.translate("FileTransfer", u"8080", None))
        self.label_5.setText(QCoreApplication.translate("FileTransfer", u"Listen port", None))
        self.remote_server_connected.setText(QCoreApplication.translate("FileTransfer", u"Connected: False", None))
        self.pick_a_file.setText(QCoreApplication.translate("FileTransfer", u"Select a file", None))
        self.receiving_label.setText(QCoreApplication.translate("FileTransfer", u"Transfering file ...", None))
        self.file_chosen.setText(QCoreApplication.translate("FileTransfer", u"...", None))
        self.send_file_btn.setText(QCoreApplication.translate("FileTransfer", u"Send", None))
        self.stop_transfer_btn.setText(QCoreApplication.translate("FileTransfer", u"Stop Transfer", None))
        self.receptionfilespath.setText(QCoreApplication.translate("FileTransfer", u"/Users/murito/Desktop/reception-files", None))
        self.label_3.setText(QCoreApplication.translate("FileTransfer", u"Folder to save files:", None))
        self.open_folder_btn.setText(QCoreApplication.translate("FileTransfer", u"Open", None))
    # retranslateUi

