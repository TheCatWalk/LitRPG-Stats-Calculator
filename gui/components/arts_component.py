from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                             QSpinBox, QGroupBox, QFormLayout, QLineEdit, QPushButton, 
                             QProgressBar, QListWidget, QTextEdit, QGridLayout)
from PyQt5.QtCore import Qt
from .base_component import BaseComponent
from .component_utils import (ClickableLabel, create_progress_bar_style, 
                              update_exp_display, create_exp_input_layout, 
                              setup_exp_display)
from backend.core.core_utils import format_number

class ArtsComponent(BaseComponent):
    def __init__(self, arts_calculator, experience_calculator, stats_calculator, parent=None):
        self.arts_calculator = arts_calculator
        self.experience_calculator = experience_calculator
        self.stats_calculator = stats_calculator
        self.selected_art = None
        self.is_locked = True
        self.show_exact_numbers = False
        super().__init__(parent)

        self.arts_calculator.calculation_updated.connect(self.update_results_display)
        self.stats_calculator.stats_updated.connect(self.recalculate)
        self.experience_calculator.experience_updated.connect(self.update_mastery_display)
        
    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # Left column: Art List
        left_column = QVBoxLayout()
        main_layout.addLayout(left_column, 1)

        self.art_list = QListWidget()
        left_column.addWidget(self.art_list)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Art")
        self.remove_button = QPushButton("Remove Art")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        left_column.addLayout(button_layout)

        # Right column: Art Parameters, Mastery Experience, and Art Information
        right_column = QVBoxLayout()
        main_layout.addLayout(right_column, 2)

        # Art Parameters group (compact)
        params_group = QGroupBox("Art Parameters")
        params_layout = QGridLayout(params_group)
        right_column.addWidget(params_group)

        params_layout.addWidget(QLabel("Name:"), 0, 0)
        self.name_input = QLineEdit()
        params_layout.addWidget(self.name_input, 0, 1, 1, 3)

        params_layout.addWidget(QLabel("Type:"), 1, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Martial", "Spiritual", "Psychic", "Bloodline", "Auxiliary", "Arcane", "Cultivation", "Mixed"])
        params_layout.addWidget(self.type_combo, 1, 1)

        params_layout.addWidget(QLabel("Quality Grade:"), 1, 2)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Mortal Grade", "Elite Grade", "Earth Grade", "Royal Grade", "Imperial Grade",
                                     "Saint Grade", "Sky Grade", "Ascended Grade", "Transcended Grade", "Eternal Grade"])
        params_layout.addWidget(self.quality_combo, 1, 3)

        params_layout.addWidget(QLabel("Quality Level:"), 2, 0)
        self.quality_level_spin = QSpinBox()
        self.quality_level_spin.setRange(1, 10)
        params_layout.addWidget(self.quality_level_spin, 2, 1)

        params_layout.addWidget(QLabel("Notes:"), 3, 0)
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        params_layout.addWidget(self.notes_input, 3, 1, 1, 3)

        # Update the Mastery Experience group
        mastery_exp_group = QGroupBox("Mastery Experience")
        mastery_exp_layout = QVBoxLayout(mastery_exp_group)
        right_column.addWidget(mastery_exp_group)

        self.mastery_level_label = QLabel("Mastery Level: 1 (Initial Step 1)")
        self.mastery_exp_label = ClickableLabel("Exp: 0/100 [0%]")
        self.mastery_exp_label.clicked.connect(self.toggle_number_format)
        
        self.mastery_progress_bar = QProgressBar()
        self.mastery_progress_bar.setTextVisible(False)
        self.mastery_progress_bar.setFixedHeight(10)
        self.mastery_progress_bar.setStyleSheet(create_progress_bar_style())
        
        exp_layout = setup_exp_display(self, self.mastery_level_label, self.mastery_exp_label, self.mastery_progress_bar)
        mastery_exp_layout.addLayout(exp_layout)

        exp_input_layout, percent_input_layout, self.mastery_exp_input, self.mastery_exp_percent_input, self.mastery_exp_add_button, self.mastery_exp_percent_add_button = create_exp_input_layout(
            self, self.add_mastery_experience, self.add_mastery_experience_percent
        )
        mastery_exp_layout.addLayout(exp_input_layout)
        mastery_exp_layout.addLayout(percent_input_layout)

        # Art Information group
        info_group = QGroupBox("Art Information")
        info_layout = QFormLayout(info_group)
        right_column.addWidget(info_group)

        self.realm_label = QLabel()
        info_layout.addRow("Realm:", self.realm_label)

        self.relevant_stats_label = QLabel()
        info_layout.addRow("Relevant Stats:", self.relevant_stats_label)

        self.total_stats_label = QLabel()
        info_layout.addRow("Total Stats:", self.total_stats_label)

        self.ratio_label = QLabel()
        info_layout.addRow("Ratio:", self.ratio_label)

        self.quality_multiplier_label = QLabel()
        info_layout.addRow("Quality Multiplier:", self.quality_multiplier_label)

        self.mastery_multiplier_label = QLabel()
        info_layout.addRow("Mastery Multiplier:", self.mastery_multiplier_label)

        self.initial_boost_label = QLabel()
        info_layout.addRow("Initial Boost:", self.initial_boost_label)

        self.adjustment_multiplier_label = QLabel()
        info_layout.addRow("Adjustment Multiplier:", self.adjustment_multiplier_label)

        self.final_boost_label = QLabel()
        info_layout.addRow("Final Boost:", self.final_boost_label)

        # Connect signals for immediate updates
        self.type_combo.currentTextChanged.connect(self.on_art_parameter_changed)
        self.quality_combo.currentTextChanged.connect(self.on_art_parameter_changed)
        self.quality_level_spin.valueChanged.connect(self.on_art_parameter_changed)
        self.add_button.clicked.connect(self.add_art)
        self.remove_button.clicked.connect(self.remove_art)
        self.art_list.itemSelectionChanged.connect(self.on_art_selection_changed)

        # Initialize
        self.show_exact_numbers = False
        self.recalculate()

    def on_art_parameter_changed(self):
        if self.selected_art:
            self.update_current_art()
            self.recalculate()

    def update_current_art(self):
        if not self.selected_art:
            return
        
        art_name = self.selected_art
        art_type = self.type_combo.currentText()
        quality = self.quality_combo.currentText()
        quality_level = self.quality_level_spin.value()
        notes = self.notes_input.toPlainText()

        self.arts_calculator.update_art(art_name, art_name, art_type, quality, quality_level, notes)

    def add_art(self):
        if self.is_locked:
            return
        name = self.name_input.text()
        if not name:
            return  # Don't add art without a name
        art_type = self.type_combo.currentText()
        quality = self.quality_combo.currentText()
        quality_level = self.quality_level_spin.value()
        notes = self.notes_input.toPlainText()
        
        art = self.arts_calculator.add_art(name, art_type, quality, quality_level, notes)
        self.update_art_list()
        self.clear_input_fields()

    def remove_art(self):
        if self.is_locked:
            return
        selected_items = self.art_list.selectedItems()
        if not selected_items:
            return
        art_name = selected_items[0].text().split(' (')[0]
        self.arts_calculator.remove_art(art_name)
        self.experience_calculator.remove_experience("mastery", art_name)
        self.update_art_list()
        self.clear_input_fields()
        self.update_mastery_display()  # Add this line to reset the display

    def update_art(self):
        if self.is_locked:
            return
        selected_items = self.art_list.selectedItems()
        if not selected_items:
            return
        old_name = selected_items[0].text().split(' (')[0]
        new_name = self.name_input.text()
        art_type = self.type_combo.currentText()
        quality = self.quality_combo.currentText()
        quality_level = self.quality_level_spin.value()
        notes = self.notes_input.toPlainText()
        
        self.arts_calculator.update_art(old_name, new_name, art_type, quality, quality_level, notes)
        self.update_art_list()

    def on_art_selection_changed(self):
        selected_items = self.art_list.selectedItems()
        if not selected_items:
            return
        art_name = selected_items[0].text().split(' (')[0]
        self.selected_art = art_name
        art = self.arts_calculator.get_art(art_name)
        if art:
            self.name_input.setText(art['name'])
            self.type_combo.setCurrentText(art['type'])
            self.quality_combo.setCurrentText(art['quality'])
            self.quality_level_spin.setValue(art['quality_level'])
            self.notes_input.setPlainText(art['notes'])
            self.recalculate()
            self.update_mastery_display()

    def clear_input_fields(self):
        self.name_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.quality_combo.setCurrentIndex(0)
        self.quality_level_spin.setValue(1)
        self.notes_input.clear()

    def update_art_list(self):
        self.art_list.clear()
        for art_name, art in self.arts_calculator.arts.items():
            results = self.arts_calculator.calculate(art_name)
            if results:
                mastery_layer = results.get('mastery_layer', 'Unknown')
                mastery_level_in_layer = results.get('mastery_level_in_layer', 'Unknown')
                display_text = f"{art['name']} ({art['quality']} - Level {art['quality_level']}, {mastery_layer} {mastery_level_in_layer})"
            else:
                display_text = f"{art['name']} ({art['quality']} - Level {art['quality_level']}, Unknown Mastery)"
            self.art_list.addItem(display_text)
    
    def recalculate(self):
        if self.selected_art:
            results = self.arts_calculator.calculate(self.selected_art)
            if results:
                self.update_results_display(results)
    
    def update_results_display(self, results):
        if not results:
            return

        self.realm_label.setText(str(results.get('realm', 'N/A')))
        self.relevant_stats_label.setText(f"{results.get('relevant_stat', 0):.2f}")
        self.total_stats_label.setText(f"{results.get('total_stat', 0):.2f}")
        self.ratio_label.setText(f"{results.get('ratio', 0):.4f}")
        self.quality_multiplier_label.setText(f"{results.get('quality_multiplier', 0):.2f}")
        self.mastery_multiplier_label.setText(f"{results.get('mastery_multiplier', 0):.2f}")
        self.initial_boost_label.setText(f"{results.get('initial_boost', 0):.4f}")
        self.adjustment_multiplier_label.setText(f"{results.get('adjustment_multiplier', 0):.4f}")
        self.final_boost_label.setText(f"{results.get('final_boost', 0):.4f}")

        # Update the art list item to reflect the current mastery level
        selected_items = self.art_list.selectedItems()
        if selected_items and self.selected_art:
            art = self.arts_calculator.get_art(self.selected_art)
            if art:
                mastery_layer = results.get('mastery_layer', 'Unknown')
                mastery_level_in_layer = results.get('mastery_level_in_layer', 'Unknown')
                display_text = f"{art['name']} ({art['quality']} - Level {art['quality_level']}, {mastery_layer} {mastery_level_in_layer})"
                selected_items[0].setText(display_text)

    def update_display(self):
        self.update_art_list()
        if self.selected_art:
            results = self.arts_calculator.calculate(self.selected_art)
            if results:
                self.update_results_display(results)
        self.update_mastery_display()
        self.update_ui_state()

    def toggle_number_format(self):
        self.show_exact_numbers = not self.show_exact_numbers
        self.update_mastery_display()

    def update_mastery_display(self):
        if not self.selected_art:
            return

        mastery_exp = self.experience_calculator.get_experience("mastery", self.selected_art)
        level = mastery_exp['level']
        current_exp = mastery_exp['exp']
        max_exp = self.experience_calculator.calculate_max_exp(level)
        
        mastery_layer = self.experience_calculator.get_mastery_layer(level)
        mastery_level_in_layer = self.experience_calculator.get_mastery_level(level)
        
        self.mastery_level_label.setText(f"Mastery Level: {level} ({mastery_layer} {mastery_level_in_layer})")
        
        update_exp_display(
            self.mastery_exp_label,
            self.mastery_progress_bar,
            current_exp,
            max_exp,
            lambda x: format_number(x, self.show_exact_numbers)
        )
    def add_mastery_experience(self, input_widget):
        if self.is_locked:
            return
        selected_items = self.art_list.selectedItems()
        if not selected_items:
            return
        art_name = selected_items[0].text().split(' (')[0]
        
        try:
            amount = int(input_widget.text() or 0)
            if amount > 2147483647:
                input_widget.setStyleSheet("border: 2px solid red;")
                return
            max_reached = self.experience_calculator.add_experience("mastery", amount, art_name)
            input_widget.clear()
            if max_reached:
                input_widget.setStyleSheet("border: 2px solid red;")
            else:
                input_widget.setStyleSheet("")
            self.recalculate()
            self.update_mastery_display()
        except ValueError:
            print("Invalid input for experience. Please enter a valid number.")

    def add_mastery_experience_percent(self, input_widget):
        if self.is_locked:
            return
        selected_items = self.art_list.selectedItems()
        if not selected_items:
            return
        art_name = selected_items[0].text().split(' (')[0]
        
        try:
            percent = float(input_widget.text() or 0)
            mastery_exp = self.experience_calculator.get_experience("mastery", art_name)
            max_exp = self.experience_calculator.calculate_max_exp(mastery_exp['level'])
            amount = int(round(max_exp * percent / 100))
            if amount > 2147483647:
                input_widget.setStyleSheet("border: 2px solid red;")
                return
            max_reached = self.experience_calculator.add_experience("mastery", amount, art_name)
            input_widget.clear()
            if max_reached:
                input_widget.setStyleSheet("border: 2px solid red;")
            else:
                input_widget.setStyleSheet("")
            self.recalculate()
            self.update_mastery_display()
        except ValueError:
            print("Invalid input for percentage. Please enter a valid number.")

    def set_locked(self, locked):
        self.is_locked = locked
        self.update_ui_state()

    def update_ui_state(self):
        self.add_button.setEnabled(not self.is_locked)
        self.remove_button.setEnabled(not self.is_locked)
        self.name_input.setEnabled(not self.is_locked)
        self.type_combo.setEnabled(not self.is_locked)
        self.quality_combo.setEnabled(not self.is_locked)
        self.quality_level_spin.setEnabled(not self.is_locked)
        self.notes_input.setEnabled(not self.is_locked)
        self.mastery_exp_input.setEnabled(not self.is_locked)
        self.mastery_exp_percent_input.setEnabled(not self.is_locked)

