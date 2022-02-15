import sys, webbrowser, requests
from PyQt5.QtWidgets import (QWidget, QApplication, QGridLayout, QLabel,
                             QScrollArea, QPushButton, QComboBox, QGroupBox, QLineEdit)
# from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtTest import QTest

import modules.wildberries.analytics as wb_analytics
import modules.wildberries.info as wb_info

supplier = ''


class LineWithSaveButton(QLineEdit):
    card = None
    headers = None
    button = None

    def __init__(self, line_text, card):
        super().__init__(line_text)
        self.init_connection(card)

    def init_connection(self, card):
        self.button = QPushButton('Сохранить')
        self.button.clicked.connect(self.save_name)
        self.headers = {'Authorization': wb_info.api_key('token', supplier)}
        self.card = card

    def save_name(self):
        body = {"id": 1,
                "jsonrpc": "2.0",
                "params": {
                    "card": self.card,
                    "supplierID": wb_info.api_key('x32', supplier)}
                }
        for i in range(len(body["params"]["card"]["addin"])):
            if body["params"]["card"]["addin"][i]["type"] == 'Наименование':
                body["params"]["card"]["addin"][i]['params'][0]['value'] = self.text()
        response = requests.post("https://suppliers-api.wildberries.ru/card/update", json=body, headers=self.headers)
        if 200 <= response.status_code < 300:
            print(f'Успешно заменено наименование: {self.text()}')
            self.button.setStyleSheet('QPushButton {color: green;}')
            QTest.qWait(1500)
            self.button.setStyleSheet('QPushButton {color: black;}')
        else:
            print(f'Ошибка при замене: {self.text()}')
            self.button.setStyleSheet('QPushButton {color: red;}')
            QTest.qWait(1500)
            self.button.setStyleSheet('QPushButton {color: black;}')


class LinkButton(QPushButton):
    url = None

    def __init__(self, text, sku):
        super().__init__(text)
        self.init_button(sku)

    def init_button(self, sku):
        self.url = f'https://www.wildberries.ru/catalog/{sku}/detail.aspx'
        self.clicked.connect(self.open_browser)

    def open_browser(self):
        webbrowser.open(self.url)


class Renamer(QWidget):
    grid = None
    rows = list() # строки, сформированные из карт
    # [[QLabel(imtId), QLineEdit(Наименование),
    # QPushButton('Сохранить'), QPushButton('Ссылка'), card_data], ...]
    download_label = None

    def __init__(self):
        super().__init__()
        self.init_main()

    def init_main(self):
        self.setWindowTitle('Переименовщик')
        self.resize(900, 480)
        self.setFixedSize(self.size())
        self.setWindowIcon(QIcon('files/wb.png'))

        company_label = QLabel('Организация', self)
        company_label.setFont(QFont('Roboto', 10))
        company_label.resize(company_label.sizeHint())
        company_label.move(20, 20)

        supplier_choice = QComboBox(self)
        supplier_choice.setFixedWidth(200)
        supplier_choice.move(105, 18)
        supplier_choice.currentTextChanged.connect(self.change_supplier)
        supplier_names_list = wb_info.suppliers_names()
        global supplier
        supplier = wb_info.supplier_by_name(supplier_names_list[0])
        supplier_choice.addItems(supplier_names_list)

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
        refresh_button.clicked.connect(self.refresh_results)

    def change_supplier(self, text):
        global supplier
        supplier = wb_info.supplier_by_name(text)

    def refresh_results(self):
        self.download_label.show()
        QTest.qWait(10)
        self.delete_old_results()
        self.add_new_results()
        self.download_label.hide()

    def add_new_results(self):
        global supplier
        cards = wb_analytics.fetch_cards(supplier=supplier)
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

            self.rows[i].append(LinkButton("Ссылка", cards[i]['nomenclatures'][0]['nmId']))
            self.grid.addWidget(self.rows[i][3], i, 3)

            self.rows[i].append(cards[i])

    def delete_old_results(self):
        for row in self.rows:
            for widget in row[:-1]: widget.deleteLater()
        self.rows = list()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Renamer()
    window.show()
    sys.exit(app.exec_())
