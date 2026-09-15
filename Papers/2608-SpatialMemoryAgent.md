---
title: "Spatial Memory Agent: Experience-Grounded Procedure Memory for Spatial Intelligence"
authors: ["Haokai Zhang", "Yuhang Ding", "Yunshu Zhou", "Xinze Du", "Shengtao Zhang", "Zhiyue Zhao", "Yuling Xi", "Hao Chen"]
institute: ["Zhejiang University", "Shanghai Jiao Tong University", "Shanghai Innovation Institute"]
date_publish: 2026-08-13
venue: arXiv
tags: [spatial-reasoning, VLM, agentic-RL]
url: "https://arxiv.org/abs/2608.12743"
arxiv_id: "2608.12743"
doi: ""
cite_key: zhang2026spatial
code: ""
rating: 3
content_scope: full-text
verification_status: source-checked
date_added: "2026-08-18"
---
## Summary

SMA 做冻结 VLM 的 parameter-update-free 空间推理自演化：在带 ground-truth verifier 的 environment split 上把每次 rollout 反思成一条 transferable lesson 写入 memory bank，为每条 lesson 维护一个由后续检索结果校准的 Transfer Reliability Score (TRS)，deployment 阶段用 semantic filter + (相似度, TRS) 组合排序检索 top-3 注入 prompt。5 benchmark × 4 base VLM 的主表上 SMA 每个 base-model block 的 macro average 最高（较最强非 SMA baseline +1.7~+2.9pp）。但主表每个 SMA 数字取自 10 次 pass 的 best checkpoint、而论文未声明 baseline 享有同等选择规则，且附录两个更大的 benchmark 上 MemRL-GT 在 ViewSpatial 反超。

## Problem & Motivation

提升 VLM 空间推理目前有两条主线：一是 post-training（SFT / RL，如 SpatialVLM、RoboSpatial），二是 agentic tool use（推理时调 depth estimation、3D reconstruction 等专家工具，如 S-Agent、SpaceTools）。作者提出第三条：冻结权重、推理时也不依赖外部空间工具，只靠一个外部 memory bank 自我改进。

这个 problem formulation 本身是清楚的，但它的适用条件被论文轻描淡写了：SMA 并非"零监督"，它需要一个**带 verified ground-truth answer 与 verifier reward 的 environment split**，而该 split 就是目标 benchmark 的另一半（per-category 50/50，seed 42）。也就是说它省掉的是"梯度更新"，没省掉"同分布标注数据"。与 post-training 相比，真正的对比轴是"用同样的标注数据，是写进权重还是写进外部文本"，而不是"有监督 vs 无监督"。论文没有把这条轴讲透。

## Method

**记忆卡片**：`m_i = (t_i, s_i, l_i, n_i, c_i, v_i)`——源任务、rollout summary、transferable lesson、访问计数、累计 reward、TRS。检索时只暴露 task / summary / lesson 三个字段，不暴露历史预测与 verified answer。

**1) Procedure Memory Generation**。反思模型 `R_φ` 拿到原始输出 `o_i`、任务 `t_i`、**verified target `y*_i`** 与 reward `r_i`，输出严格 JSON 两字段：summary 抽象任务形态与成败模式，lesson 是"pattern + 要避的坑 + 要做的检查"三件套的可复用原则；有 anti-leakage 规则禁止复述答案。与只给 reward 的变体（MemRL-R）的区别就在于是否给 `y*`。

**2) Two-Stage Retrieval**。一阶段 semantic filter：`rel_ij = cos(ψ(t_i), ψ(t_j))`，`C_i = {m_j : rel_ij ≥ δ}`（ψ 用 text-embedding-3-large，δ 逐 benchmark 调 0.488–0.618）。二阶段 combined ranking：`S_ij = (1−η)·z(rel_ij) + η·z(v_j)`，z 为 clipped z-score，取 top-k=3 组成 guidance set 前置进 prompt。

