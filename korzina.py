import sqlite3

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPixmap,  QIcon
from PyQt6.QtCore import QTimer
from random import randint
from datetime import datetime

from styled_widgets import animated_widget, styled_message_box
from item_cards import little_card

class korzina_item(QWidget):
    def __init__(self, korzina_item_id):
        super().__init__()
        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('ui/korzina_item.ui', self)

        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"""SELECT user_id FROM current_user_id""")
        data = self.cur.fetchone()
        self.current_user_id = data[0]

        # информация о размере, количестве
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

    # смотрим сколько товаров выбрано
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

    # удаление из корзины
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
        self.setWindowIcon(QIcon('images/icon.png'))
        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"""SELECT user_id FROM current_user_id""")
        data = self.cur.fetchone()
        self.current_user_id = data[0]

        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('ui/korzina.ui', self)

        self.page = 0
        self.current_price = 0
        self.timer = QTimer(self)

        # загружаем корзину для текущего пользователя или загружаем рекоммендации
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

    # очистить layout перед заполнением
    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # загружаем 2 товароа в layout
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

    # пролистывание товаров
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

    # пролистывание рекоммендаций
    def update_recommendation(self):
        self.clear_layout(self.gridLayout)
        max_item = self.cur.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        ids = [randint(1, max_item) for _ in range(20)]

        for i in range(20):
            widget = little_card(ids[i])
            self.gridLayout.addWidget(widget, i // 10, i % 10)

    # обновляем цену и кнопку назад
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

    # анимация смены цены
    def animate_price_change(self, new_price, chosen_count):
        self.animation_steps = 100  # количество шагов для анимации
        self.animation_duration = 1000  # длительность в миллисекундах

        self.step_value = (new_price - self.current_price) / self.animation_steps
        self.step_duration = int(self.animation_duration / self.animation_steps)

        self.target_price = new_price
        self.chosen_count = chosen_count

        # запусскаем смену кадров по тикам
        self.timer.timeout.connect(self.update_label)
        self.timer.start(self.step_duration)

    # цена красиво сменается
    def update_label(self):
        self.current_price += self.step_value
        if (self.step_value > 0 and self.current_price >= self.target_price) or \
                (self.step_value < 0 and self.current_price <= self.target_price):
            self.current_price = self.target_price
            self.timer.stop()

        self.label_3.setText(f"Выбрано товаров: {self.chosen_count} на сумму {int(self.current_price)}")

    # меняем кнопку назад на обновить заказ и обратно (подстраиваем размер)
    def update_back(self):
        self.back.adjustSize()
        self.back.setFixedWidth(self.back.sizeHint().width() + 20)
        size = self.back.size()
        self.back.setGeometry(self.width() // 2 - size.width() // 2 - 10,
                              self.back.geometry().y(), size.width() + 20, size.height())

    # записываем заказ в базу данных
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

    # обрабока нажатий кнопки назад или сформировать заказ
    def on_back_clicked(self):
        if self.back.text() == "Оформить заказ":
            self.form_order()
        else:
            self.close()