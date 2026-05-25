#!/usr/bin/env python3
"""
使用 Zotero Web API 批量导入论文并生成 BibTeX
"""
import json
import requests
import time
from pathlib import Path

# Zotero API 配置
API_KEY = "K6RluVSWYvxrpxoZ46mI0Lb5"
LIBRARY_ID = "20631142"
LIBRARY_TYPE = "user"
BASE_URL = f"https://api.zotero.org/{LIBRARY_TYPE}s/{LIBRARY_ID}"

def add_paper_by_url(url):
    """通过 URL 添加论文到 Zotero"""
    headers = {
        "Zotero-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    # 使用 Zotero 的 translation server
    translate_url = "https://translation.zotero.org/web"

    try:
        # 第一步：获取论文元数据
        response = requests.post(
            translate_url,
            json={"url": url},
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code != 200:
            return None, f"Translation failed: {response.status_code}"

        items = response.json()
        if not items:
            return None, "No metadata found"

        # 第二步：添加到 Zotero
        item = items[0]
        create_response = requests.post(
            f"{BASE_URL}/items",
            json=[item],
            headers=headers,
            timeout=30
        )

        if create_response.status_code in [200, 201]:
            return item, None
        else:
            return None, f"Failed to add: {create_response.status_code}"

    except Exception as e:
        return None, str(e)

def main():
    # 读取待导入论文
    with open("skills/4-writing/latex-citation-enhancer/papers_to_import.json", 'r') as f:
        papers = json.load(f)

    print(f"准备导入 {len(papers)} 篇论文到 Zotero...")
    print("这可能需要一些时间，请耐心等待...\n")

    success_count = 0
    failed_count = 0
    failed_papers = []

    for i, paper in enumerate(papers, 1):
        url = paper.get('url')
        title = paper.get('title', 'Unknown')

        print(f"[{i}/{len(papers)}] {title[:60]}...")

        if not url:
            print("  ⚠️  跳过：无 URL")
            failed_count += 1
            continue

        item, error = add_paper_by_url(url)

        if item:
            print(f"  ✅ 成功")
            success_count += 1
        else:
            print(f"  ❌ 失败: {error}")
            failed_count += 1
            failed_papers.append({"title": title, "url": url, "error": error})

        # 避免 API 限流
        time.sleep(1)

        # 每 10 篇显示进度
        if i % 10 == 0:
            print(f"\n进度: {success_count} 成功, {failed_count} 失败\n")

    print(f"\n{'='*60}")
    print(f"导入完成！")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"{'='*60}")

    # 保存失败列表
    if failed_papers:
        with open("skills/4-writing/latex-citation-enhancer/failed_imports.json", 'w') as f:
            json.dump(failed_papers, f, ensure_ascii=False, indent=2)
        print(f"\n失败的论文已保存到: failed_imports.json")

if __name__ == '__main__':
    main()
