from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QHBoxLayout, QWidget
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
import os


class UserSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # --- Fondo translúcido ---
        backdrop = QWidget(self)
        backdrop.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(backdrop)

        # --- Contenedor principal ---
        self.container = QWidget(backdrop)
        self.container.setFixedWidth(340)
        self.container.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 12px;
                color: #222;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #222;
            }
            QLineEdit {
                font-size: 14px;
                color: #222;
                padding: 6px 8px;
                border: 1px solid #CCC;
                border-radius: 6px;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:disabled {
                background-color: gray;
            }
        """)

        # --- Botón “X” redondo flotante sobre el backdrop ---
        self.close_btn = QPushButton("✕", backdrop)
        self.close_btn.setFixedSize(36, 36)

        # Posición flotante sobre el contenedor
        self.close_btn.move(
            self.container.x() + self.container.width() - 18,  # 18 para centrar sobre el borde
            self.container.y()                             # -18 para que sobresalga arriba
        )
        self.close_btn.raise_()
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #666;   /* gris */
                color: white;             /* X blanca */
                font-size: 20px;
                font-weight: bold;
                border: none;
                border-radius: 18px;      /* círculo */
            }
        """)
        self.close_btn.clicked.connect(self.reject)

        # --- Elementos del formulario ---
        self.nickname_input = QLineEdit("Jhon Doe")
        self.nickname_input.setPlaceholderText("Ingresa tu nickname")

        self.image_label = QLabel()
        self.image_label.setFixedSize(64, 64)
        self.image_label.setStyleSheet("background-color: #EEE; border-radius: 32px;")
        self.image_label.setAlignment(Qt.AlignCenter)

        # Imagen por defecto
        default_image = "images/user.png"
        if os.path.exists(default_image):
            pixmap = QPixmap(default_image).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
            self.image_path = default_image
        else:
            self.image_path = ""

        self.image_button = QPushButton("Seleccionar imagen")
        self.image_button.clicked.connect(self.choose_image)

        self.save_button = QPushButton("Guardar")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.accept)

        # --- Layout de contenido interno ---
        inner_layout = QVBoxLayout(self.container)
        inner_layout.setContentsMargins(20, 40, 20, 20)  # margen superior mayor (por la X)
        inner_layout.setSpacing(10)

        title_label = QLabel("Configura tu perfil")
        inner_layout.addWidget(title_label)
        inner_layout.addWidget(self.nickname_input)

        img_layout = QHBoxLayout()
        img_layout.addWidget(self.image_label)
        img_layout.addWidget(self.image_button)
        inner_layout.addLayout(img_layout)

        inner_layout.addSpacing(10)
        inner_layout.addWidget(self.save_button)

        # --- Centrar el contenedor ---
        wrapper_layout = QVBoxLayout(backdrop)
        wrapper_layout.setAlignment(Qt.AlignCenter)
        wrapper_layout.addWidget(self.container)

        # --- Conexión de eventos ---
        self.nickname = ""
        self.nickname_input.textChanged.connect(self.validate)

    def validate(self):
        """Activa el botón Guardar solo si hay nickname."""
        self.save_button.setEnabled(bool(self.nickname_input.text().strip()))

    def choose_image(self):
        """Seleccionar y redimensionar imagen."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen", "", "Imágenes (*.png *.jpg *.jpeg)"
        )
        if not file_path:
            return

        image = QImage(file_path)
        if image.isNull():
            return

        if image.width() > 64 or image.height() > 64:
            image = image.scaled(64, 64, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        pixmap = QPixmap.fromImage(image).scaled(64, 64, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)
        self.image_path = file_path
        self.validate()

    def accept(self):
        """Guardar nickname e imagen al cerrar."""
        self.nickname = self.nickname_input.text().strip()
        if not self.image_path:
            self.image_path = "images/user.png"
        super().accept()
