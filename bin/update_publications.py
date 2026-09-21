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

# Collect unique DOI and work type information from the main ORCID data
doi_to_type = {}  # Map DOI to work type to avoid duplicates
doi_to_title = {}

for group in data.get('group', []):
    for work in group.get('work-summary', []):
        work_type = work.get('type')
        
        # Get DOI if available
        doi = None
        for ext_id in work.get('external-ids', {}).get('external-id', []):
            if ext_id.get('external-id-type') == 'doi':
                doi = ext_id.get('external-id-value')
                break
        
        if doi:  # Only include works that have DOI
            # Only store the first occurrence of each DOI to avoid duplicates
            if doi not in doi_to_type:
                doi_to_type[doi] = work_type
                title = work.get('title', {}).get('title', {}).get('value', 'No title')
                doi_to_title[doi] = title

print(f"Found {len(doi_to_type)} unique works with DOIs")
preprints = [doi for doi, type_ in doi_to_type.items() if type_ == 'preprint']
book_chapters = [doi for doi, type_ in doi_to_type.items() if type_ == 'book-chapter']
print(f"Found {len(preprints)} preprints and {len(book_chapters)} book chapters")

bibtex_entries = []
for doi, work_type in doi_to_type.items():
    title = doi_to_title[doi]
    
    try:
        req = urllib.request.Request(f"https://api.crossref.org/works/{doi}/transform/application/x-bibtex")
        with urllib.request.urlopen(req) as response:
            bib = response.read().decode().strip()
            
            # Modify BibTeX to mark preprints and book chapters
            if work_type == "preprint":
                if bib.endswith('}'):
                    # Find journal field and replace with "preprint"
                    lines = bib.split('\n')
                    new_lines = []
                    journal_found = False
                    
                    for line in lines:
                        if line.startswith('  journal = '):
                            # Replace with preprint marker
                            new_lines.append('  journal = {Preprint},')
                            journal_found = True
                        else:
                            new_lines.append(line)
                    
                    bib = '\n'.join(new_lines)
            elif work_type == "book-chapter":
                if bib.endswith('}'):
                    # Find journal field and replace with "Book Chapter"
                    lines = bib.split('\n')
                    new_lines = []
                    journal_found = False
                    
                    for line in lines:
                        if line.startswith('  journal = '):
                            # Replace with book chapter marker  
                            new_lines.append('  journal = {Book Chapter},')
                            journal_found = True
                        else:
                            new_lines.append(line)
                    
                    bib = '\n'.join(new_lines)
            
            # Inject badges before the closing brace
            if bib.endswith('}'):
                bib = bib[:-1] + ',\n  altmetric={true},\n  dimensions={true}\n}'
            bibtex_entries.append(bib)
        print(f"Fetched bib for DOI: {doi} (type: {work_type})")
    except Exception as e:
        print(f"Failed to fetch {doi}: {e}")
    time.sleep(0.1) # Be nice to the Crossref API

if bibtex_entries:
    # Ensure the _bibliography directory exists
    os.makedirs("_bibliography", exist_ok=True)
    with open("_bibliography/papers.bib", "w") as f:
        f.write("\n\n".join(bibtex_entries))
    print(f"Successfully updated _bibliography/papers.bib with {len(bibtex_entries)} publications.")
    if len(preprints) > 0:
        print(f"Note: {len(preprints)} preprints were marked in the bibliography")
    if len(book_chapters) > 0:
        print(f"Note: {len(book_chapters)} book chapters were marked in the bibliography")
else:
    print("No publications found.")