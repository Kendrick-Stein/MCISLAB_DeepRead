#!/usr/bin/env python3
"""
批量导入论文到 Zotero 并生成 BibTeX 文件
"""
import json
import time
from pathlib import Path

def load_paper_index():
    """加载论文索引"""
    index_file = Path("skills/4-writing/latex-citation-enhancer/paper_index.json")
    with open(index_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def filter_papers_with_url(papers):
    """筛选有 URL 的论文"""
    return [p for p in papers if p.get('url')]

def main():
    papers = load_paper_index()
    papers_with_url = filter_papers_with_url(papers)

    print(f"总论文数: {len(papers)}")
    print(f"有 URL 的论文: {len(papers_with_url)}")
    print(f"\n准备导入到 Zotero...")

    # 输出待导入的论文列表
    output_file = Path("skills/4-writing/latex-citation-enhancer/papers_to_import.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(papers_with_url, f, ensure_ascii=False, indent=2)

    print(f"待导入论文列表已保存到: {output_file}")
    print(f"\n前 10 篇论文:")
    for i, p in enumerate(papers_with_url[:10], 1):
        print(f"{i}. {p['title'][:60]}")
        print(f"   URL: {p['url']}")

if __name__ == '__main__':
    main()
