import sys
from os import environ

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QLocale, Qt
from loginWindow import LoginWindow
from credentials import databaseLogin, databasePassword

SERVER = '192.168.1.18,1433'
DATABASE = 'Baza'
USERNAME = databaseLogin
PASSWORD = databasePassword


def suppressQtWarnings():
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"


def main():
    suppressQtWarnings()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    QLocale.setDefault(QLocale(QLocale.English))
    loginWindow = LoginWindow(app)
    loginWindow.show()
    sys.exit(app.exec_())


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    main()
