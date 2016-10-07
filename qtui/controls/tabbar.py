from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic

DEBUG = False

if DEBUG:
    from sys import stdout
    debug = lambda *a: stdout.write(' '.join(map(str, a)) + '\n')
else:
    debug = lambda *a: None

Qt.QT_NO_DEBUG_OUTPUT = True


class TabBar(QTabBar):
    def __init__(self, parent=None):
        super(TabBar, self).__init__(parent)
        self.parent = parent

    # def mousePressEvent(self, event):
    #     super(TabBar, self).mousePressEvent(event)
    #     debug("pressed")
    #     debug(self.tabAt(event.pos()))

    def mouseReleaseEvent(self, event):
        super(TabBar, self).mouseReleaseEvent(event)
        debug(event.pos)
        debug(self.tabAt(event.pos()))
        if self.tabAt(event.pos()) == self.count() - 1:
            self.parent.addCustomTab()
        # debug("released\n")


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = TabBar()
    win.show()
    sys.exit(app.exec_())
