#!/usr/bin/env python3
"""
Fetch CV metrics from ORCID and Scopus APIs.
Updates _data/cv.yml with live counts.

Sources:
- ORCID: works count, DOI count (free, no auth)
- Scopus: h-index, citations, document count (requires API key)
"""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime

ORCID_ID = "0000-0003-0983-3319"
SCOPUS_AUTHOR_ID = "36774714200"
SCOPUS_API_KEY = os.environ.get("SCOPUS_API_KEY", "")
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


def fetch_scopus_metrics():
    """Fetch metrics from Scopus API."""
    url = f"https://api.elsevier.com/content/author?author_id={SCOPUS_AUTHOR_ID}&apiKey={SCOPUS_API_KEY}&httpAccept=application/json&field=h-index,citation-count,document-count,cited-by-count"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())

    author = data.get("author-retrieval-response", [{}])[0]
    coredata = author.get("coredata", {})

    return {
        "h_index": int(author.get("h-index", 0)),
        "citation_count": int(coredata.get("citation-count", 0)),
        "document_count": int(coredata.get("document-count", 0)),
        "cited_by_count": int(coredata.get("cited-by-count", 0)),
    }


def update_cv_yml(orcid_works, doi_count, scopus):
    """Update _data/cv.yml with live metrics."""
    with open(CV_FILE, "r") as f:
        content = f.read()

    year = datetime.utcnow().strftime("%Y")

    # Update ORCID line
    pattern = r'(- title: ORCID\n\s+year: ")\d+(")\n(\s+description: ")\d+ works \| \d+ DOIs \| (https://orcid\.org/[^"]+)(")'
    replacement = rf'\g<1>{year}\g<2>\n\g<3>{orcid_works} works | {doi_count} DOIs | \g<4>\g<5>'
    content = re.sub(pattern, replacement, content)

    # Update Scholar Metrics line with Scopus data
    pattern = r'(- title: Scopus\n\s+year: ")\d+(")\n(\s+description: "h-index: )\d+( \| Total citations: )[\d,]+\+?(\| <a href=.)'
    replacement = rf'\g<1>{year}\g<2>\n\g<3>{scopus["h_index"]}\g<4>{scopus["citation_count"]}+\5'
    content = re.sub(pattern, replacement, content)

    with open(CV_FILE, "w") as f:
        f.write(content)

    print(f"Updated metrics:")
    print(f"  ORCID: {orcid_works} works, {doi_count} DOIs")
    print(f"  Scopus: h-index={scopus['h_index']}, citations={scopus['citation_count']}")


def main():
    print(f"Fetching ORCID data for {ORCID_ID}...")
    orcid_data = fetch_orcid_works()
    works_count = len(orcid_data.get("group", []))
    dois = count_dois(orcid_data)
    doi_count = len(dois)

    print(f"Fetching Scopus metrics...")
    scopus = fetch_scopus_metrics()

    print(f"ORCID: {works_count} works, {doi_count} DOIs")
    print(f"Scopus: {scopus}")

    update_cv_yml(works_count, doi_count, scopus)


if __name__ == "__main__":
    try:
        main()
        print("Successfully updated CV metrics")
    except Exception as e:
        print(f"Error updating metrics: {e}", file=sys.stderr)
        sys.exit(1)
