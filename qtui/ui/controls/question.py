#! /usr/bin/python
#-*-coding: utf8-*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic

#import model

class Widget(QWidget):
    def __init__(self):
        super(Widget, self).__init__()
        self.ui = uic.loadUi("question.ui", self)
        item = self.ui.listWidget.addCustomItem()
        self.ui.listWidget.editItem(item)

    def getQuestions():
        pass


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = Widget()
    win.show()#Maximized
    sys.exit(app.exec_())
