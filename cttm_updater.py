# cttm_updater.py - Runs daily to update Dhammi's real-time Paññā
import requests
from bs4 import BeautifulSoup
import datetime
import json
import os
from cttm_knowledge import load_cttm_facts, save_cttm_facts, CTTM_FILE_PATH

# ----------------------------- 1. DEFINED TRUSTED SOURCES -----------------------------
# These URLs are placeholders and must be verified and potentially adjusted
# to match the specific structure of the target websites for accurate scraping.
TRUSTED_SOURCES = {
    "Irrawaddy": "https://www.irrawaddy.com/news",
    "MyanmarNow": "https://www.myanmar-now.org/news",
    "DVB": "https://english.dvb.no/category/news",
    "BBC_Burmese": "https://www.bbc.com/burmese" # Note: BBC Burmese is often in Burmese script
}

# ----------------------------- 2. CORE SCRAPING LOGIC -----------------------------
def fetch_and_summarize_news() -> str:
    """Fetches headlines from trusted sources and returns a summarized string."""
    all_headlines = []
    
    for name, url in TRUSTED_SOURCES.items():
        try:
            # We are using a simple request, which is fine for basic content
            response = requests.get(url, timeout=10)
            response.raise_for_status() # Raise an exception for bad status codes
            
            # Simple summarization: we only need the URL and the source name for now
            all_headlines.append(f"Source: {name} (Accessed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})")
            
            # NOTE: For a real solution, you would use BeautifulSoup (bs4) 
            # to parse the HTML and extract the actual headline text from specific tags.
            # Example of what you would do (requires 'pip install beautifulsoup4'):
            # soup = BeautifulSoup(response.content, 'html.parser')
            # headlines = soup.find_all('h2', class_='headline-class') # Placeholder class
            # for h in headlines[:3]: # Get top 3 headlines
            #    all_headlines.append(f"- {h.text.strip()}")
            
            # For this exercise, we'll keep the output simple as a placeholder
            all_headlines.append(f"- [Latest News Summary from {name}]")

        except requests.exceptions.RequestException as e:
            all_headlines.append(f"Source: {name} - Connection Error: {e}")

    return "\n".join(all_headlines)

# ----------------------------- 3. UPDATE CTTM FACT FILE -----------------------------
def update_cttm_facts():
    """Fetches news and updates the CTTM fact file with the latest headlines."""
    
    # Load current facts (including the essential political facts)
    current_facts = load_cttm_facts()
    
    # Fetch the new data
    latest_news_summary = fetch_and_summarize_news()
    
    # Update the dictionary with the new real-time fact (Paññā update)
    current_facts["FACT_DAILY_HEADLINES"] = latest_news_summary
    
    # Save the updated facts back to the JSON file
    save_cttm_facts(current_facts)
    
    print("✅ CTTM Fact Database updated successfully with latest news.")
    
# --- Execution ---
if __name__ == "__main__":
    update_cttm_facts()
  
