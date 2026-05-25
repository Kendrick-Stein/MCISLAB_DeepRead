#!/usr/bin/env python3
"""
简化版：从 arXiv API 修复 Unknown 作者
"""

import re
import time
import urllib.request
import xml.etree.ElementTree as ET

def fetch_arxiv_authors(arxiv_id):
    """从 arXiv API 获取作者列表"""
    url = f'http://export.arxiv.org/api/query?id_list={arxiv_id}'

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            xml_data = response.read().decode('utf-8')

        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        entry = root.find('atom:entry', ns)
        if entry is None:
            return None

        authors = []
        for author in entry.findall('atom:author', ns):
            name = author.find('atom:name', ns)
            if name is not None and name.text:
                authors.append(name.text.strip())

        return authors if authors else None

    except Exception as e:
        print(f"Error fetching {arxiv_id}: {e}")
        return None

def main():
    bib_file = '/Users/kendrickstein/Code/Reward-Agent/writing/references.bib'

    print("Reading BibTeX file...")
    with open(bib_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到所有 Unknown 作者的条目
    pattern = r'(@\w+\{[^}]+,\s*title=\{[^}]+\},\s*author=\{Unknown\},[^}]*journal=\{arXiv preprint arXiv:([0-9.]+)\}[^}]*\})'

    matches = list(re.finditer(pattern, content, re.DOTALL))
    print(f"Found {len(matches)} entries with Unknown authors and arXiv IDs")

    if not matches:
        print("No Unknown authors with arXiv IDs found!")
        return

    fixed_content = content
    fixed_count = 0

    for i, match in enumerate(matches, 1):
        old_entry = match.group(1)
        arxiv_id = match.group(2)

        print(f"\n[{i}/{len(matches)}] Processing arXiv:{arxiv_id}...")

        authors = fetch_arxiv_authors(arxiv_id)

        if authors:
            author_str = ' and '.join(authors)
            new_entry = old_entry.replace('author={Unknown}', f'author={{{author_str}}}')
            fixed_content = fixed_content.replace(old_entry, new_entry)
            fixed_count += 1
            print(f"  ✓ Fixed: {authors[0]} et al. ({len(authors)} authors)")
        else:
            print(f"  ✗ Failed to fetch")

        time.sleep(0.5)  # 避免请求过快

    # 保存
    output_file = bib_file.replace('.bib', '_fixed.bib')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    print(f"\n{'='*60}")
    print(f"✓ Fixed {fixed_count}/{len(matches)} entries")
    print(f"✓ Saved to: {output_file}")
    print(f"\nNext: mv {output_file} {bib_file}")

if __name__ == '__main__':
    main()
