# image_search.py - Google Image Search and Download

import hashlib
import mimetypes
import re
import urllib.parse
from pathlib import Path
from typing import Any

try:
    import requests
    from bs4 import BeautifulSoup

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

from .config.constants import (
    GOOGLE_IMAGE_SEARCH_URL,
    MAX_IMAGE_SIZE,
    REQUEST_TIMEOUT,
    SUPPORTED_IMAGE_FORMATS,
    USER_AGENT,
)


class GoogleImageSearch:
    """Google Images search implementation"""

    def __init__(self):
        self.session = None
        if DEPENDENCIES_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update({"User-Agent": USER_AGENT})

    def search(self, query: str, max_results: int = 20) -> list[dict[str, Any]]:
        """
        Search Google Images for the given query

        Returns:
            List of dicts with keys: url, thumbnail, title, source
        """
        if not DEPENDENCIES_AVAILABLE:
            return []

        try:
            # Build search URL with udm=2 for image search
            params = {
                "q": query,
                "udm": "2",  # Image search mode (unified display mode)
            }

            url = f"{GOOGLE_IMAGE_SEARCH_URL}?{urllib.parse.urlencode(params)}"

            # Make request
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract image data - Google Images with udm=2 uses img tags with class DS1iW
            results = []

            # Find all image result containers (divs that contain the images)
            # Google's structure: div containers with img.DS1iW inside
            image_tags = soup.find_all("img", class_="DS1iW")

            for img_tag in image_tags[:max_results]:
                try:
                    # Get image URL from src attribute
                    img_url = img_tag.get("src")

                    if not img_url or img_url.startswith("data:") or img_url.startswith("/images/branding"):
                        # Skip base64 thumbnails and Google logos
                        continue

                    # For Google Images, the src is already a valid thumbnail URL
                    thumbnail_url = img_url

                    # Get title/alt text
                    title = img_tag.get("alt", "")

                    # Try to find the parent link to get source URL
                    parent_link = img_tag.find_parent("a")
                    source_url = ""
                    if parent_link:
                        href = parent_link.get("href", "")
                        # Extract the actual image URL from Google's redirect link
                        if href and "imgurl=" in href:
                            # Parse the imgurl parameter from Google's link
                            import urllib.parse
                            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                            if "imgurl" in parsed:
                                source_url = parsed["imgurl"][0]
                        else:
                            source_url = href

                    # Use the high-res source URL if available, otherwise use thumbnail
                    final_url = source_url if source_url and source_url.startswith("http") else img_url

                    results.append(
                        {
                            "url": final_url,
                            "thumbnail": thumbnail_url,
                            "title": title or "Image",
                            "source": source_url,
                        }
                    )
                except Exception as e:
                    print(f"Error parsing image element: {e}")
                    continue

            return results

        except Exception as e:
            print(f"Error searching images: {e}")
            return []

    def download_image(self, url: str) -> bytes | None:
        """Download image from URL"""
        print(f"[ImageSearch] 开始下载图片: {url[:100]}")
        if not DEPENDENCIES_AVAILABLE:
            print("[ImageSearch] 依赖不可用")
            return None

        try:
            print("[ImageSearch] 发送HTTP请求...")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT, stream=True)
            response.raise_for_status()
            print(f"[ImageSearch] HTTP状态码: {response.status_code}")

            # Check content type
            content_type = response.headers.get("content-type", "")
            print(f"[ImageSearch] Content-Type: {content_type}")
            if not content_type.startswith("image/"):
                print(f"[ImageSearch] 错误：无效的Content-Type: {content_type}")
                return None

            # Check file size
            content_length = response.headers.get("content-length")
            if content_length:
                print(f"[ImageSearch] Content-Length: {content_length} 字节")
                if int(content_length) > MAX_IMAGE_SIZE:
                    print(f"[ImageSearch] 错误：图片太大: {content_length} 字节")
                    return None

            # Download image
            print("[ImageSearch] 正在读取图片数据...")
            image_data = response.content
            print(f"[ImageSearch] 下载完成，大小: {len(image_data)} 字节")

            if len(image_data) > MAX_IMAGE_SIZE:
                print(f"[ImageSearch] 错误：下载的图片太大: {len(image_data)} 字节")
                return None

            return image_data

        except Exception as e:
            print(f"[ImageSearch] 下载异常: {e}")
            import traceback
            traceback.print_exc()
            return None


