from PyQt4.QtGui import *
from PyQt4.QtCore import Qt
from PyQt4 import uic
import os
from os.path import join
from glob import glob
import api
from model import Tag
TEMPLATE_PATH = 'qtui/master.jinja'


class GeneratePage(QWizardPage):
    path = "qtui/ui/page2_generate.ui"

    def __init__(self, project, parentW=None):
        super(GeneratePage, self).__init__()
        self.ui = uic.loadUi(join(os.environ['AUTOEXAM_FOLDER'], self.path), self)
        self.project = project

        self.ui.questionCountSpin.setValue(self.project.total_questions_per_exam)
        self.ui.examCountSpin.setValue(self.project.total_exams_to_generate)

        self.ui.questionCountSpin.valueChanged.connect(self.updateProject)
        self.ui.examCountSpin.valueChanged.connect(self.updateProject)

        self.grid = self.ui.scrollAreaWidgetContents.layout()
        self.setupTagMenu()

        self.parentWizard = parentW

    def gridItemAt(self, r, c):
         self.grid.itemAtPosition(r, c).widget()

    def setupTagMenu(self):
        print 'tags:', self.project.tags
        if self.project.tags:
            tags = iter(self.project.tags)

            t1 = next(tags)
            self.gridItemAt(0, 0).setText(t1.name)
            self.gridItemAt(0, 2).setValue(t1.min_questions)

            for i, tag in enumerate(tags, 1):
                self.grid.addWidget(QLabel(tag.name), i, 0, Qt.AlignTop|Qt.AlignRight)
                self.grid.addWidget(QSpinBox(tag.min_questions), i, 2, Qt.AlignTop)

    def getTags(self):
        for i in range(self.grid.rows()-1):
            name = str(self.gridItemAt(i, 0).text())
            minq = self.gridItemAt(i, 2).value()
            yield Tag(name, minq)

    def generate(self):
        # Both master and exam generation are being done here temporally

        self.update_project()

        msgBox = QMessageBox()
        msgBox.setText("The master file will now be generated.")
        msgBox.setModal(True)
        msgBox.exec_()

        master_data = api.render_master(self.project, join(os.environ['AUTOEXAM_FOLDER'], TEMPLATE_PATH))
        api.save_master(master_data)

        api.gen(**{"tests_count": self.project.total_exams_to_generate,
                   "dont_shuffle_tags": not self.ui.randTagCheck.isChecked(),
                   "sort_questions": self.ui.sortQuestionCheck.isChecked(),
                   "dont_shuffle_options": not self.ui.randItemCheck.isChecked()
                   })

        msgBox = QMessageBox()
        msgBox.setText("The exam has been successfully generated.")
        msgBox.setModal(True)
        msgBox.exec_()

        self.parentWizard.should_regenerate_master = False

    def updateProject(self):
        self.project.total_questions_per_exam = self.ui.questionCountSpin.value()
        self.project.total_exams_to_generate = self.ui.examCountSpin.value()
        self.project.tags = {tag for tag in self.getTags()}


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = GeneratePage()
    win.show()
    sys.exit(app.exec_())
