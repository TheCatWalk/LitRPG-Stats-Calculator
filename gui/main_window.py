from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from backend.core import CalculatorFactory
from .ui_factory import UIFactory

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.calculator = CalculatorFactory.get_calculator("stats")
        self.components = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("LitRPG Stats Calculator")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Level Up component
        self.components['level_up'] = UIFactory.create_component("level_up", self.calculator)
        self.components['level_up'].levelUpSignal.connect(self.update_all_components)
        main_layout.addWidget(self.components['level_up'])
        
        # Stats component
        self.components['stats'] = UIFactory.create_component("stats", self.calculator)
        main_layout.addWidget(self.components['stats'])

    def update_all_components(self):
        for component in self.components.values():
            component.update_display()