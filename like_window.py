import sqlite3

from PyQt6 import uic
from PyQt6.QtGui import QIcon
from random import randint

from styled_widgets import animated_widget
from item_cards import little_card, card


class like_widget(animated_widget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Понравившееся")
        self.setWindowIcon(QIcon('images/icon.png'))
        self.conn = sqlite3.connect('cards.db')
        self.cur = self.conn.cursor()

        self.cur.execute(f"""SELECT user_id FROM current_user_id""")
        data = self.cur.fetchone()
        self.current_user_id = data[0]

        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('ui/like.ui', self)
        self.page = 0

        # лайки текущего пользователя или рекоммендации
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

    # очистить layout перед заполнением
    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # загружаем 5 товаров в layout
    def load_items(self):
        self.cur.execute(f"""SELECT item_id FROM like 
                        WHERE user_id = {self.current_user_id} 
                        LIMIT 5 OFFSET {self.page * 5}""")
        data = self.cur.fetchall()

        for i in range(len(data)):
            widget = card(data[i][0])
            self.gridLayout.addWidget(widget, 0, 4-i)

    # пролистывание понравившихся
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

    # пролистывание рекоммендаций
    def update_recommendation(self):
        self.clear_layout(self.gridLayout)
        max_item = self.cur.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        ids = [randint(1, max_item) for _ in range(20)]

        for i in range(20):
            widget = little_card(ids[i])
            self.gridLayout.addWidget(widget, i // 10, i % 10)
