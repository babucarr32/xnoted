import json
from pathlib import Path
from typing import Any, Dict, List

class Storage():
    def __init__(self, path: str):
        self.path = path

    def save(self, data: Dict[str, Any]):
        try:
            with open(self.path, "w") as f:
                json.dump([data], f, indent=2)
        except Exception as e:
            print(f"Error saving data {e}")

    def load(self) -> List[Dict[str, Any]]:
        try:
            file_path = Path(self.path)
            if (file_path.exists()):
                with open(file_path, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading db {e}")

    def append(self, data: Dict[str, Any]):
        db = self.load()
        db.append(data)

        try:
            with open(self.path, "w") as f:
                json.dump(db, f, indent=2)
        except Exception as e:
            print(f"Error updating data {e}")

    def is_storage_exist(self) -> bool:
        return isinstance(self.load(), list)
