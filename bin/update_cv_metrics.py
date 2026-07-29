#!/usr/bin/env python3
"""
Fetch CV metrics from ORCID and OpenAlex APIs.
Updates _data/cv.yml with live counts.

Sources:
- ORCID: works count, DOI count (free, no auth) - accurate publication count
- OpenAlex: h-index, citations, i10-index (free, no auth) - comprehensive metrics
"""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime

ORCID_ID = "0000-0003-0983-3319"
CV_FILE = os.path.join(os.path.dirname(__file__), "..", "_data", "cv.yml")


def fetch_orcid_works():
    """Fetch works from ORCID API."""
    url = f"https://pub.orcid.org/v3.0/{ORCID_ID}/works"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())


def count_dois(data):
    """Count unique DOIs from ORCID works."""
    dois = set()
    for group in data.get("group", []):
        for work in group.get("work-summary", []):
            for ext_id in work.get("external-ids", {}).get("external-id", []):
                if ext_id.get("external-id-type") == "doi":
                    dois.add(ext_id.get("external-id-value"))
                    break
    return dois


def fetch_openalex_metrics():
    """Fetch citation metrics from OpenAlex API."""
    url = f"https://api.openalex.org/authors?filter=orcid:{ORCID_ID}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())

    author = data.get("results", [{}])[0]
    stats = author.get("summary_stats", {})

    return {
        "cited_by_count": author.get("cited_by_count", 0),
        "h_index": stats.get("h_index", 0),
        "i10_index": stats.get("i10_index", 0),
    }


def update_cv_yml(orcid_works, doi_count, openalex):
    """Update _data/cv.yml with live metrics."""
    with open(CV_FILE, "r") as f:
        content = f.read()

    year = datetime.utcnow().strftime("%Y")

    # Update ORCID line
    pattern = r'(- title: ORCID\n\s+year: ")\d+(")\n(\s+description: ")\d+ works \| \d+ DOIs \| (https://orcid\.org/[^"]+)(")'
    replacement = rf'\g<1>{year}\g<2>\n\g<3>{orcid_works} works | {doi_count} DOIs | \g<4>\g<5>'
    content = re.sub(pattern, replacement, content)

    # Update Scopus line with OpenAlex citation metrics
    pattern = r'(- title: Scopus\n\s+year: ")\d+(")\n(\s+description: "h-index: )\d+( \| Total citations: )[\d,]+\+?'
    replacement = rf'\g<1>{year}\g<2>\n\g<3>{openalex["h_index"]}\g<4>{openalex["cited_by_count"]}+'
    content = re.sub(pattern, replacement, content)

    with open(CV_FILE, "w") as f:
        f.write(content)

    print(f"Updated metrics:")
    print(f"  ORCID: {orcid_works} works, {doi_count} DOIs")
    print(f"  OpenAlex: h-index={openalex['h_index']}, i10-index={openalex['i10_index']}, citations={openalex['cited_by_count']}")


def main():
    print(f"Fetching ORCID data for {ORCID_ID}...")
    orcid_data = fetch_orcid_works()
    works_count = len(orcid_data.get("group", []))
    dois = count_dois(orcid_data)
    doi_count = len(dois)

    print(f"Fetching OpenAlex metrics...")
    openalex = fetch_openalex_metrics()

    print(f"ORCID: {works_count} works, {doi_count} DOIs")
    print(f"OpenAlex: {openalex}")

    update_cv_yml(works_count, doi_count, openalex)


if __name__ == "__main__":
    try:
        main()
        print("Successfully updated CV metrics")
    except Exception as e:
        print(f"Error updating metrics: {e}", file=sys.stderr)
        sys.exit(1)
