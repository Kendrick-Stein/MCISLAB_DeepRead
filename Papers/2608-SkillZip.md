---
title: "SkillZip: Evaluation-Free Skill Compression for Self-Evolving Agents by Discovering Reusable Structure"
authors: [Xiaofan Bai, Hongqiang Lin, Chao Liu, Yantao Zhang, Xuan Jin, Xipeng Cao, Yuhong Li]
institute: [Alibaba Group, Zhejiang University, Duke University]
date_publish: 2026-08-11
venue: arXiv
tags: [task-planning, agentic-RL]
url: "https://arxiv.org/abs/2608.11079"
arxiv_id: "2608.11079"
doi:
cite_key: bai2026skillzip
code:
rating: 4
content_scope: full-text
verification_status: source-checked
date_added: 2026-08-13
---
## Summary

SkillZip 把自进化 agent 不断膨胀的 skill 文本压缩问题形式化为"最短忠实结构解释"：先把 skill 解析成 typed contract（triggers、workflow、tool contracts、scoped rules、output fields），再在 hard coverage constraint 下最小化 typed MDL objective，按 "explain once, reference many" 合并共享结构、按构造保留独有规则。全程 evaluation-free——压缩不接触任务、rollout、reward 或 verifier——平均压缩率 31.2%（evaluation-guided 的 SkillReducer 为 9.2%）且 macro-average score 0.577 略超未压缩的 0.570、开销 3.5× 更低；continual 的 Zip-on-Write 模式把 16 轮自进化的 skill 膨胀从 2.5–3.7× 封顶到约 1.6–1.9×，精度不降。

## Problem & Motivation

自进化 agent 通过追加成功流程和失败修复来积累 skill，同一约束被复述进多个分支、示例与警告，公共动作序列被复制而非复用。论文量化了这一 bloat：SkillOpt 进化 5 轮后 skill 达到初始的约 5.6×/3.1×/6.7×（BFCL-V4 / LiveMath / SpreadsheetBench），平均约 5.2×。

关键论点是 evolved skill 的冗余性质与普通 public skill 不同：经过 rollout 反馈才被接受的更新是 knowledge-dense 的，即使一条只触发过一次的 warning 也可能编码了昂贵的失败教训。因此冗余主要是 repeated representation（同一 invariant 复制进多个分支、workflow 在每次失败后被重述），而非无关内容——压缩目标应从 content filtering 转向 knowledge consolidating。

现有两条路都不合适：generic prompt compression 把 skill 当扁平文本，无视 name/description 决定何时触发、workflow 控制执行、tool/output contract 约束有效性的结构语义；evaluation-guided 压缩（SkillReducer）用生成任务做验证回环，每次压缩需 40–80 rollouts，且把压缩结果耦合到 compression-time eval set——可以反复修好被观测到的分支，却仍丢掉一条未被测到的 guard。由此提出更严的问题：能否只用 skill 内部已有的结构做压缩，完全不观测 tasks、rewards、trajectories、verifiers？

## Method

**Typed contract 解析**。确定性扫描 Markdown 结构后，一次 schema-constrained extraction call 恢复 contract：interface 条目、workflow 节点与边、tool 调用及必需参数、带 modality 与 guard 的 scoped rules、output fields。每个抽取单元必须引用 source block，host 拒绝无支撑引用、极性错配、未知工具名与非法 workflow 引用；解析置信不足的 span 成为 **locked residual**——原样保留、排除删除，保守失败模式是 under-compress 而非静默丢弃。extractor 被刻意不要求做压缩：解释（LLM）与优化（确定性）分离。

**Typed MDL objective（Eq. 4）**。在可复用 contract library K 与 residual R 上最小化 L(K) + L(R|K)，subject to hard coverage constraint：每个 required unit a ∈ A_req(S) 必须被覆盖（a ⪯ (K,R)）。长度模型 L(x) = 渲染 token 数 + γ_def + γ_ref + γ_scope，γ 项惩罚"抽象记号比重复文本更贵"的情况。coverage 是 type-sensitive 的：工具名不覆盖必需参数、general rule 不覆盖冲突的 exception。由此得到 Proposition IV.1（feasible 解保留所有解析出的 requirement）与 Corollary IV.2（**rare-rule preservation**：独有规则的保留不依赖其分支在任何 compression-time 任务分布中出现的频率）。

