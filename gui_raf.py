import io
import sys
from data_processing.google_api import get_df_with_geocodes
import folium
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtWebEngineWidgets


def add_location_map(locations, m):
    for location_f in locations:
        folium.Marker(location=location_f[1], popup=f'{location_f[0]}', tooltip='Click here to see full address',
                      icon=folium.Icon(color="blue", icon="info-sign")).add_to(m)


def table_loop(locations, table):
    for i, location_f in enumerate(locations):
        table.setItem(i, 0, QTableWidgetItem(location_f[0]))


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()
        self.input_path = ''
        self.location_path = ''


    def initWindow(self):
        self.setWindowTitle(self.tr("Hack the tracK!"))
        self.setFixedSize(1500, 800)
        self.buttonUI()

    def btn_input_choose_file(self):
        print('im in da function')
        filename = QFileDialog.getOpenFileName()
        print(filename[0])
        self.input_path = filename[0]

    def btn_locations_choose_file(self):
        filename = QFileDialog.getOpenFileName()
        print(filename[0])
        self.location_path = filename[0]

        df = get_df_with_geocodes(self.input_path, self.location_path)
        df['lat/lng'] = df[['lat_n', 'lng_n']].values.tolist()

        input_list = df[df['isStart'] == True][['formatted_address_n', 'lat/lng']].values.tolist()
        locations_list = df[df['isStart'] == False][['formatted_address_n', 'lat/lng']].values.tolist()

        m = folium.Map(location=input_list[0][1], zoom_start=15)

        folium.Marker(location=input_list[0][1], popup=f'{input_list[0][0]}', tooltip='Click here to see full address',
                      icon=folium.Icon(color="green", icon="info-sign")).add_to(m)

        add_location_map(locations_list, m=m)

        data = io.BytesIO()
        m.save(data, close_file=False)

        while self.tableWidget.rowCount() > 0:
            self.tableWidget.removeRow(0)
        self.tableWidget.setRowCount(len(locations_list))
        self.tableWidget.setColumnCount(1)

        table_loop(locations_list, self.tableWidget)
        self.tableWidget.move(0, 0)

        self.view.setHtml(data.getvalue().decode())
        self.show()

    def buttonUI(self):
        input_button = QtWidgets.QPushButton(self.tr("Starting point JSON file"))
        locations_button = QtWidgets.QPushButton(self.tr("Locations JSON file"))
        HackTheTrack_button = QtWidgets.QPushButton(self.tr("HackTheTrack!"))
        exit_button = QtWidgets.QPushButton(self.tr("Exit"))

        input_button.setFixedSize(180, 50)
        locations_button.setFixedSize(180, 50)
        HackTheTrack_button.setFixedSize(180, 50)
        exit_button.setFixedSize(180, 50)

        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.setGeometry(50, 50, 400, 100)

        self.createTable()

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)

        input_button.clicked.connect(self.btn_input_choose_file)
        locations_button.clicked.connect(self.btn_locations_choose_file)
        HackTheTrack_button.clicked.connect(self.HackTheTrack)
        exit_button.clicked.connect(self.closeEvent)
        self.tableWidget.doubleClicked.connect(self.on_click)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        lay = QtWidgets.QHBoxLayout(central_widget)

        button_container = QtWidgets.QWidget()
        vlay = QtWidgets.QVBoxLayout(button_container)
        vlay.setSpacing(20)
        vlay.addStretch()
        vlay.addWidget(input_button)
        vlay.addWidget(locations_button)
        vlay.addWidget(HackTheTrack_button)
        vlay.addWidget(exit_button)
        vlay.addStretch()
        lay.addWidget(button_container)
        lay.addWidget(self.view, stretch=1)
        lay.addWidget(self.tableWidget)

        self.show()

    def HackTheTrack(self):
        df = get_df_with_geocodes(self.location_path, self.input_path)
        df['lat/lng'] = df[['lat_n', 'lng_n']].values.tolist()

        input_list = df[df['isStart'] == True][['formatted_address_n', 'lat/lng']].values.tolist()
        locations_list = df[df['isStart'] == False][['formatted_address_n', 'lat/lng']].values.tolist()

        # QtWidgets.QHBoxLayout(QtWidgets.QWidget()).addWidget(self.tableWidget)


        m = folium.Map(location=input_list[0][1], zoom_start=15)

        folium.Marker(location=input_list[0][1], popup=f'{input_list[0][0]}', tooltip='Click here to see full address',
                      icon=folium.Icon(color="green", icon="info-sign")).add_to(m)

        add_location_map(locations_list, m=m)

        data = io.BytesIO()
        m.save(data, close_file=False)

        # self.tableWidget.setRowCount(len(locations_list))
        # self.tableWidget.setColumnCount(1)
        #
        # table_loop(locations_list)
        # self.tableWidget.move(0, 0)
        #
        # self.view.setHtml(data.getvalue().decode())

    def createTable(self):
        # Create table
        self.tableWidget = QTableWidget()
        # self.tableWidget.setRowCount(1)
        # self.tableWidget.setColumnCount(2)
        self.tableWidget.move(0, 0)

        # table selection change
        self.tableWidget.doubleClicked.connect(self.on_click)

    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

    def closeEvent(self, event):
        close = QtWidgets.QMessageBox.question(self,
                                               "QUIT",
                                               "Are you sure want to quit?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if close == QtWidgets.QMessageBox.Yes:
            sys.exit(App.exec())
        else:
            event.ignore()


if __name__ == "__main__":
    App = QtWidgets.QApplication(sys.argv)
    window = Window()

    window.show()
    sys.exit(App.exec())

