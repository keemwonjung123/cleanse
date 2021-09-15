import math
import time
from PyQt5.QtCore import *


def get_time(my_time):
    h = str(int(my_time / 3600))
    m = str(int((my_time % 3600) / 60))
    s = str(int(my_time % 60))
    return f"{h}h {m}m {s}s"


class LoginWorker(QThread):
    def __init__(self, window):
        super(LoginWorker, self).__init__()
        self.window = window
        self.cleaner = window.cleaner

    def run(self):
        self.window.set_enabled_by_login(True)
        info = 'LOGIN\n\n'
        user_id = self.window.id_text.text()
        pw = self.window.pw_text.text()
        text = f"Trying to log in...\n" \
               f"ID : {user_id}\n" \
               f"PW : {('*' * len(pw))}"
        self.window.output(info + text)

        res = self.cleaner.login(user_id, pw)
        if res:
            text = f"Login successful\n" \
                   f"ID : {user_id}\n" \
                   f"PW : {('*' * len(pw))}"
            self.window.output(info + text)
            self.window.set_enabled_by_login(True)
            self.window.set_enabled_by_delete(False)
        else:
            text = f"Login failed\n" \
                   f"ID/PW might be incorrect.\n" \
                   f"Please try again."
            self.window.output(info + text)
            self.window.set_enabled_by_login(False)


class DeleteWorker(QThread):
    def __init__(self, window):
        super(DeleteWorker, self).__init__()
        self.window = window
        self.cleaner = window.cleaner
        self.working = True

    def run(self):
        post_types = ["comment", "posting"]
        post_type = post_types[self.window.posting_chk.isChecked()]

        info = f"DELETE {post_type.upper()}S\n\n"
        text = f"Counting the number of {post_type}s...\n" \
               f"Hold on a moment, please.\n"
        self.window.output(info + text)

        number_of_posts = self.cleaner.get_number_of_posts(post_type)
        cnt = 0
        spent_time = 0
        expected_time = math.inf

        text = f"{cnt} / {number_of_posts}\n" \
               f"{str(get_time(spent_time))} done\n" \
               f"{str(get_time(expected_time))} todo"
        self.window.output(info + text)

        while self.working:
            starting_time = time.time()
            post_number = self.cleaner.get_post_number(post_type)

            if post_number == 'BLOCKED':
                signal_type = 'warning'
                signal = "An error has occured.\n" \
                         "Please run Cleanse again."
                self.inform(signal_type, signal)
                break
            elif post_number is None:
                break

            time.sleep(1)
            res = self.cleaner.delete_post(post_number, post_type)
            if res and "captcha" in res["result"]:
                signal_type = "warning"
                signal = "CAPTCHA is detected.\n" \
                         "Please delete one posting/comment,\n" \
                         "solve the CAPTCHA, and run Cleanse again."
                self.inform(signal_type, signal)

            cnt += 1
            spent_time += time.time() - starting_time
            self.window.progressbar.setValue(cnt / number_of_posts * 100)
            expected_time = 0 if cnt == number_of_posts else spent_time / cnt * (number_of_posts - cnt)
            text = f"{cnt} / {number_of_posts}\n" \
                   f"{str(get_time(spent_time))} done\n" \
                   f"{str(get_time(expected_time))} todo"
            self.window.output(info + text)

        if cnt == number_of_posts:
            signal_type = "information"
            signal = "Deletion has been completed."
            self.window.inform(signal_type, signal)
        else:
            info = "DELETION STOPPED\n\n"
            text = f"{cnt} / {number_of_posts}\n" \
                   f"{str(get_time(spent_time))} done\n" \
                   f"{str(get_time(expected_time))} todo"
            self.window.set_enabled_by_delete(False)
            self.window.output(info + text)