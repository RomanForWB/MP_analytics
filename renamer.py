import sys, time
from PyQt5.QtWidgets import (QWidget, QApplication, QGridLayout, QLabel,
                             QScrollArea, QHBoxLayout, QVBoxLayout, QToolTip,
                             QPushButton, QComboBox, QGroupBox, QFormLayout, QLineEdit)
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtTest import QTest
from modules.wildberries import fetch_cards
import webbrowser
import requests

WILDBERRIES_SUPPLIER_KEYS_64 = {'ИП Марьина А.А.' : 'MmY1ZTU0ZTUtN2E2NC00YmI5LTgwNTgtODU4MWVlZTRlNzVh',
                             'ИП Туманян А.А.' : 'OGY2MWFhYWEtMmJjYi00YzdkLWFjMDYtZDY1Y2FkMzFjZmUy',
                             'ООО НЬЮЭРАМЕДИА' : 'NmEyMWYyZTItNTNmZi00NjZkLWIwNTMtYTU1MTI0NzgwZTIw',
                             'ИП Ахметов В.Р.' : 'OWVhNTlhMTQtNjAwYi00ZmZkLTgzNGQtNzFlZTI1NTdmMGVi'}

WILDBERRIES_SUPPLIER_KEYS_32 = {'ИП Марьина А.А.' : '2f5e54e5-7a64-4bb9-8058-8581eee4e75a'}

WILDBERRIES_TOKENS = {'ИП Марьина А.А.' : 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6IjgyOGMzOTJmLWJkMzUtNDRjYi04MDM5LTFjODQ3ZjQ1YmEzNSJ9.5D_uGQ5yt4KsAd_4Og9qMRbzZ6praIYdtQAnWG9IU6Q'}

supplier = 'ИП Марьина А.А.'

class LineWithSaveButton(QLineEdit):
    card = None
    headers = None
    button = None
    def __init__(self, line_text, card):
        super().__init__(line_text)
        self.initConnection(card)
    def initConnection(self, card):
        self.button = QPushButton('Сохранить')
        self.button.clicked.connect(self.saveName)
        self.headers = {'Authorization': WILDBERRIES_TOKENS[supplier]}
        self.card = card
    def saveName(self):
        body = {"id": 1,
                "jsonrpc": "2.0",
                "params": {
                    "card": self.card,
                    "supplierID": WILDBERRIES_SUPPLIER_KEYS_32[supplier]}
                }
        for i in range(len(body["params"]["card"]["addin"])):
            if body["params"]["card"]["addin"][i]["type"] == 'Наименование':
                body["params"]["card"]["addin"][i]['params'][0]['value'] = self.text()
                print(self.text())
        response = requests.post("https://suppliers-api.wildberries.ru/card/update", json=body, headers=self.headers)
        if response.status_code >= 200 and response.status_code < 300:
            print('Успешно заменено наименование')
            self.button.setStyleSheet('QPushButton {color: green;}')
            QTest.qWait(1000)
            self.button.setStyleSheet('QPushButton {color: black;}')
        else:
            print('Ошибка')
            self.button.setStyleSheet('QPushButton {color: red;}')
            QTest.qWait(1000)
            self.button.setStyleSheet('QPushButton {color: black;}')

class LinkButton(QPushButton):
    url = None
    def __init__(self, text, sku):
        super().__init__(text)
        self.initButton(sku)
    def initButton(self, sku):
        self.url = f'https://www.wildberries.ru/catalog/{sku}/detail.aspx'
        self.clicked.connect(self.openBrowser)
    def openBrowser(self):
        webbrowser.open(self.url)

class Renamer(QWidget):
    grid = None
    rows = list() # [[QLabel(imtId), QLineEdit(Наименование),
                   # QPushButton('Сохранить'), QPushButton('Ссылка'), card_data], ...]
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
        company_choice.addItems(list(WILDBERRIES_SUPPLIER_KEYS_64.keys()))
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
        QTest.qWait(10)
        self.deleteOldResults()
        self.addNewResults()
        self.download_label.hide()

    def addNewResults(self):
        global supplier
        cards = fetch_cards(WILDBERRIES_TOKENS[supplier])
        for i in range(len(cards)):
            self.rows.append([])
            self.rows[i].append(QLabel(str(cards[i]['imtId'])))
            self.grid.addWidget(self.rows[i][0], i, 0)

            for type in cards[i]['addin']:
                if type['type'] == 'Наименование':
                    line = LineWithSaveButton(str(type['params'][0]['value']), cards[i])
                    self.rows[i].append(line)
                    self.grid.addWidget(self.rows[i][1], i, 1)
                    self.rows[i].append(line.button)
                    self.grid.addWidget(self.rows[i][2], i, 2)
                    break

            # self.rows[i].append(QPushButton("Сохранить"))
            # self.grid.addWidget(self.rows[i][2], i, 2)

            self.rows[i].append(LinkButton("Ссылка", cards[i]['nomenclatures'][0]['nmId']))
            self.grid.addWidget(self.rows[i][3], i, 3)

            self.rows[i].append(cards[i])

    def deleteOldResults(self):
        for row in self.rows:
            for widget in row[:-1]: widget.deleteLater()
        self.rows = list()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Renamer()
    window.show()
    sys.exit(app.exec_())