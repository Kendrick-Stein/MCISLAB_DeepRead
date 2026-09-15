---
title: "Addressable Memory for Video World Models"
authors:
  - "Xindi Wu"
  - "Sven Elflein"
  - "James Lucas"
  - "Olga Russakovsky"
  - "Laura Leal-Taixé"
  - "Despoina Paschalidou"
  - "Jonathan Lorraine"
  - "Aljoša Ošep"
institute: ["NVIDIA", "Princeton University", "University of Toronto", "Vector Institute"]
date_publish: "2026-08-07"
venue: "arXiv"
tags: ["world-model", "spatial-memory"]
url: "https://arxiv.org/abs/2608.07408"
arxiv_id: "2608.07408"
doi:
cite_key: wu2026addressable
code:
rating: 4
content_scope: "full-text"
verification_status: "source-checked"
date_added: "2026-08-11"
---
## Summary

诊断 autoregressive video world model 长时程 visual persistence 崩坏的根因不是"存得不够"而是"存了读不出"：rollout 超出训练 horizon 后 temporal RoPE 的 query-key offset 落到训练分布外，KV cache 里的记忆变得不可寻址，且在 RoPE 旋转空间 naive 平均压缩会因 phase cancellation 损坏 summary。提出 training-free 的 WorldTrace：给每个 summary slot 按 slot rank 分配固定 offset 的 in-distribution virtual position，key 在 canonical（未旋转）空间压缩、读取时单次旋转到 virtual position；两种写入器 WorldTrace-Field（连续时间组 canonical key 平均，N=48 TempSSIM 相对 +15.5%）与 WorldTrace-Landmark（冻结 scene-entry 帧的 verbatim canonical key，自建 LoopBench ABA episodic recall +19.5%）。

## Problem & Motivation

Interactive video world model（游戏引擎、closed-loop robot simulator）要求 visual persistence：agent 走开再回到原地时，生成结果应与场景原貌一致而非"另一个貌似合理的场景"。现有做法把线性增长的 KV cache 压缩到固定大小，但作者指出瓶颈不在内容是否还在 cache 里，而在两个耦合的失败：

1. **可寻址性失败（position 侧）**：训练时 query 只见过有界的相对 offset（0 ≤ δ ≤ Δt_train）；长时程推理中 offset 越界后，快频 RoPE 分量的相位绕过 π 多圈、对 attention score 的贡献退化为噪声——记忆仍在 cache 中但 attention 读不到。附录 C 对 MG2-1.3B 逐频率量化：训练最大 offset 为 5 时 f≥10 的分量近似语义载体，而 offset=30 时最快三个分量相位已超 3π。
2. **信息性失败（content 侧）**：在 RoPE 已旋转空间对 key 做 naive 平均，不同时间戳的帧旋转角不同、方向相反时部分抵消（phase cancellation），无论内容是什么，该频率的信号都被削弱。

并行工作各修一侧：Infinity-RoPE 的 Block-relative 把所有 offset 封顶在 Δt_train，用在压缩 cache 上会让跨度超过 Δt_train 的多个 summary slot 坍缩到同一位置无法区分；MemRoPE 只因恰好只有 long/short 两个 EMA stream 才避免坍缩，不能扩展到 N-slot cache。两个失败必须联合解决。

## Method

**Cache 结构**：把局部 attention 窗口 L_attn 划分为 recent window（N_r 帧 verbatim）+ summary cache（N_s 个压缩 slot），N_s + N_r = L_attn，恒定 O(1) 预算。

**Slot-rank virtual position（Def. 1）**：summary slot s 的 virtual position 为 t_s^v = q − (L_attn − 1 − s)，offset 只由 slot rank 决定、与绝对 horizon N 无关。满足四条性质：线性、in-distribution、horizon-稳定、slot 间互异——避免 Block-relative 的坍缩（Rem. 1），也避免 Centroid-linear（按源帧平均时间戳线性映射）随 N 漂移出分布的问题。

