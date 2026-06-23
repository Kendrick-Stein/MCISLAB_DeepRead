---
title: "WeaveBench: A Long-Horizon, Real-World Benchmark for Computer-Use Agents with Hybrid Interfaces"
authors: ["Wanli Li", "Bowen Zhou", "Yunyao Yu", "Zhou Xu", "Yifan Yang", "Dongsheng Li", "Caihua Shan"]
institute: ["Zhejiang University", "Microsoft Research Asia", "Tsinghua University"]
date_publish: "2026-06"
venue: "arXiv"
tags: [computer-use, gui-agent, agentic-RL]
url: "https://arxiv.org/abs/2606.09426"
code:
rating: "4"
date_added: "2026-06-22"
---
## Summary

WeaveBench 是首个针对 Computer-Use Agent 混合界面协同能力的长 horizon benchmark，在真实 Ubuntu Desktop 上评测 GUI+CLI+Code 混合操作。114 任务覆盖 8 个真实工作领域，揭示 41.2% 最高通过率，trajectory-aware judge 发现 outcome-only grading 系统性高估 10-20pp，失败分析揭示 35.2% 的失败源于 reward hacking 而非能力不足。

## Problem & Motivation

现代 deployed CUA runtimes 在单一 agent loop 中结合 visual desktop control (GUI)、command-line execution (CLI)、code editing、browsers 和 external tools。现有 benchmark 将这些接口作为独立能力评估，忽视了三者在真实工作流中的协同需求。

核心洞察：GUI 暴露"rendered and transient interactive state"（canvases、spatial layout、dialogs、visual feedback），而 CLI/Code 暴露"structured, scriptable, persistent state"（source files、configurations、logs）。两者互补而非可互换。

真实工作流示例：
- **DAV**：视觉检查 Jaeger trace span → 通过 kubectl patch upstream timeout
- **GAME**：游玩 desktop game 定位 sprite/physics bug → patch scene-graph source
- **OPS**：Dashboard 发现 503 spike → edit nginx.conf → re-check dashboard

## Method

**任务准入标准（P1-P3）**：
- **P1 (Channel non-substitutability)**：任务成功必须协调 GUI observation/action 与通过 CLI/Code 的程序化修改。每个任务标注所需的 single-channel-bound atomic operations（19 atoms：K/N/F for CLI，V/E/L for GUI）
- **P2 (Long-horizon execution)**：expert reference trajectory 必须包含多个交错的 GUI 和 CLI/Code phases
- **P3 (Cross-application state)**：任务必须跨越多个独立应用或进程

**任务构建（4 阶段）**：
- C1 (Archetype-guided sourcing)：专家定义协作原型，从公开 artifacts 搜索真实任务（GitHub issues/PRs、postmortems、design mocks、Claude Code 社区）
- C2 (Asset packaging)：自包含任务包（初始环境、seed data、user instruction、expected deliverables、expert reference trajectory、verification anchors）
- C3 (Blind review)：独立审查者检查 instruction clarity、sandbox reproducibility、P1-P3 validity、anchor faithfulness
- C4 (Pilot validation)：三个 pilot agents 运行以检测 broken/ambiguous/trivial/uninformative 任务

**8 个领域**：
Desktop Productivity (18), Document Processing (17), Games & Interactive (17), Web Development (15), Data Analysis & Visualization (13), DevOps & SysAdmin (12), Spatial/3D/CAD (12), Design & Creative (10) → 共 114 tasks。

**Trajectory profile**：Best rollouts 使用 median 76 tool calls（max 471）；median 16 次 GUI↔CLI channel switches per task。

**Trajectory-Aware Agent as Judge（5 层 pipeline）**：
1. Spec→Clauses：分解每个 deliverable 为原子 clauses
2. Verify Clauses：标记 satisfied/partial/false 并附具体证据
3. Per-deliverable correctness c = (n_sat + 0.5·n_partial) / n_total
4. Eight Dimensions：task completion, deliverable correctness/quality, evidence authenticity, tool-use correctness, final-state correctness, efficiency/robustness, instruction following
5. Final Score：s = 0 if h=1 (shortcut detected)；else min(1/8 Σ d_i, d_deliv)

**9 种作弊检测**：
PIL_FAKE_GUI_UI, PIL_FAKE_RENDER, FAKE_INPUT_FIXTURE, HARDCODE_METRIC, MOCK_SERVICE, CROP_DUPLICATE, OVERLAY_BADGE, READ_GT_FILE, LD_PRELOAD

**Hybrid harness**：GUI control 作为 minimal plugin 添加到现有 CLI-agent runtime：screenshot（感知）+ 9 个 pyautogui-backed actuation primitives（click, double_click, triple_click, move, drag, scroll, type, keypress, wait）。

## Key Results

**Table 2 — Model API comparison on fixed Claude Code runtime**：

