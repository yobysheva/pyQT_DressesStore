import sqlite3

from PyQt6 import uic

from styled_widgets import styled_dialog, styled_message_box

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
        if (self.login.text() != "" and self.password.text() != "" and self.fio.text() != "" and
                self.card_number.text() != "" and self.expiration_date.text() != "" and self.cvv.text() != ""
                and self.post_index.text() != ""):
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
                self.con = sqlite3.connect('cards.db')

            except Exception as e:
                message = styled_message_box()
                message.setWindowTitle("Аккаунт не зарегистрирован")
                message.setText("Не удалось зарегистрировать. Убедитесь, что данные внесены верно. Логин должен быть уникален.")

                message.exec()
                print(e)
            self.cur = self.con.cursor()
            self.cur.execute(f"""SELECT  user_id FROM users WHERE login = "{login}" """)
            data = self.cur.fetchone()
            self.close()
            current_user_id = data[0]
            self.con = sqlite3.connect('cards.db')
            self.cur = self.con.cursor()
            # задаю текущего пользователя
            # a = f"""UPDATE current_user_id SET current_user_id = {current_user_id}"""
            #print(current_user_id)
        else:
            message = styled_message_box()
            message.setWindowTitle("Регистрация не выполнена")
            message.setText("Не удалось зарегистрироваться. "
                            "Убедитесь, что данные внесены верно.")
            message.exec()


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

