# cleanse 3.0
# main.py

import sys
from PyQt5.QtWidgets import *
from cleanse_window import CleanseWindow


# main
if __name__ == "__main__":
    app = QApplication(sys.argv)
    cleanse_window = CleanseWindow()
    cleanse_window.show()
    app.exec_()