**Canonical key 存储**：压缩前先把每个 key 反旋转回 canonical（未旋转）表示，在该空间合并，读取时再单次旋转到 slot 的 virtual position——同时解决 phase cancellation 和"压缩 key 残留源时间戳相位"两个问题。canonical 缓存机制与 MemRoPE 同源，新贡献是与 slot-rank position 的配对。

**Structured sparse attention 视角（Sec. 3.2）**：把压缩形式化为用投影矩阵 P（L×T）近似全量 attention；放松 P 为非负值即 NMF 问题。近优行结构随 query 分布二分：attention 平滑铺开时行应做连续时间组平均，集中在少数显著帧时行应 verbatim 选帧——正好导出两个变体：

- **WorldTrace-Field**：每个 slot 均匀平均其连续时间组的 canonical key（M ≈ T/N_s 随 rollout 线性增长），有 mean attention preservation 保证（Prop. 2，pre-softmax score 层面）。默认 recompute writer 把被逐出帧的 canonical key 留在 host memory；附录 E.7 给出 O(N_s) 状态的 streaming writer，保留大部分增益。
- **WorldTrace-Landmark**：用相邻帧 canonical key 的 cosine distance 突增（阈值 τ）检测 scene-entry 事件，把这些帧的 canonical key **冻结**后 verbatim 存入 slot；每次 slot 移位只做一次从冻结 canonical 形式到当前 virtual position 的新鲜旋转，避免反复 unrotate-rerotate 在 bfloat16 下的浮点漂移。slot 满后 FIFO 逐出最老 landmark。

两变体只差 P 矩阵的行结构，共享 slot-rank + canonical-store 设计；附录 E.1 显示两者可按 slot 配额混合共存于同一 cache。

## Key Results

主实验：Matrix-Game-2（MG2-1.3B，蒸馏自 Wan 1.3B T2V，3D-RoPE，L_attn=6 latent frames）；跨架构验证：LingBot-World（14B MoE，Plücker camera conditioning，附录 E.4）。

- **Position 是主约束（Table 1，压缩固定为 canonical averaging 只变 position）**：WorldTrace 超 Block-relative +5.9%/+2.8%、超 Centroid-linear +9.5%/+13.8%（TempSSIM，N=8/16）。
- **Coherence（Table 2）**：N=48 时 WorldTrace-Field TempSSIM 0.545 vs sliding window 0.472（相对 +15.5%），Scene Drift 同时最低（0.0295）；N=32 时 TempSSIM 最高（0.613）但 Drift 略高于 centroid 变体。
- **Episodic recall（Table 3，LoopBench，n=100 初始场景/条件）**：四个难度 tier 的全部条件 PAC 占优；ABA（N=16）0.864 vs 0.723（+19.5%）。最难的 Tier 3 360° pan 增益最小（0.577 vs 0.559）。
- **对并行 training-free 基线（Table 9，ABA N=32/48）**：WorldTrace-Landmark 0.964/0.972 > Landmark+Block-relative 0.929/0.934 > MemRoPE 0.651/0.706；YaRN 需 O(N) cache（约 N=100 即 OOM）；MemRoPE 换上 WorldTrace position 反而变差（写读 offset 不一致，p<0.001）。
- **扩展 sweep（Table 10）**：recall 分三档——compression-only 约 0.4-0.6；canonical-K anchoring 中等 horizon 0.91-0.955 但 N=256 跌至 0.610；只有 verbatim landmark 在 N=256 保持 0.989。
- **跨架构（Table 11，LingBot-World）**：Landmark 在 4×/6×/8× 训练 horizon 提升 +8.9%/+14.1%/+7.3%，2× 无显著增益（−0.006，p>0.1）；Field 与 sliding window 接近（Plücker 条件已提供 recall 信号）。
- **开销（Table 13，A100 80GB）**：Field 的 peak GPU memory 与 sliding window 在 N=64/256/512 完全一致（host memory 每 latent frame +5.4 MB）；Landmark 恒定 +约 0.6 GB。

