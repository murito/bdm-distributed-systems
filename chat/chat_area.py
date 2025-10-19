from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from chat_bubble import ChatBubble

class ChatArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setStyleSheet("background: transparent; border: none;")

        # Crear un container interno dedicado
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(5)  # separación entre burbujas

        self.setWidget(self.container)

    def add_message(self, name, message, is_sender=False):
        bubble = ChatBubble(name, message, is_sender)
        self.layout.addWidget(bubble)

        # Scroll automático al final
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

