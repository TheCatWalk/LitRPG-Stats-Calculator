from .components.stats_component import StatsComponent
from .components.level_up_component import LevelUpComponent

class UIFactory:
    @staticmethod
    def create_component(component_type, *args, **kwargs):
        if component_type == "stats":
            return StatsComponent(*args, **kwargs)
        elif component_type == "level_up":
            return LevelUpComponent(*args, **kwargs)
        # Add more component types here as needed
        else:
            raise ValueError(f"Unknown component type: {component_type}")