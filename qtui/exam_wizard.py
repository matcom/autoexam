from PyQt4.QtGui import *
from master_page import MasterPage
from generate_page import GeneratePage
from scan_page import ScanPage
from scores_page import ScoresPage
from results_page import ResultsPage


class ExamWizard(QWizard):

    def __init__(self, project):
        super(ExamWizard, self).__init__()
        self.project = project
        self.addPage(MasterPage(project))
        self.addPage(GeneratePage(project))
        self.addPage(ScanPage(project))
        self.addPage(ScoresPage(project))
        self.addPage(ResultsPage(project))
