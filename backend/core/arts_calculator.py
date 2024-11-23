from PyQt5.QtCore import QObject, pyqtSignal
from .base_calculator import BaseCalculator
from .core_utils import (calculate_quality_multiplier, calculate_mastery_multiplier,
                         calculate_adjustment_multiplier, calculate_triangular_number)

class ArtsCalculator(QObject):
    calculation_updated = pyqtSignal(dict)
    arts_updated = pyqtSignal()

    def __init__(self, stats_calculator, experience_calculator):
        super().__init__()
        self.base_calculator = BaseCalculatorImplementation()
        self.stats_calculator = stats_calculator
        self.experience_calculator = experience_calculator
        self.arts = {}
        self.primary_stats = stats_calculator.primary_totals
        stats_calculator.stats_updated.connect(self.update_stats)

    def reset(self):
        self.arts = {}
        self.arts_updated.emit()

    def add_art(self, name, art_type, quality, quality_level, notes):
        art = {
            'name': name,
            'type': art_type,
            'quality': quality,
            'quality_level': quality_level,
            'notes': notes
        }
        self.arts[name] = art
        self.arts_updated.emit()
        return art

    def remove_art(self, name):
        if name in self.arts:
            del self.arts[name]
            self.arts_updated.emit()

    def update_art(self, old_name, new_name, art_type, quality, quality_level, notes):
        if old_name in self.arts:
            del self.arts[old_name]
        self.add_art(new_name, art_type, quality, quality_level, notes)

    def get_art(self, name):
        return self.arts.get(name)

    def calculate(self, art_name):
        art = self.get_art(art_name)
        if not art:
            return None

        try:
            mastery_exp = self.experience_calculator.get_experience("mastery", art_name)
            mastery_level = mastery_exp['level']
            mastery_layer = self.experience_calculator.get_mastery_layer(mastery_level)
            mastery_level_in_layer = self.experience_calculator.get_mastery_level(mastery_level)

            realm = self.stats_calculator.get_realm()
            total_stat = sum(self.primary_stats.values())
            relevant_stat = self.calculate_relevant_stats(art['type'])
            ratio = relevant_stat / total_stat if total_stat != 0 else 0
            quality_multiplier = calculate_quality_multiplier(art['quality'], art['quality_level'])
            mastery_multiplier = calculate_mastery_multiplier(mastery_level)
            initial_boost = quality_multiplier * mastery_multiplier * ratio
            adjustment_multiplier = calculate_adjustment_multiplier(art['quality'], mastery_level, realm)
            final_boost = initial_boost * adjustment_multiplier

            results = {
                'realm': realm,
                'relevant_stat': relevant_stat,
                'total_stat': total_stat,
                'ratio': ratio,
                'quality_multiplier': quality_multiplier,
                'mastery_multiplier': mastery_multiplier,
                'initial_boost': initial_boost,
                'adjustment_multiplier': adjustment_multiplier,
                'final_boost': final_boost,
                'mastery_level': mastery_level,
                'mastery_layer': mastery_layer,
                'mastery_level_in_layer': mastery_level_in_layer
            }
        except Exception as e:
            print(f"Error calculating art {art_name}: {str(e)}")
            results = {
                'realm': 0,
                'relevant_stat': 0,
                'total_stat': 0,
                'ratio': 0,
                'quality_multiplier': 0,
                'mastery_multiplier': 0,
                'initial_boost': 0,
                'adjustment_multiplier': 0,
                'final_boost': 0,
                'mastery_level': 1,
                'mastery_layer': 'Initial Step',
                'mastery_level_in_layer': 1
            }

        self.calculation_updated.emit(results)
        return results

    def calculate_relevant_stats(self, art_type):
        if art_type == "Martial":
            return self.primary_stats["Body"]
        elif art_type == "Spiritual":
            return self.primary_stats["Spirit"]
        elif art_type == "Psychic":
            return self.primary_stats["Mind"]
        elif art_type == "Bloodline":
            return (self.primary_stats["Body"] * 0.5 +
                    self.primary_stats["Spirit"] * 0.3 +
                    self.primary_stats["Mind"] * 0.2)
        elif art_type == "Auxiliary":
            return (self.primary_stats["Mind"] * 0.5 +
                    self.primary_stats["Spirit"] * 0.3 +
                    self.primary_stats["Body"] * 0.2)
        elif art_type == "Arcane":
            return (self.primary_stats["Spirit"] * 0.5 +
                    self.primary_stats["Mind"] * 0.3 +
                    self.primary_stats["Body"] * 0.2)
        elif art_type == "Cultivation":
            return max(self.primary_stats.values())
        else:  # Mixed
            return sum(self.primary_stats.values()) / 3

    def update_stats(self):
        self.primary_stats = self.stats_calculator.primary_totals
        for art_name in self.arts:
            self.calculate(art_name)

    def load_arts(self, arts_data):
        if not arts_data:
            return
        self.arts = arts_data
        for art_name in self.arts:
            self.calculate(art_name)
        self.arts_updated.emit()

    def get_arts(self):
        return self.arts

class BaseCalculatorImplementation(BaseCalculator):
    def calculate(self):
        pass

    def update(self, *args, **kwargs):
        pass
