---
title: World Model Survey
tags: [world-model, agent, simulation, planning, MBRL]
date_updated: "2026-04-28"
year_range: 2024-2026
papers_analyzed: 12
---
## Overview

World Model 是 AI Agent 的环境建模能力——预测行动后果、模拟状态转移、支持 counterfactual planning。从 MBRL 的 transition model 到 Video Generation 的 action-conditioned prediction，再到 GUI/Web Agent 的 environment simulator，不同社区对"world model"有不同理解。

**核心洞察**：[[2604-AgenticWorldModel]] Survey 提出的 "Levels × Laws" taxonomy 是当前最系统的框架：
- **能力层级**：L1 Predictor（单步转移）→ L2 Simulator（多步 rollout）→ L3 Evolver（自主修正）
- **约束域**：Physical（物理定律）/ Digital（软件逻辑）/ Social（社会规则）/ Scientific（科学规律）

**整体趋势**（2024-2026）：
1. Engineering-heavy，insight-light。HybridMemory、MultiWorld、GenerativeWorldRenderer 都是工程整合，缺少改变问题 formulation 的核心 idea
2. 唯一亮点是 SpatialEvo 的 DGE 设计——用确定性几何替代 model voting
3. Agentic RL 的 failure mode 诊断（如 RAGEN-2 template collapse）开始受关注
4. L3 Evolver 层级仍是 open problem——现有系统无法自主修正模型

## 技术路线

### 1. Video World Model (主流)

**代表工作**：
- [[2604-MultiWorld]]：Multi-agent multi-view video world model，用 MACM + GSE 保证多视角一致性
- [[2604-HYWorld2]]：多模态到 3D 世界的流水线（HY-Pano → WorldNav → WorldStereo → WorldMirror）
- [[2603-HybridMemory]]：动态主体出画再入画的 memory 机制，用 HyDRA 压缩 memory latent

**核心思路**：用 video generation 技术预测 action-conditioned future frames

**优势**：
- 视觉直观，支持 agent 训练和 evaluation
- 可用于 synthetic data generation

**劣势**：
- 像素级预测噪声大，长期 rollout 误差累积
- 缺少底层逻辑/物理建模
- 实验闭环往往封闭（如 HybridMemory 只在 UE5 数据上验证）

### 2. Deterministic Geometric Environment (突破点)

**代表工作**：[[2604-SpatialEvo]] (🔥 Rating 3)

**核心思路**：3D 空间推理的答案可以从点云和 camera pose 确定性计算，不需要 model voting

**关键发现**：
- w/o Physical Grounding → VSI-Bench 从 46.1 暴跌到 18.8（27+差距）
- DGE 提供"零噪声"奖励信号，支持 GRPO self-evolving

**优势**：
- 确定性答案，无 model voting 噪声
- 支持 self-evolving curriculum

**劣势**：
- 适用边界极窄：只能跑 ScanNet 类室内静态场景
- 第一阶段 entity parsing 仍依赖 LLM（噪声只是被转移）

### 3. Environment Synthesis (工程方向)

**代表工作**：
- [[2604-AgentWorld]]：1,978 环境 / 19,822 工具，从 MCP servers + PRD 采集
- [[2604-GenerativeWorldRenderer]]：4M 帧 RGB+G-buffer 数据集，从游戏截取
- [[2604-OpenWorldLib]]：统一 inference framework（Library Paper，Rating 1）

**核心思路**：大规模采集 + 合成环境

**优势**：
- 工程量大，数据有价值
- Agent-World 的 scaling 曲线清晰（+20.1pt）

**劣势**：
- Agent-World 的 "Real-World" 水分大——本质是 JSON/CSV 本地读写
- MCP-Mark 绝对分数低（8B 8.9%，14B 13.3%）
- GenerativeWorldRenderer 只是 dataset paper

### 4. UI/GUI World Model

**代表工作**：
- [[2600-MobiledreamerGenerativeSketchWorld]]：文本草图世界模型 + 回滚想象策略，+5.25% AndroidWorld
- [[2500-UisimInteractiveImageBased]]：两阶段 UI simulator（layout prediction → layout-to-image）

**核心思路**：预测 UI 状态转移，支持 agent planning

**优势**：
- 直接服务于 GUI Agent
- UISim 的 layout-first 设计符合 UI 结构化本质

**劣势**：
- UISim 图像式模拟器缺少真实系统状态（网络请求、权限弹窗等）
- MobileDreamer 的 sketch world model 精度有限

### 5. Conceptual Framework (Survey)

**代表工作**：
- [[2604-AgenticWorldModel]]：Levels × Laws taxonomy（🔥 Rating 5，最系统的 Survey）
- [[2604-Externalization]]：Memory/Skills/Protocols/Harness 四组件框架（Rating 2，54 页讲一句话）

## Datasets & Benchmarks

| Dataset | 规模 | 评估指标 | SOTA | 特点 |
|:--------|:-----|:---------|:-----|:-----|
| HM-World | 59K 视频 | Subject Consistency, Background Consistency | HyDRA 0.926/0.932 | UE5 渲染，exit-entry 场景 |
| Agent-World | 1,978 环境 / 19,822 工具 | MCP-Mark | 14B 13.3% | MCP servers + PRD 采集 |
| GenerativeWorldRenderer | 4M 帧 RGB+G-buffer | FID, LPIPS | DiffusionRenderer | 游戏截取 |
| VSI-Bench | - | Spatial Reasoning | SpatialEvo 46.1 | 3D 空间推理 |
| ItTakesTwo | 多人游戏 | FVD, PSNR | MultiWorld | Multi-agent gaming |
| RoboFactory | 多机械臂 | Action Accuracy | Concat-View 92.0 | Robot manipulation |

## Key Takeaways

1. **SpatialEvo 的 DGE 是唯一真正的 insight**——确定性几何替代 model voting，但适用场景极窄
2. **L3 Evolver 层级仍是 open problem**——现有 world model 无法自主修正
3. **Video World Model 的 memory 机制有问题**——HybridMemory 发现动态主体出画再入画会消失/扭曲
4. **Agent-World 的 environment scaling 有价值**，但 MCP-Mark 绝对分数暴露问题
5. **UI World Model 的 layout-first 设计是对的**——UISim 的 decomposition 符合 UI 结构化本质

## Open Problems

1. **L3 Evolver 实现**：当 prediction 失败时如何自主修正模型？
2. **World Model 的 failure mode 系统性分析**：RAGEN-2 发现 template collapse，但其他 failure mode 未知
3. **Video World Model 的误差累积**：长期 rollout 如何保持 fidelity？
4. **Deterministic vs Probabilistic 的 trade-off**：DGE 适用边界如何扩展？
5. **Real-World vs Synthetic 的 gap**：Agent-World 的 JSON/CSV 环境离真实 web/app 差多远？
6. **World Model for GUI Agent 的 grounding 问题**：如何与 grounding robustness 结合？

## 调研日志

- **调研日期**: 2026-04-28
- **论文统计**: vault 已有 4 篇（Archive）+ 2 篇（Papers）+ 新创建 6 篇 + Survey 1 篇
- **未能获取**: 无（基于已有月度总结创建笔记）