**3) Visit-Evidence Calibration**。初始化 `n←0, c←0, v←v_0=0.5`——**不因源 rollout 的对错给不同初值**（Appendix B.1 把 uniform initialization 列为显式设计要求）。每当 `m_j` 进入 guidance set 且该题得 reward `r_i ∈ [0,1]`：

```
n_j ← n_j + 1,  c_j ← c_j + r_i,  v_j ← (λ·v_0 + c_j) / (λ + n_j)
```

等价于 `v = λ/(λ+n)·v_0 + n/(λ+n)·(c/n)`，即先验（λ=2 相当于两次虚拟访问、一胜一负）与经验访问成功率的凸组合，`n/(λ+n)` 是 confidence 项。这个估计量是 order-invariant 的（同样的 n 与 c 得同样的值），并对低访问量做收缩。

**4) One-Pass Memory Writing（默认）**。只在第 0 遍 environment split 写卡（每题一张），后续 pass 复用固定 bank、只更新 TRS。Deployment 阶段 bank 完全冻结：不写新卡，`n / c / v` 即使被检索也不更新。

## Key Results

**主表（Table 1，5 benchmark × 4 frozen VLM）**。SMA 的 macro average 在每个 base-model block 最高：Qwen3.5-122B-A10B 68.8、Qwen3.6-35B-A3B 66.7、Qwen3.6-27B 69.8、Qwen3.5-9B 63.5，较最强非 SMA baseline 分别 +2.6 / +2.9 / +1.7 / +2.8。逐格核对 20 个 (model, benchmark) 单元：SMA 严格最优 18 格，与 MemRL-GT 打平 1 格（27B 的 SAT，同为 87.0），落后 1 格（Qwen3.5-9B 的 ERQA，MemP 53.0 > SMA 52.0）。

> 口径边界：主表每个 SMA 数字是**10 次 pass 评测中的 best checkpoint**，论文原文把这条选择规则限定为"applied to all SMA rows"；verifier 通读 §4.1.3 与 Appendix C.4.1–C.4.5、C.6 后确认，全文没有任何一处说明 baseline 也做了同等的 best-of-10 选择，baseline 描述中不含多 pass 评测。Appendix C.6 逐格给出的 Pass 值在 2–10 之间无规律跳动（Qwen3.6-27B 为 3 / 9 / 2 / 10 / 6；122B 为 6 / 2 / 10 / 9 / 4），且所有结果都测在 deployment split 上。因此上述 margin 不是 selection-matched 的，下文所有"提升"均需带这一限定读。

**消融（Table 2 / Table 8，Qwen3.6-27B）**。RoboSpatial：SMA 68.5；−summary 65.3（−3.2）、−transferable lesson 65.0（−3.5）、−semantic filter 62.7（−5.8）、+model output 64.1（−4.4）、reward-only reflection 63.0（−5.5）。Omni3D：SMA 47.6；对应 −1.6 / −5.2 / **−7.2** / −2.0 / −2.8。两个 benchmark 一致把 **semantic filter** 排在最大贡献项——即"先按相似度筛掉不相关卡片"比 TRS 本身更关键；而 TRS 权重 η 的消融只以 sensitivity sweep（峰值 η=0.5、k=3）的形式出现，**没有 η=0 的对照行**，所以"TRS 相对纯相似度的净贡献"在消融表里是缺失的。

**TRS 有效性诊断**。按检索卡片的 mean TRS 分箱，deployment accuracy 从 [0.2,0.3) 的 19.3% 升到 [0.9,1.0] 的 97.3%——论文自己注明该 pooled trend 可能同时反映 benchmark 难度与题型构成差异。按源题成败分层（Table 5）：成功源卡片 mean TRS 0.522 / 下游 accuracy 85.7%，失败源 0.452 / 61.4%（差 24.3pp）。按单题三张检索卡的成败构成（Table 6）：all-success N=13,226 / 93.0% / TRS 0.909，mixed N=10,264 / 65.1% / 0.653，all-failure N=603 / 39.0% / 0.480。

**相似度—准确率解耦（§4.6.2）**。相对 MemP，SMA 把检索卡片的 macro 平均相似度从 0.792 **降到** 0.698，同时 macro accuracy 从 66.8% 升到 69.8%，每个 benchmark 方向一致。这是全文最有信息量的一条：说明"最近邻不等于最有用"。

