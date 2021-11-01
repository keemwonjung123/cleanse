# cleanse 3.0
# main.py

import sys, os
from platform import system as get_platform
from PyQt5.QtWidgets import *
from cleanse_window import CleanseWindow


# main
if __name__ == "__main__":
    if get_platform() == "Windows":
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    app = QApplication(sys.argv)
    cleanse_window = CleanseWindow()
    cleanse_window.show()
    app.exec_()
