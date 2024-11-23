from typing import Dict, Any

def calculate_triangular_number(n: int) -> int:
    return n * (n + 1) // 2

def calculate_max_exp(level: int) -> int:
    if level <= 10:
        return level * 100
    else:
        tier = (level - 1) // 10
        base = 10 ** (tier + 2)
        level_in_tier = (level - 1) % 10 + 1
        return base * level_in_tier

def get_mastery_layer(level: int) -> str:
    mastery_layers = [
        "Initial Step", "Blossoming Path", "Grasping Intent", "Lesser Mastery", "Grand Completion",
        "Shaping Insight", "Law Crystal", "Forged Apotheosis", "Karmic Liberation", "Absolute Truth"
    ]
    return mastery_layers[(level - 1) // 10]

def get_mastery_level(level: int) -> int:
    return ((level - 1) % 10) + 1

def calculate_quality_multiplier(quality: str, quality_level: int) -> float:
    quality_grades = {
        "Mortal Grade": 1, "Elite Grade": 2, "Earth Grade": 3, "Royal Grade": 4, "Imperial Grade": 5,
        "Saint Grade": 6, "Sky Grade": 7, "Ascended Grade": 8, "Transcended Grade": 9, "Eternal Grade": 10
    }
    current_grade = quality_grades.get(quality, 1)
    next_grade = min(current_grade + 1, 10)
    return current_grade + ((next_grade - current_grade) / 10) * quality_level

def calculate_mastery_multiplier(mastery_level: int) -> float:
    current_layer = (mastery_level - 1) // 10 + 1
    next_layer = min(current_layer + 1, 10)
    T_current = calculate_triangular_number(current_layer)
    T_next = calculate_triangular_number(next_layer)
    level_in_layer = (mastery_level - 1) % 10 + 1
    return T_current + ((T_next - T_current) / 10) * level_in_layer

def calculate_adjustment_multiplier(quality: str, mastery_level: int, realm: int) -> float:
    quality_grades = {
        "Mortal Grade": 1, "Elite Grade": 2, "Earth Grade": 3, "Royal Grade": 4, "Imperial Grade": 5,
        "Saint Grade": 6, "Sky Grade": 7, "Ascended Grade": 8, "Transcended Grade": 9, "Eternal Grade": 10
    }
    grade_num = quality_grades.get(quality, 1)
    mastery_layer_num = (mastery_level - 1) // 10 + 1
    return 1 + ((realm - grade_num) / 10) + (mastery_layer_num / 10)

def format_number(number: int, show_exact: bool = False) -> str:
    if show_exact:
        return f"{number:,}"
    elif number < 1000:
        return str(number)
    elif number < 1000000:
        return f"{number/1000:.1f}K"
    elif number < 1000000000:
        return f"{number/1000000:.1f}M"
    else:
        return f"{number/1000000000:.1f}B"

def validate_stat_entry(stat_entry: Dict[str, Any]) -> bool:
    required_keys = ['level', 'experience', 'stats', 'arts', 'traits']
    return all(key in stat_entry for key in required_keys)

def create_diff(old_stats: Dict[str, Any], new_stats: Dict[str, Any]) -> Dict[str, Any]:
    diff = {}
    for key, value in new_stats.items():
        if key not in old_stats or old_stats[key] != value:
            if isinstance(value, dict):
                nested_diff = create_diff(old_stats.get(key, {}), value)
                if nested_diff:
                    diff[key] = nested_diff
            else:
                diff[key] = value
    return diff

def apply_diff(base_stats: Dict[str, Any], diff: Dict[str, Any]) -> Dict[str, Any]:
    result = base_stats.copy()
    for key, value in diff.items():
        if isinstance(value, dict):
            result[key] = apply_diff(result.get(key, {}), value)
        else:
            result[key] = value
    return result
