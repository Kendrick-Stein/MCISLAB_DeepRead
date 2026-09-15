---
title: "Skills in Weights, Memory in Code: Hybrid Learning for Memory-Dependent Robot Manipulation"
authors: [Yunhao Zhao, Zhenyang Ni, Haoyang Chen, Ruohan Zhang, Qi Zhu]
institute: [Northwestern University, University of Minnesota, Stanford University]
date_publish: 2026-08-10
venue: arXiv
tags: [manipulation, VLA, task-planning]
url: "https://arxiv.org/abs/2608.09410"
arxiv_id: "2608.09410"
doi:
cite_key: zhao2026skills
code:
rating: 4
content_scope: full-text
verification_status: source-checked
date_added: 2026-08-11
---
## Summary

HyMeS 把 memory-dependent manipulation 拆成两条学习通道：motor skill 在 weight space 用 flow-matching imitation learning 学（π0.5 fine-tune 后冻结），memory-management 策略由 coding agent（Opus 4.8）在 code space 通过 rollout 反馈的 heuristic learning 迭代编辑可执行程序获得。推理时 symbolic memory 选出 stage-specific 可微 constraint，其梯度注入冻结 VLA 的 flow-matching velocity field 实现 steering，并用 proprioception + Qwen3-VL-8B 多帧投票（PACE）验证 stage 完成来更新 memory。在 RoboMemArena 修正后的 12-task protocol 上，CSR 52.5%→66.2%、TSR 41.3%→60.1%（vs 同权重 π0.5），总体超 PrediMem 4.5 / 14.5 点。

## Problem & Motivation

现代 VLA（π0.5 等）的 motor 能力已相当强，但结构上是 Markovian 的：每个 action chunk 只依赖当前观测或短的固定长度 context。而现实操作任务常是 non-Markovian 的——比如按键次数由 episode 开始时出现、随后被移走的卡片指定，此时同一当前观测对应多个不兼容的 action mode（observation aliasing），Markovian policy 只能在各 mode 间平均。

现有 memory-augmented VLA 的主流补救是把 memory 端到端学进 action model（扩展 context、memory token、hierarchical/event memory 等），但这把 memory 获取与 motor 学习纠缠在一起：memory 逻辑是组合式、离散的，在 weight space 学习就要求 demonstration 覆盖组合式的任务状态空间，且得到的 latent memory buffer 难以检查和编辑。

## Method

核心思想：**分离 motor-skill learning 与 memory-strategy learning**，各用适配的学习机制。

**1. Motor-skill learning in weight space**。从 π0.5 初始化的 Markovian flow-matching policy，用标准 flow-matching objective 在 expert demonstration 上 fine-tune；此后权重全程冻结，memory 获取不再更新参数、不需要额外 expert action。

**2. Memory-strategy learning in code space（heuristic learning）**。外部程序 P=(C,V,U) 包含 constraint-selection、event-verification、memory-update 三类规则，维护显式 symbolic state s_t =（plan、active stage ρ_t、task bindings、repeated-event counts、persistent states），作为 latent task state z_t 的可执行估计。coding agent（claude code / codex，实验用 Opus 4.8）拿 rollout 的 symbolic execution trace ξ_n 与 benchmark 的 stage-wise verdicts b_n 定位失败 stage，诊断是 constraint reward 错设还是 verification 规则过严/过松，然后修订程序：P^(n+1) = Edit(P^(n), ξ_n, b_n)。整个过程不用梯度、不用 expert action label。开发集上最优的 P* 在评测时冻结（仍由 coding agent 应用它实例化 stage 规则与初始 memory，但禁用 rollout 级诊断与程序修订）。

**3. Memory-conditioned action steering**。active stage + symbolic memory 选出 stage-specific 可微 constraint R（如 reaching stage 的 end-effector 到目标 keypoint 距离；symbolic target 经 open-vocabulary detection、mask refinement、depth back-projection ground 到场景 keypoint，keypoint 提取用 SAM + DINOv2）。R 的梯度按 VLS 的接口注入 flow-matching velocity field（v̂ = v_θ* + λ_t ∇R），guidance 系数 λ_t 随 constraint residual 的下降按 sigmoid 调度衰减——让 memory 主导全局行为选择、让学到的 motor policy 主导 contact-rich 执行。