def save_image_to_media(image_data: bytes, url: str, note=None) -> str | None:
    """
    Save image to Anki media folder and return filename

    Args:
        image_data: Image bytes
        url: Original image URL
        note: Anki note object (optional, for context)

    Returns:
        Filename in media folder, or None if failed
    """
    print("[SaveImage] 开始保存图片到媒体文件夹")
    print(f"[SaveImage] 图片大小: {len(image_data)} 字节")
    print(f"[SaveImage] URL: {url[:100]}")

    try:
        from aqt import mw

        if not mw or not mw.col:
            print("[SaveImage] 错误：Anki主窗口或集合不可用")
            return None

        print("[SaveImage] Anki集合已就绪")

        # Get configuration
        from .state import get_config

        config = get_config()
        print(f"[SaveImage] 格式转换: {config.convert_format}, 输出格式: {config.output_format.value}")

        # Convert format if enabled
        original_data = image_data
        if config.convert_format and config.output_format.value != "original":
            from .ffmpeg_utils import get_converter

            converter = get_converter()
            if converter.is_available():
                converted_data, error = converter.convert_image(
                    image_data, config.output_format.value, config.ffmpeg_quality
                )
                if converted_data:
                    image_data = converted_data
                    print(
                        f"Image converted to {config.output_format.value} using ffmpeg"
                    )
                else:
                    print(f"Format conversion failed: {error}, using original")
                    # Continue with original image if conversion fails
            else:
                print("FFmpeg not available, using original image format")

        # Generate unique filename
        print("[SaveImage] 生成唯一文件名...")
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        print(f"[SaveImage] URL哈希: {url_hash}")

        # Determine extension
        if config.convert_format and config.output_format.value != "original":
            # Use configured output format
            print("[SaveImage] 使用配置的输出格式")
            from .ffmpeg_utils import get_converter

            converter = get_converter()
            ext = converter.get_format_extension(config.output_format.value)
            print(f"[SaveImage] FFmpeg扩展名: {ext}")
        else:
            # Try to get extension from URL
            print("[SaveImage] 从URL提取扩展名...")
            parsed_url = urllib.parse.urlparse(url)
            path = parsed_url.path
            ext = Path(path).suffix.lower()
            print(f"[SaveImage] URL扩展名: {ext}")

            # If no extension, try to guess from content
            if not ext or ext not in SUPPORTED_IMAGE_FORMATS:
                # Try to detect from image data
                print("[SaveImage] 从图片数据检测格式...")
                import imghdr

                detected = imghdr.what(None, h=image_data)
                if detected:
                    ext = f".{detected}"
                    print(f"[SaveImage] 检测到格式: {detected}")
                else:
                    ext = ".jpg"  # Default fallback
                    print("[SaveImage] 使用默认扩展名: .jpg")

        filename = f"image_search_{url_hash}{ext}"
        print(f"[SaveImage] 最终文件名: {filename}")

        # Write to media folder
        print("[SaveImage] 写入到媒体文件夹...")
        mw.col.media.write_data(filename, image_data)
        print("[SaveImage] 写入成功")

        return filename

    except Exception as e:
        print(f"[SaveImage] 保存异常: {e}")
        import traceback
        traceback.print_exc()
        return None


def insert_image_to_field(editor, field_name: str, filename: str):
    """Insert image into note field"""
    print("[InsertImage] 开始插入图片到字段")
    print(f"[InsertImage] 字段名: {field_name}")
    print(f"[InsertImage] 文件名: {filename}")

    try:
        note = editor.note
        if not note:
            print("[InsertImage] 错误：笔记对象为空")
            return False

        if field_name not in note:
            print(f"[InsertImage] 错误：字段 '{field_name}' 不存在于笔记中")
            print(f"[InsertImage] 可用字段: {list(note.keys())}")
            return False

        print("[InsertImage] 笔记和字段验证通过")

        # Create image HTML
        img_html = f'<img src="{filename}">'
        print(f"[InsertImage] 生成的HTML: {img_html}")

        # Get current field content
        current_content = note[field_name]
        print(f"[InsertImage] 当前字段内容长度: {len(current_content)} 字符")

        # Append or replace image
        if current_content.strip():
            # Append to existing content
            note[field_name] = f"{current_content}<br>{img_html}"
            print("[InsertImage] 图片追加到现有内容")
        else:
            # Set as new content
            note[field_name] = img_html
            print("[InsertImage] 图片设置为新内容")

        # Update editor
        print("[InsertImage] 更新编辑器...")
        editor.loadNoteKeepingFocus()
        print("[InsertImage] 编辑器更新完成")

        return True

    except Exception as e:
        print(f"[InsertImage] 插入异常: {e}")
        import traceback
        traceback.print_exc()
        return False
