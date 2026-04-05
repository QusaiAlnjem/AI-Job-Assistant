import re
import urllib.parse
import pycountry
from scrapling.fetchers import StealthySession

# --- Helper to find Country Code ---
def get_country_code(location_name):
    try:
        return pycountry.countries.search_fuzzy(location_name)[0].alpha_2
    except LookupError:
        return None

def scrape_weworkremotely(title, location, job_type):
    print(f"Starting WWR Scraper for: {title}...")
    results = []
    
    base_url = "https://weworkremotely.com/remote-jobs/search"
    query_str = urllib.parse.quote_plus(title)
    if job_type != 'remote' and location:
         query_str += f"+{urllib.parse.quote_plus(location)}"
    full_search_url = f"{base_url}?term={query_str}"
    
    # Using StealthySession to maintain state and speed up subsequent description fetches
    with StealthySession(headless=True) as session:
        try:
            page = session.fetch(full_search_url, network_idle=True)
            job_rows = page.css("section.jobs ul li")
            
            for row in job_rows[:5]:
                row_class = row.css("::attr(class)").get() or ""
                if "view-all" in row_class or "ad" in row_class:
                    continue

                href = row.css("a::attr(href)").get()
                job_title = row.css("h3::text").get()
                company = row.css(".new-listing__company-name::text").get()

                if not job_title or not company or not href:
                    continue

                full_link = f"https://weworkremotely.com{href}"

                try:
                    job_page = session.fetch(full_link)
                    desc_elem = job_page.css("#job-listing-show-container")
                    if not desc_elem: 
                        desc_elem = job_page.css(".listing-container")
                    
                    description = " ".join(desc_elem.css("::text").getall()).strip() if desc_elem else "No description available."
                    
                    results.append({
                        "title": job_title.strip(),
                        "company": company.strip(),
                        "url": full_link,
                        "description": description,
                        "source": "WeWorkRemotely"
                    })
                except Exception as e:
                    print(f"Error fetching WWR description: {e}")
                    
        except Exception as e:
            print(f"WWR Scraping Error: {e}")

    return results

def scrape_indeed(title, location):
    print(f"Starting Indeed Scraper for: {title}...")
    results = []
    base_url = "https://www.indeed.com/jobs"
    query_str = f"?q={urllib.parse.quote_plus(title)}"
    if location:
        query_str += f"&l={urllib.parse.quote_plus(location)}"
    
    full_search_url = base_url + query_str
    
    with StealthySession(headless=True) as session:
        try:
            page = session.fetch(full_search_url, network_idle=True)
            job_rows = page.css('div.job_seen_beacon')[:5] 
            
            for row in job_rows:
                job_title = row.css('h2.jobTitle span::text').get()
                company = row.css('[data-testid="company-name"]::text').get()
                href = row.css('h2.jobTitle a::attr(href)').get()
                
                if not job_title or not href:
                    continue
                
                # --- THE FIX: Extract Job Key to bypass JS redirects ---
                jk_match = re.search(r'jk=([a-zA-Z0-9]+)', href)
                if jk_match:
                    jk = jk_match.group(1)
                    # Build the direct, SEO-friendly URL
                    full_link = f"https://www.indeed.com/viewjob?jk={jk}"
                else:
                    # Fallback
                    full_link = f"https://www.indeed.com{href}" if href.startswith('/') else href
                
                try:
                    job_page = session.fetch(full_link)
                    
                    # Extract text
                    desc_elem = job_page.css("#jobDescriptionText")
                    description = " ".join(desc_elem.css("::text").getall()).strip() if desc_elem else ""
                    
                    # --- DEBUGGING SAFETY NET ---
                    if not description:
                        print(f"  [!] Description empty for {full_link}. Saving HTML to debug...")
                        with open("indeed_debug_page.html", "w", encoding="utf-8") as f:
                            f.write(job_page.text)
                    
                    results.append({
                        "title": job_title.strip(),
                        "company": company.strip() if company else "Unknown",
                        "url": full_link,
                        "description": description or "No description available.",
                        "source": "Indeed"
                    })
                except Exception as e:
                    print(f"Error fetching Indeed description: {e}")
                    
        except Exception as e:
            print(f"Indeed Scraping Error: {e}")
            
    return results

def scrape_linkedin(title, location):
    print(f"Starting LinkedIn Scraper for: {title}...")
    results = []
    base_url = "https://www.linkedin.com/jobs/search"
    query_str = f"?keywords={urllib.parse.quote_plus(title)}"
    if location:
        query_str += f"&location={urllib.parse.quote_plus(location)}"
        
    full_search_url = base_url + query_str
        
    with StealthySession(headless=True) as session:
        try:
            page = session.fetch(full_search_url, network_idle=True)
            job_rows = page.css('ul.jobs-search__results-list li')[:5]
            
            for row in job_rows:
                job_title = row.css('h3.base-search-card__title::text').get()
                company = row.css('h4.base-search-card__subtitle a::text').get()
                href = row.css('a.base-card__full-link::attr(href)').get()
                
                if not job_title or not href:
                    continue
                
                clean_url = href.split('?')[0]
                
                try:
                    job_page = session.fetch(clean_url)
                    
                    # 2. FALLBACK SELECTORS FOR DYNAMIC HTML
                    # It will try these one by one until it finds the description
                    selectors_to_try = [
                        '[data-testid="expandable-text-box"]',  # From your screenshot
                        'div.show-more-less-html__markup',      # Classic LinkedIn layout
                        'div.jobs-description-content__text',   # Alternate layout
                        'article'                               # Broad fallback
                    ]
                    
                    description = ""
                    for selector in selectors_to_try:
                        desc_elem = job_page.css(selector)
                        if desc_elem:
                            raw_text_list = desc_elem.css("::text").getall()
                            description = " ".join([text.strip() for text in raw_text_list if text.strip()])
                            
                            if description:
                                break 
                    
                    if not description:
                        print(f"  [!] No description found for '{job_title}'. Skipping job.")
                        continue

                    results.append({
                        "title": job_title.strip(),
                        "company": company.strip() if company else "Unknown",
                        "url": clean_url,
                        "description": description or "No description available.",
                        "source": "LinkedIn"
                    })
                except Exception as e:
                    print(f"Error fetching LinkedIn description: {e}")
                    
        except Exception as e:
            print(f"LinkedIn Scraping Error: {e}")
            
    return results

if __name__ == "__main__":
    import json
    
    print("--- Starting Scraper Tests ---")
    
    test_title = "AI Engineer"
    test_location = "United Arab Emirates"
    test_type = "On-site"
    
    # --- Test 1: WeWorkRemotely ---
    print("\n[1] Testing WeWorkRemotely...")
    wwr_results = scrape_weworkremotely(test_title, test_location, test_type)
    for i, job in enumerate(wwr_results, 1):
        print(f"  {i}. {job['title']} | {job['company']}\nDesc: {job['description']}\nURL: {job['url']}")
        
    # --- Test 2: Indeed ---
    print("\n[2] Testing Indeed...")
    indeed_results = scrape_indeed(test_title, test_location)
    for i, job in enumerate(indeed_results, 1):
        print(f"  {i}. {job['title']} | {job['company']}\nDesc: {job['description']}\nURL: {job['url']}")
        
    # --- Test 3: LinkedIn ---
    print("\n[3] Testing LinkedIn...")
    linkedin_results = scrape_linkedin(test_title, test_location)
    for i, job in enumerate(linkedin_results, 1):
        print(f"  {i}. {job['title']} | {job['company']}\nDesc: {job['description']}\nURL: {job['url']}")
        
    print("\n--- Testing Complete ---")
    