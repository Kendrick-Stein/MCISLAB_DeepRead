---
last_updated: "2026-05-06"
updated_by: agenda-evolve
active_topic: GUI Agent
---

## Mission

构建能够可靠理解、定位和操作图形用户界面的视觉 Agent 系统，重点关注 grounding robustness、高效训练范式（RL vs SFT）、以及 self-improving 系统的可靠性保障。长期目标是让 GUI Agent 在跨平台、跨分辨率、动态变化的真实界面中稳定执行长程任务。

---

## Active Directions

### GUI Grounding Robustness

- **priority**: high
- **status**: exploring
- **origin**: researcher-discovered
- **hypothesis**: 架构级 multi-scale 设计（FPN + multi-resolution training + consistency loss）可以在不增加推理开销的前提下，显著提升 GUI grounding 在跨分辨率/跨设备场景下的鲁棒性
- **evidence**: [[Topics/GUIAgent-Survey]], [[Papers/2604-GoClick]], [[Ideas/ScaleInvariant-Grounding-GUI]], [[2500-GuiActorCoordinateFree]], [[Papers/2604-AutoGUIv2]] (dichotomy: fine-tuned grounding 强于通用 VLM)
- **next_action**: 原型验证——GoClick 代码未公开（阻塞），需寻找替代方案：(1) 用 GUI-Actor (microsoft/GUI-Actor-2B-Qwen2-VL, 有开源代码) 作为 baseline 添加 FPN，或 (2) 从零搭建轻量 encoder-decoder grounding 模型。同时 MEGA-GUI 已读，Qwen-GUI-3B 非公开论文（实为 OpenCSG fine-tuned model，无 paper）
- **confidence**: 0.35 (↑ from 0.3，AutoGUI-v2 dichotomy 证明 grounding 作为专门训练能力的价值)

### RL-based GUI Agent Training

- **priority**: medium
- **status**: exploring
- **origin**: researcher-discovered
- **hypothesis**: Rule-based RL（GRPO 风格）配合结构化 action reward，可以以 10x 更少的训练数据达到或超越 SFT 的 GUI action prediction 性能，且 OOD 泛化更强
- **evidence**: [[Topics/GUIAgent-Survey]], [[2500-UiR1EnhancingEfficient]], [[Papers/2604-ClawGUI]], [[2025-MobileRL- Online Agentic Reinforcement Learning for Mobile GUI Agents]], [[Ideas/ForkPoint-CreditAssignment-GUI]], [[Papers/2604-AutoGUIv2]] (fine-tuning on agent data 对 grounding 有显著增益), [[Papers/2604-SOLAR-RL]] (first failure point detection, 3-stage reward shaping), [[Papers/2602-ProxMO]] (PSC+PSA, 90.6% ALFWorld, state similarity credit assignment)
- **next_action**: ForkPoint 方向已评估 10/25（ProxMO PSA 概念重叠），建议暂停 credit assignment 子方向，转向 rule-based reward design（更底层、更少竞争）；需要 Supervisor 决策是否完全放弃 credit assignment
- **confidence**: 0.3 (unchanged)

### Self-Improving Agent Reliability

- **priority**: low
- **status**: exploring
- **origin**: researcher-discovered
- **hypothesis**: Self-improving GUI Agent 的自增强循环中存在系统性验证偏差，需要外部纠错机制（adversarial verifier 或 self-grounded verification）防止偏差放大
- **evidence**: [[Topics/GUIAgent-Survey]], [[2500-UiGenieSelfImproving]], [[Ideas/AdversarialVerification-SelfImproving-GUI]]
- **next_action**: 阅读 SGV (Self-Grounded Verification) 论文，了解当前 state-of-the-art 的 verification debiasing 方法；监控该方向进展，暂不作为主攻方向
- **confidence**: 0.15

---

## Paused Directions

（暂无）

---

## Abandoned Directions

（暂无）

---

## Discussion Topics

### GUI Agent 研究方向优先级确认 — 2026-04-28

- **raised_by**: agenda-evolve
- **context**: 今日完成 GUI Agent 全面 survey（190 篇论文）、memory-distill（4 个新 pattern）、3 个 idea 生成与评估。Grounding Robustness (16/25) 评分最高，Credit Assignment 方向被 WebSearch 发现极拥挤（5+ concurrent works），Adversarial Verification 风险最高 (11/25)
- **question**: 当前以 GUI Grounding Robustness 为 primary direction、RL Training 为 secondary、Self-Improving 为 monitoring 的优先级分配是否合理？是否需要调整？
- **related_direction**: GUI Grounding Robustness, RL-based GUI Agent Training, Self-Improving Agent Reliability

### Credit Assignment 方向是否继续 — 2026-05-06 更新

- **raised_by**: agenda-evolve
- **context**: SOLAR-RL 和 ProxMO 已读完。ForkPoint 评估从 12/25 降至 10/25——ProxMO 的 PSA (TF-IDF state similarity → soft baseline) 概念上与 ForkPoint 的 state change detection 高度重叠，SOLAR-RL 的 first failure point detection 本质就是 fork point detection。Credit assignment 赛道已有 6+ concurrent works (SOLAR-RL, GiGPO, ProxMO, ADMIRE, DAPO, GUI-Shepherd)
- **question**: 建议暂停 credit assignment 子方向，转向 rule-based reward design（更底层、更少竞争的 RL 子方向）。是否同意？或者是否有 credit assignment 的独特角度（如 GUI-specific visual state similarity）值得继续探索？
- **related_direction**: RL-based GUI Agent Training
