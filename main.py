# main.py
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()  # now os.getenv can return None or str

groq_key = os.getenv("GROQ_API_KEY")
if groq_key is not None:
    os.environ["OPENAI_API_KEY"] = groq_key


import argparse
from gooey import Gooey, GooeyParser
from crawl4ai import AsyncWebCrawler
from config import CSS_SELECTOR, REQUIRED_KEYS
from utils.data_utils import save_venues_to_csv
from utils.scraper_utils import fetch_and_process_page, get_browser_config, get_llm_strategy

@Gooey(program_name="Scraper")
def cli():
    parser = GooeyParser()
    parser.add_argument(
        '--urls', 
        widget='Textarea', 
        help='One community URL per line'
    )
    parser.add_argument(
        '--sleep', 
        type=int, 
        default=30, 
        help='Seconds to wait between scrapes'
    )
    return parser.parse_args()

async def run(urls, pause):
    browser_cfg = get_browser_config()
    llm = get_llm_strategy()
    session = "venue_crawl_session"
    all_venues, seen = [], set()

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        for url in urls:
            print(f"Scraping {url}")
            v, empty = await fetch_and_process_page(
                crawler, 1, url, CSS_SELECTOR, llm, session, REQUIRED_KEYS, seen
            )
            all_venues.extend(v)
            if pause:
                print(f"Sleeping {pause}s…")
                await asyncio.sleep(pause)

    save_venues_to_csv(all_venues, "completed_scraping.csv")
    llm.show_usage()
    print("Done! CSV written to completed_scraping.csv")

if __name__ == "__main__":
    args = cli()
    url_list = [u.strip() for u in args.urls.splitlines() if u.strip()]
    asyncio.run(run(url_list, args.sleep))
