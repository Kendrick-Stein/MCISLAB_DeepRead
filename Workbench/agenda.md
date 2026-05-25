---
last_updated: "2026-05-19"
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
- **evidence**: [[Topics/GUIAgent-Survey]], [[Papers/2604-GoClick]], [[Ideas/ScaleInvariant-Grounding-GUI]], [[2500-GuiActorCoordinateFree]], [[Papers/2604-AutoGUIv2]] (dichotomy: fine-tuned grounding 强于通用 VLM), [[Papers/2604-WindowsWorld]] (跨应用是独立瓶颈 L1 46% vs L2 14%，grounding 能力比 reasoning 更关键), [[Papers/2605-WorkspaceBench]] (Heterogeneous File Understanding 和 Lineage Tracing 是 workspace agent 瓶颈，最佳 agent 68.7% vs 人类 80.7%，说明 grounding 在复杂环境中仍有显著提升空间)
- **next_action**: 实验已重设计为 GUI-Actor baseline（Experiments/2026-04-29-ScaleInvariantGroundingGUI 已更新），下一步：原型验证 FPN + multi-resolution training 在 ScreenSpot-Pro 上的效果
- **confidence**: 0.45 (↑ from 0.4，WorkspaceBench 的 74 file types + 20K files 场景下 grounding 瓶颈进一步验证方向重要性)

### RL-based GUI Agent Training

- **priority**: medium
- **status**: exploring
- **origin**: researcher-discovered
- **hypothesis**: Rule-based RL（GRPO 风格）配合结构化 action reward，可以以 10x 更少的训练数据达到或超越 SFT 的 GUI action prediction 性能，且 OOD 泛化更强
- **evidence**: [[Topics/GUIAgent-Survey]], [[2500-UiR1EnhancingEfficient]], [[Papers/2604-ClawGUI]], [[2025-MobileRL- Online Agentic Reinforcement Learning for Mobile GUI Agents]], [[Ideas/ForkPoint-CreditAssignment-GUI]], [[Papers/2604-AutoGUIv2]] (fine-tuning on agent data 对 grounding 有显著增益), [[Papers/2604-SOLAR-RL]] (first failure point detection, 3-stage reward shaping), [[Papers/2602-ProxMO]] (PSC+PSA, 90.6% ALFWorld, state similarity credit assignment), [[Papers/2605-DUDE]] (asymmetric reward ω=10 for deception, hybrid-reward learning 减少 53.8% 欺骗易感性), [[Papers/2605-Skill1]] (unified skill selection/utilization/distillation via single policy, reward signal frequency decomposition for credit assignment)
- **next_action**: ForkPoint 方向已评估 10/25（ProxMO PSA 概念重叠），建议暂停 credit assignment 子方向，转向 rule-based reward design（更底层、更少竞争）；DUDE 的 asymmetric penalty 和 Skill1 的 frequency-based credit assignment 提供了 reward design 的新视角；需要 Supervisor 决策是否完全放弃 credit assignment
- **confidence**: 0.35 (↑ from 0.3，DUDE asymmetric reward + Skill1 frequency decomposition 为 reward design 提供新思路)

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

### SGV 论文来源 — 2026-05-07

- **raised_by**: autoresearch
- **context**: Self-Improving direction next_action 指向"阅读 SGV (Self-Grounded Verification) 论文"。Vault 中 DomainMap 提到 SGV "20pp OSWorld 提升"，但无具体 paper URL 或 arxiv ID。Web search 未返回匹配结果。UI-Genie 论文已消化，未提及 SGV 论文。
- **question**: 请提供 SGV (Self-Grounded Verification) 论文的 arxiv URL 或完整标题。如果该论文未公开发表或名称不同，请告知正确来源。
- **related_direction**: Self-Improving Agent Reliability

### Autoresearch 推进受阻 — 2026-05-19

- **raised_by**: autoresearch
- **context**: Round 2 检测到所有 active directions 均被阻塞：(1) GUI Grounding Robustness 的 next_action 是"原型验证 FPN + multi-resolution training"（需实验实现，超出 autoresearch scope）；(2) RL-based GUI Agent Training 的 next_action 需要"Supervisor 决策是否完全放弃 credit assignment"；(3) Self-Improving Agent Reliability 需要 SGV 论文 URL。同时，Queue 中有 32 个 pending papers（多为 daily-papers 产生的 summarize_paper 任务），但 WebFetch 被网络限制阻塞，无法执行 paper-digest。
- **question**: 请提供以下任一指导以解除阻塞：(1) 提供可访问的论文 PDF 或替代获取方式（绕过 WebFetch 限制）；(2) 决策 RL Training 方向是否放弃 credit assignment 转向 rule-based reward design；(3) 提供 SGV 论文来源；(4) 指示 GUI Grounding 实验实现的优先级（是否应作为 autoresearch 的行动项）。
- **related_direction**: 所有 active directions
