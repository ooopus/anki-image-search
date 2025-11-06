#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的图片搜索功能
"""

import sys
import io
from pathlib import Path

# Fix Windows console encoding for Chinese characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup imports to handle the add-on structure
try:
    import requests
    from bs4 import BeautifulSoup
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    print("❌ 缺少依赖：请运行 pip install requests beautifulsoup4")
    sys.exit(1)

# Constants (from config/constants.py)
GOOGLE_IMAGE_SEARCH_URL = "https://www.google.com/search"
REQUEST_TIMEOUT = 10
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Import the GoogleImageSearch class inline
import urllib.parse
import re
from typing import Any


class GoogleImageSearch:
    """Google Images search implementation"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def search(self, query: str, max_results: int = 20) -> list[dict[str, Any]]:
        """Search Google Images for the given query"""
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


def test_search(query: str, max_results: int = 10):
    """测试图片搜索"""
    print(f"\n{'='*60}")
    print(f"测试搜索: {query}")
    print(f"{'='*60}\n")

    searcher = GoogleImageSearch()
    results = searcher.search(query, max_results)

    if not results:
        print("❌ 未找到任何图片")
        return False

    print(f"✅ 成功找到 {len(results)} 张图片\n")

    for i, result in enumerate(results, 1):
        print(f"图片 #{i}:")
        print(f"  URL: {result['url'][:80]}...")
        print(f"  缩略图: {result['thumbnail'][:80]}...")
        print(f"  标题: {result['title'] or '(无标题)'}")
        print(f"  来源: {result['source'][:80] if result['source'] else '(无来源)'}")
        print()

    return True


if __name__ == "__main__":
    # 测试多个关键词
    test_queries = ["cat", "hello", "python"]

    if len(sys.argv) > 1:
        # 使用命令行参数
        test_queries = [" ".join(sys.argv[1:])]

    success_count = 0
    for query in test_queries:
        if test_search(query, max_results=5):
            success_count += 1

    print(f"\n{'='*60}")
    print(f"测试完成：{success_count}/{len(test_queries)} 个搜索成功")
    print(f"{'='*60}\n")

    if success_count == len(test_queries):
        print("🎉 所有测试通过！图片搜索功能正常工作。")
    else:
        print("⚠️ 部分测试失败，请检查网络连接或Google访问情况。")
