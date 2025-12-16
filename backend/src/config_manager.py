import json
import os
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".rubber_duck"
        self.config_file = self.config_dir / "config.json"
        self.projects_file = self.config_dir / "projects.json"
        self._ensure_config_dir()
        self.config = self._load_config()
        self.projects = self._load_projects()
    
    def _ensure_config_dir(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> dict:
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._default_config()
    
    def _load_projects(self) -> dict:
        if self.projects_file.exists():
            with open(self.projects_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"projects": [], "active_project": None}
    
    def _default_config(self) -> dict:
        return {
            "push_to_talk_key": "ctrl+shift+d",
            "language": "pl",
            "llm_provider": "claude",
            "tts_enabled": True,
            "duck_position": "bottom_left",
            "duck_size": 120,
            "api_keys": {
                "anthropic": "",
                "google": "",
                "elevenlabs": ""
            }
        }
    
    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def save_projects(self):
        with open(self.projects_file, 'w', encoding='utf-8') as f:
            json.dump(self.projects, f, indent=2, ensure_ascii=False)
    
    def add_project(self, project: dict):
        self.projects["projects"].append(project)
        self.save_projects()
    
    def remove_project(self, project_name: str):
        self.projects["projects"] = [
            p for p in self.projects["projects"] 
            if p["name"] != project_name
        ]
        if self.projects["active_project"] == project_name:
            self.projects["active_project"] = None
        self.save_projects()
    
    def set_active_project(self, project_name: str):
        self.projects["active_project"] = project_name
        self.save_projects()
    
    def get_active_project(self) -> dict | None:
        if not self.projects["active_project"]:
            return None
        for p in self.projects["projects"]:
            if p["name"] == self.projects["active_project"]:
                return p
        return None
    
    def update_project(self, project_name: str, updated_data: dict):
        for i, p in enumerate(self.projects["projects"]):
            if p["name"] == project_name:
                self.projects["projects"][i].update(updated_data)
                break
        self.save_projects()
    
    def get_api_key(self, provider: str) -> str:
        return self.config.get("api_keys", {}).get(provider, "")
    
    def set_api_key(self, provider: str, key: str):
        if "api_keys" not in self.config:
            self.config["api_keys"] = {}
        self.config["api_keys"][provider] = key
        self.save_config()
