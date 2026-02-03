import time
import random
from playwright.sync_api import sync_playwright

def scrape_weworkremotely(job_title):
    """
    Searches WeWorkRemotely for the job_title.
    Returns a list of dicts: [{'title':..., 'company':..., 'url':..., 'description':...}]
    """
    print(f"🕵️‍♂️ Starting Scraper for: {job_title}...")
    
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()
        
        search_url = f"https://weworkremotely.com/remote-jobs/search?term={job_title}"
        page.goto(search_url)
        
        # Wait for results to load
        try:
            page.wait_for_selector("section.jobs", timeout=5000) # Selects the <section> tag with class="jobs"
        except:
            print("No jobs found or timeout.")
            browser.close()
            return []

        # Extract Job Links (first 5 to save time)
        job_cards = page.query_selector_all("li.feature")[:5] # Selects all <li> tag with class="feature"

        print(f"Found {len(job_cards)} potential jobs. Parsing details...")

        for card in job_cards:
            try:
                link_elem = card.query_selector("a") # deep search for <a> inside <li>
                if not link_elem: continue

                relative_link = link_elem.get_attribute("href")
                full_link = f"https://weworkremotely.com{relative_link}"

                title_elem = card.query_selector("h3")
                company_elem = card.query_selector(".new-listing__company-name")
                
                if not title_elem or not company_elem:
                    print("Skipping card (missing title/company)")
                    continue

                title = title_elem.inner_text().strip()
                company = company_elem.inner_text().strip()
                
                print(f"-> Scraping details for: {title}")
                
                # Create a temporary page to fetch description
                detail_page = browser.new_page()
                detail_page.goto(full_link)
                description = detail_page.inner_text(".company-show-card") # searches for class='company-show-card' and extracts all text inside
                
                results.append({
                    "title": title,
                    "company": company,
                    "url": full_link,
                    "description": description,
                    "source": "WeWorkRemotely"
                })

                detail_page.close()
                
                # Sleep to be polite to the server
                time.sleep(random.uniform(1, 3)) 
                
            except Exception as e:
                print(f"Error parsing a job: {e}")
                continue

        browser.close()
        
    print(f"Scraping Complete. Found {len(results)} jobs.")
    return results