**迁移（Table 4）**。模型迁移 122B→27B：RoboSpatial 54.1→63.5（+9.4）、SAT 82.3→88.0（+5.7）。benchmark 迁移（27B）：ERQA→RoboSpatial 54.1→61.7（+7.6）、Omni3D→EmbSpatial 85.7→87.2（+1.5）。

**原子能力（§4.6.4）**。四模型平均、RoboSpatial/ERQA/SAT/EmbSpatial 口径下 SMA 十项全正：Correspondence +11.2pp、Attribute +8.0、Object motion +7.6，最低的 Distance/depth +2.6、Affordance +2.9；对照组 MemP 在 Tracking −3.0、Affordance −1.9 为负。

**与 training-based 方法比较（Table 3）**。SMA（Qwen3.5-9B）63.5 vs SpatialEvo-7B 47.1，Δ=+16.4，逐 benchmark 全面领先。

> 口径边界：这是跨 backbone 世代的比较。同一 Qwen3.5-9B 在 **no-memory** 下的 macro 已经是 60.6（Table 1）。论文正文只给 47.1→63.5，没有做这个分解。

**附录两个 benchmark（Table 7，SITE-image / ViewSpatial）**。SMA 不再全面领先：Qwen3.5-122B-A10B 的 ViewSpatial 上 MemRL-GT 62.8 > SMA 59.7，该 block 两 benchmark 平均 MemRL-GT 66.9 > SMA 65.6；Qwen3.6-27B 的 ViewSpatial 上 MemRL-GT 64.3 > SMA 63.2。8 格记录为严格最优 5、打平 1（122B 的 SITE 与 MemP 同为 71.4）、落后 2。合并 28 格则为 23 胜 / 2 平 / 3 负。值得注意的是这两个被放进附录的 benchmark 恰是 deployment split 最大的两个（2224 与 2856），而主表五个中有三个只有 175 / 200 / 250 题；Appendix C.6 也**未给出**它们的 δ 与 Pass 值。

**协议开销**。全文无任何 token / latency / 推理开销核算（verifier 全文确认："latency" 仅在 Appendix D.2 作为 future work 出现，"token" 仅出现在 max 32768 new tokens）；One-Pass vs Continual 的比较也只覆盖 bank 大小、冗余度（One-Pass 少 21%）与 TRS-update 覆盖率（约 2 倍），**没有任何 accuracy 对照**。

## Evidence Ledger

