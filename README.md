# ENT Doctor Finder in Lahore ⚕️

A premium, modern web application to find and filter the best ENT Specialists in Lahore.

## Features
- **Modern UI**: Built with Streamlit and custom CSS for a premium glassmorphism aesthetic.
- **Dynamic Search**: Search doctors by name instantly.
- **Advanced Filtering**: Filter by specialization or budget (consultation fee).
- **Automated Scraper**: Includes a Selenium-based scraper to keep doctor information up-to-date.
- **Interactive Experience**: View ratings, experience, and availability at a glance.

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the scraper (optional):
   ```bash
   python scraper.py --once
   ```
3. Launch the app:
   ```bash
   streamlit run app.py
   ```

## Repository Structure
- `app.py`: Main Streamlit application.
- `scraper.py`: Selenium scraper for doctor data.
- `doctors.db`: SQLite database containing the scraped info.
- `logo.png`: Premium application logo.
- `requirements.txt`: Python package dependencies.
