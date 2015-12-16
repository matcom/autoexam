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
import exam_wizard
from os import mkdir, environ
from os.path import join, exists, abspath

import api
import model
import scanresults

DEFAULT_PROJECT_FILENAME = '.autoexam_project'
DEFAULT_PROJECT_PATH = join(environ['HOME'], 'autoexam_projects')
DEFAULT_PROJECT_FOLDER_NAME = 'Project %d'
DEFAULT_MASTER_FILENAME = 'master.txt'
DEFAULT_RESULTS_PATH = 'generated/last/results.json'

# Qt.QT_NO_DEBUG_OUTPUT = True


def src(path):
    return os.path.join(os.environ['AUTOEXAM_FOLDER'], path)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = uic.loadUi(src("qtui/ui/main_window.ui"), self)
        self.ui.clbNewExam.clicked.connect(self.newExam)
        self.ui.clbLoadExam.clicked.connect(self.loadExam)
        # self.ui.tabWidget.tabCloseRequested.connect(self.ui.tabWidget.removeTab)

        if exists('.autoexam'):
            self.loadExam(directory=os.getcwd())

    def setExistingDirectory(self):
        if not exists(DEFAULT_PROJECT_PATH):
            mkdir(DEFAULT_PROJECT_PATH)

        # TOFIX: directory always returns a string even on cancel.
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                "Select a project folder...", DEFAULT_PROJECT_PATH, options)
        return directory

    def startWizard(self, load=False):
        self.examWizard = exam_wizard.ExamWizard(self.project)
        self.examWizard.should_generate_master = True

        self.ui.stackedWidget.addWidget(self.examWizard)
        self.ui.stackedWidget.setCurrentIndex(1)

        # for i in range(self.project.current_page):
        #     self.examWizard.next()

        finish_button = self.examWizard.button(QWizard.FinishButton)
        finish_button.clicked.connect(self.returnToStartScreen)

        cancel_button = self.examWizard.button(QWizard.CancelButton)
        cancel_button.clicked.connect(self.returnToStartScreen)

    def returnToStartScreen(self):
        wizard = self.ui.stackedWidget.currentWidget()
        self.ui.stackedWidget.removeWidget(wizard)
        self.saveOnClose()

    def newExam(self):
        directory = str(self.setExistingDirectory())

        if directory:
            directory = abspath(directory)
            print(directory)

            project_count = 1

            while os.path.exists(join(directory, DEFAULT_PROJECT_FOLDER_NAME % project_count)):
                project_count += 1

            name = DEFAULT_PROJECT_FOLDER_NAME % project_count

            project_path = join(directory, name)

            # TODO: Fix project creation
            self.project = model.Project(name, 5, 1, [], [])
            self.project_path = join(project_path, DEFAULT_PROJECT_FILENAME)

            # Invoke Autoexam
            api.init(name, project_path)

            # Create base project file
            model.dump_project(self.project, '%s' % self.project_path)

            os.chdir(project_path)
            self.startWizard()

    def loadExam(self, directory=False):
        if directory is False:
            directory = str(self.setExistingDirectory())

        if directory:
            __project_file_path__ = join(directory, DEFAULT_PROJECT_FILENAME)
            if exists(__project_file_path__):
                self.project = model.load_project(__project_file_path__)
                self.project_path = __project_file_path__
            else:
                self.project = None
                master_filename = join(directory, DEFAULT_MASTER_FILENAME)
                if exists(master_filename):
                    print 'there is no project, but there is a master file that could be imported'
                    import gen
                    gen.parser(master_filename)
                    project = model.load_project_from_master(gen.questions_by_id, gen.restrictions)

                    self.project = project
                    self.project_path = __project_file_path__

                else:
                    msgBox = QMessageBox()
                    msgBox.setText("No project found in the given folder.")
                    msgBox.setModal(True)
                    msgBox.exec_()
                    return

            os.chdir(directory)
            self.startWizard(load=True)

    def closeEvent(self, event):
        # TODO: Place a close dialog?
        if self.saveOnClose():
            model.dump_project(self.project, self.project_path)
            try:
                # self.project.current_page = self.examWizard.currentId()
                scanresults.dump(self.examWizard.results, DEFAULT_RESULTS_PATH)
                print 'saved test results'
            except AttributeError:
                pass
                print 'no tests results to save'

            if event is not None:
                event.accept()

    def saveOnClose(self):
        try:
            return self.project is not None
        except:
            return False


def main():
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()

    win.show()  # Maximized
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
