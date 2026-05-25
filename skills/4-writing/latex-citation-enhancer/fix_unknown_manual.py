#!/usr/bin/env python3
"""
手动修复 Unknown 作者 - 使用从 Zotero 获取的真实作者信息
"""

import re

# 从 Zotero 获取的真实作者信息
AUTHOR_MAP = {
    '2504.17934': 'Chaoran Chen and Zhiping Zhang and Ibrahim Khalilov and Bingcan Guo and Simret A Gebreegziabher and Yanfang Ye and Ziang Xiao and Yaxing Yao and Tianshi Li and Toby Jia-Jun Li',
    '2410.13860': 'Runsen Xu and Zhiwei Huang and Tai Wang and Yilun Chen and Jiangmiao Pang and Dahua Lin',
    '2501.01149': 'Zhenting Wang and Shuming Hu and Shiyu Zhao and Xiaowen Lin and Felix Juefei-Xu and Zhuowei Li and Ligong Han and Harihar Subramanyam and Li Chen and Jianfa Chen and Nan Jiang and Lingjuan Lyu and Shiqing Ma and Dimitris N. Metaxas',
    '2503.18492': 'Jungjae Lee and Seongyeop Kim and Joonhyuk Kang and Dongyoon Hahm and Dongkyu Lee and Hyungjun Yoon and Taehwan Kwon and Youngjae Yu',
    '2506.03143': 'Qianhui Wu and Kanzhi Cheng and Rui Yang and Chaoyun Zhang and Jianwei Yang and Huiqiang Jiang and Jian Mu and Baolin Peng and Bo Qiao and Reuben Tan and Si Qin and Lars Liden and Qingwei Lin and Huan Zhang and Tong Zhang and Jianbing Zhang and Dongmei Zhang and Jianfeng Gao',
    '2507.05720': 'Yucheng Shi and Wenhao Yu and Zaitang Li and Yonglin Wang and Hongming Zhang and Ninghao Liu and Haitao Mi and Dong Yu',
    '2509.23263': 'Tao Xiong and Xavier Hu and Yurun Chen and Yuhang Liu and Changqiao Wu and Pengzhi Gao and Wei Liu and Jian Luan and Shengyu Zhang',
    '2510.04791': 'Kristian Kolthoff and Felix Kretzer and Simone Paolo Ponzetto and Alexander Maedche and Christian Bartelt',
    '2601.21352': 'Ziyu Lu and Tengjin Weng and Yiying Yang and Yuhang Zhao and Xinxin Huang and Wenhao Jiang',
    '2604.27776': 'Jinchao Li and Yunxin Li and Chenrui Zhao and Zhenran Xu and Baotian Hu and Min Zhang',
    '2605.04785': 'Chenglin Yang',
}

def main():
    bib_file = '/Users/kendrickstein/Code/Reward-Agent/writing/references.bib'

    print("Reading BibTeX file...")
    with open(bib_file, 'r', encoding='utf-8') as f:
        content = f.read()

    fixed_count = 0

    for arxiv_id, authors in AUTHOR_MAP.items():
        # 查找包含此 arXiv ID 且作者为 Unknown 的条目
        pattern = rf'(@\w+\{{[^}}]+,\s*title=\{{[^}}]+\}},\s*author=\{{Unknown\}},[^}}]*(?:arxiv\.org/abs/{re.escape(arxiv_id)}|arXiv:{re.escape(arxiv_id)})[^}}]*\}})'

        matches = list(re.finditer(pattern, content, re.DOTALL | re.IGNORECASE))

        if matches:
            print(f"\n[{arxiv_id}] Found {len(matches)} entries")
            for match in matches:
                old_entry = match.group(1)
                new_entry = old_entry.replace('author={Unknown}', f'author={{{authors}}}')
                content = content.replace(old_entry, new_entry)
                fixed_count += 1
                print(f"  ✓ Fixed: {authors.split(' and ')[0]} et al.")

    # 保存
    output_file = bib_file.replace('.bib', '_fixed_manual.bib')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n{'='*60}")
    print(f"✓ Fixed {fixed_count} entries")
    print(f"✓ Saved to: {output_file}")

    # 检查剩余 Unknown
    remaining = content.count('author={Unknown}')
    print(f"\nRemaining Unknown authors: {remaining}")

    if remaining > 0:
        print("\nRemaining Unknown entries:")
        unknown_pattern = r'@\w+\{([^,]+),[^}]*author=\{Unknown\}[^}]*title=\{([^}]+)\}'
        for match in re.finditer(unknown_pattern, content):
            key, title = match.groups()
            print(f"  - {key}: {title[:60]}...")

if __name__ == '__main__':
    main()
