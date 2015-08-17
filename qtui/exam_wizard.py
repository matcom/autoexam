from PyQt4.QtGui import QWizard, QWizardPage, QMessageBox
from PyQt4 import uic
from threading import Thread
import os
from os.path import join
import api

TEMPLATE_PATH = 'qtui/master.jinja'


class ExamWizard(QWizard):

    def __init__(self, project):
        super(ExamWizard, self).__init__()
        self.addPage(MasterPage(project))
        self.addPage(GeneratePage(project))
        self.addPage(ScanPage(project))
        self.addPage(ScoresPage(project))
        self.addPage(ResultsPage(project))


class MasterPage(QWizardPage):
    path = "qtui/ui/page1_master.ui"

    def __init__(self, project):
        super(MasterPage, self).__init__()
        self.ui = uic.loadUi( join(os.environ['AUTOEXAM_FOLDER'], self.path), self)
        self.project = project
        # self.ui.masterGenBtn.clicked.connect(self.gen_master)

    def validatePage(self):
        try:
            tags, questions = self.ui.widget.dump()

            self.project.tags = tags
            self.project.questions = questions

            api.validate_project(self.project)

            # TODO: Do at least one of the following:

            # 1. Set the project total_questions number before generating
            #    the master here (with a dialog or a modified ui)
            # 2. Get the total_questions number out of the master and into
            #    gen.py as a parameter (just like test_count)

            # Uncomment when one of the above is done.

            # master_data = api.render_master(self.project, TEMPLATE_PATH)
            # api.save_master(master_data)

            return True
        except Exception as e:
            self.diag = QMessageBox(QMessageBox.Warning, "Warning", str(e))
            self.diag.show()

            return False


class GeneratePage(QWizardPage):
    path = "qtui/ui/page2_generate.ui"

    def __init__(self, project):
        super(GeneratePage, self).__init__()
        self.ui = uic.loadUi( join(os.environ['AUTOEXAM_FOLDER'], self.path), self)
        self.project = project

        self.ui.generateBtn.clicked.connect(self.generate)

    def generate(self):
        # Both master and exam generation are being done here temporally
        self.project.total_questions = self.ui.questionCountSpin.value()

        print "Project.total_questions", self.project.total_questions

        master_data = api.render_master(self.project, join(os.environ['AUTOEXAM_FOLDER'], TEMPLATE_PATH))
        api.save_master(master_data)

        api.gen(**{"dont_shuffle_tags": not self.ui.randTagCheck.isChecked(),
                   "sort_questions": self.ui.sortQuestionCheck.isChecked(),
                   "dont_shuffle_options": not self.ui.randItemCheck.isChecked()
                   })


class ScanPage(QWizardPage):
    path = "qtui/ui/page3_scan.ui"

    def __init__(self, project):
        super(ScanPage, self).__init__()
        self.ui = uic.loadUi( join(os.environ['AUTOEXAM_FOLDER'], self.path), self)
        self.project = project
        self.scan_thread = None

    def initializePage(self):
        super(ScanPage, self).initializePage()
        api.add_scan_event_subscriber(self)

        self.scan_thread = Thread(target=self.start_scan)
        # self.scan_thread.setDaemon(True)
        self.scan_thread.start()

        # self.start_scan()


    def cleanupPage(self):
        super(ScanPage, self).cleanupPage()
        api.remove_scan_event_subscriber(self)

        # TODO: Do proper shutdown
        self.scan_thread.__stop()

    def on_scan_event(self, report):
        if report.success:
            print 'successful report: ', report
        else:
            print 'failed report: ', report

    def start_scan(self):

        class _args:
            outfile = None
            cameras = [1]
            folder = ""
            time = None
            autowrite = None
            poll = None
            debug = True

        api.scan(_args()) # TODO: Fill dictionary properly


class ScoresPage(QWizardPage):
    path = "qtui/ui/page4_scores.ui"

    def __init__(self, project):
        super(ScoresPage, self).__init__()
        self.ui = uic.loadUi( join(os.environ['AUTOEXAM_FOLDER'], self.path), self)
        self.project = project


class ResultsPage(QWizardPage):
    path = "qtui/ui/page5_results.ui"

    def __init__(self, project):
        super(ResultsPage, self).__init__()
        self.ui = uic.loadUi( join(os.environ['AUTOEXAM_FOLDER'], self.path), self)
        self.project = project
