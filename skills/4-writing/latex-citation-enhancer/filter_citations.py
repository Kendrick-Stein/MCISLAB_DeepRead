#!/usr/bin/env python3
"""
Filter and select top 50-80 citations from comprehensive plan.
Criteria:
- High relevance score
- Diversity (avoid too many citations in one location)
- Quality (prefer high-rated papers, recent work, top venues)
- No duplicates
"""

import json
from collections import defaultdict
from pathlib import Path

def load_citation_plan(plan_path: str):
    """Load the comprehensive citation plan."""
    with open(plan_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def score_citation_quality(plan_item):
    """Score a citation based on paper quality and relevance."""
    score = 0.0

    # Average paper score
    if 'papers' in plan_item:
        paper_scores = [p.get('score', 0) for p in plan_item['papers']]
        if paper_scores:
            score += sum(paper_scores) / len(paper_scores)

    # Bonus for introduction/related work (more important sections)
    if 'introduction' in plan_item.get('file', ''):
        score += 5.0
    elif 'related_work' in plan_item.get('file', ''):
        score += 4.0
    elif 'method' in plan_item.get('file', ''):
        score += 3.0

    return score

def deduplicate_citations(citation_plan):
    """Remove duplicate citation keys across all locations."""
    seen_keys = set()
    deduped = []

    for item in citation_plan:
        # Filter out already-seen citation keys
        new_keys = [k for k in item['cite_keys'] if k not in seen_keys]

        if new_keys:
            # Update the item with only new keys
            item_copy = item.copy()
            item_copy['cite_keys'] = new_keys
            # Also filter papers
            item_copy['papers'] = [p for i, p in enumerate(item['papers'])
                                   if i < len(new_keys)]
            deduped.append(item_copy)
            seen_keys.update(new_keys)

    return deduped

def balance_citations_by_section(citation_plan, target_total=60):
    """Balance citations across sections."""
    # Group by section
    by_section = defaultdict(list)
    for item in citation_plan:
        section = item['file']
        by_section[section].append(item)

    # Calculate target per section (proportional to current distribution)
    total_items = len(citation_plan)
    section_targets = {}
    for section, items in by_section.items():
        proportion = len(items) / total_items
        section_targets[section] = max(5, int(target_total * proportion))

    # Select top items from each section
    selected = []
    for section, items in by_section.items():
        target = section_targets[section]
        # Sort by quality score
        sorted_items = sorted(items, key=score_citation_quality, reverse=True)
        selected.extend(sorted_items[:target])

    return selected

def filter_low_quality(citation_plan, min_score=8.0):
    """Filter out low-quality citations."""
    filtered = []
    for item in citation_plan:
        if 'papers' in item and item['papers']:
            avg_score = sum(p.get('score', 0) for p in item['papers']) / len(item['papers'])
            if avg_score >= min_score:
                filtered.append(item)
    return filtered

def main():
    base_dir = "/Users/kendrickstein/Code/Reward-Agent/writing"
    plan_path = f"{base_dir}/citation_plan_v2.json"

    print("="*70)
    print("CITATION FILTERING & SELECTION")
    print("="*70)

    # Load comprehensive plan
    print("\n[1/5] Loading comprehensive citation plan...")
    citation_plan = load_citation_plan(plan_path)
    print(f"  ✓ Loaded {len(citation_plan)} citation locations")

    # Count total citation keys
    total_keys = sum(len(item['cite_keys']) for item in citation_plan)
    print(f"  ✓ Total citation keys: {total_keys}")

    # Step 1: Filter low quality
    print("\n[2/5] Filtering low-quality citations (score < 8.0)...")
    filtered = filter_low_quality(citation_plan, min_score=8.0)
    print(f"  ✓ Kept {len(filtered)} high-quality locations")

    # Step 2: Deduplicate
    print("\n[3/5] Removing duplicate citation keys...")
    deduped = deduplicate_citations(filtered)
    print(f"  ✓ After deduplication: {len(deduped)} locations")

    unique_keys = set()
    for item in deduped:
        unique_keys.update(item['cite_keys'])
    print(f"  ✓ Unique citation keys: {len(unique_keys)}")

    # Step 3: Balance by section
    print("\n[4/5] Balancing citations across sections...")
    target_total = 70  # Target 70 citation locations
    balanced = balance_citations_by_section(deduped, target_total=target_total)
    print(f"  ✓ Selected {len(balanced)} balanced locations")

    # Count final citation keys
    final_keys = set()
    for item in balanced:
        final_keys.update(item['cite_keys'])
    print(f"  ✓ Final unique citation keys: {len(final_keys)}")

    # Breakdown by section
    by_section = defaultdict(int)
    for item in balanced:
        by_section[item['file']] += 1

    print("\n  Breakdown by section:")
    for section, count in sorted(by_section.items()):
        print(f"    - {section}: {count} citations")

    # Step 4: Save filtered plan
    print("\n[5/5] Saving filtered citation plan...")

    filtered_plan_path = f"{base_dir}/citation_plan_filtered.json"
    with open(filtered_plan_path, 'w', encoding='utf-8') as f:
        json.dump(balanced, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Filtered plan saved to {filtered_plan_path}")

    # Extract unique BibTeX entries needed
    print("\n  Extracting required BibTeX entries...")

    # Load all new citations
    new_bib_path = f"{base_dir}/new_citations.bib"
    with open(new_bib_path, 'r', encoding='utf-8') as f:
        all_bib_content = f.read()

    # Extract entries for selected keys
    import re
    selected_entries = []
    for key in sorted(final_keys):
        # Find the BibTeX entry for this key
        pattern = rf'@\w+\{{{re.escape(key)},.*?\n\}}'
        match = re.search(pattern, all_bib_content, re.DOTALL)
        if match:
            selected_entries.append(match.group(0))

    # Save selected BibTeX entries
    selected_bib_path = f"{base_dir}/citations_to_add.bib"
    with open(selected_bib_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(selected_entries))
    print(f"  ✓ Selected BibTeX entries saved to {selected_bib_path}")
    print(f"  ✓ Total entries: {len(selected_entries)}")

    # Generate insertion script
    print("\n  Generating LaTeX insertion script...")

    insertion_script = []
    insertion_script.append("# LaTeX Citation Insertion Guide\n")
    insertion_script.append(f"# Total citations to add: {len(balanced)}\n")
    insertion_script.append(f"# Unique citation keys: {len(final_keys)}\n\n")

    for section, items in sorted(by_section.items()):
        insertion_script.append(f"\n## {section} ({items} citations)\n\n")

        section_items = [item for item in balanced if item['file'] == section]
        for i, item in enumerate(section_items[:10], 1):  # Show first 10
            insertion_script.append(f"{i}. **Location**: {item['location']}\n")
            insertion_script.append(f"   **Context**: {item['context'][:100]}...\n")
            insertion_script.append(f"   **Add**: `\\cite{{{','.join(item['cite_keys'])}}}`\n")
            insertion_script.append(f"   **Papers**:\n")
            for paper in item['papers']:
                insertion_script.append(f"   - {paper['title']}\n")
            insertion_script.append("\n")

        if len(section_items) > 10:
            insertion_script.append(f"   ... and {len(section_items) - 10} more\n\n")

    guide_path = f"{base_dir}/citation_insertion_guide.md"
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.writelines(insertion_script)
    print(f"  ✓ Insertion guide saved to {guide_path}")

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\n✓ Selected {len(final_keys)} high-quality citations")
    print(f"✓ Distributed across {len(balanced)} locations")
    print(f"✓ Balanced across {len(by_section)} sections")
    print(f"\nFiles generated:")
    print(f"  1. {filtered_plan_path} - Filtered citation plan")
    print(f"  2. {selected_bib_path} - BibTeX entries to add")
    print(f"  3. {guide_path} - Manual insertion guide")
    print(f"\nNext: Review citation_insertion_guide.md and add citations to LaTeX files")

if __name__ == '__main__':
    main()
