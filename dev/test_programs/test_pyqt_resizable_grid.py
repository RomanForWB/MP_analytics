import sys

from PyQt5.QtWidgets import (QWidget, QApplication, QGridLayout, QLabel,
                             QScrollArea, QHBoxLayout, QVBoxLayout)
# класс основного окна
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.grid = QGridLayout()
        self.addComponents()

        layoutH = QHBoxLayout()
        layoutV = QVBoxLayout()

        scroll      = QScrollArea()
        self.widget = QWidget()
        layoutH.addWidget(scroll)
        self.widget.setLayout(self.grid)
        scroll.setWidget(self.widget)
        scroll.setWidgetResizable(True)

        layoutV.addLayout(layoutH)
        self.setLayout(layoutV)

    def addComponents(self):
        i = 0
        j = 0
        countLab = 0
        while i < 25:
            while j < 25:
                lab = QLabel('lab_'+str(countLab))
                self.grid.addWidget(lab, i, j)
                countLab += 1
                j += 1
            j = 0
            i += 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.setWindowTitle('Example')
    mainWindow.setGeometry(300, 100, 480, 320)
    mainWindow.show()
    sys.exit(app.exec_())