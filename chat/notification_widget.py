from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QPixmap, QFont, QPainter, QColor
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, Signal


class NotificationWidget(QWidget):
    clicked = Signal()  # 🔹 Nuevo signal para click

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Propiedades de estilo ---
        self._bg_color = QColor(43, 43, 43, 230)   # color inicial
        self.hover_color = QColor(70, 70, 70, 230) # color al hacer hover
        self.setFixedHeight(80)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        # --- Layout principal ---
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(15, 10, 15, 10)
        self.main_layout.setSpacing(10)

        # --- Icono ---
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)
        self.icon_label.setStyleSheet("background: transparent;")
        self.main_layout.addWidget(self.icon_label)

        # --- Texto (título + descripción) ---
        self.text_layout = QVBoxLayout()
        self.title_label = QLabel("App Name")
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.title_label.setStyleSheet("background: transparent; color: white;")

        self.desc_label = QLabel("Description goes here...")
        self.desc_label.setFont(QFont("Arial", 10))
        self.desc_label.setStyleSheet("background: transparent; color: #bfbfbf;")
        self.desc_label.setWordWrap(True)

        self.text_layout.addWidget(self.title_label)
        self.text_layout.addWidget(self.desc_label)
        self.main_layout.addLayout(self.text_layout)

        # --- Fecha ---
        self.date_label = QLabel("00/00/00")
        self.date_label.setFont(QFont("Arial", 10))
        self.date_label.setStyleSheet("background: transparent; color: #bfbfbf;")
        self.date_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.date_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
        self.main_layout.addWidget(self.date_label)

    # ---------------------------------------------------------------------
    # 🔹 Método público para actualizar datos
    # ---------------------------------------------------------------------
    def setData(self, icon_path, title, description, date):
        pixmap = QPixmap(icon_path).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(pixmap)
        self.title_label.setText(title)
        self.desc_label.setText(description)
        self.date_label.setText(date)

    # ---------------------------------------------------------------------
    # 🔹 Propiedad animada del color de fondo
    # ---------------------------------------------------------------------
    def getBgColor(self):
        return self._bg_color

    def setBgColor(self, color):
        self._bg_color = color
        self.update()

    bgColor = Property(QColor, getBgColor, setBgColor)

    # ---------------------------------------------------------------------
    # 🔹 Eventos del mouse para animación hover
    # ---------------------------------------------------------------------
    def enterEvent(self, event):
        self.animate_bg(self.hover_color)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animate_bg(QColor(43, 43, 43, 230))
        super().leaveEvent(event)

    def animate_bg(self, target_color):
        self.anim = QPropertyAnimation(self, b"bgColor")
        self.anim.setDuration(200)
        self.anim.setStartValue(self._bg_color)
        self.anim.setEndValue(target_color)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.start()

    # ---------------------------------------------------------------------
    # 🔹 Dibujo personalizado del fondo con color actual
    # ---------------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self._bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)
        super().paintEvent(event)

    # ---------------------------------------------------------------------
    # 🔹 Evento click
    # ---------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
