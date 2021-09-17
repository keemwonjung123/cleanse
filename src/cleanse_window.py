# cleanse 3.0
# cleanse_window.py

import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from workers import LoginWorker, DeleteWorker
from cleaner import Cleaner
from info import CLEANSE_INFO


# cleanse window
class CleanseWindow(QMainWindow):
    # when instance created
    def __init__(self):
        # initial settings
        super(CleanseWindow, self).__init__()
        self.cleaner = Cleaner()
        self.thread_pool = QThreadPool()
        self.delete_worker = DeleteWorker(self.cleaner)
        # window settings
        self.setWindowTitle("Cleanse")
        self.setFixedSize(275, 245)
        self.setStyleSheet(open("./style.qss", "r").read())
        # id line edit
        self.id_line_edit = QLineEdit(self)
        self.id_line_edit.setGeometry(10, 6, 150, 24)
        self.id_line_edit.setPlaceholderText("User ID")
        # pw line edit
        self.pw_line_edit = QLineEdit(self)
        self.pw_line_edit.setGeometry(10, 35, 150, 24)
        self.pw_line_edit.setEchoMode(QLineEdit.Password)
        self.pw_line_edit.setPlaceholderText("password")
        # login button
        self.login_button = QPushButton("Login", self)
        self.login_button.setGeometry(165, 5, 100, 55)
        self.login_button.clicked.connect(self.login)
        # posting radio button
        self.posting_radio_button = QRadioButton('posts', self)
        self.posting_radio_button.setGeometry(10, 65, 60, 25)
        self.posting_radio_button.setChecked(True)
        self.posting_radio_button.setEnabled(False)
        # comment radio button
        self.comment_radio_button = QRadioButton('comts', self)
        self.comment_radio_button.setGeometry(80, 65, 80, 25)
        self.comment_radio_button.setEnabled(False)
        # top check box
        self.top_check_box = QCheckBox('always on top', self)
        self.top_check_box.setGeometry(10, 95, 150, 25)
        self.top_check_box.stateChanged.connect(self.top)
        # delete button
        self.delete_button = QPushButton("Delete", self)
        self.delete_button.setGeometry(165, 65, 100, 25)
        self.delete_button.clicked.connect(self.delete)
        self.delete_button.setEnabled(False)
        # stop button
        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setGeometry(165, 95, 100, 25)
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setEnabled(False)
        # progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(10, 125, 255, 110)
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setFormat('')
        # output label
        self.output_label = QLabel(CLEANSE_INFO, self)
        self.output_label.setGeometry(10, 125, 255, 110)
        self.output_label.setAlignment(Qt.AlignCenter)
        # enable using enter key to login
        self.id_line_edit.returnPressed.connect(self.login)
        self.pw_line_edit.returnPressed.connect(self.login)

    # enable/disables always on top feature
    def top(self):
        if self.top_check_box.isChecked():
            self.window().setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.window().setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    # Slots for signals

    # when set_enabled_by_login signal emitted by worker
    def set_enabled_by_login(self, logged_in):
        self.id_line_edit.setEnabled(not logged_in)
        self.pw_line_edit.setEnabled(not logged_in)
        self.login_button.setEnabled(not logged_in)

    # when set_enabled_by_delete signal emitted by worker
    def set_enabled_by_delete(self, deleting):
        self.posting_radio_button.setEnabled(not deleting)
        self.comment_radio_button.setEnabled(not deleting)
        self.delete_button.setEnabled(not deleting)
        self.stop_button.setEnabled(deleting)

    # when progressbar_set_value signal emitted by worker
    def progressbar_set_value(self, value):
        self.progress_bar.setValue(value)

    # when inform signal emitted by worker
    def inform(self, inform_data):
        signal_type = inform_data[0]
        signal = inform_data[1]
        if signal_type == 'warning':
            QMessageBox.warning(self, signal_type, signal)
        elif signal_type == 'information':
            QMessageBox.information(self, signal_type, signal)

    # when output signal emitted by worker
    def output(self, text):
        self.output_label.setText(text)

    # when login_button clicked
    def login(self):
        # create login worker & connect signals with funcs
        login_worker = LoginWorker(self.cleaner)
        login_worker.signals.set_enabled_by_login.connect(self.set_enabled_by_login)
        login_worker.signals.set_enabled_by_delete.connect(self.set_enabled_by_delete)
        login_worker.signals.output.connect(self.output)
        # set id and pw
        login_worker.user_id = self.id_line_edit.text()
        login_worker.user_pw = self.pw_line_edit.text()
        # start login thread
        self.thread_pool.start(login_worker)

    # when delete_button clicked
    def delete(self):
        # create delete worker & connect signals with funcs
        self.delete_worker = DeleteWorker(self.cleaner)
        self.delete_worker.signals.set_enabled_by_delete.connect(self.set_enabled_by_delete)
        self.delete_worker.signals.progressbar_set_value.connect(self.progressbar_set_value)
        self.delete_worker.signals.inform.connect(self.inform)
        self.delete_worker.signals.output.connect(self.output)
        # set post type
        post_types = ["comment", "posting"]
        self.delete_worker.post_type = post_types[self.posting_radio_button.isChecked()]
        # start delete thread
        self.thread_pool.start(self.delete_worker)

    # when stop_button pressed
    def stop(self):
        # set delete worker's working state False
        self.delete_worker.working = False
