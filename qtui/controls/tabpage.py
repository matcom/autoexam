#! /usr/bin/python
#-*-coding: utf8-*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
from qtui.model import Answer
import os, os.path


class TabPage(QWidget):
    def __init__(self, content=None):
        super(TabPage, self).__init__()
        self.ui = uic.loadUi(os.path.join(os.environ['AUTOEXAM_FOLDER'], "qtui/ui/tabpage.ui"), self)
        if content:
            self.addContent(content)

    def addContent(self, content):
        self.ui.rightBox.setChecked(content.valid)
        self.ui.fixedBox.setChecked(content.fixed_position)
        self.ui.questionEdit.setPlainText(content.text)

    def dump(self):
        right = self.ui.rightBox.isChecked()
        fixed = self.ui.fixedBox.isChecked()
        text = str(self.ui.questionEdit.toPlainText().toUtf8()).decode('utf-8')
        return Answer(right, fixed, text)