**四种共享结构**，各有代价阈值不等式：equivalent requirements 合并（Eq. 7）、scope lifting 上提到祖先作用域（Eq. 8）、workflow 片段抽成 shared procedure（Eq. 9）、common core + guarded exceptions（Eq. 10）。

**One-shot 模式（Algorithm 1）**：扫描 → 一次 extraction call → type-compatible reuse proposal → 确定性 min-cost covering → 固定模板渲染 + 可选 structural audit。audit parser 不看原 skill，独立重解析压缩结果并做确定性 diff，发现缺失的 trigger/guard/workflow edge/tool argument/output field 即恢复覆盖它的最短原文 span 并加锁。

**Zip-on-Write 模式（Algorithm 2，Appendix A）**：维护 sidecar `skillzip.json`（当前 contract、来源溯源、scope tree、workflow graph），agent 仍只加载渲染后的 SKILL.md。每个自进化 patch 在同一 objective 下比较四种解释——**ABSORB**（复述既有要求）/ **REFINE**（给既有单元加 guard/参数/校验/exception）/ **EXTEND**（真正的新要求）/ **REFACTOR**（使共享结构变得划算）——取 Eq. 4 增量最小的可行操作；候选检索限制在同类型、当前及祖先 scope、相邻 workflow 节点，复杂度 O(dk) 而非全历史。局部更新可能错过多个 patch 之后才有利可图的复用，故按估计可回收节省超 θ_repack、contract 增长超 ρ 或累计 B 个 patch 触发 periodic global repack（在 compact contract 上操作，不重放历史 prose）。演化器决定学什么，SkillZip 只决定如何表示：任何操作都不因提升任务分数而被接受。

## Key Results

Setup：backbone 为 Qwen3.7-Max / Qwen3.6-Plus / Kimi K2.6，benchmark 为 BFCL-v4 Web Search / LiveMathematicianBench / SpreadsheetBench，evolver 为 SkillOpt；one-shot 统一用 Qwen3.7-max 做 compressor（temperature 0），Zip-on-Write 由各 backbone 自压自己的 skill。baseline：No Skill / Human Skill / Evolved Skill（未压缩）/ SkillReducer。

- **RQ1 膨胀量化**（Fig. 4）：5 轮进化后 skill 达初始 5.6× / 3.1× / 6.7×，平均约 5.2×。
- **RQ2 压缩-保真**（Table I）：SkillZip 压缩率 27.1%（Qwen-3.7-Max）/ 29.7%（Qwen-3.6-Plus）/ 36.9%（Kimi-K2.6），平均 31.2%；macro-average score 0.577 略超未压缩 Evolved Skill 的 0.570。对比 SkillReducer：压缩率 31.2% vs 9.2%（per-model 10.5%/3.6%/13.4%），score 0.577 vs 0.544。Qwen-3.7-Max 上逐 benchmark：SkillZip 0.863/0.472/0.519 vs Evolved 0.869/0.474/0.525。
- **RQ3 压缩开销**（Table II）：SkillZip 全数据集 **0 rollouts**，平均 286 s vs SkillReducer 的对应 1331→207 s（LiveMath）、1082→332 s（Spreadsheet）、587→318 s（BFCL-V4），平均 **3.5× 提速**；SkillReducer 每次压缩另耗 40–80 个 validation rollouts，且因 warm cache 其报告时间是乐观下界。
- **RQ4 跨模型泛化**（Fig. 6）：LiveMath 上压缩 skill 换 backbone 执行的 overall retention 为 **0.97 vs SkillReducer 0.91**，提升主要来自 off-diagonal source–target 对；BFCL-V4 上与 SkillReducer 相当。
- **RQ5 continual 压缩**（Fig. 5）：LiveMath 16 轮自进化，不压缩时 skill 长到 seed 的 2.5×/3.1×/3.7×；第 1 轮起启用 Zip-on-Write 封顶约 1.6×–1.9×（相对未压缩终点减 38%–50%），最终 held-out 精度持平或略超未压缩。第 8 轮才启用则追不回来（Kimi-K2.6 上 2.6× vs 1.9×）——冗余防住比事后清除便宜。

