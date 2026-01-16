#!/usr/bin/env python3
"""
Scrape project metadata from OpenSAFELY approved projects page.

The approved-projects page on opensafely.org has the actual organization data,
project titles, study leads, and approval dates.

Usage:
    python3 scripts/scrape_project_organizations.py

Output:
    data/project_organization_mapping.csv
    data/project_organization_mapping.json
"""

import csv
import json
import logging
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set, Any

import requests
from bs4 import BeautifulSoup
import pandas as pd

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
CSV_OUTPUT = DATA_DIR / "project_organization_mapping.csv"
JSON_OUTPUT = DATA_DIR / "project_organization_mapping.json"
JOBS_CSV = DATA_DIR / "opensafely_jobs_history.csv"

USER_AGENT = "UKHealthDataAssistant/1.0 (Project Metadata Scraper)"


def scrape_approved_projects() -> Optional[pd.DataFrame]:
    """Scrape project metadata from opensafely.org/approved-projects/"""

    url = "https://www.opensafely.org/approved-projects/"
    logger.info(f"Fetching approved projects from {url}")

    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=60)

    if response.status_code != 200:
        logger.error(f"Failed to fetch page. Status: {response.status_code}")
        return None

    logger.info("Page fetched. Parsing project data...")
    soup = BeautifulSoup(response.content, 'html.parser')

    projects_data = []

    # Search for details blocks which contain project info
    potential_entries = soup.find_all('details')

    # Fallback: if 'details' structure isn't used, search generic blocks
    if not potential_entries:
        potential_entries = soup.find_all(['div', 'li'])

    logger.info(f"Scanning {len(potential_entries)} page elements...")

    for entry in potential_entries:
        text = entry.get_text(" | ", strip=True)

        if "Project #" in text and "Study lead:" in text:

            # Extract Project ID
            id_match = re.search(r"Project\s*#(\d+)", text)
            project_id = id_match.group(1) if id_match else None

            # Extract Organisation
            org_match = re.search(
                r"Organisation:\s*(.*?)(?:\s\|\sProject type|\s\|\sTopic area|\s\|\sDate|$)",
                text
            )
            organization = org_match.group(1).strip() if org_match else "Unknown"

            # Extract Study Lead
            lead_match = re.search(
                r"Study lead:\s*(.*?)(?:\s\|\sOrganisation|\s\|\sProject type|$)",
                text
            )
            study_lead = lead_match.group(1).strip() if lead_match else "Unknown"

            # Extract Title
            title_match = re.search(
                r"Project\s*#\d+[:\s\|]+(.*?)(?:\s\|\sStudy lead|\s\|\sThe|\.|$)",
                text
            )
            if title_match:
                title = title_match.group(1).strip()
            else:
                title = text.split(f"Project #{project_id}")[-1].split("|")[0].strip()

            title = title.lstrip(":| ").strip()

            # Extract Approval Date
            date_match = re.search(r"Date of approval:\s*([\d-]+)", text)
            approval_date = date_match.group(1).strip() if date_match else None

            # Extract Project Type
            type_match = re.search(r"Project type:\s*(.*?)(?:\s\|\s|$)", text)
            project_type = type_match.group(1).strip() if type_match else None

            # Extract Topic Area
            topic_match = re.search(r"Topic area:\s*(.*?)(?:\s\|\s|$)", text)
            topic_area = topic_match.group(1).strip() if topic_match else None

            # Project Status
            status = "Active"
            if "Completed" in text:
                status = "Completed"

            projects_data.append({
                "project_id": project_id,
                "project_title": title,
                "organization": organization,
                "study_lead": study_lead,
                "approval_date": approval_date,
                "project_type": project_type,
                "topic_area": topic_area,
                "project_status": status,
            })

    if not projects_data:
        logger.error("No projects found. Page structure may have changed.")
        return None

    # Create DataFrame and deduplicate
    df = pd.DataFrame(projects_data).drop_duplicates(subset=['project_id'])

    # Clean up titles
    df['project_title'] = df['project_title'].str.split("View project").str[0].str.strip()

    logger.info(f"Found {len(df)} unique approved projects")
    return df


def load_job_history_projects() -> Set[str]:
    """Get unique project slugs from job history CSV."""
    if not JOBS_CSV.exists():
        logger.warning(f"Jobs CSV not found: {JOBS_CSV}")
        return set()

    projects = set()
    with open(JOBS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            slug = row.get('organization', '').strip()  # Actually project slug
            if slug:
                projects.add(slug)

    logger.info(f"Found {len(projects)} unique project slugs in job history")
    return projects


def create_slug_from_id(project_id: str) -> str:
    """Create a potential slug pattern from project ID."""
    return f"{project_id}-"


def main():
    """Main function to scrape and save project metadata."""
    logger.info("Starting project metadata scraper")

    # Scrape approved projects
    df = scrape_approved_projects()

    if df is None or df.empty:
        logger.error("Failed to scrape projects")
        return

    # Load existing job history projects for matching
    job_projects = load_job_history_projects()

    # Try to match approved projects to job history slugs
    def find_matching_slug(row):
        project_id = row['project_id']
        title = row['project_title'].lower() if pd.notna(row['project_title']) else ''

        for slug in job_projects:
            # Match by project ID prefix (e.g., "112-" matches "112-coronavirus...")
            if slug.startswith(f"{project_id}-"):
                return slug
            # Match by title similarity (simplified)
            title_words = set(re.findall(r'\w+', title))
            slug_words = set(slug.split('-'))
            if len(title_words & slug_words) >= 3:
                return slug
        return None

    df['job_history_slug'] = df.apply(find_matching_slug, axis=1)

    matched = df['job_history_slug'].notna().sum()
    logger.info(f"Matched {matched}/{len(df)} projects to job history slugs")

    # Save CSV
    DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(CSV_OUTPUT, index=False)
    logger.info(f"Saved CSV to {CSV_OUTPUT}")

    # Save JSON with additional metadata
    result = {
        "metadata": {
            "scraped_at": datetime.utcnow().isoformat(),
            "source": "https://www.opensafely.org/approved-projects/",
            "total_projects": len(df),
            "matched_to_job_history": matched,
        },
        "projects": df.to_dict(orient='records'),
        "organizations": {}
    }

    # Aggregate by organization
    for _, row in df.iterrows():
        org = row['organization']
        if org and org != "Unknown":
            if org not in result["organizations"]:
                result["organizations"][org] = {
                    "name": org,
                    "project_count": 0,
                    "project_ids": []
                }
            result["organizations"][org]["project_count"] += 1
            result["organizations"][org]["project_ids"].append(row['project_id'])

    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved JSON to {JSON_OUTPUT}")

    # Print organization summary
    logger.info(f"\nUnique organizations: {len(result['organizations'])}")
    logger.info("\nTop organizations by project count:")
    sorted_orgs = sorted(
        result["organizations"].items(),
        key=lambda x: x[1]["project_count"],
        reverse=True
    )[:15]
    for org_name, org_data in sorted_orgs:
        logger.info(f"  {org_name}: {org_data['project_count']} projects")


if __name__ == "__main__":
    main()
