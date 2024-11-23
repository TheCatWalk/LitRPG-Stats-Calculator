from PyQt5.QtCore import QObject, pyqtSignal
from .base_calculator import BaseCalculator

class StatsCalculator(QObject):
    stats_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.base_calculator = BaseCalculatorImplementation()
        self.primary_stats = {
            "Body": ["Endurance", "Vitality", "Strength", "Agility", "Dexterity"],
            "Mind": ["Intelligence", "Memory", "Perception", "Clarity", "Focus"],
            "Spirit": ["Adaptability", "Magnitude", "Density", "Purity", "Fortitude"]
        }
        self.reset()

    def reset(self):
        self.stats = {stat: {"auto": 1, "free": 0, "train": 0, "weight": 0.20, "constraint": 20.00, "total": 1}
                      for primary in self.primary_stats.values() for stat in primary}
        self.primary_totals = {primary: 1.0 for primary in self.primary_stats}
        self.free_points = 0
        self.train_points = 0
        self.level = 0
        self.calculate()

    def calculate(self):
        for primary, secondary_stats in self.primary_stats.items():
            total_points = sum(sum(self.stats[stat][cat] for cat in ['auto', 'free', 'train']) for stat in secondary_stats)
            total_manual_auto_points = sum(self.stats[stat]['auto'] + self.stats[stat]['free'] for stat in secondary_stats)
            primary_total = 0

            for stat in secondary_stats:
                auto = self.stats[stat]['auto']
                free = self.stats[stat]['free']
                train = self.stats[stat]['train']
                total = auto + free + train

                weight = (auto + free) / total_manual_auto_points if total_manual_auto_points > 0 else 0
                normalized_weight = weight / sum((self.stats[s]['auto'] + self.stats[s]['free']) / total_manual_auto_points
                                                 for s in secondary_stats) if total_manual_auto_points > 0 else 0

                self.stats[stat]['weight'] = weight
                self.stats[stat]['total'] = total
                self.stats[stat]['constraint'] = (total / total_points) * 100 if total_points > 0 else 0

                primary_total += total * normalized_weight

            self.primary_totals[primary] = primary_total
        
        self.stats_updated.emit()

    def update(self, stat, category, change):
        if category == 'free':
            if self.free_points - change < 0 or self.stats[stat][category] + change < 0:
                return False
            self.free_points -= change
        elif category == 'train':
            if self.train_points - change < 0 or self.stats[stat][category] + change < 0:
                return False
            self.train_points -= change
        
        self.stats[stat][category] += change
        self.calculate()
        return True

    def handle_level_up(self, new_level, primary):
        levels_gained = new_level - self.level
        for _ in range(levels_gained):
            for stat in self.primary_stats[primary]:
                self.stats[stat]['auto'] += 1
            
            self.free_points += 5
            self.train_points += 5

        self.level = new_level
        self.calculate()

    def get_realm(self):
        return (self.level - 1) // 10 + 1

    def load_stats(self, stats_data):
        if not stats_data:
            self.reset()
            return
        self.stats = stats_data.get('stats', self.stats)
        self.primary_totals = stats_data.get('primary_totals', self.primary_totals)
        self.free_points = stats_data.get('free_points', self.free_points)
        self.train_points = stats_data.get('train_points', self.train_points)
        self.level = stats_data.get('level', self.level)
        self.calculate()
        self.stats_updated.emit()

    def get_stats(self):
        return {
            'stats': self.stats,
            'primary_totals': self.primary_totals,
            'free_points': self.free_points,
            'train_points': self.train_points,
            'level': self.level
        }

class BaseCalculatorImplementation(BaseCalculator):
    def calculate(self):
        pass

    def update(self, *args, **kwargs):
        pass