| Claim ID | Claim | Type | Source locator | Evidence excerpt | Status |
|:--|:--|:--|:--|:--|:--|
| C1 | macro avg 68.8 / 66.7 / 69.8 / 63.5，较最强非 SMA baseline +2.6 / +2.9 / +1.7 / +2.8 | number | §4.2, Table 1 | "68.8 on Qwen3.5-122B-A10B... the average gains are 2.6, 2.9, 1.7, and 2.8 points" | source-verified |
| C2 | 20 格中 SMA 严格最优 18、打平 1（27B SAT）、落后 1（9B ERQA，MemP 53.0 > 52.0） | comparison | Table 1（逐格核对） | "MemP \| 53.7 \| 53.0 \| 34.4 \| 78.0 \| 84.2 \| 60.7" vs "SMA \| 58.5 \| 52.0 ..." | source-verified |
| C3 | 主表 SMA 数字为 10-pass best checkpoint；全文无 baseline 同等选择规则的陈述 | benchmark-setting | §4.1.2 + Table 1 caption + App C.4/C.6 | "SMA reports the best checkpoint from the 10-pass evaluation... applied to all SMA rows" | source-verified |
| C4 | 每格 Pass 值不同（27B: 3/9/2/10/6；122B: 6/2/10/9/4）；λ=2.0, v0=0.5, K=3, η=0.5 全局固定，δ 逐 benchmark 0.488–0.618 | number | App C.6, Table 28 / Table 30 | "Pass \| 3 \| 9 \| 2 \| 10 \| 6" | source-verified |
| C5 | Table 3：SMA(Qwen3.5-9B) 63.5 vs SpatialEvo-7B 47.1（Δ+16.4）；同一 base 的 no-memory 已 60.6 | comparison | §4.4 Table 3 + Table 1 | "SMA improves the average from 47.1 to 63.5 (Δ=+16.4)"；"No memory ... 60.6" | source-verified |
| C6 | RoboSpatial 消融 −3.2/−3.5/−5.8/−4.4/−5.5；Omni3D −1.6/−5.2/−7.2/−2.0/−2.8 | number | Table 2 / Table 8 | "62.7 −5.8"；"40.4 −7.2" | source-verified |
| C7 | TRS 分箱 accuracy 19.3%→97.3%，论文自承 pooled trend 受 benchmark 难度混淆 | causal-mechanism | §4.6.1 | "Accuracy rises from 19.3%... to 97.3%... may also reflect differences in benchmark difficulty" | source-verified |
| C8 | 成功源卡 TRS 0.522/85.7% vs 失败源 0.452/61.4%；构成分层 13,226/93.0%、10,264/65.1%、603/39.0% | number | Table 5, Table 6 | "Success \| 0.522 \| 85.7%"；"All failure \| 603 \| 39.0% \| 0.480" | source-verified |
| C9 | 相对 MemP，检索相似度 0.792→0.698 而 macro accuracy 66.8%→69.8% | number | §4.6.2 | "reduces macro-average similarity from 0.792 to 0.698 while raising macro accuracy from 66.8% to 69.8%" | source-verified |
| C10 | 迁移：122B→27B RoboSpatial +9.4、SAT +5.7；ERQA→RoboSpatial +7.6；Omni3D→EmbSpatial +1.5 | number | Table 4 | "RoboSpatial \| 54.1 \| 63.5 \| +9.4" | source-verified |
| C11 | Table 7 上 MemRL-GT 在 ViewSpatial 反超（122B 62.8>59.7；27B 64.3>63.2），122B 两 benchmark 均值 66.9>65.6 | comparison | App A.1, Table 7 | "MemRL-GT \| 70.9 \| 62.8 \| 66.9 \| SMA (ours) \| 71.4 \| 59.7 \| 65.6" | source-verified |
| C12 | env/deployment 为同 benchmark 的 50/50 disjoint 划分；写记忆需 verified `y*` 与 verifier reward；deployment 不写卡也不更新 n/c/v | benchmark-setting | §3.1, §3.3, §4.1.1, Table 27 | "Deployment does not write new memories and does not update any memory-value state" | source-verified |
| C13 | 4 个 frozen base VLM 经 vLLM 服务，同一模型兼任 solver 与 reflection model；temperature=0、top-p=1、max 32768 tokens、text-embedding-3-large | benchmark-setting | §4.1.2 | "All runs use temperature=0, top-p=1, a maximum of 32768 new tokens, and precomputed task embeddings" | source-verified |
| C14 | One-Pass 相对 Continual：记忆量 1/10、冗余低 21%、TRS-update 覆盖率约 2 倍；**无 accuracy 对照** | number | §4.6.3 | "uses only one-tenth as many memories, exhibits 21% less redundancy... roughly twice the TRS-update coverage" | source-verified |
| C15 | 原子能力增益 Correspondence +11.2 / Attribute +8.0 / Object motion +7.6 / Distance-depth +2.6 / Affordance +2.9；MemP 在 Tracking −3.0、Affordance −1.9 | number | §4.6.4 | "MemP has negative gains on Tracking (-3.0 pp) and Affordance (-1.9 pp)" | source-verified |
| C16 | 无公开代码仓库；仅 project page https://aim-uofa.github.io/SMA/ 且标注 "Code Coming Soon"；license 为 arXiv perpetual non-exclusive | license-code | 标题脚注 + arXiv abs + project page | "Project page: https://aim-uofa.github.io/SMA/"；project page: "Code Coming Soon" | source-verified |
| C17 | TRS 更新式 `v_j ← (λv_0+c_j)/(λ+n_j)`，检索式 `S_ij=(1−η)z(rel_ij)+η z(v_j)`，语义筛 `rel_ij ≥ δ` | causal-mechanism | §3.2.3, §3.2.4, App B.1/B.2 | "v_j ← (λv_0+c_j)/(λ+n_j)"；"S_ij=(1−η)z(rel_ij)+η z(v_j)" | source-verified |
| C18 | 自承局限：credit assignment 无法区分写入/反思/检索/过滤/使用；无 memory lifecycle（delete/merge/compress/expire）；全文无 token/latency/开销核算 | causal-mechanism | App D.1, D.2（全文检索） | "cannot precisely determine whether the outcome should be attributed to memory writing, reflection, retrieval..." | source-verified |

