from PyQt4.QtGui import *
from PyQt4 import uic
import os
from os.path import join
import api
import model

#TODO: Save current question on close


class MasterPage(QWizardPage):
    path = "qtui/ui/page1_master.ui"

    def __init__(self, project, parentW=None):
        super(MasterPage, self).__init__()
        self.ui = uic.loadUi(join(os.environ['AUTOEXAM_FOLDER'], self.path), self)
        self.project = project
        self.ui.questionWidget.initializeProject(project)
        # self.ui.masterGenBtn.clicked.connect(self.gen_master)
        self.parentWizard = parentW

    def validatePage(self):
        try:
            tags, questions = self.ui.questionWidget.dump()

            for tag in tags:
                if tag not in list(map(lambda tag: tag.name, self.project.tags)):
                    # import pdb; pdb.set_trace()
                    self.project.tags.append(model.Tag(tag,0))

            # self.project.tags = tags
            self.project.questions = questions

            api.validate_project(self.project)

            # TODO: Do at least one of the following:

            # 1. Set the project total_questions_per_exam number before generating
            #    the master here (with a dialog or a modified ui)
            # 2. Get the total_questions_per_exam number out of the master and into
            #    gen.py as a parameter (just like test_count)

            # Uncomment when one of the above is done.

            # master_data = api.render_master(self.project, TEMPLATE_PATH)
            # api.save_master(master_data)

            return True
        except Exception as e:
            self.diag = QMessageBox(QMessageBox.Warning, "Warning", str(e))
            self.diag.show()

            return False
