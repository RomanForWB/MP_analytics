import sys

# QtWidgets - базовый класс для любого объекта из PyQt
from PyQt5.QtWidgets import (QWidget, QApplication, QGridLayout, QLabel,
                             QScrollArea, QHBoxLayout, QVBoxLayout, QToolTip,
                             QPushButton)
from PyQt5.QtCore import QCoreApplication

# QIcon - для определения иконки приложения
# QFont - для передачи определенного шрифта
from PyQt5.QtGui import QIcon, QFont

# класс кнопки
class Button(QPushButton):
    def __init__(self, text, window):
        super().__init__(text, window)
        self.initButton()

    def initButton(self):
        # текст всплывающей подсказки (можно применять форматирование текста)
        self.setToolTip('<b>Кнопка</b>')

        # метод, возвращающий рекомендуемый размер для кнопки
        recommended_size = self.sizeHint()

        # изменение размеров виджета
        self.resize(recommended_size)

        # перемещение виджета на экране на координату 50, 50
        # self.move(50, 50)

        #self.clicked.connect(self.hide)

# класс основного окна
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # координаты окна и размеры окна одновременно
        # self.setGeometry(300, 300, 300, 220)

        # заголовок окна
        self.setWindowTitle('Заголовок')

        # изменение размеров виджета на 250 в ширину и 150 в высоту
        self.resize(250, 150)

        # сделать окно нерастягиваемым
        self.setFixedSize(self.size())

        # перемещение виджета на экране на координату 300, 300
        # по умолчанию запускается по центру
        # self.move(300, 300)

        # иконка приложения при запуске
        self.setWindowIcon(QIcon('files/wb.png'))

        # текст всплывающей подсказки (можно применять форматирование текста)
        self.setToolTip('<b>Окно</b>')

if __name__ == '__main__':
    # Каждое приложение PyQt5 должно создать объект приложения (экземпляр QApplication).
    # Параметр sys.argv это список аргументов командной строки.
    # Скрипты Python можно запускать из командной строки.
    # Это способ, которым можно контролировать запуск приложения
    app = QApplication(sys.argv)

    # шрифт всплывающих подсказок
    QToolTip.setFont(QFont('Roboto', 10))

    # виджет без родителей - окно
    # виджет сначала не показывается, а генерируется в памяти
    test_window = MainWindow()

    # показать виджет окна
    test_window.show()

    # создание виджета кнопки на окне
    test_button = Button('Надпись на кнопке', test_window)

    # переместить кнопку на координаты 50, 50
    test_button.move(50, 50)

    # показать виджет кнопки
    test_button.show()

    # создание виджета кнопки на окне
    quit_button = Button('Кнопка выключения', test_window)

    # переместить кнопку на координаты 150, 50
    quit_button.move(50, 80)

    # назначение функции при клике на кнопку
    # при клике - выход из приложения
    quit_button.clicked.connect(QCoreApplication.instance().quit)

    # показать кнопку выхода
    quit_button.show()

    # создание виджета кнопки на окне
    hide_button = Button('Кнопка скрытия', test_window)

    # переместить кнопку на координаты 50, 110
    hide_button.move(50, 110)

    # назначение функции при клике на кнопку
    # при клике - скрыть кнопку
    hide_button.clicked.connect(hide_button.hide)

    # переместить кнопку на координаты 150, 50
    hide_button.show()

    # выход из приложения
    sys.exit(app.exec_())