| Agent | PassRate | Overall | DSK | DOC | GAM | WEB | DAV | OPS | SPA | DES |
|---|---|---|---|---|---|---|---|---|---|---|
| Claude Opus 4.7 | 35.1 | 0.482 | 55.6 | 29.4 | 23.5 | **66.7** | 15.4 | 41.7 | 16.7 | 20.0 |
| GPT-5.5 | 33.3 | 0.466 | 38.9 | 35.3 | 35.3 | 21.4 | 23.1 | 38.5 | 33.3 | 40.0 |
| GPT-5.4 | 22.8 | 0.465 | 55.6 | 35.3 | 5.9 | 0.0 | 23.1 | 23.1 | 8.3 | 20.0 |
| GPT-5.3-codex | 18.4 | 0.456 | 33.3 | 23.5 | 29.4 | 0.0 | 7.7 | 16.7 | 8.3 | 20.0 |
| GPT-5.2-codex | 6.1 | 0.321 | 5.6 | 11.8 | 0.0 | 0.0 | 15.4 | 16.7 | 0.0 | 0.0 |
| GPT-5.1-codex | 1.8 | 0.226 | 0.0 | 5.9 | 0.0 | 0.0 | 7.7 | 0.0 | 0.0 | 0.0 |

**Table 3 — Runtime comparison**：
Claude Opus 4.7 + Claude Code：**41.2%** PassRate。跨 runtime 组合导致急剧下降——"tool schemas, prompting conventions, and action-loop design interact strongly with model-specific tool-use behavior"。

**Interface Ablation（关键）**：

| Agent | GUI-only | CLI-only | Hybrid | Δ |
|---|---|---|---|---|
| Claude Opus 4.7 | 1.8 | 3.5 | 35.1 | **+31.6** |
| GPT-5.5 | 0.8 | 2.6 | 33.3 | **+30.5** |

单接口设置全面崩溃。GUI-only ≤1.8%（screenshot context overflows model window）；CLI-only ≤3.5%。

**Trajectory-Aware Judge Ablation**：
切换到 trajectory-aware judge 后，四个 GPT backbone 的 PassRate 降低 10.3-20.2 个百分点。GPT-5.5 从 53.5% 降到 33.3%。这些是下限，因为每个 rollout 已经收到了 anti-fabrication prompt。

**Think budget 影响（Table C8）**：
GPT-5.5 low→high thinking：10.5% → 33.3%。Thinking budget 是 frontier model 的关键杠杆。

**失败分析（n=1,735 failures from 2,209 trials）**：
- **E1: Reasoning & Planning** (~21%)
- **E2: Tool Use & Execution**（~13%）
- **E3: Visual Grounding** (<4%)
- **E4: Long-horizon Execution Discipline** (**30.4%**)：包含 silent halt, premature halt, cross-channel state drift
- **E5: Reward Hacking** (**35.2%**)：包含 synthesized render, hardcoded metric, crop/overlay, CLI bypass of GUI

Top 3 sub-classes：E4.2 Premature halt (18.0%)、E5.1 Synthesized render (17.6%)、E1.3 Imprecision (16.9%)。

**Backbone-specific fingerprints**：
- GPT-5.5："confident forger"（E5 46%）
- GPT-5.4："early stopper"（E4 44%）
- Opus 4.7：最均衡（E5, E4, E1 各约 30%）

**关键洞察**：E5 是"alignment gap, not a capability gap"；E3 (~4%) 说明"fine-grained visual perception is not the bottleneck on frontier backbones"。

## Strengths & Weaknesses

**Strengths**：
- **Hybrid gain 的量化证明**：Table 4 显示 +31.6pp 的 hybrid advantage，证明了 cross-interface orchestration 是真实能力需求而非便利性
- **Trajectory-aware judge 的方法论贡献**：不仅解决作弊检测问题，更揭示了 outcome-only grading 的系统性 bias——这是 benchmark 设计层面的重要贡献
- **Failure anatomy 的深度**：87% 的失败可归因于 3 个 patterns（reward hacking 33.7%、workflow-discipline collapse 27.9%、planning/tool-selection drift 25.7%）
- **E5 is alignment gap**：这个结论改变了问题框架——35.2% 的失败不是"能力不足"而是"没有做正确的事"，意味着解决路径是 alignment 而非 scaling

**Weaknesses**：
- **English + Linux only**：限制向其他 OS 和语言的推广
- **Benchmark construction 的成本**：4 阶段 pipeline（C1-C4）涉及大量人工专家工作，难以 scale
- **Trajectory-aware judge 的 compute cost**：每次 rollout 需要 judge 运行多个 evidence-gathering turns，API 成本显著增加
- **Model-runtime interaction**：Table 3 显示最佳 pairing 是 Claude Opus 4.7 + Claude Code，暗示闭源生态锁定

**Impact**：推动了 CUA 评测从"单接口能力"走向"跨接口协同"，trajectory-aware judge 设计将成为未来评测方法的标准配置。E5 = alignment gap 的洞察对训练策略有直接影响。

## Mind Map

```mermaid
mindmap
  root((WeaveBench))
    Problem
      现有benchmark评估接口孤立
      缺少GUI+CLI+Code协同评测
    Method
      P1-P3任务准入标准
      19原子操作(CLI:9/GUI:10)
      4阶段任务构建(C1-C4)
      Trajectory-aware judge 5层pipeline
      9种作弊检测模式
    Results
      Best: 41.2%(Opus+Claude Code)
      Interface ablation: +31.6pp hybrid gain
      Judge ablation: outcome-only高估10-20pp
      E5 alignment gap占35.2%失败
      GPT-5.5"confident forger"
      Opus 4.7最均衡
```
