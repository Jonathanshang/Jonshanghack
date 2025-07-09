import os
import json
from typing import Dict, Any

class Config:
    """Configuration management for the Competitive Analysis Tool"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize configuration with default values and load from file if exists
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = config_file
        
        # Default configuration values
        self.defaults = {
            # API Configuration
            "openai_api_key": "",
            "google_api_key": "",
            "google_search_engine_id": "",
            "serp_api_key": "",
            
            # Analysis Settings
            "max_search_results": 50,
            "request_timeout": 30,
            "rate_limit_delay": 1.0,
            "max_retries": 3,
            
            # Scraping Settings
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "max_pages_per_site": 10,
            "scraping_delay": 2.0,
            "bypass_robots_txt": False,  # Allow bypassing robots.txt for competitive analysis
            "respect_robots_txt": True,  # Deprecated - use bypass_robots_txt instead
            
            # Social Media Settings
            "social_platforms": [
                "facebook.com",
                "twitter.com",
                "youtube.com",
                "instagram.com",
                "linkedin.com",
                "reddit.com"
            ],
            "review_sites": [
                "g2.com",
                "capterra.com",
                "trustpilot.com",
                "glassdoor.com"
            ],
            
            # LLM Settings
            "model_name": "gpt-4",
            "max_tokens": 8000,
            "temperature": 0.3,
            "analysis_chunks": 5,
            
            # Report Settings
            "report_formats": ["pdf", "json", "excel"],
            "include_charts": True,
            "include_raw_data": False,
            
            # Logging Settings
            "log_level": "INFO",
            "log_file": "competitive_analysis.log",
            "log_rotation": True,
            "log_max_size": "10MB",
            
            # Application Settings
            "debug_mode": False,
            "cache_duration": 3600,  # 1 hour in seconds
            "output_directory": "outputs",
            "data_directory": "data"
        }
        
        self.config = self.defaults.copy()
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file if it exists"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
                print("Using default configuration")
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Error: Could not save config file {self.config_file}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        self.config[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        self.config.update(updates)
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self.config = self.defaults.copy()
    
    # Convenience properties for commonly used settings
    @property
    def openai_api_key(self) -> str:
        return self.config.get("openai_api_key", "")
    
    @property
    def google_api_key(self) -> str:
        return self.config.get("google_api_key", "")
    
    @property
    def max_search_results(self) -> int:
        return self.config.get("max_search_results", 50)
    
    @property
    def request_timeout(self) -> int:
        return self.config.get("request_timeout", 30)
    
    @property
    def rate_limit_delay(self) -> float:
        return self.config.get("rate_limit_delay", 1.0)
    
    @property
    def user_agent(self) -> str:
        return self.config.get("user_agent", "")
    
    @property
    def model_name(self) -> str:
        return self.config.get("model_name", "gpt-4")
    
    @property
    def max_tokens(self) -> int:
        return self.config.get("max_tokens", 8000)
    
    @property
    def temperature(self) -> float:
        return self.config.get("temperature", 0.3)
    
    @property
    def debug_mode(self) -> bool:
        return self.config.get("debug_mode", False)
    
    @property
    def log_level(self) -> str:
        return self.config.get("log_level", "INFO")
    
    @property
    def log_file(self) -> str:
        return self.config.get("log_file", "competitive_analysis.log")
    
    @property
    def output_directory(self) -> str:
        return self.config.get("output_directory", "outputs")
    
    @property
    def data_directory(self) -> str:
        return self.config.get("data_directory", "data")
    
    @property
    def bypass_robots_txt(self) -> bool:
        return self.config.get("bypass_robots_txt", False)
    
    @property
    def scraping_delay(self) -> float:
        return self.config.get("scraping_delay", 2.0)
    
    def create_directories(self) -> None:
        """Create necessary directories if they don't exist"""
        directories = [self.output_directory, self.data_directory]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def __str__(self) -> str:
        """String representation of the configuration"""
        return json.dumps(self.config, indent=2) 