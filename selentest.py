import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time

class WARScraper:
    def __init__(self, start_date_str, end_date_str):
        self.start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        self.driver = None
        self.data = []
        self._setup_browser()

    def _setup_browser(self):
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1550,1000")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--headless=new")
        self.driver = uc.Chrome(options=options)

    def restart_browser(self):
        print("🔁 Restarting browser...")
        try:
            self.driver.quit()
        except Exception:
            pass
        time.sleep(3)
        self._setup_browser()

    def scrape(self):
        current_date = self.start_date
        MAX_RETRIES = 3

        while current_date <= self.end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            success = False

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    print(f"\n📡 Attempt {attempt} for {date_str}...")

                    url = (
                        "https://www.fangraphs.com/leaders/major-league?"
                        "pos=all&stats=bat&lg=all&type=8&season=2025&month=1000"
                        "&season1=2025&ind=0&team=25&qual=0"
                        f"&startdate=2025-03-01&enddate={date_str}"
                    )

                    self.driver.get(url)

                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "table-scroll"))
                    )

                    time.sleep(3)  # Let the page render

                    soup = BeautifulSoup(self.driver.page_source, "html.parser")
                    table = soup.find("div", class_="table-scroll").find("table")
                    tbody = table.find("tbody")
                    rows = tbody.find_all("tr")

                    for tr in rows:
                        player = {"Date": date_str}
                        for td in tr.find_all("td"):
                            stat = td.get("data-stat")
                            if stat == "Name":
                                player["Name"] = td.get_text(strip=True)
                            elif stat == "WAR":
                                player["WAR"] = td.get_text(strip=True)
                        if "Name" in player and "WAR" in player:
                            self.data.append(player)

                    print(f"✅ Success for {date_str}: {len(rows)} players")
                    success = True
                    break  

                except Exception as e:
                    print(f"❌ Error on attempt {attempt} for {date_str}: {e}")
                    time.sleep(5)
                    if attempt == MAX_RETRIES:
                        self.restart_browser()

            current_date += timedelta(days=1)

        self.driver.quit()

    def save_to_csv(self, filename):
        df = pd.DataFrame(self.data)
        df["WAR"] = pd.to_numeric(df["WAR"], errors="coerce")
        df.to_csv(filename, index=False)
        print(f"\n📁 Saved to {filename}")


scraper = WARScraper(start_date_str="2025-04-06", end_date_str="2025-04-21")
scraper.scrape()
scraper.save_to_csv("mets_daily_war_mar27_apr21.csv")
