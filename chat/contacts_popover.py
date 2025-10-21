from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
    QPushButton, QFrame, QLabel, QStackedWidget, QHBoxLayout, QCheckBox
)
from PySide6.QtCore import Qt, QPoint, Signal, QSize
from PySide6.QtGui import QPixmap, QCursor, QPainter, QBrush


def circular_pixmap(pixmap, size):
    """Devuelve un QPixmap recortado en círculo"""
    pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    mask = QPixmap(size, size)
    mask.fill(Qt.transparent)

    painter = QPainter(mask)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(Qt.white))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(0, 0, size, size)
    painter.end()

    pixmap.setMask(mask.createMaskFromColor(Qt.transparent, Qt.MaskInColor))
    return pixmap


# ---------------------------------------------------
#  Contact item widgets
# ---------------------------------------------------
class ContactItemWidget(QWidget):
    clicked = Signal()

    """Widget simple para la página 1 (solo nombre e imagen a la izquierda)."""
    def __init__(self, contact_id, name, image_path=None, parent=None):
        super().__init__(parent)
        self.contact_id = contact_id
        self.name = name
        self.image_path = image_path or "images/user.png"

        self.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        # Imagen
        self.avatar = QLabel()
        pix = QPixmap(self.image_path).scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.avatar.setPixmap(circular_pixmap(pix, 36))
        self.avatar.setFixedSize(36, 36)
        layout.addWidget(self.avatar)

        # Nombre
        self.name_label = QLabel(self.name)
        self.name_label.setStyleSheet("border: none; color: white; font-size: 13px; background: transparent;")
        layout.addWidget(self.name_label)

        layout.addStretch()
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class SelectableContactItem(QWidget):
    """Widget para la página 2 (imagen + nombre + checkbox)."""
    def __init__(self, contact_id, name, image_path=None, parent=None):
        super().__init__(parent)
        self.contact_id = contact_id
        self.name = name
        self.image_path = image_path or "images/user.png"

        self.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        # Imagen
        self.avatar = QLabel()
        pix = QPixmap(self.image_path).scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.avatar.setPixmap(circular_pixmap(pix, 36))
        self.avatar.setFixedSize(36, 36)
        layout.addWidget(self.avatar)

        # Nombre
        self.name_label = QLabel(self.name)
        self.name_label.setStyleSheet("border: none; color: white; font-size: 13px; background: transparent;")
        layout.addWidget(self.name_label)

        layout.addStretch()

        # Checkbox
        self.checkbox = QCheckBox()
        layout.addWidget(self.checkbox)
        self.setCursor(QCursor(Qt.PointingHandCursor))


