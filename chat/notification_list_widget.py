from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from PySide6.QtCore import Signal
from notification_widget import NotificationWidget


class NotificationListWidget(QWidget):
    notif_clicked = Signal(dict)

    def __init__(self, scroll_area: QScrollArea):
        super().__init__()

        self.notifications = {}  # 🔹 Diccionario para evitar duplicados por ID

        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)
        self.layout.addStretch()

        scroll_area.setWidget(self.container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

    def add_notification(self, icon_path, title, description, date, notif_id=None):
        """Agrega una notificación si su ID no existe."""
        notif_id = notif_id or f"{title}_{date}"

        if notif_id in self.notifications:
            print(f"⚠️ Notificación con ID '{notif_id}' ya existe. Ignorada.")
            return None

        notif = NotificationWidget(notif_id)
        notif.setData(icon_path, title, description, date, notif_id)
        notif.clicked.connect(lambda: self.clicked(notif.data))

        self.layout.insertWidget(self.layout.count() - 1, notif)
        self.notifications[notif_id] = notif  # 🔹 Guardar referencia

        return notif

    def clicked(self, notif):
        self.notif_clicked.emit(notif)
