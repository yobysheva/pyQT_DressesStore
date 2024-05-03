from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QCheckBox, QSpinBox, QLabel, QVBoxLayout, QFrame, QPushButton, QMainWindow
from PyQt6.QtGui import QFont, QPixmap, QPainterPath, QPainter
from PyQt6.QtCore import QRectF

class MyWidget(QWidget):
    def __init__(self, photo, text, num):
        super().__init__()

        # Загрузить пользовательский интерфейс из файла .ui
        uic.loadUi('card.ui', self)

        # Установить переданные значения
        self.name.setText(text)

        self.price.setText(str(num))

        photo_label = QLabel(self)
        image = QPixmap(photo)
        # уменьшение изображения
        photo_label.setScaledContents(True)

        photo_label.setPixmap(image)

        self.verticalLayout.addWidget(photo_label)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузить пользовательский интерфейс главного окна из файла .ui
        uic.loadUi('MainWindow.ui', self)

        # Создать экземпляры MyWidget с разными значениями
        widget1 = MyWidget("dress5.jpg", "Маленькое черное платье", 1999)
        widget2 = MyWidget("dress2.jpg", "Маленькое черное платье", 2990)
        widget3 = MyWidget("dress3.jpg", "Маленькое черное платье", 1859)
        widget4 = MyWidget("dress4.jpg", "Маленькое черное платье",999)
        widget5 = MyWidget("dress7.jpg", "Маленькое черное платье",4999)

        # Разместить виджеты в QGridLayout главного окна
        self.gridLayout.addWidget(widget1, 0, 0)
        self.gridLayout.addWidget(widget2, 0, 1)
        self.gridLayout.addWidget(widget3, 0, 2)
        self.gridLayout.addWidget(widget4, 0, 3)
        self.gridLayout.addWidget(widget5, 0, 4)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