## Evidence Ledger

| Claim ID | Claim | Type | Source locator | Evidence excerpt | Status |
|:--|:--|:--|:--|:--|:--|
| C1 | 5 轮进化后 skill 达初始 5.6×/3.1×/6.7×，平均约 5.2× | number | Sec VI-B (RQ1), Fig. 4 | "the skills reach approximately 5.6×, 3.1×, and 6.7× their initial sizes… average growth of about 5.2×" | source-verified |
| C2 | SkillZip 压缩率 27.1%/29.7%/36.9%（均 31.2%），macro-avg 0.577 vs 未压缩 0.570 | number | Sec VI-C (RQ2), Table I | "compression rates of 27.1%–36.9% (31.2% on average). Its macro-average score is 0.577, slightly exceeding… 0.570" | source-verified |
| C3 | vs SkillReducer：压缩 31.2% vs 9.2%，性能 0.577 vs 0.544 | comparison | Sec VI-C, Table I 后正文 | "both higher compression (31.2% vs. 9.2% on average) and higher task performance (0.577 vs. 0.544)" | source-verified |
| C4 | 0 rollouts、平均 286 s、3.5× 提速；SkillReducer 每次 40–80 rollouts | number | Sec VI-D (RQ3), Table II | "SkillZip requires 286 seconds, corresponding to a 3.5× speedup… 40–80 validation rollouts per compression" | source-verified |
| C5 | LiveMath 跨模型 retention 0.97 vs 0.91，提升主要在 off-diagonal | number | Sec VI-E (RQ4), Fig. 6 | "overall retention of 0.97, compared with 0.91 for SkillReducer… off-diagonal source–target pairs" | source-verified |
| C6 | 16 轮进化膨胀 2.5×/3.1×/3.7×；round-1 启用封顶 1.6×–1.9×（减 38%–50%）无精度损失；round-8 启用仅部分恢复（2.6× vs 1.9×） | number | Sec VI-F (RQ5), Fig. 5 | "capping the skill at roughly 1.6×–1.9×… a 38%–50% reduction… 2.6× vs. 1.9× on Kimi-k2.6" | source-verified |
| C7 | typed MDL objective L(K)+L(R|K) + hard coverage constraint，rare rule 保留与任务频率无关 | causal-mechanism | Sec IV, Eq. 4, Prop. IV.1, Cor. IV.2 | "preservation of a unique requirement does not depend on how often its branch appears in any compression-time task distribution" | source-verified |
| C8 | one-shot 为单次 extraction call + 确定性优化；Zip-on-Write 用 sidecar JSON、四操作 ABSORB/REFINE/EXTEND/REFACTOR、O(dk) 候选、periodic repack | causal-mechanism | Sec V-A/V-B, Alg. 1; Alg. 2 (App. A) | "stores a sidecar, skillzip.json… compares against O(dk) retrieved candidates rather than the complete history" | source-verified |
| C9 | 无公开代码仓库链接；Appendix B 仅给 intended repository 布局与 CLI | license-code | 全文检索 + Appendix B-A | "The intended repository separates parsing, optimization, rendering, and evaluation" | source-verified |
| C10 | 压缩不接触任务/rollout/reward/verifier；one-shot 用固定 compressor Qwen3.7-max，Zip-on-Write 由 backbone 自压 | benchmark-setting | Sec VI-A (Setup) | "a single fixed compressor model (Qwen3.7-max) across all skills, whereas for continual Zip-on-Write the agent's backbone model compresses its own skill" | source-verified |

## Strengths & Weaknesses

**亮点**

