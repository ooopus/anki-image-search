# config/types.py - Configuration Types

from dataclasses import dataclass, field

from .constants import (
    DEFAULT_CONVERT_FORMAT,
    DEFAULT_FFMPEG_QUALITY,
    DEFAULT_IMAGE_FORMAT,
    DEFAULT_IMAGE_QUALITY,
    DEFAULT_MAX_RESULTS,
    DEFAULT_SEARCH_FIELD,
    DEFAULT_TARGET_FIELD,
)
from .enums import ImageFormat, ImageQuality
from .languages import LanguageCode


@dataclass
class NoteTypeTemplate:
    """Configuration for a specific note type"""

    note_type_name: str
    search_field: str
    target_field: str
    enabled: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "note_type_name": self.note_type_name,
            "search_field": self.search_field,
            "target_field": self.target_field,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NoteTypeTemplate":
        """Create from dictionary"""
        return cls(
            note_type_name=data.get("note_type_name", ""),
            search_field=data.get("search_field", DEFAULT_SEARCH_FIELD),
            target_field=data.get("target_field", DEFAULT_TARGET_FIELD),
            enabled=data.get("enabled", True),
        )


@dataclass
class AppConfig:
    """Application configuration"""

    # General settings
    enabled: bool = True
    language: LanguageCode = LanguageCode.AUTO

    # Default field configuration (fallback)
    search_field: str = DEFAULT_SEARCH_FIELD
    target_field: str = DEFAULT_TARGET_FIELD

    # Note type specific templates
    note_type_templates: list[NoteTypeTemplate] = field(default_factory=list)
    use_note_type_templates: bool = True

    # Search settings
    max_results: int = DEFAULT_MAX_RESULTS
    auto_download: bool = True
    image_quality: ImageQuality = ImageQuality.MEDIUM

    # Format conversion settings
    convert_format: bool = DEFAULT_CONVERT_FORMAT
    output_format: ImageFormat = ImageFormat.ORIGINAL
    ffmpeg_quality: int = DEFAULT_FFMPEG_QUALITY

    def to_dict(self) -> dict:
        """Convert config to dictionary for JSON serialization"""
        return {
            "enabled": self.enabled,
            "language": self.language.value,
            "search_field": self.search_field,
            "target_field": self.target_field,
            "note_type_templates": [t.to_dict() for t in self.note_type_templates],
            "use_note_type_templates": self.use_note_type_templates,
            "max_results": self.max_results,
            "auto_download": self.auto_download,
            "image_quality": self.image_quality.value,
            "convert_format": self.convert_format,
            "output_format": self.output_format.value,
            "ffmpeg_quality": self.ffmpeg_quality,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        """Create config from dictionary"""
        # Parse note type templates
        templates_data = data.get("note_type_templates", [])
        templates = [NoteTypeTemplate.from_dict(t) for t in templates_data]

        return cls(
            enabled=data.get("enabled", True),
            language=LanguageCode.from_string(data.get("language", "auto")),
            search_field=data.get("search_field", DEFAULT_SEARCH_FIELD),
            target_field=data.get("target_field", DEFAULT_TARGET_FIELD),
            note_type_templates=templates,
            use_note_type_templates=data.get("use_note_type_templates", True),
            max_results=data.get("max_results", DEFAULT_MAX_RESULTS),
            auto_download=data.get("auto_download", True),
            image_quality=ImageQuality(
                data.get("image_quality", DEFAULT_IMAGE_QUALITY)
            ),
            convert_format=data.get("convert_format", DEFAULT_CONVERT_FORMAT),
            output_format=ImageFormat(data.get("output_format", DEFAULT_IMAGE_FORMAT)),
            ffmpeg_quality=data.get("ffmpeg_quality", DEFAULT_FFMPEG_QUALITY),
        )

    def get_fields_for_note_type(self, note_type_name: str) -> tuple[str, str]:
        """
        Get search and target fields for a specific note type

        Args:
            note_type_name: Name of the note type

        Returns:
            Tuple of (search_field, target_field)
        """
        if self.use_note_type_templates:
            # Look for matching template
            for template in self.note_type_templates:
                if template.enabled and template.note_type_name == note_type_name:
                    return (template.search_field, template.target_field)

        # Fallback to default fields
        return (self.search_field, self.target_field)
