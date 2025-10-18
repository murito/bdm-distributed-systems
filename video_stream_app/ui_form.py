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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QSlider, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(640, 567)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.videoLabel = QLabel(self.centralwidget)
        self.videoLabel.setObjectName(u"videoLabel")
        self.videoLabel.setMinimumSize(QSize(320, 240))
        self.videoLabel.setStyleSheet(u"background-color: #202020; color: #aaaaaa; border:\n"
"                                1px solid #555;")
        self.videoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.videoLabel)

        self.frameServer = QFrame(self.centralwidget)
        self.frameServer.setObjectName(u"frameServer")
        self.frameServer.setFrameShape(QFrame.Shape.StyledPanel)
        self.horizontalLayoutServer = QHBoxLayout(self.frameServer)
        self.horizontalLayoutServer.setObjectName(u"horizontalLayoutServer")
        self.sliderProgress = QSlider(self.frameServer)
        self.sliderProgress.setObjectName(u"sliderProgress")
        self.sliderProgress.setOrientation(Qt.Horizontal)

        self.horizontalLayoutServer.addWidget(self.sliderProgress)

        self.btnBackward = QPushButton(self.frameServer)
        self.btnBackward.setObjectName(u"btnBackward")

        self.horizontalLayoutServer.addWidget(self.btnBackward)

        self.btnPlayPause = QPushButton(self.frameServer)
        self.btnPlayPause.setObjectName(u"btnPlayPause")

        self.horizontalLayoutServer.addWidget(self.btnPlayPause)

        self.btnForward = QPushButton(self.frameServer)
        self.btnForward.setObjectName(u"btnForward")

        self.horizontalLayoutServer.addWidget(self.btnForward)


        self.verticalLayout.addWidget(self.frameServer)

        self.frameServer1 = QFrame(self.centralwidget)
        self.frameServer1.setObjectName(u"frameServer1")
        self.frameServer1.setFrameShape(QFrame.Shape.StyledPanel)
        self.horizontalLayoutServer1 = QHBoxLayout(self.frameServer1)
        self.horizontalLayoutServer1.setObjectName(u"horizontalLayoutServer1")
        self.inputServerPort = QLineEdit(self.frameServer1)
        self.inputServerPort.setObjectName(u"inputServerPort")

        self.horizontalLayoutServer1.addWidget(self.inputServerPort)

        self.btnStartServer = QPushButton(self.frameServer1)
        self.btnStartServer.setObjectName(u"btnStartServer")

        self.horizontalLayoutServer1.addWidget(self.btnStartServer)


        self.verticalLayout.addWidget(self.frameServer1)

        self.frameClient = QFrame(self.centralwidget)
        self.frameClient.setObjectName(u"frameClient")
        self.frameClient.setFrameShape(QFrame.Shape.StyledPanel)
        self.horizontalLayoutClient = QHBoxLayout(self.frameClient)
        self.horizontalLayoutClient.setObjectName(u"horizontalLayoutClient")
        self.inputClientIP = QLineEdit(self.frameClient)
        self.inputClientIP.setObjectName(u"inputClientIP")

        self.horizontalLayoutClient.addWidget(self.inputClientIP)

        self.inputClientPort = QLineEdit(self.frameClient)
        self.inputClientPort.setObjectName(u"inputClientPort")

        self.horizontalLayoutClient.addWidget(self.inputClientPort)

        self.btnStartClient = QPushButton(self.frameClient)
        self.btnStartClient.setObjectName(u"btnStartClient")

        self.horizontalLayoutClient.addWidget(self.btnStartClient)


        self.verticalLayout.addWidget(self.frameClient)

        self.stop_play = QPushButton(self.centralwidget)
        self.stop_play.setObjectName(u"stop_play")

        self.verticalLayout.addWidget(self.stop_play)

        self.statusLabel = QLabel(self.centralwidget)
        self.statusLabel.setObjectName(u"statusLabel")
        self.statusLabel.setStyleSheet(u"color: #00ff99;")
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.statusLabel)

        self.verticalLayout.setStretch(2, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 640, 24))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Video Streaming TCP - SSL", None))
        self.videoLabel.setText(QCoreApplication.translate("MainWindow", u"Vista de video", None))
        self.btnBackward.setText(QCoreApplication.translate("MainWindow", u"<<", None))
        self.btnPlayPause.setText(QCoreApplication.translate("MainWindow", u"Play", None))
        self.btnForward.setText(QCoreApplication.translate("MainWindow", u">>", None))
        self.inputServerPort.setText(QCoreApplication.translate("MainWindow", u"8080", None))
        self.inputServerPort.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Puerto servidor", None))
        self.btnStartServer.setText(QCoreApplication.translate("MainWindow", u"Iniciar Servidor", None))
        self.inputClientIP.setText(QCoreApplication.translate("MainWindow", u"127.0.0.1", None))
        self.inputClientIP.setPlaceholderText(QCoreApplication.translate("MainWindow", u"IP del servidor", None))
        self.inputClientPort.setText(QCoreApplication.translate("MainWindow", u"8080", None))
        self.inputClientPort.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Puerto del servidor", None))
        self.btnStartClient.setText(QCoreApplication.translate("MainWindow", u"Iniciar Cliente", None))
        self.stop_play.setText(QCoreApplication.translate("MainWindow", u"Detener streamming", None))
        self.statusLabel.setText(QCoreApplication.translate("MainWindow", u"Listo.", None))
    # retranslateUi

