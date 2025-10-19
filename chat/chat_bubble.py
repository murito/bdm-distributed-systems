from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSizePolicy

class ChatBubble(QWidget):
    def __init__(self, name, message, is_sender=False, max_width=400):
        super().__init__()
        self.is_sender = is_sender

        # Contenedor principal de la burbuja
        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(5, 2, 5, 2)

        # Widget interno que será la burbuja
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

        # Layout vertical para nombre + mensaje
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(8, 4, 8, 4)
        content_layout.setSpacing(2)

        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: bold;")
        message_label = QLabel(message)
        message_label.setWordWrap(True)

        content_layout.addWidget(name_label)
        content_layout.addWidget(message_label)

        bubble_widget.setLayout(content_layout)

        # Alineación izquierda/derecha
        if is_sender:
            outer_layout.addStretch()
            outer_layout.addWidget(bubble_widget)
        else:
            outer_layout.addWidget(bubble_widget)
            outer_layout.addStretch()

        self.setLayout(outer_layout)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
