import os
import json
from typing import Dict, Any, Optional, Tuple

class ConfigManager:
    """
    Manages loading, parsing, and storing configurations from users.json.
    """
    def __init__(self, filepath: str = "users.json"):
        self.filepath = filepath
        self.config_data = {}
        self.load()

    def load(self) -> bool:
        """Loads configuration from file."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.config_data = json.load(f)
                return True
            except Exception:
                self.config_data = {}
        return False

    def save(self) -> bool:
        """Saves current configuration to file."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False

    def get_api_base_url(self) -> str:
        """Gets configured API base URL, defaults to official endpoint."""
        return self.config_data.get("api_base_url", "https://api.cloudns.net/")

    def get_profiles(self) -> Dict[str, Dict[str, str]]:
        """Gets all configuration profiles."""
        return self.config_data.get("profiles", {})

    def update_last_used(self, profile_name: str) -> None:
        """Updates the timestamp or last used profile in users.json."""
        import datetime
        profiles = self.get_profiles()
        if profile_name in profiles:
            profiles[profile_name]["last_used_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save()
