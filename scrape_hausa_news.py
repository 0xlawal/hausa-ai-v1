import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_soup(url):
    """Fetch page and return BeautifulSoup object."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_bbc_hausa(max_articles=100):
    """Scrape BBC Hausa articles."""
    articles = []
    base_url = "https://www.bbc.com/hausa"
    soup = get_soup(base_url)
    if not soup:
        return articles

    # Find all internal links to articles
    links = soup.select("a[href*='/hausa/']")
    seen_urls = set()

    for link in links:
        href = link.get("href")
        if not href or "/hausa/" not in href:
            continue
        full_url = urljoin(base_url, href)
        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)

        try:
            article_soup = get_soup(full_url)
            if not article_soup:
                continue
            title = article_soup.find("h1")
            if title:
                title = title.get_text(strip=True)
            else:
                title = ""
            # BBC article body is often in <div data-component="text-block">
            paragraphs = article_soup.select("div[data-component='text-block'] p")
            body = " ".join(p.get_text(strip=True) for p in paragraphs)
            if title and body:
                articles.append({
                    "source": "BBC Hausa",
                    "title": title,
                    "text": body,
                    "url": full_url,
                    "date_collected": datetime.now().isoformat()
                })
                print(f"BBC: {title[:60]}...")
                time.sleep(1)  # polite delay
            if len(articles) >= max_articles:
                break
        except Exception as e:
            print(f"Failed on {full_url}: {e}")
            continue
    return articles

def scrape_voa_hausa(max_articles=100):
    """Scrape VOA Hausa articles."""
    articles = []
    base_url = "https://www.voahausa.com"
    soup = get_soup(base_url)
    if not soup:
        return articles

    # VOA uses <article> tags for stories
    for item in soup.find_all("article")[:max_articles]:
        link = item.find("a")
        if not link:
            continue
        href = link.get("href")
        if not href:
            continue
        full_url = urljoin(base_url, href)
        try:
            article_soup = get_soup(full_url)
            if not article_soup:
                continue
            # VOA article content is often in <div class="article-text">
            content_div = article_soup.find("div", class_="article-text")
            if content_div:
                text = content_div.get_text(strip=True)
                title_tag = article_soup.find("h1")
                title = title_tag.get_text(strip=True) if title_tag else ""
                if text:
                    articles.append({
                        "source": "VOA Hausa",
                        "title": title,
                        "text": text,
                        "url": full_url,
                        "date_collected": datetime.now().isoformat()
                    })
                    print(f"VOA: {title[:60]}...")
                    time.sleep(1)
        except Exception as e:
            print(f"Failed on {full_url}: {e}")
            continue
        if len(articles) >= max_articles:
            break
    return articles

if __name__ == "__main__":
    print("Starting scraping...")
    bbc_articles = scrape_bbc_hausa(max_articles=100)
    voa_articles = scrape_voa_hausa(max_articles=100)
    
    all_articles = bbc_articles + voa_articles
    print(f"\nTotal collected: {len(all_articles)} articles")
    
    # Save to JSON
    with open("hausa_news_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    
    print("Saved to hausa_news_raw.json")