import sqlite3

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QIcon

from styled_widgets import animated_widget
from item_cards import image_button

class ordered_item(QWidget):
    def __init__(self, order_id):
        super().__init__()
        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('ui/order.ui', self)

        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"""SELECT user_id FROM current_user_id""")
        data = self.cur.fetchone()
        self.current_user_id = data[0]

        data = self.cur.execute(f"""SELECT id, name, cost, photo1, size, count FROM ordered_items 
                INNER JOIN items on items.id = ordered_items.item_id
                WHERE order_id = {order_id}""").fetchall()

        date = self.cur.execute(f"""SELECT date FROM orders
                WHERE order_id = {order_id}""").fetchone()[0]

        # формируем чек
        s = "\n" +"."*50 + "\n"
        text = f"Номер заказа: {order_id}" + s + \
               f"Дата отпрапвки: {date}\n" \
               "Ожидаемое время в пути: 14 дней" + s +\
               "Пункт выдачи № 789. к10, посёлок " \
               "\nАякс, кампус Дальневосточного " \
               "\nфедерального университета, посёлок " \
               "\nРусский." + s + \
               "Состав заказа:"

        total_cost = 0
        for i in range(len(data)):
            id, name, cost, photo, size, count = data[i]
            image = image_button(id)
            self.horizontalLayout.addWidget(image)
            text += s + f"{name}. Размер: {size}. Цена: {cost} x {count}"
            total_cost += cost * count

        text += s + f"Заказ на сумму: {total_cost} рублей"

        self.ordered_items.setText(text)
        self.ordered_items.setWordWrap(True)


class orders_widget(animated_widget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мои заказы")
        self.setWindowIcon(QIcon('images/icon.png'))
        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"""SELECT user_id FROM current_user_id""")
        data = self.cur.fetchone()
        self.current_user_id = data[0]

        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('ui/orders.ui', self)

        # задаем страницу и счетчик
        self.page = 0
        self.offset = 0

        # загружаем заказы для текущего пользователя
        if self.current_user_id != 0:
            korzina_items_count = self.cur.execute(f"""SELECT COUNT(*) FROM orders 
                                                 WHERE user_id = {self.current_user_id}""").fetchone()[0]
            if korzina_items_count == 0:
                self.label_3.setText("Нет ни одного заказа.")
            else:
                self.label_3.setText("Мои заказы:")
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
        self.clear_layout(self.gridLayout)

        self.cur.execute(f"""SELECT order_id FROM orders 
                        WHERE user_id = {self.current_user_id} 
                        LIMIT 2 OFFSET {self.page * 2}""")
        data = self.cur.fetchall()

        for i in range(len(data)):
            self.widget = ordered_item(data[i][0])
            self.widget.number.setText(str(i + 1 + self.offset))
            self.gridLayout.addWidget(self.widget, i, 0)

    # листаем
    def update_page(self):
        sender = self.sender()
        max_pages = self.cur.execute(f"""SELECT COUNT(*) FROM orders 
                                     WHERE user_id = {self.current_user_id}""").fetchone()[0]
        max_pages = max_pages // 2 if max_pages % 2 == 1 else max_pages // 2 - 1

        if sender == self.next and self.page < max_pages:
            self.page += 1
            self.offset += 2
        elif sender == self.prev and self.page > 0:
            self.page -= 1
            self.offset -= 2

        self.load_items()
