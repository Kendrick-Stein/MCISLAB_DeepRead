#!/usr/bin/env python3
"""
Enhanced citation enhancement script v2.
- Processes all potential citation locations (not just first 10)
- Includes daily papers from Workbench/daily/
- Smarter relevance matching
- Generates comprehensive citation plan
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import defaultdict

def load_paper_index(index_path: str) -> List[Dict]:
    """Load the paper index JSON."""
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_daily_papers(daily_dir: str) -> List[Dict]:
    """Load recent papers from daily summaries."""
    papers = []
    daily_path = Path(daily_dir)

    # Load .candidates.json which has recent papers
    candidates_file = daily_path / '.candidates.json'
    if candidates_file.exists():
        with open(candidates_file, 'r', encoding='utf-8') as f:
            candidates = json.load(f)
            for paper in candidates:
                # Convert to our format
                papers.append({
                    'filename': f"daily-{paper.get('id', 'unknown')}.md",
                    'title': paper.get('title', ''),
                    'authors': paper.get('authors', []),
                    'year': paper.get('published', '2026')[:4],
                    'venue': 'arXiv',
                    'tags': paper.get('tags', []),
                    'url': paper.get('url', ''),
                    'summary': paper.get('summary', ''),
                    'rating': '2'  # Default rating for daily papers
                })

    return papers

def extract_existing_citations(bib_content: str) -> Set[str]:
    """Extract existing citation keys from .bib file."""
    pattern = r'@\w+\{([^,]+),'
    return set(re.findall(pattern, bib_content))

def read_latex_sections(base_dir: str) -> Dict[str, str]:
    """Read all LaTeX section files, return dict of filename -> content."""
    sections = {}
    secs_dir = Path(base_dir) / "secs"

    if secs_dir.exists():
        for tex_file in sorted(secs_dir.glob("*.tex")):
            with open(tex_file, 'r', encoding='utf-8') as f:
                sections[tex_file.name] = f.read()

    return sections

def identify_citation_needs_comprehensive(sections: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Comprehensive citation need identification.
    Returns list of {context, keywords, location, file, full_text}
    """
    needs = []

    # Expanded citation triggers
    citation_triggers = [
        # Methods and approaches
        r'recent work', r'prior work', r'existing approaches', r'previous studies',
        r'methods?', r'approaches?', r'techniques?', r'frameworks?',

        # Models and systems
        r'vision-language models?', r'VLM', r'language models?', r'LLM',
        r'GUI agents?', r'agents?', r'foundation models?',

        # Techniques
        r'reinforcement learning', r'RLHF', r'test-time scaling',
        r'computer use', r'tool use', r'multimodal',

        # Evaluation
        r'benchmarks?', r'evaluation', r'metrics?', r'assessment',
        r'verification', r'validation',

        # Data and representations
        r'screenshots?', r'accessibility tree', r'hidden state',
        r'configuration files?', r'environment state',

        # Domains
        r'desktop automation', r'web agents?', r'mobile agents?',
        r'GUI automation', r'task completion',

        # Specific systems (should cite)
        r'OSWorld', r'AgentStudio', r'Mind2Web', r'AndroidEnv',
        r'UI-TARS', r'CogAgent', r'GPT-4', r'Claude',

        # Research concepts
        r'grounding', r'reasoning', r'planning', r'spatial',
        r'visual understanding', r'action space',
    ]

    for filename, content in sections.items():
        # Split into sentences for finer-grained analysis
        sentences = re.split(r'(?<=[.!?])\s+', content)

        for i, sentence in enumerate(sentences):
            # Skip if already has citations
            if '\\cite{' in sentence:
                continue

            # Skip LaTeX commands and tables
            if sentence.strip().startswith('\\begin{') or sentence.strip().startswith('\\end{'):
                continue

            # Check for citation triggers
            matched_triggers = []
            for trigger in citation_triggers:
                if re.search(trigger, sentence, re.IGNORECASE):
                    matched_triggers.append(trigger)

            if matched_triggers:
                # Extract key concepts
                keywords = extract_keywords_enhanced(sentence)

                needs.append({
                    'context': sentence[:300],
                    'keywords': keywords,
                    'location': f'{filename}:sentence_{i}',
                    'file': filename,
                    'full_text': sentence,
                    'triggers': matched_triggers
                })

    return needs

