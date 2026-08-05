---
name: writing-refine
description: >
  当 Supervisor 说"打磨一下""改改这段""逻辑不通顺""说人话"，
  或 autoresearch 在写作阶段自检时，
  从结构/清晰度/论据/机器味四个维度打磨已有文稿
argument-hint: "<target> [section] [focus]"
allowed-tools: Read, Edit, Glob, Grep
---

## Purpose

对已有文稿进行结构化打磨，从四个维度审视并生成具体修改建议：

- **structure**：逻辑链是否完整、段落过渡是否自然、论证顺序是否最优
- **clarity**：冗余表达、歧义措辞、过度抽象的概念是否需要具体化
- **evidence**：每个关键 claim 是否有 `[[wikilink]]` 支撑，引用是否恰当
- **ai-tells**：句子级的机器味——套话、假人味语气、模糊归属、增量锚定

默认行为：输出建议列表，由 Supervisor 确认后再执行修改。

---

## Steps

### Step 1 — 读取目标内容

读取 `target` 文件。如果指定了 `section`，定位到对应章节（通过标题匹配）。

```
Read(target)
# 若 section 非空，截取对应章节文本
```

记录文稿的基本信息：总字数（估算）、章节数、已有 `[[wikilink]]` 数量。

### Step 2 — 按维度审视

根据 `focus` 参数决定审视范围：

| focus 值 | 执行维度 |
|----------|----------|
| `structure` | 仅审视逻辑链与过渡 |
| `clarity` | 仅审视冗余/歧义/抽象 |
| `evidence` | 仅审视 claim-citation 匹配 |
| `ai-tells` | 仅审视机器味 |
| `all`（默认） | 四个维度全部审视 |

**structure 审视要点：**
- 段落首句是否清晰表达段落主旨？
- 段落间过渡是否有逻辑连词或过渡句？
- 论证路径是否遵循"问题 → 现有方法 → 不足 → 本文方案"？
- 是否存在论点跳跃（缺少中间推导步骤）？

**clarity 审视要点：**
- 是否有重复表达同一意思的冗余句子？
- 是否有模糊词（"一些"、"某种程度上"、"相关工作"）未加具体化？
- 是否有过长的从句可以拆分？
- 专业术语首次出现是否有解释？

**evidence 审视要点：**
- 每个"XX 方法表现更好/更差"等比较性 claim 是否有 `[[paper]]` 引用？
- 每个背景陈述（"现有方法普遍存在 X 问题"）是否有文献支撑？
- 已有 `[[wikilink]]` 是否指向实际存在的笔记（可用 Glob 验证）？
- 是否有孤立 claim（无任何引用支撑）？

**ai-tells 审视要点：**

先 `Read("references/writing-style.md")`，按其 §A 的四组逐条比对：

- **A1 内容层**：模糊归属（"研究者普遍认为"）、意义膨胀（"标志着重要里程碑"）、表层 -ing 分析、空泛结语、知识截止免责、机构堆砌
- **A2 语言层**：AI 高频词、否定式排比、三项凑数、同义词轮换（同一术语换词指代）、伪范围、行内标题式列表、连用破折号
- **A3 语气层**：导览铺垫、口语式反问开头、权威腔、制造金句、格言体、标题后复读、对话残留、emoji
- **A4 版本层**：增量锚定（"本节新增"/"本轮并入"——只属于调研日志，不入正文）

两条反向约束，比对时不可违反：

- **hedge 不删**（§B）。要改的只是不落地的 hedge——判据是它后面跟不跟得上一个条件、一个数字或一个具体检验方式。跟得上就保留原样。
- **不新增信息**。改写只能重排与删减；具体性必须来自原文，不能由改写发明事实、数字、日期或引用。做不到就只提"删"的建议。

逐条比对之后另做一次整体通读，判断全篇语气是否仍像自动生成——局部检查抓不到通篇的腔调问题。

### Step 3 — 生成修改建议列表

以结构化列表输出，每条建议包含：

```
[维度] 位置（行号或段落标识）
问题描述：……
建议：……
```

示例格式：

```
[evidence] 第 3 段，第 2 句
问题描述：claim "端到端方法在导航成功率上显著优于模块化方法" 无引用支撑
建议：添加 [[CMA-R2R]] 或 [[DUET]] 作为 evidence，或将断言改为引用具体论文的归因句

[clarity] 第 5 段，第 1 句
问题描述："相关工作在这方面有所探索" 表述模糊
建议：具体化为 "[[VLNBERT]] 和 [[HAMT]] 分别从 X/Y 角度探索了这一问题"

[structure] 第 2 段 → 第 3 段 过渡
问题描述：从"数据增强"直接跳到"模型架构"，缺少过渡说明两者关系
建议：添加一句过渡："数据层面的增强有其上限；本节转而从模型架构角度寻求突破。"

[ai-tells] 第 4 段，第 1 句（A1 模糊归属 + A4 增量锚定）
问题描述："本轮并入的研究普遍认为验证 gate 是收益来源" —— "普遍认为" 无归属，"本轮并入" 是内部记账
建议：改为 "[[2605-GRASP]] 报告移除 gate 后 88.8%→63.5%，而 [[2607-HarnessBank]] 的同类消融为 ±0.0"

[ai-tells] 第 6 段，末句（A3 格言体）
问题描述："评测即共识" 是格言而非论断，无法证伪
建议：换成实际主张 "不同接口范式在同一批 case 上不可比，除非做 matched 对照"
```

