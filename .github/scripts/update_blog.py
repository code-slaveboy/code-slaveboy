#!/usr/bin/env python3
"""Fetch latest blog posts from RSS and update README between markers."""

import re
import urllib.request
import xml.etree.ElementTree as ET

BLOG_URL = "https://light.sakurafishermua.top/index.xml"
README_PATH = "README.md"
MAX_POSTS = 5

def fetch_rss(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read()

def parse_posts(xml_data):
    root = ET.fromstring(xml_data)
    items = []
    for item in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title = item.find("{http://www.w3.org/2005/Atom}title")
        link = item.find("{http://www.w3.org/2005/Atom}link")
        updated = item.find("{http://www.w3.org/2005/Atom}updated")
        if title is not None and link is not None:
            href = link.get("href", "")
            items.append((title.text or "无标题", href))
    # Also try RSS 2.0 format
    if not items:
        for item in root.iter("item"):
            title = item.find("title")
            link = item.find("link")
            if title is not None and link is not None:
                items.append((title.text or "无标题", link.text or ""))
    return items[:MAX_POSTS]

def format_posts(posts):
    if not posts:
        return "- 🚧 暂无文章\n"
    lines = []
    for title, url in posts:
        lines.append(f"- [{title}]({url})")
    return "\n".join(lines) + "\n"

def update_readme(posts_text):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = r"<!-- BLOG:START -->.*?<!-- BLOG:END -->"
    replacement = f"<!-- BLOG:START -->\n{posts_text}<!-- BLOG:END -->"
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False

def main():
    try:
        xml_data = fetch_rss(BLOG_URL)
        posts = parse_posts(xml_data)
        posts_text = format_posts(posts)
        if update_readme(posts_text):
            print(f"✅ README updated with {len(posts)} posts")
        else:
            print("⚠️  BLOG markers not found in README")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