def extract_keywords_enhanced(text: str) -> List[str]:
    """Enhanced keyword extraction."""
    keywords = []

    # Technical terms
    patterns = [
        # Models and systems
        r'\b(GUI|VLM|LLM|RLHF|RL|GPT|Claude|Gemini)\b',
        r'\b(agent|benchmark|evaluation|reward|verification)\b',
        r'\b(vision-language|multimodal|foundation model)\b',

        # Techniques
        r'\b(screenshot|accessibility|grounding|reasoning)\b',
        r'\b(desktop|web|mobile|computer use|tool use)\b',
        r'\b(hidden state|configuration|environment state)\b',

        # Specific systems
        r'\b(OSWorld|AgentStudio|Mind2Web|AndroidEnv|UI-TARS|CogAgent)\b',
        r'\b(SayCan|PaLM|Flamingo|BLIP|CLIP)\b',

        # Research areas
        r'\b(spatial reasoning|visual understanding|action space)\b',
        r'\b(task completion|trajectory|execution)\b',
        r'\b(precision|recall|accuracy|F1)\b',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        keywords.extend([m.lower() for m in matches])

    return list(set(keywords))

def search_relevant_papers_enhanced(
    citation_need: Dict,
    paper_index: List[Dict],
    top_k: int = 3
) -> List[Tuple[float, Dict]]:
    """
    Enhanced paper search with better scoring.
    Returns list of (score, paper) tuples.
    """
    keywords = set(citation_need['keywords'])
    context = citation_need['full_text'].lower()
    scores = []

    for paper in paper_index:
        score = 0.0

        # 1. Tag matching (strong signal)
        paper_tags = set([t.lower() for t in paper.get('tags', [])])
        tag_overlap = len(keywords & paper_tags)
        score += tag_overlap * 5.0

        # 2. Title matching (very strong signal)
        title_lower = paper.get('title', '').lower()
        title_words = set(re.findall(r'\b\w+\b', title_lower))
        title_overlap = len(keywords & title_words)
        score += title_overlap * 3.0

        # 3. Context relevance (check if paper title concepts appear in context)
        for word in title_words:
            if len(word) > 4 and word in context:  # Only meaningful words
                score += 1.5

        # 4. Summary matching
        summary_lower = paper.get('summary', '').lower()
        for kw in keywords:
            if kw in summary_lower:
                score += 1.0

        # 5. Venue/year boost (prefer recent, high-quality venues)
        venue = paper.get('venue', '').lower()
        year_str = paper.get('year', '2020')
        try:
            year = int(year_str) if year_str else 2020
        except (ValueError, TypeError):
            year = 2020

        if any(conf in venue for conf in ['cvpr', 'iccv', 'eccv', 'neurips', 'icml', 'iclr']):
            score += 3.0
        elif 'arxiv' in venue and year >= 2024:
            score += 2.0

        # Recency boost
        if year >= 2025:
            score += 2.0
        elif year >= 2024:
            score += 1.0

        # 6. Rating boost
        rating = paper.get('rating', '1')
        if rating in ['3', '4']:
            score += 3.0
        elif rating == '2':
            score += 1.5

        if score > 0:
            scores.append((score, paper))

    # Sort by score and return top_k
    scores.sort(reverse=True, key=lambda x: x[0])
    return scores[:top_k]

def generate_bibtex_entry(paper: Dict, existing_keys: Set[str]) -> Tuple[str, str]:
    """
    Generate BibTeX entry from paper metadata.
    Returns (citation_key, bibtex_entry)
    """
    # Generate citation key: FirstAuthorYear
    authors = paper.get('authors', [])
    year = paper.get('year', '2024')

    if authors:
        first_author_name = authors[0]
        if isinstance(first_author_name, str) and first_author_name.strip():
            parts = first_author_name.split()
            first_author = parts[-1] if parts else 'Unknown'  # Last name
            # Clean up author name
            first_author = re.sub(r'[^a-zA-Z]', '', first_author)
        else:
            first_author = 'Unknown'
    else:
        first_author = 'Unknown'

    # Base citation key
    cite_key = f"{first_author}{year}"

    # Handle duplicates by adding suffix
    if cite_key in existing_keys:
        suffix = ord('a')
        while f"{cite_key}{chr(suffix)}" in existing_keys:
            suffix += 1
        cite_key = f"{cite_key}{chr(suffix)}"

    # Determine entry type
    venue = paper.get('venue', '')
    url = paper.get('url', '')

    if 'arxiv' in venue.lower() or 'arxiv.org' in url:
        entry_type = 'article'
        journal = "arXiv preprint"
        if url and 'arxiv.org/abs/' in url:
            arxiv_id = url.split('arxiv.org/abs/')[-1].split('v')[0]
            journal += f" arXiv:{arxiv_id}"
    elif venue and any(conf in venue for conf in ['CVPR', 'ICCV', 'ECCV', 'NeurIPS', 'ICML', 'ICLR']):
        entry_type = 'inproceedings'
        journal = None
    else:
        entry_type = 'article'
        journal = venue if venue else 'Unknown'

    # Format authors
    if authors:
        author_str = ' and '.join(authors)
    else:
        author_str = 'Unknown'

    # Build BibTeX entry
    lines = [f"@{entry_type}{{{cite_key},"]
    lines.append(f"  title={{{paper.get('title', 'Unknown')}}},")
    lines.append(f"  author={{{author_str}}},")

    if entry_type == 'article' and journal:
        lines.append(f"  journal={{{journal}}},")
    elif entry_type == 'inproceedings':
        lines.append(f"  booktitle={{Proceedings of {venue}}},")

    lines.append(f"  year={{{year}}}")

    if url:
        lines.append(f",\n  url={{{url}}}")

    lines.append("}")

    return cite_key, '\n'.join(lines)

def group_citations_by_section(citation_plan: List[Dict]) -> Dict[str, List[Dict]]:
    """Group citations by section for better organization."""
    grouped = defaultdict(list)

    for plan in citation_plan:
        section = plan['location'].split(':')[0]
        grouped[section].append(plan)

    return dict(grouped)

def main():
    # Paths
    base_dir = "/Users/kendrickstein/Code/Reward-Agent/writing"
    index_path = "/Users/kendrickstein/Code/ReadPaperMachine/skills/4-writing/latex-citation-enhancer/paper_index.json"
    daily_dir = "/Users/kendrickstein/Code/ReadPaperMachine/Workbench/daily"
    bib_path = f"{base_dir}/references.bib"

    print("="*70)
    print("COMPREHENSIVE CITATION ENHANCEMENT v2")
    print("="*70)

    # Load data
    print("\n[1/6] Loading paper sources...")
    paper_index = load_paper_index(index_path)
    print(f"  ✓ Loaded {len(paper_index)} papers from Papers/")

    daily_papers = load_daily_papers(daily_dir)
    print(f"  ✓ Loaded {len(daily_papers)} papers from daily summaries")

    # Combine paper sources
    all_papers = paper_index + daily_papers
    print(f"  ✓ Total paper pool: {len(all_papers)} papers")

    # Read existing bib
    with open(bib_path, 'r', encoding='utf-8') as f:
        existing_bib = f.read()
    existing_keys = extract_existing_citations(existing_bib)
    print(f"  ✓ Found {len(existing_keys)} existing citations")

    # Read LaTeX content
    print("\n[2/6] Analyzing LaTeX content...")
    sections = read_latex_sections(base_dir)
    print(f"  ✓ Read {len(sections)} section files")

    # Identify citation needs
    print("\n[3/6] Identifying citation opportunities...")
    citation_needs = identify_citation_needs_comprehensive(sections)
    print(f"  ✓ Found {len(citation_needs)} potential citation locations")

    # Search for relevant papers
    print("\n[4/6] Matching papers to citation needs...")
    new_entries = {}
    citation_plan = []

    for i, need in enumerate(citation_needs):
        if (i + 1) % 20 == 0:
            print(f"  Processing... {i+1}/{len(citation_needs)}")

        relevant_papers = search_relevant_papers_enhanced(need, all_papers, top_k=2)

        if relevant_papers:
            cite_keys = []
            papers_info = []

            for score, paper in relevant_papers:
                cite_key, bib_entry = generate_bibtex_entry(paper, existing_keys | set(new_entries.keys()))

                # Only add if not duplicate
                if cite_key not in existing_keys and cite_key not in new_entries:
                    new_entries[cite_key] = bib_entry

                cite_keys.append(cite_key)
                papers_info.append({
                    'title': paper['title'],
                    'score': score
                })

            if cite_keys:
                citation_plan.append({
                    'location': need['location'],
                    'file': need['file'],
                    'context': need['context'],
                    'cite_keys': cite_keys,
                    'papers': papers_info,
                    'full_text': need['full_text']
                })

    print(f"  ✓ Generated {len(citation_plan)} citation recommendations")
    print(f"  ✓ Found {len(new_entries)} new papers to cite")

    # Group by section
    print("\n[5/6] Organizing citations by section...")
    grouped = group_citations_by_section(citation_plan)

    # Output results
    print("\n" + "="*70)
    print("CITATION PLAN SUMMARY")
    print("="*70)

    print(f"\nTotal new citations: {len(new_entries)}")
    print(f"Total citation locations: {len(citation_plan)}")
    print(f"\nBreakdown by section:")
    for section, plans in sorted(grouped.items()):
        print(f"  - {section}: {len(plans)} citations")

    # Save detailed plan
    print("\n[6/6] Saving results...")

    plan_path = f"{base_dir}/citation_plan_v2.json"
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(citation_plan, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Citation plan saved to {plan_path}")

    # Save new BibTeX entries
    new_bib_path = f"{base_dir}/new_citations.bib"
    with open(new_bib_path, 'w', encoding='utf-8') as f:
        for entry in new_entries.values():
            f.write(entry)
            f.write("\n\n")
    print(f"  ✓ New BibTeX entries saved to {new_bib_path}")

    # Generate human-readable report
    report_path = f"{base_dir}/citation_report_v2.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Comprehensive Citation Enhancement Report\n\n")
        f.write(f"Generated: 2026-05-22\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- **Total new citations**: {len(new_entries)}\n")
        f.write(f"- **Citation locations**: {len(citation_plan)}\n")
        f.write(f"- **Paper sources**: {len(all_papers)} (Papers/ + daily)\n\n")

        f.write("## Citations by Section\n\n")
        for section, plans in sorted(grouped.items()):
            f.write(f"### {section} ({len(plans)} citations)\n\n")
            for plan in plans[:5]:  # Show first 5 per section
                f.write(f"**Location**: {plan['location']}\n\n")
                f.write(f"**Context**: {plan['context'][:150]}...\n\n")
                f.write(f"**Suggested citations**: `{', '.join(plan['cite_keys'])}`\n\n")
                for paper in plan['papers']:
                    f.write(f"- {paper['title']} (score: {paper['score']:.1f})\n")
                f.write("\n")
            if len(plans) > 5:
                f.write(f"... and {len(plans) - 5} more\n\n")

        f.write("\n## New BibTeX Entries\n\n")
        f.write(f"Total: {len(new_entries)} entries\n\n")
        for i, (key, entry) in enumerate(list(new_entries.items())[:20], 1):
            f.write(f"{i}. `{key}`\n")
        if len(new_entries) > 20:
            f.write(f"\n... and {len(new_entries) - 20} more (see new_citations.bib)\n")

    print(f"  ✓ Human-readable report saved to {report_path}")

    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("\n1. Review citation_report_v2.md for detailed recommendations")
    print("2. Review new_citations.bib for BibTeX entries")
    print("3. Manually insert \\cite{} commands in LaTeX files")
    print("4. Append new_citations.bib to references.bib")
    print("\nNote: This script generates recommendations. Manual review recommended")
    print("before adding all citations to ensure relevance and avoid over-citation.")

if __name__ == '__main__':
    main()