**4. PACE（Proprioception-And-Completion-driven stagE-switching）**。周期性发 completion query：proprioceptive 判断（动作相关运动模式 + symbolic latch）与 Qwen3-VL-8B 多帧判断（active stage + 最多 5 帧近期 RGB）做 OR 合并，最近 w 次 query 中至少 k 次通过才触发 stage 切换（全部实验 w=5, k=3）。事件通过后 U 更新 bindings/counters/persistent states 并激活下一 stage 的 constraint，形成 steering 与执行之间的双向闭环。

与相近工作的区别：steering 类方法（VLS、DynaGuide、value guidance 等）的 guidance 是 reactive 的、信息单向流入 policy，不维护 episode 级 memory；Harness VLA 的 memory 在 primitive 粒度上编排冻结 VLA，而 HyMeS 把可执行 memory 直接耦合进 denoising 过程逐 action steer。

## Key Results

- **RoboMemArena（修正 12-task protocol，160 episodes，四类：transferring / counting / sequence / occlusion）**：同一 fine-tuned π0.5 权重下，HyMeS overall CSR 52.5%→66.2%、TSR 41.3%→60.1%；超 PrediMem 4.5 CSR / 14.5 TSR 点（61.7/45.6→66.2/60.1）。TSR 增益远大于 CSR 增益，说明 HyMeS 更能把中间进度转化为整任务成功。
- **分类别**：对 π0.5 的最大 TSR 增益在 counting（+30.0）、transferring（+26.6）、sequence（+22.5），与显式 counter、object–location binding、stage state 的作用一致。counting 类 HyMeS TSR 高于 PrediMem（50.0 vs 36.7）但 CSR 反而更低（60.3 vs 72.2），失败集中在早期执行阶段，作者猜测源于冻结 VLA 的局限或 guidance 干扰。
- **Occlusion 是 memory 注入最难的类别**：PrediMem 的 CSR 反而低于 reactive π0.5（38.3 vs 50.4）——不可靠的 memory 会在目标被遮挡时主动误导执行；HyMeS CSR 与 π0.5 持平（50.6）、TSR 高 7.0 点，说明 verified stage transition 限制了错误 binding 的损害。
- **真机 SO-101（3 个 memory-dependent 任务，每方法 35 trials）**：overall TSR 25.7%→57.1%；分任务 2/10→7/10（observe-and-pick-up）、7/15→11/15（number-guided button pressing）、0/10→2/10（put-back block）。
- **Ablation（六任务子集）**：rollout 精炼的 P* vs one-shot P^(0) 提升 CSR +8.5 / TSR +18.4（63.3/53.3→71.8/71.7），验证 heuristic learning 有效；vision-only PACE 相对 full 掉 16.0 CSR / 21.7 TSR，proprio-only 掉 8.8 / 8.4——两路证据互补，单一信号都会误判 stage transition。
- **失败模式可解释**：symbolic memory 和 constraint 正确时的失败可定位到 motor 执行（pre-grasp 偏移导致 missed grasp、按键 jitter 导致多按）或 verification（按压深度不足未被 PACE 判完成），而非 memory 损坏。

## Evidence Ledger

