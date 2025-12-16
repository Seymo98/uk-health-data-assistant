#!/usr/bin/env python3
"""
SAIL Databank Data Use Register Scraper

Extracts the data use register from https://saildatabank.com/data/data-use-register/
including detailed project information from project title hyperlinks.

Usage:
    python scrape_sail_register.py

Output:
    sail_data_use_register.csv - Complete data use register with project details
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import json
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Browser-like headers to avoid blocking
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-GB,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
}

BASE_URL = "https://saildatabank.com"
REGISTER_URL = f"{BASE_URL}/data/data-use-register/"


class SAILScraper:
    """Scraper for SAIL Databank Data Use Register."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.projects = []

    def get_page(self, url, retries=3, delay=2):
        """Fetch a page with retry logic."""
        for attempt in range(retries):
            try:
                logger.info(f"Fetching: {url} (attempt {attempt + 1}/{retries})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Error fetching {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(delay * (attempt + 1))
        return None

    def parse_main_register(self, html):
        """Parse the main data use register page."""
        soup = BeautifulSoup(html, 'lxml')
        projects = []

        # Strategy 1: Look for tables
        tables = soup.find_all('table')
        logger.info(f"Found {len(tables)} tables on page")

        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 1:
                # Get headers
                headers = []
                header_row = table.find('thead')
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                else:
                    first_row = rows[0]
                    headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
                    rows = rows[1:]  # Skip header row

                logger.info(f"Table headers: {headers}")

                # Extract data rows
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        row_data = {}
                        for i, cell in enumerate(cells):
                            key = headers[i] if i < len(headers) else f'col_{i}'
                            row_data[key] = cell.get_text(strip=True)
                            # Check for links
                            link = cell.find('a', href=True)
                            if link:
                                href = link.get('href')
                                if not href.startswith('http'):
                                    href = urljoin(BASE_URL, href)
                                row_data[f'{key}_link'] = href
                        if any(row_data.values()):
                            projects.append(row_data)

        # Strategy 2: Look for accordion/card structures
        if not projects:
            logger.info("No tables found, looking for card/accordion structures...")

            # Common patterns for project listings
            project_cards = soup.find_all(['div', 'article', 'li'],
                class_=re.compile(r'(project|card|item|entry|accordion)', re.I))

            for card in project_cards:
                title_elem = card.find(['h1', 'h2', 'h3', 'h4', 'h5', 'a'])
                if title_elem:
                    project = {
                        'title': title_elem.get_text(strip=True),
                    }

                    # Get link if available
                    link = title_elem if title_elem.name == 'a' else title_elem.find('a')
                    if link and link.get('href'):
                        href = link.get('href')
                        if not href.startswith('http'):
                            href = urljoin(BASE_URL, href)
                        project['project_link'] = href

                    # Get any description text
                    desc = card.find(['p', 'div'], class_=re.compile(r'(desc|summary|content)', re.I))
                    if desc:
                        project['description'] = desc.get_text(strip=True)

                    projects.append(project)

        # Strategy 3: Look for definition lists
        if not projects:
            logger.info("Looking for definition lists...")
            dl_elements = soup.find_all('dl')
            for dl in dl_elements:
                project = {}
                dts = dl.find_all('dt')
                dds = dl.find_all('dd')
                for dt, dd in zip(dts, dds):
                    key = dt.get_text(strip=True)
                    value = dd.get_text(strip=True)
                    project[key] = value
                    link = dd.find('a', href=True)
                    if link:
                        href = link.get('href')
                        if not href.startswith('http'):
                            href = urljoin(BASE_URL, href)
                        project[f'{key}_link'] = href
                if project:
                    projects.append(project)

        # Strategy 4: Extract all links that look like project pages
        if not projects:
            logger.info("Looking for project links...")
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                # Look for links that might be project pages
                if any(pattern in href.lower() for pattern in ['/project', '/study', '/research']):
                    if text and len(text) > 10:  # Skip short links
                        full_url = href if href.startswith('http') else urljoin(BASE_URL, href)
                        projects.append({
                            'title': text,
                            'project_link': full_url
                        })

        return projects, soup

    def get_project_details(self, project_url):
        """Fetch detailed information from a project page."""
        html = self.get_page(project_url)
        if not html:
            return {}

        soup = BeautifulSoup(html, 'lxml')
        details = {'project_url': project_url}

        # Extract page title
        title = soup.find('h1')
        if title:
            details['full_title'] = title.get_text(strip=True)

        # Look for common field patterns
        field_patterns = [
            ('Lead Organisation', 'lead_organisation'),
            ('Lead Applicant', 'lead_applicant'),
            ('Principal Investigator', 'principal_investigator'),
            ('Start Date', 'start_date'),
            ('End Date', 'end_date'),
            ('Status', 'status'),
            ('Project Status', 'project_status'),
            ('Datasets', 'datasets'),
            ('Data Sources', 'data_sources'),
            ('Research Summary', 'research_summary'),
            ('Lay Summary', 'lay_summary'),
            ('Public Benefit', 'public_benefit'),
            ('Approval Date', 'approval_date'),
            ('Project ID', 'project_id'),
            ('IGRP', 'igrp_number'),
        ]

        # Method 1: Definition lists
        for dl in soup.find_all('dl'):
            dts = dl.find_all('dt')
            dds = dl.find_all('dd')
            for dt, dd in zip(dts, dds):
                label = dt.get_text(strip=True)
                value = dd.get_text(strip=True)
                for pattern, key in field_patterns:
                    if pattern.lower() in label.lower():
                        details[key] = value
                        break

        # Method 2: Table rows
        for table in soup.find_all('table'):
            for row in table.find_all('tr'):
                cells = row.find_all(['th', 'td'])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    for pattern, key in field_patterns:
                        if pattern.lower() in label.lower():
                            details[key] = value
                            break

        # Method 3: Labeled elements
        for elem in soup.find_all(['div', 'p', 'span'], class_=re.compile(r'(field|value|data)', re.I)):
            label_elem = elem.find(['label', 'span', 'strong'], class_=re.compile(r'label', re.I))
            if label_elem:
                label = label_elem.get_text(strip=True)
                value_elem = elem.find(['span', 'div', 'p'], class_=re.compile(r'value', re.I))
                if value_elem:
                    value = value_elem.get_text(strip=True)
                    for pattern, key in field_patterns:
                        if pattern.lower() in label.lower():
                            details[key] = value
                            break

        # Extract main content/description
        main_content = soup.find(['main', 'article', 'div'], class_=re.compile(r'(content|main|body)', re.I))
        if main_content:
            # Get first few paragraphs as summary
            paragraphs = main_content.find_all('p', limit=5)
            summary_text = ' '.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
            if summary_text and 'research_summary' not in details:
                details['research_summary'] = summary_text[:1000]  # Limit length

        return details

    def scrape_register(self, include_details=True, max_workers=5):
        """Main scraping function."""
        logger.info("Starting SAIL Databank Data Use Register scraping...")
        logger.info(f"Target URL: {REGISTER_URL}")

        # Fetch main register page
        html = self.get_page(REGISTER_URL)
        if not html:
            logger.error("Failed to fetch the main register page")
            return pd.DataFrame()

        logger.info(f"Successfully fetched page ({len(html)} bytes)")

        # Save raw HTML for inspection
        with open('sail_register_raw.html', 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info("Saved raw HTML to sail_register_raw.html")

        # Parse the main register
        self.projects, soup = self.parse_main_register(html)
        logger.info(f"Found {len(self.projects)} projects in main register")

        if not self.projects:
            logger.warning("No projects found. Please check sail_register_raw.html for page structure.")
            return pd.DataFrame()

        # Get detailed info for each project
        if include_details:
            project_urls = [p.get('project_link') or p.get('title_link') for p in self.projects]
            project_urls = [url for url in project_urls if url]

            if project_urls:
                logger.info(f"Fetching details for {len(project_urls)} projects...")

                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    future_to_url = {executor.submit(self.get_project_details, url): url
                                     for url in project_urls}

                    for i, future in enumerate(as_completed(future_to_url)):
                        url = future_to_url[future]
                        try:
                            details = future.result()
                            # Find the project and update it
                            for proj in self.projects:
                                proj_url = proj.get('project_link') or proj.get('title_link')
                                if proj_url == url:
                                    proj.update(details)
                                    break
                        except Exception as e:
                            logger.warning(f"Error getting details for {url}: {e}")

                        if (i + 1) % 10 == 0:
                            logger.info(f"Progress: {i + 1}/{len(project_urls)} projects")

        # Create DataFrame
        df = pd.DataFrame(self.projects)
        return df

    def save_to_csv(self, df, filename='sail_data_use_register.csv'):
        """Save DataFrame to CSV."""
        if df.empty:
            logger.warning("No data to save")
            return

        df.to_csv(filename, index=False, encoding='utf-8-sig')
        logger.info(f"Saved {len(df)} records to {filename}")


def scrape_with_selenium():
    """Alternative scraper using Selenium for JavaScript-rendered pages."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager

        logger.info("Using Selenium for JavaScript-rendered content...")

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(f'user-agent={HEADERS["User-Agent"]}')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(REGISTER_URL)

        # Wait for content to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)  # Additional wait for dynamic content

        html = driver.page_source
        driver.quit()

        return html

    except ImportError:
        logger.info("Selenium not installed. Install with: pip install selenium webdriver-manager")
        return None
    except Exception as e:
        logger.warning(f"Selenium error: {e}")
        return None


def scrape_with_playwright():
    """Alternative scraper using Playwright for JavaScript-rendered pages."""
    try:
        from playwright.sync_api import sync_playwright

        logger.info("Using Playwright for JavaScript-rendered content...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=HEADERS['User-Agent'],
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()

            page.goto(REGISTER_URL, wait_until='networkidle', timeout=60000)
            time.sleep(3)  # Additional wait for dynamic content

            html = page.content()

            # Take screenshot for debugging
            page.screenshot(path='sail_register_screenshot.png', full_page=True)
            logger.info("Saved screenshot to sail_register_screenshot.png")

            browser.close()

        return html

    except ImportError:
        logger.info("Playwright not installed. Install with: pip install playwright && playwright install chromium")
        return None
    except Exception as e:
        logger.warning(f"Playwright error: {e}")
        return None


def main():
    """Main entry point."""
    print("=" * 70)
    print("SAIL Databank Data Use Register Scraper")
    print("=" * 70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    scraper = SAILScraper()

    # Try standard requests first
    df = scraper.scrape_register(include_details=True)

    # If no data found, try with Selenium or Playwright
    if df.empty:
        logger.info("Standard scraping failed. Trying alternative methods...")

        # Try Playwright first (generally more reliable)
        html = scrape_with_playwright()

        # Fall back to Selenium
        if not html:
            html = scrape_with_selenium()

        if html:
            with open('sail_register_raw.html', 'w', encoding='utf-8') as f:
                f.write(html)

            projects, soup = scraper.parse_main_register(html)
            if projects:
                scraper.projects = projects
                df = pd.DataFrame(projects)

    if not df.empty:
        # Display summary
        print(f"\nExtracted {len(df)} projects")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst 5 records:")
        print(df.head().to_string())

        # Save to CSV
        scraper.save_to_csv(df)
        print(f"\nData saved to: sail_data_use_register.csv")
    else:
        print("\nNo data could be extracted.")
        print("Please check sail_register_raw.html for the page structure.")
        print("\nPossible reasons:")
        print("1. The page requires JavaScript to render content")
        print("2. The page structure has changed")
        print("3. Access is blocked by the website")
        print("\nTry installing Selenium or Playwright for JavaScript support:")
        print("  pip install selenium webdriver-manager")
        print("  pip install playwright && playwright install chromium")

    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return df


if __name__ == "__main__":
    df = main()
