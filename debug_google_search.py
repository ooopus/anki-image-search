#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本：查看Google Images搜索的实际HTML响应
用于诊断为什么无法找到图片
"""

import sys
import io
import urllib.parse
from pathlib import Path

# Fix Windows console encoding for Chinese characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("错误：需要安装依赖")
    print("运行: pip install requests beautifulsoup4")
    exit(1)

# Google Images搜索URL
GOOGLE_IMAGE_SEARCH_URL = "https://www.google.com/search"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def debug_search(query: str):
    """调试Google Images搜索"""
    print(f"\n{'='*60}")
    print(f"搜索关键词: {query}")
    print(f"{'='*60}\n")

    # 创建会话
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    # 构建搜索URL
    params = {
        "q": query,
        "udm": "2",  # Image search mode (unified display mode)
    }
    url = f"{GOOGLE_IMAGE_SEARCH_URL}?{urllib.parse.urlencode(params)}"

    print(f"📍 请求URL:\n{url}\n")

    try:
        # 发送请求
        print("🔄 正在发送HTTP请求...")
        response = session.get(url, timeout=10)
        response.raise_for_status()

        print(f"✅ HTTP状态码: {response.status_code}")
        print(f"✅ 响应大小: {len(response.text)} 字符\n")

        # 保存原始HTML
        output_file = Path("debug_google_response.html")
        output_file.write_text(response.text, encoding="utf-8")
        print(f"💾 原始HTML已保存到: {output_file.absolute()}\n")

        # 解析HTML
        print("🔍 开始解析HTML...\n")
        soup = BeautifulSoup(response.text, "html.parser")

        # 检查当前代码使用的选择器
        print("【1】检查新的解析逻辑 (img.DS1iW):")

        image_tags = soup.find_all("img", class_="DS1iW")
        print(f"   找到 {len(image_tags)} 个 img.DS1iW 元素")

        if image_tags:
            print("   ✅ 找到了图片元素！")

            # 模拟实际代码的解析逻辑
            results = []
            for img_tag in image_tags[:5]:
                img_url = img_tag.get("src")

                if not img_url or img_url.startswith("data:") or img_url.startswith("/images/branding"):
                    continue

                thumbnail_url = img_url
                title = img_tag.get("alt", "")

                # Try to find parent link
                parent_link = img_tag.find_parent("a")
                source_url = ""
                if parent_link:
                    href = parent_link.get("href", "")
                    if href and "imgurl=" in href:
                        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                        if "imgurl" in parsed:
                            source_url = parsed["imgurl"][0]
                    else:
                        source_url = href

                final_url = source_url if source_url and source_url.startswith("http") else img_url

                results.append({
                    "url": final_url,
                    "thumbnail": thumbnail_url,
                    "title": title or "Image",
                    "source": source_url,
                })

            print(f"   ✅ 成功解析 {len(results)} 张图片\n")

            for i, result in enumerate(results[:3], 1):
                print(f"   图片 #{i}:")
                print(f"   - URL: {result['url'][:80]}")
                print(f"   - 缩略图: {result['thumbnail'][:80]}")
                print(f"   - 标题: {result['title']}")
                print(f"   - 来源: {result['source'][:80] if result['source'] else '(无)'}")
                print()
        else:
            print("   ❌ 未找到任何图片元素！")

        # 尝试其他可能的选择器
        print("\n【2】尝试其他常见的图片选择器:")

        selectors = [
            ("所有 img 标签", "img"),
            ("所有 a 标签", "a"),
            ("class包含'rg_i'的img", "img.rg_i"),
            ("class包含'Q4LuWd'的img", "img.Q4LuWd"),
            ("data-src属性的img", "img[data-src]"),
        ]

        for desc, selector in selectors:
            elements = soup.select(selector)
            print(f"   {desc}: {len(elements)} 个")

        # 分析所有img标签
        print("\n【3】分析所有img标签的详细信息:")
        all_images = soup.find_all("img")
        print(f"   总共找到 {len(all_images)} 个img标签\n")

        if all_images:
            for i, img in enumerate(all_images[:5], 1):
                print(f"   图片 #{i}:")
                print(f"   - class: {img.get('class', [])}")
                print(f"   - src: {img.get('src', 'N/A')[:80]}")
                print(f"   - data-src: {img.get('data-src', 'N/A')[:80]}")
                print(f"   - data-iurl: {img.get('data-iurl', 'N/A')[:80]}")
                print(f"   - alt: {img.get('alt', 'N/A')[:50]}")
                print()

        # 查找所有div的class属性
        print("\n【4】分析所有div的class属性（前20个）:")
        all_divs = soup.find_all("div", class_=True)
        unique_classes = set()
        for div in all_divs[:100]:
            classes = div.get("class", [])
            if isinstance(classes, list):
                unique_classes.update(classes)

        sorted_classes = sorted(unique_classes)
        print(f"   找到 {len(sorted_classes)} 个唯一的class名称")
        print("   前20个class名称:")
        for cls in sorted_classes[:20]:
            print(f"   - {cls}")

        # 检查是否有CAPTCHA或错误页面
        print("\n【5】检查是否有反爬虫/CAPTCHA:")
        captcha_indicators = [
            "captcha",
            "recaptcha",
            "automated",
            "unusual traffic",
            "robot",
        ]

        page_text = response.text.lower()
        found_indicators = [
            indicator for indicator in captcha_indicators if indicator in page_text
        ]

        if found_indicators:
            print(f"   ⚠️ 检测到可能的反爬虫机制:")
            for indicator in found_indicators:
                print(f"   - '{indicator}'")
        else:
            print("   ✅ 未检测到明显的反爬虫机制")

        print(f"\n{'='*60}")
        print("调试完成！请查看上述输出和保存的HTML文件")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # 使用简单的测试关键词
    test_query = "cat"
    debug_search(test_query)

    print("\n提示：你可以修改脚本中的 test_query 变量来测试不同的搜索词")
    print("      或者用命令行参数: python debug_google_search.py \"your search term\"")

    import sys

    if len(sys.argv) > 1:
        custom_query = " ".join(sys.argv[1:])
        debug_search(custom_query)
