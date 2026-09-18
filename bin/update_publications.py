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
preprint_count = 0
book_chapter_count = 0

for i, doi in enumerate(dois):
    try:
        req = urllib.request.Request(f"https://api.crossref.org/works/{doi}/transform/application/x-bibtex")
        with urllib.request.urlopen(req) as response:
            bib = response.read().decode().strip()
            
            # Check if this work is a preprint or book chapter by examining the structure from ORCID
            # Re-fetch work details to determine type
            work_type = "journal-article"  # default
            
            try:
                # Try to get work details to check if preprint  
                work_url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
                work_req = urllib.request.Request(work_url, headers={"Accept": "application/json"})
                with urllib.request.urlopen(work_req) as work_response:
                    work_data = json.loads(work_response.read().decode())
                    
                # Look for this specific DOI in the works
                for group in work_data.get('group', []):
                    for work in group.get('work-summary', []):
                        work_doi = None
                        for ext_id in work.get('external-ids', {}).get('external-id', []):
                            if ext_id.get('external-id-type') == 'doi':
                                work_doi = ext_id.get('external-id-value')
                                break
                        
                        if work_doi == doi:
                            work_type = work.get('type', 'journal-article')
                            break
            except Exception as e:
                print(f"Could not determine work type for DOI {doi}: {e}")
            
            # Modify BibTeX to mark preprints and book chapters
            if work_type == "preprint":
                preprint_count += 1
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
                book_chapter_count += 1
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
    if preprint_count > 0:
        print(f"Note: {preprint_count} preprints were marked in the bibliography")
    if book_chapter_count > 0:
        print(f"Note: {book_chapter_count} book chapters were marked in the bibliography")
else:
    print("No publications found.")