import sqlite3

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QCheckBox, QSpinBox, QLabel,  QVBoxLayout, QFrame, QPushButton, \
    QMainWindow, QListWidget, QListWidgetItem
from PyQt6.QtGui import QFont, QPixmap, QPainterPath, QPainter, QIcon
from PyQt6.QtCore import QRectF, QSize
from functools import partial

class big_card(QWidget):
    def __init__(self, photo, text, num):
        super().__init__()

        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('description.ui', self)

        self.name.setText(text)
        self.name.setWordWrap(True)

        # Установить переданные значения
        self.long_description.setText(text)

        self.price.setText(str(num))

        self.like.setIcon(QIcon('images/like.png'))
        self.like.setIconSize(QSize(25, 25))

        self.buy.setIcon(QIcon('images/bag.png'))
        self.buy.setIconSize(QSize(25, 25))

        photo_label = QLabel(self)
        image = QPixmap(photo)
        # уменьшение изображения
        photo_label.setScaledContents(True)

        photo_label.setPixmap(image)

        self.verticalLayout.addWidget(photo_label)


class Card(QWidget):
    def __init__(self, photo, text, num):
        super().__init__()

        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('card.ui', self)

        # Установить переданные значения
        self.name.setText(text)

        self.price.setText(str(num))

        photo_label = QLabel(self)
        image = QPixmap(photo)
        # уменьшение изображения
        photo_label.setScaledContents(True)

        photo_label.setPixmap(image)

        self.verticalLayout.addWidget(photo_label)

        self.show_description_partial = partial(self.show_description, photo, text, num)
        self.details.clicked.connect(self.show_description_partial)

    def show_description(self, photo, text, num):
        self.w2 = big_card(photo, text, num)
        self.w2.show()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузить пользовательский интерфейс главного окна из файла .ui
        uic.loadUi('MainWindow.ui', self)

        # Connect to the database
        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        # Берем первые 5 товаров из бд
        self.cur.execute("SELECT * FROM items LIMIT 5")
        data = self.cur.fetchall()

        for i, row in enumerate(data):
            widget = Card(f'{row[3]}', row[1], row[2])
            self.gridLayout.addWidget(widget, 0, i)

        self.page = 0

        self.next.clicked.connect(self.update_data)
        self.prev.clicked.connect(self.update_data)

    def update_data(self):
        sender = self.sender()
        max_pages = self.cur.execute("SELECT COUNT(*) FROM items").fetchone()[0] // 5
        if sender == self.next and self.page < max_pages:
            self.page += 1
        elif sender == self.prev and self.page > 0:
            self.page -= 1

        self.cur.execute(f"SELECT * FROM items LIMIT 5 OFFSET 5*{self.page}")
        data = self.cur.fetchall()

        for i, row in enumerate(data):
            widget = Card(f'{row[3]}', row[1],row[2])
            self.gridLayout.addWidget(widget, 0, 4-i)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())