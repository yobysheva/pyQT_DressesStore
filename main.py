from PyQt6.QtWidgets import QApplication
from the_main_window import main_window


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = main_window()
    window.show()
    sys.exit(app.exec())