**本笔记自行推算（非论文陈述，输入数字均来自上表已核实条目）**：

- Table 3 的 +16.4 分解：同一 Qwen3.5-9B 的 no-memory macro 为 60.6，SpatialEvo-7B 为 47.1，故 16.4 中约 13.5 来自 backbone 世代差（Qwen2.5-VL-7B → Qwen3.5-9B），memory 机制自身贡献 60.6→63.5 即 +2.9。论文正文未做此分解。
- Qwen3.6-27B block 的 +1.7pp 折算成题数：对 MemRL-GT 的逐列差为 RoboSpatial +1.3pp、ERQA +2.5pp、Omni3D +4.0pp、SAT 0、EmbSpatial +0.7pp，按各自 deployment 规模（175/200/250/300/1820）约合 2 / 5 / 10 / 0 / 13 题，共约 30 题；其中 ERQA + Omni3D 两个 ~200 题的小 split 贡献了 15 题。在 best-of-10-pass 选择、且无多 seed / 置信区间的前提下，这个量级的领先不足以排除选择噪声。
- RoboSpatial 列的数值与 175 题的单题粒度对不上（54.1% → 94.68 题；65.5% → 114.6 题；68.5% → 119.9 题，均非整数，邻近整数题数四舍五入后也不等于报告值），推测该列用了 per-category macro 或 pointing 子集的部分得分口径，论文未说明。

## Strengths & Weaknesses

**值得学的地方。** §4.6.2 是全文最扎实的一段：用"检索相似度下降 0.094 而准确率上升 3.0pp"这一组配对测量，把"最近邻检索是最优检索"这条 convention 直接证伪，且方向在每个 benchmark 上一致。这比主表的 macro average 更有信息量，因为它测的是机制而非分数。Table 5/6 的源题成败分层同样是好设计——它让"记忆质量从哪来"变成可观测量。诊断的密度（TRS 分箱、源结果分层、检索构成分层、原子能力分解、跨模型/跨 benchmark 迁移）明显高于同类 memory 论文的平均水平。Appendix B.1 对估计量的五条设计要求（uniform init / visit-evidence / order invariance / low-visit conservatism / evidence-driven convergence）写得清楚，是可以直接复用的规格。E.2 的失败案例分类也诚实：把 benchmark-side ambiguity 与 base-model grounding 失败分开，并指出三个 TRS≥0.6 的高质量记忆仍无法纠正 movement direction / object count / connectivity 的误读——"memory 能引导推理过程但替代不了准确的视觉 grounding"。

**主要问题。** 第一也是最重的一条：**主表的比较不是 selection-matched**。SMA 的每个数字取 10 次 pass 的最优，baseline 没有对应机制，Appendix C.6 逐格 Pass 值在 2–10 间无规律跳动正是 max 操作的形态。而所报 margin 折算成题数只有几十题（27B block 约 30 题，其中 15 题落在两个 ~200 题的 split 上），温度为 0 意味着单次确定性运行、无多 seed 与置信区间。在这个信噪比下，"SMA 每个 block 都最优"这个结论的稳健性是未知的，不是已知的。

