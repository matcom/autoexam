from PyQt4.QtGui import QWizard, QWizardPage
from PyQt4 import uic


class ExamWizard(QWizard):

    def __init__(self, path):
        super(ExamWizard, self).__init__()
        self.loadPage("./ui/page1_master.ui")
        self.loadPage("./ui/page2_generate.ui")
        self.loadPage("./ui/page3_scan.ui")
        self.loadPage("./ui/page4_scores.ui")
        self.loadPage("./ui/page5_results.ui")
        self.path = path

    def loadPage(self, path):
        page = QWizardPage()
        page.ui = uic.loadUi(path, page)
        self.addPage(page)
