import sqlite3

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPixmap,  QIcon
from PyQt6.QtCore import QSize
from functools import partial
from random import randint

from styled_widgets import animated_widget, styled_message_box

class image_button(QWidget):
    def __init__(self, id):
        super().__init__()
        uic.loadUi('order_photo.ui', self)
        # выгрузка данных для карточки товара из базы данных
        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"SELECT photo1 FROM items WHERE id = {id}")
        data = self.cur.fetchone()
        photo1 = data[0]

        width = self.photo.size().width()
        height = self.photo.size().height()

        # ставим кликбельное изображение в мини-карточку
        self.photo.setIcon(QIcon(photo1))
        self.photo.setIconSize(QSize(width, height))
        self.show_description_partial = partial(self.show_description, id)
        self.photo.clicked.connect(self.show_description_partial)

    def show_description(self, id):
        w2 = big_card(id)
        w2.show()


class little_card(QWidget):
    def __init__(self, id):
        super().__init__()
        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('little_card.ui', self)

        # выгрузка данных для карточки товара из базы данных
        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"SELECT * FROM items WHERE id = {id}")
        data = self.cur.fetchall()
        text, num, photo1, photo2, order_quantity = data[0][1:]

        # поставили значения из бд в соответствующие поля
        self.price.setText(str(num))

        width = self.photo.size().width()
        height = self.photo.size().height()

        # ставим кликбельное изображение в мини-карточку
        self.photo.setIcon(QIcon(photo1))
        self.photo.setIconSize(QSize(width, height))

        # открываем большую карточку товара при нажатии на фото или на цену
        self.show_description_partial = partial(self.show_description, id)
        self.price.clicked.connect(self.show_description_partial)
        self.photo.clicked.connect(self.show_description_partial)

    # открываем новое окно
    def show_description(self, id):
        w2 = big_card(id)
        w2.show()


class big_card(animated_widget):
    def __init__(self, id):
        super().__init__()
        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('description.ui', self)
        self.setWindowTitle("Карточка товара")
        self.setWindowIcon(QIcon('images/icon.png'))

        # выгрузка данных для карточки товара из базы данных
        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"SELECT * FROM items WHERE id = {id}")
        data = self.cur.fetchall()
        text, num, photo1, photo2, order_quantity = data[0][1:]

        description = text
        # составление описания при помощи таблицы description
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

        # поставили значения из бд в соответствующие поля
        self.name.setText(text)
        self.name.setWordWrap(True)

        # Установить переданные значения
        self.long_description.setText(description)
        self.long_description.setWordWrap(True)

        self.price.setText(str(num))

        self.buttons = self.sizes.buttons()
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

        # пролистывание фотографий
        self.photo_counter = 0

        self.next1.clicked.connect(self.update_photo)
        self.prev1.clicked.connect(self.update_photo)

        max_item = self.cur.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        ids = [randint(1, max_item) for i in range(5)]

        # добавление рекомендаций
        for i in ids:
            widget = little_card(i)
            self.horizontalLayout.addWidget(widget)

        # выбор размера
        self.current_size = None
        self.current_size_num = None
        # Проходим по всем кнопкам и связываем их с обработчиками
        self.buttons = self.sizes.buttons()

        # Проходим по всем кнопкам и связываем их с обработчиками
        for button in self.buttons:
            button.clicked.connect(lambda checked, b=button: self.size_pushed(b))

        # добавление в корзину
        self.korzina_or_like_pushed_partial = partial(self.korzina_or_like_pushed, id)
        self.buy.clicked.connect(self.korzina_or_like_pushed_partial)
        self.like.clicked.connect(self.korzina_or_like_pushed_partial)

    def size_pushed(self, button):
        if self.current_size:
            self.current_size.setStyleSheet("""border: 1px solid #000; 
            border-radius: 13px; 
            border-style: outset; 
            color: black; 
            font-weight: bold; 
            font: 18pt 'HelveticaNeueCyr';""")

        button.setStyleSheet("""border: 0px solid #000; 
        border-radius: 13px; 
        border-style: outset; 
        background: black; 
        color: rgb(254,254,254); 
        font-weight: bold; 
        font: 18pt 'HelveticaNeueCyr';""")
        self.current_size = button
        self.current_size_num = button.text()

    def korzina_or_like_pushed(self, id):
        self.value = self.spinBox.value()
        self.cur = self.conn.cursor()
        self.cur.execute(f"""SELECT user_id FROM current_user_id""")
        data = self.cur.fetchone()
        current_user_id = data[0]
        sender = self.sender()

        if current_user_id == 0:
            message = styled_message_box()
            message.setWindowTitle("Ошибка")
            if sender == self.buy:
                message.setText("Войдите в аккаунт, чтобы добавлять товары в корзину.")
            else:
                message.setText("Войдите в аккаунт, чтобы добавлять товары в понравившиеся.")
            message.exec()
        elif self.current_size_num == None and sender == self.buy:
            message = styled_message_box()
            message.setWindowTitle("Ошибка")
            message.setText("Пожалуйста, выберете размер.")
            message.exec()
        elif sender == self.like:
            self.add_row(id, self.current_size_num, self.value, current_user_id)
        else:
            self.add_row(id, self.current_size_num, self.value, current_user_id)

    def add_row(self, item_id, size, count, current_user_id):
        self.conn = sqlite3.connect("cards.db")
        try:
            sender = self.sender()
            cur = self.conn.cursor()
            if sender == self.buy:
                a = f"""INSERT INTO bag(user_id, item_id, size, count) 
                VALUES("{current_user_id}", "{item_id}", "{size}", {count})"""
            else:
                a = f"""INSERT INTO like(user_id, item_id) 
                VALUES("{current_user_id}", "{item_id}")"""
            cur.execute(a)
            self.conn.commit()
            cur.close()

            message = styled_message_box()
            message.setWindowTitle("Успешное добавление")
            if sender == self.buy:
                message.setText("Товар добавлен в корзину.")
            else:
                message.setText("Товар добавлен в понравившиеся.")
            message.exec()

        except Exception as e:
            message = styled_message_box()
            message.setWindowTitle("не добавлено")
            message.setText("Не добавлено. Проверьте, выбран ли размер.")
            message.exec()
            print(e)

    # листание фото
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
        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('card.ui', self)

        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        # Берем первые 5 товаров из бд
        self.cur.execute(f"SELECT * FROM items WHERE id = {id}")
        data = self.cur.fetchall()
        text, num, photo1, photo2, order_quantity = data[0][1:]

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
        w2 = big_card(id)
        w2.show()
