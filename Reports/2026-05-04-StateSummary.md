---
date: 2026-05-04
type: state-summary
tags: [report, gui-agent, research-direction]
---
# 研究方向状态汇总

## 概览

截至 2026-05-04，GUI Agent 研究方向的三个 active direction 状态如下：

| Direction | Priority | Status | Confidence | Key Evidence |
|:----------|:---------|:-------|:-----------|:-------------|
| GUI Grounding Robustness | high | exploring | 0.35 ↑ | AutoGUI-v2 dichotomy + GoClick baseline + FPN hypothesis |
| RL-based GUI Agent Training | medium | exploring | 0.3 ↑ | UI-R1/ClawGUI rule-based RL + fine-tuning value |
| Self-Improving Agent Reliability | low | exploring | 0.15 | UI-Genie RM + SGV pending |

---

## Direction 1: GUI Grounding Robustness (Primary)

### Hypothesis
架构级 multi-scale 设计（FPN + multi-resolution training + consistency loss）可以在不增加推理开销的前提下，显著提升 GUI grounding 在跨分辨率/跨设备场景下的鲁棒性。

### Evidence Strength
- **AutoGUI-v2 dichotomy**：开源模型（Qwen3-VL）在功能性 grounding 上超越商业模型 → grounding 作为专门训练能力有显著价值
- **GoClick baseline**：230M encoder-decoder 达大模型精度，证明专门架构可行
- **GUI-Actor coordinate-free**：patch-level attention优于text-coordinate生成
- **ScreenSpot-Pro OOD**：跨分辨率 grounding 是 documented bottleneck

### Confidence Evolution
- 2026-04-28: 0.3（基于 survey + idea evaluation）
- 2026-05-04: 0.35 ↑（AutoGUI-v2 dichotomy 强化证据）

### Next Action
原型验证——在 GoClick encoder-decoder 架构上添加 FPN，在 ScreenSpot 多分辨率子集上测试 cross-resolution grounding accuracy

### Blocking Issues
- 需要代码实现 + GPU 环境
- Qwen-GUI-3B / MEGA-GUI baseline 论文未消化（WebSearch 失败）

### Idea Status
- [[Ideas/ScaleInvariant-Grounding-GUI]]: developing, evaluation 16/25
- Experiment [[Experiments/2026-04-29-ScaleInvariantGroundingGUI]]: planned, not started

---

## Direction 2: RL-based GUI Agent Training (Secondary)

### Hypothesis
Rule-based RL（GRPO 风格）配合结构化 action reward，可以以 10x 更少的训练数据达到或超越 SFT 的 GUI action prediction 性能。

### Evidence Strength
- **UI-R1**: 136 tasks + rule-based reward → ScreenSpot +22.1%
- **ClawGUI**: GiGPO + PRM → MobileWorld 17.1% SR (+6 abs)
- **MobileRL**: ADAGRPO → AndroidWorld 80.2%
- **AutoGUI-v2**: fine-tuning on agent data 对 grounding 有显著增益

### Confidence Evolution
- 2026-04-28: 0.25（基于 survey + crowded field awareness）
- 2026-05-04: 0.3 ↑（AutoGUI-v2 dichotomy 支持 fine-tuning value）

### Next Action
阅读 SOLAR-RL 和 ProxMO 确认差异化空间；若 ForkPoint 方向被证伪，转向 rule-based reward design

### Blocking Issues
- Credit Assignment 方向极度拥挤（SOLAR-RL, GiGPO, ProxMO, ADMIRE 等 5+ concurrent works）
- 需要确认差异化空间

### Idea Status
- [[Ideas/ForkPoint-CreditAssignment-GUI]]: developing, evaluation 12/25（lowest score）

---

## Direction 3: Self-Improving Agent Reliability (Monitoring)

### Hypothesis
Self-improving GUI Agent 的自增强循环中存在系统性验证偏差，需要外部纠错机制防止偏差放大。

### Evidence Strength
- **UI-Genie**: RM 作为 verifier，但 RM 本身可能有偏差
- **UI-Mem**: hierarchical experience memory，template-based abstraction 可能固化错误
- **Pattern observation**: "自增强过程可能放大系统性偏差"

### Confidence Evolution
- 2026-04-28: 0.15（基于 survey + risk assessment）
- 2026-05-04: 0.15（无新证据）

### Next Action
阅读 SGV (Self-Grounded Verification) 论文，了解 verification debiasing SOTA

### Blocking Issues
- Low priority，暂不作为主攻方向

### Idea Status
- [[Ideas/AdversarialVerification-SelfImproving-GUI]]: developing, evaluation 11/25（high risk）

---

## Validated Insights

### [2026-05-03] GUI Agent evaluation shifting from binary success to process-level diagnosis
- **confidence**: medium ↑（AutoGUI-v2 dichotomy + failure mode 分析强化）
- **status**: validated ↑
- **impact**: Benchmark design, model selection

### [2026-05-04] VLM grounding vs captioning capability dichotomy
- **claim**: 开源 grounding 强，商业 captioning 强
- **confidence**: medium
- **status**: provisional
- **impact**: Model selection for GUI Agent tasks

---

## Patterns Observed

1. **Latent-space agent communication**: 75%+ token reduction (RecursiveMAS)
2. **Production deployment cost bottleneck**: Step-level cascade 74.6% cost reduction
3. **Workflow automation <70% success**: Claw-Eval-Live 66.7%, Odysseys 44.5%

---

## Discussion Topics (Awaiting Supervisor Decision)

### 1. GUI Agent 研究方向优先级确认
- **Question**: 当前优先级分配是否合理？是否需要调整？
- **Options**:
  - A) 保持当前优先级（Grounding primary, RL secondary, Self-Improving monitoring）
  - B) RL Training 提升 primary（rule-based reward design 更底层，拥挤但重要）
  - C) 新增 direction（如 Production Deployment Cost）

### 2. Credit Assignment 方向是否继续
- **Question**: ForkPoint idea 12/25 + crowded field → 继续或转向？
- **Options**:
  - A) 继续投入（先读完 SOLAR-RL/ProxMO 确认差异化）
  - B) 转向 rule-based reward design（更底层，更少竞争）
  - C) 暂停（等待 field consolidation）

---

## Knowledge Base Stats

| Category | Count | Last Updated |
|:---------|:------|:-------------|
| Papers | 70+ | 2026-05-04 (AutoGUI-v2) |
| Topics/Surveys | 13 | 2026-05-04 (GUIAgent-Survey) |
| Ideas | 3 (developing) | 2026-04-28 |
| Experiments | 1 (planned) | 2026-04-29 |
| Insights | 2 (validated/provisional) | 2026-05-04 |
| Patterns | 3 | 2026-05-03 |

---

## Recommended Next Actions

### For Supervisor
1. 决策 Discussion Topics 优先级
2. 如需推进 Grounding 实验，配置 GPU 环境

### For Researcher
1. 消化 Qwen-GUI-3B / MEGA-GUI（cross-resolution baseline）
2. 阅读 SOLAR-RL / ProxMO 确认 RL 方向差异化空间
3. 阅读 SGV 论文更新 Self-Improving direction
4. 等待 Supervisor 优先级决策

---

## Appendix: Recent Daily Papers (2026-05-03)

| Rating | Papers |
|:-------|:-------|
| 🔥 3 | RecursiveMAS, Claude Code Architecture, OpenGame, LaST-R1, IVLR |
| 👀 2 | Tuna-2, World-R1, Agentic World Model Survey, ClawGUI |

See [[Workbench/daily/2026-05-03]] for full review.