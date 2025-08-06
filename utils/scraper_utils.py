import json  
import os
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
    Returns the browser configuration for the crawler in text mode
    (no Playwright chromium launch).
    """
    return BrowserConfig(
        browser_type="chromium",
        headless=True,
        verbose=True,
        text_mode=True,     # ← add this
    )

def get_llm_strategy() -> LLMExtractionStrategy:
    return LLMExtractionStrategy(
    provider="groq/llama3-70b-8192",  # ✅ supported model
    schema=Venue.model_json_schema(),
    extraction_type="schema",
    instruction=(
        "for each community extract data from ONLY avaialble homes ONLY in that community, 'price' 'square footage' 'bed' 'bath' 'stories' 'descripition' \
         for description put the community that the home is in. Do not extract data if home does not have a specific address, or 6 digit price. Make sure to include $ at beginning of price." \
    
    ),
    input_format="markdown",
    verbose=True,
)



async def check_no_results(
    crawler: AsyncWebCrawler,
    url: str,
    session_id: str,
) -> bool:
    """
    Checks if the "No Results Found" message is present on the page.

    Args:
        crawler (AsyncWebCrawler): The web crawler instance.
        url (str): The URL to check.
        session_id (str): The session identifier.

    Returns:
        bool: True if "No Results Found" message is found, False otherwise.
    """
   
    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            session_id=session_id,
        ),
    )

    if result.success:
       
       
        
        return False
    else:
        print(
            f"Error fetching page for 'No Results Found' check: {result.error_message}"
        )

    return False


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
    """
    Fetches and processes venue data from the given URL.

    Args:
        crawler (AsyncWebCrawler): The web crawler instance.
        page_number (int): The page number to fetch.
        base_url (str): The URL of the website (no pagination).
        css_selector (str): The CSS selector to target the content.
        llm_strategy (LLMExtractionStrategy): The LLM extraction strategy.
        session_id (str): The session identifier.
        required_keys (List[str]): List of required keys in the venue data.
        seen_names (Set[str]): Set of venue names that have already been seen.

    Returns:
        Tuple[List[dict], bool]:
            - List[dict]: A list of processed venues from the page.
            - bool: A flag indicating if the "No Results Found" message was encountered.
    """
    url = f"{base_url}"
    print(f"Loading URL: {url}")

    
    no_results = await check_no_results(crawler, url, session_id)
    if no_results:
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
        print(f"No venues found at URL.")
        return [], False

   
    print("Extracted data:", extracted_data)

    
    complete_venues = []
    for venue in extracted_data:
        
        print("Processing venue:", venue)

       
        if venue.get("error") is False:
            venue.pop("error", None)  

        if not is_complete_venue(venue, required_keys):
            continue  

       
        if is_duplicate_venue(venue["Address"], seen_names):
            print(f"Duplicate venue '{venue['Address']}' found. Skipping.")
            continue  

       
        seen_names.add(venue["Address"])
        complete_venues.append(venue)

    if not complete_venues:
        print(f"No complete venues found at URL.")
        return [], False

    print(f"Extracted {len(complete_venues)} venues from URL.")
    return complete_venues, False  