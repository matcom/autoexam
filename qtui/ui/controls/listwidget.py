from __future__ import print_function
from PyQt4.QtGui import *
from PyQt4.QtCore import *

DEL = 16777223

class ListWidget(QListWidget):
    def __init__(self, parent=None):
        super(ListWidget, self).__init__(parent)
        self.doubleClicked.connect(self.itemDoubleClicked)
        self.itemChanged.connect(self.verifyItem)
        self.setAlternatingRowColors(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.item_clicked = False
        self.num = 1

    def addCustomItem(self):
        item = QListWidgetItem()
        item.setText("")
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        self.insertItem(self.count(), item)
        item.setText("Question %d" % self.num)
        self.num += 1
        return item

    def itemDoubleClicked(self, index):
        self.item_clicked = True

    def verifyItem(self, item):
        text = item.text()
        row = self.row(item)
        # print("editing", item.text(), "at", row)
        if not text:
            # item cannot be empty
            self.takeItem(row)
            return
        for i in range(self.count()):
            other = self.item(i)
            if i != row and text == other.text():
                # item names must be unique
                self.takeItem(row)
                return

    def mouseDoubleClickEvent(self, event):
        super(ListWidget, self).mouseDoubleClickEvent(event)
        if not self.item_clicked:
            item = self.addCustomItem()
            self.editItem(item)
        self.item_clicked = False

    def keyPressEvent(self, event):
        super(ListWidget, self).keyPressEvent(event)
        print(event.key(), QKeySequence.Delete)
        if event.key() == DEL:
            print("item %d will be deleted" % self.currentRow())
            self.takeItem(self.currentRow())


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = ListWidget()
    win.show()
    sys.exit(app.exec_())
