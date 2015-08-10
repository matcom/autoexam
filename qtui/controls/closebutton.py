from PyQt4.QtGui import *

class CloseButton(QPushButton):
    css = """
    background-color: rgb(255, 10, 46);
    border-color: rgb(0, 0, 0);
    color: rgb(255, 255, 255);
    """
    def __init__(self, parent, tabWidget):
        super(CloseButton, self).__init__("x", parent)
        self.parent = parent
        self.tabWidget = tabWidget
        self.setMaximumSize(18, 18)
        # self.setStyleSheet(self.css)
        self.clicked.connect(self.closeTab)

    def closeTab(self):
        self.tabWidget.closeTab(self.parent)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = CloseButton(None, None)
    win.show()
    sys.exit(app.exec_())
