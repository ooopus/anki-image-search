# config/config.py - Configuration Management

import json
from pathlib import Path

from .constants import CONFIG_FILE_PATH, USER_FILES_DIR
from .types import AppConfig


def load_config() -> AppConfig:
    """Load configuration from file or return default"""
    # Ensure user_files directory exists
    USER_FILES_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE_PATH.exists():
        # Create default config
        config = AppConfig()
        save_config(config)
        return config

    try:
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return AppConfig.from_dict(data)
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        # If config is corrupted, return default
        print(f"Error loading config: {e}")
        return AppConfig()


def save_config(config: AppConfig):
    """Save configuration to file"""
    USER_FILES_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving config: {e}")
