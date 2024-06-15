import sqlite3

from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import  QIcon
from PyQt6.QtCore import QSize

from functools import partial

from enter_or_registration import enter_or_registration_dialog
from item_cards import card
from korzina import korzina_widget
from like_window import like_widget
from order_window import orders_widget

white_button_style = """border: 2px solid #000;
                        border-radius: 10px;
                        border-style: outset;
                        color: black;
                        font-weight: bold;
                        font: 26pt 'Futurespore Cyrillic';
                        """

black_button_style = """border: 2px solid #000;
                    border-radius: 10px;
                    border-style: outset;
                    background: black;
                    color: rgb(254,254,254);
                    font-weight: bold;
                    font: 26pt 'Futurespore Cyrillic';"""

class main_window(QMainWindow):
    def __init__(self):
        super().__init__()
        # Загрузить пользовательский интерфейс главного окна из файла .ui
        uic.loadUi('ui/MainWindow.ui', self)
        self.setWindowTitle("Karmen - магазин премиальной одежды")
        self.setWindowIcon(QIcon('images/icon.png'))

        # иконки для кнопок корзина, вход и избранное
        self.like.setIcon(QIcon('images/like.png'))
        self.like.setIconSize(QSize(20, 20))

        self.korzina.setIcon(QIcon('images/bag.png'))
        self.korzina.setIconSize(QSize(20, 20))

        self.log_in.setIcon(QIcon('images/log_in.png'))
        self.log_in.setIconSize(QSize(20, 20))

        self.orders.setIcon(QIcon('images/box.png'))
        self.orders.setIconSize(QSize(23, 23))

        self.korzina.clicked.connect(self.open_korzina)
        self.log_in.clicked.connect(self.enter_or_registration)
        self.like.clicked.connect(self.open_like)
        self.orders.clicked.connect(self.open_orders)

        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()
        # задаю текущего пользователя
        a = f"""UPDATE current_user_id SET user_id = 0"""
        self.cur.execute(a)
        self.conn.commit()

        # Берем первые 5 товаров из бд
        self.cur.execute("SELECT * FROM items LIMIT 5")
        data = self.cur.fetchall()

        for i, row in enumerate(data):
            widget = card(row[0])
            self.gridLayout.addWidget(widget, 0, 4 - i)

        # задаем текущую страницу и текущее собщение для фильтрации
        self.page = 0
        self.message = ' '

        # листание страниц по нажатию на кнопки
        self.update_data_partial = partial(self.update_data, self.message)
        self.next.clicked.connect(self.update_data_partial)
        self.prev.clicked.connect(self.update_data_partial)

        self.all.clicked.connect(self.categories_filter)
        self.red.clicked.connect(self.categories_filter)

        self.all.clicked.connect(self.all_pushed)
        self.red.clicked.connect(self.color_pushed)

        for button in self.filter.buttons():
            button.clicked.connect(self.categories_filter)

        # выбор фильтра
        self.current_filter = None
        # Проходим по всем кнопкам и связываем их с обработчиками
        self.buttons = self.filter.buttons()

        # смена цветов
        self.colors = ['красный', 'черный', 'серый', 'пастельные']
        self.current_color = 0  # Индекс текущего цвета

        # Проходим по всем кнопкам и связываем их с обработчиками
        for button in self.buttons:
            button.clicked.connect(lambda checked, b=button: self.filter_pushed(b))

    # меняем текст на кнопке цвет
    def color_pushed(self):
        self.buttons = self.filter.buttons()
        for button in self.buttons:
            button.setStyleSheet(white_button_style)
        self.current_color = (self.current_color + 1) % len(self.colors)
        # Переходим к следующему тексту циклически
        self.red.setText(self.colors[self.current_color])

    # меняем цвет всех кнопок обратно на белый
    def all_pushed(self):
        self.buttons = self.filter.buttons()
        for button in self.buttons:
            button.setStyleSheet(white_button_style)

    # функция для смены цвета кнопок фильтрации
    def filter_pushed(self, button):
        if self.current_filter:
            self.current_filter.setStyleSheet(white_button_style)
        button.setStyleSheet(black_button_style)
        self.current_filter = button

    # функция для вывода 5 товаров по страницам
    def update_data(self, message):
        sender = self.sender()
        # количество товаров в таблице
        max_pages = self.cur.execute(f"SELECT COUNT(*) FROM items {self.message}").fetchone()[0]
        max_pages = max_pages // 5 if max_pages % 5 != 0 else max_pages // 5 - 1
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

    # фильтрация по категориям
    def categories_filter(self):
        self.page = 0
        category = self.sender().text()
        if category == 'все':
            self.message = ''
        elif category == 'Новая коллекция':
            self.message = 'ORDER BY id DESC'
        elif category == 'пастельные':
            self.message = f""" 
                            INNER JOIN description ON description.id = items.id
                            INNER JOIN colors ON colors."colors id" = description.color
                            WHERE colors.name = 'белый' or colors.name = 'желтый' or 
                            colors.name = 'голубой' or colors.name = 'бежевый' or colors.name = 'розовый'"""
        elif category in self.colors:
            self.message = f""" 
                            INNER JOIN description ON description.id = items.id
                            INNER JOIN colors ON colors."colors id" = description.color
                            WHERE colors.name = '{category}'"""
        else:
            self.message = f""" 
                INNER JOIN description ON description.id = items.id
                INNER JOIN categories ON categories."categoy id" = description.category
                WHERE categories.name = '{category}'"""
        self.update_data(self.message)

    # открывается корзина
    def open_korzina(self):
        self.korzina_window = korzina_widget()
        self.korzina_window.show()

    # открываются понравившиеся
    def open_like(self):
        self.like_window = like_widget()
        self.like_window.show()

    # окно входа и регистрации
    def enter_or_registration(self):
        self.w2 = enter_or_registration_dialog()
        self.w2.exec()

    # окно заказов текущего пользователя
    def open_orders(self):
        self.orders_window = orders_widget()
        self.orders_window.show()
