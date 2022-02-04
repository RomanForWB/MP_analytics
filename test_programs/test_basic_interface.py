import sys

# QtWidgets - базовый класс для любого объекта из PyQt
from PyQt5.QtWidgets import (QWidget, QApplication, QGridLayout, QLabel,
                             QScrollArea, QHBoxLayout, QVBoxLayout)
from PyQt5.QtGui import QIcon

if __name__ == '__main__':
    # Каждое приложение PyQt5 должно создать объект приложения (экземпляр QApplication).
    # Параметр sys.argv это список аргументов командной строки.
    # Скрипты Python можно запускать из командной строки.
    # Это способ, которым можно контролировать запуск приложения
    app = QApplication(sys.argv)

    # виджет без родителей - окно
    # виджет сначала не показывается, а генерируется в памяти
    test_window = QWidget()

    # изменение размеров виджета на 250 в ширину и 150 в высоту
    test_window.resize(250, 150)

    # перемещение виджета на экране на координату 300, 300
    # по умолчанию запускается по центру
    # test_window.move(300, 300)

    # значок приложения
    test_window.setWindowIcon(QIcon('files/wb.png'))

    # заголовок окна
    test_window.setWindowTitle('Заголовок')

    # показать виджет
    test_window.show()

    # выход из приложения
    sys.exit(app.exec_())