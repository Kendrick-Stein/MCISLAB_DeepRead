#!/usr/bin/env python3
"""
Enhance LaTeX citations by finding relevant papers from Papers/ directory.
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

def extract_existing_citations(bib_content: str) -> Set[str]:
    """Extract existing citation keys from .bib file."""
    pattern = r'@\w+\{([^,]+),'
    return set(re.findall(pattern, bib_content))

def read_latex_sections(base_dir: str) -> str:
    """Read all LaTeX section files."""
    sections = []
    secs_dir = Path(base_dir) / "secs"

    if secs_dir.exists():
        for tex_file in sorted(secs_dir.glob("*.tex")):
            with open(tex_file, 'r', encoding='utf-8') as f:
                sections.append(f.read())

    return "\n\n".join(sections)

def identify_citation_needs(latex_content: str) -> List[Dict[str, str]]:
    """
    Identify places in LaTeX that need citations.
    Returns list of {context, keywords, location}
    """
    needs = []

    # Keywords that suggest citation needs
    citation_triggers = [
        r'recent work',
        r'prior work',
        r'existing approaches',
        r'methods',
        r'benchmarks',
        r'vision-language models?',
        r'VLM',
        r'GUI agents?',
        r'reinforcement learning',
        r'RLHF',
        r'test-time scaling',
        r'computer use',
        r'tool use',
        r'multimodal',
        r'screenshot',
        r'accessibility tree',
        r'desktop automation',
        r'web agents?',
        r'mobile agents?',
        r'agent evaluation',
        r'reward model',
        r'verification',
        r'hidden state',
        r'configuration files?',
    ]

    # Split into paragraphs
    paragraphs = latex_content.split('\n\n')

    for i, para in enumerate(paragraphs):
        # Skip if already has citations
        if '\\cite{' in para:
            continue

        # Check for citation triggers
        for trigger in citation_triggers:
            if re.search(trigger, para, re.IGNORECASE):
                # Extract key concepts from paragraph
                keywords = extract_keywords(para)
                needs.append({
                    'context': para[:200],  # First 200 chars
                    'keywords': keywords,
                    'location': f'paragraph_{i}',
                    'full_text': para
                })
                break

    return needs

def extract_keywords(text: str) -> List[str]:
    """Extract technical keywords from text."""
    # Common technical terms in GUI/Agent/VLM domain
    keywords = []

    patterns = [
        r'\b(GUI|VLM|RLHF|RL|agent|benchmark|evaluation|reward|verification)\b',
        r'\b(vision-language|multimodal|screenshot|accessibility)\b',
        r'\b(desktop|web|mobile|computer use|tool use)\b',
        r'\b(hidden state|configuration|environment state)\b',
        r'\b(OSWorld|AgentStudio|Mind2Web|AndroidEnv)\b',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        keywords.extend([m.lower() for m in matches])

    return list(set(keywords))

def search_relevant_papers(
    citation_need: Dict,
    paper_index: List[Dict],
    top_k: int = 3
) -> List[Dict]:
    """
    Search for relevant papers based on keywords and context.
    Returns top_k most relevant papers.
    """
    keywords = set(citation_need['keywords'])
    scores = []

    for paper in paper_index:
        score = 0

        # Match tags
        paper_tags = set([t.lower() for t in paper.get('tags', [])])
        tag_overlap = len(keywords & paper_tags)
        score += tag_overlap * 3  # Tags are strong signals

        # Match title
        title_lower = paper.get('title', '').lower()
        for kw in keywords:
            if kw in title_lower:
                score += 2

        # Match summary
        summary_lower = paper.get('summary', '').lower()
        for kw in keywords:
            if kw in summary_lower:
                score += 1

        # Boost by rating
        rating = paper.get('rating', '1')
        if rating in ['3', '4']:
            score += 2
        elif rating == '2':
            score += 1

        if score > 0:
            scores.append((score, paper))

    # Sort by score and return top_k
    scores.sort(reverse=True, key=lambda x: x[0])
    return [paper for score, paper in scores[:top_k]]

def generate_bibtex_entry(paper: Dict) -> Tuple[str, str]:
    """
    Generate BibTeX entry from paper metadata.
    Returns (citation_key, bibtex_entry)
    """
    # Generate citation key: FirstAuthorYear
    authors = paper.get('authors', [])
    year = paper.get('year', '2024')

    if authors:
        first_author = authors[0].split()[-1]  # Last name
    else:
        first_author = 'Unknown'

    cite_key = f"{first_author}{year}"

    # Determine entry type
    venue = paper.get('venue', '')
    url = paper.get('url', '')

    if 'arxiv' in venue.lower() or 'arxiv.org' in url:
        entry_type = 'article'
        journal = f"arXiv preprint"
        if url and 'arxiv.org/abs/' in url:
            arxiv_id = url.split('arxiv.org/abs/')[-1]
            journal += f" arXiv:{arxiv_id}"
    elif venue and any(conf in venue for conf in ['CVPR', 'ICCV', 'ECCV', 'NeurIPS', 'ICML', 'ICLR']):
        entry_type = 'inproceedings'
        journal = None
    else:
        entry_type = 'article'
        journal = venue if venue else 'Unknown'

    # Format authors
    author_str = ' and '.join(authors) if authors else 'Unknown'

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

def main():
    # Paths
    base_dir = "/Users/kendrickstein/Code/Reward-Agent/writing"
    index_path = "/Users/kendrickstein/Code/ReadPaperMachine/skills/4-writing/latex-citation-enhancer/paper_index.json"
    bib_path = f"{base_dir}/references.bib"

    # Load data
    print("Loading paper index...")
    paper_index = load_paper_index(index_path)
    print(f"Loaded {len(paper_index)} papers")

    # Read existing bib
    with open(bib_path, 'r', encoding='utf-8') as f:
        existing_bib = f.read()
    existing_keys = extract_existing_citations(existing_bib)
    print(f"Found {len(existing_keys)} existing citations")

    # Read LaTeX content
    print("\nAnalyzing LaTeX content...")
    latex_content = read_latex_sections(base_dir)

    # Identify citation needs
    citation_needs = identify_citation_needs(latex_content)
    print(f"Identified {len(citation_needs)} potential citation locations")

    # Search for relevant papers
    print("\nSearching for relevant papers...")
    new_entries = {}
    citation_plan = []

    for need in citation_needs[:10]:  # Limit to first 10 for now
        relevant_papers = search_relevant_papers(need, paper_index, top_k=2)

        if relevant_papers:
            cite_keys = []
            for paper in relevant_papers:
                cite_key, bib_entry = generate_bibtex_entry(paper)

                # Avoid duplicates
                if cite_key not in existing_keys and cite_key not in new_entries:
                    new_entries[cite_key] = bib_entry

                cite_keys.append(cite_key)

            citation_plan.append({
                'location': need['location'],
                'context': need['context'],
                'cite_keys': cite_keys,
                'papers': [p['title'] for p in relevant_papers]
            })

    # Output results
    print(f"\n{'='*60}")
    print("CITATION ENHANCEMENT PLAN")
    print(f"{'='*60}\n")

    print(f"Found {len(new_entries)} new papers to cite:\n")

    for i, plan in enumerate(citation_plan, 1):
        print(f"{i}. Location: {plan['location']}")
        print(f"   Context: {plan['context'][:100]}...")
        print(f"   Suggested citations: {', '.join(plan['cite_keys'])}")
        print(f"   Papers:")
        for paper in plan['papers']:
            print(f"     - {paper}")
        print()

    # Write new BibTeX entries
    if new_entries:
        print(f"\n{'='*60}")
        print("NEW BIBTEX ENTRIES")
        print(f"{'='*60}\n")

        for cite_key, entry in new_entries.items():
            print(entry)
            print()

        # Append to bib file
        output_path = bib_path
        with open(output_path, 'a', encoding='utf-8') as f:
            f.write("\n\n")
            for entry in new_entries.values():
                f.write(entry)
                f.write("\n\n")

        print(f"\n✓ Added {len(new_entries)} new entries to {output_path}")
    else:
        print("\nNo new citations needed (all relevant papers already in bibliography)")

    # Save citation plan
    plan_path = f"{base_dir}/citation_plan.json"
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(citation_plan, f, indent=2, ensure_ascii=False)

    print(f"✓ Citation plan saved to {plan_path}")

if __name__ == '__main__':
    main()
