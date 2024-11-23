from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                             QSpinBox, QGroupBox, QFormLayout, QLineEdit, QPushButton, 
                             QProgressBar, QListWidget, QTextEdit, QGridLayout)
from PyQt5.QtCore import Qt
from .base_component import BaseComponent
from .component_utils import (ClickableLabel, create_progress_bar_style, 
                              update_exp_display, create_exp_input_layout, 
                              setup_exp_display)
from backend.core.core_utils import format_number

class TraitsComponent(BaseComponent):
    def __init__(self, traits_calculator, experience_calculator, parent=None):
        self.traits_calculator = traits_calculator
        self.experience_calculator = experience_calculator
        self.show_exact_numbers = False
        self.quality_grades = ["Mortal Grade", "Elite Grade", "Earth Grade", "Royal Grade", "Imperial Grade",
                               "Saint Grade", "Sky Grade", "Ascended Grade", "Transcended Grade", "Eternal Grade"]
        self.is_locked = True
        super().__init__(parent)

        self.experience_calculator.experience_updated.connect(self.update_trait_display)


    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # Left column: Trait List
        left_column = QVBoxLayout()
        main_layout.addLayout(left_column, 1)

        trait_list_group = QGroupBox("Traits")
        trait_list_layout = QVBoxLayout(trait_list_group)
        left_column.addWidget(trait_list_group)

        self.trait_list = QListWidget()
        trait_list_layout.addWidget(self.trait_list)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.remove_button = QPushButton("Remove")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        trait_list_layout.addLayout(button_layout)

        # Right column: Trait Details and Experience
        right_column = QVBoxLayout()
        main_layout.addLayout(right_column, 2)

        # Trait Parameters group
        params_group = QGroupBox("Trait Details")
        params_layout = QFormLayout(params_group)
        right_column.addWidget(params_group)

        self.name_input = QLineEdit()
        params_layout.addRow("Name:", self.name_input)

        quality_layout = QHBoxLayout()
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(self.quality_grades)
        quality_layout.addWidget(self.quality_combo)
        self.quality_level_spin = QSpinBox()
        self.quality_level_spin.setRange(1, 10)
        quality_layout.addWidget(self.quality_level_spin)
        params_layout.addRow("Quality:", quality_layout)

        self.notes_input = QTextEdit()
        self.notes_input.setFixedHeight(60)
        params_layout.addRow("Notes:", self.notes_input)

        # Trait Experience group
        exp_group = QGroupBox("Trait Experience")
        exp_layout = QVBoxLayout(exp_group)
        right_column.addWidget(exp_group)

        self.trait_level_label = QLabel("Level: 1 (Mortal Grade 1)")
        self.trait_exp_label = ClickableLabel("Exp: 0/100 [0%]")
        self.trait_exp_label.clicked.connect(self.toggle_number_format)
        
        self.exp_progress_bar = QProgressBar()
        self.exp_progress_bar.setTextVisible(False)
        self.exp_progress_bar.setFixedHeight(10)
        self.exp_progress_bar.setStyleSheet(create_progress_bar_style())
        
        exp_display_layout = setup_exp_display(self, self.trait_level_label, self.trait_exp_label, self.exp_progress_bar)
        exp_layout.addLayout(exp_display_layout)

        exp_input_layout, percent_input_layout, self.exp_input, self.exp_percent_input, self.exp_add_button, self.exp_percent_add_button = create_exp_input_layout(
            self, self.add_experience, self.add_experience_percent
        )
        exp_layout.addLayout(exp_input_layout)
        exp_layout.addLayout(percent_input_layout)

        # Connect signals
        self.add_button.clicked.connect(self.add_trait)
        self.remove_button.clicked.connect(self.remove_trait)
        self.trait_list.itemSelectionChanged.connect(self.on_trait_selection_changed)

        # Set tooltips
        self.add_button.setToolTip("Add a new trait")
        self.remove_button.setToolTip("Remove the selected trait")
        self.name_input.setToolTip("Enter the name of the trait")
        self.quality_combo.setToolTip("Select the quality grade of the trait")
        self.quality_level_spin.setToolTip("Set the quality level of the trait")
        self.notes_input.setToolTip("Enter any additional notes about the trait")
        self.exp_input.setToolTip("Enter the amount of experience to add")
        self.exp_percent_input.setToolTip("Enter the percentage of experience to add")

    def add_trait(self):
        if self.is_locked:
            return
        name = self.name_input.text()
        if not name:
            return  # Don't add trait without a name
        quality = self.quality_combo.currentText()
        quality_level = self.quality_level_spin.value()
        notes = self.notes_input.toPlainText()
        
        trait = self.traits_calculator.create_trait(name, quality, quality_level)
        trait.notes = notes
        self.traits_calculator.add_trait(trait)
        
        # Initialize experience for the new trait based on its quality grade and level
        initial_exp = self.calculate_total_exp(quality, quality_level)
        self.experience_calculator.set_experience("trait", initial_exp, trait.name)
        
        self.update_trait_list()
        self.clear_input_fields()


    def calculate_total_exp(self, quality, level):
        grade_index = self.quality_grades.index(quality)
        total_levels = grade_index * 10 + level
        return sum(self.experience_calculator.calculate_max_exp(i) for i in range(1, total_levels))


    def remove_trait(self):
        if self.is_locked:
            return
        selected_items = self.trait_list.selectedItems()
        if not selected_items:
            return
        index = self.trait_list.row(selected_items[0])
        trait = self.traits_calculator.get_traits()[index]
        self.traits_calculator.remove_trait(index)
        self.experience_calculator.remove_experience("trait", trait.name)
        self.update_trait_list()
        self.clear_input_fields()
        self.clear_trait_display()  # New method to clear the display

    def clear_trait_display(self):
        self.trait_level_label.setText("Level: - (-)")
        self.trait_exp_label.setText("Exp: 0/0 [0%]")
        self.exp_progress_bar.setValue(0)
        self.quality_combo.setCurrentIndex(0)
        self.quality_level_spin.setValue(1)
        self.name_input.clear()
        self.notes_input.clear()


    def update_trait(self):
        if self.is_locked:
            return
        selected_items = self.trait_list.selectedItems()
        if not selected_items:
            return
        index = self.trait_list.row(selected_items[0])
        trait = self.traits_calculator.get_traits()[index]
        name = self.name_input.text()
        quality = self.quality_combo.currentText()
        quality_level = self.quality_level_spin.value()
        notes = self.notes_input.toPlainText()
        
        self.traits_calculator.update_trait(index, name=name, quality_grade=quality, quality_level=quality_level, notes=notes)
        
        # Update experience if quality or level changed
        if quality != trait.quality_grade or quality_level != trait.quality_level:
            new_exp = self.calculate_initial_exp(quality, quality_level)
            self.experience_calculator.set_experience("trait", new_exp, trait.name)
        
        self.update_trait_list()
        self.update_trait_display()

    def on_trait_selection_changed(self):
        selected_items = self.trait_list.selectedItems()
        if not selected_items:
            return
        index = self.trait_list.row(selected_items[0])
        trait = self.traits_calculator.get_traits()[index]
        self.name_input.setText(trait.name)
        self.quality_combo.setCurrentText(trait.quality_grade)
        self.quality_level_spin.setValue(trait.quality_level)
        self.notes_input.setPlainText(trait.notes)
        self.update_trait_display()

    def clear_input_fields(self):
        self.name_input.clear()
        self.quality_combo.setCurrentIndex(0)
        self.quality_level_spin.setValue(1)
        self.notes_input.clear()

    def update_trait_list(self):
        self.trait_list.clear()
        for trait in self.traits_calculator.get_traits():
            exp_data = self.experience_calculator.get_experience("trait", trait['name'])
            total_exp = exp_data['exp']
            current_grade, current_level, _, _ = self.calculate_trait_level(total_exp)
            display_text = f"{trait['name']} ({current_grade}, Level {current_level})"
            self.trait_list.addItem(display_text)

    def update_trait_display(self, exp_type=None, identifier=None, *args):
        if exp_type is not None and exp_type != "trait":
            return

        selected_items = self.trait_list.selectedItems()
        if not selected_items:
            self.clear_trait_display()
            return

        index = self.trait_list.row(selected_items[0])
        traits = self.traits_calculator.get_traits()
        
        if index >= len(traits):
            self.clear_trait_display()
            return

        trait = traits[index]

        exp_data = self.experience_calculator.get_experience("trait", trait['name'])
        total_exp = exp_data['exp']
        
        current_grade, current_level, current_exp, max_exp = self.calculate_trait_level(total_exp)
        
        self.trait_level_label.setText(f"Level: {current_level} ({current_grade})")
        
        update_exp_display(
            self.trait_exp_label,
            self.exp_progress_bar,
            current_exp,
            max_exp,
            lambda x: format_number(x, self.show_exact_numbers)
        )

        # Update UI to reflect trait's current grade and level
        self.quality_combo.setCurrentText(current_grade)
        self.quality_level_spin.setValue(current_level)
        self.name_input.setText(trait['name'])
        self.notes_input.setPlainText(trait['notes'])

        # Update the trait list item
        display_text = f"{trait['name']} ({current_grade}, Level {current_level})"
        selected_items[0].setText(display_text)

        # Clear and reset styling for input fields
        self.exp_input.clear()
        self.exp_input.setStyleSheet("")
        self.exp_percent_input.clear()
        self.exp_percent_input.setStyleSheet("")

    def calculate_initial_exp(self, quality, level):
        grade_index = self.quality_grades.index(quality)
        total_levels = grade_index * 10 + level
        return sum(self.experience_calculator.calculate_max_exp(i) for i in range(1, total_levels))

    def calculate_trait_level(self, total_exp):
        accumulated_exp = 0
        for grade_index, grade in enumerate(self.quality_grades):
            for level in range(1, 11):
                max_exp = self.experience_calculator.calculate_max_exp(grade_index * 10 + level)
                if accumulated_exp + max_exp > total_exp:
                    return grade, level, total_exp - accumulated_exp, max_exp
                accumulated_exp += max_exp
        return self.quality_grades[-1], 10, 0, self.experience_calculator.calculate_max_exp(100)  # Max level

    def toggle_number_format(self):
        self.show_exact_numbers = not self.show_exact_numbers
        self.update_trait_display()

    def add_experience(self, input_widget):
        if self.is_locked:
            return
        selected_items = self.trait_list.selectedItems()
        if not selected_items:
            input_widget.setStyleSheet("border: 2px solid red;")
            return
        index = self.trait_list.row(selected_items[0])
        trait = self.traits_calculator.get_traits()[index]
        
        try:
            amount = int(input_widget.text() or 0)
            if amount <= 0:
                input_widget.setStyleSheet("border: 2px solid red;")
                return
            
            current_exp = self.experience_calculator.get_experience("trait", trait.name)['exp']
            new_total_exp = current_exp + amount
            
            # Calculate new grade and level
            new_grade, new_level, _, _ = self.calculate_trait_level(new_total_exp)
            
            # Update trait
            trait.quality_grade = new_grade
            trait.quality_level = new_level
            self.traits_calculator.update_trait(index, quality_grade=new_grade, quality_level=new_level)
            
            # Update experience
            self.experience_calculator.set_experience("trait", new_total_exp, trait.name)
            
            input_widget.clear()
            input_widget.setStyleSheet("")
            self.update_trait_display()
        except ValueError:
            input_widget.setStyleSheet("border: 2px solid red;")
            print("Invalid input for experience. Please enter a valid number.")


    def add_experience_percent(self, input_widget):
        if self.is_locked:
            return
        selected_items = self.trait_list.selectedItems()
        if not selected_items:
            input_widget.setStyleSheet("border: 2px solid red;")
            return
        index = self.trait_list.row(selected_items[0])
        trait = self.traits_calculator.get_traits()[index]
        
        try:
            percent = float(input_widget.text() or 0)
            if percent <= 0:
                input_widget.setStyleSheet("border: 2px solid red;")
                return
            
            current_exp = self.experience_calculator.get_experience("trait", trait.name)['exp']
            current_grade, current_level, _, max_exp = self.calculate_trait_level(current_exp)
            amount = int(round(max_exp * percent / 100))
            new_total_exp = current_exp + amount
            
            # Calculate new grade and level
            new_grade, new_level, _, _ = self.calculate_trait_level(new_total_exp)
            
            # Update trait
            trait.quality_grade = new_grade
            trait.quality_level = new_level
            self.traits_calculator.update_trait(index, quality_grade=new_grade, quality_level=new_level)
            
            # Update experience
            self.experience_calculator.set_experience("trait", new_total_exp, trait.name)
            
            input_widget.clear()
            input_widget.setStyleSheet("")
            self.update_trait_display()
        except ValueError:
            input_widget.setStyleSheet("border: 2px solid red;")
            print("Invalid input for percentage. Please enter a valid number.")

    def update_display(self):
        self.update_trait_list()
        self.update_trait_display()
        self.update_ui_state()

    def set_locked(self, locked):
        self.is_locked = locked
        self.update_ui_state()

    def update_ui_state(self):
        self.add_button.setEnabled(not self.is_locked)
        self.remove_button.setEnabled(not self.is_locked)
        self.name_input.setEnabled(not self.is_locked)
        self.quality_combo.setEnabled(not self.is_locked)
        self.quality_level_spin.setEnabled(not self.is_locked)
        self.notes_input.setEnabled(not self.is_locked)
        self.exp_input.setEnabled(not self.is_locked)
        self.exp_percent_input.setEnabled(not self.is_locked)

