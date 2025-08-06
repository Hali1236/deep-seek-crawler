# app.py
import sys, subprocess

# Ensure the Chromium browser gets installed for Playwright
subprocess.run(
    [sys.executable, "-m", "playwright", "install", "chromium"],
    check=True,
)

import os, streamlit as st
# … rest of your imports …

import os
import streamlit as st

# ——— Inject your secrets into os.environ ———
# (set these in your Streamlit Cloud “Secrets” panel)
os.environ["GROQ_API_KEY"]   = st.secrets["GROQ_API_KEY"]
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# ——— Now import the rest ———
import pandas as pd
from scraper import scrape_all

import streamlit as st
import pandas as pd
from scraper import scrape_all      # the function you exposed in scraper.py
from config import BASE_URLS        # default URLs you defined
st.title("Homes Scraper")
st.sidebar.header("Settings")
pause = st.sidebar.slider("Seconds between scrapes", min_value=0, max_value=60, value=30)
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
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "homes.csv", "text/csv")