> **协议边界**：同一 ABA 配置在不同表格的绝对 PAC 差异很大（如 N=16 sliding window 在 Table 3 为 0.723、Table 4/10 为 0.540、Table 8 固定 seed 为 0.837），论文未明文解释口径差异；+19.5%（Table 3 口径）与 0.989（Table 10 口径）来自不同实验协议，绝对值不可跨表混用。

## Evidence Ledger

| Claim ID | Claim | Type | Source locator | Evidence excerpt | Status |
|:--|:--|:--|:--|:--|:--|
| C1 | 长时程失败根因是 addressability：offset 越界后记忆存而不可读 | causal-mechanism | Abstract; Sec 1; Sec 2.1 | "even if past memories are stored in the KV cache, the model cannot reliably retrieve them" | source-verified |
| C2 | RoPE 旋转空间 naive 平均因 phase cancellation 损坏 summary | causal-mechanism | Sec 2.2 | "their angles can point in opposite directions and partially cancel" | source-verified |
| C3 | slot-rank virtual position（t_s^v = q − (L_attn − 1 − s)）+ canonical 空间存储保持可寻址 | causal-mechanism | Sec 3.1 Def 1; Sec 3.3 | "unrotate each key to its canonical content, average in that space, and then re-encode at virtual position" | source-verified |
| C4 | 两变体：Field 连续时间组平均；Landmark 冻结 cosine-spike 检出的 scene-entry 帧 | benchmark-setting | Sec 3.3; Sec 3.4 | "cosine distance... spikes above threshold τ as a scene-entry event" | source-verified |
| C5 | training-free：固定 checkpoint 上只改 cache 读写，无需 retraining | license-code | Abstract; App D.5 | "no retraining, restoring addressability by changing cache read/write on a fixed checkpoint" | source-verified |
| C6 | N=48 TempSSIM 0.545 vs 0.472（相对 +15.5%），Drift 最低 | number | Table 2; Sec 4.2 | "+15.5% relative gain on TempSSIM, lowest Drift" | source-verified |
| C7 | LoopBench ABA PAC 0.864 vs 0.723（+19.5%，N=16） | number | Table 3 Tier 1; Conclusion | "raises Scene Consistency by +19.5% on LoopBench ABA loops" | source-verified |
| C8 | LoopBench：自参考打分（PAC），4 难度轴 12 配置，n=100 场景/条件 | benchmark-setting | Sec 4.1; App F | "the rollout itself produces both the target and the prediction" | source-verified |
| C9 | N=256 时 Landmark PAC 0.989 vs canonical-K anchoring tier 0.610 | number | App E.3 Table 10 | "canonical-K tier's PAC falls to 0.610 while WorldTrace-Landmark holds at 0.989" | source-verified |
| C10 | Block-relative 封顶致 slot 坍缩；MemRoPE 仅两 stream 不扩展到 N-slot | comparison | Sec 2.1; Rem 1 | "caps every offset... so distinct summary slots collapse onto the same position" | source-verified |
| C11 | LingBot-World：Landmark +8.9%/+14.1%/+7.3%（4×/6×/8×），2× 无显著增益 | number | App E.4 Table 11 | "+8.9%, +14.1%, +7.3% at 4×/6×/8×... no significant gain at 2×" | source-verified |
| C12 | Field peak GPU 与 baseline 完全一致（host +5.4 MB/帧）；Landmark 恒定 +0.6 GB | number | App E.6 Table 13 | "matches the sliding-window baseline exactly at all three horizons" | source-verified |
| C13 | Position ablation：超 Block-relative +5.9%/+2.8%，超 Centroid-linear +9.5%/+13.8% | number | Sec 4.2 Table 1 | "outperforming Block-relative by +5.9% and +2.8% TempSSIM" | source-verified |

