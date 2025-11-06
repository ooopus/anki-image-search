# state.py - Application State Management

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config.types import AppConfig

# Global singleton instance
_app_state: AppState | None = None


class AppState:
    """Singleton class to manage application state"""

    def __init__(self, config: AppConfig):
        self.config = config

    def update_and_save_config(self, new_config: AppConfig):
        """Update configuration and save to file"""
        self.config = new_config
        from .config.config import save_config

        save_config(new_config)


def get_app_state() -> AppState:
    """Get or create the global AppState instance"""
    global _app_state
    if _app_state is None:
        from .config.config import load_config

        config = load_config()
        _app_state = AppState(config)
    return _app_state


def get_config() -> AppConfig:
    """Get current configuration"""
    return get_app_state().config


def update_config_value(key: str, value):
    """Update a single configuration value"""
    app_state = get_app_state()
    new_config = replace(app_state.config, **{key: value})
    app_state.update_and_save_config(new_config)


def reset_app_state():
    """Reset the global app state (mainly for testing)"""
    global _app_state
    _app_state = None
