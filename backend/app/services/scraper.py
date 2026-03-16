import asyncio
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from app.database import get_db
from app.services.parser import extract_resources, infer_metadata
from app.seed_data import get_seed_docs

BLOG_URLS = [
    "https://aws.amazon.com/blogs/architecture/category/architecture/",
    "https://aws.amazon.com/blogs/architecture/",
    "https://aws.amazon.com/blogs/aws/",
    "https://aws.amazon.com/blogs/compute/",
    "https://aws.amazon.com/blogs/database/",
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
MAX_RETRIES = 3
RETRY_DELAY = 2


async def fetch_page(url: str) -> str | None:
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                r = await client.get(url, headers={"User-Agent": USER_AGENT})
                r.raise_for_status()
                return r.text
        except Exception:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
            else:
                return None


def parse_blog_list(html: str) -> list[tuple[str, str, str]]:
    results = []
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if not href.startswith("http"):
            continue
        if "/blogs/" in href and "aws.amazon.com" in href and href.count("/") >= 5:
            title = a.get_text(strip=True)
            if title and len(title) > 10:
                results.append((href, title, ""))
    seen = set()
    unique = []
    for href, title, desc in results:
        if href not in seen:
            seen.add(href)
            unique.append((href, title, desc))
    return unique[:20]


def parse_blog_post(html: str, url: str, title: str) -> dict | None:
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find("article") or soup.find("main") or soup.find("body")
    if not body:
        return None
    text = body.get_text(separator=" ", strip=True)[:15000]
    if len(text) < 100:
        return None
    resources = extract_resources(text)
    metadata, parsed_with = infer_metadata(text, resources)
    return {
        "source_url": url,
        "title": title or "Untitled",
        "description": text[:500],
        "raw_content": text,
        "scraped_at": datetime.utcnow(),
        "resources": resources,
        "metadata": metadata,
        "parsed_with": parsed_with,
    }


async def run_scrape():
    db = await get_db()
    coll = db["architectures"]

    seed_docs = get_seed_docs()
    for doc in seed_docs:
        await coll.update_one(
            {"source_url": doc["source_url"]},
            {"$set": doc},
            upsert=True,
        )

    for list_url in BLOG_URLS:
        html = await fetch_page(list_url)
        if not html:
            continue
        items = parse_blog_list(html)
        for url, title, _ in items:
            await asyncio.sleep(1.5)
            page_html = await fetch_page(url)
            if page_html:
                doc = parse_blog_post(page_html, url, title)
                if doc:
                    await coll.update_one(
                        {"source_url": doc["source_url"]},
                        {"$set": doc},
                        upsert=True,
                    )
