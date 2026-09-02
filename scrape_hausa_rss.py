import requests
import json
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_soup(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"  ⚠️ Error fetching {url}: {e}")
        return None

def extract_article_text(soup):
    """Try multiple selectors to find the main article content."""
    if not soup:
        return ""
    
    # BBC Hausa often uses these
    for selector in [
        "div[data-component='text-block'] p",
        "div.bbc-19j92fr p",
        "article p",
        "div[role='main'] p",
        "main p",
        ".story-body p",
        ".content p",
        ".article-text p"
    ]:
        paragraphs = soup.select(selector)
        if paragraphs:
            text = " ".join(p.get_text(strip=True) for p in paragraphs)
            if len(text) > 200:  # enough to be a real article
                return text
    
    # Fallback: grab all <p> tags inside the main content area
    main = soup.find("main") or soup.find("article") or soup.find("div", class_="content")
    if main:
        paragraphs = main.find_all("p")
        text = " ".join(p.get_text(strip=True) for p in paragraphs)
        if len(text) > 200:
            return text
    
    # Last resort: all <p> tags on the page
    paragraphs = soup.find_all("p")
    text = " ".join(p.get_text(strip=True) for p in paragraphs)
    return text

def scrape_bbc_hausa_rss(max_articles=100):
    articles = []
    rss_url = "https://www.bbc.com/hausa/index.xml"
    print(f"📡 Fetching BBC RSS: {rss_url}")
    try:
        resp = requests.get(rss_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        # RSS items are under <item>
        for item in root.findall(".//item"):
            title = item.find("title").text if item.find("title") is not None else ""
            link = item.find("link").text if item.find("link") is not None else ""
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
            if not link or not title:
                continue
            # BBC links may be relative – ensure absolute
            if link.startswith("/"):
                link = urljoin("https://www.bbc.com", link)
            print(f"  🔗 BBC: {title[:60]}...")
            soup = get_soup(link)
            text = extract_article_text(soup) if soup else ""
            if text:
                articles.append({
                    "source": "BBC Hausa",
                    "title": title,
                    "text": text,
                    "url": link,
                    "date_published": pub_date,
                    "date_collected": datetime.now().isoformat()
                })
                print(f"    ✅ {len(text)} chars")
            else:
                print(f"    ❌ No text extracted")
            time.sleep(1)
            if len(articles) >= max_articles:
                break
    except Exception as e:
        print(f"❌ BBC RSS error: {e}")
    return articles

def scrape_voa_hausa_rss(max_articles=100):
    articles = []
    rss_url = "https://www.voahausa.com/api/av_news_site_rss?sectionId=5628&language=ha"
    print(f"📡 Fetching VOA RSS: {rss_url}")
    try:
        resp = requests.get(rss_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        for item in root.findall(".//item"):
            title = item.find("title").text if item.find("title") is not None else ""
            link = item.find("link").text if item.find("link") is not None else ""
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
            if not link or not title:
                continue
            print(f"  🔗 VOA: {title[:60]}...")
            soup = get_soup(link)
            text = extract_article_text(soup) if soup else ""
            if text:
                articles.append({
                    "source": "VOA Hausa",
                    "title": title,
                    "text": text,
                    "url": link,
                    "date_published": pub_date,
                    "date_collected": datetime.now().isoformat()
                })
                print(f"    ✅ {len(text)} chars")
            else:
                print(f"    ❌ No text extracted")
            time.sleep(1)
            if len(articles) >= max_articles:
                break
    except Exception as e:
        print(f"❌ VOA RSS error: {e}")
    return articles

if __name__ == "__main__":
    print("🚀 Starting RSS-based scraping...")
    bbc = scrape_bbc_hausa_rss(max_articles=100)
    voa = scrape_voa_hausa_rss(max_articles=100)
    all_articles = bbc + voa
    print(f"\n📊 Total collected: {len(all_articles)} articles")
    output_file = "hausa_news_raw.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    print(f"💾 Saved to {output_file}")