在列表末尾附上**摘要统计**：

```
总建议数：N
- structure: X 条
- clarity: Y 条
- evidence: Z 条
- ai-tells: W 条
```

### Step 4 — Copilot 确认流程

**默认行为**：输出建议列表后，等待 Supervisor 确认。不主动执行 Edit。

询问 Supervisor：
> "以上 N 条修改建议，请确认哪些执行？可回复：全部执行 / 执行 #1 #3 #5 / 跳过全部"

收到确认后，逐条使用 `Edit` 执行。每次 Edit 后在建议前标记 `[✓]`。

### Step 5 — 追加日志

在 `Workbench/logs/YYYY-MM-DD.md`（用实际日期替换）追加：

```markdown
## writing-refine — HH:MM

- target: [[relative/path/to/file]]
- section: <指定章节 或 "全文">
- focus: <structure / clarity / evidence / ai-tells / all>
- 建议总数: N（structure: X, clarity: Y, evidence: Z, ai-tells: W）
- 执行: <已确认执行的条目序号，或 "待 Supervisor 确认">
```

---

## Verify

执行完成后确认以下五点：

1. **无新 [TODO] 占位符**：Edit 引入的文本中不含 `[TODO]`、`[待补充]` 等占位符。
2. **[[wikilink]] 仍有效**：被修改段落中的所有 `[[wikilink]]` 仍指向实际存在的文件（用 Glob 抽查）。
3. **未引入新信息**：改后文本中的每个事实、数字、日期、引用都能在改前文本里找到对应；新出现的一律回退。
4. **限定词未被吃掉**：改前带范围/条件限定的 claim（"尚未见独立验证"、"在当前检索范围内"、"仅在 X 条件下"），改后限定仍在。
5. **日志已追加**：`Workbench/logs/YYYY-MM-DD.md` 包含本次操作记录。

---

## Guard

- **默认先确认再修改**：不经 Supervisor 确认不执行 Edit。
- **不改变核心论点**：只调整表达和结构，不替换或删除作者的核心主张。
- **不新增信息**：打磨只能重排与删减。任何新增的事实、数字、日期、引用都属越界——具体性必须来自原文或 Supervisor，不能由改写发明。做不到具体化时只提"删"的建议。
- **不删 hedge**：`尚未见独立验证`、`在当前检索范围内`、`原文一致性已核查而非独立复现` 这类限定是 claim 的真实认知状态，不是含糊措辞。ai-tells 维度只处理**不落地的 hedge**（后面跟不上条件/数字/具体检验方式的），处理方式是补上落点或删掉整个 claim，不是软化后保留。详见 `references/writing-style.md` §B。
- **不增删章节**：不新增标题层级，不删除现有段落（除非 Supervisor 明确指示）。
- **语言规范**：遵循文稿原有语言风格（中英混用 / 纯英文 / 纯中文），不擅自切换。
- **范围限定**：若指定了 `section`，只在该章节内给出建议，不扩散到全文。

---

## Examples

### Example 1 — 打磨 Related Work 章节（focus: evidence）

**触发**：

> "帮我看看 Related Work 那节，感觉 claim 都没有引用"

**Researcher 执行流程**：

```
Read(".claude/skills/4-writing/writing-refine/SKILL.md")  # 重新读取 SKILL
Read("Papers/drafts/survey-draft.md")                      # Step 1
# section = "Related Work", focus = "evidence"
```

**输出示例**：

```
[evidence] Related Work § 1，第 3 句
问题描述："早期 VLN 方法依赖 LSTM 编码指令" 无引用
建议：添加 [[Speaker-Follower]] 或 [[R2R-EnvDrop]] 作为代表性早期方法引用

[evidence] Related Work § 2，第 1 句
问题描述："基于 Transformer 的方法大幅提升了成功率" 属于泛化陈述，无数据支撑
建议：具体化为 "[[DUET]] 在 R2R val-unseen 上达到 60.6% SR，较 LSTM 基线提升约 15%"

[evidence] Related Work § 3，第 4 句
问题描述：[[VLN-BERT]] 已引用，但 [[HAMT]] 同样相关，建议补充对比
建议：添加 "[[HAMT]] 进一步引入历史感知机制，在长指令场景下表现更优"

总建议数：3
- structure: 0 条
- clarity: 0 条
- evidence: 3 条
```

**Researcher 等待 Supervisor 确认后，逐条执行 Edit。**
