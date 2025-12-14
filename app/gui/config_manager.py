"""
Configuration Manager for Python Linter GUI
Handles loading, saving, and default config generation
"""
import json
import os
from pathlib import Path

class ConfigManager:
    """Manages application configuration"""
    
    DEFAULT_CONFIG = {
        "max_function_lines": 20,
        "max_nesting_depth": 5,
        "max_arguments": 3,
        "max_cyclomatic_complexity": 5,
        "parser_errors_enabled": True,
        "naming_convention": {
            "function": "snake_case",
            "class": "PascalCase",
            "variable": "snake_case"
        },
        "semantic_checker": {
            "ignore_pascalcase": False,
            "ignore_uppercase": False,
            "strict_import_tracking": True
        },
        "exclude": [
            "__pycache__",
            "generated"
        ]
    }
    
    def __init__(self, config_path="config.json"):
        """
        Initialize config manager
        
        Args:
            config_path: Path to config file (relative to app directory)
        """
        self.config_path = Path(config_path)
        self.config = None
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                # Merge with defaults to ensure all keys exist
                self.config = self._merge_with_defaults(self.config)
            else:
                # Create default config
                self.config = self.DEFAULT_CONFIG.copy()
                self.save_config()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}. Using defaults.")
            self.config = self.DEFAULT_CONFIG.copy()
            self.save_config()
    
    def _merge_with_defaults(self, config):
        """Merge loaded config with defaults to ensure all keys exist"""
        merged = self.DEFAULT_CONFIG.copy()
        
        # Update with loaded values
        for key, value in config.items():
            if isinstance(value, dict) and key in merged:
                merged[key].update(value)
            else:
                merged[key] = value
        
        return merged
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_config(self):
        """Get current configuration"""
        return self.config
    
    def update_config(self, new_config):
        """Update configuration with new values"""
        self.config = new_config
        return self.save_config()
    
    def add_exclude_pattern(self, pattern):
        """Add a pattern to exclude list"""
        if pattern not in self.config['exclude']:
            self.config['exclude'].append(pattern)
            return self.save_config()
        return True
    
    def remove_exclude_pattern(self, pattern):
        """Remove a pattern from exclude list"""
        if pattern in self.config['exclude']:
            self.config['exclude'].remove(pattern)
            return self.save_config()
        return True
    
    def get_exclude_patterns(self):
        """Get list of exclude patterns"""
        return self.config.get('exclude', [])
