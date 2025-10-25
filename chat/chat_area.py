from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from chat_bubble import ChatBubble, FileBubble
import os

class ChatArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setStyleSheet("background: transparent; border: none;")

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(5)

        self.setWidget(self.container)

        # map file_id -> FileBubble
        self.file_bubbles = {}

    def add_message(self, user_id, name, message=None, is_sender=False, file_path=None, file_id=None, filename=None, upload_tag=None):
        """Agrega un mensaje (texto) o un archivo. Si es archivo, usa FileBubble."""
        if file_path or filename or upload_tag:
            fb = FileBubble(user_id, name, filename if filename else (file_path and os.path.basename(file_path)), file_id=file_id, is_sender=is_sender)
            self.layout.addWidget(fb)
            # register under file_id if present, otherwise under upload_tag if provided
            if file_id:
                self.file_bubbles[file_id] = fb
            elif upload_tag:
                self.file_bubbles[upload_tag] = fb
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
            return fb
        else:
            bubble = ChatBubble(name, message, is_sender)
            self.layout.addWidget(bubble)
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
            return bubble

    def update_progress(self, file_id, percent):
        if file_id in self.file_bubbles:
            self.file_bubbles[file_id].set_progress(percent)

    def mark_completed(self, file_id, local_path=None):
        if file_id in self.file_bubbles:
            self.file_bubbles[file_id].mark_completed(local_path)

    def clear_messages(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.file_bubbles.clear()
