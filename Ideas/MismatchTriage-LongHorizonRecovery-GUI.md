---
title: "Recovery-Selection Gap：GUI Agent 的固定恢复策略留下多少可收回的成功率"
tags: [gui-agent, computer-use, research-idea]
status: raw
linked_project:
date_updated: "2026-07-20"
---
## Hypothesis

GUI agent 检测到"执行结果与预期不符"（mismatch）后，现有方法的恢复行为是固定的（重试或回退一步）。假设：**最优恢复动作随 mismatch 点而变，固定策略因此留下可测量的成功率差距（recovery-selection gap）**。

该假设不依赖任何错误分类学。可证伪预测：

- 用 emulator 快照在每个 mismatch 点分叉执行全部候选恢复动作，逐点最优选择（oracle）与最强固定策略之间的任务成功率差距 ≥8pp；
- 一个运行时 selector（prompted 起步，分叉数据可供训练）能收回该差距的 ≥50%；
- **Kill criterion**：若某单一恢复动作在 ≥85% 的 mismatch 点上属于最优集合，则固定恢复已足够，假设证伪——差距测量本身作为负结果报告。

候选恢复动作集（有限动作空间，非分类学）：① 原样重试；② 重新定位目标后重试；③ 等待后重新截屏、继续原计划；④ 关闭当前浮层、继续原计划；⑤ 回退上一屏；⑥ 重读当前页面、更新任务状态记录后重新决策。

## Motivation

**问题是测出来的，不是想象的**。已发表数据表明固定恢复会造成净损害：[[Papers/2505-BacktrackAgent]]（EMNLP 2025 oral）中 0.78% 本来正确的动作被恢复机制改错（检测 precision 75.12%），input 类动作回退重写后性能反而下降（IoU -1.60），真错的 8.48% 中仅救回 2.37%；[[Papers/2605-MobileWorldModelGUI]] 的 verification pollution 案例中，正确动作被判为失败并处以 -0.8 惩罚。恢复这一步在文献中始终是单一固定操作：[[Papers/2604-VeriGUI]] 统一 self-correction（其分布中仅存在"动作失败且屏幕不变"一种情形），[[Papers/2505-BacktrackAgent]] 固定回退一步，[[Papers/2607-TSR]] 的 verifier 只输出三值 action_effective 并施加软引导，LongHorizonUI（ICLR 2026）按感知降级分层回滚。**没有工作测量过"如果每个 mismatch 点都选对恢复动作，能多完成多少任务"**——这个量决定了恢复策略研究是否值得继续投入。

**方法论定位**：此前版本以"mismatch 原因三分类/五分类"为先验假设，Supervisor 指出该路线无终点——先验分类必须辩护完备性，且可无限细分。本版本将分类从假设降为输出：错误类型仅作为分析节出现，由"哪些恢复动作有效"对 mismatch 点做事后聚类得到，类别数量由数据决定。

**测量装置一套三用**：emulator 分叉结果同时是 (i) 问题存在性证明（gap 是测出的量），(ii) selector 的训练/校准数据，(iii) 评测协议（fixed / selector / oracle 三档对比）。

## Related Work

