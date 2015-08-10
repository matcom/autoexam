from PyQt4.QtGui import QWizard, QWizardPage, QMessageBox
from PyQt4 import uic
import api, jinja2

TEMPLATE_PATH = 'master.jinja'

class ExamWizard(QWizard):

    def __init__(self, project):
        super(ExamWizard, self).__init__()
        self.addPage(MasterPage(project))
        self.addPage(GeneratePage(project))
        self.addPage(ScanPage(project))
        self.addPage(ScoresPage(project))
        self.addPage(ResultsPage(project))

class MasterPage(QWizardPage):
    path = "./ui/page1_master.ui"

    def __init__(self, project):
        super(MasterPage, self).__init__()
        self.ui = uic.loadUi(self.path, self)
        self.project = project
        # self.ui.masterGenBtn.clicked.connect(self.gen_master)

    def validatePage(self):
        try:
            tags, questions = self.ui.widget.dump()
            
            self.project.tags = tags
            self.project.questions = questions

            master = jinja2.Template(open(TEMPLATE_PATH).read().decode('utf-8'))

            for question in self.project.questions:
                if not question.tag_names:
                    # TODO: Tr (translator)
                    raise Exception("Debe haber al menos una etiqueta por pregunta")

            master_data = master.render(project = self.project)

            api.save_master(master_data)

            return True
        
        except Exception as e:
            
            self.diag = QMessageBox(QMessageBox.Warning, "Warning", str(e))
            self.diag.show()

            return False


    # def gen_master(self):
    #     master = jinja2.Template(open(TEMPLATE_PATH).read().decode('utf-8'))
    #     master_data = master.render(project = self.project)
    #     print master_data


class GeneratePage(QWizardPage):
    path = "./ui/page2_generate.ui"
    
    def __init__(self, project):
        super(GeneratePage, self).__init__()
        self.ui = uic.loadUi(self.path, self)
        self.project = project

        self.ui.generateBtn.clicked.connect(self.generate)

    def generate(self):
        api.gen(**{   "dont_shuffle_tags" : not self.ui.randTagCheck.isChecked(),
                    "sort_questions" : self.ui.sortQuestionCheck.isChecked(),
                    "dont_shuffle_options" : not self.ui.randItemCheck.isChecked()
                })

class ScanPage(QWizardPage):
    path = "./ui/page3_scan.ui"
    
    def __init__(self, project):
        super(ScanPage, self).__init__()
        self.ui = uic.loadUi(self.path, self)
        self.project = project

class ScoresPage(QWizardPage):
    path = "./ui/page4_scores.ui"
    
    def __init__(self, project):
        super(ScoresPage, self).__init__()
        self.ui = uic.loadUi(self.path, self)
        self.project = project

class ResultsPage(QWizardPage):
    path = "./ui/page5_results.ui"
    
    def __init__(self, project):
        super(ResultsPage, self).__init__()
        self.ui = uic.loadUi(self.path, self)
        self.project = project
        