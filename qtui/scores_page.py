from PyQt4.QtGui import *
from PyQt4 import uic
import os
from os.path import join


class ScoresPage(QWizardPage):
    path = "qtui/ui/page4_scores.ui"

    def __init__(self, project, parentW=None):
        super(ScoresPage, self).__init__()
        self.ui = uic.loadUi(join(os.environ['AUTOEXAM_FOLDER'], self.path), self)
        self.project = project
        self.parentWizard = parentW
