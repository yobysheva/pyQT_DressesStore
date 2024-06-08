import sqlite3

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QCheckBox, QSpinBox, QLabel, QVBoxLayout, QFrame, QPushButton, \
    QMainWindow, QListWidget, QListWidgetItem, QDialog, QMessageBox, QScrollArea, QFormLayout, QGroupBox
from PyQt6.QtGui import QFont, QPixmap, QPainterPath, QPainter, QIcon
from PyQt6.QtCore import Qt, QRectF, QSize, QEvent, QPropertyAnimation, QRect, QTimer
from functools import partial
from random import randint
from datetime import datetime


# классы с анимацией для наследования другими классами
class animated_widget(QWidget):
    def __init__(self):
        super().__init__()
        # Класс анимации прозрачности окна
        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(200)  # Продолжительность: 1 секунда

        # Выполните постепенное увеличение
        self.do_show()

    def do_show(self):
        try:
            self.animation.finished.disconnect(self.close)
        except:
            pass
        self.animation.stop()
        # Диапазон прозрачности постепенно увеличивается от 0 до 1.
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def do_close(self):
        self.animation.stop()
        # Закройте окно, когда анимация будет завершена
        self.animation.finished.connect(self.close)
        # Диапазон прозрачности постепенно уменьшается с 1 до 0.
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.start()


class styled_dialog(QDialog):
    def __init__(self):
        super().__init__()
        # Класс анимации прозрачности окна
        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(200)  # Продолжительность: 1 секунда

        # Выполните постепенное увеличение
        self.do_show()

    def do_show(self):
        try:
            self.animation.finished.disconnect(self.close)
        except:
            pass
        self.animation.stop()
        # Диапазон прозрачности постепенно увеличивается от 0 до 1.
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def do_close(self):
        self.animation.stop()
        self.animation.finished.connect(self.close)  # Закройте окно, когда анимация будет завершена
        # Диапазон прозрачности постепенно уменьшается с 1 до 0.
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.start()


