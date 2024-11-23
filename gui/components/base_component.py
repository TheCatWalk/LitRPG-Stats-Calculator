from PyQt5.QtWidgets import QWidget

class BaseComponent(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        pass

    def update_display(self):
        pass