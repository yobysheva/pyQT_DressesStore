import sqlite3

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QCheckBox, QSpinBox, QLabel,  QVBoxLayout, QFrame, QPushButton, \
    QMainWindow, QListWidget, QListWidgetItem, QDialog
from PyQt6.QtGui import QFont, QPixmap, QPainterPath, QPainter, QIcon
from PyQt6.QtCore import QRectF, QSize, QEvent, QSequentialAnimationGroup, QPropertyAnimation, QRect
from functools import partial
from random import randint
def QWidget1(QWidget):
    def __init__(self, id):
        super().__init__()
        # Класс анимации прозрачности окна
        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(250)  # Продолжительность: 1 секунда

        # Выполните постепенное увеличение
        self.doShow()

    def doShow(self):
        try:
            self.animation.finished.disconnect(self.close)
        except:
            pass
        self.animation.stop()
        # Диапазон прозрачности постепенно увеличивается от 0 до 1.
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def doClose(self):
        self.animation.stop()
        self.animation.finished.connect(self.close)  # Закройте окно, когда анимация будет завершена
        # Диапазон прозрачности постепенно уменьшается с 1 до 0.
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.start()

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

        # Класс анимации прозрачности окна
        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(250)  # Продолжительность: 1 секунда

        # Выполните постепенное увеличение
        self.doShow()

    def doShow(self):
        try:
            self.animation.finished.disconnect(self.close)
        except:
            pass
        self.animation.stop()
        # Диапазон прозрачности постепенно увеличивается от 0 до 1.
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def doClose(self):
        self.animation.stop()
        self.animation.finished.connect(self.close)  # Закройте окно, когда анимация будет завершена
        # Диапазон прозрачности постепенно уменьшается с 1 до 0.
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.start()

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

class registration_dialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('registration_dialog.ui', self) # загружаем UI файл в текущий виджет

class enter_dialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('enter_dialog.ui', self)  # загружаем UI файл в текущий виджет

class enter_or_registration_dialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('enter_or_registration.ui', self) # загружаем UI файл в текущий виджет
        self.registrate.clicked.connect(self.registration)
        self.enter.clicked.connect(self.do_enter)

    def registration(self):
        self.w2 = registration_dialog()
        self.close()
        self.w2.exec()

    def do_enter(self):
        self.w2 = enter_dialog()
        self.close()
        self.w2.exec()

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
        self.log_in.clicked.connect(self.enter_or_registration)

        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(250)  # Продолжительность: 1 секунда

        # Выполните постепенное увеличение
        self.doShow()

    def doShow(self):
        try:
            self.animation.finished.disconnect(self.close)
        except:
            pass
        self.animation.stop()
        # Диапазон прозрачности постепенно увеличивается от 0 до 1.
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def doClose(self):
        self.animation.stop()
        self.animation.finished.connect(self.close)  # Закройте окно, когда анимация будет завершена
        # Диапазон прозрачности постепенно уменьшается с 1 до 0.
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.start()

    def enter_or_registration(self):
        self.w2 = enter_or_registration_dialog()
        self.w2.exec()


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
        self.log_in.clicked.connect(self.enter_or_registration)

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

    def enter_or_registration(self):
        self.w2 = enter_or_registration_dialog()
        self.w2.exec()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())