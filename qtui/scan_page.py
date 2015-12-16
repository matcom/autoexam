from PyQt4.QtGui import *
from PyQt4 import uic
from PyQt4.QtCore import QFileSystemWatcher, pyqtSignal, Qt
import os
from os.path import join
import time
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
    scanSuccess = pyqtSignal()
    path = "qtui/ui/page3_scan.ui"

    def __init__(self, project, parentW=None):
        super(ScanPage, self).__init__()
        self.ui = uic.loadUi(join(os.environ['AUTOEXAM_FOLDER'], self.path), self)
        self.project = project
        self.scan_thread = None
        self.ui.treeWidget.currentItemChanged.connect(self.change_tree_item)
        self.ui.openCameraButton.clicked.connect(self.open_camera)
        self.question_item_to_question = {}

        self.exams = []
        self.order = None
        self.results = None
        self.parentWizard = parentW
        self.scanError.connect(self.on_scan_error)
        self.scanSuccess.connect(self.on_scan_success)
        self.scanning = False

    def initializePage(self):
        super(ScanPage, self).initializePage()
        # api.add_scan_event_subscriber(self)

        self.open_camera()

        if os.path.exists(ORDER_FILE_PATH):
            self.order = scanresults.parse(ORDER_FILE_PATH)

        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.on_scan_file_change)

        if os.path.exists(TESTS_RESULTS_FILE_PATH):
            self.results = scanresults.parse(TESTS_RESULTS_FILE_PATH)
            self.update_question_tree_widget()
        else:
            with open(TESTS_RESULTS_FILE_PATH,'w') as f:
                f.write('{}')

        # TODO: Check why this doesn't always work
        self.watcher.addPath(TESTS_RESULTS_FILE_PATH)
        self.last_load_time = time.time()

    def update_question_tree_widget(self):
        tree = self.ui.treeWidget
        tree.clear()

        for i in range(len(self.order)):
            incomplete_test = False
            exam_item = QTreeWidgetItem(tree, ['Exam %d' % i])
            for j in range(len(self.order[i].questions)):
                question_item = QTreeWidgetItem(exam_item, ['Question %d' % (j + 1)])
                if i in self.results:
                    question_item.question = self.project.questions[self.order[i].questions[j].id - 1]
                else:
                    incomplete_test = True
            if incomplete_test:
                exam_item.setBackground(0, QBrush(Qt.lightGray))

        first_exam_item = tree.topLevelItem(0)
        first_exam_item.setExpanded(True)
        tree.setCurrentItem(
            tree.itemBelow(first_exam_item))


    def validatePage(self):

        if self.scanning:
            self.show_modal_message(
            'Please close the scanner window first by pressing \'q\'')
            return False
        # TODO: Warning validation here!!!
        if self.results is not None:
            scanresults.dump(self.results, TESTS_RESULTS_FILE_PATH, overwrite=False)
            self.parentWizard.results = self.results
            return True
        else:
            self.show_modal_message('There are still no results to save')
            return False

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
        if time.time() - self.last_load_time > 2:
            try:
                print('Reloading results...')
                self.results = scanresults.parse(TESTS_RESULTS_FILE_PATH)
                self.update_question_tree_widget()
                self.last_load_time = time.time()
                print('Results reloaded')
            except:
                print('Could not load results.')
        else:
            # print('Ignoring repetitive filewatcher event (this is normal)')
            pass


    # def process_report(self, report):
    #     current = self.ui.treeWidget.topLevelItem(report.test.id)
    #
    #     if current:
    #         if len(report.test.warnings) == 0:
    #             current.setForeground(0, ok_color)
    #         elif len(report.test.warnings) > 0:
    #             current.setForeground(0, warn_color)

    def change_tree_item(self):
        currentItem = self.ui.treeWidget.currentItem()
        if currentItem is not None:
            self.cleanupPanel()
            self.current_item = currentItem
            if currentItem.parent() is not None:  # i.e. it is a question
                self.update_question_panel_with_question()
            else:
                self.update_question_panel_with_exam()

    def update_question_panel_with_question(self):
        current_exam_item = self.current_item.parent()
        exam_no = self.ui.treeWidget.indexOfTopLevelItem(current_exam_item)
        question_no = current_exam_item.indexOfChild(self.current_item)
        question_info = self.project.questions[self.order[exam_no].questions[question_no].id - 1]

        self.ui.questionDataLayout.addWidget(QLabel(question_info.text))

        order_info = self.order[exam_no].questions[question_no].order

        for answer_no in order_info:
            answer = question_info.answers[answer_no]
            answer_text = answer.text
            answer_text += ' (x)' if answer.valid else ''
            question_answer_check = QCheckBox(answer_text)
            question_answer_check.setChecked(
                self.is_answer_checked(exam_no, question_no, answer_no))
            question_answer_check.stateChanged.connect(
                self.update_current_question_state)
            self.ui.questionDataLayout.addWidget(question_answer_check)

    def update_question_panel_with_exam(self):
        current_exam_item = self.current_item
        exam_no = self.ui.treeWidget.indexOfTopLevelItem(current_exam_item)

        if exam_no in self.results:
            question_text_label = QLabel('TODO: Put here the warnings...')
        else:
            question_text_label = QLabel('This exam has not been scanned!')

        self.ui.questionDataLayout.addWidget(question_text_label)

    def is_answer_checked(self, exam_no, question_no, answer_no):
        # print 'is_answer_checked'
        # print(exam_no,question_no,answer_no)

        try:
            results_data = self.results
            exam_data = results_data[exam_no]

            question_data = exam_data.questions[question_no]
            return answer_no in question_data.answers
        except:
            # print('answer not scanned exception')
            return False

    def update_current_question_state(self, state):
        current_exam_item = self.current_item.parent()

        exam_no = self.ui.treeWidget.indexOfTopLevelItem(current_exam_item)
        question_no = current_exam_item.indexOfChild(self.current_item)

        results_data = self.results

        if exam_no in results_data:
            question_data = results_data[exam_no].questions[question_no]

            order_data = self.order[exam_no].questions[question_no].order
            self.synchronize_answers_with_model(order_data,question_data)

        else:
            # If we get here, we're trying to manually enter info for an
            # exam that has not been scanned yet.
            # We should create an entry in results_data similar
            confirm_edit = QMessageBox.question(None, "Manual input?", "Do you want to manually enter this test's results?", QMessageBox.Yes | QMessageBox.No )
            regen = confirm_edit == QMessageBox.Yes
            if confirm_edit:
                self.results[exam_no] = self.order[exam_no]
                question_data = results_data[exam_no].questions[question_no]
                order_data = self.order[exam_no].questions[question_no].order
                self.synchronize_answers_with_model(order_data,question_data)

                current_exam_item.setBackground(0, QBrush(Qt.white))

    def synchronize_answers_with_model(self, order_data, question_data):
        for i in range(len(order_data)):
            checked = self.ui.questionDataLayout.itemAt(i + 1).widget().isChecked()
            question_idx = order_data[i]
            if checked and question_idx not in question_data.answers:
                question_data.answers.append(question_idx)
            elif not checked and question_idx in question_data.answers:
                question_data.answers.remove(question_idx)

    def cleanupPage(self):
        self.watcher.fileChanged.disconnect(self.on_scan_file_change)
        del self.watcher

    def cleanupPanel(self):
        for i in reversed(range(self.ui.questionDataLayout.count())):
            elem = self.ui.questionDataLayout.itemAt(i)
            if not elem:
                break
            elem.widget().deleteLater()

    def start_scan(self):

        class _args:
            outfile = TESTS_RESULTS_FILE_PATH
            cameras = [self.ui.cameraIndexSpin.value()] #TODO: UN-WIRE THIS !!!!
            folder = IMAGES_FOLDER
            time = None
            autowrite = True
            poll = None
            debug = False

        self.scanning = True

        ok = api.scan(_args()) # TODO: Fill dictionary properly
        if ok:
            self.scanSuccess.emit()
        else:
            self.scanError.emit()

        self.scanning = False

    def open_camera(self):
        self.ui.openCameraButton.setEnabled(False)

        self.scan_thread = Thread(target=self.start_scan)
        self.scan_thread.setDaemon(True)
        self.scan_thread.start()
        # self.start_scan()

    def on_scan_error(self):
        # self.parentWizard.back()
        self.show_modal_message(
        "There was an error in the scanning process.\
        Please, check if the right camera is selected and try again.")
        self.ui.openCameraButton.setEnabled(True)

    def show_modal_message(self, msg):
        """
        Shows a modal MessageBox displaying the argument string
        """
        msgBox = QMessageBox()
        msgBox.setText(msg)
        msgBox.setModal(True)
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.exec_()

    def on_scan_success(self):
        """
        Reloads results one last time in case the filewatcher doesn't work
        """

        # Do another dump first to store manually entered results
        scanresults.dump(self.results, TESTS_RESULTS_FILE_PATH)

        # Reload merged results
        self.results = scanresults.parse(TESTS_RESULTS_FILE_PATH)

        # Update UI
        self.update_question_tree_widget()

        # Reenable the button in case someone needs to scan again
        self.ui.openCameraButton.setEnabled(True)

        # Msg for debugging purposes
        print 'All OK with the scanning!'
