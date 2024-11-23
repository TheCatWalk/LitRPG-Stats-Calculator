from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox, QMessageBox
from backend.core.calculator_factory import CalculatorFactory
from gui.ui_factory import UIFactory

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DeepStats - LitRPG Character Manager")
        self.setGeometry(100, 100, 1200, 800)
        self.init_calculators()
        self.init_ui()

    def init_calculators(self):
        self.stats_calculator = CalculatorFactory.get_calculator("stats")
        self.energy_calculator = CalculatorFactory.get_calculator("energy", self.stats_calculator)
        self.experience_calculator = CalculatorFactory.get_calculator("experience", self.stats_calculator)
        self.arts_calculator = CalculatorFactory.get_calculator("arts", self.stats_calculator, self.experience_calculator)
        self.traits_calculator = CalculatorFactory.get_calculator("traits", self.experience_calculator)
        self.character_database = CalculatorFactory.get_calculator("character_database", "data")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Character Progression Component (top section)
        self.progression_component = UIFactory.create_component(
            "character_progression",
            self.character_database,
            self.stats_calculator,
            self.energy_calculator,
            self.arts_calculator,
            self.traits_calculator,
            self.experience_calculator
        )
        main_layout.addWidget(self.progression_component)

        # Tab widget for other components
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Profile tab (combining stats, energy, and experience)
        profile_widget = QWidget()
        profile_layout = QVBoxLayout(profile_widget)
        
        self.experience_component = UIFactory.create_component("experience", self.experience_calculator)
        profile_layout.addWidget(self.experience_component)
        
        self.stats_component = UIFactory.create_component("stats", self.stats_calculator)
        profile_layout.addWidget(self.stats_component)
        
        energy_group = QGroupBox("Energies")
        energy_layout = QVBoxLayout(energy_group)
        self.energy_component = UIFactory.create_component("energy", self.energy_calculator)
        energy_layout.addWidget(self.energy_component)
        profile_layout.addWidget(energy_group)
        
        self.tab_widget.addTab(profile_widget, "Profile")

        # Other tabs
        self.tab_widget.addTab(UIFactory.create_component("arts", self.arts_calculator, self.experience_calculator, self.stats_calculator), "Arts")
        self.tab_widget.addTab(UIFactory.create_component("traits", self.traits_calculator, self.experience_calculator), "Traits")

        # Connect signals
        self.progression_component.character_selected.connect(self.load_character_data)
        self.progression_component.checkpoint_selected.connect(self.load_checkpoint_data)
        self.experience_calculator.character_level_up.connect(self.handle_level_up)
        self.stats_calculator.stats_updated.connect(self.update_components)

        # Connect the lock state signal
        self.progression_component.lock_state_changed.connect(self.update_component_lock_states)

        # Initially disable tabs and lock UI until a character is selected
        self.tab_widget.setEnabled(False)
        self.update_component_lock_states(False)
    
    def handle_level_up(self, new_level, primary_stat):
        self.stats_calculator.handle_level_up(new_level, primary_stat)

    def load_character_data(self, character_name):
        # Load the character's data and update all components
        character_data = self.character_database.load_character(character_name)
        self.update_all_components(character_data)
        self.tab_widget.setEnabled(True)
        self.update_component_lock_states(False)  # Unlock UI when a character is loaded


    def load_checkpoint_data(self, checkpoint_data):
        # Update all components with the checkpoint data
        self.update_all_components(checkpoint_data)

    def update_all_components(self, data):
        self.stats_calculator.load_stats(data.get('stats', {}))
        self.energy_calculator.load_energy(data.get('energy', {}))
        self.experience_calculator.load_experience(data.get('experience', {}))
        self.arts_calculator.load_arts(data.get('arts', {}))
        self.traits_calculator.load_traits(data.get('traits', []))
        self.update_components()

    def update_components(self):
        # Update individual components
        self.stats_component.update_display()
        self.energy_component.update_display()
        self.experience_component.update_display()
        
        # Update the arts and traits components
        self.tab_widget.widget(1).update_display()  # Arts tab
        self.tab_widget.widget(2).update_display()  # Traits tab
        
        # Update the progression component if needed
        self.progression_component.update_display()

    def update_component_lock_states(self, is_locked):
        self.stats_component.set_locked(is_locked)
        self.energy_component.set_locked(is_locked)
        self.experience_component.set_locked(is_locked)
        self.tab_widget.widget(1).set_locked(is_locked)  # Arts tab
        self.tab_widget.widget(2).set_locked(is_locked)  # Traits tab

        # Enable or disable tabs based on lock state
        self.tab_widget.setEnabled(is_locked)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit', 'Are you sure you want to exit?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Save current character data before exiting
            self.progression_component.save_current_character_data()
            event.accept()
        else:
            event.ignore()
