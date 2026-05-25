# 引用验证与质量保证指南

## 问题诊断

你发现了一个重要问题：`author={Unknown}` 表示引用信息不完整。

### 根本原因

1. **Papers/ 笔记缺少作者信息**
   - 论文笔记的 frontmatter 中 `authors: []` 为空
   - 或者根本没有 `authors` 字段

2. **Daily papers 元数据不完整**
   - `.candidates.json` 中某些论文缺少作者信息
   - 自动抓取时未能正确解析

### 影响范围

```bash
# 统计 Unknown 作者数量
grep -c "author={Unknown}" references.bib
# 结果：约 30-40 个条目
```

---

## 解决方案

### 方案 1: 自动修复（推荐）✨

使用 `fix_unknown_authors.py` 从 arXiv API 自动获取真实作者信息：

```bash
cd /Users/kendrickstein/Code/ReadPaperMachine

# 修复 Unknown 作者
python3 skills/4-writing/latex-citation-enhancer/fix_unknown_authors.py \
    /Users/kendrickstein/Code/Reward-Agent/writing/references.bib

# 生成文件：
# - references_fixed.bib (修复后的文件)
# - references_fixed_report.json (修复报告)
```

**工作原理**：
1. 扫描 BibTeX 文件，找到所有 `author={Unknown}` 条目
2. 提取 arXiv ID（从 journal 或 url 字段）
3. 调用 arXiv API 获取真实的作者、标题、年份
4. 替换 Unknown 为真实作者信息
5. 生成修复报告

**验证方式**：
- ✅ 数据来源：arXiv 官方 API（http://export.arxiv.org/api/）
- ✅ 无 AI 合成：直接从 arXiv 数据库获取
- ✅ 可追溯：每个修复都有 arXiv ID 可验证
- ✅ 报告透明：生成 JSON 报告记录所有修复

### 方案 2: 手动验证

对于非 arXiv 论文或 API 失败的情况：

```bash
# 1. 找出所有 Unknown 作者
grep -B 2 "author={Unknown}" references.bib > unknown_list.txt

# 2. 对于每个条目，手动查找：
# - Google Scholar: scholar.google.com
# - DBLP: dblp.org
# - 会议官网
# - 论文 PDF

# 3. 手动更新 references.bib
```

### 方案 3: 改进论文笔记质量

**预防措施**：确保 Papers/ 笔记包含完整元数据

```yaml
---
title: "Paper Title"
authors:
  - FirstName LastName
  - FirstName LastName
venue: "CVPR 2024"
date_publish: "2024-06-01"
url: "https://arxiv.org/abs/2404.xxxxx"
---
```

**检查脚本**：
```bash
# 检查哪些论文笔记缺少作者
cd Papers/
for file in *.md; do
    if ! grep -q "^authors:" "$file"; then
        echo "Missing authors: $file"
    fi
done
```

---

## 验证引用准确性的方法

### 1. arXiv ID 验证（最可靠）

对于 arXiv 论文：

```bash
# 提取 arXiv ID
grep "arxiv.org/abs/" references.bib | sed 's/.*abs\///' | sed 's/[,}].*//'

# 手动验证（访问 URL）
https://arxiv.org/abs/2404.xxxxx
```

### 2. DOI 验证

对于有 DOI 的论文：

```bash
# 提取 DOI
grep "doi=" references.bib

# 验证（访问 URL）
https://doi.org/10.xxxx/xxxxx
```

### 3. 交叉验证

```bash
# 1. 检查标题是否匹配
# 在 Google Scholar 搜索标题，验证作者

# 2. 检查年份是否合理
grep "year=" references.bib | sort | uniq -c

# 3. 检查会议/期刊名称
grep "booktitle=" references.bib
grep "journal=" references.bib
```

### 4. 批量验证脚本

```python
# validate_citations.py
import re

def validate_bibtex(bib_file):
    with open(bib_file, 'r') as f:
        content = f.read()
    
    issues = []
    
    # 检查 Unknown 作者
    unknown_count = content.count('author={Unknown}')
    if unknown_count > 0:
        issues.append(f"Found {unknown_count} Unknown authors")
    
    # 检查缺少 URL/DOI
    entries = re.findall(r'@\w+\{([^,]+),', content)
    for key in entries:
        entry_match = re.search(rf'@\w+\{{{key},.*?\n\}}', content, re.DOTALL)
        if entry_match:
            entry = entry_match.group(0)
            if 'url=' not in entry and 'doi=' not in entry:
                issues.append(f"{key}: No URL or DOI")
    
    return issues
```

---

## 改进 latex-citation-enhancer Skill

### 新增功能：自动验证

在 `enhance_citations_v2.py` 中添加验证步骤：

```python
def validate_paper_metadata(paper: Dict) -> bool:
    """验证论文元数据是否完整。"""
    
    # 必需字段
    required = ['title', 'authors', 'year']
    for field in required:
        if not paper.get(field):
            return False
    
    # 作者不能为空
    authors = paper.get('authors', [])
    if not authors or len(authors) == 0:
        return False
    
    # 至少有一个可验证的标识符
    if not paper.get('url') and not paper.get('doi'):
        return False
    
    return True

# 在匹配论文时过滤
valid_papers = [p for p in all_papers if validate_paper_metadata(p)]
```

