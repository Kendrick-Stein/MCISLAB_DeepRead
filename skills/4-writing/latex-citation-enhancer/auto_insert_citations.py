#!/usr/bin/env python3
"""
Automatically insert citations into LaTeX files.
Final optimization: select top 60 most relevant citations.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

def load_filtered_plan(plan_path: str):
    """Load the filtered citation plan."""
    with open(plan_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def further_optimize(citation_plan, target=60):
    """Further optimize to exactly target citations."""
    # Score each citation
    scored = []
    for item in citation_plan:
        score = 0.0

        # Paper quality score
        if 'papers' in item:
            paper_scores = [p.get('score', 0) for p in item['papers']]
            if paper_scores:
                score += sum(paper_scores) / len(paper_scores)

        # Section importance
        file = item.get('file', '')
        if 'introduction' in file:
            score += 8.0
        elif 'related_work' in file:
            score += 7.0
        elif 'method' in file:
            score += 6.0
        elif 'experiments' in file:
            score += 4.0
        elif 'conclusion' in file:
            score += 3.0

        # Prefer citations with known authors (not "Unknown")
        cite_keys = item.get('cite_keys', [])
        if not any('Unknown' in k for k in cite_keys):
            score += 3.0

        scored.append((score, item))

    # Sort by score and take top target
    scored.sort(reverse=True, key=lambda x: x[0])
    return [item for score, item in scored[:target]]

def insert_citation_in_text(text: str, location: str, cite_command: str) -> str:
    """
    Insert citation at the specified location in text.
    Location format: "filename:sentence_N"
    """
    # Extract sentence number
    match = re.search(r'sentence_(\d+)', location)
    if not match:
        return text

    sentence_idx = int(match.group(1))

    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)

    if sentence_idx >= len(sentences):
        return text

    # Get the target sentence
    target_sentence = sentences[sentence_idx]

    # Skip if already has citation
    if '\\cite{' in target_sentence:
        return text

    # Insert citation at end of sentence (before period)
    # Handle different sentence endings
    if target_sentence.endswith('.'):
        modified = target_sentence[:-1] + cite_command + '.'
    elif target_sentence.endswith('...'):
        modified = target_sentence[:-3] + cite_command + '...'
    else:
        modified = target_sentence + cite_command

    # Replace in original text
    sentences[sentence_idx] = modified

    # Rejoin
    return ' '.join(sentences)

def main():
    base_dir = "/Users/kendrickstein/Code/Reward-Agent/writing"
    plan_path = f"{base_dir}/citation_plan_filtered.json"
    secs_dir = Path(base_dir) / "secs"

    print("="*70)
    print("AUTOMATIC CITATION INSERTION")
    print("="*70)

    # Load filtered plan
    print("\n[1/4] Loading filtered citation plan...")
    citation_plan = load_filtered_plan(plan_path)
    print(f"  ✓ Loaded {len(citation_plan)} citation locations")

    # Further optimize to top 60
    print("\n[2/4] Optimizing to top 60 citations...")
    optimized = further_optimize(citation_plan, target=60)
    print(f"  ✓ Selected {len(optimized)} top citations")

    # Group by file
    by_file = defaultdict(list)
    for item in optimized:
        by_file[item['file']].append(item)

    print(f"\n  Distribution:")
    for file, items in sorted(by_file.items()):
        print(f"    - {file}: {len(items)} citations")

    # Count unique citation keys
    all_keys = set()
    for item in optimized:
        all_keys.update(item['cite_keys'])
    print(f"\n  ✓ Total unique citation keys: {len(all_keys)}")

    # Insert citations
    print("\n[3/4] Inserting citations into LaTeX files...")

    modifications = {}
    for file, items in by_file.items():
        file_path = secs_dir / file

        if not file_path.exists():
            print(f"  ⚠ File not found: {file}")
            continue

        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Sort items by sentence number (insert from end to beginning to preserve indices)
        items_sorted = sorted(items, key=lambda x: int(re.search(r'sentence_(\d+)', x['location']).group(1)), reverse=True)

        # Insert citations
        for item in items_sorted:
            cite_keys = item['cite_keys']
            cite_command = f"~\\cite{{{','.join(cite_keys)}}}"

            content = insert_citation_in_text(content, item['location'], cite_command)

        # Check if modified
        if content != original_content:
            modifications[file] = content
            print(f"  ✓ Modified {file}: {len(items)} citations added")

    # Save modifications
    print("\n[4/4] Saving modified files...")

    for file, content in modifications.items():
        file_path = secs_dir / file
        backup_path = secs_dir / f"{file}.backup"

        # Create backup
        with open(file_path, 'r', encoding='utf-8') as f:
            with open(backup_path, 'w', encoding='utf-8') as fb:
                fb.write(f.read())

        # Write modified content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✓ Saved {file} (backup: {file}.backup)")

    # Save final citation list
    final_plan_path = f"{base_dir}/citations_final.json"
    with open(final_plan_path, 'w', encoding='utf-8') as f:
        json.dump(optimized, f, indent=2, ensure_ascii=False)

    # Extract and save final BibTeX entries
    print("\n  Extracting final BibTeX entries...")

    new_bib_path = f"{base_dir}/new_citations.bib"
    with open(new_bib_path, 'r', encoding='utf-8') as f:
        all_bib_content = f.read()

    selected_entries = []
    for key in sorted(all_keys):
        pattern = rf'@\w+\{{{re.escape(key)},.*?\n\}}'
        match = re.search(pattern, all_bib_content, re.DOTALL)
        if match:
            selected_entries.append(match.group(0))

    final_bib_path = f"{base_dir}/citations_final.bib"
    with open(final_bib_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(selected_entries))

    print(f"  ✓ Final BibTeX entries saved to {final_bib_path}")
    print(f"  ✓ Total entries: {len(selected_entries)}")

    # Append to references.bib
    print("\n  Appending to references.bib...")
    ref_bib_path = f"{base_dir}/references.bib"

    with open(ref_bib_path, 'a', encoding='utf-8') as f:
        f.write("\n\n% ===== AUTO-GENERATED CITATIONS =====\n")
        f.write("% Generated by latex-citation-enhancer\n")
        f.write(f"% Date: 2026-05-22\n")
        f.write(f"% Total: {len(selected_entries)} entries\n\n")
        f.write('\n\n'.join(selected_entries))

    print(f"  ✓ Appended {len(selected_entries)} entries to references.bib")

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\n✓ Inserted {len(all_keys)} citations across {len(modifications)} files")
    print(f"✓ Modified files: {', '.join(modifications.keys())}")
    print(f"✓ Backups created with .backup extension")
    print(f"✓ BibTeX entries appended to references.bib")
    print(f"\nNext steps:")
    print(f"  1. Review modified LaTeX files")
    print(f"  2. Compile with: pdflatex main.tex && bibtex main && pdflatex main.tex")
    print(f"  3. Check for any compilation errors")
    print(f"  4. If satisfied, delete .backup files")

if __name__ == '__main__':
    main()
