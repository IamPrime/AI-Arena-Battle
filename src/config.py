import os
from typing import Optional

class Config:
    def __init__(self):
        self.mongo_uri = self._get_required_env("MONGO_URI")
        self.api_key = self._get_required_env("API_KEY")
        self.show_debug = os.getenv("SHOW_DEBUG", "false").lower() == "true"
        
        # Optional: Environment detection
        self.environment = os.getenv("ENVIRONMENT", "production").lower()
        self.is_production = self.environment == "production"
        self.is_development = self.environment == "development"
    
    def _get_required_env(self, key: str) -> Optional[str]:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value