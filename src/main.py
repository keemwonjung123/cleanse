import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from cleaner import Cleaner
from text import CLEANSE_INFO, LINE_STYLE, LOGIN_STYLE, PUSH_STYLE, PROGRESSBAR_STYLE, LABEL_STYLE


class Login(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
    
    def run(self):
        user_id = self.parent.id_text.text()
        pw = self.parent.pw_text.text()
        self.parent.cleaner.login(user_id, pw)


class Delete(QThread):
    def __init__(self, parent, post_type):
        super().__init__(parent)
        self.parent = parent
        self.post_type = post_type

    def run(self):
        res = self.parent.cleaner.delete_posts(self.post_type)

        if res == 'BLOCKED':
            self.parent.sig_type = 'warning'
            self.parent.sig = ("Warning", "에러가 발생하였습니다.\n프로그램을 종료한 뒤 다시 실행해주세요.")
            self.parent.signal.run()

        elif res == 'CAPTCHA':
            self.parent.sig_type = 'warning'
            self.parent.sig = ("Warning", "CAPTCHA가 감지되었습니다.\n직접 글/댓글을 하나 삭제하여\nCAPTCHA를 해결한 뒤 다시 실행해주세요.")
            self.parent.signal.run()

        else:
            self.parent.sig_type = 'information'
            self.parent.sig = ("Info", "삭제가 완료되었습니다.")
            self.parent.signal.run()


class Signal(QObject):
    sig = pyqtSignal()

    def run(self):
        self.sig.emit()


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.cleaner = Cleaner(self)
        
        self.setWindowIcon(QIcon('D:/cleanse/icon.jpg'))
        self.setWindowTitle("Cleanse")
        self.setStyleSheet("background-color: white;")
        self.setFixedSize(275, 245)

        self.sig_type = None
        self.sig = ('', '')
        self.signal = Signal()
        self.signal.sig.connect(self.inform)

        self.id_text = QLineEdit(self)
        self.id_text.setGeometry(10, 6, 150, 24)
        self.id_text.setStyleSheet(LINE_STYLE)
        self.pw_text = QLineEdit(self)
        self.pw_text.setGeometry(10, 35, 150, 24)
        self.pw_text.setStyleSheet(LINE_STYLE)
        self.pw_text.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("Login", self)
        login_btn.setGeometry(165, 5, 100, 55)
        login_btn.setStyleSheet(LOGIN_STYLE)
        login_btn.clicked.connect(self.login)

        self.posting_chk = QRadioButton('posts', self)
        self.posting_chk.setGeometry(10, 65, 60, 25)
        self.posting_chk.setChecked(True)

        self.comment_chk = QRadioButton('comts', self)
        self.comment_chk.setGeometry(80, 65, 80, 25)

        self.top_chk = QCheckBox('always on top', self)
        self.top_chk.setGeometry(10, 95, 150, 25)
        self.top_chk.stateChanged.connect(self.top)

        delete_btn = QPushButton("Delete", self)
        delete_btn.setGeometry(165, 65, 100, 25)
        delete_btn.setStyleSheet(PUSH_STYLE)
        delete_btn.clicked.connect(self.delete)

        stop_btn = QPushButton("Stop", self)
        stop_btn.setGeometry(165, 95, 100, 25)
        stop_btn.setStyleSheet(PUSH_STYLE)
        stop_btn.clicked.connect(self.stop)

        self.progressbar = QProgressBar(self)
        self.progressbar.setGeometry(10, 125, 255, 110)
        self.progressbar.setStyleSheet(PROGRESSBAR_STYLE)
        self.progressbar.setValue(0)
        self.progressbar.setAlignment(Qt.AlignCenter)
        self.progressbar.setFormat('')

        self.info = QLabel(CLEANSE_INFO, self)
        self.info.setGeometry(10, 125, 255, 110)
        self.info.setStyleSheet(LABEL_STYLE)
        self.info.setAlignment(Qt.AlignCenter)

    def output(self, _str):
        self.info.setText(_str)

    def login(self):
        self.stop()
        self.thread = Login(self)
        self.thread.start()
    
    def top(self):
        if self.top_chk.isChecked():
            self.window().setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.window().setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def delete(self):
        self.stop()
        if self.posting_chk.isChecked():
            post_type = 'posting'
        else:
            post_type = 'comment'
        self.thread = Delete(self, post_type)
        self.thread.start()

    def stop(self):
        if self.thread is not None:
            self.thread.quit()
            self.thread = None
            self.progressbar.setValue(0)
        self.output(CLEANSE_INFO)
    
    def inform(self):
        if self.sig_type == 'warning':
            QMessageBox.warning(self, self.sig[0], self.sig[1])
            self.stop()
        elif self.sig_type == 'information':
            QMessageBox.information(self, self.sig[0], self.sig[1])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_window = MyWindow()
    my_window.show()
    app.exec_()