# ---------------------------------------------------
#  Main Popover
# ---------------------------------------------------
class ContactsPopover(QFrame):
    group_created = Signal(dict)
    item_clicked = Signal(dict)
    contacts_changed = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QFrame {
                background-color: #1f1f1f;
                border: 1px solid #333;
            }
            QLineEdit {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 12px;
                padding: 4px 6px;
            }
            QPushButton:hover {
                color: #25D366;
            }
            QListWidget {
                background: #1f1f1f;
                border: none;
            }
            QListWidget::item {
                border: none;
                background: transparent;
                margin: 3px 0;
                padding: 0px;
            }
            QListWidget::item:hover {
                background-color: #2c2c2c;
            }
        """)

        self.current_group_id = None  # 🔹 nuevo campo

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Páginas
        self.pages = QStackedWidget()
        layout.addWidget(self.pages)
        self.page_contacts = QWidget()
        self.page_new_group = QWidget()
        self.setup_contacts_page()
        self.setup_group_page()
        self.pages.addWidget(self.page_contacts)
        self.pages.addWidget(self.page_new_group)

        # Lista de contactos
        self.contacts = []
        self.create_btn.clicked.connect(self.on_create_group)


    def on_create_group(self):
        """Cuando el usuario presiona 'Create'."""
        members = self.get_selected_members()
        group_name = self.group_name_box.text().strip()
        if not group_name or not members:
            return

        data = {
            "group_id": None,  # 🔹 el servidor la llenará después
            "group_name": group_name,
            "members": members
        }
        self.group_created.emit(data)
        self.reset_group_page()
        self.go_to_contacts_page()
        self.close()

    # 🔹 Nuevo método para actualizar desde el servidor
    def on_group_created_from_server(self, group_data):
        """
        Llamado cuando el servidor confirma la creación del grupo y asigna ID.
        group_data = { "group_id": "...", "group_name": "...", "members": [...] }
        """
        print(f"Grupo creado por servidor: {group_data}")
        self.current_group_id = group_data.get("group_id")
        # Aquí podrías actualizar una lista visual de grupos si la tienes,
        # o simplemente emitir una señal global si tu app la necesita.

    # ---------------- CONTACTS PAGE ----------------
    def setup_contacts_page(self):
        layout = QVBoxLayout(self.page_contacts)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        new_group_btn = QPushButton("New group")
        new_group_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 6px;
                color: #25D366;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #2b2b2b; }
        """)
        new_group_btn.clicked.connect(self.go_to_group_page)
        layout.addWidget(new_group_btn)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search name or number")
        layout.addWidget(self.search_box)

        self.contacts_list = QListWidget()
        self.contacts_list.setFocusPolicy(Qt.NoFocus)
        self.contacts_list.setSelectionMode(QListWidget.NoSelection)
        layout.addWidget(self.contacts_list)

        self.search_box.textChanged.connect(self.filter_contacts)

    # ---------------- GROUP PAGE ----------------
    def setup_group_page(self):
        layout = QVBoxLayout(self.page_new_group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        header_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.setStyleSheet("font-size: 11px; color: #bbb;")
        self.back_btn.clicked.connect(self.go_to_contacts_page)

        title = QLabel("New group")
        title.setStyleSheet("font-weight: bold; color: white; font-size: 13px;")

        self.create_btn = QPushButton("Create")
        self.create_btn.setStyleSheet("font-size: 11px; color: #25D366;")

        header_layout.addWidget(self.back_btn)
        header_layout.addStretch()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.create_btn)
        layout.addLayout(header_layout)

        self.group_name_box = QLineEdit()
        self.group_name_box.setPlaceholderText("Group name")
        layout.addWidget(self.group_name_box)

        self.group_search_box = QLineEdit()
        self.group_search_box.setPlaceholderText("Select contacts")
        layout.addWidget(self.group_search_box)

        self.group_contacts_list = QListWidget()
        self.group_contacts_list.setFocusPolicy(Qt.NoFocus)
        self.group_contacts_list.setSelectionMode(QListWidget.NoSelection)
        layout.addWidget(self.group_contacts_list)

        self.group_search_box.textChanged.connect(self.filter_group_contacts)

    # ---------------- PUBLIC METHODS ----------------
    def set_contacts(self, contact_list):
        self.contacts = contact_list or []
        self.populate_contacts(self.contacts_list, ContactItemWidget)
        self.populate_contacts(self.group_contacts_list, SelectableContactItem)
        self.contacts_changed.emit(self.contacts)

    def get_contacts(self):
        return self.contacts

    def add_contact(self, contact_id, name, image_path=None):
        if not any(item.get("id") == contact_id for item in self.contacts):
            new_contact = {"id": contact_id, "name": name, "image": image_path or "images/user.png"}
            self.contacts.append(new_contact)
            self.set_contacts(self.contacts)

    def get_selected_members(self):
        members = []
        for i in range(self.group_contacts_list.count()):
            item = self.group_contacts_list.item(i)
            widget = self.group_contacts_list.itemWidget(item)
            if widget.checkbox.isChecked():
                members.append({
                    "id": widget.contact_id,
                    "name": widget.name_label.text(),
                    "image": widget.avatar.pixmap()
                })
        return members

    # ---------------- EVENTS ----------------
    def on_create_group(self):
        members = self.get_selected_members()
        group_name = self.group_name_box.text().strip()
        if not group_name or not members:
            return
        data = {"group_name": group_name, "members": members}
        self.group_created.emit(data)
        self.reset_group_page()
        self.go_to_contacts_page()
        self.close()

    def on_contact_clicked(self, contact):
        self.item_clicked.emit(contact)
        self.close()

    # ---------------- HELPERS ----------------
    def reset_group_page(self):
        self.group_name_box.clear()
        self.group_search_box.clear()
        for i in range(self.group_contacts_list.count()):
            item = self.group_contacts_list.item(i)
            widget = self.group_contacts_list.itemWidget(item)
            widget.checkbox.setChecked(False)

    def populate_contacts(self, list_widget, widget_class, filtered=None):
        list_widget.clear()
        data = filtered if filtered else self.contacts
        for c in data:
            item = QListWidgetItem()
            item.setFlags(Qt.ItemIsEnabled)
            widget = widget_class(c["id"], c["name"], c.get("image"))
            item.setSizeHint(widget.sizeHint() + QSize(0, 6))
            list_widget.addItem(item)
            list_widget.setItemWidget(item, widget)

            if isinstance(widget, ContactItemWidget):
                widget.clicked.connect(lambda contact=c: self.on_contact_clicked(contact))

    def filter_contacts(self, text):
        filtered = [c for c in self.contacts if text.lower() in c["name"].lower()]
        self.populate_contacts(self.contacts_list, ContactItemWidget, filtered)

    def filter_group_contacts(self, text):
        filtered = [c for c in self.contacts if text.lower() in c["name"].lower()]
        self.populate_contacts(self.group_contacts_list, SelectableContactItem, filtered)

    def go_to_group_page(self):
        self.pages.setCurrentWidget(self.page_new_group)

    def go_to_contacts_page(self):
        self.pages.setCurrentWidget(self.page_contacts)

    def show_above_button(self, button):
        global_pos = button.mapToGlobal(QPoint(0, button.height()))
        self.move(global_pos)
        self.adjustSize()
        self.show()