第二，**方法的算法增量比论文呈现的要小**。检索式与 MemRL 在函数形式上一致（阈值预筛 + 相似度/价值的 z-score 加权和，权重同取 0.5），真正换掉的只是价值更新式——把 order-dependent 的 EMA 换成 order-invariant 的收缩均值。这是个合理的改进（Appendix B.1 论证得也好），但把它叫作"a practical parameter-update-free path for spatial self-evolution"的核心贡献，与 MemRL-GT 这个 baseline 在多数格子上只差 1–3pp 的事实是相称的——换言之贡献主要是"把已有的 selection 侧演化范式移植到多模态空间域并验证其可行"，这比"新机制"要弱。

第三，**Table 3 的 training-free vs training-based 比较在当前呈现下会被误读**。跨了一整代 backbone，而同 backbone 的 no-memory 基线（60.6）就已经比 SpatialEvo-7B（47.1）高 13.5。论文正文的措辞（"can be competitive... under this evaluation scope"）是有保留的，但表格没有把这个保留可视化。

第四，**benchmark 选择存在明显的呈现偏斜**。SITE-image 与 ViewSpatial 是 deployment split 最大的两个（2224 / 2856），却被放进附录，而恰恰在这两个上 MemRL-GT 于 ViewSpatial 两次反超、并拿下 122B block 的两 benchmark 均值。附录也没给这两个 benchmark 的 δ 与 Pass。这不构成造假（abstract 的 "20 evaluations" 确实限定在主表五个），但 5 个主表 benchmark 恰好是 SMA 全胜的那 5 个，读者需要自己去附录才看得到另一半。

第五，**消融缺关键一格**。两张消融表都把 semantic filter 排在最大贡献项（−5.8 / −7.2），而 TRS 本身没有 η=0 的对照行——只有 sensitivity sweep 的峰值。于是"TRS 相对纯相似度检索的净增益"在实验里是缺的，而这正是全文的中心主张。MemP 作为"相似度-only 的 procedural memory"是最接近的替身，但它同时少了 verifier-guided reflection 里的 ground-truth 信号，两个变量没分离。

第六，**bundle-level 归因未被检验**。k=3 的 guidance set 里三张卡片共吃同一个 `r_i`，这正是 credit assignment 最脆弱的形式；论文在 D.1 承认了这一点，但没有做任何受控探针（例如注入无效记忆看它们能吃到多少正向更新）。同理，§4.6.3 只报了 TRS-update 覆盖率的**相对**倍数，从未给出"最终有多少比例的卡片仍停在 v0=0.5"的绝对数——而这恰是判断 TRS 到底覆盖了多少 bank 的关键量。

第七，**成本完全未记账**。每题 prepend 3 张卡片、外加 environment 阶段每题一次反思调用，全文无 token / latency / 调用量数字。在 memory 类工作已被系统性质疑"收益来自预算不对称"的背景下，这是个不该省的对照。

第八，一个更根本的边界：SMA 的 uniform initialization 是**主动丢弃**了一个它自己测出来很强的先验——Table 5 显示成功源卡片的下游准确率高 24.3pp。Appendix B.1 的辩护（"正确的 rollout 也可能产出过于具体的 lesson"）在概念上成立，但既然数据方向如此明确，"按源结果设不同 v0"至少应该是一个消融项。

**影响判断（推测）。** 这篇更可能作为"selection 侧记忆演化可以推广到多模态空间任务"的一个存在性证据被引用，而不是作为方法基线被沿用——因为核心机制与 MemRL 高度重合、代码未放出、且主表口径无法直接复现比较。§4.6.2 的相似度—准确率解耦结论有独立价值，值得单独引。

## Connections

