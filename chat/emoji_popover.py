from PySide6.QtWidgets import QWidget, QPushButton, QGridLayout, QScrollArea, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QBrush, QColor

class EmojiPopover(QWidget):
    def __init__(self, target_lineedit=None):
        super().__init__(None)  # sin parent
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.target_lineedit = target_lineedit

        # ScrollArea para muchos emojis
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("border:none;")

        container = QWidget()
        scroll.setWidget(container)

        layout = QGridLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10,10,10,10)
        container.setLayout(layout)

        # Lista de emojis
        self.emojis = [
            # Originales
            "😀","😂","😍","😎","😭","😡","👍","👎","🙏","🎉","💯","🔥",
            "😅","😆","😉","🙃","😴","🤯","🤩","🥳","🤔","😇","🤪","🤬",

            # Nuevos agregados
            "😋","😜","🤤","😏","😌","😔","😢","🥺","🤗","🤭","🫣","😱",
            "😳","🥵","🥶","😷","🤒","🤕","🤠","😈","👻","💀","☠️","🤡",
            "💩","👽","🤖","🎃","😺","😸","😹","😻","😼","😽","🙀","😿",
            "😾","👐","👏","🤝","💪","🖤","❤️","💔","💖","💗","💙"
        ]

        row, col = 0, 0
        for e in self.emojis:
            btn = QPushButton(e)
            btn.setFixedSize(32,32)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 20px;
                    background: none;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                    border-radius: 5px;
                }
            """)
            btn.clicked.connect(lambda checked, emoji=e: self.insert_emoji(emoji))
            layout.addWidget(btn,row,col)
            col += 1
            if col >= 6:
                col = 0
                row += 1

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def insert_emoji(self, emoji):
        if self.target_lineedit:
            cursor = self.target_lineedit.cursorPosition()
            text = self.target_lineedit.text()
            self.target_lineedit.setText(text[:cursor]+emoji+text[cursor:])
            self.target_lineedit.setCursorPosition(cursor+len(emoji))
        self.hide()

    def paintEvent(self,event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor("white")))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(),10,10)

    def show_above_button(self, button):
        button_center = button.mapToGlobal(button.rect().center())
        self.layout().activate()
        self.adjustSize()
        popover_width = self.width()
        popover_height = self.height()
        x = button_center.x() - popover_width//2
        y = button_center.y() - popover_height
        self.move(x,y)
        self.show()
