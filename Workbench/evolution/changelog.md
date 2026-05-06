# Evolution Changelog

> Record of Domain Map updates and system evolution.

---

## 2026-04-28

- **System restructured**: Aligned with MindFlow architecture. Removed Python engine/infrastructure code. Flattened vault structure (Papers, Topics, Ideas, DomainMaps, Reports moved to root). Added references/, Projects/, evolution/.

### [2026-04-28] memory-distill

- **period**: 2026-04-21 ~ 2026-04-28
- **logs_processed**: 2
- **new_patterns**: 4
- **promoted_to_insight**: 0 (L1 → L2)
- **validated_insights**: 0 (L2 → L3)
- **queued_for_review**: 0 (L3 → L4 候选)

### [2026-04-28] agenda-evolve

- **trigger**: autoresearch 第 6 轮——survey/ideas/memory 全部完成但 agenda 为空 stub，需结构化
- **insights_reviewed**: 0（无 validated insight）
- **directions_added**: 3（GUI Grounding Robustness, RL-based GUI Agent Training, Self-Improving Agent Reliability）
- **directions_updated**: 0
- **directions_paused**: 0
- **directions_abandoned**: 0
- **reasoning**: 基于今日 survey（190 篇论文 + 6 条技术路线）、3 个 idea 评估（16/25, 12/25, 11/25）、4 个新 pattern，将 GUI Agent 研究组织为三个层级的方向：Grounding（high priority，基础瓶颈 + 最高评分 idea）、RL Training（medium priority，拥挤但重要的赛道）、Self-Improving Reliability（low priority，monitoring 模式）。添加 2 个 Discussion Topic 供 Supervisor 确认优先级。

## 2026-05-03

### [2026-05-03] memory-distill

- **period**: 2026-04-28 ~ 2026-05-03
- **logs_processed**: 4
- **new_patterns**: 3（latent-space agent communication, production deployment cost bottleneck, workflow automation <70% success rate）
- **promoted_to_insight**: 1 (L1 → L2) — evaluation methodology shift 获第3次独立来源
- **validated_insights**: 0 (L2 → L3)
- **queued_for_review**: 0 (L3 → L4 候选)

## 2026-05-04

### [2026-05-04] agenda-evolve

- **trigger**: autoresearch Round 4——新 validated insight（evaluation shift）+ provisional insight（VLM dichotomy）需反映到 agenda
- **insights_reviewed**: 2（evaluation shift validated, VLM dichotomy provisional）
- **directions_added**: 0
- **directions_updated**: 2（GUI Grounding Robustness + RL-based GUI Agent Training，添加 AutoGUI-v2 evidence）
- **directions_paused**: 0
- **directions_abandoned**: 0
- **reasoning**: AutoGUI-v2 dichotomy 发现（开源 grounding 强，商业 captioning 强）支持两个现有 direction：grounding 作为专门训练能力的价值，fine-tuning on agent data 的增益。更新 evidence + confidence 微调（0.3→0.35, 0.25→0.3）。Dichotomy 是 model selection 指南而非研究 hypothesis，不新增 direction。

## 2026-05-06

### [2026-05-06] agenda-evolve

- **trigger**: autoresearch Round 3——SOLAR-RL + ProxMO 已读完，ForkPoint 从 12/25 降至 10/25，RL direction next_action 完成需更新
- **insights_reviewed**: 2（evaluation shift validated, VLM dichotomy provisional）
- **directions_added**: 0
- **directions_updated**: 2（RL-based GUI Agent Training: 更新 next_action + evidence；GUI Grounding Robustness: 更新 next_action 标注 GoClick 代码阻塞）
- **directions_paused**: 0
- **directions_abandoned**: 0
- **reasoning**: ProxMO 的 PSA (TF-IDF state similarity → soft baseline) 概念上与 ForkPoint 的 state change detection 高度重叠，SOLAR-RL 的 first failure point detection 本质就是 fork point detection。Credit assignment 赛道已有 6+ concurrent works。建议暂停 credit assignment 子方向，转向 rule-based reward design。Grounding direction 因 GoClick 代码未公开被阻塞，需寻找 GUI-Actor 等替代 baseline。
