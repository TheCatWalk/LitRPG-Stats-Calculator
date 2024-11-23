from .components.stats_component import StatsComponent
from .components.energy_component import EnergyComponent
from .components.experience_component import ExperienceComponent
from .components.arts_component import ArtsComponent
from .components.traits_component import TraitsComponent
from .components.character_progression_component import CharacterProgressionComponent

class UIFactory:
    @staticmethod
    def create_component(component_type, *args, **kwargs):
        if component_type == "stats":
            return StatsComponent(*args, **kwargs)
        elif component_type == "energy":
            return EnergyComponent(*args, **kwargs)
        elif component_type == "arts":
            if len(args) >= 3:
                return ArtsComponent(args[0], args[1], args[2])
            else:
                raise ValueError("ArtsComponent requires arts_calculator, experience_calculator, and stats_calculator")
        elif component_type == "experience":
            return ExperienceComponent(*args, **kwargs)
        elif component_type == "traits":
            return TraitsComponent(*args, **kwargs)
        elif component_type == "character_progression":
            return CharacterProgressionComponent(*args, **kwargs)
        else:
            raise ValueError(f"Unknown component type: {component_type}")
