# cleanse 3.0
# workers.py

import time
from PyQt5.QtCore import *


# translate seconds into string
def get_time(seconds):
    h = str(int(seconds / 3600))
    m = str(int((seconds % 3600) / 60))
    s = str(int(seconds % 60))
    return f"{h}h {m}m {s}s"


# worker signals
class WorkerSignals(QObject):
    set_enabled_by_login = pyqtSignal(bool)
    set_enabled_by_delete = pyqtSignal(bool)
    progressbar_set_value = pyqtSignal(float)
    inform = pyqtSignal(tuple)
    output = pyqtSignal(object)


# login worker
class LoginWorker(QRunnable):
    # when instance created
    def __init__(self, cleaner):
        # initial settings
        super(LoginWorker, self).__init__()
        self.cleaner = cleaner
        self.signals = WorkerSignals()
        self.user_id = ""
        self.user_pw = ""

    # when login worker starts
    def run(self):
        # change gui
        self.signals.set_enabled_by_login.emit(True)
        info = 'LOGIN\n\n'
        text = f"Trying to log in...\n" \
               f"ID : {self.user_id}\n" \
               f"PW : {('*' * len(self.user_pw))}"
        self.signals.output.emit(info + text)
        # try login
        res = self.cleaner.login(self.user_id, self.user_pw)
        # when login succeeded
        if res:
            text = f"Login successful\n" \
                   f"ID : {self.user_id}\n" \
                   f"PW : {('*' * len(self.user_pw))}"
            self.signals.output.emit(info + text)
            self.signals.set_enabled_by_login.emit(True)
            self.signals.set_enabled_by_delete.emit(False)
        # when login failed
        else:
            text = f"Login failed\n" \
                   f"ID/PW might be incorrect.\n" \
                   f"Please try again."
            self.signals.output.emit(info + text)
            self.signals.set_enabled_by_login.emit(False)


# delete worker
class DeleteWorker(QRunnable):
    # when instance created
    def __init__(self, cleaner):
        # initial settings
        super(DeleteWorker, self).__init__()
        self.cleaner = cleaner
        self.signals = WorkerSignals()
        self.working = True
        self.post_type = ""

    # when delete worker starts
    def run(self):
        # change gui
        info = f"DELETE {self.post_type.upper()}S\n\n"
        text = f"Counting the number of {self.post_type}s...\n" \
               f"Hold on a moment, please.\n"
        self.signals.set_enabled_by_delete.emit(True)
        self.signals.progressbar_set_value.emit(0)
        self.signals.output.emit(info + text)
        # get number of posts
        number_of_posts = self.cleaner.get_number_of_posts(self.post_type)
        cnt = 0
        spent_time = 0
        expected_time = 0
        text = f"{cnt} / {number_of_posts}\n" \
               f"time spent: {str(get_time(spent_time))}\n"
        self.signals.output.emit(info + text)
        # delete posts
        while self.working:
            # get current time
            time_started = time.time()
            # get post number
            post_number = self.cleaner.get_post_number(self.post_type)
            # when ip blocked
            if post_number == 'BLOCKED':
                signal_type = 'warning'
                signal = "An error has occured.\n" \
                         "Please run Cleanse again."
                self.signals.inform.emit((signal_type, signal))
                break
            # when there's no more posts
            elif post_number is None:
                break
            # wait a second to prevent ip block
            time.sleep(1)
            # delete post
            res = self.cleaner.delete_post(post_number, self.post_type)
            # when captcha detected
            if res and "captcha" in res["result"]:
                signal_type = "warning"
                signal = "CAPTCHA is detected.\n" \
                         "Please delete one posting/comment,\n" \
                         "solve the CAPTCHA, and run Cleanse again."
                self.signals.inform.emit((signal_type, signal))
                break
            # change gui
            cnt += 1
            spent_time += time.time() - time_started
            expected_time = 0 if cnt == number_of_posts else spent_time / cnt * (number_of_posts - cnt)
            text = f"{cnt} / {number_of_posts}\n" \
                   f"time spent: {str(get_time(spent_time))}\n" \
                   f"time left: {str(get_time(expected_time))}"
            self.signals.progressbar_set_value.emit(cnt / number_of_posts * 100)
            self.signals.output.emit(info + text)
        # when deleting posts stopped and there's no more posts
        if cnt == number_of_posts:
            # change gui
            signal_type = "information"
            signal = "Deletion has been completed."
            self.signals.set_enabled_by_delete.emit(False)
            self.signals.inform.emit((signal_type, signal))
        # when deleting posts stopped and there are more posts
        else:
            # change gui
            info = "DELETION STOPPED\n\n"
            text = f"{cnt} / {number_of_posts}\n" \
                   f"time spent: {str(get_time(spent_time))}\n" \
                   f"time left: {str(get_time(expected_time))}"
            self.signals.set_enabled_by_delete.emit(False)
            self.signals.output.emit(info + text)
