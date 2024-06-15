from PyQt6.QtWidgets import QWidget, QDialog, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QPropertyAnimation

# классы с анимацией для наследования другими классами
class animated_widget(QWidget):
    def __init__(self):
        super().__init__()
        # класс анимации прозрачности окна
        self.animation = QPropertyAnimation(self, b'windowOpacity')
        # продолжительность: 200 миллисекунд
        self.animation.setDuration(200)
        self.do_show()

    def do_show(self):
        try:
            self.animation.finished.disconnect(self.close)
        except:
            pass
        self.animation.stop()
        # диапазон прозрачности постепенно увеличивается от 0 до 1.
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()


class styled_dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('images/icon.png'))
        # класс анимации прозрачности окна
        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(200)  # продолжительность: 200 миллисекунд
        self.do_show()

    def do_show(self):
        try:
            self.animation.finished.disconnect(self.close)
        except:
            pass
        self.animation.stop()
        # диапазон прозрачности постепенно увеличивается от 0 до 1.
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

# месседж с примерненным стилем
class styled_message_box(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
        """background: rgb(254,254,254);
        font-weight: bold;
        color: black;
        font: 24pt "HelveticaNeueCyr";""")