from PyQt5.QtCore import QObject, pyqtSignal
from .base_calculator import BaseCalculator
from .core_utils import calculate_max_exp

class Trait:
    def __init__(self, name, quality_grade, quality_level=1):
        self.name = name
        self.quality_grade = quality_grade
        self.quality_level = quality_level
        self.exp = 0
        self.notes = ""

class TraitsCalculator(QObject):
    traits_updated = pyqtSignal()
    exp_updated = pyqtSignal(int, int, int)  # trait_index, current_exp, max_exp

    def __init__(self, experience_calculator):
        super().__init__()
        self.base_calculator = BaseCalculatorImplementation()
        self.experience_calculator = experience_calculator
        self.traits = []

    def reset(self):
        self.traits = []
        self.traits_updated.emit()

    def create_trait(self, name, quality_grade, quality_level):
        return Trait(name, quality_grade, quality_level)

    def add_trait(self, trait):
        if isinstance(trait, Trait):
            # Check if a trait with the same name already exists
            existing_trait_index = next((index for index, t in enumerate(self.traits) if t.name == trait.name), None)
            if existing_trait_index is not None:
                # Replace the existing trait
                self.traits[existing_trait_index] = trait
            else:
                # Add new trait
                self.traits.append(trait)
            self.traits_updated.emit()

    def remove_trait(self, index):
        if 0 <= index < len(self.traits):
            del self.traits[index]
            self.traits_updated.emit()

    def update_trait(self, index, **kwargs):
        if 0 <= index < len(self.traits):
            trait = self.traits[index]
            for key, value in kwargs.items():
                setattr(trait, key, value)
            self.traits_updated.emit()

    def get_traits(self):
        return self.traits

    def add_experience(self, trait_index, amount):
        if 0 <= trait_index < len(self.traits):
            trait = self.traits[trait_index]
            trait.exp += amount
            max_exp = calculate_max_exp(trait.quality_level)
            
            while trait.exp >= max_exp and trait.quality_level < 10:
                trait.exp -= max_exp
                trait.quality_level += 1
                max_exp = calculate_max_exp(trait.quality_level)
            
            if trait.quality_level == 10:
                trait.exp = min(trait.exp, max_exp - 1)
            
            self.exp_updated.emit(trait_index, trait.exp, max_exp)
            self.traits_updated.emit()

    def add_experience_percent(self, trait_index, percent):
        if 0 <= trait_index < len(self.traits):
            trait = self.traits[trait_index]
            max_exp = calculate_max_exp(trait.quality_level)
            amount = int(max_exp * percent / 100)
            self.add_experience(trait_index, amount)

    def load_traits(self, traits_data):
        if not traits_data:
            return
        self.traits = [Trait(**trait_dict) for trait_dict in traits_data]
        self.traits_updated.emit()

    def get_traits(self):
        return [trait.__dict__ for trait in self.traits]

class BaseCalculatorImplementation(BaseCalculator):
    def calculate(self):
        pass

    def update(self, *args, **kwargs):
        pass
