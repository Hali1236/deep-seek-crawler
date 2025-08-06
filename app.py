# app.py

import os

# 1️⃣ Force Crawl4AI into HTTP+JS “text mode” (no real browser)
os.environ["CRAWL4AI_TEXT_MODE"] = "1"

import streamlit as st

# 2️⃣ Inject your secrets into the environment (set these in
#    the Streamlit Cloud UI under Settings → Secrets)
os.environ["GROQ_API_KEY"]   = st.secrets["GROQ_API_KEY"]
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# 3️⃣ Now import the rest of your dependencies
import pandas as pd
from config import BASE_URLS       # your default list of community URLs
from scraper import scrape_all     # your async scrape entrypoint

# 4️⃣ Build the Streamlit UI
st.title("Homes Scraper")

st.sidebar.header("Settings")
pause = st.sidebar.slider(
    "Seconds between scrapes",
    min_value=0,
    max_value=60,
    value=30,
)

urls = st.text_area(
    "Community URLs (one per line)",
    value="\n".join(BASE_URLS),
    height=150,
)

if st.button("Run Scraper"):
    url_list = [u.strip() for u in urls.splitlines() if u.strip()]
    with st.spinner("Scraping… this can take a minute"):
        data = scrape_all(url_list, pause)

    if not data:
        st.error("No homes extracted.")
    else:
        df = pd.DataFrame(data)
        st.success(f"Extracted {len(df)} homes")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "homes.csv", "text/csv")
