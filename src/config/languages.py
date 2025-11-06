# config/languages.py - Language Code Enum

from enum import Enum


class LanguageCode(str, Enum):
    """Supported language codes for translation"""

    AUTO = "auto"
    EN_US = "en_US"
    ZH_CN = "zh_CN"

    def __str__(self):
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "LanguageCode":
        """Convert string to LanguageCode enum"""
        try:
            return cls(value)
        except ValueError:
            return cls.AUTO
