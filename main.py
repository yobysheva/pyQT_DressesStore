import sqlite3

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QCheckBox, QSpinBox, QLabel,  QVBoxLayout, QFrame, QPushButton, \
    QMainWindow, QListWidget, QListWidgetItem
from PyQt6.QtGui import QFont, QPixmap, QPainterPath, QPainter, QIcon
from PyQt6.QtCore import QRectF, QSize, QEvent
from functools import partial
from random import randint

class little_card(QWidget):
    def __init__(self, id):
        super().__init__()

        # выгрузка данных для карточки товара из базы данных
        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"SELECT * FROM items WHERE id = {id}")
        data = self.cur.fetchall()
        text, num, photo1, photo2, order_quantity = data[0][1:]

        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('little_card.ui', self)

        # поставили значения из бд в соответствующие поля
        self.price.setText(str(num))

        # предыдущий метод вставки изображния в мини-карточку
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

        #ставим кликбельное изображение в мини-карточку
        self.photo.setIcon(QIcon(photo1))
        self.photo.setIconSize(QSize(width, height))

        # открываем большую карточку товара при нажатии на фото или на цену
        self.show_description_partial = partial(self.show_description, id)
        self.price.clicked.connect(self.show_description_partial)
        self.photo.clicked.connect(self.show_description_partial)

    # открываем новое окно
    def show_description(self, id):
        self.w2 = big_card(id)
        self.w2.show()


class big_card(QWidget):
    def __init__(self, id):
        super().__init__()
        # выгрузка данных для карточки товара из базы данных
        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"SELECT * FROM items WHERE id = {id}")
        data = self.cur.fetchall()
        text, num, photo1, photo2, order_quantity = data[0][1:]

        description = text

        #составление описания при помощи таблицы description
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

            description = f"Тип товара: платье\nМодель: {model}\nМатериал: {material}\nЦвет: {color}\n" \
                          f"Длина: {length}\nКатегория: {category}"
        except Exception as e:
            print(e)

        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('description.ui', self)

        # поставили значения из бд в соответствующие поля
        self.name.setText(text)
        self.name.setWordWrap(True)

        # Установить переданные значения
        self.long_description.setText(description)
        self.long_description.setWordWrap(True)

        self.price.setText(str(num))

        # иконки для кнопок корзина и избранное
        self.like.setIcon(QIcon('images/like.png'))
        self.like.setIconSize(QSize(25, 25))

        self.buy.setIcon(QIcon('images/bag.png'))
        self.buy.setIconSize(QSize(25, 25))

        self.photo_label = QLabel(self)
        # self.photo_label.setScaledContents(True)

        # подключение к фотографиям айтемов из db
        self.original_image = QPixmap(photo1)
        self.hover_image = QPixmap(photo2)
        self.photo_label.setPixmap(self.original_image)

        # уменьшение изображения
        self.photo_label.setScaledContents(True)
        self.verticalLayout.addWidget(self.photo_label)

        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        # пролистывание фоторафий
        self.photo_counter = 0

        self.next1.clicked.connect(self.update_photo)
        self.prev1.clicked.connect(self.update_photo)

        max_item = self.cur.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        ids = [randint(1, max_item) for i in range(5)]

        # добавление рекомендаций
        for i in ids:
            widget = little_card(i)
            self.horizontalLayout.addWidget(widget)

    # листание фото (пока по нажатию, но должно быть по наведению)
    def update_photo(self):
        sender = self.sender()
        if sender == self.next1 and self.photo_counter == 0 or sender == self.prev1 and self.photo_counter == 0:
            self.photo_counter += 1
            self.photo_label.setPixmap(self.hover_image)
        elif sender == self.prev1 and self.photo_counter == 1 or sender == self.next1 and self.photo_counter == 1:
            self.photo_counter -= 1
            self.photo_label.setPixmap(self.original_image)


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

        # открываем большую карточку товара при нажатии на подробнее или на цену
        self.show_description_partial = partial(self.show_description, id)
        self.details.clicked.connect(self.show_description_partial)
        self.price.clicked.connect(self.show_description_partial)

    # открываем новое окно
    def show_description(self, id):
        self.w2 = big_card(id)
        self.w2.show()