- **问题选得准**：skill bloat 是自进化 agent 的真实运维痛点（5.2× 平均膨胀是论文自己量化的），而"低频 exception 不能按频率删"这一失效模式直击 evaluation-guided 压缩的结构性盲区——后者只能修被 eval set 覆盖到的分支。
- **形式化干净**：一个 typed MDL objective 统一了规则合并、scope 上提、workflow 复用、exception 编码四种压缩形态，hard coverage 给出 by-construction 的 rare-rule preservation（Cor. IV.2），符合 simple & principled 的品味。
- **工程纪律好**：解释与优化分离（LLM 只提结构、host 确定性校验与落盘）、locked residual 的保守回退、audit 独立重解析——失败模式被刻意设计成 under-compress 而非 silent deletion。
- **报告诚实**：明说 SkillReducer 的目标 regime 是 public skill debloating 而非 evolved skill、SkillReducer 计时因 warm cache 是乐观下界、preservation guarantee 是 parser-relative 的。

**局限**

- **保证是 parser-relative 的**：Prop. IV.1 只保护被 extraction 解析进 contract 的 requirement，parser 漏掉的语义 coverage 无从覆盖（附录明示"does not establish that arbitrary natural language has been interpreted perfectly"）。整条 pipeline 的真实风险从 optimizer 转移到了 structural parser，而 parser 召回质量在主文没有直接评测。
- **对照不对称**：31.2% vs 9.2% 的压缩差距部分来自 regime 错配（SkillReducer 被用在其不擅长的 evolved skill 上），不能读成通用意义上的方法碾压。
- **评测面窄**：单一 evolver（SkillOpt）、3 个 benchmark、两个模型家族；主文无 component ablation（如去掉 typed matching 或 hard coverage 的对照），"哪个设计贡献了多少"未知。
- **无公开代码**：附录给了详细 intended repository 与 CLI，但全文无仓库链接，"evaluation-free claim 可从文件访问与日志审计"目前停留在纸面。
- （推测）hard coverage 约束下可压缩空间天然有上限——31.2% 相对 5.2× 的膨胀只回收了部分冗余；剩余部分是真知识还是 parser 不敢动的 locked residual，论文未拆分。

## Mind Map

```mermaid
mindmap
  root((SkillZip))
    Problem
      Skill bloat 5.2x by round 5
      Evolved skill 冗余是 repeated representation
      Evaluation-guided 压缩耦合 eval set
    Method
      Typed contract 解析 + locked residual
      Typed MDL: min L(K)+L(R|K)
      Hard coverage → rare-rule preservation
      四种共享结构 Eq.7-10
      One-shot: 1 次 extraction + 确定性优化
      Zip-on-Write: ABSORB/REFINE/EXTEND/REFACTOR + repack
    Results
      压缩 31.2% vs 9.2%, score 0.577 vs 0.544
      0 rollouts, 3.5x 提速
      跨模型 retention 0.97 vs 0.91
      16 轮膨胀 2.5-3.7x → 1.6-1.9x 无精度损失
```

## Notes

- 本文的 evolver 即 [[2605-SkillOpt]]（arXiv 2605.23904，同一工作）；Fig. 4 的膨胀曲线还覆盖了 Memento-Skills。主要 baseline SkillReducer（arXiv 2603.29919, "optimizing LLM agent skills for token efficiency"）vault 尚无笔记，要深挖 evaluation-guided vs evaluation-free 这条对比线可补一篇。
- "Compression as a skill" 的打包方式——model 只提议结构化操作、deterministic host 校验 schema/重算 saving/写事务日志/渲染成功才原子替换——对本 vault 的 skill 系统维护（SKILL.md 自身的膨胀治理）有直接可借鉴性。
- 疑问：Zip-on-Write 中 backbone 自压自己的 skill，contract 抽取质量是否随 backbone 能力波动？RQ5 只报长度因子与最终精度，没报 per-model 的 contract 召回质量。
- 疑问：θ_repack、ρ、B 等 repack 触发超参如何设定、敏感性如何，主文未见分析。
