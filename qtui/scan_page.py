from PyQt4.QtGui import *
from PyQt4 import uic
from PyQt4.QtCore import QFileSystemWatcher, pyqtSignal
import os
from os.path import join
import api
import model
import scanresults

from threading import Thread

ok_color = QBrush(QColor(0, 128, 0))
warn_color = QBrush(QColor(128, 128, 0))

TESTS_RESULTS_FILE_PATH = 'generated/last/results.json'
ORDER_FILE_PATH = os.path.join('generated', 'last', 'order.json')
IMAGES_FOLDER = 'generated/last/images'

class ScanPage(QWizardPage):
    scanError = pyqtSignal() # name
    path = "qtui/ui/page3_scan.ui"

    def __init__(self, project, parentW=None):
        super(ScanPage, self).__init__()
        self.ui = uic.loadUi(join(os.environ['AUTOEXAM_FOLDER'], self.path), self)
        self.project = project
        self.scan_thread = None
        self.ui.treeWidget.currentItemChanged.connect(self.change_tree_item)
        self.question_item_to_question = {}

        self.exams = []
        self.order = None
        self.results = None
        self.parentWizard = parentW
        self.scanError.connect(self.go_to_previous)

    def initializePage(self):
        super(ScanPage, self).initializePage()
        # api.add_scan_event_subscriber(self)

        self.scan_thread = Thread(target=self.start_scan)
        self.scan_thread.setDaemon(True)
        self.scan_thread.start()
        # self.start_scan()

        if os.path.exists(ORDER_FILE_PATH):
            self.order = scanresults.parse(ORDER_FILE_PATH)


        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.on_scan_file_change)

        if os.path.exists(TESTS_RESULTS_FILE_PATH):
            self.results = scanresults.parse(TESTS_RESULTS_FILE_PATH)
            self.loadResults()
        else:
            with open(TESTS_RESULTS_FILE_PATH,'w') as f:
                f.write('{}')

        self.watcher.addPath(TESTS_RESULTS_FILE_PATH)

    def loadResults(self):
        tree = self.ui.treeWidget
        tree.clear()

        for i in range(self.project.total_exams_to_generate):
            exam_item = QTreeWidgetItem(tree, ['Exam %d' % (i + 1)])
            for j in range(self.project.total_questions_per_exam):
                question_item = QTreeWidgetItem(exam_item, ['Question %d' % (j + 1)])
                if i in self.results:
                    question_item.question = self.project.questions[self.results[i].questions[j].id - 1]

        first_exam_item = tree.topLevelItem(0)
        first_exam_item.setExpanded(True)
        tree.setCurrentItem(
            tree.itemBelow(first_exam_item))


    def validatePage(self):
        # TODO: Warning validation here!!!
        scanresults.dump(self.results, TESTS_RESULTS_FILE_PATH, overwrite=True)
        self.parentWizard.results = self.results
        return True

    def cleanupPage(self):
        super(ScanPage, self).cleanupPage()
        # api.remove_scan_event_subscriber(self)

        # TODO: Do proper shutdown
        # self.scan_thread.__stop()

    # def on_scan_event(self, report):
    #     if report.success:
    #         print 'successful report: ', report
    #         self.process_report(report)
    #     else:
    #         print 'failed report: ', report

    def on_scan_file_change(self, filename):
        print('Detected changes!!! ', filename)
        try:
            self.results = scanresults.parse(TESTS_RESULTS_FILE_PATH)
            self.loadResults()
        except:
            print('Could not load results.')

    def process_report(self, report):
        current = self.ui.treeWidget.topLevelItem(report.test.id)

        if current:
            if len(report.test.warnings) == 0:
                current.setForeground(0, ok_color)
            elif len(report.test.warnings) > 0:
                current.setForeground(0, warn_color)

    def change_tree_item(self):
        currentItem = self.ui.treeWidget.currentItem()
        if currentItem is not None:
            if currentItem.parent() is not None:  # If it is a question
                # print 'selected question'
                self.current_item = currentItem
                self.update_question_panel()
            else:
                pass
                # print 'selected exam'

    def update_question_panel(self):
        for i in reversed(range(self.ui.questionDataLayout.count())):
            elem = self.ui.questionDataLayout.itemAt(i)
            if not elem:
                break
            elem.widget().deleteLater()

        current_exam_item = self.current_item.parent()

        exam_no = self.ui.treeWidget.indexOfTopLevelItem(current_exam_item)
        question_no = current_exam_item.indexOfChild(self.current_item)

        if not 'question' in dir(self.current_item):
            question_text_label = QLabel('This exam has not been scanned yet.')
            self.ui.questionDataLayout.addWidget(question_text_label)
            return
        else:
            question_text_label = QLabel(self.current_item.question.text)
            self.ui.questionDataLayout.addWidget(question_text_label)

            for answer_no, answer in enumerate(self.current_item.question.answers):
                question_answer_check = QCheckBox(answer.text)
                question_answer_check.setChecked(self.is_answer_checked(exam_no, question_no, answer_no))

                question_answer_check.stateChanged.connect(self.update_current_question_state)
                self.ui.questionDataLayout.addWidget(question_answer_check)

    def is_answer_checked(self, exam_no, question_no, answer_no):
        # print 'is_answer_checked'
        # print(exam_no,question_no,answer_no)
        results_data = self.results
        exam_data = results_data[exam_no]

        question_data = exam_data.questions[question_no]
        return answer_no in question_data.answers

    def update_current_question_state(self, state):
        current_exam_item = self.current_item.parent()

        exam_no = self.ui.treeWidget.indexOfTopLevelItem(current_exam_item)
        question_no = current_exam_item.indexOfChild(self.current_item)

        results_data = self.results
        exam_data = results_data[exam_no]
        question_data = exam_data.questions[question_no]

        for i, answer in enumerate(self.current_item.question.answers):
            # i += 1
            checked = self.ui.questionDataLayout.itemAt(i + 1).widget().isChecked()
            if checked and i not in question_data.answers:
                question_data.answers.append(i)
            elif not checked and i in question_data.answers:
                question_data.answers.remove(i)

        assert len(question_data.answers) <= len(question_data.order)

    def cleanupPage(self):
        pass


    def start_scan(self):

        class _args:
            outfile = TESTS_RESULTS_FILE_PATH
            cameras = [self.parentWizard.camera_id] #TODO: UN-WIRE THIS !!!!
            folder = IMAGES_FOLDER
            time = None
            autowrite = True
            poll = None
            debug = False

        ok = api.scan(_args()) # TODO: Fill dictionary properly
        if not ok:
            self.scanError.emit()
        else:
            print 'All OK with the scanning!'

    def go_to_previous(self):
        self.parentWizard.back()
        msgBox = QMessageBox()
        msgBox.setText("There was an error in the scanning process. Please, check if the right camera is selected and try again.")
        msgBox.setModal(True)
        msgBox.exec_()
