#! /usr/bin/python
#-*-coding: utf8-*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic

from tabbar import TabBar
from tabpage import TabPage
from closebutton import CloseButton
from qtui.model import Answer

DEBUG = True

if DEBUG:
    from sys import stdout
    debug = lambda *a: stdout.write(' '.join(map(str, a)) + '\n')
else:
    debug = lambda *a: None

QT_NO_DEBUG_OUTPUT = True


class TabWidget(QTabWidget):
    def __init__(self, parent=None, content=None):
        super(TabWidget, self).__init__(parent)
        self.setMovable(True)
        self.setDocumentMode(False)
        self.initBar()
        self.initTabs()
        if not content:
            self.addCustomTab()
        else:
            self.addContent(content)

    def initTabs(self):
        self.num = 1
        self.clear()
        self.addTab(QWidget(), '+')
        self.setTabEnabled(0, False)

    def addContent(self, content):
        for item in content:
            self.addCustomTab(item)

    def initBar(self):
        self.tab_bar = TabBar(self)
        self.setTabBar(self.tab_bar)

    def addCustomTab(self, content=None):
        page = TabPage(content)
        pos = self.count() - 1
        self.insertTab(pos, page, "Answer %d" % self.num)
        self.tab_bar.setTabButton(pos, QTabBar.RightSide, CloseButton(page, self))
        self.num += 1
        self.setCurrentWidget(page)

    def closeTabAt(self, index):
        self.widget(index).destroy()
        self.removeTab(index)
        if self.count() == 1:
            self.addCustomTab()

    def closeTab(self, widget):
        widget.destroy()
        self.removeTab(self.indexOf(widget))
        if self.count() == 1:
            self.addCustomTab()

    def tabRemoved(self, index):
        if index == self.count() - 1:
            self.setCurrentIndex(index - 1)

    def reset(self, content=None):
        self.num = 1
        if content:
            self.initTabs()
            self.addContent(content)
            self.setCurrentIndex(0)
        else:
            for i in xrange(self.count() - 1):
                self.closeTabAt(0)

    def dump(self):
        answers = []
        for i in xrange(self.count() - 1):
            answers.append(self.widget(i).dump())
        return answers


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = TabWidget()
    win.show()
    sys.exit(app.exec_())
