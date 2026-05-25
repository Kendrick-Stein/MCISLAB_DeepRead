#!/usr/bin/env python3
"""
从 Papers/ 目录的 frontmatter 直接生成 BibTeX 文件
"""
import json
import re
from pathlib import Path

def generate_citation_key(authors, year, title):
    """生成 citation key: FirstAuthorYYYY"""
    if authors and len(authors) > 0:
        # 提取第一作者的姓
        first_author = authors[0]
        # 移除特殊字符，只保留字母
        last_name = re.sub(r'[^a-zA-Z]', '', first_author.split()[-1])
    else:
        # 如果没有作者，使用标题的第一个单词
        title_words = re.findall(r'\b[A-Z][a-z]+\b', title)
        last_name = title_words[0] if title_words else 'Unknown'

    year_str = year if year else '2024'
    return f"{last_name}{year_str}"

def format_authors(authors):
    """格式化作者列表为 BibTeX 格式"""
    if not authors:
        return ""
    return " and ".join(authors)

def escape_latex(text):
    """转义 LaTeX 特殊字符"""
    if not text:
        return ""
    # 基本转义
    text = text.replace('&', r'\&')
    text = text.replace('%', r'\%')
    text = text.replace('$', r'\$')
    text = text.replace('#', r'\#')
    text = text.replace('_', r'\_')
    text = text.replace('{', r'\{')
    text = text.replace('}', r'\}')
    return text

def paper_to_bibtex(paper):
    """将论文信息转换为 BibTeX 条目"""
    title = escape_latex(paper.get('title', ''))
    authors = paper.get('authors', [])
    year = paper.get('year', '')
    venue = paper.get('venue', 'arXiv')
    url = paper.get('url', '')

    # 生成 citation key
    citation_key = generate_citation_key(authors, year, title)

    # 确定条目类型
    if 'arxiv' in url.lower():
        entry_type = 'article'
        journal = 'arXiv preprint'
    elif venue and venue.lower() != 'arxiv':
        entry_type = 'inproceedings'
        journal = venue
    else:
        entry_type = 'article'
        journal = 'arXiv preprint'

    # 构建 BibTeX 条目
    bibtex = f"@{entry_type}{{{citation_key},\n"
    bibtex += f"  title={{{title}}},\n"

    if authors:
        bibtex += f"  author={{{format_authors(authors)}}},\n"

    if year:
        bibtex += f"  year={{{year}}},\n"

    if journal:
        if entry_type == 'inproceedings':
            bibtex += f"  booktitle={{{journal}}},\n"
        else:
            bibtex += f"  journal={{{journal}}},\n"

    if url:
        bibtex += f"  url={{{url}}},\n"

    # 移除最后的逗号
    bibtex = bibtex.rstrip(',\n') + '\n'
    bibtex += "}\n"

    return citation_key, bibtex

def main():
    # 读取论文索引
    index_file = Path("skills/4-writing/latex-citation-enhancer/paper_index.json")
    with open(index_file, 'r', encoding='utf-8') as f:
        papers = json.load(f)

    print(f"从 {len(papers)} 篇论文生成 BibTeX...")

    # 生成 BibTeX 条目
    bibtex_entries = []
    citation_keys = []

    for paper in papers:
        try:
            citation_key, bibtex = paper_to_bibtex(paper)
            bibtex_entries.append(bibtex)
            citation_keys.append(citation_key)
        except Exception as e:
            print(f"警告: 处理论文失败 - {paper.get('title', 'Unknown')}: {e}")

    # 保存 BibTeX 文件
    output_file = Path("references.bib")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("% BibTeX file generated from ReadPaperMachine Papers/\n")
        f.write(f"% Total entries: {len(bibtex_entries)}\n")
        f.write(f"% Generated: {Path.cwd()}\n\n")
        f.write("\n".join(bibtex_entries))

    print(f"\n✅ 成功生成 BibTeX 文件: {output_file}")
    print(f"   总条目数: {len(bibtex_entries)}")
    print(f"\n前 5 个 citation keys:")
    for i, key in enumerate(citation_keys[:5], 1):
        print(f"   {i}. {key}")

    # 保存 citation keys 列表
    keys_file = Path("skills/4-writing/latex-citation-enhancer/citation_keys.txt")
    with open(keys_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(citation_keys))

    print(f"\n📝 Citation keys 已保存到: {keys_file}")

if __name__ == '__main__':
    main()
