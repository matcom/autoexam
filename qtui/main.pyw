#!/usr/bin/python3
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
from exam_wizard import ExamWizard
from os import mkdir
from os import system as run
from os.path import join

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = uic.loadUi("./ui/main_window.ui", self)
        self.ui.clbNewExam.clicked.connect(self.newExam)
        self.ui.clbLoadExam.clicked.connect(self.loadExam)
        self.ui.tabWidget.tabCloseRequested.connect(self.ui.tabWidget.removeTab)

        self.project_count = 0

    def setExistingDirectory(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                "QFileDialog.getExistingDirectory()", "~", options)
        return directory


    def newExam(self):
        directory = str(self.setExistingDirectory())
        if directory:

            # Logic + UI
            self.project_count += 1
            name = 'Project %d' % self.project_count
            page = ExamWizard(directory + '/' + name)

            # Invoke Autoexam
            run('autoexam init -f "{0}" "{1}"'.format(join(directory, name), name))


            # UI-only stuff
            self.ui.tabWidget.addTab(page, name)
            self.ui.tabWidget.setCurrentWidget(page)
            finish_button = page.button(QWizard.FinishButton)
            finish_button.clicked.connect(lambda: self.ui.tabWidget.removeTab(self.ui.tabWidget.currentIndex()))




    def loadExam(self):
        pass

    def function(self):
        pass

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()#Maximized
    sys.exit(app.exec_())
