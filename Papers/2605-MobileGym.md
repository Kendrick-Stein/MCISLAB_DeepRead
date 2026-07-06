---
title: "MobileGym: A Verifiable and Highly Parallel Simulation Platform for Mobile GUI Agent Research"
authors: ["Dingbang Wu", "Rui Hao", "Haiyang Wang", "Shuzhe Wu", "Han Xiao", "Zhenghong Li", "Bojiang Zhou", "Zheng Ju", "Zichen Liu", "Lue Fan", "Zhaoxiang Zhang"]
institute: ["CASIA", "Peking University", "CUHK"]
date_publish: "2026-05"
venue: "arXiv"
tags: [gui-agent, agentic-RL]
url: "https://arxiv.org/abs/2605.26114"
cite_key: wu2026mobilegym
arxiv_id: "2605.26114"
code: "https://github.com/Purewhiter/mobilegym"
rating: "4"
date_added: "2026-06-22"
---
## Summary

MobileGym 是一个浏览器托管的 Android-like 仿真平台，通过 JSON 状态建模实现确定性验证，支持低成本并行 RL 训练。GRPO on Qwen3-VL-4B-Instruct 在 416-task MobileGym-Bench 上 +12.8pp；真实设备迁移保留 95.1% 训练增益，揭示 functional modeling 已足够抓住 everyday app 交互本质。

## Problem & Motivation

现有 mobile GUI agent 环境存在根本性 trade-off：emulator-based 系统（AndroidWorld、AndroidLab）可重复评估但只覆盖系统工具和开源 app，实例重量级；real-device 基准（MobileBench-OL）覆盖 everyday apps 但面临账号问题、后端状态漂移、真实后果风险和高维护成本。两者都无法同时提供 verifiable outcome signals + scalable online RL training。

Everyday apps 的核心障碍：
- **Unreadable**：余额、订单等内部状态难以通过 adb 和 accessibility tree 检查
- **Unwritable**：任务相关状态分散在私有存储、缓存和远程服务
- **Unforkable**：GRPO 等 group-based RL 方法需要从相同初始状态发起多个 rollouts
- **Irreversible**：操作可能发送真实消息、转账或导致永久账户变更

核心洞察：GUI agent 只观察 screenshot 并执行离散操作，轻量级仿真器只要实现**交互保真度**（interaction fidelity）而非复制专有后端。

## Method

**核心设计：Interaction fidelity 而非 pixel-perfect 渲染**

MobileGym 在浏览器中运行 Android-like 运行时，将 app 数据、OS 状态和设备上下文表示为结构化 JSON。每个浏览器实例 ~400 MB RAM，~3s 冷启动，单机可运行数百并行实例。

**Layered state model（三层分离）**：
- **World data**：大型只读数据（posts、products 等公开实体）
- **Runtime state**：可变的 per-environment 状态（agent 操作写入层）
- **OS runtime state**：操作系统运行时状态

Agent 只向 runtime state 写入。视图通过在只读 world data 上叠加 runtime state 生成。只有 runtime state 用于配置、重置、judging 和比较。

**Declarative navigation specification（EFSM）**：
每个 app 的 UI 导航建模为声明式有限状态机，形式化为 ℳ=(S,Σ,Δ,s₀,D,G,U)，其中 S=UI 状态、Σ=用户动作、Δ=转移函数（带 guards 和 updates）、D=应用状态变量、G=guards、U=update 操作。同一规范文件驱动运行时导航、静态分析、任务轨迹枚举和新任务自动生成。

**AnswerSheet protocol**：
查询任务以 agent 填写 AnswerSheet 表单结束，字段声明类型并显示格式提示。提交的 typed state 由类型特定匹配器检查（精确文本、数字容差、格式或选择检查），取代脆弱的自由文本匹配。

**State forking**：全环境状态序列化为 JSON 并按需恢复，实现精确重置和从任意快照 fork。对不可逆操作，后果-free 仿真在每个 trajectory 后完全恢复。

**17-action unified abstraction**：tap, long_press, swipe, text input, key events (back, home, recent), scroll, system controls。

**开发成本**：每个 everyday app ~3-4 人天，每个系统 app ~1 人天，28 个 app 共 ~60 人天。

## Key Results

**Benchmark 结果（256 test tasks，9 个 agent）**：