- [[Papers/2601-MemRL]] —— 同构程度极高，且作者列里有 MemRL 一作 Shengtao Zhang，论文亦把 MemRL 当 baseline（MemRL-R / MemRL-GT）。检索式几乎逐项对应：MemRL 的 `(1−λ)·sim̂ + λ·Q̂` + δ 阈值预筛 + z-score 归一化 vs SMA 的 `(1−η)·z(rel) + η·z(v)` + `rel ≥ δ`，权重都取 0.5，δ 都逐 benchmark 调（MemRL 0.25–0.62 / SMA 0.488–0.618），检索深度都是 3–5。真正的差异只在价值更新式：MemRL 是 α=0.3 的 Monte Carlo 增量 `Q←Q+α(r−Q)`（order-dependent），SMA 换成 λ=2、v0=0.5 的收缩均值（order-invariant）。连诊断都同构——MemRL 的 Q 分箱成功率 21.5%→88.1%（Pearson r=0.861），SMA 的 TRS 分箱 19.3%→97.3%。因此 SMA 的定位应读作"MemRL 范式的多模态空间域移植 + 估计量换形"，不是新机制。
- [[Papers/2608-RoMeRL]] —— 提供了 SMA 缺失的那组探针。RoMeRL 已实测出这类 selection 侧演化的 memory-reward trap：第一轮注入 10% null 化记忆（保留标题维持可检索性、抹掉实际效用字段）后，噪声条目十轮累计吃到正向更新 MemRL 3.7 次、MemRL+UCB 7.2 次、RoMeRL 2.4 次；且 **47.8% 的 MemRL 记忆终局仍停在初始 Q=0.5**（RoMeRL 降到 5.0%）。SMA 用同样的 bundle-level 归因（k=3 的三张卡吃同一个 `r_i`），在 D.1 承认无法归因到具体环节，却没做任何污染探针；§4.6.3 只给出 One-Pass 的 TRS-update 覆盖率约为 Continual 的 2 倍这一**相对**量，从未给 RoMeRL 已量化过的那个绝对量（多少比例卡片终局仍在 v0）。这是复现 SMA 时第一个该补的实验。
- [[Papers/2604-SpatialEvo]] —— Table 3 的对照方。SpatialEvo 的 backbone 是 Qwen2.5-VL-3B/7B-Instruct，SMA 用 Qwen3.5-9B，两者跨了一代；按 Table 1 的 no-memory 60.6 推算，+16.4 中约 13.5 来自 backbone、2.9 来自 memory。另注意口径不可互引：SpatialEvo 原文在 EmbSpatial 报 7B 为 66.0（9 benchmark 口径），SMA 在自己 1820 题的 deployment split 上给 SpatialEvo-7B 报 74.1。两篇的第一作者单位都是 Zhejiang University。
- [[Papers/2608-AgentMemoryDistill]] —— 写入侧的直接对立设计。AMD 只保留 teacher 的**成功轨迹**构建 memory store；SMA 反过来对成功与失败 rollout 一律写卡并统一初始化 v0=0.5（Appendix B.1 把 uniform initialization 列为显式设计要求）。但 SMA 自己的 Table 5 给出了支持 AMD 那一侧的证据：成功源卡片下游 accuracy 85.7% vs 失败源 61.4%，差 24.3pp。SMA 因此是在丢弃一个自测很强的先验，而"按源结果设差异化 v0"这一消融缺席。
- [[Papers/2606-SkillMemoryBudget]] —— 预算匹配的证伪框架。该文在 WebArena 三域上把 online skill/memory 模块的 token 开销折算给 vanilla actor（10→15 步 + AXTree 剪枝）后，Vanilla-IB 全面追平或反超 AWM / ASI / ReasoningBank。SMA 每题 prepend 3 张卡片且 environment 阶段每题多一次反思调用，却无任何 token / latency 核算（已全文确认），也没有"把等量 context 预算给 no-memory 基线"的对照——它的 +1.7~+2.9pp 无法排除预算不对称这一解释。
- [[Papers/2606-ProceduralMemoryAFTER]] —— 迁移检验的标准。AFTER 的核心主张是 procedural memory 必须过 held-out context 的 promotion gate，且同一 pdf skill 跨 role 迁移会掉 4.8–7.5pp（source-context overfitting）。SMA 的 env/deployment 是同一 benchmark 的 50/50 划分，属 in-distribution held-out；其真正的 cross-context 证据是 Table 4 的 benchmark transfer——ERQA→RoboSpatial +7.6，对照同域 54.1→68.5 的 +14.4，量级约减半，方向与 AFTER 的 specialization 结论一致。
- [[Papers/2604-CoTDegradesSpatial]] —— 反向先验。该文测出 CoT prompting 在 13 个 spatial benchmark 上平均掉 3%，8 个 RL 训练的 MRM 里 7 个打不过自己的 backbone，并用 No-Image++ 证明模型在看不见时仍编造几何。SMA 注入的正是文本 procedure，所以"文本 lesson 能改善 spatial grounding"并非默认成立——SMA 的 E.2 也承认三个 TRS≥0.6 的高质量记忆案例中，模型照样误读 movement direction、object count 与 spatial connectivity，与该文的机制诊断同向。SMA 之所以没掉点，可能与它注入的是"检查清单式的短 procedure"而非长 CoT 有关，但这条假设论文没测。
- [[Topics/SelfEvolvingAgents-Survey]] —— 该 survey 的 read-side / selection 演化一栏目前只有 [[Papers/2601-MemRL]] 与 [[Papers/2608-RoMeRL]] 两条文本 agent 证据，SMA 是第一条多模态空间域的同构实例，可作为该栏的 modality 外推点。另一处值得记的是：survey 指出"同一任务集跑 10 epochs、per-task 重复暴露是多数记忆方法的隐含前提"——SMA 用 env/deployment 划分把这个前提换掉了（10 个 pass 全部跑在 environment split 上，评测始终在 held-out），这一点比 MemRL 的 runtime 设置干净，是该栏可以吸收的协议改进；但它同时引入了新的口径问题（best-of-10 选择落在 deployment 上）。

