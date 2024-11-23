from PyQt5.QtCore import QObject, pyqtSignal
from .base_calculator import BaseCalculator
from .core_utils import get_mastery_layer, get_mastery_level

class ExperienceCalculator(QObject):
    experience_updated = pyqtSignal(str, str, int, int)
    level_up = pyqtSignal(str, str, int)
    character_level_up = pyqtSignal(int, str)
    max_level_reached = pyqtSignal(str, str)
    MAX_LEVEL = 100

    def __init__(self, stats_calculator):
        super().__init__()
        self.base_calculator = BaseCalculatorImplementation()
        self.stats_calculator = stats_calculator
        self.experience = {
            "character": {"character": {"exp": 0, "level": 0}},  # Changed initial level to 0
            "mastery": {},
            "trait": {},
        }
        self.level_up_order = ["Body", "Spirit", "Mind"]
        self.initial_stat_index = 0
        self.reset()


    def reset(self):
        self.experience = {
            "character": {"character": {"exp": 0, "level": 0}},
            "mastery": {},
            "trait": {},
        }

    def set_initial_stat(self, stat):
        if stat not in self.level_up_order:
            raise ValueError(f"Invalid initial stat: {stat}")
        self.initial_stat_index = self.level_up_order.index(stat)

    def get_current_level_up_index(self):
        char_level = self.get_level("character")
        return (self.initial_stat_index + char_level) % 3

    def add_experience(self, exp_type, amount, identifier="character"):
        if exp_type not in self.experience:
            raise ValueError(f"Invalid experience type: {exp_type}")

        if exp_type == "character":
            identifier = "character"
        
        if identifier not in self.experience[exp_type]:
            self.experience[exp_type][identifier] = {"exp": 0, "level": 1}
        
        return self._add_exp_and_level_up(exp_type, identifier, amount)

    def _add_exp_and_level_up(self, exp_type, identifier, amount):
        exp_data = self.experience[exp_type][identifier]
        original_level = exp_data["level"]
        exp_data["exp"] += amount
        
        if amount >= 0:
            while exp_data["level"] < self.MAX_LEVEL:
                max_exp = self.calculate_max_exp(exp_data["level"])
                if exp_data["exp"] >= max_exp:
                    exp_data["exp"] -= max_exp
                    exp_data["level"] += 1
                    self.level_up.emit(exp_type, identifier, exp_data["level"])
                    if exp_type == "character" and identifier == "character":
                        current_stat_index = (self.initial_stat_index + exp_data["level"] - 1) % 3
                        current_stat = self.level_up_order[current_stat_index]
                        self.character_level_up.emit(exp_data["level"], current_stat)
                else:
                    break
            
            if exp_data["level"] == self.MAX_LEVEL:
                exp_data["exp"] = min(exp_data["exp"], self.calculate_max_exp(self.MAX_LEVEL) - 1)
                if original_level != self.MAX_LEVEL:
                    self.max_level_reached.emit(exp_type, identifier)

        next_level_exp = self.calculate_max_exp(exp_data["level"])
        self.experience_updated.emit(exp_type, identifier, exp_data["exp"], next_level_exp)
        return exp_data["level"] == self.MAX_LEVEL and amount > 0

    def set_experience(self, exp_type, amount, identifier):
        if exp_type not in self.experience:
            raise ValueError(f"Invalid experience type: {exp_type}")
        
        if exp_type == "trait":
            self.experience[exp_type][identifier] = {"exp": amount, "level": 1}
            self.experience_updated.emit(exp_type, identifier, amount, self.calculate_max_exp(1))
        else:
            raise ValueError(f"set_experience is only supported for traits")

    def remove_experience(self, exp_type, identifier):
        if exp_type not in self.experience:
            raise ValueError(f"Invalid experience type: {exp_type}")
        
        if identifier in self.experience[exp_type]:
            del self.experience[exp_type][identifier]
            self.experience_updated.emit(exp_type, identifier, 0, 0)

    def calculate_max_exp(self, level):
        if level == 0:
            return 10
        elif level <= 10:
            return level * 100
        else:
            tier = (level - 1) // 10
            base = 10 ** (tier + 2)
            level_in_tier = (level - 1) % 10 + 1
            return base * level_in_tier

    def get_level(self, exp_type, identifier=None):
        if exp_type not in self.experience:
            raise ValueError(f"Invalid experience type: {exp_type}")
        
        if exp_type == "character":
            return self.experience["character"]["character"]["level"]
        else:
            return self.experience[exp_type].get(identifier, {"level": 1})["level"]

    def get_experience(self, exp_type, identifier=None):
        if exp_type not in self.experience:
            raise ValueError(f"Invalid experience type: {exp_type}")
        
        if exp_type == "character":
            return self.experience["character"]["character"]
        else:
            return self.experience[exp_type].get(identifier, {"exp": 0, "level": 1})

    def get_mastery_layer(self, level):
        return get_mastery_layer(level)

    def get_mastery_level(self, level):
        return get_mastery_level(level)

    def load_experience(self, experience_data):
        if not experience_data:
            self.reset()
            return
        self.experience = experience_data
        self.experience_updated.emit("character", "character", 
                                     self.experience["character"]["character"]["exp"], 
                                     self.calculate_max_exp(self.experience["character"]["character"]["level"]))

    def get_all_experience(self):
        return self.experience

class BaseCalculatorImplementation(BaseCalculator):
    def calculate(self):
        pass

    def update(self, *args, **kwargs):
        pass