| Model | Overall SR | PR | L1 (n=20) | L2 (n=73) | L3 (n=83) | L4 (n=80) | USE |
|---|---|---|---|---|---|---|---|
| Gemini 3.1 Pro | **58.8** | 72.1 | 97.5 | 83.6 | 63.3 | **21.9** | 5.5 |
| Doubao-Seed-2.0-Pro | 52.0 | 63.6 | 100.0 | 93.2 | 48.2 | 6.2 | 4.7 |
| Qwen3.6-Plus | 45.7 | 59.2 | 100.0 | 78.1 | 44.6 | 3.8 | 14.5 |
| AutoGLM-Phone-9B | 20.0 | 35.3 | 86.2 | 33.6 | 9.6 | 1.9 | 12.6 |
| UI-TARS-1.5-8B | 13.8 | 26.3 | 77.5 | 21.9 | 3.0 | 1.6 | 11.0 |
| UI-Venus-1.5-8B | 15.4 | 28.3 | 85.0 | 21.9 | 6.0 | 1.9 | 7.7 |
| GUI-Owl-1.5-8B-Think | 15.1 | 28.8 | 76.2 | 26.0 | 4.2 | 1.2 | 14.1 |
| Step-GUI-4B | 12.9 | 25.7 | 83.8 | 17.8 | 2.4 | 1.6 | 7.6 |
| Qwen3-VL-4B-Instruct | 9.4 | 20.1 | 71.2 | 12.3 | 0.6 | 0.3 | 10.0 |

关键发现：
- L4 是 frontier discriminator：只有 Gemini 3.1 Pro 保持有意义的 21.9%，其他均 ≤6.2%
- USE (Unexpected Side Effects) 4.7%-14.5%，与能力不简单相关——即使 SR 相近（12.9%-15.4%），USE 也相差近 2 倍（7.6%-14.1%）
- False Complete (FC) 高达 22.9%-39.6%，说明 agent 频繁误判完成

**Sim-to-Real Transfer（GRPO 训练）**：
- 训练配置：Qwen3-VL-4B-Instruct + GRPO，160-task train set，10 steps，lr=10⁻⁶，group size k=8，batch size=12，KL 0.01，DAPO-style asymmetric clip（0.2/0.28）
- 仿真侧提升：Overall SR 9.4%→22.2%（**+12.8pp**）；L1: 71.2%→92.5%，L2: 12.3%→37.7%，L3: 0.6%→11.7%，L4: 0.3%→1.2%
- 真实设备（Redmi Note 12 Turbo，59-task 信号子集）：Pass rate 32.2%→72.9%（+40.7pt）；仿真侧 33.9%→76.7%（+42.8pt）；**95.1% retained gain**

**效率对比**：

| Platform | Memory/instance | Disk | Cold start |
|---|---|---|---|
| AndroidWorld (Emulator) | ~4.5 GB | ~20 GB | ~78s |
| AndroidLab (Emulator) | ~6 GB | ~9 GB | — |
| **MobileGym (Browser)** | **~400 MB** | **~50 MB** | **~3s** |

256 并行实例 <10% CPU，~100 GB RAM，完整评测 ~6 分钟。

**VLM Judge Error Analysis**：118 个 signal-bucket trajectories 中，Qwen3.6-Plus 有 12 个判断错误（10.2%）。程序化 state verification 完全避免了这个 failure mode。

## Strengths & Weaknesses

**Strengths**：
- **95.1% sim-to-real retention**：这是本批论文中最有说服力的数字，说明 functional modeling 方向正确——pixel-perfect 渲染对 everyday app 交互是 over-engineering，JSON state 足够抓住交互本质
- **State-based judging 的简洁性**：程序化验证比 VLM judge 更可靠（10.2% error rate vs 0），且提供 dense reward signal
- **资源效率革命**：1/10 内存、1/100 磁盘，相比 emulator 方案是数量级改进
- **开发成本可控**：60 人天 28 个 app 是可接受的工程投入

**Weaknesses**：
- **Functional coverage 的边界不清晰**：每个 app 只实现 main everyday-use scenarios，less common features 处于 scope 之外；具体哪些真实世界复杂性被丢失了？
- **Backend/dynamic content modeling 的局限**：Server-driven content（ads、pop-ups、推荐 feed、实时消息）表示为可控 JSON state，不捕获随机现象如 live recommendation dynamics、fraud checks 或 latency spikes
- **高风险任务无 explicit refusal**：Gemini 3.1 Pro 在 Payment 任务上达 64.3%，open-source specialists ≤10.7%，但两者都没有 explicit refusal——只报告了执行能力而非 endorsement
- **任务模板的构建成本**：416 个参数化模板的手工设计成本没说清楚，这限制了对可扩展性的判断

**Impact**：为 mobile GUI agent 的 online RL 训练提供了第一个真正可行的基础设施。Sim-to-real 95.1% retention 是关键数字——它证明了 functional modeling 路径的可行性，而非追求 pixel-perfect 渲染。

## Mind Map

```mermaid
mindmap
  root((MobileGym))
    Problem
      Emulator可重复但只覆盖开源app
      Real-device覆盖日常app但不可控
      无法同时满足verifiable+parallel RL
    Method
      Browser-hosted Android-like OS
      JSON state三层分离(World/Runtime/OS)
      Declarative EFSM导航规范
      AnswerSheet protocol
      State forking支持GRPO
      17-action unified abstraction
    Results
      9 agents: 9.4%-58.8% SR
      GRPO +12.8pp(仿真)/+40.7pp(真机)
      95.1% sim-to-real retention
      ~400MB 3s startup 10x资源效率
      L4 frontier discriminator
      USE 4.7%-14.5%
```
