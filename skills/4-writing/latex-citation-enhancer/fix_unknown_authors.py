#!/usr/bin/env python3
"""
验证和修复 BibTeX 中的 Unknown 作者。
从 arXiv API 获取真实的作者信息，确保引用准确无幻觉。
"""

import re
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

def extract_arxiv_id(entry: str) -> Optional[str]:
    """从 BibTeX 条目中提取 arXiv ID。"""
    # 从 journal 字段提取
    match = re.search(r'arXiv:(\d+\.\d+)', entry)
    if match:
        return match.group(1)

    # 从 url 字段提取
    match = re.search(r'arxiv\.org/abs/(\d+\.\d+)', entry)
    if match:
        return match.group(1)

    return None

def fetch_arxiv_metadata(arxiv_id: str) -> Optional[Dict]:
    """从 arXiv API 获取论文元数据。"""
    base_url = 'http://export.arxiv.org/api/query?'
    query = f'id_list={arxiv_id}'

    try:
        with urllib.request.urlopen(base_url + query) as response:
            xml_data = response.read().decode('utf-8')

        # 解析 XML
        root = ET.fromstring(xml_data)

        # 命名空间
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom'
        }

        entry = root.find('atom:entry', ns)
        if entry is None:
            return None

        # 提取信息
        title = entry.find('atom:title', ns)
        title_text = title.text.strip().replace('\n', ' ') if title is not None else None

        # 提取作者
        authors = []
        for author in entry.findall('atom:author', ns):
            name = author.find('atom:name', ns)
            if name is not None:
                authors.append(name.text.strip())

        # 提取发表日期
        published = entry.find('atom:published', ns)
        year = published.text[:4] if published is not None else None

        return {
            'title': title_text,
            'authors': authors,
            'year': year,
            'arxiv_id': arxiv_id
        }

    except Exception as e:
        print(f"  ⚠ Error fetching {arxiv_id}: {e}")
        return None

def parse_bibtex_entries(bib_content: str) -> List[Dict]:
    """解析 BibTeX 文件，提取所有条目。"""
    entries = []

    # 匹配 BibTeX 条目
    pattern = r'@(\w+)\{([^,]+),\s*(.*?)\n\}'
    matches = re.finditer(pattern, bib_content, re.DOTALL)

    for match in matches:
        entry_type = match.group(1)
        cite_key = match.group(2)
        content = match.group(3)
        full_entry = match.group(0)

        # 检查是否有 Unknown 作者
        if 'author={Unknown}' in full_entry:
            entries.append({
                'type': entry_type,
                'key': cite_key,
                'content': content,
                'full_entry': full_entry,
                'has_unknown_author': True
            })

    return entries

def format_authors_bibtex(authors: List[str]) -> str:
    """格式化作者列表为 BibTeX 格式。"""
    if not authors:
        return 'Unknown'

    # BibTeX 格式：FirstName LastName and FirstName LastName
    return ' and '.join(authors)

def fix_unknown_authors(bib_path: str, output_path: str = None):
    """修复 BibTeX 文件中的 Unknown 作者。"""

    if output_path is None:
        output_path = bib_path.replace('.bib', '_fixed.bib')

    print("="*70)
    print("BIBTEX UNKNOWN AUTHOR FIXER")
    print("="*70)

    # 读取 BibTeX 文件
    print(f"\n[1/4] Reading {bib_path}...")
    with open(bib_path, 'r', encoding='utf-8') as f:
        bib_content = f.read()

    # 解析条目
    print("\n[2/4] Parsing BibTeX entries...")
    entries = parse_bibtex_entries(bib_content)
    unknown_entries = [e for e in entries if e.get('has_unknown_author')]

    print(f"  ✓ Found {len(unknown_entries)} entries with Unknown authors")

    if not unknown_entries:
        print("\n✓ No Unknown authors found. Nothing to fix!")
        return

    # 从 arXiv 获取元数据
    print("\n[3/4] Fetching metadata from arXiv API...")
    fixes = []
    failed = []

    for i, entry in enumerate(unknown_entries, 1):
        print(f"\n  [{i}/{len(unknown_entries)}] Processing {entry['key']}...")

        # 提取 arXiv ID
        arxiv_id = extract_arxiv_id(entry['full_entry'])

        if not arxiv_id:
            print(f"    ⚠ No arXiv ID found, skipping")
            failed.append(entry['key'])
            continue

        print(f"    arXiv ID: {arxiv_id}")

        # 获取元数据
        metadata = fetch_arxiv_metadata(arxiv_id)

        if not metadata or not metadata.get('authors'):
            print(f"    ⚠ Failed to fetch metadata")
            failed.append(entry['key'])
            continue

        print(f"    ✓ Found {len(metadata['authors'])} authors")
        print(f"    Authors: {metadata['authors'][0]} et al.")

        # 记录修复
        fixes.append({
            'key': entry['key'],
            'old_entry': entry['full_entry'],
            'metadata': metadata
        })

        # 避免请求过快
        time.sleep(0.5)

    print(f"\n  ✓ Successfully fetched {len(fixes)} entries")
    print(f"  ⚠ Failed to fetch {len(failed)} entries")

    # 应用修复
    print("\n[4/4] Applying fixes...")
    fixed_content = bib_content

    for fix in fixes:
        old_entry = fix['old_entry']
        metadata = fix['metadata']

        # 生成新的作者字段
        new_authors = format_authors_bibtex(metadata['authors'])

        # 替换 author={Unknown}
        new_entry = old_entry.replace(
            'author={Unknown}',
            f'author={{{new_authors}}}'
        )

        # 如果标题也需要更新（可选）
        if metadata.get('title'):
            # 提取旧标题
            old_title_match = re.search(r'title=\{([^}]+)\}', old_entry)
            if old_title_match:
                old_title = old_title_match.group(1)
                # 只在旧标题是 Unknown 或空时更新
                if 'Unknown' in old_title or not old_title.strip():
                    new_entry = new_entry.replace(
                        f'title={{{old_title}}}',
                        f'title={{{metadata["title"]}}}'
                    )

        fixed_content = fixed_content.replace(old_entry, new_entry)

    # 保存修复后的文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    print(f"\n  ✓ Fixed BibTeX saved to: {output_path}")

    # 生成报告
    report_path = output_path.replace('.bib', '_report.json')
    report = {
        'total_unknown': len(unknown_entries),
        'fixed': len(fixes),
        'failed': failed,
        'fixes': [
            {
                'key': f['key'],
                'authors': f['metadata']['authors'],
                'title': f['metadata']['title']
            }
            for f in fixes
        ]
    }

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Report saved to: {report_path}")

    # 打印总结
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\n✓ Fixed {len(fixes)} / {len(unknown_entries)} Unknown authors")

    if failed:
        print(f"\n⚠ Failed to fix {len(failed)} entries:")
        for key in failed[:10]:
            print(f"  - {key}")
        if len(failed) > 10:
            print(f"  ... and {len(failed) - 10} more")

    print(f"\nNext steps:")
    print(f"  1. Review {output_path}")
    print(f"  2. If satisfied, replace original: mv {output_path} {bib_path}")
    print(f"  3. Recompile LaTeX: pdflatex && bibtex && pdflatex")

def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 fix_unknown_authors.py <bib_file> [output_file]")
        sys.exit(1)

    bib_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    fix_unknown_authors(bib_path, output_path)

if __name__ == '__main__':
    main()
