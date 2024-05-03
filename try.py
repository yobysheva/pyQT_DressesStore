import sqlite3

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QCheckBox, QSpinBox, QLabel, QVBoxLayout, QFrame, QPushButton, \
    QMainWindow, QListWidget, QListWidgetItem
from PyQt6.QtGui import QFont, QPixmap, QPainterPath, QPainter
from PyQt6.QtCore import QRectF

class MyWidget(QWidget):
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
            widget = MyWidget('futbolka.png', row[1], row[2])
            self.gridLayout.addWidget(widget, 0, i)

        self.page = 0
        # кнопка для предлючения
        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self.update_data)
        self.gridLayout.addWidget(self.update_button, 1, 0, 1, 5)

    def update_data(self):
        self.cur.execute("SELECT * FROM items LIMIT 5 OFFSET 5")
        data = self.cur.fetchall()

        for i, row in enumerate(data):
            widget = MyWidget('dress1.jpg', row[1],row[2])
            self.gridLayout.addWidget(widget, 0, i)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())