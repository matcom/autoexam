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
        self.order = None # TODO: Implement order loading here?
        self.results = None # TODO: Implement result loading here?
        self.setOption(QWizard.IndependentPages, False)
        self.addPage(MasterPage(project, self))
        self.addPage(GeneratePage(project, self))
        self.addPage(ScanPage(project, self))
        # self.addPage(ScoresPage(project, self))
        self.addPage(ResultsPage(project, self))
