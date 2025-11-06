# ffmpeg_utils.py - FFmpeg utilities for image format conversion

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple

from .config.constants import FFMPEG_COMMAND, FFMPEG_TIMEOUT


class FFmpegConverter:
    """FFmpeg-based image format converter"""

    def __init__(self):
        self._ffmpeg_available = None
        self._ffmpeg_path = None

    def is_available(self) -> bool:
        """Check if ffmpeg is available in system PATH"""
        if self._ffmpeg_available is not None:
            return self._ffmpeg_available

        self._ffmpeg_path = shutil.which(FFMPEG_COMMAND)
        self._ffmpeg_available = self._ffmpeg_path is not None

        return self._ffmpeg_available

    def get_version(self) -> str | None:
        """Get ffmpeg version string"""
        if not self.is_available():
            return None

        try:
            result = subprocess.run(
                [self._ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                # Extract first line which contains version
                return result.stdout.split("\n")[0]
        except Exception as e:
            print(f"Error getting ffmpeg version: {e}")

        return None

    def convert_image(
        self, input_data: bytes, output_format: str, quality: int = 80
    ) -> Tuple[bytes | None, str | None]:
        """
        Convert image to specified format using ffmpeg

        Args:
            input_data: Input image bytes
            output_format: Target format (webp, png, jpg, jpeg)
            quality: Quality for lossy formats (0-100), higher is better

        Returns:
            Tuple of (converted_image_bytes, error_message)
            Returns (None, error) if conversion failed
        """
        if not self.is_available():
            return None, "FFmpeg is not installed or not found in PATH"

        # Normalize format
        output_format = output_format.lower().strip()
        if output_format not in ["webp", "png", "jpg", "jpeg"]:
            return None, f"Unsupported output format: {output_format}"

        # Create temporary files
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp()
            temp_dir_path = Path(temp_dir)

            # Write input to temporary file
            input_file = temp_dir_path / "input"
            with open(input_file, "wb") as f:
                f.write(input_data)

            # Output file
            output_file = temp_dir_path / f"output.{output_format}"

            # Build ffmpeg command
            cmd = [
                self._ffmpeg_path,
                "-i",
                str(input_file),
                "-y",  # Overwrite output file
            ]

            # Add format-specific options
            if output_format == "webp":
                # WebP options
                cmd.extend(["-quality", str(quality)])
                # Add lossless option for quality 100
                if quality >= 100:
                    cmd.extend(["-lossless", "1"])
            elif output_format in ["jpg", "jpeg"]:
                # JPEG options
                cmd.extend(["-q:v", str(max(1, min(31, int((100 - quality) / 3))))])
            elif output_format == "png":
                # PNG is lossless, but we can control compression
                # 0-9, where 9 is best compression (slowest)
                compression = min(9, int(quality / 11))
                cmd.extend(["-compression_level", str(compression)])

            # Add output file
            cmd.append(str(output_file))

            # Run ffmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=FFMPEG_TIMEOUT,
            )

            if result.returncode != 0:
                error_msg = result.stderr or "FFmpeg conversion failed"
                return None, error_msg

            # Read converted image
            if not output_file.exists():
                return None, "Output file not created"

            with open(output_file, "rb") as f:
                converted_data = f.read()

            return converted_data, None

        except subprocess.TimeoutExpired:
            return None, f"FFmpeg conversion timed out after {FFMPEG_TIMEOUT} seconds"
        except Exception as e:
            return None, f"Error during conversion: {str(e)}"
        finally:
            # Clean up temporary directory
            if temp_dir:
                try:
                    import shutil

                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception as e:
                    print(f"Error cleaning up temp directory: {e}")

    def get_format_extension(self, format_name: str) -> str:
        """
        Get file extension for format name

        Args:
            format_name: Format name (webp, png, jpg, jpeg, original)

        Returns:
            File extension with dot (e.g., '.webp')
        """
        format_name = format_name.lower().strip()
        if format_name in ["jpg", "jpeg"]:
            return ".jpg"
        elif format_name == "png":
            return ".png"
        elif format_name == "webp":
            return ".webp"
        else:
            return ".jpg"  # Default fallback


# Global instance
_converter = None


def get_converter() -> FFmpegConverter:
    """Get or create global FFmpegConverter instance"""
    global _converter
    if _converter is None:
        _converter = FFmpegConverter()
    return _converter


def check_ffmpeg() -> Tuple[bool, str]:
    """
    Check if ffmpeg is available

    Returns:
        Tuple of (is_available, message)
    """
    converter = get_converter()
    if converter.is_available():
        version = converter.get_version()
        if version:
            return True, f"FFmpeg found: {version}"
        else:
            return True, "FFmpeg is available"
    else:
        return False, "FFmpeg not found in system PATH"
