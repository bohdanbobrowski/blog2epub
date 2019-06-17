
import sys
from PyQt5.QtWidgets import (QApplication)
from PyQt5.QtWidgets import (QDialog, QGroupBox, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QTableView,
                             QMessageBox)
from PyQt5.QtGui import (QStandardItem, QStandardItemModel)


def main():
    app = QApplication(sys.argv)
    blog2epub_window = Blog2EpubQt()
    blog2epub_window.show()
    sys.exit(app.exec_())


class Blog2EpubQt(QDialog):
    # TODO: this is even not a sketch

    def __init__(self):
        super(KeywordCounterWindow, self).__init__()
        self.setWindowTitle("Keyword counter")
        self.input = self.draw_input()
        self.button = self.draw_button(self.button_clicked)
        self.table = self.draw_table()
        self.set_main_layout()

    def button_clicked(self):
        crawler = KeywordCounterCrawler(self.input.text())
        if crawler.download() is False:
            self.input.setText("")
            self.set_table_data([])
        else:
            message = QMessageBox();
            message.setIcon(QMessageBox.Information)
            message.setText("Entered url is correct")
            message.setInformativeText(str(len(crawler.keywords)) + " keywords found")
            message.setWindowTitle("Keyword Counter Message")
            message.setDetailedText(crawler.body)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec_()
            self.set_table_data(crawler.data)

    def set_main_layout(self):
        main_layout = QVBoxLayout()
        input_segment = self.draw_inputs_segment()
        main_layout.addWidget(input_segment)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

    def draw_inputs_segment(self):
        input_segment = QGroupBox("Enter address to count keywords")
        layout = QHBoxLayout()
        layout.addWidget(self.input, 0)
        layout.addWidget(self.button)
        input_segment.setLayout(layout)
        return input_segment

    def set_table_data(self, data):
        table_model = QStandardItemModel()
        table_model.setHorizontalHeaderLabels(['Keyword', 'Count'])
        for row in data:
            qrow = []
            for item in row:
                qitem = QStandardItem(str(item))
                qrow.append(qitem)
            table_model.appendRow(qrow)
        self.table.setModel(table_model)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    @staticmethod
    def draw_button(callback):
        button = QPushButton("START")
        button.clicked.connect(callback)
        return button

    @staticmethod
    def draw_input():
        input = QLineEdit()
        input.setFixedWidth(400)
        input.setText("http://")
        return input

    @staticmethod
    def draw_table():
        tv = QTableView()
        tv.setMinimumSize(400, 400)
        tv.setShowGrid(False)
        vh = tv.verticalHeader()
        vh.setVisible(False)
        hh = tv.horizontalHeader()
        hh.setStretchLastSection(True)
        tv.setSortingEnabled(True)
        return tv
