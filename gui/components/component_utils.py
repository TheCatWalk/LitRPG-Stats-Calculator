from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QProgressBar
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor

class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

def create_progress_bar_style():
    return """
        QProgressBar {
            background-color: #F0F0F0;
            border: 1px solid #CCCCCC;
            border-radius: 5px;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
            border-radius: 5px;
        }
    """

def update_exp_display(exp_label, progress_bar, current_exp, max_exp, format_func):
    percentage = (current_exp / max_exp) * 100 if max_exp > 0 else 0
    exp_label.setText(f"Exp: {format_func(current_exp)}/{format_func(max_exp)} [{percentage:.1f}%]")
    progress_bar.setMaximum(100)
    progress_bar.setValue(int(percentage))

def create_exp_input_layout(parent, add_exp_func, add_percent_func):
    exp_input_layout = QHBoxLayout()
    exp_input_layout.addWidget(QLabel("Add Exp:"))
    exp_input = QLineEdit()
    exp_input.setFixedWidth(60)
    exp_input_layout.addWidget(exp_input)
    exp_add_button = QPushButton("+")
    exp_add_button.setFixedWidth(30)
    exp_add_button.clicked.connect(lambda: add_exp_func(exp_input))
    exp_input_layout.addWidget(exp_add_button)

    percent_input_layout = QHBoxLayout()
    percent_input_layout.addWidget(QLabel("Add %:"))
    percent_input = QLineEdit()
    percent_input.setFixedWidth(60)
    percent_input_layout.addWidget(percent_input)
    percent_add_button = QPushButton("+")
    percent_add_button.setFixedWidth(30)
    percent_add_button.clicked.connect(lambda: add_percent_func(percent_input))
    percent_input_layout.addWidget(percent_add_button)

    return exp_input_layout, percent_input_layout, exp_input, percent_input, exp_add_button, percent_add_button

def setup_exp_display(parent, level_label, exp_label, progress_bar):
    exp_info_layout = QHBoxLayout()
    exp_info_layout.addWidget(level_label)
    exp_info_layout.addWidget(exp_label)

    exp_layout = QVBoxLayout()
    exp_layout.addLayout(exp_info_layout)
    exp_layout.addWidget(progress_bar)

    return exp_layout


