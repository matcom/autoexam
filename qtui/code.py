#!/usr/bin/python3
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic

class Win(QMainWindow):
    def __init__(self):
        super(Win, self).__init__()

        self.ui = uic.loadUi("./ui/main.ui", self)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = Win()
    win.showMaximized()
    sys.exit(app.exec_())
