from PyQt4.QtGui import *
from PyQt4 import uic
import os
from os.path import join
from glob import glob
import api

TEMPLATE_PATH = 'qtui/master.jinja'


class GeneratePage(QWizardPage):
    path = "qtui/ui/page2_generate.ui"

    def __init__(self, project):
        super(GeneratePage, self).__init__()
        self.ui = uic.loadUi(join(os.environ['AUTOEXAM_FOLDER'], self.path), self)
        self.project = project

        self.ui.questionCountSpin.setValue(self.project.total_questions_per_exam)
        self.ui.examCountSpin.setValue(self.project.total_exams_to_generate)

        self.ui.generateBtn.clicked.connect(self.generate)
        self.ui.questionCountSpin.valueChanged.connect(self.update_project)
        self.ui.examCountSpin.valueChanged.connect(self.update_project)

    def generate(self):
        # Both master and exam generation are being done here temporally

        master_data = api.render_master(self.project, join(os.environ['AUTOEXAM_FOLDER'], TEMPLATE_PATH))
        api.save_master(master_data)

        api.gen(**{"tests_count": self.project.total_exams_to_generate,
                   "dont_shuffle_tags": not self.ui.randTagCheck.isChecked(),
                   "sort_questions": self.ui.sortQuestionCheck.isChecked(),
                   "dont_shuffle_options": not self.ui.randItemCheck.isChecked()
                   })

        # TODO: Remove this when scanning is working
        print 'cwd', os.getcwd()
        dst_image_dir = os.path.join('generated', 'last', 'images')
        if not os.path.exists(dst_image_dir):
            os.mkdir(dst_image_dir)
            print 'created images directory'
        file_list = glob('generated/last/pdf/Answer*')
        for i, filename in enumerate(file_list):
            os.system('pdftocairo -jpeg {filename} {dst_image_dir}/{i}-scan'
                .format(filename=filename, dst_image_dir=dst_image_dir, i=i))

        msgBox = QMessageBox()
        msgBox.setText("The exam has been successfully generated.")
        msgBox.setModal(True)
        msgBox.exec_()

    def update_project(self):
        self.project.total_questions_per_exam = self.ui.questionCountSpin.value()
        self.project.total_exams_to_generate = self.ui.examCountSpin.value()
