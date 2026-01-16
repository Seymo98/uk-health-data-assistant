#!/usr/bin/env python3
"""
OpenSAFELY Event Log Scraper.

Scrapes the complete job history from jobs.opensafely.org/event-log/
and saves it to a CSV file for use in the dashboard.

Usage:
    python scripts/scrape_opensafely_event_log.py

Output:
    data/opensafely_jobs_history.csv
"""

import argparse
import csv
import json
import logging
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://jobs.opensafely.org"
EVENT_LOG_URL = f"{BASE_URL}/event-log/"
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "data"
DEFAULT_OUTPUT_FILE = "opensafely_jobs_history.csv"
METADATA_FILE = "opensafely_jobs_metadata.json"

# Rate limiting
REQUESTS_PER_SECOND = 2  # Be respectful to the server
REQUEST_DELAY = 1.0 / REQUESTS_PER_SECOND


class OpenSAFELYEventLogScraper:
    """Scraper for OpenSAFELY job event log."""

    def __init__(self, output_dir: Path = DEFAULT_OUTPUT_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Setup session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update({
            "User-Agent": "OpenSAFELY-Dashboard-Scraper/1.0 (Research Transparency Project)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })

        self.jobs_scraped = 0
        self.pages_scraped = 0
        self.errors = []

    def get_total_pages(self) -> int:
        """Get the total number of pages in the event log."""
        try:
            response = self.session.get(EVENT_LOG_URL, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            # Look for pagination info - usually shows "Page X of Y"
            # or look for the last page number link
            pagination = soup.find("nav", {"aria-label": "Pagination"})
            if pagination:
                # Find all page number links
                page_links = pagination.find_all("a")
                page_numbers = []
                for link in page_links:
                    text = link.get_text(strip=True)
                    if text.isdigit():
                        page_numbers.append(int(text))
                if page_numbers:
                    return max(page_numbers)

            # Alternative: look for "Page X of Y" text
            page_info = soup.find(text=re.compile(r"Page \d+ of \d+"))
            if page_info:
                match = re.search(r"of (\d+)", page_info)
                if match:
                    return int(match.group(1))

            # Fallback: estimate from job count if available
            # The user mentioned 988 pages
            logger.warning("Could not determine total pages, using estimate of 988")
            return 988

        except Exception as e:
            logger.error(f"Failed to get total pages: {e}")
            return 988  # User provided this number

    def parse_job_row(self, row) -> Optional[Dict[str, Any]]:
        """Parse a single job request row from the table."""
        try:
            cells = row.find_all(["td", "th"])
            if len(cells) < 7:
                return None

            # Extract status from icon/class
            status_cell = cells[0]
            status = "unknown"
            status_icon = status_cell.find("svg") or status_cell.find("span")
            if status_icon:
                # Check class names for status
                classes = " ".join(status_icon.get("class", []))
                if "success" in classes.lower() or "green" in classes.lower():
                    status = "succeeded"
                elif "fail" in classes.lower() or "red" in classes.lower():
                    status = "failed"
                elif "running" in classes.lower() or "yellow" in classes.lower() or "amber" in classes.lower():
                    status = "running"
                elif "pending" in classes.lower() or "gray" in classes.lower():
                    status = "pending"

            # Also check text content
            status_text = status_cell.get_text(strip=True).lower()
            if "succeeded" in status_text:
                status = "succeeded"
            elif "failed" in status_text:
                status = "failed"
            elif "running" in status_text:
                status = "running"
            elif "pending" in status_text:
                status = "pending"

            # Extract project
            project_cell = cells[1]
            project_link = project_cell.find("a")
            project_name = project_link.get_text(strip=True) if project_link else project_cell.get_text(strip=True)
            project_url = project_link.get("href", "") if project_link else ""

            # Extract organization from project URL or nearby text
            org_name = ""
            if project_url:
                # URL format is typically /{org}/{project}/
                parts = project_url.strip("/").split("/")
                if len(parts) >= 1:
                    org_name = parts[0]

            # Extract workspace
            workspace_cell = cells[2]
            workspace_link = workspace_cell.find("a")
            workspace_name = workspace_link.get_text(strip=True) if workspace_link else workspace_cell.get_text(strip=True)
            workspace_url = workspace_link.get("href", "") if workspace_link else ""

            # Extract user
            user_cell = cells[3]
            user_name = user_cell.get_text(strip=True)

            # Extract jobs count (e.g., "3/5")
            jobs_cell = cells[4]
            jobs_text = jobs_cell.get_text(strip=True)
            jobs_completed = 0
            jobs_total = 0
            jobs_match = re.search(r"(\d+)/(\d+)", jobs_text)
            if jobs_match:
                jobs_completed = int(jobs_match.group(1))
                jobs_total = int(jobs_match.group(2))

            # Extract backend
            backend_cell = cells[5]
            backend = backend_cell.get_text(strip=True).lower()

            # Extract timestamp
            started_cell = cells[6]
            time_elem = started_cell.find("time")
            started_at = ""
            started_at_iso = ""
            if time_elem:
                started_at_iso = time_elem.get("datetime", "")
                started_at = time_elem.get_text(strip=True)
            else:
                started_at = started_cell.get_text(strip=True)

            # Extract job request ID from view link
            job_request_id = ""
            if len(cells) > 7:
                view_cell = cells[7]
                view_link = view_cell.find("a")
                if view_link:
                    href = view_link.get("href", "")
                    # URL format: /{workspace}/job-requests/{id}/
                    id_match = re.search(r"/job-requests/([^/]+)/", href)
                    if id_match:
                        job_request_id = id_match.group(1)

            return {
                "job_request_id": job_request_id,
                "status": status,
                "organization": org_name,
                "project": project_name,
                "project_url": project_url,
                "workspace": workspace_name,
                "workspace_url": workspace_url,
                "user": user_name,
                "jobs_completed": jobs_completed,
                "jobs_total": jobs_total,
                "backend": backend,
                "started_at": started_at,
                "started_at_iso": started_at_iso,
            }

        except Exception as e:
            logger.debug(f"Failed to parse row: {e}")
            return None

    def scrape_page(self, page_num: int) -> List[Dict[str, Any]]:
        """Scrape a single page of the event log."""
        url = f"{EVENT_LOG_URL}?page={page_num}"
        jobs = []

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            # Find the table
            table = soup.find("table")
            if not table:
                logger.warning(f"No table found on page {page_num}")
                return jobs

            # Find all rows (skip header)
            tbody = table.find("tbody")
            if tbody:
                rows = tbody.find_all("tr")
            else:
                rows = table.find_all("tr")[1:]  # Skip header row

            for row in rows:
                job = self.parse_job_row(row)
                if job:
                    jobs.append(job)

            logger.debug(f"Page {page_num}: found {len(jobs)} jobs")

        except requests.RequestException as e:
            logger.error(f"Failed to fetch page {page_num}: {e}")
            self.errors.append({"page": page_num, "error": str(e)})
        except Exception as e:
            logger.error(f"Error parsing page {page_num}: {e}")
            self.errors.append({"page": page_num, "error": str(e)})

        return jobs

    def scrape_all(self, start_page: int = 1, end_page: Optional[int] = None,
                   progress_callback=None) -> List[Dict[str, Any]]:
        """Scrape all pages of the event log."""
        if end_page is None:
            end_page = self.get_total_pages()

        logger.info(f"Starting scrape from page {start_page} to {end_page}")

        all_jobs = []

        for page_num in range(start_page, end_page + 1):
            jobs = self.scrape_page(page_num)
            all_jobs.extend(jobs)

            self.pages_scraped += 1
            self.jobs_scraped += len(jobs)

            if progress_callback:
                progress_callback(page_num, end_page, len(all_jobs))

            # Progress logging every 10 pages
            if page_num % 10 == 0:
                logger.info(f"Progress: {page_num}/{end_page} pages, {len(all_jobs)} jobs scraped")

            # Rate limiting
            time.sleep(REQUEST_DELAY)

        logger.info(f"Scraping complete: {len(all_jobs)} jobs from {self.pages_scraped} pages")

        if self.errors:
            logger.warning(f"Encountered {len(self.errors)} errors during scraping")

        return all_jobs

    def save_to_csv(self, jobs: List[Dict[str, Any]], filename: str = DEFAULT_OUTPUT_FILE):
        """Save jobs to CSV file."""
        output_path = self.output_dir / filename

        if not jobs:
            logger.warning("No jobs to save")
            return output_path

        fieldnames = [
            "job_request_id", "status", "organization", "project", "project_url",
            "workspace", "workspace_url", "user", "jobs_completed", "jobs_total",
            "backend", "started_at", "started_at_iso"
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(jobs)

        logger.info(f"Saved {len(jobs)} jobs to {output_path}")
        return output_path

    def save_metadata(self, jobs_count: int, pages_count: int):
        """Save metadata about the scrape."""
        metadata = {
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "last_updated_formatted": datetime.utcnow().strftime("%d %B %Y at %H:%M UTC"),
            "total_jobs": jobs_count,
            "total_pages": pages_count,
            "errors_count": len(self.errors),
            "source_url": EVENT_LOG_URL,
        }

        metadata_path = self.output_dir / METADATA_FILE
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Saved metadata to {metadata_path}")
        return metadata_path


def main():
    parser = argparse.ArgumentParser(description="Scrape OpenSAFELY event log")
    parser.add_argument("--start-page", type=int, default=1, help="Start page number")
    parser.add_argument("--end-page", type=int, default=None, help="End page number (default: all)")
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_OUTPUT_DIR), help="Output directory")
    parser.add_argument("--output-file", type=str, default=DEFAULT_OUTPUT_FILE, help="Output CSV filename")
    parser.add_argument("--test", action="store_true", help="Test mode: only scrape first 3 pages")
    args = parser.parse_args()

    if args.test:
        args.end_page = 3
        logger.info("Running in test mode (3 pages only)")

    scraper = OpenSAFELYEventLogScraper(output_dir=Path(args.output_dir))

    def progress_callback(current, total, jobs_count):
        pct = (current / total) * 100
        print(f"\rProgress: {current}/{total} pages ({pct:.1f}%) - {jobs_count} jobs", end="", flush=True)

    jobs = scraper.scrape_all(
        start_page=args.start_page,
        end_page=args.end_page,
        progress_callback=progress_callback
    )

    print()  # New line after progress

    if jobs:
        csv_path = scraper.save_to_csv(jobs, args.output_file)
        scraper.save_metadata(len(jobs), scraper.pages_scraped)

        print(f"\nScraping complete!")
        print(f"  - Total jobs: {len(jobs)}")
        print(f"  - Pages scraped: {scraper.pages_scraped}")
        print(f"  - Output: {csv_path}")

        if scraper.errors:
            print(f"  - Errors: {len(scraper.errors)}")
    else:
        print("\nNo jobs were scraped. Check the logs for errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