class korzina_widget(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()
        id = 1

        # Берем первые 5 товаров из бд
        self.cur.execute(f"SELECT * FROM items WHERE id = {id}")
        data = self.cur.fetchall()
        text, num, photo1, photo2, order_quantity = data[0][1:]

        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('korzina.ui', self)

        # иконки для кнопок корзина, вход и избранное
        self.like.setIcon(QIcon('images/like.png'))
        self.like.setIconSize(QSize(20, 20))

        self.korzina.setIcon(QIcon('images/bag.png'))
        self.korzina.setIconSize(QSize(20, 20))

        self.log_in.setIcon(QIcon('images/log_in.png'))
        self.log_in.setIconSize(QSize(20, 20))

        max_item = self.cur.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        ids = [randint(1, max_item) for i in range(10)]

        # добавление рекомендаций
        for i in ids:
            widget = little_card(i)
            self.horizontalLayout_2.addWidget(widget)
            
        ids = [randint(1, max_item) for i in range(10)]

        # добавление рекомендаций
        for i in ids:
            widget = little_card(i)
            self.horizontalLayout_4.addWidget(widget)

        # кнопка назад закрывает окно
        self.back.clicked.connect(self.close)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузить пользовательский интерфейс главного окна из файла .ui
        uic.loadUi('MainWindow.ui', self)

        # иконки для кнопок корзина, вход и избранное
        self.like.setIcon(QIcon('images/like.png'))
        self.like.setIconSize(QSize(20, 20))

        self.korzina.setIcon(QIcon('images/bag.png'))
        self.korzina.setIconSize(QSize(20, 20))

        self.log_in.setIcon(QIcon('images/log_in.png'))
        self.log_in.setIconSize(QSize(20, 20))

        self.korzina.clicked.connect(self.open_korzina)

        # Connect to the database
        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        # Берем первые 5 товаров из бд
        self.cur.execute("SELECT * FROM items LIMIT 5")
        data = self.cur.fetchall()

        for i, row in enumerate(data):
            widget = card(row[0])
            self.gridLayout.addWidget(widget, 0, 4 - i)

        self.page = 0
        self.message = ' '

        # листание страниц по нажатию на кнопки
        self.update_data_partial = partial(self.update_data, self.message)
        self.next.clicked.connect(self.update_data_partial)
        self.prev.clicked.connect(self.update_data_partial)

        self.summer.clicked.connect(self.categoriesFilter)
        self.ofice.clicked.connect(self.categoriesFilter)
        self.evening.clicked.connect(self.categoriesFilter)

    # функция для вывода 5 товаров по страницам
    def update_data(self, message):
        sender = self.sender()
        # количество товаров в таблице
        max_pages = self.cur.execute(f"SELECT COUNT(*) FROM items {self.message}").fetchone()[0] // 5
        if sender == self.next and self.page < max_pages:
            self.page += 1
        elif sender == self.prev and self.page > 0:
            self.page -= 1

        self.cur.execute(f"SELECT * FROM items {self.message} LIMIT 5 OFFSET 5*{self.page}")
        data = self.cur.fetchall()
        # добавление товаров в сетку
        for i, row in enumerate(data):
            widget = card(row[0])
            self.gridLayout.addWidget(widget, 0, 4 - i)

    def categoriesFilter(self):
        self.page = 0
        category = self.sender().text()
        self.message = f""" 
    INNER JOIN description ON description.id = items.id
    INNER JOIN categories ON categories."categoy id" = description.category
    WHERE categories.name = '{category}'"""
        self.update_data(self.message)

    # открывается корзина, нужно сделать так, чтобы закрывалось изначальное окно
    def open_korzina(self):
        try:
            self.korzina_window = korzina_widget()
            self.korzina_window.show()
        except Exception as e:
            print(e)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())