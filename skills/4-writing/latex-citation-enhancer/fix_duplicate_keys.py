#!/usr/bin/env python3
"""
修复 BibTeX 文件中的重复键名
"""

import re
from collections import defaultdict

def main():
    bib_file = '/Users/kendrickstein/Code/Reward-Agent/writing/references.bib'

    print("Reading BibTeX file...")
    with open(bib_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到所有 BibTeX 条目
    pattern = r'@(\w+)\{([^,]+),'
    matches = list(re.finditer(pattern, content))

    # 统计键名出现次数
    key_counts = defaultdict(int)
    for match in matches:
        key = match.group(2)
        key_counts[key] += 1

    # 找出重复的键
    duplicates = {k: v for k, v in key_counts.items() if v > 1}

    if not duplicates:
        print("No duplicate keys found!")
        return

    print(f"\nFound {len(duplicates)} duplicate keys:")
    for key, count in sorted(duplicates.items()):
        print(f"  {key}: {count} occurrences")

    # 修复重复键
    fixed_content = content
    key_occurrence = defaultdict(int)

    for match in matches:
        entry_type = match.group(1)
        old_key = match.group(2)

        if old_key in duplicates:
            key_occurrence[old_key] += 1

            if key_occurrence[old_key] > 1:
                # 为重复的键添加后缀
                suffix_map = {2: 'a', 3: 'b', 4: 'c', 5: 'd', 6: 'e', 7: 'f', 8: 'g', 9: 'h', 10: 'i', 11: 'j', 12: 'k', 13: 'l', 14: 'm', 15: 'n', 16: 'o', 17: 'p', 18: 'q', 19: 'r', 20: 's', 21: 't', 22: 'u', 23: 'v', 24: 'w', 25: 'x', 26: 'y', 27: 'z'}
                suffix = suffix_map.get(key_occurrence[old_key], str(key_occurrence[old_key]))
                new_key = f"{old_key}{suffix}"

                # 替换第 N 次出现的键
                old_pattern = f'@{entry_type}{{{old_key},'
                new_pattern = f'@{entry_type}{{{new_key},'

                # 只替换当前这一个
                pos = match.start()
                fixed_content = fixed_content[:pos] + fixed_content[pos:].replace(old_pattern, new_pattern, 1)

                print(f"  Renamed: {old_key} -> {new_key}")

    # 保存
    output_file = bib_file.replace('.bib', '_dedup.bib')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    print(f"\n{'='*60}")
    print(f"✓ Fixed duplicate keys")
    print(f"✓ Saved to: {output_file}")

if __name__ == '__main__':
    main()