- [[Papers/2505-BacktrackAgent]] — 固定回退一步 + 双模块检测；其误伤数据（0.78% 改错、input 退化）是本 idea 的直接动机
- [[Papers/2604-VeriGUI]] — TVAE 自校验 + 统一 self-correction；Limitations 自认不覆盖 unintended navigation / partial transition 等复杂失败
- [[Papers/2605-MobileWorldModelGUI]] — verification pollution：恢复管线把正确行为惩罚成错误的实证案例
- [[Papers/2607-TSR]] — transition verifier 软引导恢复，无恢复动作选择
- [[Papers/2512-AgentProg]] — GBS 检测 Belief-Reality Gap 后触发固定 recovery routine（重开 app 重填），是候选动作⑥的现成实现参照
- [[Papers/2605-SaaSBench]] — checkpoint 43.9% vs resolved 3.8%：长程任务中错误累积是待解释的现象
- [[Ideas/ForkPoint-CreditAssignment-GUI]] — 共享 emulator 分叉基建；问题不同（训练期 credit assignment vs 运行期恢复选择）
- 外部（vault 暂无笔记）：LongHorizonUI（[ICLR 2026](https://openreview.net/forum?id=BK7Mk5d4WE)）— 感知降级分层回滚；VisCritic（[2606.24525](https://arxiv.org/pdf/2606.24525)）— 前后帧比对检测，无恢复选择

**Novelty**: 4/5 — closest works: [[Papers/2505-BacktrackAgent]], [[Papers/2604-VeriGUI]], LongHorizonUI（外部）。检测与单一恢复机制各有占坑者；"分叉测量 recovery-selection gap + 运行时恢复动作选择"无先例（2026-07-16 全文核查三篇对照确认均无归因或选择机制）。

## Approach sketch

1. **Mismatch 采集**：固定检测器（VeriGUI 式 no-change 检查 + prompted 前后帧比对），2 个 base agent 跑 AndroidWorld + AW-Extend 全部任务，记录每个 mismatch 点的 emulator 快照。预计 300–500 个点。
2. **分叉测量**：每点从快照并行执行 6 个候选恢复动作，各自续跑至任务结束（上限 15–20 步），记录成败。产出逐点的"有效恢复动作集合"。约 4 万步交互；8 并行 emulator 实例 1–2 天。
3. **Gap 计算**：oracle（逐点取最优）vs 6 个固定策略 vs 现有方法（BacktrackAgent 式固定回退、VeriGUI 式重试）。此步即 kill/go 决策点。
4. **Selector**：v1 prompted（输入：前后截图、预期效果、最近动作与状态记录；输出：动作 ①–⑥），在 held-out 任务上评测；若 prompted 选择准确率不足，v2 用分叉数据训轻量分类器。
5. **分析节（事后聚类）**：按有效恢复动作集合对 mismatch 点聚类，报告聚类结构与代表案例——错误"类型"在此作为发现陈述，不作为假设辩护。

## Expected outcome

- Oracle 与最强固定策略的 gap ≥8pp（AndroidWorld 尺度上足以区分 SOTA 排名）；
- Selector 收回 gap 的 ≥50%，且对 2 个 base agent 均成立；
- 聚类揭示 2–4 个行为可分的 mismatch 群（预期：需要等待/关浮层的环境干扰群 vs 需要重定位的执行错误群 vs 需要状态更新的过时群），与 BacktrackAgent 误伤案例、verification pollution 案例可对上号；
- 副产品：带分叉标签的 mismatch 数据集公开，供恢复策略研究复用。

## Risk

- **Gap 太小（kill criterion 触发）**：单一动作普遍最优 → 负结果照发，测量协议与数据集仍是贡献；这是最先出结果、成本最低的一步。
- **快照分叉的工程边界**：跨 app 状态（如网络侧写入）快照无法完全回滚。缓解：任务床限制在本地状态可回滚的 AndroidWorld 任务；受影响任务剔除并报告比例。
- **Mismatch 点偏采样**：检测器决定了哪些点被采集，检测器漏检的 mismatch 不在分布内。缓解：用两个独立检测器求并集，报告各自覆盖差异。
- **续跑方差**：分叉后续跑本身有随机性。缓解：每分叉重复 2–3 次取多数，成本已计入估算。

## Evaluation — 2026-07-16 (Supervisor 讨论后第三版)

| Dimension | Score | Notes |
|:----------|:-----:|:------|
| Novelty | 4/5 | recovery-selection gap 无人测过；分叉测量装置在恢复研究中无先例 |
| Feasibility | 4/5 | emulator 快照是成熟机制；零训练可完成测量；成本 1–2 天并行计算 |
| Impact | 4/5 | gap 数字直接裁决"恢复策略研究值不值得做"；数据集可复用 |
| Risk | 4/5 | kill criterion 在第 3 步即触发，沉没成本极低；主要风险均有报告出路 |
| Evidence | 5/5 | BacktrackAgent 误伤数据 + verification pollution + VeriGUI 自认覆盖局限，三路已发表证据表明固定恢复有害的情形真实存在 |
| **Total** | **21/25**（↑ from 20：Risk +1，claim 不再依赖分类学假设） | |

**Reasoning**：第三版把 claim 收缩为一个可测量的量（gap），完备性辩护义务消失，kill/go 在实验第 3 步即分晓。相比前版，唯一的让步是不再承诺机制解释——聚类是描述性的；若 gap 显著且聚类结构清晰，机制研究是自然的后续论文而非本篇负担。

**History**：v1（2026-07-16 上午）三分类先验 + 归因混淆率；v2（同日下午）五分类 + 完备性三重验收；v3（本版）应 Supervisor 要求去除分类学依赖，改为分叉测量 gap。教训：claim 不应建立在需要无限辩护的分类学之上。

## Upgrade — 2026-07-20（AgentRuntimePrimitives 调研后的算法强化）

本周三原语调研（[[Topics/AgentRuntimePrimitives-Survey]] 37 篇 + idea 淘汰赛检索）为本 idea 补三块，novelty 复查后仍干净：

**1. 训练信号的免疫性论证（新亮点）**：[[Papers/2607-EvoCUA15]] 实证 PRM 在稀疏 reward 下被 hack（Fig 7：PRM 分升、真实成功率停滞），并指名 counterfactual local replay 为替代方向但未实现。本 idea 的分叉标签正是该方向在恢复子问题上的实现——selector 的监督是**反事实环境结局**（同一 mismatch 点分叉出的各恢复动作的真实成败），不是 judge 打分，结构上免疫 EvoCUA-1.5 记录的 reward hacking 失效模式。这把 selector 从"工程组件"提升为"grounded counterfactual supervision 的首个 GUI 实例"。

**2. Train-with-fork, deploy-fork-free（部署故事）**：分叉只发生在可快照的 emulator（测量/训练期），部署时 selector 是纯 policy 前向、零分叉——绕开 live 环境不可分叉的硬约束（survey 核心张力）。先例定位：[[Papers/2410-ExACT]] 把搜索树蒸馏进 policy（恢复 87% 搜索性能），本 idea 蒸馏的是恢复选择且标签更强（环境结局 vs 树遍历）。

**3. Novelty 复查（2026-07-20 检索）**：邻域新增三篇均不覆盖——ALAS (2505.12501)：workflow 调度域的 retry/rollback/delay 成本启发式选择（非学习、非 GUI）；MTTR-A (2511.20663)：多 agent 恢复反射（rollback/replan/retry）的度量学（测延迟不选动作）；Scheduler-theoretic (2604.11378)：主张恢复应为有界协议而非 ad-hoc LLM 决策（规则路线，恰构成对立面——learned selector 是 ad-hoc 与固定协议之间的第三条路，可作为 positioning 引用）。Learning to Explore (2605.08978) 学的是"何时探索"非"选哪种恢复"；EvoCUA-1.5 的 Reflection & Recovery 偏好对是二元（反思恢复 vs 盲走），非多候选选择。"分叉测量 gap + mismatch-conditioned 恢复选择"仍无先例。
