import json
import os

class SetManager:
    def __init__(self):
        self.sets = {}
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pdfcoverSetts.json")
        self.load_sets()
    
    def load_sets(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.sets = json.load(f)
        else:
            self.sets = {}
    
    def save_set(self, set_name, set_data):
        self.sets[set_name] = set_data
        self._save_to_file()
    
    def _save_to_file(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.sets, f, ensure_ascii=False, indent=4)
        print(f"Saved sets to {self.config_path}")  # デバッグ用出力