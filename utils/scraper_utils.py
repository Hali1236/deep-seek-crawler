# utils/scraper_utils.py

import json
from typing import List, Set, Tuple

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMExtractionStrategy,
)

from models.venue import Venue
from utils.data_utils import is_complete_venue, is_duplicate_venue

def get_browser_config() -> BrowserConfig:
    """
    Returns a text-mode browser config (no real browser binary).
    """
    return BrowserConfig(
        browser_type="chromium",  # Chromium for JS support
        headless=True,            # No visible UI
        verbose=True,
        text_mode=True,           # <<< THIS forces HTTP+JS instead of Playwright
    )

def get_llm_strategy() -> LLMExtractionStrategy:
    return LLMExtractionStrategy(
        provider="groq/llama3-70b-8192",
        schema=Venue.model_json_schema(),
        extraction_type="schema",
        instruction=(
            "Extract data from all available homes in each community: "
            "'price' 'square footage' 'bed' 'bath' 'stories' 'description'. "
            "For description, use the community name."
        ),
        input_format="markdown",
        verbose=True,
    )

async def check_no_results(
    crawler: AsyncWebCrawler,
    url: str,
    session_id: str,
) -> bool:
    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            session_id=session_id,
        ),
    )
    return not result.success

async def fetch_and_process_page(
    crawler: AsyncWebCrawler,
    page_number: int,
    base_url: str,
    css_selector: str,
    llm_strategy: LLMExtractionStrategy,
    session_id: str,
    required_keys: List[str],
    seen_names: Set[str],
) -> Tuple[List[dict], bool]:
    url = base_url
    print(f"Loading URL: {url}")

    if await check_no_results(crawler, url, session_id):
        return [], True

    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=llm_strategy,
            css_selector=css_selector,
            session_id=session_id,
        ),
    )

    if not (result.success and result.extracted_content):
        print(f"Error fetching URL: {result.error_message}")
        return [], False

    extracted_data = json.loads(result.extracted_content)
    if not extracted_data:
        print("No venues found at URL.")
        return [], False

    complete_venues = []
    for venue in extracted_data:
        if venue.get("error") is False:
            venue.pop("error", None)
        if not is_complete_venue(venue, required_keys):
            continue
        if is_duplicate_venue(venue["address"], seen_names):
            continue
        seen_names.add(venue["address"])
        complete_venues.append(venue)

    return complete_venues, False
