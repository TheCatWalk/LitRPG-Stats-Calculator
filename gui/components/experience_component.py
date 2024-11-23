from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QRadioButton, QButtonGroup, QGroupBox, QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from .base_component import BaseComponent
from .component_utils import (ClickableLabel, create_progress_bar_style, 
                              update_exp_display, create_exp_input_layout, 
                              setup_exp_display)
from backend.core.core_utils import format_number

class ExperienceComponent(BaseComponent):
    def __init__(self, calculator, parent=None):
        self.calculator = calculator
        self.initial_stat = None
        self.show_exact_numbers = False
        self.is_locked = False
        super().__init__(parent)

        self.calculator.experience_updated.connect(self.update_display)
        self.calculator.level_up.connect(self.update_display)
        self.calculator.max_level_reached.connect(self.handle_max_level)

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # Character Progress Group
        progress_group = QGroupBox("Character Progress")
        progress_layout = QHBoxLayout(progress_group)

        self.char_level_label = QLabel("Level: 0")
        progress_layout.addWidget(self.char_level_label)
        
        self.char_exp_label = ClickableLabel("Exp: 0/10 [0%]")
        self.char_exp_label.clicked.connect(self.toggle_number_format)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setStyleSheet(create_progress_bar_style())
        
        exp_layout = setup_exp_display(self, self.char_level_label, self.char_exp_label, self.progress_bar)
        progress_layout.addLayout(exp_layout)

        exp_input_layout, percent_input_layout, self.char_exp_input, self.char_exp_percent_input, self.char_exp_add_button, self.char_exp_percent_add_button = create_exp_input_layout(
            self, self.add_character_experience, self.add_character_experience_percent
        )
        progress_layout.addLayout(exp_input_layout)
        progress_layout.addLayout(percent_input_layout)

        main_layout.addWidget(progress_group, 3)

        # Level Up Order Group
        level_up_group = QGroupBox("Level Up Order")
        level_up_layout = QHBoxLayout(level_up_group)
        self.level_up_labels = []
        self.initial_stat_buttons = QButtonGroup(self)
        for primary in ["Body", "Spirit", "Mind"]:
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setAlignment(Qt.AlignCenter)
            container_layout.setContentsMargins(0, 0, 0, 0)
            label = QLabel(primary)
            label.setAlignment(Qt.AlignCenter)
            self.level_up_labels.append(label)
            container_layout.addWidget(label)
            
            radio = QRadioButton()
            self.initial_stat_buttons.addButton(radio)
            container_layout.addWidget(radio)
            
            level_up_layout.addWidget(container)

        main_layout.addWidget(level_up_group, 1)

        self.initial_stat_buttons.buttonClicked.connect(self.on_initial_stat_selected)
        self.initial_stat_buttons.buttons()[0].setChecked(True)
        self.on_initial_stat_selected(self.initial_stat_buttons.buttons()[0])

        # Connect buttons to methods
        self.char_exp_add_button.clicked.connect(lambda: self.add_character_experience(self.char_exp_input))
        self.char_exp_percent_add_button.clicked.connect(lambda: self.add_character_experience_percent(self.char_exp_percent_input))

        # Connect radio buttons
        self.initial_stat_buttons.buttonClicked.connect(self.on_initial_stat_selected)


    def toggle_number_format(self):
        self.show_exact_numbers = not self.show_exact_numbers
        self.update_display()

    def update_display(self):
        char_exp = self.calculator.get_experience("character")
        level = char_exp['level']
        current_exp = char_exp['exp']
        max_exp = self.calculator.calculate_max_exp(level)
        
        self.char_level_label.setText(f"Level: {level}")
        
        update_exp_display(
            self.char_exp_label,
            self.progress_bar,
            current_exp,
            max_exp,
            lambda x: format_number(x, self.show_exact_numbers)
        )


        # Update level up order display
        current_index = self.calculator.get_current_level_up_index()
        for i, label in enumerate(self.level_up_labels):
            if i == current_index:
                self.initial_stat_buttons.buttons()[i].setChecked(True)
            
            if self.level_up_labels[i].text() == self.initial_stat:
                color = QColor("#FF0000") if self.initial_stat == "Body" else \
                        QColor("#00FF00") if self.initial_stat == "Spirit" else \
                        QColor("#0000FF")
                label.setStyleSheet(f"color: {color.name()}; font-weight: bold;")
            else:
                label.setStyleSheet("")

        # Enable initial stat selection only at level 0
        for button in self.initial_stat_buttons.buttons():
            button.setEnabled(level == 0)
        self.update_ui_state()

    def on_initial_stat_selected(self, button):
        if not self.is_locked:
            return
        index = self.initial_stat_buttons.buttons().index(button)
        self.initial_stat = ["Body", "Spirit", "Mind"][index]
        self.calculator.set_initial_stat(self.initial_stat)
        self.update_display()

    def add_character_experience(self, input_widget):
        if not self.is_locked:
            return
        try:
            amount = int(input_widget.text() or 0)
            if amount > 2147483647:
                input_widget.setStyleSheet("border: 2px solid red;")
                return
            max_reached = self.calculator.add_experience("character", amount)
            input_widget.clear()
            if max_reached:
                input_widget.setStyleSheet("border: 2px solid red;")
            else:
                input_widget.setStyleSheet("")
        except ValueError:
            print("Invalid input for experience. Please enter a valid number.")

    def add_character_experience_percent(self, input_widget):
        if not self.is_locked:
            return
        try:
            percent = float(input_widget.text() or 0)
            char_exp = self.calculator.get_experience("character")
            max_exp = self.calculator.calculate_max_exp(char_exp['level'])
            amount = int(round(max_exp * percent / 100))
            if amount > 2147483647:
                input_widget.setStyleSheet("border: 2px solid red;")
                return
            max_reached = self.calculator.add_experience("character", amount)
            input_widget.clear()
            if max_reached:
                input_widget.setStyleSheet("border: 2px solid red;")
            else:
                input_widget.setStyleSheet("")
        except ValueError:
            print("Invalid input for percentage. Please enter a valid number.")

    def handle_max_level(self, exp_type, identifier):
        if exp_type == "character" and identifier == "character":
            self.char_exp_input.setStyleSheet("border: 2px solid red;")
            self.char_exp_percent_input.setStyleSheet("border: 2px solid red;")
            self.char_exp_input.setEnabled(False)
            self.char_exp_percent_input.setEnabled(False)

    def set_locked(self, locked):
        self.is_locked = locked
        self.update_ui_state()

    def update_ui_state(self):
        self.char_exp_input.setEnabled(self.is_locked)
        self.char_exp_add_button.setEnabled(self.is_locked)
        self.char_exp_percent_input.setEnabled(self.is_locked)
        self.char_exp_percent_add_button.setEnabled(self.is_locked)
        for button in self.initial_stat_buttons.buttons():
            button.setEnabled(self.is_locked and self.calculator.get_level("character") == 0)

    def handle_max_level(self, exp_type, identifier):
        if exp_type == "character" and identifier == "character":
            self.char_exp_input.setStyleSheet("border: 2px solid red;")
            self.char_exp_percent_input.setStyleSheet("border: 2px solid red;")
            self.char_exp_input.setEnabled(False)
            self.char_exp_percent_input.setEnabled(False)

