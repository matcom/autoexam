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

        self.parentWizard = parentW

    def gridItemAt(self, r, c):
         self.grid.itemAtPosition(r, c).widget()

    def listGrid(self):
        for i in range(self.grid.count()):
            item = self.grid.itemAt(i)
            # print i, type(item.widget() if item.widget() else item).__name__

    def clearGrid(self):
        widget = QWidget()
        layout = QGridLayout()
        widget.setLayout(layout)
        self.ui.scrollArea.widget().destroy()
        self.ui.scrollArea.setWidget(widget)
        self.grid = layout

    def setupTagMenu(self):
        self.clearGrid()
        for i, tag in enumerate(self.project.tags):
            self.grid.addWidget(QLabel(tag.name), i, 0, Qt.AlignTop|Qt.AlignRight)
            spinbox = QSpinBox()
            spinbox.setValue(tag.min_questions)
            self.grid.addWidget(spinbox, i, 2, Qt.AlignTop)

        hs = QSpacerItem(40, 20, hPolicy=QSizePolicy.Fixed)
        self.grid.addItem(hs, 0, 1)

        vs1 = QSpacerItem(20, 300, vPolicy=QSizePolicy.Expanding)
        vs2 = QSpacerItem(20, 300, vPolicy=QSizePolicy.Expanding)
        vs3 = QSpacerItem(20, 300, vPolicy=QSizePolicy.Expanding)
        pos = len(self.project.tags)
        self.grid.addItem(vs1, pos, 0)
        self.grid.addItem(vs2, pos, 1)
        self.grid.addItem(vs3, pos, 2)

    def updateTags(self):
        self.listGrid()
        tags = []
        for i in xrange(len(self.project.tags)):
            name = str(self.grid.itemAt(2*i).widget().text())
            minq = self.grid.itemAt(2*i+1).widget().value()
            tags.append(Tag(name, minq))
        self.project.tags = tags

    def initializePage(self):
        self.setupTagMenu()

    def validatePage(self):
        if self.parentWizard.should_generate_master:
            self.generate()
            self.parentWizard.should_generate_master = False
        self.parentWizard.camera_id = self.ui.cameraSourceCombo.currentIndex()
        return True

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
        self.updateTags()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = GeneratePage()
    win.show()
    sys.exit(app.exec_())
