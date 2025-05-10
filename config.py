import json
import os
from typing import Dict, Any

class Config:
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            self.config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        else:
            self.config_path = config_path
        
        self.config_data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load config file: {str(e)}")
    
    def get(self, key: str, default=None) -> Any:
        return self.config_data.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        return self.config_data[key]
    
    @property
    def mongo_uri(self) -> str:
        return self.config_data.get("MONGO_URI", "mongodb://localhost:27017/")
    
    @property
    def db_name(self) -> str:
        return self.config_data.get("DB_NAME", "video_database")
    
    @property
    def collection_name(self) -> str:
        return self.config_data.get("COLLECTION_NAME", "video_frames")
    
    @property
    def api_key(self) -> str:
        return self.config_data.get("api_key", "")
    
    @property
    def base_url(self) -> str:
        return self.config_data.get("base_url", "")
    
    @property
    def embed_model(self) -> str:
        return self.config_data.get("embed_model", "")
    
    @property
    def llm_model(self) -> str:
        return self.config_data.get("llm_model", "")
    
    @property
    def hf_token(self) -> str:
        return self.config_data.get("hf_token", "")


config = Config()

if __name__ == "__main__":
    print("MongoDB URI:", config.mongo_uri)
    print("Database Name:", config.db_name)
    print("Collection Name:", config.collection_name)
    print("API Key:", config.api_key)
    print("Base URL:", config.base_url)
    print("Embedding Model:", config.embed_model)
    print("LLM Model:", config.llm_model)
    
    print("Get HF Token using get method:", config.get("hf_token", "default value"))
    
    print("Access API Key using dictionary style:", config["api_key"])