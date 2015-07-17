from PyQt4.QtGui import QTabWidget, QWidget
from PyQt4 import uic

class Page(QWidget):
    def __init__(self, parent=None):
        super(Page, self).__init__(parent)
        uic.loadUi('tabpage.ui')


class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent)
        self.setTabsCloseable(True)
        self.setMovable(True)
        self.setDocumentMode(False)
        self.currentChanged.connect(self.currentIndexChanged)
        self.num = 1

        self.addTab(QWidget(), '+')
        self.addCustomTab()

    def addCustomTab(self):
        page = Page()
        self.insert(self.count() - 1, page, "Answer %d" % self.num)
        self.num += 1
        self.setCurrentWidget(widget)

    def currentIndexChanged(self, index):
        if index == self.count() - 1:
            self.addCustomTab()
