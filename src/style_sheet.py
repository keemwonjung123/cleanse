STYLE_SHEET = """
QMainWindow{
    background-color: white;
}

QWidget{
    background-color: white;
    color: black;
    font-size: 11px;
}

QLineEdit{
    border: 1px solid black;
}

QLineEdit:disabled{
    border: 1px solid rgb(220, 220, 220);
    color: rgb(220, 220, 220);
}

QRadioButton:disabled{
    color: rgb(220, 220, 220);
}

QPushButton {
    background-color: rgb(240, 240, 240);
    border: 1px solid black;
}

QPushButton:pressed {
    background-color: rgb(220, 220, 220);
}

QPushButton:disabled {
    background-color: white;
    border: 1px solid rgb(220, 220, 220);
    color: rgb(220, 220, 220);
}

QProgressBar{
    border: 1px solid #7a7a7a;
}

QProgressBar::chunk{
    background-color: rgb(230, 230, 230);
}

QLabel{
    background-color: rgba(0,0,0,0%);
}
"""
