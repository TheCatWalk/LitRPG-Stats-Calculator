from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QListWidget, QGroupBox, QFormLayout, 
                             QMessageBox, QInputDialog, QListWidgetItem, QCheckBox)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor
import logging
from .base_component import BaseComponent

class CharacterProgressionComponent(BaseComponent):
    character_selected = pyqtSignal(str)
    chapter_selected = pyqtSignal(int)
    checkpoint_selected = pyqtSignal(dict)
    lock_state_changed = pyqtSignal(bool)

    def __init__(self, character_database, stats_calculator, energy_calculator, 
                 arts_calculator, traits_calculator, experience_calculator, parent=None):
        self.character_db = character_database
        self.stats_calculator = stats_calculator
        self.energy_calculator = energy_calculator
        self.arts_calculator = arts_calculator
        self.traits_calculator = traits_calculator
        self.experience_calculator = experience_calculator
        self.current_character = None
        self.current_chapter = None
        self.current_checkpoint = None
        self.is_locked = False
        self.lock_checkbox = None
        
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        
        super().__init__(parent)

    def init_ui(self):
        layout = QHBoxLayout(self)


        # Character Management
        character_group = QGroupBox("Characters")
        character_layout = QVBoxLayout(character_group)
        self.character_list = QListWidget()
        self.character_list.itemClicked.connect(self.on_character_selected)
        character_layout.addWidget(self.character_list)

        character_button_layout = QHBoxLayout()
        self.create_character_btn = QPushButton("Create")
        self.remove_character_btn = QPushButton("Remove")
        self.create_character_btn.clicked.connect(self.create_character)
        self.remove_character_btn.clicked.connect(self.remove_character)
        character_button_layout.addWidget(self.create_character_btn)
        character_button_layout.addWidget(self.remove_character_btn)
        character_layout.addLayout(character_button_layout)

        self.character_input = QLineEdit()
        character_layout.addWidget(self.character_input)

        layout.addWidget(character_group)

        # Chapter Management
        chapter_group = QGroupBox("Chapters")
        chapter_layout = QVBoxLayout(chapter_group)
        self.chapter_list = QListWidget()
        self.chapter_list.itemClicked.connect(self.on_chapter_selected)
        chapter_layout.addWidget(self.chapter_list)

        chapter_button_layout = QHBoxLayout()
        self.add_chapter_btn = QPushButton("Add Chapter")
        self.remove_chapter_btn = QPushButton("Remove Chapter")
        self.add_chapter_btn.clicked.connect(self.add_chapter)
        self.remove_chapter_btn.clicked.connect(self.remove_chapter)
        chapter_button_layout.addWidget(self.add_chapter_btn)
        chapter_button_layout.addWidget(self.remove_chapter_btn)
        chapter_layout.addLayout(chapter_button_layout)

        layout.addWidget(chapter_group)

        # Checkpoint Management
        checkpoint_group = QGroupBox("Checkpoints")
        checkpoint_layout = QVBoxLayout(checkpoint_group)
        self.checkpoint_list = QListWidget()
        self.checkpoint_list.itemClicked.connect(self.on_checkpoint_selected)
        checkpoint_layout.addWidget(self.checkpoint_list)

        checkpoint_button_layout = QHBoxLayout()
        self.add_checkpoint_btn = QPushButton("Add Checkpoint")
        self.remove_checkpoint_btn = QPushButton("Remove Checkpoint")
        self.save_checkpoint_btn = QPushButton("Save Current State")
        self.add_checkpoint_btn.clicked.connect(self.add_checkpoint)
        self.remove_checkpoint_btn.clicked.connect(self.remove_checkpoint)
        self.save_checkpoint_btn.clicked.connect(self.save_current_state)
        checkpoint_button_layout.addWidget(self.add_checkpoint_btn)
        checkpoint_button_layout.addWidget(self.remove_checkpoint_btn)
        checkpoint_button_layout.addWidget(self.save_checkpoint_btn)
        checkpoint_layout.addLayout(checkpoint_button_layout)

        layout.addWidget(checkpoint_group)

        # Rename "Lock Editing" to "Lock"
        self.lock_checkbox = QCheckBox("Lock")
        self.lock_checkbox.setChecked(False)
        self.lock_checkbox.setEnabled(False)
        self.lock_checkbox.stateChanged.connect(self.toggle_lock)
        layout.addWidget(self.lock_checkbox)

        self.update_character_list()
        self.update_ui_state()
    
    
    def update_character_list(self):
        self.character_list.clear()
        for character_file in self.character_db.get_character_list():
            character_name = character_file.replace('.json', '')
            item = QListWidgetItem(character_name)
            if character_name == self.current_character:
                item.setBackground(QColor(173, 216, 230))  # Light blue background for selected character
            self.character_list.addItem(item)

    def toggle_lock(self, state):
        if state == Qt.Checked and (self.current_character is None or self.current_chapter is None or self.current_checkpoint is None):
            QMessageBox.warning(self, "Cannot Lock", "Please select a character, chapter, and checkpoint before locking.")
            self.lock_checkbox.setChecked(False)
            return

        self.is_locked = state == Qt.Checked
        if not self.is_locked:
            self.save_current_state(auto_save=True)
        self.lock_state_changed.emit(self.is_locked and self.current_character is not None and self.current_chapter is not None and self.current_checkpoint is not None)
        self.update_ui_state()


    def create_character(self):
        character_name = self.character_input.text().strip()
        if not character_name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a character name.")
            return

        try:
            self.character_db.create_character(character_name)
            self.update_character_list()
            self.character_input.clear()
            self.reset_all_calculators()
            self.current_character = character_name
            self.current_chapter = None
            self.current_checkpoint = None
            self.update_ui_state()
            self.character_selected.emit(self.current_character)
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def on_character_selected(self, item):
        if self.is_locked:
            return

        if self.current_character:
            self.save_current_state(auto_save=True)

        self.current_character = item.text()
        self.logger.debug(f"Character selected: {self.current_character}")
        self.current_chapter = None
        self.current_checkpoint = None
        self.character_selected.emit(self.current_character)
        self.update_character_list()
        self.load_character_data()
        self.update_ui_state()

    def on_chapter_selected(self, item):
        if self.is_locked:
            return

        if self.current_chapter:
            self.save_current_state(auto_save=True)

        self.current_chapter = int(item.text().split()[-1])
        self.logger.debug(f"Chapter selected: {self.current_chapter}")
        self.chapter_selected.emit(self.current_chapter)
        self.update_chapter_list()
        self.update_checkpoint_list()
        self.update_ui_state()

        # Auto-select corresponding character
        character_item = self.character_list.findItems(self.current_character, Qt.MatchExactly)[0]
        self.character_list.setCurrentItem(character_item)

    def on_checkpoint_selected(self, item):
        if self.is_locked:
            return

        if self.current_checkpoint:
            self.save_current_state(auto_save=True)

        self.select_checkpoint(item.text())

    def update_chapter_list(self):
        self.chapter_list.clear()
        if not self.current_character:
            return

        character_data = self.character_db.load_character(self.current_character)
        for chapter in character_data.get("chapters", []):
            item = QListWidgetItem(f"Chapter {chapter['number']}")
            if chapter['number'] == self.current_chapter:
                item.setBackground(QColor(173, 216, 230))  # Light blue background for selected chapter
            self.chapter_list.addItem(item)  # Changed from addWidget to addItem

    def update_checkpoint_list(self):
        self.checkpoint_list.clear()
        if not self.current_character or self.current_chapter is None:
            return

        character_data = self.character_db.load_character(self.current_character)
        chapter = next((c for c in character_data.get("chapters", []) if c["number"] == self.current_chapter), None)
        if chapter:
            for checkpoint in chapter.get("checkpoints", []):
                item = QListWidgetItem(checkpoint["name"])
                if checkpoint["name"] == self.current_checkpoint:
                    item.setBackground(QColor(173, 216, 230))  # Light blue background for selected checkpoint
                self.checkpoint_list.addItem(item)
        
        self.logger.debug(f"Updated checkpoint list. Items: {[self.checkpoint_list.item(i).text() for i in range(self.checkpoint_list.count())]}")

    def add_chapter(self):
        if not self.current_character:
            QMessageBox.warning(self, "Error", "Please select a character first.")
            return

        chapter_number, ok = QInputDialog.getInt(self, "Add Chapter", "Chapter number:")
        if not ok:
            return

        try:
            self.character_db.add_chapter(self.current_character, chapter_number, "", "")
            self.update_chapter_list()
            self.current_chapter = chapter_number
            self.update_ui_state()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def add_checkpoint(self):
        self.logger.debug(f"Attempting to add checkpoint. Current character: {self.current_character}, Current chapter: {self.current_chapter}")
        if self.current_character is None or self.current_chapter is None:
            QMessageBox.warning(self, "Error", "Please select a character and chapter first.")
            self.logger.warning("Attempted to add checkpoint without character or chapter selected")
            return

        checkpoint_name, ok = QInputDialog.getText(self, "Add Checkpoint", "Checkpoint name:")
        if not ok or not checkpoint_name.strip():
            return

        stats = self.gather_current_stats()

        try:
            self.character_db.add_checkpoint(self.current_character, self.current_chapter, checkpoint_name, stats)
            self.update_checkpoint_list()
            self.select_checkpoint(checkpoint_name)
            self.logger.info(f"Checkpoint '{checkpoint_name}' added successfully for character '{self.current_character}' in chapter {self.current_chapter}")
            QMessageBox.information(self, "Success", f"Checkpoint '{checkpoint_name}' added successfully.")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            self.logger.error(f"Error adding checkpoint: {str(e)}")

    def select_checkpoint(self, checkpoint_name):
        self.current_checkpoint = checkpoint_name
        self.logger.debug(f"Checkpoint selected: {self.current_checkpoint}")
        checkpoint_data = self.load_checkpoint_data(self.current_checkpoint)
        self.checkpoint_selected.emit(checkpoint_data)
        self.update_ui_state()

        # Update the checkpoint list selection
        items = self.checkpoint_list.findItems(checkpoint_name, Qt.MatchExactly)
        if items:
            self.checkpoint_list.setCurrentItem(items[0])

    def remove_character(self):
        if not self.current_character:
            QMessageBox.warning(self, "Error", "Please select a character to remove.")
            return

        reply = QMessageBox.question(self, 'Remove Character',
                                     f"Are you sure you want to remove the character '{self.current_character}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.character_db.remove_character(self.current_character)
                self.current_character = None
                self.current_chapter = None
                self.current_checkpoint = None
                self.update_character_list()
                self.chapter_list.clear()
                self.checkpoint_list.clear()
                self.reset_all_calculators()
                self.update_ui_state()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def remove_chapter(self):
        if not self.current_character or self.current_chapter is None:
            QMessageBox.warning(self, "Error", "Please select a character and chapter to remove.")
            return

        reply = QMessageBox.question(self, 'Remove Chapter',
                                     f"Are you sure you want to remove Chapter {self.current_chapter}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.character_db.remove_chapter(self.current_character, self.current_chapter)
                self.current_chapter = None
                self.current_checkpoint = None
                self.update_chapter_list()
                self.checkpoint_list.clear()
                self.update_ui_state()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def remove_checkpoint(self):
        if not self.current_character or self.current_chapter is None or not self.current_checkpoint:
            QMessageBox.warning(self, "Error", "Please select a character, chapter, and checkpoint to remove.")
            return

        reply = QMessageBox.question(self, 'Remove Checkpoint',
                                     f"Are you sure you want to remove the checkpoint '{self.current_checkpoint}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.character_db.remove_checkpoint(self.current_character, self.current_chapter, self.current_checkpoint)
                self.current_checkpoint = None
                self.update_checkpoint_list()
                self.update_ui_state()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def load_character_data(self):
        if not self.current_character:
            return
        character_data = self.character_db.load_character(self.current_character)
        self.reset_all_calculators()
        self.update_all_calculators(character_data)
        self.logger.debug(f"Loaded character data: {character_data}")
        
        # Reset chapter and checkpoint selection
        self.current_chapter = None
        self.current_checkpoint = None
        
        # Update chapters and checkpoints
        self.update_chapter_list()
        self.checkpoint_list.clear()
        
        self.update_ui_state()
        self.lock_state_changed.emit(False)  # Ensure everything is unlocked when loading a new character


    def update_all_calculators(self, data):
        self.stats_calculator.load_stats(data.get('stats', {}))
        self.energy_calculator.load_energy(data.get('energy', {}))
        self.experience_calculator.load_experience(data.get('experience', {}))
        self.arts_calculator.load_arts(data.get('arts', {}))
        self.traits_calculator.load_traits(data.get('traits', []))
        
        self.logger.debug(f"Updated free points: {self.stats_calculator.free_points}, train points: {self.stats_calculator.train_points}")

    def reset_all_calculators(self):
        self.stats_calculator.reset()
        self.energy_calculator.reset()
        self.experience_calculator.reset()
        self.arts_calculator.reset()
        self.traits_calculator.reset()

    def gather_current_stats(self):
        return {
            "stats": self.stats_calculator.get_stats(),
            "energy": self.energy_calculator.get_energy_values(),
            "experience": self.experience_calculator.get_all_experience(),
            "arts": self.arts_calculator.get_arts(),
            "traits": self.traits_calculator.get_traits(),
        }

    def save_current_state(self, auto_save=False):
        if not self.current_character or self.current_chapter is None or not self.current_checkpoint:
            return

        stats = self.gather_current_stats()

        try:
            if auto_save:
                self.character_db.update_checkpoint(self.current_character, self.current_chapter, self.current_checkpoint, stats)
                self.logger.info(f"Auto-saved checkpoint '{self.current_checkpoint}' for character '{self.current_character}' in chapter {self.current_chapter}")
            else:
                checkpoint_name, ok = QInputDialog.getText(self, "Save Current State", "Checkpoint name:")
                if ok and checkpoint_name.strip():
                    self.character_db.add_checkpoint(self.current_character, self.current_chapter, checkpoint_name, stats)
                    self.current_checkpoint = checkpoint_name
                    self.update_checkpoint_list()
                    QMessageBox.information(self, "Success", f"Checkpoint '{checkpoint_name}' saved successfully.")
                    self.logger.info(f"Checkpoint '{checkpoint_name}' saved successfully for character '{self.current_character}' in chapter {self.current_chapter}")
            self.update_ui_state()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            self.logger.error(f"Error saving checkpoint: {str(e)}")

    def load_checkpoint_data(self, checkpoint_name):
        if not self.current_character or self.current_chapter is None:
            return {}

        try:
            checkpoint_data = self.character_db.get_character_data(
                self.current_character, self.current_chapter, checkpoint_name
            )
            if checkpoint_data and 'stats' in checkpoint_data:
                self.update_all_calculators(checkpoint_data['stats'])
                return checkpoint_data['stats']
            else:
                self.logger.warning(f"Invalid checkpoint data for {checkpoint_name}")
                return {}
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            return {}

    def update_ui_state(self):
        has_character = self.current_character is not None
        has_chapter = self.current_chapter is not None
        has_checkpoint = self.current_checkpoint is not None

        self.lock_checkbox.setEnabled(has_character and has_chapter and has_checkpoint)
        self.lock_checkbox.setChecked(self.is_locked)

        if self.is_locked:
            self.character_list.setEnabled(False)
            self.chapter_list.setEnabled(False)
            self.checkpoint_list.setEnabled(False)
            self.create_character_btn.setEnabled(False)
            self.remove_character_btn.setEnabled(False)
            self.add_chapter_btn.setEnabled(False)
            self.remove_chapter_btn.setEnabled(False)
            self.add_checkpoint_btn.setEnabled(False)
            self.remove_checkpoint_btn.setEnabled(False)
            self.save_checkpoint_btn.setEnabled(True)
        else:
            self.character_list.setEnabled(True)
            self.chapter_list.setEnabled(has_character)
            self.checkpoint_list.setEnabled(has_character and has_chapter)
            self.create_character_btn.setEnabled(True)
            self.remove_character_btn.setEnabled(has_character)
            self.add_chapter_btn.setEnabled(has_character)
            self.remove_chapter_btn.setEnabled(has_character and has_chapter)
            self.add_checkpoint_btn.setEnabled(has_character and has_chapter)
            self.remove_checkpoint_btn.setEnabled(has_character and has_chapter and has_checkpoint)
            self.save_checkpoint_btn.setEnabled(has_character and has_chapter and has_checkpoint)

        self.lock_state_changed.emit(self.is_locked and has_character and has_chapter and has_checkpoint)

    def handle_level_up(self, new_level, primary_stat):
        self.logger.debug(f"Handling level up to {new_level}, primary stat: {primary_stat}")
        self.stats_calculator.handle_level_up(new_level, primary_stat)
        self.energy_calculator.calculate()
        self.update_display()
        self.save_current_character_data()

    def save_current_character_data(self):
        if self.current_character and not self.is_locked:
            current_data = self.gather_current_stats()
            try:
                self.character_db.update_character(self.current_character, current_data)
                self.logger.info(f"Character '{self.current_character}' data saved successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save character data: {str(e)}")
                self.logger.error(f"Error saving character data: {str(e)}")

    def update_display(self):
        self.update_character_list()
        if self.current_character:
            self.update_chapter_list()
        if self.current_chapter is not None:
            self.update_checkpoint_list()
        self.update_ui_state()

