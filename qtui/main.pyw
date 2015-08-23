#!/usr/bin/env python

import sys
import os

if 'AUTOEXAM_FOLDER' not in os.environ:
    os.environ['AUTOEXAM_FOLDER'] = os.path.dirname(
        os.path.dirname(os.path.realpath(__file__)))
    sys.path.append(os.environ['AUTOEXAM_FOLDER'])

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
from exam_wizard import ExamWizard
from os import mkdir, environ
from os.path import join, exists, abspath
import api
import model

DEFAULT_PROJECT_FILENAME = '.autoexam_project'
DEFAULT_PROJECT_PATH = join(environ['HOME'], 'autoexam_projects')
DEFAULT_PROJECT_FOLDER_NAME = 'Project %d'


def src(path):
    return os.path.join(os.environ['AUTOEXAM_FOLDER'], path)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = uic.loadUi(src("qtui/ui/main_window.ui"), self)
        self.ui.clbNewExam.clicked.connect(self.newExam)
        self.ui.clbLoadExam.clicked.connect(self.loadExam)
        self.ui.tabWidget.tabCloseRequested.connect(self.ui.tabWidget.removeTab)

    def setExistingDirectory(self):
        if not exists(DEFAULT_PROJECT_PATH):
            mkdir(DEFAULT_PROJECT_PATH)

        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                "Project", DEFAULT_PROJECT_PATH, options)
        return directory

    def startWizard(self):
        page = ExamWizard(self.project)

        name = self.project.name

        self.ui.tabWidget.addTab(page, name)
        self.ui.tabWidget.setCurrentWidget(page)

        finish_button = page.button(QWizard.FinishButton)
        finish_button.clicked.connect(lambda: self.ui.tabWidget.removeTab(self.ui.tabWidget.currentIndex()))

    def newExam(self):
        directory = abspath(str(self.setExistingDirectory()))
        if directory:
            # Logic + UI

            project_count = 1

            while exists(join(directory, DEFAULT_PROJECT_FOLDER_NAME % project_count)):
                project_count += 1

            name = DEFAULT_PROJECT_FOLDER_NAME % project_count

            __project_path__ = join(directory, name)

            # TODO: Fix project creation
            self.project = Project(name, 0, [], [])

            # Invoke Autoexam
            api.init(name, __project_path__)

            model.dump_project(self.project, '%s' % join(__project_path__, DEFAULT_PROJECT_FILENAME))

            os.chdir(__project_path__)
            self.startWizard()

    def loadExam(self):
        directory = str(self.setExistingDirectory())

        if directory:
            __project_file_path__ = join(directory, DEFAULT_PROJECT_FILENAME)
            if not exists(__project_file_path__):
                self.project = None
                print("No project found!!")
                # TODO: QDialog
                return
            else:
                self.project = model.load_project(__project_file_path__)

            os.chdir(directory)
            self.startWizard()


def getProject():
    t1 = Tag('t1', 3)
    a1 = Answer(True, False, 'anstxt')
    q1 = Question('a', ['t1'], 'qtxt', [a1, a1])
    p1 = Project('p1', 2, [t1], [q1, q1])
    return p1

def main():
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()

    win.show()  # Maximized
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
