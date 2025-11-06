# config/enums.py - Configuration Enums

from enum import Enum


class ImageQuality(str, Enum):
    """Image quality settings"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    def __str__(self):
        return self.value


class ImageFormat(str, Enum):
    """Image format options for conversion"""

    ORIGINAL = "original"  # Keep original format
    WEBP = "webp"
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"

    def __str__(self):
        return self.value


class StatusBarFormat(str, Enum):
    """Status bar display format"""

    ICON_ONLY = "{icon}"
    ICON_STATUS = "{icon} {status}"
    FULL = "{icon} {status} - {count} images"

    def __str__(self):
        return self.value
