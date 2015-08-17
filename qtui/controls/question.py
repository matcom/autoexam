#! /usr/bin/python
#-*-coding: utf8-*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
from qtui.model import *
import os.path


class QuestionWidget(QWidget):
    def __init__(self, parent=None):
        super(QuestionWidget, self).__init__(parent)
        self.ui = uic.loadUi(os.path.join(os.environ['AUTOEXAM_FOLDER'],"qtui/ui/question.ui"), self)
        self.questions = []
        self.current = -1
        self.connectSignals()
        item = self.ui.idsWidget.addCustomItem()
        self.ui.idsWidget.editItem(item)

    def connectSignals(self):
        self.ui.idsWidget.rowAdded.connect(self.addQuestion)
        self.ui.idsWidget.rowChanged.connect(self.changeQuestionId)
        self.ui.idsWidget.rowRemoved.connect(self.removeQuestion)
        self.ui.idsWidget.currentRowChanged.connect(self.changeCurrentQuestion)

    def addQuestion(self, question_id):
        # save question and answers
        question = Question(question_id, '', '', [])
        if self.questions:
            self.saveQuestion(self.current)
        self.ui.questionEdit.clear()
        self.tagsEdit.clear()
        self.ui.answersWidget.reset()
        self.questions.append(question)
        self.current = len(self.questions) - 1

    def printStatus(self):
        print 'questions:', self.questions
        print 'current', self.current
        pass

    def changeQuestionId(self, index, question_id):
        self.questions[index].id = question_id

    def removeQuestion(self, index):
        del(self.questions[index])
        self.ui.questionEdit.clear()
        self.tagsEdit.clear()

    def saveQuestion(self, index):
        q_id = str(self.idsWidget.item(index).text())
        tag_names = str(self.ui.tagsEdit.text()).split()
        text = str(self.questionEdit.toPlainText())
        answers = self.answersWidget.dump()
        self.questions[index] = Question(q_id, tag_names, text, answers)

    def changeCurrentQuestion(self, index):
        if index != -1:
            self.saveQuestion(self.current)
            self.ui.questionEdit.setPlainText(self.questions[index].text)
            self.ui.tagsEdit.setText(' '.join(self.questions[index].tag_names))
            self.ui.answersWidget.reset(self.questions[index].answers)
            self.current = index

    def getTags(self):
        tag_names = set()
        for question in self.questions:
            tag_names.update(set(question.tag_names))
        return [Tag(tag_name, 0) for tag_name in tag_names]

    def dump(self):
        if 0 <= self.current < len(self.questions):
            self.saveQuestion(self.current)
        return self.getTags(), self.questions


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = QuestionWidget()
    win.show()
    sys.exit(app.exec_())
