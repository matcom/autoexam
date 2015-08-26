from PyQt4.QtGui import *
from PyQt4 import uic
import os
from os.path import join


class ResultsPage(QWizardPage):
    path = "qtui/ui/page5_results.ui"

    def __init__(self, project):
        super(ResultsPage, self).__init__()
        self.ui = uic.loadUi(join(os.environ['AUTOEXAM_FOLDER'], self.path), self)
        self.project = project
