# config/constants.py - Constants

from pathlib import Path

# File paths
CONFIG_FILE_NAME = "config.json"
USER_FILES_DIR = Path(__file__).parent.parent / "user_files"
CONFIG_FILE_PATH = USER_FILES_DIR / CONFIG_FILE_NAME

# Default values
DEFAULT_SEARCH_FIELD = "Word"
DEFAULT_TARGET_FIELD = "Picture"
DEFAULT_MAX_RESULTS = 20
DEFAULT_IMAGE_QUALITY = "medium"
DEFAULT_IMAGE_FORMAT = "original"
DEFAULT_CONVERT_FORMAT = False
DEFAULT_FFMPEG_QUALITY = 80  # Quality for lossy formats (0-100)

# Image search
GOOGLE_IMAGE_SEARCH_URL = "https://www.google.com/search"
# Simplified USER_AGENT works better with Google Images udm=2 API
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
REQUEST_TIMEOUT = 10  # seconds

# Image processing
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
THUMBNAIL_SIZE = (200, 200)

# UI
IMAGE_PICKER_WIDTH = 800
IMAGE_PICKER_HEIGHT = 600
GRID_COLUMNS = 4

# FFmpeg
FFMPEG_TIMEOUT = 30  # seconds for conversion
FFMPEG_COMMAND = "ffmpeg"  # Command to check/use ffmpeg
