#!/usr/bin/env python3
"""
SAIL Databank Data Use Register Extractor

This script extracts the data use register from SAIL Databank using multiple methods:
1. Direct scraping from https://saildatabank.com/data/data-use-register/
2. HDR UK Gateway API (which includes SAIL data use registers)

Usage:
    python extract_sail_data_use_register.py

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
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Browser-like headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/json',
    'Accept-Language': 'en-GB,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

# Configuration
SAIL_BASE_URL = "https://saildatabank.com"
SAIL_REGISTER_URL = f"{SAIL_BASE_URL}/data/data-use-register/"
HDR_API_BASE = "https://api.www.healthdatagateway.org/api/v1"


class HDRGatewayAPI:
    """Client for HDR UK Gateway API to fetch data use registers."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.session.headers['Accept'] = 'application/json'

    def search_data_uses(self, search_terms=None, custodian=None, limit=1000):
        """
        Search for data uses via the HDR UK Gateway API.

        Args:
            search_terms: Optional search keywords
            custodian: Optional custodian name (e.g., 'SAIL')
            limit: Maximum number of results
        """
        try:
            # The search endpoint accepts POST requests
            url = f"{HDR_API_BASE}/search/dur"

            payload = {
                "limit": limit,
                "offset": 0,
            }

            if search_terms:
                payload["search"] = search_terms

            if custodian:
                payload["filters"] = {
                    "publisher": [custodian]
                }

            logger.info(f"Searching HDR UK Gateway for data uses... (custodian: {custodian or 'all'})")
            response = self.session.post(url, json=payload, timeout=60)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Found {len(data.get('data', []))} data use records")
            return data

        except requests.RequestException as e:
            logger.warning(f"Error searching HDR Gateway: {e}")
            return None

    def export_data_uses(self):
        """Export all data uses from HDR UK Gateway."""
        try:
            url = f"{HDR_API_BASE}/dur/export"
            logger.info("Exporting data uses from HDR UK Gateway...")
            response = self.session.get(url, timeout=120)
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get('Content-Type', '')
            if 'json' in content_type:
                return response.json()
            else:
                # Might be CSV or other format
                return response.text

        except requests.RequestException as e:
            logger.warning(f"Error exporting from HDR Gateway: {e}")
            return None

    def get_data_use(self, dur_id):
        """Get a specific data use by ID."""
        try:
            url = f"{HDR_API_BASE}/dur/{dur_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.warning(f"Error fetching DUR {dur_id}: {e}")
            return None

    def get_sail_data_uses(self):
        """
        Get all data uses specifically from SAIL Databank.

        The SAIL Databank may be listed under different names in the Gateway.
        """
        sail_terms = [
            "SAIL Databank",
            "SAIL",
            "Secure Anonymised Information Linkage",
            "Swansea University"
        ]

        all_results = []

        for term in sail_terms:
            result = self.search_data_uses(custodian=term)
            if result and result.get('data'):
                for record in result['data']:
                    # Check if it's actually SAIL-related
                    publisher = record.get('publisher', '')
                    if 'sail' in publisher.lower() or 'swansea' in publisher.lower():
                        all_results.append(record)

        # Also try a general search
        result = self.search_data_uses(search_terms="SAIL Databank")
        if result and result.get('data'):
            for record in result['data']:
                if record not in all_results:
                    all_results.append(record)

        # Remove duplicates based on ID
        unique_results = {r.get('id', str(i)): r for i, r in enumerate(all_results)}

        return list(unique_results.values())


