import sqlite3

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QCheckBox, QSpinBox, QLabel,  QVBoxLayout, QFrame, QPushButton, \
    QMainWindow, QListWidget, QListWidgetItem
from PyQt6.QtGui import QFont, QPixmap, QPainterPath, QPainter, QIcon
from PyQt6.QtCore import QRectF, QSize
from functools import partial
from random import randint

class little_card(QWidget):
    def __init__(self, id):
        super().__init__()
        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"SELECT * FROM items WHERE id = {id}")
        data = self.cur.fetchall()
        text, num, photo1, photo2, order_quantity = data[0][1:]

        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('little_card.ui', self)

        self.price.setText(str(num))

        # photo_label = QLabel(self)
        # image = QPixmap(photo1)
        # # уменьшение изображения
        # photo_label.setScaledContents(True)
        #
        # photo_label.setPixmap(image)
        #
        # self.verticalLayout.addWidget(photo_label)

        width = self.photo.size().width()
        height = self.photo.size().height()

        self.photo.setIcon(QIcon(photo1))
        self.photo.setIconSize(QSize(width, height))

        self.show_description_partial = partial(self.show_description, id)
        self.price.clicked.connect(self.show_description_partial)
        self.photo.clicked.connect(self.show_description_partial)

    def show_description(self, id):
        self.w2 = big_card(id)
        self.w2.show()

class big_card(QWidget):
    def __init__(self, id):
        super().__init__()

        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"SELECT * FROM items WHERE id = {id}")
        data = self.cur.fetchall()
        text, num, photo1, photo2, order_quantity = data[0][1:]

        description = text

        try:
            self.cur.execute(f"""SELECT materials.name, models.name, colors.name, length.name, categories.name FROM description 
                    INNER JOIN items ON items.id = description.id
                    INNER JOIN materials ON materials."material id" = description.material
                    INNER JOIN models ON models."models id" = description.model
                    INNER JOIN colors ON colors."colors id" = description.color
                    INNER JOIN length ON length."length id" = description.length
                    INNER JOIN categories ON categories."categoy id" = description.category
                    WHERE items.id = {id}""")

            data = self.cur.fetchall()

            material, model, color, length, category = data[0]

            description = f"Тип товара: платье\nМодель: {model}\nМатериал: {material}\nЦвет: {color}\nДлина: {length}\nКатегория: {category}"
        except Exception as e:
            print(e)

        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('description.ui', self)

        self.name.setText(text)
        self.name.setWordWrap(True)


        # Установить переданные значения
        self.long_description.setText(description)
        self.long_description.setWordWrap(True)

        self.price.setText(str(num))

        self.like.setIcon(QIcon('images/like.png'))
        self.like.setIconSize(QSize(25, 25))

        self.buy.setIcon(QIcon('images/bag.png'))
        self.buy.setIconSize(QSize(25, 25))

        self.photo_label = QLabel(self)
        # self.photo_label.setScaledContents(True)

        self.original_image = QPixmap(photo1)
        self.hover_image = QPixmap(photo2)
        self.photo_label.setPixmap(self.original_image)

        # self.photo_label.installEventFilter(self)

        # уменьшение изображения
        self.photo_label.setScaledContents(True)
        self.verticalLayout.addWidget(self.photo_label)

        # self.conn = sqlite3.connect('cards.db')
        # self.cur = self.conn.cursor()

        self.photo_counter = 0

        self.next1.clicked.connect(self.update_photo)
        self.prev1.clicked.connect(self.update_photo)

        ids = [randint(1,47) for i in range(5)]

        for i in ids:
            widget = little_card(i)
            self.horizontalLayout.addWidget(widget)

    def update_photo(self):
        sender = self.sender()
        if sender == self.next1 and self.photo_counter == 0 or sender == self.prev1 and self.photo_counter == 0:
            self.photo_counter += 1
            self.photo_label.setPixmap(self.hover_image)
        elif sender == self.prev1 and self.photo_counter == 1 or sender == self.next1 and self.photo_counter == 1:
            self.photo_counter -= 1
            self.photo_label.setPixmap(self.original_image)
    # def eventFilter(self, obj, event):
    #     if obj == self.photo_label:
    #         if event.type() == QEvent.Enter:
    #             self.photo_label.setPixmap(self.hover_image)
    #         elif event.type() == QEvent.Leave:
    #             self.photo_label.setPixmap(self.original_image)
    #
    #     return super(big_card, self).eventFilter(obj, event)


class card(QWidget):
    def __init__(self, id):
        super().__init__()
        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        # Берем первые 5 товаров из бд
        self.cur.execute(f"SELECT * FROM items WHERE id = {id}")
        data = self.cur.fetchall()
        text, num, photo1, photo2, order_quantity = data[0][1:]

        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('card.ui', self)

        # Установить переданные значения
        self.name.setText(text)

        self.price.setText(str(num))

        photo_label = QLabel(self)
        image = QPixmap(photo1)
        # уменьшение изображения
        photo_label.setScaledContents(True)

        photo_label.setPixmap(image)

        self.verticalLayout.addWidget(photo_label)

        self.show_description_partial = partial(self.show_description, id)
        self.details.clicked.connect(self.show_description_partial)
        self.price.clicked.connect(self.show_description_partial)

    def show_description(self, id):
        self.w2 = big_card(id)
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
            widget = card(row[0])
            self.gridLayout.addWidget(widget, 0, 4-i)

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
            widget = card(row[0])
            self.gridLayout.addWidget(widget, 0, 4-i)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())