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
            self.ui.idsWidget.setCurrentRow(0)

        # print 'project', project

    def connectSignals(self):
        self.ui.idsWidget.rowAdded.connect(self.newQuestion)
        self.ui.idsWidget.rowRenamed.connect(self.renameQuestion)
        self.ui.idsWidget.rowRemoved.connect(self.removeQuestion)
        self.ui.idsWidget.currentItemChanged.connect(self.saveQuestionOnChange)
        self.ui.idsWidget.currentRowChanged.connect(self.__loadQuestionData__)
        self.ui.minusButton.clicked.connect(self.ui.idsWidget.removeCurrentItem)
        self.ui.plusButton.clicked.connect(self.ui.idsWidget.addCustomItem)

    def newQuestion(self, question_id):
        # save question and answers
        question = qtui.model.Question(str(question_id), ['default'], 'Place {question_number}\'s text here.'.format(question_number=question_id), [qtui.model.Answer(False, False,'This is a default answer for {question_number}'.format(question_number=question_id))])

        self.questions.append(question)
        self.ui.idsWidget.setCurrentRow(len(self.questions) - 1)

    def renameQuestion(self, index, question_id):
        self.questions[index].id = question_id

    def removeQuestion(self, index):
        del self.questions[index]
        if len(self.questions) == 0:
            self.clearQuestionData()

    def saveQuestionOnChange(self, new_item, old_item):
        print 'saving item: ', old_item
        if old_item is not None:
            self.saveQuestion(self.idsWidget.row(old_item))
        print 'new item is: ', new_item

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

    # DO NOT CALL THIS DIRECTLY FROM THIS CLASS!!!
    def __loadQuestionData__(self, index):
        print 'changing current question to: ', index
        # import pdb; pdb.set_trace()
        q = self.questions[index]

        self.ui.questionEdit.setPlainText(q.text)
        self.ui.tagsEdit.setText(' '.join(q.tag_names))
        self.ui.answersWidget.reset(q.answers)

    def clearQuestionData(self):
        self.ui.questionEdit.setPlainText('')
        self.ui.tagsEdit.setText('')
        self.ui.answersWidget.reset([])

    def getTags(self):
        tag_names = set()
        for question in self.questions:
            tag_names.update(set(question.tag_names))
        return [qtui.model.Tag(tag_name, 0) for tag_name in tag_names]

    def printStatus(self):
        print 'questions:', self.questions

    def dump(self):
        if 0 <= self.idsWidget.currentRow() < len(self.questions):
            self.saveQuestion(self.idsWidget.currentRow())
        return self.getTags(), self.questions
