from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSizePolicy
from PySide6.QtGui import QPixmap, QCursor
from PySide6.QtCore import Qt
import os
import subprocess
import platform

class ChatBubble(QWidget):
    def __init__(self, name, message=None, is_sender=False, max_width=400, file_path=None, file_icon_path="images/file.png"):
        super().__init__()
        self.is_sender = is_sender
        self.file_path = file_path

        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(5, 2, 5, 2)

        bubble_widget = QFrame()
        bubble_widget.setStyleSheet("""
            QFrame {
                border-radius: 10px;
                background-color: %s;
            }
            QLabel {
                color: white;
            }
        """ % ("#4CAF50" if is_sender else "#333333"))

        bubble_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        bubble_widget.setMaximumWidth(max_width)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(8, 4, 8, 4)
        content_layout.setSpacing(4)

        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: bold;")
        content_layout.addWidget(name_label)

        if file_path:  # burbuja de archivo
            icon_label = QLabel()
            icon_pixmap = QPixmap(file_icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(icon_pixmap)
            icon_label.setCursor(QCursor(Qt.PointingHandCursor))
            icon_label.mousePressEvent = self.open_file_location
            content_layout.addWidget(icon_label, alignment=Qt.AlignCenter)

            # Nombre del archivo
            filename = os.path.basename(file_path)
            file_label = QLabel(filename)
            file_label.setStyleSheet("color: white; font-size: 12px;")
            file_label.setWordWrap(True)
            file_label.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(file_label)

        else:  # burbuja de texto normal
            message_label = QLabel(message)
            message_label.setWordWrap(True)
            content_layout.addWidget(message_label)

        bubble_widget.setLayout(content_layout)

        if is_sender:
            outer_layout.addStretch()
            outer_layout.addWidget(bubble_widget)
        else:
            outer_layout.addWidget(bubble_widget)
            outer_layout.addStretch()

        self.setLayout(outer_layout)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def open_file_location(self, event):
        """Abre la carpeta donde se descargó el archivo y selecciona el archivo."""
        if not self.file_path or not os.path.exists(self.file_path):
            return

        folder = os.path.dirname(self.file_path)
        if platform.system() == "Windows":
            subprocess.run(f'explorer /select,"{self.file_path}"')
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", folder])
        else:  # Linux
            subprocess.run(["xdg-open", folder])
