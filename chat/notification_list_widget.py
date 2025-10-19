from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from notification_widget import NotificationWidget


class NotificationListWidget(QWidget):
    def __init__(self, scroll_area: QScrollArea):
        super().__init__()

        # Contenedor interno donde se colocan las notificaciones
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)
        self.layout.addStretch()

        # Configurar el scroll area
        scroll_area.setWidget(self.container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

    def add_notification(self, icon_path, title, description, date):
        notif = NotificationWidget()
        notif.setData(icon_path, title, description, date)
        self.layout.insertWidget(self.layout.count() - 1, notif)
        return notif
