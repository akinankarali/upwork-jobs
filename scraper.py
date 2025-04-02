from playwright.sync_api import sync_playwright
import urllib.parse

def build_url():
    print("🔎 Upwork'te iş arama filtreleri:")
    q = input("Arama terimi (örn: python, react): ").strip()
    job_type = input("İş türü (hourly / fixed-price / boş bırak): ").strip()
    experience = input("Deneyim seviyesi (entry_level / intermediate / expert / boş bırak): ").strip()
    duration = input("Süre (week / month / ongoing / boş bırak): ").strip()

    base_url = "https://www.upwork.com/nx/jobs/search/"
    params = {
        "q": q,
        "sort": "recency"
    }
    if job_type:
        params["job_type"] = job_type
    if experience:
        params["experience_level"] = experience
    if duration:
        params["duration"] = duration

    full_url = base_url + "?" + urllib.parse.urlencode(params)
    print(f"🔗 Oluşturulan URL: {full_url}")
    return full_url

def scrape_jobs(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        page = browser.new_page()
        page.goto(url, timeout=60000)

        page.wait_for_selector("article[data-test='JobTile']", timeout=30000)
        job_cards = page.query_selector_all("article[data-test='JobTile']")

        jobs = []
        for card in job_cards:
            try:
                title_el = card.query_selector("a[data-test*='job-tile-title-link']")
                title = title_el.inner_text().strip()
                href = title_el.get_attribute("href")
                url = f"https://www.upwork.com{href}"

                description_el = card.query_selector("div[data-test='UpCLineClamp JobDescription']")
                description = description_el.inner_text().strip() if description_el else ""

                rate_el = card.query_selector("li[data-test='job-type-label']")
                rate = rate_el.inner_text().strip() if rate_el else ""

                experience_el = card.query_selector("li[data-test='experience-level']")
                experience = experience_el.inner_text().strip() if experience_el else ""

                duration_el = card.query_selector("li[data-test='duration-label']")
                duration = duration_el.inner_text().strip() if duration_el else ""

                tags_el = card.query_selector_all("div[data-test='TokenClamp JobAttrs'] span")
                tags = [tag.inner_text().strip() for tag in tags_el]

                jobs.append({
                    "title": title,
                    "url": url,
                    "description": description,
                    "rate": rate,
                    "experience": experience,
                    "duration": duration,
                    "tags": tags
                })
            except Exception as e:
                print(f"Hata: {e}")

        browser.close()
        return jobs

# === Çalıştır ===
search_url = build_url()
job_list = scrape_jobs(search_url)

print("\n🟢 Çekilen İş İlanları:")
for job in job_list:
    print(f"📌 {job['title']}")
    print(f"🔗 {job['url']}")
    print(f"💸 {job['rate']} | 🧠 {job['experience']} | ⏱️ {job['duration']}")
    print(f"📝 {job['description'][:150]}...")
    print(f"🏷️ Etiketler: {', '.join(job['tags'])}")
    print("-" * 80)