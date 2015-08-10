from PyQt4.QtGui import *
from PyQt4.QtCore import *


REMOVE_KEYS = (Qt.Key_Backspace, Qt.Key_Delete)


class ListWidget(QListWidget):
    rowAdded = pyqtSignal([str]) # name
    rowChanged = pyqtSignal([int, str]) # index, name
    rowRemoved = pyqtSignal([int]) # index

    def __init__(self, parent=None):
        super(ListWidget, self).__init__(parent)
        self.doubleClicked.connect(self.itemDoubleClicked)
        self.itemChanged.connect(self.verifyItem)
        self.setAlternatingRowColors(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.item_clicked = False
        self.num = 1
        self.questions = []

    def addCustomItem(self):
        item = QListWidgetItem()
        item.setText("")
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        self.insertItem(self.count(), item)
        question_id = "Question %d" % self.num
        self.rowAdded.emit(question_id)
        item.setText(question_id)
        self.num += 1
        return item

    def itemDoubleClicked(self, index):
        self.item_clicked = True

    def verifyItem(self, item):
        text = item.text()
        row = self.row(item)
        if not text:
            # item cannot be empty
            self.takeItem(row)
            self.rowRemoved.emit(row)
            return
        for i in range(self.count()):
            other = self.item(i)
            if i != row and text == other.text():
                # item names must be unique
                self.takeItem(row)
                self.rowRemoved.emit(row)
                return
        self.rowChanged.emit(row, text)

    def mouseDoubleClickEvent(self, event):
        super(ListWidget, self).mouseDoubleClickEvent(event)
        if not self.item_clicked:
            item = self.addCustomItem()
            self.editItem(item)
        self.item_clicked = False

    def keyPressEvent(self, event):
        super(ListWidget, self).keyPressEvent(event)
        if event.key() in REMOVE_KEYS:
            index = self.currentRow()
            self.takeItem(index)
            self.rowRemoved.emit(index)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = ListWidget()
    win.show()
    sys.exit(app.exec_())