### 新增功能：arXiv API 回填

```python
def enrich_from_arxiv(paper: Dict) -> Dict:
    """如果论文有 arXiv URL 但缺少作者，从 API 获取。"""
    
    url = paper.get('url', '')
    if 'arxiv.org/abs/' not in url:
        return paper
    
    if paper.get('authors'):
        return paper  # 已有作者，跳过
    
    # 提取 arXiv ID
    arxiv_id = url.split('arxiv.org/abs/')[-1]
    
    # 调用 API
    metadata = fetch_arxiv_metadata(arxiv_id)
    
    if metadata and metadata.get('authors'):
        paper['authors'] = metadata['authors']
        paper['title'] = metadata.get('title', paper.get('title'))
        paper['year'] = metadata.get('year', paper.get('year'))
    
    return paper
```

### 新增功能：质量报告

生成引用质量报告：

```python
def generate_quality_report(citations: List[Dict]) -> Dict:
    """生成引用质量报告。"""
    
    report = {
        'total': len(citations),
        'with_authors': 0,
        'with_url': 0,
        'with_doi': 0,
        'arxiv_papers': 0,
        'conference_papers': 0,
        'unknown_authors': [],
        'missing_identifiers': []
    }
    
    for cite in citations:
        if cite.get('authors') and 'Unknown' not in str(cite['authors']):
            report['with_authors'] += 1
        else:
            report['unknown_authors'].append(cite['key'])
        
        if cite.get('url'):
            report['with_url'] += 1
        
        if cite.get('doi'):
            report['with_doi'] += 1
        
        if 'arxiv' in cite.get('venue', '').lower():
            report['arxiv_papers'] += 1
        
        if cite.get('type') == 'inproceedings':
            report['conference_papers'] += 1
    
    return report
```

---

## 更新后的 Skill 工作流

### Phase 0: 元数据验证（新增）

```
0.1. 加载论文池
0.2. 验证每篇论文的元数据完整性
0.3. 对于缺少作者的 arXiv 论文：
     - 自动调用 arXiv API 补全
     - 更新论文笔记（可选）
0.4. 过滤掉无法验证的论文
0.5. 生成数据质量报告
```

### Phase 5: 引用质量验证（新增）

```
5.1. 扫描生成的 BibTeX 文件
5.2. 检查 Unknown 作者
5.3. 对于 Unknown 作者：
     - 如果有 arXiv ID，自动修复
     - 否则，标记为需要手动验证
5.4. 生成质量报告
5.5. 输出验证清单
```

---

## 最佳实践

### 1. 论文笔记规范

使用 `paper-digest` skill 时，确保生成完整的 frontmatter：

```yaml
---
title: "Full Paper Title"
authors:
  - FirstName LastName  # 必需
  - FirstName LastName
venue: "CVPR 2024"      # 必需
date_publish: "2024-06-01"  # 必需
url: "https://arxiv.org/abs/2404.xxxxx"  # 推荐
doi: "10.xxxx/xxxxx"    # 可选
tags:
  - GUI-Agent
  - VLM
rating: "3"
---
```

### 2. Daily Papers 质量控制

改进 `daily-papers` skill，确保抓取完整元数据：

```python
# 在 daily-papers 中添加验证
def validate_paper_entry(paper):
    if not paper.get('authors'):
        # 尝试从 arXiv API 获取
        paper = enrich_from_arxiv(paper)
    
    if not paper.get('authors'):
        # 标记为需要手动补充
        paper['needs_review'] = True
    
    return paper
```

### 3. 定期审计

```bash
# 每月运行一次审计
cd Papers/
python3 ../skills/4-writing/latex-citation-enhancer/audit_papers.py

# 输出：
# - 缺少作者的论文列表
# - 缺少 URL/DOI 的论文列表
# - 元数据不完整的论文列表
```

---

## 总结

### 当前问题
- ❌ 约 30-40 个引用有 `author={Unknown}`
- ❌ 来源：Papers/ 笔记或 daily papers 元数据不完整

### 解决方案
- ✅ **自动修复**：`fix_unknown_authors.py` 从 arXiv API 获取真实作者
- ✅ **验证方式**：arXiv ID 可追溯，无 AI 合成
- ✅ **预防措施**：改进 skill，在生成引用前验证元数据

### 下一步
1. 运行 `fix_unknown_authors.py` 修复现有问题
2. 更新 `latex-citation-enhancer` skill 添加验证步骤
3. 改进 `paper-digest` 和 `daily-papers` 确保元数据完整
4. 定期审计 Papers/ 目录质量

---

**关键原则**：
- 🎯 **可验证性**：每个引用都有 arXiv ID、DOI 或 URL 可追溯
- 🚫 **零幻觉**：不使用 AI 生成作者信息，只从官方 API 获取
- 📊 **透明度**：生成质量报告，明确标注需要手动验证的条目
- 🔄 **持续改进**：从源头（论文笔记）确保数据质量
