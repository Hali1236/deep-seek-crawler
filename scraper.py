# scraper.py
import asyncio
from crawl4ai import AsyncWebCrawler
from config import BASE_URLS, CSS_SELECTOR, REQUIRED_KEYS
from utils.scraper_utils import fetch_and_process_page, get_browser_config, get_llm_strategy

async def _scrape(urls: list[str], pause: int = 30) -> list[dict]:
    cfg  = get_browser_config()
    llm  = get_llm_strategy()
    seen = set()
    out  = []
    async with AsyncWebCrawler(config=cfg) as crawler:
        for url in urls:
            print(f"Scraping {url}")
            venues, no_results = await fetch_and_process_page(
                crawler, 1, url, CSS_SELECTOR, llm, "session", REQUIRED_KEYS, seen
            )
            if not no_results:
                out.extend(venues)
            await asyncio.sleep(pause)
    return out

def scrape_all(urls: list[str], pause: int = 30) -> list[dict]:
    """Blocking entrypoint for Streamlit UI."""
    return asyncio.run(_scrape(urls, pause))