class SAILDirectScraper:
    """Scraper for direct extraction from SAIL Databank website."""

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

    def parse_register_page(self, html):
        """Parse the SAIL data use register page."""
        soup = BeautifulSoup(html, 'lxml')
        projects = []

        # Strategy 1: Tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 1:
                headers = []
                header_row = table.find('thead')
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                else:
                    first_row = rows[0]
                    headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
                    rows = rows[1:]

                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        row_data = {}
                        for i, cell in enumerate(cells):
                            key = headers[i] if i < len(headers) else f'col_{i}'
                            row_data[key] = cell.get_text(strip=True)
                            link = cell.find('a', href=True)
                            if link:
                                href = link.get('href')
                                if not href.startswith('http'):
                                    href = urljoin(SAIL_BASE_URL, href)
                                row_data[f'{key}_link'] = href
                        if any(row_data.values()):
                            projects.append(row_data)

        # Strategy 2: Cards/Accordions
        if not projects:
            project_cards = soup.find_all(['div', 'article', 'li'],
                class_=re.compile(r'(project|card|item|entry|accordion)', re.I))

            for card in project_cards:
                title_elem = card.find(['h1', 'h2', 'h3', 'h4', 'h5', 'a'])
                if title_elem:
                    project = {'title': title_elem.get_text(strip=True)}
                    link = title_elem if title_elem.name == 'a' else title_elem.find('a')
                    if link and link.get('href'):
                        href = link.get('href')
                        if not href.startswith('http'):
                            href = urljoin(SAIL_BASE_URL, href)
                        project['project_link'] = href
                    projects.append(project)

        return projects

    def get_project_details(self, project_url):
        """Fetch detailed information from a project page."""
        html = self.get_page(project_url)
        if not html:
            return {}

        soup = BeautifulSoup(html, 'lxml')
        details = {'project_url': project_url}

        # Extract title
        title = soup.find('h1')
        if title:
            details['full_title'] = title.get_text(strip=True)

        # Field patterns to look for
        field_patterns = [
            ('Lead Organisation', 'lead_organisation'),
            ('Lead Applicant', 'lead_applicant'),
            ('Principal Investigator', 'principal_investigator'),
            ('Start Date', 'start_date'),
            ('End Date', 'end_date'),
            ('Status', 'status'),
            ('Datasets', 'datasets'),
            ('Research Summary', 'research_summary'),
            ('Lay Summary', 'lay_summary'),
            ('Public Benefit', 'public_benefit'),
            ('Approval Date', 'approval_date'),
            ('Project ID', 'project_id'),
            ('IGRP', 'igrp_number'),
        ]

        # Extract from definition lists
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

        # Extract from tables
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

        return details

    def scrape(self, include_details=True, max_workers=5):
        """Main scraping function."""
        html = self.get_page(SAIL_REGISTER_URL)
        if not html:
            logger.error("Failed to fetch the SAIL register page")
            return pd.DataFrame()

        # Save raw HTML
        with open('sail_register_raw.html', 'w', encoding='utf-8') as f:
            f.write(html)

        self.projects = self.parse_register_page(html)
        logger.info(f"Found {len(self.projects)} projects from direct scraping")

        # Fetch details
        if include_details and self.projects:
            project_urls = [p.get('project_link') or p.get('title_link') for p in self.projects]
            project_urls = [url for url in project_urls if url]

            if project_urls:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    future_to_url = {executor.submit(self.get_project_details, url): url
                                     for url in project_urls}

                    for future in as_completed(future_to_url):
                        url = future_to_url[future]
                        try:
                            details = future.result()
                            for proj in self.projects:
                                if proj.get('project_link') == url or proj.get('title_link') == url:
                                    proj.update(details)
                                    break
                        except Exception as e:
                            logger.warning(f"Error getting details: {e}")

        return pd.DataFrame(self.projects)


def normalize_hdr_record(record):
    """Convert HDR UK Gateway record to standardized format."""
    return {
        'project_id': record.get('id'),
        'project_title': record.get('projectTitle'),
        'organisation_name': record.get('organisationName'),
        'organisation_sector': record.get('organisationSector'),
        'lay_summary': record.get('laySummary'),
        'public_benefit_statement': record.get('publicBenefitStatement'),
        'technical_summary': record.get('technicalSummary'),
        'release_date': record.get('releaseDate'),
        'access_date': record.get('accessDate'),
        'datasets_used': record.get('datasetTitles'),
        'data_custodian': record.get('publisher'),
        'access_type': record.get('accessType'),
        'project_start_date': record.get('projectStartDate'),
        'project_end_date': record.get('projectEndDate'),
        'latest_approval_date': record.get('latestApprovalDate'),
        'research_outputs': record.get('researchOutputs'),
        'funding_source': record.get('fundingSource'),
        'gateway_url': record.get('gatewayUrl'),
        'source': 'HDR UK Gateway',
    }


