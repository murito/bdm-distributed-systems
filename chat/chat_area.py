from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from chat_bubble import ChatBubble

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

    def add_message(self, name, message=None, is_sender=False, file_path=None):
        """Agrega un mensaje o un archivo al chat."""
        bubble = ChatBubble(name, message, is_sender, file_path=file_path)
        self.layout.addWidget(bubble)

        # Scroll automático al final
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def clear_messages(self):
        """Elimina todas las burbujas del chat actual."""
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
