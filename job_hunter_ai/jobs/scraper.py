import time
import random
import urllib.parse
from playwright.sync_api import sync_playwright
import pycountry

# --- Helper to find Country Code ---
def get_country_code(location_name):
    try:
        return pycountry.countries.search_fuzzy(location_name)[0].alpha_2
    except LookupError:
        return None

def scrape_weworkremotely(title, location, job_type):
    print(f"Starting Scraper for: {title}...")
    results = []
    
    # 1. Build URL
    base_url = "https://weworkremotely.com/remote-jobs/search"
    query_str = urllib.parse.quote_plus(title)
    if job_type != 'remote' and location:
         query_str += f"+{urllib.parse.quote_plus(location)}"
    full_search_url = f"{base_url}?term={query_str}"
    print(f"Accessing URL: {full_search_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()

        try:
            page.goto(full_search_url, wait_until="domcontentloaded", timeout=15000)
            
            try:
                page.wait_for_selector("section.jobs ul li", timeout=5000)
                print("content loaded successfully.")
            except Exception as e:
                print("Timeout: Job list did not appear on page.")

            job_rows = page.query_selector_all("section.jobs ul li")
            
            print(f"Found {len(job_rows)} list items. Filtering for real jobs...")

            for row in job_rows[:5]:
                # Skip "View All" buttons or Ads (they usually have class 'view-all' or no anchor)
                if "view-all" in row.get_attribute("class") or "ad" in row.get_attribute("class"):
                    continue

                link_elem = row.query_selector("a")
                href = link_elem.get_attribute("href")

                title_elem = row.query_selector("h3")
                company_elem = row.query_selector(".new-listing__company-name")

                if not title_elem or not company_elem:
                    continue

                job_title = title_elem.inner_text().strip()
                company = company_elem.inner_text().strip()
                full_link = f"https://weworkremotely.com{href}"

                print(f"-> Found Real Job: {job_title} at {company}")

                # Get Description
                try:
                    job_page = context.new_page()
                    job_page.goto(full_link, wait_until="domcontentloaded", timeout=10000)
                    
                    desc_elem = job_page.query_selector("#job-listing-show-container")
                    if not desc_elem: desc_elem = job_page.query_selector(".listing-container")
                    
                    description = desc_elem.inner_text() if desc_elem else "No description available."
                    
                    results.append({
                        "title": job_title,
                        "company": company,
                        "url": full_link,
                        "description": description,
                        "source": "WeWorkRemotely"
                    })
                    job_page.close()
                    
                except Exception as e:
                    print(f"Error fetching description: {e}")
                    job_page.close()
                    continue

        except Exception as e:
            print(f"Scraping Error: {e}")

        browser.close()
        
    print(f"Scraping Complete. Returning {len(results)} jobs.")
    return results