class styled_message_box(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""background: rgb(254,254,254);
        font-weight: bold;
        color: black;
        font: 24pt "HelveticaNeueCyr";""")


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


class registration_dialog(styled_dialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('registration_dialog.ui', self)  # загружаем UI файл в текущий виджет
        self.setWindowTitle("Регистрация")
        try:
            self.registrate.clicked.connect(
                lambda: self.add_row(self.login.text(), self.password.text(),
                                     self.fio.text(), self.card_number.text(),
                                     self.expiration_date.text(), self.cvv.text(), self.post_index.text()))
        except Exception as e:
            print(e)
        self.escape.clicked.connect(self.close)
    def add_row(self, login, password, fio, card_number, expiration_date, cvv, post_index):
        self.con = sqlite3.connect("cards.db")
        try:
            cur = self.con.cursor()
            a = f"""INSERT INTO users(login, password, FIO, card_number, validity_period, CVV, postal_code) 
            VALUES("{login}", "{password}", "{fio}", {card_number}, "{expiration_date}", {cvv}, {post_index}) """
            cur.execute(a)
            self.con.commit()
            cur.close()

            message = styled_message_box()
            message.setWindowTitle("Успешная регистрация")
            message.setText("Аккаунт зарегистрирован.")
            message.exec()

            self.con = sqlite3.connect("cards.db")
            self.conn = sqlite3.connect('cards.db')

        except Exception as e:
            message = styled_message_box()
            message.setWindowTitle("Аккаунт не зарегистрирован")
            message.setText("Не удалось зарегистрировать. Убедитесь, что данные внесены верно. Логин должен быть уникален.")

            message.exec()
            print(e)
        self.cur = self.conn.cursor()
        self.cur.execute(f"""SELECT  user_id FROM users WHERE login = "{login}" """)
        data = self.cur.fetchone()
        self.close()
        current_user_id = data[0]
        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()
        # задаю текущего пользователя
       # a = f"""UPDATE current_user_id SET current_user_id = {current_user_id}"""
        #print(current_user_id)


class enter_dialog(styled_dialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('enter_dialog.ui', self)  # загружаем UI файл в текущий виджет
        self.setWindowTitle("Вход в аккаунт")

        try:
            self.enter.clicked.connect(
                lambda: self.check_enter(self.login.text(), self.password.text()))

        except Exception as e:
            print(e)
        self.escape.clicked.connect(self.close)

    def check_enter(self, login, entered_password):
        self.con = sqlite3.connect("cards.db")
        self.cur = self.con.cursor()
        data = []
        if self.login.text() != "" and self.password.text() != "":
            self.cur.execute(f"""SELECT user_id, password FROM users WHERE login = "{login}" """)
            data = self.cur.fetchone()
            self.con.close()
            if data:
                password = data[1]
                if entered_password == password:
                    message = styled_message_box()
                    message.setWindowTitle("Успешное выполнение")
                    message.setText("Вы вошли в аккаунт.")
                    message.exec()

                    current_user_id = data[0]
                    self.change_user_id(current_user_id)
                    self.close()
                else:
                    self.create_massege()
            else:
                self.create_massege()
        else:
            self.create_massege()
    def change_user_id(self, user_id):
        self.con = sqlite3.connect("cards.db")
        self.cur = self.con.cursor()
        a = f"""UPDATE current_user_id SET user_id = {user_id}"""
        self.cur.execute(a)
        self.con.commit()
        self.con.close()  # закрыть соединение
        self.close()
    def create_massege(self):
        message = styled_message_box()
        message.setWindowTitle("Вход не выполнен")
        message.setText("Не удалось войти в аккаунт. "
                        "Убедитесь, что данные внесены верно или зарегистрируйтесь.")
        message.exec()


class enter_or_registration_dialog(styled_dialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('enter_or_registration.ui', self)  # загружаем UI файл в текущий виджет
        self.setWindowTitle("Войдите или зарегистрируйтесь")

        self.registrate.clicked.connect(self.registration)
        self.enter.clicked.connect(self.do_enter)

    def registration(self):
        w2 = registration_dialog()
        self.close()
        w2.exec()

    def do_enter(self):
        w2 = enter_dialog()
        self.close()
        w2.exec()


class korzina_item(QWidget):
    def __init__(self, korzina_item_id):
        super().__init__()
        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('korzina_item.ui', self)

        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"""SELECT user_id FROM current_user_id""")
        data = self.cur.fetchone()
        self.current_user_id = data[0]

        self.cur.execute(f"""SELECT korzina_item_id, item_id, size, count, is_chosen FROM bag 
        WHERE korzina_item_id = {korzina_item_id}""")
        desc2_data = self.cur.fetchone()
        self.korzina_item_id, user_id, size, count, is_chosen = desc2_data
        description2 = f"Размер: {size}\nКоличество: {count}"

        self.cur.execute(f"SELECT * FROM items WHERE id = {user_id}")
        data = self.cur.fetchone()
        text, num, photo1, photo2, order_quantity = data[1:]
        description = text

        # составление описания при помощи таблицы description
        self.cur.execute(f"""SELECT materials.name, models.name, colors.name, length.name, categories.name FROM description 
                            INNER JOIN items ON items.id = description.id
                            INNER JOIN materials ON materials."material id" = description.material
                            INNER JOIN models ON models."models id" = description.model
                            INNER JOIN colors ON colors."colors id" = description.color
                            INNER JOIN length ON length."length id" = description.length
                            INNER JOIN categories ON categories."categoy id" = description.category
                            WHERE items.id = {user_id}""")
        desc_data = self.cur.fetchone()
        if desc_data:
            material, model, color, length, category = desc_data
            description = f"Модель: {model}\nМатериал: {material}\nЦвет: {color}\n" \
                                f"Длина: {length}\nКатегория: {category}"


        # Установить значения из бд в соответствующие поля
        self.name.setText(text)
        self.name.setWordWrap(True)

        self.long_description.setText(description)
        self.long_description.setWordWrap(True)
        self.long_description_2.setText(description2)
        self.long_description_2.setWordWrap(True)

        self.price.setText(str(num))

        self.photo_label = QLabel(self)
        self.original_image = QPixmap(photo1)
        self.photo_label.setPixmap(self.original_image)
        self.photo_label.setScaledContents(True)
        self.verticalLayout.addWidget(self.photo_label)

        self.checkBox.setChecked(is_chosen == 1)
        self.checkBox.stateChanged.connect(self.update_is_chosen)

        self.delete_item.clicked.connect(self.del_item)

    def update_is_chosen(self):
        is_chosen = 1 if self.checkBox.isChecked() else 0
        self.cur.execute(f"""UPDATE bag SET is_chosen = {is_chosen} 
                    WHERE korzina_item_id = {self.korzina_item_id}""")
        self.conn.commit()

        if is_chosen:
            chosen_count = self.cur.execute(f"""SELECT COUNT(*) FROM bag 
                    WHERE user_id = {self.current_user_id} AND is_chosen = 1""").fetchone()[0]

            if chosen_count > 5:
                message = styled_message_box()
                message.setWindowTitle("Не удалось добавить товар в заказ")
                message.setText("Невозможно заказать более 5 товаров за один раз.")
                message.exec()

                self.cur.execute(f"""UPDATE bag SET is_chosen = 0 
                                WHERE korzina_item_id = {self.korzina_item_id}""")

                self.checkBox.setChecked(False)
                self.conn.commit()

    def del_item(self):
        self.conn = sqlite3.connect("cards.db")
        try:
            cur = self.conn.cursor()
            a = f"""DELETE FROM bag WHERE korzina_item_id = "{self.korzina_item_id}" """
            cur.execute(a)
            self.conn.commit()
            cur.close()

        except Exception as e:
            print(e)


class korzina_widget(animated_widget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Корзина")
        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"""SELECT user_id FROM current_user_id""")
        data = self.cur.fetchone()
        self.current_user_id = data[0]

        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('korzina.ui', self)

        self.page = 0
        self.current_price = 0
        self.timer = QTimer(self)

        if self.current_user_id == 0:
            self.update_recommendation()
            self.gridLayout.setContentsMargins(0, 20, 0, 0)
            self.next.clicked.connect(self.update_recommendation)
            self.prev.clicked.connect(self.update_recommendation)
            self.back.clicked.connect(self.on_back_clicked)
        else:
            self.label_4.setText("Выберите товары, чтобы сформировать заказ. "
                                 "В одном заказе может содержаться не более 5 наименований.")
            korzina_items_count = self.cur.execute(f"""SELECT COUNT(*) FROM bag 
                                                 WHERE user_id = {self.current_user_id}""").fetchone()[0]
            if korzina_items_count == 0:
                self.update_recommendation()
                self.gridLayout.setContentsMargins(0, 20, 0, 0)
                self.next.clicked.connect(self.update_recommendation)
                self.prev.clicked.connect(self.update_recommendation)
                self.back.clicked.connect(self.on_back_clicked)
            else:
                self.load_items()
                self.next.clicked.connect(self.update_page)
                self.prev.clicked.connect(self.update_page)
                self.back.clicked.connect(self.on_back_clicked)
        self.update_back()
        self.price = 0

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def load_items(self):
        self.update_price()
        self.clear_layout(self.gridLayout)

        self.cur.execute(f"""SELECT korzina_item_id FROM bag 
                        WHERE user_id = {self.current_user_id} 
                        LIMIT 2 OFFSET {self.page * 2}""")
        data = self.cur.fetchall()

        for i in range(len(data)):
            self.widget = korzina_item(data[i][0])
            self.gridLayout.addWidget(self.widget, i, 0)
            self.widget.checkBox.stateChanged.connect(self.update_price)
            self.widget.delete_item.clicked.connect(self.update_page)

    def update_page(self):
        sender = self.sender()
        max_pages = self.cur.execute(f"""SELECT COUNT(*) FROM bag 
                                     WHERE user_id = {self.current_user_id}""").fetchone()[0]
        max_pages = max_pages // 2 if max_pages % 2 == 1 else max_pages // 2 - 1

        if sender == self.next and self.page < max_pages:
            self.page += 1
        elif sender == self.prev and self.page > 0:
            self.page -= 1

        self.load_items()

    def update_recommendation(self):
        self.clear_layout(self.gridLayout)
        max_item = self.cur.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        ids = [randint(1, max_item) for _ in range(20)]

        for i in range(20):
            widget = little_card(ids[i])
            self.gridLayout.addWidget(widget, i // 10, i % 10)

    def update_price(self):
        chosen_count = self.cur.execute(
            f"""SELECT COUNT(*) FROM bag
            WHERE user_id = {self.current_user_id} AND is_chosen = 1""").fetchone()[0]

        chosen_items = self.cur.execute(
            f"""SELECT bag.count, items.cost, bag.is_chosen FROM bag
                INNER JOIN items ON items.id = bag.item_id
                WHERE bag.user_id = {self.current_user_id}""").fetchall()

        new_price = sum(count * price * is_chosen for count, price, is_chosen in chosen_items)

        self.animate_price_change(new_price, chosen_count)

        # обновляем кнопку в зависимости от количества выбранных товаров
        if chosen_count > 0:
            self.back.setText("Оформить заказ")
        else:
            self.back.setText("Назад")
            self.back.clicked.connect(self.on_back_clicked)

        # поправляем размер кнопки
        self.update_back()

    def animate_price_change(self, new_price, chosen_count):
        self.animation_steps = 100  # количество шагов для анимации
        self.animation_duration = 1000  # длительность в миллисекундах

        self.step_value = (new_price - self.current_price) / self.animation_steps
        self.step_duration = int(self.animation_duration / self.animation_steps)

        self.target_price = new_price
        self.chosen_count = chosen_count

        self.timer.timeout.connect(self.update_label)
        self.timer.start(self.step_duration)

    def update_label(self):
        self.current_price += self.step_value
        if (self.step_value > 0 and self.current_price >= self.target_price) or \
                (self.step_value < 0 and self.current_price <= self.target_price):
            self.current_price = self.target_price
            self.timer.stop()

        self.label_3.setText(f"Выбрано товаров: {self.chosen_count} на сумму {int(self.current_price)}")

    def update_back(self):
        self.back.adjustSize()
        self.back.setFixedWidth(self.back.sizeHint().width() + 20)
        size = self.back.size()
        self.back.setGeometry(self.width() // 2 - size.width() // 2 - 10,
                              self.back.geometry().y(), size.width() + 20, size.height())

    def form_order(self):
        today_date = datetime.now().strftime("%d.%m.%y")
        a = f"""INSERT INTO orders(user_id, date) 
                VALUES("{self.current_user_id}", "{today_date}")"""
        self.cur.execute(a)
        self.conn.commit()

        order_id = self.cur.execute(f"""SELECT order_id FROM orders 
                 ORDER BY order_id DESC""").fetchone()[0]

        ordered_items = self.cur.execute(
            f"""SELECT korzina_item_id, item_id, size, count FROM bag
            WHERE user_id = {self.current_user_id} AND is_chosen = 1""").fetchall()
        try:
            for item in ordered_items:
                korzina_item_id, item_id, size, count = item
                a = f"""INSERT INTO ordered_items(order_id, item_id, size, count) 
                                                    VALUES({order_id}, {item_id}, {size}, {count})"""
                self.cur.execute(a)
                self.conn.commit()

                a = f"""DELETE FROM bag WHERE korzina_item_id = "{korzina_item_id}" """
                self.cur.execute(a)
                self.conn.commit()
                print(korzina_item_id, item_id, size, count)

            # Обновляем страницу после оформления заказа
            self.update_page()

            # Показать сообщение об успешном заказе
            message = styled_message_box()
            message.setWindowTitle("Товар в пути")
            message.setText("Вы успешно заказали выбранные товары.")
            message.exec()

        except Exception as e:
            message = styled_message_box()
            message.setWindowTitle("Ошибка")
            message.setText("Не удалось заказать выбранные товары.")
            message.exec()
            print(e)

    def on_back_clicked(self):
        if self.back.text() == "Оформить заказ":
            self.form_order()
        else:
            self.close()


class like_widget(animated_widget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Понравившееся")
        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"""SELECT user_id FROM current_user_id""")
        data = self.cur.fetchone()
        self.current_user_id = data[0]

        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('like.ui', self)
        self.page = 0

        if self.current_user_id == 0:
            self.update_recommendation()
            self.gridLayout.setContentsMargins(0, 40, 0, 0)

            self.next.clicked.connect(self.update_recommendation)
            self.prev.clicked.connect(self.update_recommendation)
        else:
            like_items_count = self.cur.execute(f"""SELECT COUNT(*) FROM like 
                                                 WHERE user_id = {self.current_user_id}""").fetchone()[0]
            if like_items_count == 0:
                self.update_recommendation()
                self.gridLayout.setContentsMargins(0, 40, 0, 0)

                self.next.clicked.connect(self.update_recommendation)
                self.prev.clicked.connect(self.update_recommendation)
            else:
                self.label_3.setText(f"Понравившихся товаров: {like_items_count}")
                self.load_items()
                self.next.clicked.connect(self.update_page)
                self.prev.clicked.connect(self.update_page)
        self.back.clicked.connect(self.close)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def load_items(self):
        self.cur.execute(f"""SELECT item_id FROM like 
                        WHERE user_id = {self.current_user_id} 
                        LIMIT 5 OFFSET {self.page * 5}""")
        data = self.cur.fetchall()

        for i in range(len(data)):
            widget = card(data[i][0])
            self.gridLayout.addWidget(widget, 0, 4-i)

    def update_page(self):
        sender = self.sender()
        max_pages = self.cur.execute(f"""SELECT COUNT(*) FROM like 
                                     WHERE user_id = {self.current_user_id}""").fetchone()[0]
        max_pages = max_pages // 5 if max_pages % 5 != 0 else max_pages // 5 - 1

        if sender == self.next and self.page < max_pages:
            self.page += 1
        elif sender == self.prev and self.page > 0:
            self.page -= 1

        self.load_items()

    def update_recommendation(self):
        self.clear_layout(self.gridLayout)
        max_item = self.cur.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        ids = [randint(1, max_item) for _ in range(20)]

        for i in range(20):
            widget = little_card(ids[i])
            self.gridLayout.addWidget(widget, i // 10, i % 10)


class my_orders(animated_widget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Корзина")
        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"""SELECT user_id FROM current_user_id""")
        data = self.cur.fetchone()
        self.current_user_id = data[0]

        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('orders.ui', self)

        self.page = 0
        self.current_price = 0
        self.timer = QTimer(self)

        if self.current_user_id != 0:
            self.label_4.setText("Выберите товары, чтобы сформировать заказ. "
                                 "В одном заказе может содержаться не более 5 наименований.")
            korzina_items_count = self.cur.execute(f"""SELECT COUNT(*) FROM bag 
                                                 WHERE user_id = {self.current_user_id}""").fetchone()[0]
            if korzina_items_count == 0:
                pass
            else:
                self.load_items()
                self.next.clicked.connect(self.update_page)
                self.prev.clicked.connect(self.update_page)
                self.back.clicked.connect(self.close)
        self.price = 0

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def load_items(self):
        self.update_price()
        self.clear_layout(self.gridLayout)

        self.cur.execute(f"""SELECT korzina_item_id FROM bag 
                        WHERE user_id = {self.current_user_id} 
                        LIMIT 2 OFFSET {self.page * 2}""")
        data = self.cur.fetchall()

        for i in range(len(data)):
            self.widget = korzina_item(data[i][0])
            self.gridLayout.addWidget(self.widget, i, 0)
            self.widget.checkBox.stateChanged.connect(self.update_price)
            self.widget.delete_item.clicked.connect(self.update_page)

    def update_page(self):
        sender = self.sender()
        max_pages = self.cur.execute(f"""SELECT COUNT(*) FROM bag 
                                     WHERE user_id = {self.current_user_id}""").fetchone()[0]
        max_pages = max_pages // 2 if max_pages % 2 == 1 else max_pages // 2 - 1

        if sender == self.next and self.page < max_pages:
            self.page += 1
        elif sender == self.prev and self.page > 0:
            self.page -= 1

        self.load_items()


class main_window(QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузить пользовательский интерфейс главного окна из файла .ui
        uic.loadUi('MainWindow.ui', self)
        self.setWindowTitle("Karmen - магазин премиальной одежды")

        # иконки для кнопок корзина, вход и избранное
        self.like.setIcon(QIcon('images/like.png'))
        self.like.setIconSize(QSize(20, 20))

        self.korzina.setIcon(QIcon('images/bag.png'))
        self.korzina.setIconSize(QSize(20, 20))

        self.log_in.setIcon(QIcon('images/log_in.png'))
        self.log_in.setIconSize(QSize(20, 20))

        self.korzina.clicked.connect(self.open_korzina)
        self.log_in.clicked.connect(self.enter_or_registration)
        self.like.clicked.connect(self.open_like)

        # Connect to the database
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

        self.page = 0
        self.message = ' '

        # листание страниц по нажатию на кнопки
        self.update_data_partial = partial(self.update_data, self.message)
        self.next.clicked.connect(self.update_data_partial)
        self.prev.clicked.connect(self.update_data_partial)

        self.all.clicked.connect(self.categoriesFilter)
        self.red.clicked.connect(self.categoriesFilter)

        for button in self.filter.buttons():
            button.clicked.connect(self.categoriesFilter)

        # выбор фильтра
        self.current_filter = None
        # Проходим по всем кнопкам и связываем их с обработчиками
        self.buttons = self.filter.buttons()

        # Проходим по всем кнопкам и связываем их с обработчиками
        for button in self.buttons:
            button.clicked.connect(lambda checked, b=button: self.filter_pushed(b))
        self.all.clicked.connect(self.all_pushed)

    def all_pushed(self):
        self.buttons = self.filter.buttons()
        for button in self.buttons:
            button.setStyleSheet("""border: 2px solid #000;
                        border-radius: 10px;
                        border-style: outset;
                        color: black;
                        font-weight: bold;
                        font: 26pt 'Futurespore Cyrillic';
                        """)

    # функция для смены цвета кнопок фильтрации
    def filter_pushed(self, button):
        if self.current_filter:
            self.current_filter.setStyleSheet("""border: 2px solid #000;
                        border-radius: 10px;
                        border-style: outset;
                        color: black;
                        font-weight: bold;
                        font: 26pt 'Futurespore Cyrillic';
                        """)
        button.setStyleSheet("""border: 2px solid #000;
                    border-radius: 10px;
                    border-style: outset;
                    background: black;
                    color: rgb(254,254,254);
                    font-weight: bold;
                    font: 26pt 'Futurespore Cyrillic';""")
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

    def categoriesFilter(self):
        self.page = 0
        category = self.sender().text()
        if category == 'все':
            self.message = ''
        elif category == 'Новая коллекция':
            self.message = 'ORDER BY id DESC'
        elif category == 'красный':
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

    # открывается корзина, нужно сделать так, чтобы закрывалось изначальное окно
    def open_korzina(self):
        try:
            self.korzina_window = korzina_widget()
            self.korzina_window.show()
        except Exception as e:
            print(e)

    def open_like(self):
        try:
            self.like_window = like_widget()
            self.like_window.show()
        except Exception as e:
            print(e)

    def enter_or_registration(self):
        self.w2 = enter_or_registration_dialog()
        self.w2.exec()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = main_window()
    window.show()
    sys.exit(app.exec())