| Claim ID | Claim | Type | Source locator | Evidence excerpt | Status |
|:--|:--|:--|:--|:--|:--|
| C1 | RoboMemArena 上 HyMeS 相对 π0.5：CSR 52.5%→66.2%、TSR 41.3%→60.1% | number | Abstract; Table 1 Overall row | "improves mean cumulative success from 52.5% to 66.2% and mean task success from 41.3% to 60.1%" | source-verified |
| C2 | 总体超 PrediMem 4.5 CSR / 14.5 TSR 点（66.2 vs 61.7、60.1 vs 45.6） | comparison | Abstract; Table 1 Overall row | "outperforming PrediMem by 4.5 points in cumulative success and 14.5 points in task success" | source-verified |
| C3 | PrediMem 在作者修正的 12-task protocol 上复评，非其发表的 26-task 结果；任务筛选只用 protocol check 与 π0.5 行为 | benchmark-setting | Experimental Setup — Tasks and metrics; Baselines | "reevaluated on our 12-task protocol rather than using its published 26-task results" | source-verified |
| C4 | memory 策略由 coding agent（Opus 4.8）经 heuristic learning 获得：P^(n+1)=Edit(P^(n),ξ_n,b_n)，无梯度无 expert label；评测时 P* 冻结 | causal-mechanism | Memory-Strategy Learning in Code Space (Eq. 9–10); Implementation details | "uses neither gradients nor expert action labels… coding agent uses an Opus 4.8 model" | source-verified |
| C5 | steering：stage constraint 梯度注入冻结 VLA 的 flow-matching velocity field（沿 VLS 接口），sigmoid 调度衰减，全程不更新权重 | causal-mechanism | Memory-Conditioned Action Steering (Eq. 12–13); Implementation details | "v̂=vθ⋆+λt∇Rρt… Policy weights remain fixed during heuristic development and evaluation" | source-verified |
| C6 | PACE：proprio OR Qwen3-VL-8B 多帧（≤5 帧）判断，k-of-w 投票触发切换，w=5、k=3 | causal-mechanism | Multimodal Progress Verification (Eq. 14–15) | "at least k of the w most recent queries… We use w=5 and k=3 in all experiments" | source-verified |
| C7 | SO-101 真机 3 任务 35 trials/方法：TSR 25.7%→57.1%；分任务 2/10→7/10、7/15→11/15、0/10→2/10 | number | Table 2; Real-world experiments | "35 trials per method in total… Overall TSR rises from 25.7% to 57.1%" | source-verified |
| C8 | ablation：P* vs P^(0) 提升 CSR +8.5 / TSR +18.4；vision-only 掉 16.0/21.7，proprio-only 掉 8.8/8.4 | number | Table 3; Ablation Studies | "improves CSR and TSR by 8.5 and 18.4 points… visual-only… 16.0 and 21.7" | source-verified |
| C9 | occlusion：PrediMem CSR 低于 π0.5（38.3 vs 50.4）；HyMeS CSR 持平（50.6）、TSR +7.0（47.0 vs 40.0） | comparison | Table 1 Occlusion category average; Quantitative Results (iv) | "PrediMem falls below the reactive π0.5 (38.3% vs. 50.4% CSR)" | source-verified |
| C10 | counting：HyMeS TSR 高于 PrediMem（50.0 vs 36.7）但 CSR 更低（60.3 vs 72.2），失败集中早期 stage | comparison | Table 1 Counting category average; Quantitative Results (iii) | "higher TSR than PrediMem (50.0% vs. 36.7%) despite lower CSR (60.3% vs. 72.2%)" | source-verified |
| C11 | demonstration 只需覆盖可复用 motor skill；每平台单一 checkpoint，memory 获取从不更新权重 | causal-mechanism | Abstract; Demonstration cost and inspectability | "a single fine-tuned checkpoint per platform: acquiring memory never updates policy weights" | source-verified |

## Strengths & Weaknesses

**亮点**：
- **问题拆分干净**：把"memory 逻辑是离散组合式的、不适合 weight space"这一观察落成 hybrid 设计——demonstration 预算随可复用 motor skill 数扩展而非随 history-dependent 配置数扩展，新 memory 配置（换目标颜色、换次数）改代码即可，不用采数据。这是对端到端 memory-augmented VLA 路线的一个结构性批评。
- **双向闭环是相对 steering 前作的实质增量**：VLS 等方法的 guidance 是 reactive、单向的；HyMeS 把 constraint 条件在显式 symbolic memory 上，且用 proprio+visual 证据回读更新 memory。occlusion 类的结果（PrediMem 反而拖累 π0.5，HyMeS 不掉点）是"unreliable memory 有害、verified transition 能兜底"的直接证据。
- **可解释性可操作**：symbolic state 每步可读，失败可三分定位（memory update / motor 执行 / event verification），failure 分析（Fig. 4）确实用上了这个性质。
- **ablation 信息量足**：P^(0)→P* 的 +18.4 TSR 说明 heuristic learning 不是摆设；两路 verification 信号的互补性也有数字支撑。

