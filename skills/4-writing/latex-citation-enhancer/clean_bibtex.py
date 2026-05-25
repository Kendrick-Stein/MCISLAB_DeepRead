#!/usr/bin/env python3
"""
全面清理 BibTeX 文件：
1. 移除重复键
2. 修复格式问题
3. 生成报告
"""

import re
from collections import defaultdict

def extract_first_author_year(entry_text):
    """从条目中提取第一作者和年份"""
    author_match = re.search(r'author=\{([^}]+)\}', entry_text)
    year_match = re.search(r'year=\{?(\d{4})\}?', entry_text)

    if author_match and year_match:
        authors = author_match.group(1)
        year = year_match.group(1)

        # 提取第一作者姓氏
        first_author = authors.split(' and ')[0].strip()
        # 取最后一个词作为姓氏
        last_name = first_author.split()[-1].replace(',', '')

        return f"{last_name}{year}"

    return None

def main():
    bib_file = '/Users/kendrickstein/Code/Reward-Agent/writing/references.bib'

    print("Reading BibTeX file...")
    with open(bib_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 分割成单独的条目
    entries = re.split(r'\n(?=@)', content)

    seen_keys = {}
    fixed_entries = []
    duplicate_count = 0
    renamed_count = 0

    for entry in entries:
        if not entry.strip() or not entry.startswith('@'):
            continue

        # 提取键名
        key_match = re.match(r'@(\w+)\{([^,]+),', entry)
        if not key_match:
            fixed_entries.append(entry)
            continue

        entry_type = key_match.group(1)
        old_key = key_match.group(2)

        # 如果键已存在，重命名
        if old_key in seen_keys:
            duplicate_count += 1

            # 尝试从内容生成新键
            new_key = extract_first_author_year(entry)

            if not new_key or new_key in seen_keys:
                # 添加后缀
                suffix = 'a'
                base_key = new_key if new_key else old_key
                while f"{base_key}{suffix}" in seen_keys:
                    suffix = chr(ord(suffix) + 1)
                new_key = f"{base_key}{suffix}"

            # 替换键名
            entry = entry.replace(f'@{entry_type}{{{old_key},', f'@{entry_type}{{{new_key},', 1)
            print(f"  Renamed duplicate: {old_key} -> {new_key}")
            renamed_count += 1
            seen_keys[new_key] = True
        else:
            seen_keys[old_key] = True

        fixed_entries.append(entry)

    # 重新组合
    fixed_content = '\n'.join(fixed_entries)

    # 保存
    output_file = bib_file.replace('.bib', '_cleaned.bib')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    print(f"\n{'='*60}")
    print(f"✓ Processed {len(fixed_entries)} entries")
    print(f"✓ Found {duplicate_count} duplicates")
    print(f"✓ Renamed {renamed_count} entries")
    print(f"✓ Saved to: {output_file}")

if __name__ == '__main__':
    main()