def main():
    """Main entry point."""
    print("=" * 70)
    print("SAIL Databank Data Use Register Extractor")
    print("=" * 70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    all_records = []

    # Method 1: Try HDR UK Gateway API
    print("\n[1] Attempting HDR UK Gateway API...")
    try:
        hdr_api = HDRGatewayAPI()

        # Try export endpoint first
        export_data = hdr_api.export_data_uses()
        if export_data:
            if isinstance(export_data, dict) and 'data' in export_data:
                records = export_data['data']
            elif isinstance(export_data, list):
                records = export_data
            else:
                records = []

            logger.info(f"HDR Gateway export returned {len(records)} records")

            # Filter for SAIL-related records
            sail_records = []
            for record in records:
                publisher = str(record.get('publisher', '')).lower()
                datasets = str(record.get('datasetTitles', '')).lower()
                if 'sail' in publisher or 'sail' in datasets or 'swansea' in publisher:
                    sail_records.append(normalize_hdr_record(record))

            logger.info(f"Found {len(sail_records)} SAIL-related records from HDR Gateway")
            all_records.extend(sail_records)

        # Also try search endpoint for SAIL
        sail_results = hdr_api.get_sail_data_uses()
        for record in sail_results:
            normalized = normalize_hdr_record(record)
            if normalized not in all_records:
                all_records.append(normalized)

    except Exception as e:
        logger.warning(f"HDR Gateway API error: {e}")

    # Method 2: Direct scraping from SAIL website
    print("\n[2] Attempting direct scraping from SAIL Databank...")
    try:
        direct_scraper = SAILDirectScraper()
        df_direct = direct_scraper.scrape(include_details=True)

        if not df_direct.empty:
            # Add source column
            df_direct['source'] = 'SAIL Direct'

            # Merge with existing records
            for _, row in df_direct.iterrows():
                record = row.to_dict()
                record['source'] = 'SAIL Direct Scrape'
                all_records.append(record)

            logger.info(f"Direct scraping found {len(df_direct)} records")

    except Exception as e:
        logger.warning(f"Direct scraping error: {e}")

    # Create final DataFrame
    if all_records:
        df = pd.DataFrame(all_records)

        # Remove duplicates based on project_title or project_id
        if 'project_title' in df.columns:
            df = df.drop_duplicates(subset=['project_title'], keep='first')
        elif 'project_id' in df.columns:
            df = df.drop_duplicates(subset=['project_id'], keep='first')

        # Reorder columns
        priority_cols = [
            'project_id', 'project_title', 'organisation_name', 'lay_summary',
            'public_benefit_statement', 'datasets_used', 'data_custodian',
            'access_type', 'latest_approval_date', 'project_start_date',
            'project_end_date', 'source', 'gateway_url'
        ]
        existing_priority = [c for c in priority_cols if c in df.columns]
        other_cols = [c for c in df.columns if c not in existing_priority]
        df = df[existing_priority + other_cols]

        # Save to CSV
        output_file = 'sail_data_use_register.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"\n{'=' * 70}")
        print(f"EXTRACTION COMPLETE")
        print(f"{'=' * 70}")
        print(f"Total records: {len(df)}")
        print(f"Output file: {output_file}")
        print(f"Columns: {list(df.columns)}")
        print(f"\nFirst 5 records:")
        print(df.head().to_string())

    else:
        print("\nNo data could be extracted.")
        print("\nPossible solutions:")
        print("1. Run this script on a machine with unrestricted network access")
        print("2. Visit https://saildatabank.com/data/data-use-register/ directly")
        print("3. Access the HDR UK Gateway at https://www.healthdatagateway.org/")
        print("4. Contact SAIL Databank for API access")

    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return df if all_records else pd.DataFrame()


if __name__ == "__main__":
    df = main()
