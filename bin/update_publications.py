#!/usr/bin/env python3
import urllib.request
import json
import time
import os

# ORCID ID for Antti Karkman
orcid_id = "0000-0003-0983-3319"
url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"

print(f"Fetching works for ORCID: {orcid_id}")
req = urllib.request.Request(url, headers={"Accept": "application/json"})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())

dois = []
for group in data.get('group', []):
    for work in group.get('work-summary', []):
        for ext_id in work.get('external-ids', {}).get('external-id', []):
            if ext_id.get('external-id-type') == 'doi':
                dois.append(ext_id.get('external-id-value'))
                break # Just need one DOI per work

dois = list(set(dois))
print(f"Found {len(dois)} DOIs")

bibtex_entries = []
for i, doi in enumerate(dois):
    try:
        req = urllib.request.Request(f"https://api.crossref.org/works/{doi}/transform/application/x-bibtex")
        with urllib.request.urlopen(req) as response:
            bib = response.read().decode().strip()
            # Inject badges before the closing brace
            if bib.endswith('}'):
                bib = bib[:-1] + ',\n  altmetric={true},\n  dimensions={true}\n}'
            bibtex_entries.append(bib)
        print(f"Fetched bib for DOI: {doi}")
    except Exception as e:
        print(f"Failed to fetch {doi}: {e}")
    time.sleep(0.1) # Be nice to the Crossref API

if bibtex_entries:
    # Ensure the _bibliography directory exists
    os.makedirs("_bibliography", exist_ok=True)
    with open("_bibliography/papers.bib", "w") as f:
        f.write("\n\n".join(bibtex_entries))
    print(f"Successfully updated _bibliography/papers.bib with {len(bibtex_entries)} publications.")
else:
    print("No publications found.")
