from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSizePolicy, QProgressBar
from PySide6.QtGui import QCursor
from PySide6.QtCore import Qt
import os
import subprocess
import platform

DOWNLOADS_DIR = os.path.join(os.getcwd(), "downloads")

class ChatBubble(QWidget):
    def __init__(self, name, message=None, is_sender=False, max_width=400):
        super().__init__()
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
        """ % ("#4CAF50" if is_sender else "#3A3A3A"))

        bubble_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        bubble_widget.setMaximumWidth(max_width)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(8, 4, 8, 4)
        content_layout.setSpacing(4)

        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: bold;")
        content_layout.addWidget(name_label)

        if message:
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

class FileBubble(QWidget):
    def __init__(self, user_id, name, filename, file_id=None, client_tag=None, is_sender=False, max_width=420):
        super().__init__()
        self.file_id = file_id
        self.client_tag = client_tag
        self.filename = filename
        self.is_sender = is_sender
        self.local_path = None
        self.completed = False
        self.user_id = user_id

        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(5, 2, 5, 2)

        bubble_widget = QFrame()
        bubble_widget.setStyleSheet(f"""
            QFrame {{
                border-radius: 10px;
                background-color: {"#4CAF50" if is_sender else "#3A3A3A"};
            }}
            QLabel {{
                color: white;
            }}
        """)
        bubble_widget.setMaximumWidth(max_width)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(8, 6, 8, 6)
        content_layout.setSpacing(6)

        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: bold;")
        content_layout.addWidget(name_label)

        file_label = QLabel(filename)
        file_label.setWordWrap(True)
        content_layout.addWidget(file_label)

        # Reemplazamos progressbar por label interactivo
        self.progress_label = QLabel("Preparando...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("background-color: rgba(0,0,0,0.2); padding: 2px; border-radius: 4px;")
        self.progress_label.setCursor(QCursor(Qt.ArrowCursor))
        content_layout.addWidget(self.progress_label)

        bubble_widget.setLayout(content_layout)

        if is_sender:
            outer_layout.addStretch()
            outer_layout.addWidget(bubble_widget)
        else:
            outer_layout.addWidget(bubble_widget)
            outer_layout.addStretch()

        self.setLayout(outer_layout)

    def set_progress(self, percent):
        percent = max(0, min(100, int(percent)))
        if not self.completed:
            self.progress_label.setText(f"{percent}%")

    def mark_completed(self, local_path=None):
        self.completed = True

        # Si es sender, creamos ruta "virtual" para abrir carpeta
        if self.is_sender and not local_path:
            user_folder = os.path.expanduser(f"{DOWNLOADS_DIR}/{self.user_id}/")
            os.makedirs(user_folder, exist_ok=True)
            local_path = os.path.join(user_folder, self.filename)

        if local_path:
            self.local_path = local_path
            self.progress_label.setText("✅ Abrir archivo")
            self.progress_label.setCursor(QCursor(Qt.PointingHandCursor))
            self.progress_label.mousePressEvent = lambda e: self._open_file()
        else:
            self.progress_label.setText("Completado ✅")
            self.progress_label.setCursor(QCursor(Qt.ArrowCursor))

    def setup_click(self, local_path=None):
            """Asigna evento click y cursor para abrir archivo/carpeta."""
            if local_path and os.path.exists(local_path):
                self.local_path = local_path
                self.progress_label.setText("✅ Abrir archivo")
                self.progress_label.setCursor(QCursor(Qt.PointingHandCursor))
                self.progress_label.mousePressEvent = lambda e: self._open_file()
            elif self.completed:
                self.progress_label.setText("Completado ✅")
                self.progress_label.setCursor(QCursor(Qt.ArrowCursor))

    def _open_file(self):
        if not self.local_path:
            print("⚠️ No hay ruta local para abrir.")
            return

        path = f"{DOWNLOADS_DIR}/{self.user_id}/"
        folder = os.path.dirname(path)

        try:
            if platform.system() == "Darwin":
                subprocess.run(["open", "-R", path])
            elif platform.system() == "Windows":
                subprocess.Popen(["explorer", "/select,", path])
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            print("❌ Error abriendo archivo:", e)


