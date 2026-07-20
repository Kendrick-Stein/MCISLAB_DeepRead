---
title: "拔电源测试：GUI Agent 的状态笔记能当 checkpoint 用吗"
tags: [gui-agent, computer-use, research-idea]
status: raw
linked_project:
date_updated: "2026-07-16"
---
## Hypothesis

**一句话**：把 agent 的上下文全部清空，只留它自己维护的状态笔记 + 当前屏幕——如果笔记真的记录了任务状态，agent 应该能接着把任务做完。过去 8 个月 6 篇论文都在给 GUI agent 加状态笔记（TSR / AgentProg / AndroTMem / MementoGUI / MGA / MemGUI-Agent），**没有一篇做过这个测试**。

可证伪预测：

- **恢复力 ≠ 成功率**：在统一 harness 下横向复现 4 类状态表示（last-n 原始式 / TSR 式 JSON 状态 / AgentProg 式程序变量+belief / AndroTMem 式 anchor），端到端 SR 相近（±5pp）的表示，重置后恢复力（resumability：任务中途清空上下文后最终完成率 ÷ 不清空的完成率）差异 >20pp——即现在所有 memory 论文用的 SR 根本测不出笔记质量；
- **恢复失败可定位到缺的字段**：删 failed-attempts 记录 → 重复无效动作循环，删 entity bindings → 跨 app 传错参数——每个字段有独立的失败指纹，直接告诉下一篇 memory 论文该记什么；
- **AgentProg 的反向检验**：它的上下文已不含历史截图（78% AndroidWorld），看似"结构化状态已足够"——但若重置后（剪枝代码史、循环迭代检索一并清掉）显著掉分，说明它在隐性依赖笔记之外的通道，表观充分性被证伪。

## Motivation

**为什么早该做这个测试**：给 agent 加"笔记本"已经是共识做法，两篇（AgentProg、MementoGUI 的 WM 模式）甚至常态就只喂笔记不喂原始历史，成绩不错。但所有人都只报端到端 SR——SR 把模型能力、grounding、规划、笔记质量混在一起，笔记记错了什么、漏了什么，从 SR 里读不出来。检验一个笔记本靠不靠谱的自然方法是人每天都在做的：重启电脑、换个会话，靠笔记接着干活。这个测试便宜、直接、每个 memory 系统都能跑，但从来没人跑过。

**Digest 后确认的空位**（2026-07-16，四篇全文核查）：

- [[Papers/2607-TSR]]：状态是**附加**在 last-3 截图 + 全量历史文本之上的，从未测过"只靠 TSR"；且它 conditionally beneficial（AndroidWorld 上 Qwen -3.45、over-decomposition 超 step budget）——领域连"笔记何时有用"都说不清；
- [[Papers/2512-AgentProg]]：五元组状态（STP+PC+剪枝代码史+变量+belief）实际就是一个显式 checkpoint，**但从没人真的从这个 checkpoint 重启过**；GBS ablation 53.9→78.0 证明状态内容是主要杠杆；开源，是现成测试载体；
- [[Papers/2603-AndroTMem]]：Raw/Summary/ASM 反事实消融是最接近的受控比较，但**全程离线预录轨迹**（动作不改变环境），连承载恢复测试的载体都没有；"memory 失败主导"的 claim 无量化归因协议；
- [[Papers/2605-MementoGUI]]：MCS 指标是**观察式**打分（判笔记写得对不对），非干预式（不测笔记够不够恢复任务）；其 Table 1 比较了 raw 回放 vs 文本摘要 vs 学习型 memory，但没有 schema 化状态、没有重置协议。

**做完的回报**：(1) memory 质量有了独立于 SR 的度量，6 个互不可比的系统第一次可比；(2) 字段级失败指纹是给后来者的设计清单；(3) 部署场景就是这样：context 溢出重启、跨会话交接、多 agent 接力——恢复力就是这些场景的直接预测量。

**机制先验**：[[Papers/2606-HiconAgent]]（长历史不总是更好、action token 是信息流 anchor）、[[Papers/2603-MEM]]（VLA 上语言摘要做长时记忆可行）、[[Papers/2605-SaaSBench]]（checkpoint 43.9% vs resolved 3.8% 的长程崩塌）。

## Related Work

- [[Papers/2607-TSR]] — training-free JSON 状态，附加式使用，无重置实验，conditionally beneficial
- [[Papers/2512-AgentProg]] — 无历史截图的程序化状态，最强"充分性"旁证，开源测试载体，无重置实验
- [[Papers/2603-AndroTMem]] — 表示形式受控消融（离线），诊断 claim 强于证据
- [[Papers/2605-MementoGUI]] — 学习型 memory controller + 观察式 MCS 指标，无干预式测量
- [[Papers/2606-HiconAgent]] — 历史长度样本依赖性的机制先验（训练时压缩路线）
- [[Papers/2603-MEM]] — 语言摘要长时记忆在 VLA 域的可行性旁证
- [[Papers/2605-SaaSBench]] — 长程状态崩塌的现象级证据与任务床

