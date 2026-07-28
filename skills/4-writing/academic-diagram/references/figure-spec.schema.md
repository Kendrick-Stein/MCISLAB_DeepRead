# figure-spec.json — 结构化图自动布局规范

> **B 路（dot-to-tikz）入口**。Claude 只输出本规范的 JSON spec，**不写任何坐标**。
> `references/dot-to-tikz.py` 调用 graphviz 算位置，套学术配色模板生成 .tex。
> 适用：架构图 / 流水线 / DAG / 分层 / 三栏映射等纯结构化图。
> **不适用**：含嵌入热力图/曲线/柱状的富视觉图——走 A 路（vision feedback）。

## Schema

```json
{
  "title": "可选标题",
  "layout": {
    "engine": "dot",
    "rankdir": "LR | TB | BT | RL",
    "nodesep": 0.6,
    "ranksep": 1.0
  },
  "colors": "academic | drawio",
  "zones": [
    {
      "id": "encoding",
      "label": "Encoding Stage",
      "members": ["text_enc", "image_enc"],
      "color": "blue"
    }
  ],
  "nodes": [
    {
      "id": "text_enc",
      "label": "Text Encoder $E_t$",
      "color": "blue",
      "size": "normal | hero | small",
      "shape": "rect | diamond | cylinder | circle"
    }
  ],
  "edges": [
    {
      "from": "text_enc",
      "to": "cmam",
      "style": "main | control | feedback | contrast",
      "label": "$\\mathbf{h}_t$"
    }
  ]
}
```

## 字段约定

### `layout`
- `engine`: `dot`（默认，层次/DAG）或 `neato`（力导）或 `fdp`（力导含 cluster）
- `rankdir`: 主信息流方向。`LR` 左→右（流水线常用），`TB` 上→下（层次常用），`BT` 下→上（端-云-链架构常用）
- `nodesep`: 同层节点间距（英寸，graphviz 单位）
- `ranksep`: 层间距

### `colors`
- `academic`：默认 12 色饱和度配色（在 `tikz-template.tex` 里）
- `drawio`：经典 6 色（在 `tikz-colors.md` 里）

### `zones[]`（可选）
- `members[]`：本 zone 包含的 node id 列表
- `color`：背景色名（blue/green/orange/purple/red/grey）

### `nodes[]`
- `id`：唯一标识，TikZ 里作为 node name
- `label`：显示文字，支持 LaTeX 公式（`$...$`）
- `color`：填充色名
- `size`：
  - `normal`：默认 2.8cm × 0.9cm
  - `hero`：5.6cm × 2.4cm，触发 hero 视觉层次
  - `small`：1.4cm × 0.6cm
- `shape`：默认 `rect`

### `edges[]`
- `style`：
  - `main`：粗橙色实线（主数据流）
  - `control`：黑色实线
  - `feedback`：红色虚线
  - `contrast`：紫色虚线
- `label`：可选标签，挂在线上

## 何时用 B 路 vs A 路

| 你想画 | 路径 |
|---|---|
| 系统架构图 / 协议流程 / 流水线 / DAG / 时序 / 三栏映射 | **B 路**（spec.json + dot-to-tikz） |
| 含嵌入热力图 / 注意力矩阵 / 训练曲线 / 柱状图 | A 路（模板 + vision feedback） |
| 几何/数学示意图 | A 路（模板） |
| Transformer/MHA 等含内部子结构的 hero | A 路（模板 06） |

判断标准：**如果图主体是"框 + 线 + 分组"，B 路；如果框内还要画东西，A 路。**
