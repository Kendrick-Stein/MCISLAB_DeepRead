#!/usr/bin/env python3
"""
BibTeX Parser and Completeness Checker
"""

import re
import json
from collections import defaultdict

def parse_bibtex_file(filepath):
    """Parse a BibTeX file and return all entries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match BibTeX entries
    pattern = r'@\s*(\w+)\s*\{\s*([^,]+)\s*,([^@]*?)\n\s*\}'
    entries = re.findall(pattern, content, re.DOTALL)

    parsed_entries = []
    for entry_type, key, fields_text in entries:
        fields = parse_fields(fields_text)
        parsed_entries.append({
            'type': entry_type.lower(),
            'key': key.strip(),
            'fields': fields
        })

    return parsed_entries

def parse_fields(fields_text):
    """Parse the fields of a BibTeX entry."""
    fields = {}
    # Match field = {value} or field = "value" patterns
    field_pattern = r'\s*(\w+)\s*=\s*\{([^}]*)\}'
    for match in re.finditer(field_pattern, fields_text):
        field_name = match.group(1).lower()
        field_value = match.group(2).strip()
        fields[field_name] = field_value

    # Also check for quoted values
    field_pattern2 = r'\s*(\w+)\s*=\s*"([^"]*)"'
    for match in re.finditer(field_pattern2, fields_text):
        field_name = match.group(1).lower()
        field_value = match.group(2).strip()
        fields[field_name] = field_value

    return fields

def check_entry_completeness(entry):
    """Check if a BibTeX entry is complete based on its type."""
    entry_type = entry['type']
    fields = entry['fields']

    result = {
        'type': entry_type,
        'has_author': 'author' in fields and fields['author'].strip() != '',
        'has_title': 'title' in fields and fields['title'].strip() != '',
        'has_year': 'year' in fields and fields['year'].strip() != '',
        'has_venue': False,
        'has_pages': False,
        'is_complete': False,
        'missing_fields': [],
        'issues': []
    }

    # Check required fields based on entry type
    if entry_type == 'article':
        result['has_venue'] = 'journal' in fields and fields['journal'].strip() != ''
        result['has_pages'] = 'pages' in fields and fields['pages'].strip() != ''

        required = ['author', 'title', 'year', 'journal']
        for req in required:
            if req not in fields or fields[req].strip() == '':
                result['missing_fields'].append(req)

        # Volume and pages are strongly recommended for articles
        if 'volume' not in fields or fields['volume'].strip() == '':
            result['issues'].append('Missing volume')
        if 'pages' not in fields or fields['pages'].strip() == '':
            result['issues'].append('Missing pages')

    elif entry_type == 'inproceedings':
        result['has_venue'] = 'booktitle' in fields and fields['booktitle'].strip() != ''
        result['has_pages'] = 'pages' in fields and fields['pages'].strip() != ''

        required = ['author', 'title', 'year', 'booktitle']
        for req in required:
            if req not in fields or fields[req].strip() == '':
                result['missing_fields'].append(req)

        # Pages recommended for inproceedings
        if 'pages' not in fields or fields['pages'].strip() == '':
            result['issues'].append('Missing pages')

    elif entry_type == 'misc':
        # For misc, at least title and author or note should be present
        required = ['title', 'year']
        if 'author' not in fields or fields['author'].strip() == '':
            if 'note' not in fields or fields['note'].strip() == '':
                result['missing_fields'].append('author or note')
        for req in required:
            if req not in fields or fields[req].strip() == '':
                result['missing_fields'].append(req)
    else:
        # For other types, check basic requirements
        required = ['author', 'title', 'year']
        for req in required:
            if req not in fields or fields[req].strip() == '':
                result['missing_fields'].append(req)

    # Determine completeness
    if entry_type == 'article':
        result['is_complete'] = (result['has_author'] and result['has_title'] and
                                  result['has_year'] and result['has_venue'])
    elif entry_type == 'inproceedings':
        result['is_complete'] = (result['has_author'] and result['has_title'] and
                                  result['has_year'] and result['has_venue'])
    elif entry_type == 'misc':
        result['is_complete'] = result['has_title'] and result['has_year']
    else:
        result['is_complete'] = result['has_author'] and result['has_title'] and result['has_year']

    # Check for empty title
    if 'title' in fields and fields['title'].strip() == '':
        result['issues'].append('Empty title')
        result['is_complete'] = False

    return result

def analyze_bib_file(filepath):
    """Analyze a BibTeX file and return completeness report."""
    entries = parse_bibtex_file(filepath)

    results = {
        'total_entries': len(entries),
        'entries': {},
        'incomplete_entries': [],
        'stats': {
            'complete': 0,
            'incomplete': 0,
            'missing_required': 0
        }
    }

    for entry in entries:
        key = entry['key']
        completeness = check_entry_completeness(entry)
        results['entries'][key] = completeness

        if completeness['is_complete']:
            results['stats']['complete'] += 1
        else:
            results['stats']['incomplete'] += 1
            results['incomplete_entries'].append(key)

        if len(completeness['missing_fields']) > 0:
            results['stats']['missing_required'] += 1

    return results

if __name__ == '__main__':
    filepath = '/Users/kendrickstein/Code/ReadPaperMachine/references.bib'
    results = analyze_bib_file(filepath)

    # Print summary
    print(f"Total entries: {results['total_entries']}")
    print(f"Complete entries: {results['stats']['complete']}")
    print(f"Incomplete entries: {results['stats']['incomplete']}")
    print(f"Entries missing required fields: {results['stats']['missing_required']}")

    # Print JSON output
    print("\n--- JSON Output ---")
    print(json.dumps(results, indent=2))