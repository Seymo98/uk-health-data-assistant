#!/usr/bin/env python3
"""
Scrape organization information for each OpenSAFELY project.

The event log doesn't include organization names, only project slugs.
This script visits each project page to extract the organization(s).

Usage:
    python scripts/scrape_project_organizations.py

Output:
    data/project_organization_mapping.json
"""

import csv
import json
import logging
import re
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set

import requests
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
CSV_PATH = DATA_DIR / "opensafely_jobs_history.csv"
OUTPUT_PATH = DATA_DIR / "project_organization_mapping.json"

BASE_URL = "https://jobs.opensafely.org"
USER_AGENT = "UKHealthDataAssistant/1.0 (Organization Mapping)"


def get_unique_projects() -> Set[str]:
    """Extract unique project slugs from the CSV."""
    if not CSV_PATH.exists():
        logger.error(f"CSV file not found: {CSV_PATH}")
        return set()

    projects = set()
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # The "organization" column actually contains project slugs
            project_slug = row.get("organization", "").strip()
            if project_slug:
                projects.add(project_slug)

    logger.info(f"Found {len(projects)} unique projects in CSV")
    return projects


def scrape_project_organization(session: requests.Session, project_slug: str) -> Dict:
    """Scrape organization info from a project page."""
    url = f"{BASE_URL}/{project_slug}/"

    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        result = {
            "project_slug": project_slug,
            "project_name": None,
            "organizations": [],
            "url": url,
            "scraped_at": datetime.utcnow().isoformat(),
        }

        # Try to find project name from h1 or title
        h1 = soup.find("h1")
        if h1:
            result["project_name"] = h1.get_text(strip=True)

        # Look for organization information
        # Common patterns: "Organisation:", "Organizations:", links to org pages

        # Method 1: Look for explicit organization section
        org_section = soup.find(text=re.compile(r"organisation|organization", re.IGNORECASE))
        if org_section:
            parent = org_section.find_parent(["dt", "th", "label", "strong", "h2", "h3"])
            if parent:
                # Look for the value in the next sibling
                sibling = parent.find_next_sibling(["dd", "td", "span", "div", "p"])
                if sibling:
                    # Extract organization names/links
                    org_links = sibling.find_all("a")
                    for link in org_links:
                        org_name = link.get_text(strip=True)
                        org_href = link.get("href", "")
                        if org_name and not any(x in org_href for x in ["github", "docs", "staff"]):
                            result["organizations"].append({
                                "name": org_name,
                                "slug": org_href.strip("/").split("/")[0] if org_href else None
                            })

        # Method 2: Look in page metadata or breadcrumbs
        if not result["organizations"]:
            # Look for organization links in the page
            for link in soup.find_all("a", href=re.compile(r"^/[^/]+/$")):
                href = link.get("href", "")
                text = link.get_text(strip=True)

                # Skip common non-org links
                if any(x in href.lower() for x in ["login", "logout", "staff", "admin", "static", "api"]):
                    continue
                if href == f"/{project_slug}/":
                    continue

                # Check if this looks like an organization page (not a project page)
                # Usually org pages are one level deep
                slug = href.strip("/")
                if "/" not in slug and text and len(text) > 2:
                    # Verify this is likely an org by checking if text looks like an org name
                    # (not a navigation item)
                    if text.lower() not in ["home", "about", "contact", "help", "docs", "documentation"]:
                        # Check if this org is already in our list
                        existing_slugs = [o.get("slug") for o in result["organizations"]]
                        if slug not in existing_slugs:
                            result["organizations"].append({
                                "name": text,
                                "slug": slug
                            })

        # Method 3: Parse from description list (dl/dt/dd pattern)
        if not result["organizations"]:
            for dt in soup.find_all("dt"):
                dt_text = dt.get_text(strip=True).lower()
                if "organisation" in dt_text or "organization" in dt_text:
                    dd = dt.find_next_sibling("dd")
                    if dd:
                        for link in dd.find_all("a"):
                            org_name = link.get_text(strip=True)
                            org_href = link.get("href", "")
                            if org_name:
                                result["organizations"].append({
                                    "name": org_name,
                                    "slug": org_href.strip("/").split("/")[0] if org_href else None
                                })

        return result

    except requests.RequestException as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return {
            "project_slug": project_slug,
            "project_name": None,
            "organizations": [],
            "url": url,
            "error": str(e),
            "scraped_at": datetime.utcnow().isoformat(),
        }


def main():
    """Main scraping function."""
    logger.info("Starting project organization scraper")

    # Get unique projects
    projects = get_unique_projects()
    if not projects:
        logger.error("No projects found to scrape")
        return

    # Setup session
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })

    # Scrape each project
    mapping = {
        "metadata": {
            "scraped_at": datetime.utcnow().isoformat(),
            "total_projects": len(projects),
            "source": "jobs.opensafely.org project pages",
        },
        "projects": {}
    }

    for i, project_slug in enumerate(sorted(projects), 1):
        logger.info(f"Scraping {i}/{len(projects)}: {project_slug}")

        result = scrape_project_organization(session, project_slug)
        mapping["projects"][project_slug] = result

        # Rate limiting - be nice to the server
        if i < len(projects):
            time.sleep(0.5)

        # Progress update every 20 projects
        if i % 20 == 0:
            logger.info(f"Progress: {i}/{len(projects)} projects scraped")

    # Count results
    with_orgs = sum(1 for p in mapping["projects"].values() if p.get("organizations"))
    mapping["metadata"]["projects_with_organizations"] = with_orgs
    mapping["metadata"]["projects_without_organizations"] = len(projects) - with_orgs

    # Save output
    DATA_DIR.mkdir(exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved mapping to {OUTPUT_PATH}")
    logger.info(f"Projects with organizations: {with_orgs}/{len(projects)}")

    # Print summary of unique organizations found
    all_orgs = set()
    for project in mapping["projects"].values():
        for org in project.get("organizations", []):
            if org.get("name"):
                all_orgs.add(org["name"])

    logger.info(f"Unique organizations found: {len(all_orgs)}")
    if all_orgs:
        logger.info("Organizations:")
        for org in sorted(all_orgs):
            logger.info(f"  - {org}")


if __name__ == "__main__":
    main()