**Novelty**: 3/5 — closest works: [[Papers/2605-MementoGUI]], [[Papers/2512-AgentProg]], [[Papers/2603-AndroTMem]], [[Papers/2607-TSR]]。四篇全文核查确认：干预式重置协议、恢复力度量、字段级归因均无先例；MementoGUI 的 memory-only 常态运行和 Table 1 表示比较削弱"ledger-only 条件"的新颖性，故 framing 必须以**重置-恢复**为核心而非"只喂笔记"。

## Approach sketch

1. **统一 harness**：固定 backbone（2 个），在线 AndroidWorld + AW-Extend（>30 步）+ SaaSBench 子集；4 类状态表示做成可插拔模块（AgentProg 用官方开源码，TSR 按 Appendix E prompt 复现，AndroTMem 按 Table 10 prompt 复现改在线版，last-n 为 baseline）。
2. **拔电源协议**：任务 25%/50%/75% 进度点强制清空上下文，只保留 {状态笔记, 当前 screenshot, 原始 instruction}；恢复力 = 重置组最终 SR ÷ 对照组 SR。每表示 × 每重置点 ≥50 任务。
3. **字段消融**：对最强表示逐字段删除（progress pointer / entity bindings / failed-attempts / belief 条目），把恢复失败归类到失败模式（重复循环 / 传错参数 / 目标漂移 / 过早终止），建立字段 → 失败模式映射。
4. **零训练**，成本主要是评估量（约 4 表示 × 3 重置点 × 50 任务 × 2 backbone + 对照 ≈ 1500 runs）。

## Expected outcome

- 恢复力排序与 SR 排序显著不一致（Spearman ρ < 0.5）——memory 论文需要新的必报指标；
- AgentProg 重置后掉分显著大于其 SR 优势所暗示的（隐性通道被暴露），或几乎不掉（真 checkpoint，直接支持"程序化状态是正确形态"）——两种结果都改写认知；
- 字段消融给出至少 2 个反直觉发现（预期 failed-attempts 记录的边际价值最大——TSR 的 over-decomposition 与 BacktrackAgent 的重复循环都指向"记住失败"比"记住计划"更关键）；
- 产出：重置-恢复评测协议 + 4 系统首次可比结果 + 字段设计清单。

## Risk

- **恢复力与 SR 高度相关（boring 结局）**：即便如此，"6 系统首次统一可比"与字段指纹仍独立成立；且该结局本身回答了"SR 够不够用"这个悬而未决的问题。
- **复现变差**：TSR/AndroTMem 靠 prompt 复现可能弱于原报告。缓解：先与原论文数字对齐再进比较；AgentProg 有官方代码，作为锚点。
- **"AgentProg 已证明不需要截图历史"的质疑**：回应明确——运行一种模式 ≠ 验证状态充分性；它保留的剪枝代码史和循环迭代检索就是换了名字的历史，重置实验恰好能测出这部分的真实贡献。
- **在线环境的方差**：live emulator 的非确定性需要更多重复；用 AndroidWorld 的固定 seed 任务子集控制。

## Evaluation — 2026-07-16 (idea-generate 深度验证)

| Dimension | Score | Notes |
|:----------|:-----:|:------|
| Novelty | 3/5 | 干预式重置协议无先例（四篇全文核查确认），但 MementoGUI 的 memory-only 运行模式与表示比较占掉了相邻位置 |
| Feasibility | 4/5 | 零训练；AgentProg 开源 + TSR/AndroTMem prompt 齐全；成本在 ~1500 online runs |
| Impact | 4/5 | 给爆发中的子领域第一个可比协议 + 字段设计清单；部署场景（context 溢出/交接）直接受益 |
| Risk | 4/5 | 最大 kill-risk（MementoGUI-Bench 已占坑）经全文核查排除；剩余风险均有可报告出路 |
| Evidence | 4/5 | AgentProg 78% 无截图历史 + MementoGUI WM 模式 + MEM/HiconAgent 机制先验，充分性"大概率部分成立"，测试有区分度 |
| **Total** | **19/25**（↑ from 18，Risk +1） | |

**Reasoning**：核心动作简单到一句话——"从没人试过把电源拔了"。四篇近孪生全文核查后空位收窄但仍成立，且拿到了两个意外弹药：TSR 的 conditionally beneficial（笔记何时有用没人说得清）和 AndroTMem 的离线评测（想测恢复也测不了）。风险结构比初版更好。

**Suggestions**：(1) 以 AgentProg 为第一个测试载体（开源 + 最强充分性表观证据，重置实验对它信息量最大）；(2) 论文 framing 用"checkpoint 从没被当 checkpoint 测过"开场，不用任何"测量科学/充分统计量"表述；(3) 与 [[Ideas/MismatchTriage-LongHorizonRecovery-GUI]] 共享在线 harness。