**局限（论文承认）**：
- 只适用于 relevant history 可压缩为 compact symbolic state 的任务；开放式指令、非结构化 memory 不在射程内。
- 任务成功仍受 motor 能力与 stage-completion verification 限制：memory 和 constraint 都对，contact-rich 执行照样会失败。
- 周期性 VLM query + coding agent 调用带来每 episode 的推理延迟与成本（论文未给出具体数字）。

**我的批判性观察（推测标注）**：
- **比较基线是作者自建口径**：12-task protocol 由作者从 RoboMemArena 修正筛选而来，PrediMem 的发表结果不可直接比较、须信任作者的复评实现。论文声明筛选只用 protocol check 与 π0.5 行为、不用 HyMeS 结果（已核实原文如此声明），但筛选标准"保留 π0.5 有 motor skill 却因缺 history 失败的任务"天然偏向 memory 注入类方法能改进的任务分布（推测）。
- **heuristic learning 依赖 benchmark 的 stage-wise verdicts b_n**：开发阶段需要 stage 级 ground-truth 反馈，这在仿真 benchmark 里免费，在真实开放场景是隐含假设——真机部分如何获得开发反馈论文着墨不多（不知道）。
- **样本量小**：每任务 10–20 episodes、真机每任务 10–15 trials，单任务数字（如 63.0、42.0 等非整倍数值）波动敏感；category/overall 层面更可信。
- **counting 类 CSR 低于 PrediMem** 提示 guidance 注入可能干扰早期 stage 的 motor 执行——steering 不是免费午餐，这与作者自己的归因一致。
- "heuristic learning" 概念引自 Weng 2026 的 blog（Learning beyond gradients）；机制上与 Eureka/Voyager 一脉的 LLM 程序迭代同源，novelty 在于把它接到 VLA denoising 内部而非替代/编排 policy。

## Mind Map

```mermaid
mindmap
  root((HyMeS))
    Problem
      VLA 是 Markovian 的
      任务 non-Markovian：observation aliasing
      端到端 memory 需覆盖组合式配置
    Method
      Weight space: flow-matching IL 学 motor skill
      Code space: coding agent heuristic learning 学 memory 策略
        P=(C,V,U) 可执行程序
        rollout trace + stage verdicts 迭代 Edit
      Steering: constraint 梯度注入 velocity field
      PACE: proprio OR VLM 多帧 k-of-w 投票
    Results
      RoboMemArena CSR 52.5→66.2 TSR 41.3→60.1
      超 PrediMem +4.5 CSR +14.5 TSR
      SO-101 TSR 25.7→57.1
      Ablation: heuristic learning +18.4 TSR
      Occlusion: verified transition 兜底
```

## Notes

- 与 [[2608-MemoryLies]] 互补：那篇实证 spatial memory staleness 会主动误导 VLM agent，本篇 occlusion 类结果（PrediMem 低于 reactive baseline）是同一现象在 manipulation 端的印证；HyMeS 的答案是 verified stage transition + 可编辑 symbolic state。
- 与 [[2606-SkillMemoryBudget]] 的张力：那篇问 skill/memory 模块是否值回 token 成本，本篇的 VLM query + coding agent 调用成本恰好未量化——若做成本核算，counting/occlusion 类的净收益如何是个开放问题。
- "memory in code" 与 Harness VLA（2607.08448，primitive 粒度编排）构成同方向不同耦合深度的两点，加上 VLS（2602.03973，无 memory 的 reactive steering），可以画一条 "steering 冻结 VLA" 的谱系。
- 疑问：真机开发阶段的 stage verdicts 从哪来（人工标注？）；P* 跨任务复用程度如何（每任务一个程序还是共享 heuristic 库），论文未明说。