## Strengths & Weaknesses

**Strengths**

- 第一性原理式的机制诊断：把长时程失败从"存多少内容"重构为"位置是否可寻址"，并给出逐频率分析（快频 RoPE 分量在 offset 越界后相位随机化、慢频仍是语义载体）——机制清晰、可检验，且被 YaRN 单独 +22% 的结果侧面支持（position 确是主瓶颈）。
- 方法极简且 training-free：两个机制（slot-rank position、canonical 空间压缩）各自对应一个明确的失败模式（Block-relative collapse / phase cancellation），ablation 把 position 轴和 content 轴干净分离验证。
- structured sparse attention / NMF 统一视角把"存什么"变成投影矩阵 P 的选择问题，Field/Landmark 只是 P 的两个特例——为后续自适应写入器留了清晰接口。
- LoopBench 自参考设计（对照模型自己 first-visit 生成的帧，无需外部 ground-truth 视频）+ 四个正交难度轴，比 Po et al. 的 Memory Maze 回溯任务覆盖面广。
- 边界报告诚实：360° pan 增益缩小、LingBot 2× 无显著增益、MemRoPE+WorldTrace 组合反而变差（写读 offset 不一致）均如实报告。

**Weaknesses**

- 同一 ABA 配置在 Table 3 与 Table 4/9/10 的绝对 PAC 差异显著（sliding window 0.723 vs 0.540，N=16），论文未解释评测口径差异，削弱跨表可比性（已知，见 Key Results 协议边界）。
- 验证面窄：主结果在单一 1.3B game world model 上，LingBot-World 仅附录级验证且 Field 在其上几乎无增益；PAC 依赖 CLIP 相似度，对"几何一致但外观漂移"类失败的敏感度未知（推测）。
- Landmark 依赖 scene-entry 检测的 cosine-spike 阈值 τ 这一启发式，slot 满后 FIFO 逐出最老 landmark——多场景长程探索下"该记住哪些地方"仍是未解问题；作者自认两种 writer 只是"两个简单结构化投影"，自适应选择留待未来。
- Field 对 recall 几乎不帮忙（compression tier PAC 约 0.4-0.6），coherence/recall 分工意味着单配置内存在 trade-off；App E.1 的 slot 配额混合只部分缓解。
- LoopBench 由同一团队提出并主要用于验证自家方法，尚无第三方结果可交叉参照（已知）。

## Mind Map

```mermaid
mindmap
  root((WorldTrace))
    Problem
      RoPE offset 越界使记忆不可寻址
      Naive 平均致 phase cancellation
    Method
      Slot-rank virtual position
      Canonical key 空间压缩
      Field 分组平均保 coherence
      Landmark 冻结 scene-entry 保 recall
    Results
      TempSSIM 相对 +15.5% at N=48
      LoopBench ABA PAC +19.5%
      N=256 verbatim recall 0.989
      Training-free 且 O(1) cache
```

## Notes

- 与 [[2603-HybridMemory]] 正交互补：HyDRA 解决动态主体出画-入画的**内容侧**记忆（需训练 + HM-World 数据），WorldTrace 解决静态场景 revisit 的**位置侧**可寻址性（training-free、geometry-free，明确不处理动态主体）。两篇合起来勾勒出 video world model memory 的 position/content 双轴分类。
- 论文把 prior work 组织为 position 修正（Block-relative/Infinity-RoPE、YaRN）与 content 写入（MemRoPE EMA、merging、eviction）两轴并声称首个联合设计——这个 framing 本身可能比具体方法更有复利价值：addressability 视角或可迁移到其他 RoPE-based 长上下文生成（streaming video LLM）（推测）。
- "MemRoPE 换上更好的 position 反而变差"是一个有信息量的负结果：position 和 content 写入必须在同一 offset 分布下共同设计，单独替换任一侧可能有害。
