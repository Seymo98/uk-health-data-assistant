#!/usr/bin/env python3
"""
Scrape full metadata for each OpenSAFELY project.

The event log doesn't include organization names or project details.
This script visits each project page to extract all available metadata.

Usage:
    python3 scripts/scrape_project_organizations.py

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
from typing import Dict, List, Optional, Set, Any

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
USER_AGENT = "UKHealthDataAssistant/1.0 (Project Metadata Scraper)"


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


def extract_text_after_label(soup: BeautifulSoup, label_patterns: List[str]) -> Optional[str]:
    """Find text content after a label (dt/dd, th/td, label/span patterns)."""
    for pattern in label_patterns:
        # Try dt/dd pattern
        for dt in soup.find_all("dt"):
            if pattern.lower() in dt.get_text(strip=True).lower():
                dd = dt.find_next_sibling("dd")
                if dd:
                    return dd.get_text(strip=True)

        # Try th/td pattern
        for th in soup.find_all("th"):
            if pattern.lower() in th.get_text(strip=True).lower():
                td = th.find_next_sibling("td")
                if td:
                    return td.get_text(strip=True)

        # Try label pattern
        for label in soup.find_all(["label", "strong", "b"]):
            if pattern.lower() in label.get_text(strip=True).lower():
                parent = label.find_parent()
                if parent:
                    # Get text excluding the label
                    label_text = label.get_text(strip=True)
                    full_text = parent.get_text(strip=True)
                    return full_text.replace(label_text, "").strip().lstrip(":").strip()

    return None


def extract_links_after_label(soup: BeautifulSoup, label_patterns: List[str]) -> List[Dict[str, str]]:
    """Find links after a label."""
    links = []
    for pattern in label_patterns:
        for dt in soup.find_all("dt"):
            if pattern.lower() in dt.get_text(strip=True).lower():
                dd = dt.find_next_sibling("dd")
                if dd:
                    for a in dd.find_all("a"):
                        links.append({
                            "name": a.get_text(strip=True),
                            "url": a.get("href", ""),
                            "slug": a.get("href", "").strip("/").split("/")[0] if a.get("href") else None
                        })
    return links


def scrape_project_metadata(session: requests.Session, project_slug: str) -> Dict[str, Any]:
    """Scrape all metadata from a project page."""
    url = f"{BASE_URL}/{project_slug}/"

    result = {
        "project_slug": project_slug,
        "url": url,
        "scraped_at": datetime.utcnow().isoformat(),
        # Core fields
        "project_name": None,
        "organizations": [],
        "status": None,
        "description": None,
        # Counts
        "member_count": None,
        "workspace_count": None,
        "job_request_count": None,
        # Links
        "github_url": None,
        "documentation_url": None,
        # Dates
        "created_at": None,
        "updated_at": None,
        # Raw data for debugging
        "all_metadata": {},
        "error": None,
    }

    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        # Project name from h1
        h1 = soup.find("h1")
        if h1:
            result["project_name"] = h1.get_text(strip=True)

        # Description - often in a <p> after the h1 or in a specific section
        desc_elem = soup.find("p", class_=re.compile(r"desc|summary|lead", re.IGNORECASE))
        if not desc_elem:
            # Try first paragraph after h1
            if h1:
                desc_elem = h1.find_next("p")
        if desc_elem:
            desc_text = desc_elem.get_text(strip=True)
            if len(desc_text) > 20:  # Likely a real description
                result["description"] = desc_text

        # Organizations - try multiple patterns
        result["organizations"] = extract_links_after_label(
            soup, ["organisation", "organization", "org"]
        )

        # If no orgs found via dt/dd, look for org links in the page
        if not result["organizations"]:
            # Look for links that appear to be organization pages
            for link in soup.find_all("a", href=re.compile(r"^/[a-z0-9-]+/$")):
                href = link.get("href", "")
                text = link.get_text(strip=True)
                slug = href.strip("/")

                # Skip if it's the project itself or common non-org links
                if slug == project_slug:
                    continue
                if any(x in slug for x in ["login", "logout", "staff", "admin", "static", "api", "docs"]):
                    continue
                if "/" in slug:  # Not a top-level page
                    continue

                # Check if this looks like an org (has reasonable name)
                if text and len(text) > 2 and text.lower() not in ["home", "about", "help"]:
                    # Avoid duplicates
                    existing = [o["slug"] for o in result["organizations"]]
                    if slug not in existing:
                        result["organizations"].append({
                            "name": text,
                            "url": href,
                            "slug": slug
                        })

        # Status
        status_text = extract_text_after_label(soup, ["status"])
        if status_text:
            result["status"] = status_text.lower()
            result["all_metadata"]["status"] = status_text

        # Member count
        members_text = extract_text_after_label(soup, ["member", "researcher", "team"])
        if members_text:
            result["all_metadata"]["members_raw"] = members_text
            match = re.search(r"(\d+)", members_text)
            if match:
                result["member_count"] = int(match.group(1))

        # Workspace count
        ws_text = extract_text_after_label(soup, ["workspace"])
        if ws_text:
            result["all_metadata"]["workspaces_raw"] = ws_text
            match = re.search(r"(\d+)", ws_text)
            if match:
                result["workspace_count"] = int(match.group(1))

        # GitHub link
        for a in soup.find_all("a", href=re.compile(r"github\.com", re.IGNORECASE)):
            result["github_url"] = a.get("href")
            break

        # Collect all dt/dd pairs for reference
        for dt in soup.find_all("dt"):
            dd = dt.find_next_sibling("dd")
            if dd:
                key = dt.get_text(strip=True).lower().replace(":", "").strip()
                value = dd.get_text(strip=True)
                result["all_metadata"][key] = value

        # Look for counts in the page (workspaces, jobs, etc.)
        for text in soup.stripped_strings:
            # Pattern: "X workspaces" or "X job requests"
            match = re.match(r"(\d+)\s+(workspace|job|member|request)", text.lower())
            if match:
                count = int(match.group(1))
                item_type = match.group(2)
                result["all_metadata"][f"{item_type}_count_from_text"] = count

    except requests.RequestException as e:
        logger.error(f"Failed to scrape {url}: {e}")
        result["error"] = str(e)

    return result


def main():
    """Main scraping function."""
    logger.info("Starting project metadata scraper")

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
        "projects": {},
        "organizations": {},  # Aggregate org info
    }

    all_orgs = {}  # Track all organizations found

    for i, project_slug in enumerate(sorted(projects), 1):
        logger.info(f"Scraping {i}/{len(projects)}: {project_slug}")

        result = scrape_project_metadata(session, project_slug)
        mapping["projects"][project_slug] = result

        # Track organizations
        for org in result.get("organizations", []):
            org_slug = org.get("slug")
            if org_slug:
                if org_slug not in all_orgs:
                    all_orgs[org_slug] = {
                        "name": org.get("name"),
                        "slug": org_slug,
                        "projects": []
                    }
                all_orgs[org_slug]["projects"].append(project_slug)

        # Rate limiting - be nice to the server
        if i < len(projects):
            time.sleep(0.5)

        # Progress update every 20 projects
        if i % 20 == 0:
            logger.info(f"Progress: {i}/{len(projects)} projects scraped")

    # Add organization summary
    mapping["organizations"] = all_orgs

    # Count results
    with_orgs = sum(1 for p in mapping["projects"].values() if p.get("organizations"))
    with_status = sum(1 for p in mapping["projects"].values() if p.get("status"))
    with_github = sum(1 for p in mapping["projects"].values() if p.get("github_url"))
    errors = sum(1 for p in mapping["projects"].values() if p.get("error"))

    mapping["metadata"]["projects_with_organizations"] = with_orgs
    mapping["metadata"]["projects_with_status"] = with_status
    mapping["metadata"]["projects_with_github"] = with_github
    mapping["metadata"]["projects_with_errors"] = errors
    mapping["metadata"]["unique_organizations"] = len(all_orgs)

    # Save output
    DATA_DIR.mkdir(exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved mapping to {OUTPUT_PATH}")
    logger.info(f"Results:")
    logger.info(f"  Projects scraped: {len(projects)}")
    logger.info(f"  With organizations: {with_orgs}")
    logger.info(f"  With status: {with_status}")
    logger.info(f"  With GitHub: {with_github}")
    logger.info(f"  Errors: {errors}")
    logger.info(f"  Unique organizations: {len(all_orgs)}")

    if all_orgs:
        logger.info("\nOrganizations found:")
        for org_slug, org_data in sorted(all_orgs.items(), key=lambda x: -len(x[1]["projects"])):
            logger.info(f"  {org_data['name']}: {len(org_data['projects'])} projects")


if __name__ == "__main__":
    main()
