from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout
from .base_component import BaseComponent

class EnergyComponent(BaseComponent):
    def __init__(self, calculator, parent=None):
        self.calculator = calculator
        self.is_locked = False
        super().__init__(parent)

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        energy_layout = QHBoxLayout()
        self.lifeforce_label = QLabel("Lifeforce: 0 + 0 = 0")
        self.qi_label = QLabel("Qi: 0 + 0 = 0")
        self.essence_label = QLabel("Essence: 0 + 0 = 0")
        
        energy_layout.addWidget(self.lifeforce_label)
        energy_layout.addWidget(self.qi_label)
        energy_layout.addWidget(self.essence_label)
        
        layout.addLayout(energy_layout)
        
        self.calculator.energy_updated.connect(self.update_display)

    def update_display(self):
        energy_values = self.calculator.get_energy_values()
        self.lifeforce_label.setText(f"Lifeforce: {energy_values['Lifeforce']['initial']} + {energy_values['Lifeforce']['adjustment']} = {energy_values['Lifeforce']['final']}")
        self.qi_label.setText(f"Qi: {energy_values['Qi']['initial']} + {energy_values['Qi']['adjustment']} = {energy_values['Qi']['final']}")
        self.essence_label.setText(f"Essence: {energy_values['Essence']['initial']} + {energy_values['Essence']['adjustment']} = {energy_values['Essence']['final']}")
        self.update_ui_state()

    def set_locked(self, locked):
        self.is_locked = locked
        self.update_ui_state()

    def update_ui_state(self):
        # You can add any UI elements that need to be enabled/disabled based on the lock state
        pass

