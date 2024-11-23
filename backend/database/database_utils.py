import json
from typing import Dict, Any

def validate_stat_entry(stat_entry: Dict[str, Any]) -> bool:
    """
    Validate the structure of a stat entry.
    """
    required_keys = ['level', 'experience', 'stats', 'arts', 'traits']
    return all(key in stat_entry for key in required_keys)

def create_diff(old_stats: Dict[str, Any], new_stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a diff between two stat entries.
    """
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
    """
    Apply a diff to a base stat entry.
    """
    result = base_stats.copy()
    for key, value in diff.items():
        if isinstance(value, dict):
            result[key] = apply_diff(result.get(key, {}), value)
        else:
            result[key] = value
    return result