## Mind Map

```mermaid
mindmap
  root((SpatialMemoryAgent))
    Problem
      冻结 VLM 提升空间推理
      不做 post-training
      推理时不调空间工具
      隐含前提 需同分布带标注 environment split
    Method
      verifier-guided reflection 产出 transferable lesson
      TRS 收缩均值 v=(λv0+c)/(λ+n)
      两阶段检索 语义筛 δ 加相似度-TRS 组合排序
      One-Pass 写入 deployment 只读
    Results
      主表 20 格 严格最优 18
      macro +1.7~+2.9pp 但为 best-of-10-pass
      相似度 0.792→0.698 而准确率 66.8→69.8
      附录 ViewSpatial 上 MemRL-GT 反超
      消融 semantic filter 贡献最大 −5.8/−7.2
```

## Notes

- Project page https://aim-uofa.github.io/SMA/ 目前标注 "Code Coming Soon"，仅链向 arXiv abs/pdf 与 OpenReview 作者页；`code` 字段暂留空，代码放出后可回填并考虑 repo-digest。arXiv 状态：v1（2026-08-13，cs.AI），Comments 为 "Under Review"。
- 待追问一：把 `η=0` 加进消融表，即在同一 bank、同一 δ 下比较"纯相似度 top-3"与"相似度+TRS top-3"。这是全文中心主张唯一直接的对照，目前只有 sensitivity 曲线的峰值作为间接证据。
- 待追问二：TRS 的 order invariance 是相对 MemRL 的 EMA 的明确改进，但收缩均值假定各次访问的 reward 独立同分布——而 guidance set 里三张卡吃同一个 `r_i`，访问之间是强相关的。用 bundle 内的相关结构做 credit 分摊（哪怕只是按 z-score 权重分配 reward），可能比换估计量更能提升 TRS 的判别力。
- 待追问三：环境阶段总共只写 |X| 张卡（每题一张），deployment 完全冻结。这意味着 SMA 学到的东西被 environment split 的题目分布硬性上界锁住。若把 environment 换成可程序化生成、且几何 ground truth 可精确计算的合成场景（[[Papers/2604-SpatialEvo]] 的 DGE 路线），memory bank 的规模与覆盖就不再受 benchmark 标注量限制——"用 DGE 造 environment、用 SMA 的 TRS 做 training-free 沉淀"是一个自然但尚无人做的组合，值得单独检索是否已被占位。
- 复现该论文时的最低要求：报告 pass 1..10 的完整曲线而非 best checkpoint，且对所有 baseline 施加同一选择规则；补 token 预算对照。
