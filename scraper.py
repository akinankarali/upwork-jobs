from playwright.sync_api import sync_playwright
import urllib.parse

class UpworkSearchBuilder:
    def __init__(self):
        self.base_url = "https://www.upwork.com/nx/jobs/search/"
        self.params = {}

    def set_query(self, query):
        self.params["q"] = query
        return self

    def set_experience_level(self, level):
        self.params["experience_level"] = level
        return self

    def set_job_type(self, job_type):
        self.params["job_type"] = job_type
        return self

    def set_budget_range(self, min_budget=None, max_budget=None):
        if min_budget is not None:
            self.params["budget_min"] = str(min_budget)
        if max_budget is not None:
            self.params["budget_max"] = str(max_budget)
        return self

    def set_hourly_rate(self, min_rate=None, max_rate=None):
        if min_rate is not None:
            self.params["hourly_rate_min"] = str(min_rate)
        if max_rate is not None:
            self.params["hourly_rate_max"] = str(max_rate)
        return self

    def set_project_length(self, length):
        self.params["duration"] = length
        return self

    def set_hours_per_week(self, hours):
        if hours == "<30":
            self.params["workload"] = "as_needed"
        elif hours == ">30":
            self.params["workload"] = "full_time"
        return self

    def set_client_history(self, history):
        if history == "no_hires":
            self.params["client_hires"] = "0"
        elif history == "one_to_nine":
            self.params["client_hires"] = "1-9"
        elif history == "ten_plus":
            self.params["client_hires"] = "10plus"
        return self

    def set_contract_to_hire(self, value):
        self.params["contract_to_hire"] = "true" if value else "false"
        return self

    def build(self):
        query_string = urllib.parse.urlencode(self.params)
        return f"{self.base_url}?{query_string}"

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
                job_url = f"https://www.upwork.com{href}"

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
                    "url": job_url,
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

if __name__ == "__main__":
    builder = UpworkSearchBuilder()

    print("🔎 Upwork'te iş arama filtreleri:")
    query = input("Arama terimi (örn: python, react): ").strip()
    job_type = input("İş türü (hourly / fixed-price / boş bırak): ").strip()
    experience = input("Deneyim seviyesi (entry_level / intermediate / expert / boş bırak): ").strip()
    duration = input("Proje süresi (week / month / ongoing / boş bırak): ").strip()
    hours = input("Haftalık saat (<30 / >30 / boş bırak): ").strip()
    min_rate = input("Minimum saatlik ücret (boş bırakılabilir): ").strip()
    max_rate = input("Maksimum saatlik ücret (boş bırakılabilir): ").strip()
    client_history = input("Müşteri geçmişi (no_hires / one_to_nine / ten_plus / boş bırak): ").strip()
    contract_to_hire = input("Contract-to-hire arıyorsan 'evet' yaz, istemiyorsan boş bırak: ").strip().lower() == "evet"

    builder.set_query(query)
    if job_type: builder.set_job_type(job_type)
    if experience: builder.set_experience_level(experience)
    if duration: builder.set_project_length(duration)
    if hours: builder.set_hours_per_week(hours)
    if min_rate or max_rate:
        builder.set_hourly_rate(min_rate=int(min_rate) if min_rate else None,
                                max_rate=int(max_rate) if max_rate else None)
    if client_history: builder.set_client_history(client_history)
    if contract_to_hire: builder.set_contract_to_hire(True)

    search_url = builder.build()
    print("🔗 Arama URL'i:", search_url)

    job_list = scrape_jobs(search_url)

    print("\n🟢 Çekilen İş İlanları:")
    for job in job_list:
        print(f"📌 {job['title']}")
        print(f"🔗 {job['url']}")
        print(f"💸 {job['rate']} | 🧠 {job['experience']} | ⏱️ {job['duration']}")
        print(f"📝 {job['description'][:150]}...")
        print(f"🏷️ Etiketler: {', '.join(job['tags'])}")
        print("-" * 80)
