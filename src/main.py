import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from worker import LoginWorker, DeleteWorker
from cleaner import Cleaner
from info import CLEANSE_INFO


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.cleaner = Cleaner()
        self.login_worker = LoginWorker(self)
        self.delete_worker = DeleteWorker(self)

        self.setWindowIcon(QIcon(sys.path[0] + "/../img/icon.jpg"))
        self.setWindowTitle("Cleanse")
        self.setFixedSize(275, 245)
        self.setStyleSheet(open("style.qss", "r").read())

        self.id_text = QLineEdit(self)
        self.id_text.setGeometry(10, 6, 150, 24)
        self.pw_text = QLineEdit(self)
        self.pw_text.setGeometry(10, 35, 150, 24)
        self.pw_text.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton("Login", self)
        self.login_btn.setGeometry(165, 5, 100, 55)
        self.login_btn.clicked.connect(self.login)

        self.posting_chk = QRadioButton('posts', self)
        self.posting_chk.setGeometry(10, 65, 60, 25)
        self.posting_chk.setChecked(True)

        self.comment_chk = QRadioButton('comts', self)
        self.comment_chk.setGeometry(80, 65, 80, 25)

        self.top_chk = QCheckBox('always on top', self)
        self.top_chk.setGeometry(10, 95, 150, 25)
        self.top_chk.stateChanged.connect(self.top)

        self.delete_btn = QPushButton("Delete", self)
        self.delete_btn.setGeometry(165, 65, 100, 25)
        self.delete_btn.clicked.connect(self.delete)

        self.stop_btn = QPushButton("Stop", self)
        self.stop_btn.setGeometry(165, 95, 100, 25)
        self.stop_btn.clicked.connect(self.stop)

        self.progressbar = QProgressBar(self)
        self.progressbar.setGeometry(10, 125, 255, 110)
        self.progressbar.setValue(0)
        self.progressbar.setAlignment(Qt.AlignCenter)
        self.progressbar.setFormat('')

        self.info = QLabel(CLEANSE_INFO, self)
        self.info.setGeometry(10, 125, 255, 110)
        self.info.setAlignment(Qt.AlignCenter)

        self.set_enabled_by_delete(True)
        self.stop_btn.setEnabled(False)

    def output(self, _str):
        self.info.setText(_str)

    def top(self):
        if self.top_chk.isChecked():
            self.window().setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.window().setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def login(self):
        self.login_btn.setEnabled(False)
        self.login_worker.start()

    def stop(self):
        self.delete_worker.working = False
        self.delete_worker = DeleteWorker(self)

    def delete(self):
        self.set_enabled_by_delete(True)
        self.delete_worker.working = True
        self.delete_worker.start()

    def inform(self, signal_type, signal):
        if signal_type == 'warning':
            QMessageBox.warning(self, signal_type, signal)
            self.stop()
        elif signal_type == 'information':
            QMessageBox.information(self, signal_type, signal)

    def set_enabled_by_login(self, logged_in):
        self.id_text.setEnabled(not logged_in)
        self.pw_text.setEnabled(not logged_in)
        self.login_btn.setEnabled(not logged_in)

    def set_enabled_by_delete(self, deleting):
        self.posting_chk.setEnabled(not deleting)
        self.comment_chk.setEnabled(not deleting)
        self.delete_btn.setEnabled(not deleting)
        self.stop_btn.setEnabled(deleting)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_window = MyWindow()
    my_window.show()
    app.exec_()
