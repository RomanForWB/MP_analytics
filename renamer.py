import sys, time
from PyQt5.QtWidgets import (QWidget, QApplication, QGridLayout, QLabel,
                             QScrollArea, QHBoxLayout, QVBoxLayout, QToolTip,
                             QPushButton, QComboBox, QGroupBox, QFormLayout, QLineEdit)
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon, QFont

WILDBERRIES_SUPPLIER_KEYS = {'ИП Марьина А.А.' : 'MmY1ZTU0ZTUtN2E2NC00YmI5LTgwNTgtODU4MWVlZTRlNzVh',
                             'ИП Туманян А.А.' : 'OGY2MWFhYWEtMmJjYi00YzdkLWFjMDYtZDY1Y2FkMzFjZmUy',
                             'ООО НЬЮЭРАМЕДИА' : 'NmEyMWYyZTItNTNmZi00NjZkLWIwNTMtYTU1MTI0NzgwZTIw',
                             'ИП Ахметов В.Р.' : 'OWVhNTlhMTQtNjAwYi00ZmZkLTgzNGQtNzFlZTI1NTdmMGVi'}

class Renamer(QWidget):
    grid = None
    card_ids = list()
    card_names = list()
    save_buttons = list()
    link_buttons = list()
    download_label = None
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Переименовщик')
        self.resize(900, 480)
        self.setFixedSize(self.size())
        self.setWindowIcon(QIcon('files/wb.png'))

        company_label = QLabel('Организация', self)
        company_label.setFont(QFont('Roboto', 10))
        company_label.resize(company_label.sizeHint())
        company_label.move(20, 20)

        company_choice = QComboBox(self)
        company_choice.addItems(list(WILDBERRIES_SUPPLIER_KEYS.keys()))
        company_choice.setFixedWidth(200)
        company_choice.move(105, 18)

        self.download_label = QLabel("<p style=\"color: grey;\">Загрузка...</p>", self)
        self.download_label.setFont(QFont('Roboto', 10))
        self.download_label.resize(company_label.sizeHint())
        self.download_label.move(420, 20)
        self.download_label.hide()

        result_box = QGroupBox(self)
        self.grid = QGridLayout()
        result_box.setLayout(self.grid)
        scroll = QScrollArea(self)
        scroll.setWidget(result_box)
        scroll.setWidgetResizable(True)
        scroll.setGeometry(20, 55, 860, 410)

        refresh_button = QPushButton('Обновить', self)
        refresh_button.move(320, 17)
        refresh_button.clicked.connect(self.refreshResults)

    def refreshResults(self):
        self.download_label.show()
        self.deleteOldResults()
        self.addNewResults()
        self.download_label.hide()

    def addNewResults(self):
        for i in range(20):
            self.card_ids.append(QLabel("00000000"))
            self.grid.addWidget(self.card_ids[i], i, 0)
            self.card_names.append(QLineEdit())
            self.grid.addWidget(self.card_names[i], i, 1)
            self.save_buttons.append(QPushButton("Сохранить"))
            self.grid.addWidget(self.save_buttons[i], i, 2)
            self.link_buttons.append(QPushButton("Ссылка"))
            self.grid.addWidget(self.link_buttons[i], i, 3)
    def deleteOldResults(self):
        for i in range(len(self.card_ids)):
            self.card_ids[i].deleteLater()
        self.card_ids = list()
        for i in range(len(self.card_names)):
            self.card_names[i].deleteLater()
        self.card_names = list()
        for i in range(len(self.save_buttons)):
            self.save_buttons[i].deleteLater()
        self.save_buttons = list()
        for i in range(len(self.link_buttons)):
            self.link_buttons[i].deleteLater()
        self.link_buttons = list()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Renamer()
    #window.addNewResults()
    window.show()
    sys.exit(app.exec_())