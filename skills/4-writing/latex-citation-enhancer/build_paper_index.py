#!/usr/bin/env python3
"""
构建论文索引，从 Papers/ 目录提取元数据用于快速检索
"""
import re
import json
from pathlib import Path
from typing import Dict, List, Any

def parse_frontmatter(content: str) -> Dict[str, Any]:
    """解析 YAML frontmatter"""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    frontmatter = {}
    yaml_content = match.group(1)

    # 简单的 YAML 解析（处理常见格式）
    for line in yaml_content.split('\n'):
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()

        # 处理列表
        if value.startswith('[') and value.endswith(']'):
            value = [v.strip() for v in value[1:-1].split(',')]
        # 处理字符串
        elif value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]

        frontmatter[key] = value

    return frontmatter

def extract_summary(content: str) -> str:
    """提取 Summary 部分"""
    match = re.search(r'## Summary\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def build_index(papers_dir: Path) -> List[Dict[str, Any]]:
    """构建论文索引"""
    index = []

    for paper_file in papers_dir.glob('*.md'):
        try:
            content = paper_file.read_text(encoding='utf-8')
            frontmatter = parse_frontmatter(content)
            summary = extract_summary(content)

            # 提取关键信息
            paper_info = {
                'filename': paper_file.name,
                'title': frontmatter.get('title', ''),
                'authors': frontmatter.get('authors', []),
                'year': frontmatter.get('date_publish', '')[:4] if frontmatter.get('date_publish') else '',
                'venue': frontmatter.get('venue', ''),
                'tags': frontmatter.get('tags', []),
                'url': frontmatter.get('url', ''),
                'summary': summary,
                'rating': frontmatter.get('rating', 0)
            }

            index.append(paper_info)
        except Exception as e:
            print(f"Warning: Failed to process {paper_file.name}: {e}")

    return index

def main():
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent
    papers_dir = project_root / 'Papers'
    output_file = script_dir / 'paper_index.json'

    if not papers_dir.exists():
        print(f"Error: Papers directory not found at {papers_dir}")
        return

    print(f"Building paper index from {papers_dir}...")
    index = build_index(papers_dir)

    # 保存索引
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"Index built successfully: {len(index)} papers indexed")
    print(f"Output: {output_file}")

if __name__ == '__main__':
    main()
