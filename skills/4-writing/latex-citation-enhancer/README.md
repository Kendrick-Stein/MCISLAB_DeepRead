# LaTeX Citation Enhancer

自动为 LaTeX 文档添加学术引用的 skill，基于 `Papers/` 目录中的历史阅读论文。

## 功能特性

- ✅ 自动分析 LaTeX 文档，识别需要引用的位置
- ✅ 从 `Papers/` 目录检索相关论文
- ✅ 通过 Zotero MCP 获取标准 BibTeX 条目（避免幻觉）
- ✅ 智能插入 `\cite{}` 命令
- ✅ 自动生成/更新 `.bib` 文件

## 前置要求

### 1. Zotero MCP 配置

已在项目根目录的 `.mcp.json` 中配置：

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

### 2. Zotero 本地 API

如果使用本地 Zotero（推荐）：
- 安装 Zotero 7+
- 在 Zotero 中启用本地 API：`Edit > Preferences > Advanced > API` → 勾选 "Enable local API"

如果使用 Zotero Web API：
- 获取 API key：https://www.zotero.org/settings/keys
- 修改 `.mcp.json` 中的 `env` 配置：
  ```json
  "env": {
    "ZOTERO_API_KEY": "your_api_key",
    "ZOTERO_LIBRARY_ID": "your_library_id",
    "ZOTERO_LIBRARY_TYPE": "user"
  }
  ```

## 使用方法

### 基本用法

```bash
/latex-citation-enhancer <latex_file_path>
```

例如：
```bash
/latex-citation-enhancer ~/Documents/paper_draft.tex
```

### 指定输出 BibTeX 文件

```bash
/latex-citation-enhancer <latex_file_path> <output_bib_path>
```

例如：
```bash
/latex-citation-enhancer ~/thesis/chapter3.tex ~/thesis/references.bib
```

## 工作流程

1. **构建论文索引**：扫描 `Papers/` 目录，提取所有论文的元数据
2. **分析 LaTeX 文档**：识别需要引用的关键陈述
3. **检索相关论文**：基于关键词、tags、主题匹配相关论文
4. **获取 BibTeX**：通过 Zotero MCP 获取标准引用格式
5. **插入引用**：在合适位置添加 `\cite{}` 命令
6. **生成 .bib 文件**：输出完整的 BibTeX 文件

## 示例

### 输入 LaTeX 文档

```latex
\section{Related Work}

Recent work has shown that visual agents can benefit from 
spatial memory representations for navigation tasks.
```

### 输出（增强后）

```latex
\section{Related Work}

Recent work has shown that visual agents can benefit from 
spatial memory representations for navigation tasks~\cite{Wang2025,Liu2024}.
```

### 生成的 BibTeX 文件

```bibtex
@article{Wang2025,
  title={AtlasVA: Self-Evolving Visual Skill Memory for Teacher-Free VLM Agents},
  author={Wang, Pan and Hu, Yihao and Liu, Xiujin and Yang, Jingchu and Wang, Hang and Wen, Zhihao},
  journal={arXiv preprint arXiv:2605.17933},
  year={2025}
}

@article{Liu2024,
  title={...},
  author={...},
  year={2024}
}
```

## 注意事项

- **不会修改原文内容**：只添加引用，不改变文档结构
- **避免重复引用**：已有的引用不会被重复添加
- **相关性优先**：只为高度相关的内容添加引用
- **可多次运行**：可以逐步完善引用，不会产生冲突

## 文件结构

```
skills/4-writing/latex-citation-enhancer/
├── SKILL.md                 # Skill 定义
├── README.md                # 本文档
├── build_paper_index.py     # 论文索引构建脚本
└── paper_index.json         # 生成的论文索引（自动生成）
```

## 故障排除

### Zotero MCP 连接失败

检查 Zotero 是否运行，以及本地 API 是否启用：
```bash
# 测试 Zotero MCP
zotero-mcp
```

### 论文索引为空

确保 `Papers/` 目录存在且包含论文笔记：
```bash
ls Papers/*.md | wc -l
```

### BibTeX 格式错误

通过 Zotero MCP 获取的 BibTeX 应该是标准格式。如果遇到问题，可以手动验证：
```bash
bibtex <your_file>.aux
```

## 相关资源

- [Zotero MCP GitHub](https://github.com/54yyyu/zotero-mcp)
- [MCP 文档](https://modelcontextprotocol.io/)
- [Skill Protocol](../../references/skill-protocol.md)
