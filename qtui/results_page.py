from PyQt4.QtGui import *
from PyQt4 import uic
import os
from os.path import join
from evaluator import evaluate
import random
import csv

class ResultsPage(QWizardPage):
    path = "qtui/ui/page5_results.ui"

    def __init__(self, project, parentW=None):
        super(ResultsPage, self).__init__()
        self.ui = uic.loadUi(join(os.environ['AUTOEXAM_FOLDER'], self.path), self)
        self.project = project
        self.parentWizard = parentW

    def initializePage(self):
        super(ResultsPage, self).initializePage()

        self.results = self.parentWizard.results
        # TODO: Unwire this
        self.grades = evaluate('generated/last/grader.txt', 'tests_results.json')

        # This assumes scores are normalized to 1 (which is probably
        # a good idea anyway. Otherwise, the max score would depend
        # on the specific questions each exam got out of randomness)
        self.max_score = len(self.grades[0]['questions_grades'].keys())

        self.ui.treeWidget.clear()

        for test_num, test_data in self.results.items():
            # TODO: Make name editable
            name = random.choice(['Fulano', 'Mengano', 'Ciclano', 'Esperanzejo'])
            grade = self.grades[test_num]['total_grade']
            score = float(grade)/float(self.max_score) * 100  # TODO: implement scoring correctly
            item = QTreeWidgetItem([str(test_num), str(name), str(grade), str(score)])
            self.ui.treeWidget.addTopLevelItem(item)

    def validatePage(self):

        count = self.ui.treeWidget.topLevelItemCount()
        rows = []

        rows.append(['Temario', 'Nombre', 'Nota', 'Puntos'])

        for i in range(count):
            row = self.ui.treeWidget.topLevelItem(i)
            txtrow = [row.text(j) for j in range(row.columnCount())]
            rows.append(txtrow)

        with open('autoexam_output.csv', 'w') as csvfile:
            autowriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in rows:
                autowriter.writerow(row)

        print 'Saved csv to project folder'

        return True
