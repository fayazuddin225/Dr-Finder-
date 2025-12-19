import time
import sqlite3
from datetime import datetime
import argparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup

# ================= CONFIG =================
URL = "https://oladoc.com/pakistan/lahore/ent-specialist"
DB_NAME = "doctors.db"
SCROLL_PAUSE = 2
REFRESH_INTERVAL = 24 * 60 * 60  # 24 hours in seconds
# =========================================


# ---------- DB SETUP ----------
def setup_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_url TEXT UNIQUE,
        name TEXT,
        specialization TEXT,
        experience TEXT,
        rating TEXT,
        reviews TEXT,
        fee TEXT,
        availability TEXT,
        is_active INTEGER DEFAULT 1,
        last_seen TEXT
    )
    """)

    conn.commit()
    return conn


# ---------- SELENIUM ----------
def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def click_load_more(driver):
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE)

        wait = WebDriverWait(driver, 10)
        load_more_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "listing-load-more-btn"))
        )

        before_count = len(driver.find_elements(By.CLASS_NAME, "doctor-listing-card"))

        driver.execute_script("arguments[0].click();", load_more_btn)

        wait.until(
            lambda d: len(d.find_elements(By.CLASS_NAME, "doctor-listing-card")) > before_count
        )

        time.sleep(SCROLL_PAUSE)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE)

        return True

    except:
        return False


# ---------- PARSING ----------
def parse_doctors(html):
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("div", class_="doctor-listing-card")

    doctors = []

    for card in cards:
        try:
            name_tag = card.find("a", class_="doctor-name")
            if not name_tag:
                continue

            name = name_tag.get_text(strip=True)
            profile_url = name_tag["href"]

            specialization = card.find("p", class_="doc-specialization")
            specialization = specialization.get_text(strip=True) if specialization else ""

            experience = card.find("span", string=lambda x: x and "Years" in x)
            experience = experience.get_text(strip=True) if experience else ""

            rating = card.find("span", class_="review-with-icon")
            rating = rating.get_text(strip=True) if rating else ""

            reviews = card.find("span", string=lambda x: x and "Reviews" in x)
            reviews = reviews.find_previous("span").get_text(strip=True) if reviews else ""

            fee = card.find("span", class_="doctor-fee")
            fee = fee.get_text(strip=True) if fee else ""

            availability_tag = card.find("span", class_="text-available")
            availability = availability_tag.get_text(strip=True) if availability_tag else "Not Available"

            doctors.append((
                profile_url,
                name,
                specialization,
                experience,
                rating,
                reviews,
                fee,
                availability
            ))

        except:
            continue

    return doctors


# ---------- SAVE TO DB ----------
def save_to_db(conn, doctors):
    cur = conn.cursor()
    now = datetime.now().isoformat()

    current_urls = []

    for d in doctors:
        profile_url = d[0]
        current_urls.append(profile_url)

        cur.execute("""
        INSERT INTO doctors (
            profile_url, name, specialization, experience,
            rating, reviews, fee, availability, last_seen
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(profile_url) DO UPDATE SET
            name=excluded.name,
            specialization=excluded.specialization,
            experience=excluded.experience,
            rating=excluded.rating,
            reviews=excluded.reviews,
            fee=excluded.fee,
            availability=excluded.availability,
            last_seen=excluded.last_seen,
            is_active=1
        """, (*d, now))

    # Mark doctors not in current scrape as inactive
    if current_urls:
        placeholders = ','.join(['?'] * len(current_urls))
        cur.execute(f"""
            UPDATE doctors
            SET is_active = 0
            WHERE profile_url NOT IN ({placeholders})
        """, current_urls)

    conn.commit()


# ---------- MAIN SCRAPER ----------
def scrape():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting scrape...")
    conn = setup_db()
    driver = setup_driver()

    driver.get(URL)
    time.sleep(5)

    print("Loading all doctors...")
    while click_load_more(driver):
        pass

    doctors = parse_doctors(driver.page_source)
    save_to_db(conn, doctors)

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Saved {len(doctors)} doctors to database")

    driver.quit()
    conn.close()


# ---------- AUTO DAILY SCRAPE ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Doctors scraper")
    parser.add_argument("--once", action="store_true", help="Run a single scrape and exit")
    parser.add_argument("--interval", type=int, default=REFRESH_INTERVAL, help="Seconds between runs when not using --once")
    args = parser.parse_args()

    if args.once:
        scrape()
    else:
        while True:
            scrape()
            print(f"Next scrape will run after {args.interval} seconds.\n")
            time.sleep(args.interval)
