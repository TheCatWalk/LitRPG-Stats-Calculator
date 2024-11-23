from PyQt5.QtCore import QObject, pyqtSignal
from .base_calculator import BaseCalculator

class EnergyCalculator(QObject):
    energy_updated = pyqtSignal()

    def __init__(self, stats_calculator):
        super().__init__()
        self.stats_calculator = stats_calculator
        self.realm_multipliers = {
            1: 1, 2: 3, 3: 6, 4: 10, 5: 15, 6: 21, 7: 28, 8: 36, 9: 45, 10: 55
        }
        self.lifeforce = {'initial': 0, 'adjustment': 0, 'final': 0}
        self.qi = {'initial': 0, 'adjustment': 0, 'final': 0}
        self.essence = {'initial': 0, 'adjustment': 0, 'final': 0}
        self.stats_calculator.stats_updated.connect(self.calculate)

    def reset(self):
        self.lifeforce = {'initial': 0, 'adjustment': 0, 'final': 0}
        self.qi = {'initial': 0, 'adjustment': 0, 'final': 0}
        self.essence = {'initial': 0, 'adjustment': 0, 'final': 0}
        self.calculate()

    def calculate(self):
        body = self.stats_calculator.primary_totals['Body']
        mind = self.stats_calculator.primary_totals['Mind']
        spirit = self.stats_calculator.primary_totals['Spirit']
        
        realm = self.stats_calculator.get_realm()
        multiplier = self.realm_multipliers.get(realm, 1.0)
        
        self.lifeforce['initial'] = int(body * 100 * multiplier)
        self.qi['initial'] = int(spirit * 50 * multiplier)
        self.essence['initial'] = int(mind * 20 * multiplier)
        
        vitality_weight = self.stats_calculator.stats['Vitality']['weight']
        magnitude_weight = self.stats_calculator.stats['Magnitude']['weight']
        memory_weight = self.stats_calculator.stats['Memory']['weight']
        
        self.lifeforce['adjustment'] = int(self.lifeforce['initial'] * vitality_weight)
        self.qi['adjustment'] = int(self.qi['initial'] * magnitude_weight)
        self.essence['adjustment'] = int(self.essence['initial'] * memory_weight)
        
        self.lifeforce['final'] = self.lifeforce['initial'] + self.lifeforce['adjustment']
        self.qi['final'] = self.qi['initial'] + self.qi['adjustment']
        self.essence['final'] = self.essence['initial'] + self.essence['adjustment']
        
        self.energy_updated.emit()

    def load_energy(self, energy_data):
        if not energy_data:
            return
        self.lifeforce = energy_data.get('Lifeforce', self.lifeforce)
        self.qi = energy_data.get('Qi', self.qi)
        self.essence = energy_data.get('Essence', self.essence)
        self.energy_updated.emit()

    def get_energy_values(self):
        return {
            'Lifeforce': self.lifeforce,
            'Qi': self.qi,
            'Essence': self.essence
        }

class BaseCalculatorImplementation(BaseCalculator):
    def calculate(self):
        pass

    def update(self, *args, **kwargs):
        pass
