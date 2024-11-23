from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QButtonGroup, QRadioButton
from .base_component import BaseComponent
from PyQt5.QtCore import pyqtSignal


class LevelUpComponent(BaseComponent):
    levelUpSignal = pyqtSignal()
    
    def __init__(self, calculator, parent=None):
        self.calculator = calculator
        super().__init__(parent)

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.addWidget(QLabel("Level:"))
        self.level_label = QLabel("0")
        layout.addWidget(self.level_label)
        
        self.level_up_group = QButtonGroup(self)
        for primary in self.calculator.primary_stats:
            radio = QRadioButton(primary)
            self.level_up_group.addButton(radio)
            layout.addWidget(radio)
        
        level_up_button = QPushButton("Level Up")
        level_up_button.clicked.connect(self.level_up)
        layout.addWidget(level_up_button)
        layout.addStretch(1)

    def level_up(self):
        selected_button = self.level_up_group.checkedButton()
        if selected_button:
            primary = selected_button.text()
            self.calculator.level_up(primary)
            self.level_label.setText(str(int(self.level_label.text()) + 1))
            self.levelUpSignal.emit()
            
    def update_display(self):
        # This method is left empty as the level display 
        # is updated directly in the level_up method
        pass

