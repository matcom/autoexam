#! /usr/bin/python
#-*-coding: utf8-*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
import qtui.model
import os.path


class QuestionWidget(QWidget):
    def __init__(self, parent=None):
        super(QuestionWidget, self).__init__(parent)
        self.ui = uic.loadUi(os.path.join(os.environ['AUTOEXAM_FOLDER'], "qtui/ui/question.ui"), self)
        self.current = -1
        self.connectSignals()
        # item = self.ui.idsWidget.addCustomItem()
        # self.ui.idsWidget.editItem(item)

    def initializeProject(self, project):
        self.project = project
        self.questions = project.questions

        self.ui.idsWidget.clear()

        for question in self.questions:
            self.ui.idsWidget.addItem(question.id)

        if len(self.questions) > 0:
            self.changeCurrentQuestion(0)
            self.current = 0

        print 'project', project

    def connectSignals(self):
        self.ui.idsWidget.rowAdded.connect(self.addQuestion)
        self.ui.idsWidget.rowChanged.connect(self.changeQuestionId)
        self.ui.idsWidget.rowRemoved.connect(self.removeQuestion)
        self.ui.idsWidget.currentRowChanged.connect(self.changeCurrentQuestion)

    def addQuestion(self, question_id):
        # save question and answers
        question = qtui.model.Question(str(question_id), '', '', [])
        if self.questions:
            # self.printStatus()
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

        question = qtui.model.Question(q_id, tag_names, text, answers)
        if index >= len(self.questions):
            self.questions.append(question)
        else:
            self.questions[index] = qtui.model.Question(q_id, tag_names, text, answers)

    def changeCurrentQuestion(self, index):
        if self.current != -1:
            # self.printStatus()
            self.saveQuestion(self.current)
        if index != -1:
            self.ui.questionEdit.setPlainText(self.questions[index].text)
            self.ui.tagsEdit.setText(' '.join(self.questions[index].tag_names))
            self.ui.answersWidget.reset(self.questions[index].answers)
            self.current = index
            self.ui.idsWidget.setCurrentItem(self.ui.idsWidget.item(index))

    def getTags(self):
        tag_names = set()
        for question in self.questions:
            tag_names.update(set(question.tag_names))
        return [qtui.model.Tag(tag_name, 0) for tag_name in tag_names]

    def dump(self):
        if 0 <= self.current < len(self.questions):
            self.saveQuestion(self.current)
        return self.getTags(), self.questions


# if __name__ == '__main__':
#     import model
#     import sys
#     app = QApplication(sys.argv)
#     win = QuestionWidget()
#     win.show()
#     sys.exit(app.exec_())
