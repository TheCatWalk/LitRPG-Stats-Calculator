import json
import os
from typing import Dict, List, Union
from datetime import datetime

class CharacterDatabase:
    def __init__(self, data_directory: str):
        self.data_directory = data_directory
        os.makedirs(data_directory, exist_ok=True)

    def get_character_list(self) -> List[str]:
        return [f for f in os.listdir(self.data_directory) if f.endswith('.json')]

    def create_character(self, character_name: str) -> None:
        file_path = self._get_character_file_path(character_name)
        if os.path.exists(file_path):
            raise ValueError(f"Character {character_name} already exists")
        
        initial_data = {
            "name": character_name,
            "created_at": datetime.now().isoformat(),
            "version": "1.0",
            "chapters": [],
            "stats": {},
            "energy": {},
            "experience": {},
            "arts": {},
            "traits": []
        }
        
        with open(file_path, 'w') as f:
            json.dump(initial_data, f, indent=2)

    def load_character(self, character_name: str) -> Dict:
        file_path = self._get_character_file_path(character_name)
        if not os.path.exists(file_path):
            raise ValueError(f"Character {character_name} does not exist")
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Ensure all required fields are present
        required_fields = ['stats', 'energy', 'experience', 'arts', 'traits']
        for field in required_fields:
            if field not in data:
                data[field] = {}
        
        return data
    def update_character(self, character_name: str, data: Dict) -> None:
        file_path = self._get_character_file_path(character_name)
        if not os.path.exists(file_path):
            raise ValueError(f"Character {character_name} does not exist")
        
        current_data = self.load_character(character_name)
        current_data.update(data)
        
        with open(file_path, 'w') as f:
            json.dump(current_data, f, indent=2)

    def add_chapter(self, character_name: str, chapter_number: int, start_section: str, end_section: str) -> None:
        data = self.load_character(character_name)
        
        new_chapter = {
            "number": chapter_number,
            "start_section": start_section,
            "end_section": end_section,
            "checkpoints": []
        }
        
        data["chapters"].append(new_chapter)
        self._save_character_data(character_name, data)

    def add_checkpoint(self, character_name: str, chapter_number: int, checkpoint_name: str, stats: Dict) -> None:
        data = self.load_character(character_name)
        
        chapter = next((c for c in data["chapters"] if c["number"] == chapter_number), None)
        if not chapter:
            raise ValueError(f"Chapter {chapter_number} not found for character {character_name}")
        
        new_checkpoint = {
            "name": checkpoint_name,
            "timestamp": datetime.now().isoformat(),
            "stats": stats
        }
        
        chapter["checkpoints"].append(new_checkpoint)
        self._save_character_data(character_name, data)

    def get_character_data(self, character_name: str, chapter_number: int = None, checkpoint_name: str = None) -> Dict:
        data = self.load_character(character_name)
        
        if chapter_number is None:
            return data
        
        chapter = next((c for c in data["chapters"] if c["number"] == chapter_number), None)
        if not chapter:
            raise ValueError(f"Chapter {chapter_number} not found for character {character_name}")
        
        if checkpoint_name is None:
            return chapter
        
        checkpoint = next((cp for cp in chapter["checkpoints"] if cp["name"] == checkpoint_name), None)
        if not checkpoint:
            raise ValueError(f"Checkpoint {checkpoint_name} not found in chapter {chapter_number}")
        
        return checkpoint

    def remove_character(self, character_name: str) -> None:
        file_path = self._get_character_file_path(character_name)
        if not os.path.exists(file_path):
            raise ValueError(f"Character {character_name} does not exist")
        
        os.remove(file_path)

    def remove_chapter(self, character_name: str, chapter_number: int) -> None:
        data = self.load_character(character_name)
        
        data["chapters"] = [c for c in data["chapters"] if c["number"] != chapter_number]
        self._save_character_data(character_name, data)

    def remove_checkpoint(self, character_name: str, chapter_number: int, checkpoint_name: str) -> None:
        data = self.load_character(character_name)
        
        chapter = next((c for c in data["chapters"] if c["number"] == chapter_number), None)
        if not chapter:
            raise ValueError(f"Chapter {chapter_number} not found for character {character_name}")
        
        chapter["checkpoints"] = [cp for cp in chapter["checkpoints"] if cp["name"] != checkpoint_name]
        self._save_character_data(character_name, data)

    def _get_character_file_path(self, character_name: str) -> str:
        return os.path.join(self.data_directory, f"{character_name}.json")

    def _save_character_data(self, character_name: str, data: Dict) -> None:
        file_path = self._get_character_file_path(character_name)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def update_checkpoint(self, character_name: str, chapter_number: int, checkpoint_name: str, stats: Dict) -> None:
        data = self.load_character(character_name)
        
        chapter = next((c for c in data["chapters"] if c["number"] == chapter_number), None)
        if not chapter:
            raise ValueError(f"Chapter {chapter_number} not found for character {character_name}")
        
        checkpoint = next((cp for cp in chapter["checkpoints"] if cp["name"] == checkpoint_name), None)
        if not checkpoint:
            raise ValueError(f"Checkpoint {checkpoint_name} not found in chapter {chapter_number}")
        
        checkpoint["stats"] = stats
        checkpoint["timestamp"] = datetime.now().isoformat()
        
        self._save_character_data(character_name, data)

