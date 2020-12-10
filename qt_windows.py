import datetime
import sys

from main_ui import Ui_Form
from PyQt5.QtWidgets import *
import socket
import os
import time

IP = "172.20.47.75"
PORT = 80


def exception_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class MainWindow(QWidget, Ui_Form):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Ground control system")
        self.show()
        self.enable_lights_btn.clicked.connect(self.enableLights)
        self.disable_lights_btn.clicked.connect(self.disableLights)
        self.enable_trackers_btn.clicked.connect(self.enableTrackers)
        self.disable_trackers_btn.clicked.connect(self.disableTrackers)
        self.enable_all_btn.clicked.connect(self.enableAll)
        self.disable_all_btn.clicked.connect(self.disableAll)
        self.reboot_btn.clicked.connect(self.rebootDrone)
        self.ping_btn.clicked.connect(self.pingDrone)
        self.get_temp_btn.clicked.connect(self.updateTemperature)
        self.get_press_btn.clicked.connect(self.updatePressure)
        self.get_alt_btn.clicked.connect(self.updateAltitude)
        self.get_hum_btn.clicked.connect(self.updateHumidity)

        self.launch1.clicked.connect(self.launch1engine)
        self.launch2.clicked.connect(self.launch2engine)
        self.launch3.clicked.connect(self.launch3engine)

        self.stop1.clicked.connect(self.stop1engine)
        self.stop2.clicked.connect(self.stop2engine)
        self.stop3.clicked.connect(self.stop3engine)

    def updateTemperature(self):
        print(self.sendMessage("update_temperature"))

    def updateAltitude(self):
        print(self.sendMessage("update_altitude"))

    def updatePressure(self):
        print(self.sendMessage("update_pressure"))


    def updateHumidity(self):
        print(self.sendMessage("update_humidity"))


    def checkConnection(self):
        ret = os.system(f"ping -o -c 1 -W {PORT} {IP}")
        return ret == 0

    def sendMessage(self, message):
        if not self.checkConnection():
            QMessageBox.warning(self, "Module is Offline", "Check the connection to the drone.")
            return None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((IP, PORT))
            sock.send(message.encode("utf-8"))
            data = sock.recv(1024)
            if data is None:
                QMessageBox.warning(self, "Error", "Couldn't connect to drone.")
                return None
            data = list(map(lambda x: x.split("="), data.decode("utf-8").split(";")))[:-1]
            data = {key: val for key, val in data}
            self.updateValues(data)
            return data
        except Exception as e:
            QMessageBox.warning(self, type(e).__name__, str(e))

    def updateValues(self, json):
        time = str(datetime.datetime.now().strftime("%H:%M:%S"))
        print(time)
        if "trackers_are_on" in json:
            self.trackers_status.setText(json["trackers_are_on"].capitalize())
            self.trackers_upd_time.setText(time)
        if "lights_are_on" in json:
            self.lights_status.setText(json["lights_are_on"].capitalize())
            self.lights_upd_time.setText(time)
        if "temperature" in json:
            self.temperature_status.setText(f'{int(float(json["temperature"]))} °C')
            self.temperature_upd_time.setText(time)
        if "humidity" in json:
            self.humidity_status.setText(f"{float(json['humidity']) * 100}%")
            self.humidity_upd_time.setText(time)
        if "pressure" in json:
            self.pressure_status.setText(json["pressure"])
            self.pressure_upd_time.setText(time)
        if "altitude" in json:
            self.altitude_status.setText(json["altitude"] + "m")
            self.altitude_upd_time.setText(time)


    def enableLights(self):
        print(self.sendMessage("enable_lights"))

    def enableTrackers(self):
        print(self.sendMessage("enable_trackers"))

    def disableLights(self):
        print(self.sendMessage("disable_lights"))

    def disableTrackers(self):
        print(self.sendMessage("disable_trackers"))

    def rebootDrone(self):
        print(self.sendMessage("reboot"))

    def enableAll(self):
        print(self.sendMessage("enable_all"))

    def disableAll(self):
        print(self.sendMessage("disable_all"))

    def pingDrone(self):
        print(self.sendMessage("ping"))

    def launch1engine(self):
        print(self.sendMessage("enable_left_engine"))

    def launch2engine(self):
        print(self.sendMessage("enable_middle_engine"))

    def launch3engine(self):
        print(self.sendMessage("enable_right_engine"))

    def stop1engine(self):
        print(self.sendMessage("disable_left_engine"))

    def stop2engine(self):
        print(self.sendMessage("disable_middle_engine"))

    def stop3engine(self):
        print(self.sendMessage("disable_right_engine"))


sys.excepthook = exception_hook
app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())
"""pyuic5 main.ui -o main_ui.py"""
