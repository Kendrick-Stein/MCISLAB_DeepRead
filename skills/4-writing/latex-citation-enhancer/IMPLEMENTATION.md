# LaTeX Citation Enhancer 实现方案

## 概述

已成功实现 `latex-citation-enhancer` skill，可以自动为 LaTeX 文档添加学术引用，基于 `Papers/` 目录中的历史阅读论文，并通过 Zotero MCP 确保引用的准确性。

## 实现的功能

### 1. Zotero MCP 配置 ✅

**位置**：`/Users/kendrickstein/Code/ReadPaperMachine/.mcp.json`

```json
{
  "mcpServers": {
    "zotero": {
      "command": "zotero-mcp",
      "env": {
        "ZOTERO_LOCAL": "true"
      }
    }
  }
}
```

**说明**：
- 使用本地 Zotero API（需要 Zotero 7+）
- 避免需要配置 API key 的复杂性
- 支持离线工作

### 2. 论文索引构建工具 ✅

**位置**：`skills/4-writing/latex-citation-enhancer/build_paper_index.py`

**功能**：
- 扫描 `Papers/` 目录中的所有 Markdown 论文笔记
- 解析 YAML frontmatter 提取元数据
- 提取 Summary 部分
- 生成 JSON 索引文件供快速检索

**测试结果**：
```
✓ 成功索引 456 篇论文
✓ 输出文件：paper_index.json
```

### 3. LaTeX Citation Enhancer Skill ✅

**位置**：`skills/4-writing/latex-citation-enhancer/SKILL.md`

**核心工作流程**：

```
1. 准备阶段
   ├─ 验证输入文件
   ├─ 构建论文索引
   └─ 加载 Papers/ 元数据

2. 分析 LaTeX 文档
   ├─ 识别已有引用
   ├─ 查找需要引用的位置
   └─ 提取关键概念

3. 检索相关论文
   ├─ 匹配 tags
   ├─ 匹配 title 关键词
   ├─ 匹配 summary 内容
   └─ 按相关性排序

4. 获取 BibTeX（通过 Zotero MCP）
   ├─ zotero_add_by_doi
   ├─ zotero_add_by_url
   └─ zotero_get_item_metadata

5. 插入引用
   ├─ 在合适位置添加 \cite{}
   └─ 避免重复引用

6. 生成 BibTeX 文件
   ├─ 收集所有引用条目
   ├─ 合并现有 .bib 文件
   └─ 输出标准格式
```

## 技术架构

### 数据流

```
Papers/*.md
    ↓
[build_paper_index.py]
    ↓
paper_index.json
    ↓
[latex-citation-enhancer skill]
    ↓
LaTeX 文档 + .bib 文件
```

### 关键组件

1. **论文索引**：
   - 格式：JSON
   - 字段：filename, title, authors, year, venue, tags, url, summary, rating
   - 更新：每次运行 skill 时重新构建

2. **Zotero MCP 集成**：
   - 工具：`zotero_add_by_doi`, `zotero_add_by_url`, `zotero_get_item_metadata`
   - 格式：BibTeX
   - 优势：标准化、无幻觉

3. **引用匹配算法**：
   - 基于关键词匹配
   - 考虑 tags 相关性
   - 结合 rating 排序

## 使用示例

### 场景 1：为论文草稿添加引用

```bash
/latex-citation-enhancer ~/Documents/paper_draft.tex
```

**输入**：
```latex
\section{Introduction}
Recent advances in visual language models have enabled 
new capabilities in GUI automation.
```

**输出**：
```latex
\section{Introduction}
Recent advances in visual language models have enabled 
new capabilities in GUI automation~\cite{Wang2025,Liu2024}.
```

### 场景 2：为论文章节指定引用文件

```bash
/latex-citation-enhancer ~/thesis/chapter3.tex ~/thesis/references.bib
```

## 安全保障

### Guard 规则

- ✅ 不修改 LaTeX 文档主要内容
- ✅ 不删除已有引用
- ✅ 不重复添加相同引用
- ✅ 不强行添加不相关引用
- ✅ 不编造 BibTeX 条目（必须通过 Zotero MCP）
- ✅ 不修改 Papers/ 目录

### Verify 检查清单

- [ ] 论文索引成功构建
- [ ] `\cite{}` 命令格式正确
- [ ] BibTeX 文件语法正确
- [ ] 每个 citation key 都有对应条目
- [ ] 包含 `\bibliography{}` 命令
- [ ] 没有重复的 BibTeX 条目
- [ ] 所有引用的论文存在于 Papers/
- [ ] 引用位置合理

## 文件清单

```
ReadPaperMachine/
├── .mcp.json                                    # MCP 配置
└── skills/4-writing/latex-citation-enhancer/
    ├── SKILL.md                                 # Skill 定义
    ├── README.md                                # 使用文档
    ├── build_paper_index.py                     # 索引构建脚本
    ├── paper_index.json                         # 生成的索引（自动）
    └── IMPLEMENTATION.md                        # 本文档
```

## 依赖项

### Python 包
- ✅ `zotero-mcp-server` (v0.3.0) - 已安装

### 系统要求
- Python 3.10+
- Zotero 7+ (可选，用于本地 API)

### MCP 服务器
- ✅ Zotero MCP - 已配置

## 下一步优化建议

### 短期优化

1. **缓存机制**：
   - 缓存 Zotero MCP 查询结果
   - 避免重复查询相同论文

2. **相关性算法改进**：
   - 使用 TF-IDF 或语义相似度
   - 考虑论文发表时间（优先引用近期工作）

3. **引用位置优化**：
   - 更智能的引用位置识别
   - 支持不同的引用风格（\citep, \citet 等）

### 长期扩展

1. **多语言支持**：
   - 支持中文 LaTeX 文档
   - 处理混合语言引用

2. **引用推荐**：
   - 基于文档主题推荐可能缺失的重要引用
   - 检测引用覆盖的完整性

3. **可视化界面**：
   - 显示引用关系图
   - 交互式选择引用

## 测试验证

### 已验证功能

- ✅ Zotero MCP 安装成功
- ✅ MCP 配置文件创建
- ✅ 论文索引构建（456 篇论文）
- ✅ Python 脚本语法正确

### 待测试功能

- [ ] 完整的 LaTeX 文档处理流程
- [ ] Zotero MCP 实际调用
- [ ] BibTeX 文件生成
- [ ] 引用插入准确性

## 参考资源

- [Zotero MCP GitHub](https://github.com/54yyyu/zotero-mcp)
- [Zotero MCP 文档](https://github.com/54yyyu/zotero-mcp/blob/main/docs/getting-started.md)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Skill Protocol](../../references/skill-protocol.md)

---

**实现日期**：2026-05-22  
**状态**：✅ 完成  
**版本**：v1.0
