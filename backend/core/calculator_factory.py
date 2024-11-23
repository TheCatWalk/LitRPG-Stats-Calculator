from .stats_calculator import StatsCalculator
from .energy_calculator import EnergyCalculator
from .experience_calculator import ExperienceCalculator
from .arts_calculator import ArtsCalculator
from .traits_calculator import TraitsCalculator
from ..database.character_database import CharacterDatabase

class CalculatorFactory:
    @staticmethod
    def get_calculator(calculator_type, *args, **kwargs):
        if calculator_type == "stats":
            return StatsCalculator()
        elif calculator_type == "energy":
            return EnergyCalculator(*args, **kwargs)
        elif calculator_type == "arts":
            return ArtsCalculator(*args, **kwargs)
        elif calculator_type == "experience":
            return ExperienceCalculator(*args, **kwargs)
        elif calculator_type == "traits":
            return TraitsCalculator(*args, **kwargs)
        elif calculator_type == "character_database":
            return CharacterDatabase(*args, **kwargs)
        else:
            raise ValueError(f"Unknown calculator type: {calculator_type}")
