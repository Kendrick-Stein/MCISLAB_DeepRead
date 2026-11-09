---
title: "Failure-Conditioned Retry：GUI Agent 第二次尝试的接口定义、匹配预算下的增益测量与可训练入口"
tags: [gui-agent, computer-use, error-recovery, memory, retry, research-idea]
status: raw
linked_project:
date_updated: "2026-11-03"
---

## Hypothesis

人做 GUI 任务第一遍失败、第二遍基本能对。agent 第二遍能不能对，取决于第二次尝试拿到了上一次失败的什么信息、从哪里接着做。我们假设：

**在真实 GUI 环境中，失败条件化重试相对同预算盲重试的增益，主要由错误步定位的准确度决定，而不是由反思文本的质量或轨迹信息量决定；并且现有 GUI 模型没有接收这类信息的原生入口，训练出入口后，同样的内容带来的增益显著高于 prompt 注入。**

形式化。第一次尝试 \(\tau_1\) 失败。第二次尝试的策略写成 \(\pi(a_t \mid o_{\le t}, g, \phi(\tau_1))\)，其中 \(\phi\) 是历史编码，\(\rho\) 是重置方式（从 \(s_0\) 重开，或恢复到第 \(k-1\) 步的环境快照）。主指标

\[
\Delta(\phi,\rho)=\mathrm{SR@2}[\pi\circ\phi,\rho]-\mathrm{SR@2}[\text{blind retry},s_0],
\]

同 task、同 seed 配对，总环境步数与 token 预算匹配。配对分解为 \(\mathrm{Rescue}_\phi=P(Y_\phi=1,Y_{\text{blind}}=0)\) 与 \(\mathrm{Harm}_\phi=P(Y_\phi=0,Y_{\text{blind}}=1)\)。

可证伪预测：

- **P1 内容排序**：人工定位纠正臂 \(\Delta\ge +8\)pp；完整原始轨迹臂 \(\Delta\le +2\)pp 或为负；自由反思臂介于两者之间。
- **P2 单调性**：把人工定位替换为随机步、偏移 ±3 步、模型自定位时，\(\Delta\) 随定位准确率单调下降。
- **P3 入口效应**：只告知"上一次尝试失败了"的臂 \(\Delta\) 在 0 到 +3pp 之间，小但可能非零。
- **P4 训练出的入口**：同一开源 GUI 模型在（失败前缀、定位纠正、成功续段）三元组上做 cross-episode 训练后，同样内容的 \(\Delta\) 比冻结模型 prompt 注入高 ≥5pp，且 Harm 不升。
- **P5 重置方式**：恢复到 \(k-1\) 快照相对从 \(s_0\) 重开，在 \(\Delta\) 持平的前提下减少 ≥30% 环境步数。

**Kill criteria**：

- 人工定位臂 \(\Delta\) 的 task-cluster 95% CI 上界 <3pp：连 oracle 定位都救不回，瓶颈在执行能力而非信息接口，方向停止。
- 完整轨迹臂与人工定位臂的 \(\Delta\) 之差 CI 含 0：定位不是瓶颈，主假设证伪，作为负结论报告。
- 盲重试加等量 token 预算的臂追平所有条件化臂：增益是预算假象，按 [[DomainMaps/GUI-Agent]] Pattern 4 判为不成立。

## Motivation

### 已知

- **协议层缺失。** [[Papers/2602-MemGUIBench]] 用 pass@3 加环境 reset 评测，attempt 之间不传上一次轨迹；Agent-S2 pass@1 27.3% → pass@3 49.2%。若所有任务成功率同为 27.3%，独立重采样 pass@3 上界为 61.6%，任务难度异质时实际期望更低，所以 pass@1→pass@3 的增益无法归因于学习，只能说明需要配对的盲重试对照。该 benchmark 对 Agent-S2 做长期记忆消融（pass@3 45.0% → 25.0%）同时移除了 attempt 内与 attempt 间的记忆，分离不出跨尝试那一部分。
- **带对照的通用环境证据说增益小且不稳。** Terminal-Bench 2.1 四次尝试预算下，retry 单独 +26.4，同预算 adaptation +2.3，p=0.774（[arXiv 2608.24876](https://arxiv.org/abs/2608.24876)）。VRL-Bench 在 MiniWoB 与 WebShop 上，Reflexion、Dynamic Cheatsheet、ACE 无一在六个 setting 全部胜过无记忆 retry，GLM-4.7 上 Reflexion 两个环境都降（[arXiv 2609.12404](https://arxiv.org/abs/2609.12404)）。CCRM 给出失败上下文抬高后续错误率的闭式模型（[arXiv 2605.08563](https://arxiv.org/abs/2605.08563)）。
- **GUI 上做对了就有信号。** EvoSkill-GUI 用同 backbone 的信息隔离 critic 诊断失败并修订 skill 文件，MobileWorld 三轮 69.5% 对 pass@3 62.8%，token 还更少；去掉信息隔离 −8.57pp；critic 人工审计正确率 80.4%（[arXiv 2609.17653](https://arxiv.org/abs/2609.17653)）。[[Papers/2606-LearningFromFailure]] 把失败诊断成 code patch，OSWorld 42.3% → 48.9%，但含人工校验。
- **定位是难点。** CUA-Recovery 报告 60.0% 的错误只在最后一步才出现证据，中位延迟 17 步；察觉到错误的运行通过率 15.6%，未察觉 12.2%（[arXiv 2610.27645](https://arxiv.org/abs/2610.27645)）。CUAErrorBench 204 条 OSWorld 失败轨迹上，人工标 root-cause step 一致率 85.8%，CUADebugger 的 Tag+Step 联合准确率 11.1% → 19.4%（[arXiv 2608.02643](https://arxiv.org/abs/2608.02643)）。
- **内容形式有反证。** [[Papers/2606-NaiveVisualMemory]] 全截图记忆让动作级失败变多；AnchorGUI 称保留完整视觉轨迹造成 context collapse（[arXiv 2609.15457](https://arxiv.org/abs/2609.15457)）；[[Papers/2609-ExpActivator]] 按 goal 检索的经验只在首步有效，按屏幕状态激活 +8.24；[[Papers/2606-SkillMemoryBudget]] 约 50% 记忆资产来自失败轨迹，token-matched vanilla 追平 AWM、ASI、ReasoningBank。
- **执行层非确定。** [[Papers/2610-GUIHARVEST]] 三次运行有 11.8%–20.4% 的任务结果翻转，action replay 不能当作可靠的前缀复用方式。

### 推测，有间接证据

- **GUI 模型没有接收上一次结果的入口。** UI-TARS、GUI-Owl、OpenCUA 的训练配方都是单 episode；[[Papers/2604-VeriGUI]]、[[Papers/2605-GUIRobustEval]] 的 RoTS、CUA-Recovery 的恢复轨迹微调训练的是 episode 内从脏状态恢复，不是条件于上一次尝试。LaMer 在 Sokoban、MineSweeper、WebShop 上证明 cross-episode 训练之后 reflection 才带来 +11/+14/+19（ICLR 2026，[arXiv 2512.16848](https://arxiv.org/abs/2512.16848)）。RoboRetry 在 VLA 上发现增益可拆成 slot 存在效应与内容效应，内容效应主要来自高质量纠正语言（[项目页](https://jedward225.github.io/RoboRetry/)）。GUI 上这两个实验都没人做。

### 为什么 GUI 的答案可能不同于文本环境

这是机制假设，不是先验断言，Phase 2 负责证实或证伪：

1. **视觉历史重。** 原始轨迹塞不进上下文，内容形式问题在 GUI 上不可回避，文本环境里可以绕过。
2. **错误显现晚。** PivotOPD 发现文本环境的 pivotal mistake 通常早出现（[arXiv 2609.40285](https://arxiv.org/abs/2609.40285)）；GUI 上 60% 到末步才可见，自定位更难，定位可能成为瓶颈。
3. **环境不可逆且非确定。** 快照恢复是 GUI 特有的重置通道，action replay 不可靠。

### 为什么以前没人做

被忽略加基础设施晚。benchmark 的单次或 reset 协议把这个问题藏起来了；带步级快照的可恢复环境（OSWorld-Verified、MobileGym、CUA-Gym-Hub）与带 root-cause step 标注的失败语料（CUAErrorBench 2608、CUA-Recovery 2610）都是最近三个月才齐备。

### 问题拆解

```text
attempt 1 fails → encode φ(τ₁) → reset ρ → attempt 2 → paired compare with blind retry
```

本工作研究 \(\phi\) 与 \(\rho\) 两个因子和它们的可训练版本。detector、终局 verifier、base agent 固定并单独审计。

## Related Work 与 novelty 边界

| Work | 已经做了什么 | 本工作仍可守住的差异 |
|:--|:--|:--|
| LaMer（[arXiv 2512.16848](https://arxiv.org/abs/2512.16848)） | meta-RL：trial 含多个 episode，策略条件于前面 episode 与自写 reflection，优化跨 episode 折扣回报 | 文本与 WebShop；内容是自由反思；没有 slot/内容/定位分解，也没有 GUI 模型 |
| PivoARL（[arXiv 2607.03702](https://arxiv.org/abs/2607.03702)） | 结构化反思输出 pivotal turn k，从 k 续跑并复用正确前缀，交互轮数 −42%；反思质量用后续回报训练 | 文本环境；前缀复用靠环境 replay；无 oracle 定位臂，无 \(\Delta\) 对盲重试 |
| VRL-Bench（[arXiv 2609.12404](https://arxiv.org/abs/2609.12404)） | 试错学习协议：T 次 trial、共享首次、retry 为强制 baseline、SR@T 与平均 trial 数 | MiniWoB 与 WebShop；只比较已有 verbal update，不拆内容形式，不做训练 |
| RoboRetry（[项目页](https://jedward225.github.io/RoboRetry/)） | VLA 上 failure-conditioned retry 对 matched blind retry 的 paired protocol；slot 存在效应与内容效应分解 | 机器人 RLBench；无定位因子，无重置因子；GUI 的三个机制差异未检验 |
| EvoSkill-GUI（[arXiv 2609.17653](https://arxiv.org/abs/2609.17653)） | GUI 上 reflect → revise → retry，信息隔离 critic，有 pass@3 对照 | 入口是 skill 文件而非策略条件；无定位、无前缀或快照复用；只有一种内容形式；无训练 |
| CUADebug / CUAErrorBench（[arXiv 2608.02643](https://arxiv.org/abs/2608.02643)） | 204 条 OSWorld 失败轨迹的 root-cause step、corrective strategy 人工标注；ReAct 式 debugger | 只诊断不重试；本工作把它的标注直接当 oracle 定位臂与 localizer 训练标签 |
| CUA-Recovery（[arXiv 2610.27645](https://arxiv.org/abs/2610.27645)） | 2,250 个自发错误状态、接管深度 0–25、root-cause 与首次可见步标注；恢复轨迹微调 | 从错误处不带提示继续，不研究第二次尝试条件于第一次 |
| AnchorGUI（[arXiv 2609.15457](https://arxiv.org/abs/2609.15457)） | 跨 trial 蒸馏，非对称记忆只保留 mismatch 处截图，AndroidWorld 69.2%（+11.9） | 无盲重试对照；本工作可把它当作一种 \(\phi\) 纳入因子实验 |
| [[Papers/2600-UiVoyagerSelfEvolving]] | GRSD 用 SSIM 在成功/失败组之间找 fork 点并蒸馏进权重 | 训练期、需多条轨迹；是 Phase 4a 的"蒸馏而不条件化"对照 |
| [[Papers/2604-SOLAR-RL]] / [[Papers/2602-ProxMO]] | first failure point 与 state similarity 用于训练期 credit assignment | 用途不同：本工作是推理时单轨迹定位喂给第二次尝试；[[Ideas/ForkPoint-CreditAssignment-GUI]] 因与它们重叠暂停，这里的差异点是用途与对照，不是定位算法 |
| [[Papers/2600-UiMemSelfEvolving]] / [[Papers/2606-NaiveVisualMemory]] | 失败模式模板与 correction guideline；独立 recovery memory | 均为 goal 检索的记忆系统，无 paired 对照；本工作把"定位后的纠正三元组"作为可控内容臂 |
| [[Papers/2606-LearningFromFailure]] | 失败诊断成 code patch 注入 CUA | 入口是 harness 代码而非策略；含人工校验 |
| [[Papers/2606-SRC]] / [[Papers/2410-ExACT]] | rollback 与 search 产生训练数据再蒸馏 | train-with-fork 先例；本工作的训练目标是条件于上一次尝试，不是无条件 policy |
| [[Papers/2604-VeriGUI]] / [[Papers/2505-BacktrackAgent]] / [[Papers/2608-StepReflect]] | episode 内每步验证与回退一步 | 同一 episode 内的恢复，不涉及第二次尝试；可作 base agent 自带恢复的对照 |
| [[Ideas/MismatchTriage-LongHorizonRecovery-GUI]] | 同 checkpoint 全分叉测恢复动作的 counterfactual value | 研究 episode 内第一次 alert 后选哪种恢复；本工作研究 episode 之间传什么。两者共用快照分叉装置与 Rescue/Harm 口径，定位结果可作 MismatchTriage selector 的输入 |

**Novelty**: 3/5 — closest works: LaMer、PivoARL、RoboRetry、EvoSkill-GUI。失败条件化重试的形式定义、paired blind-retry 协议、slot 与内容分解、pivotal step 定位与前缀复用，在文本环境、VLA 和 GUI skill 系统里都分别有先例。可守的是三者交集：**真实 GUI 上同预算配对的 \(\Delta\) 四因子分解（slot、内容形式、定位准确度、重置方式）+ 定位主导的机制假设及其 GUI 特有理由 + 条件于上一次尝试的 GUI policy 训练与冻结注入的直接对比**。

更安全的 claim：

> 据我们所知，尚无工作在真实 GUI 环境中，以同 task 同 seed 配对、总预算匹配的盲重试为对照，系统比较第二次尝试所接收的失败信息形式（标志、原始轨迹、自由反思、定位后的纠正）与重置方式（重开、快照恢复）对成功率的影响，也没有工作比较"训练出接收入口的 GUI 模型"与"向冻结模型 prompt 注入同样内容"。

不再声称：

- 从自己的失败中学习第二次尝试无人研究；
- GUI agent 完全没有跨尝试记忆；
- pivotal step 定位本身是新方法；
- pass@k 的提升证明或否定了学习。

## Prior-art 检索记录（2026-11-03）

| 查询 | 命中 | 判定 |
|:--|:--|:--|
| retry / learn from own failure / second attempt GUI agent | EvoSkill-GUI、UI-Voyager、UI-Mem、AnchorGUI、Learning-from-Failure、BacktrackAgent、StepReflect | 有反思重试与跨 trial 记忆，无 paired blind-retry 对照与内容分解 |
| pass@k vs resampling / retry baseline / matched budget | VRL-Bench、Terminal-Bench RSI 2608.24876、PAST-Bench 2608.04003、SkillMemoryBudget | 协议在文本与 web 环境已立，GUI 上未有 |
| pivotal / fork / first-error step localization + retry | PivoARL、PivotOPD、SRC、HDL 2609.36864、SOLAR-RL、ProxMO、LACL-GUI、2610.39251、UI-Voyager、CUADebug、CatchBench、DiagEval | GUI 上的定位全在训练期或只诊断；推理时单轨迹定位加重试仅见文本环境 |
| cross-episode / in-context RL / meta-RL LLM agent | LaMer、MR-Search、2602.04089、MAGE | 入口需训练的证据在文本环境；无 GUI 模型 |
| failure-conditioned retry interface, slot vs content | RoboRetry（VLA）、CCRM、AgentRewind | 分解与反面模型存在；GUI 无 |
| GUI model fine-tuned to take previous failed trajectory as input | 未检索到 | 推测为空白，待 Phase 4a 前再核一次 |

## Approach sketch

### Phase 0：快照保真与功效 pilot

1. 环境选 OSWorld-Verified（VM 快照）与 AndroidWorld 或 MobileGym（emulator 或 JSON state 快照）。每步执行前落快照。
2. 对同一快照重复 restore，比较截图、AX tree、app 状态与 task verifier，报告 restore divergence rate。快照恢复不过关的任务剔除，这是前置 gate，不是事后 limitation。
3. primary unit 是 task，seed 是重复测量。先做 MDE 与功效分析再定任务数。按 \(\Delta=8\)pp、配对设计粗估，需要 ≥150 条第一次失败的任务。

### Phase 1：第一次失败库

1. 两个 base agent：一个开源 GUI 模型（GUI-Owl-1.5-8B 或 OpenCUA-7B 级别），一个 API 模型。每任务跑一次，保留失败的 \(\tau_1\) 及全部步级快照。
2. 对失败库做 root-cause step 标注：两人独立标 step、错动作、一行纠正，沿用 CUADebug 的五字段与裁决流程，报告一致率。规模 150–200 条。
3. 并行做 counterfactual 自动标注子集：从第 j 步快照恢复、换一个动作、冻结策略续跑到终局，最早翻转结果的 j 作为 fork 标签。用于校准人工标注，并为 Phase 4b 扩数据。

### Phase 2：因子实验（冻结 agent，零训练）

内容臂 \(\phi\)：

| 臂 | 第二次尝试拿到什么 | 回答什么 |
|:--|:--|:--|
| A0 blind | 什么都不给 | \(\Delta\) 零点 |
| A0' blind, token-matched | 不给信息，但步数与 token 预算补齐到最贵的臂 | 预算假象 |
| A1 flag | 一句话：上一次尝试此任务失败了 | slot 存在效应 |
| A2 raw | \(\tau_1\) 完整截图与动作，按上下文上限截断 | 原始轨迹是否有害 |
| A3 raw-text | \(\tau_1\) 动作序列加屏幕文本摘要，无截图 | 模态是否是问题 |
| A4 reflect | 同 backbone 信息隔离 critic 的自由反思，EvoSkill-GUI 口径 | 现有做法的 \(\Delta\) |
| A5 loc-oracle | 人工标注的 \(k\)、第 \(k\) 步截图、错动作、一行纠正 | 定位准确时的上界 |
| A5' loc-step-only | 只给 \(k\) 与第 \(k\) 步截图，不给纠正文本 | 定位与纠正内容分离 |
| A6 loc-model | 同 A5 格式，\(k\) 由模型自定位 | 当前可部署水平 |
| A7 loc-perturbed | \(k\) 随机、\(k\pm3\) | P2 的单调性曲线 |

重置臂 \(\rho\)：对 A5、A5'、A6 各做"从 \(s_0\) 重开"与"恢复到 \(k-1\) 快照"两种。

所有臂同 task 同 seed 配对，两个 base agent 分开报告再等权汇总，统计用 task 层 paired bootstrap。主表报告 \(\Delta\)、Rescue、Harm、环境步数、token、95% CI。

### Phase 3：gate

按 Hypothesis 的 kill criteria 判读。只有 A5 显著高于 A2 且 A0' 未追平时进入 Phase 4。若 A2 本身显著为负，Harm 分解作为 GUI 上 contamination 的直接证据单独报告。

### Phase 4a：训练出入口（可学习组件一）

1. 数据：Phase 1 与 Phase 2 产生的三元组（\(\tau_1\) 前缀、第 \(k\) 步定位纠正、从 \(k-1\) 快照起的成功续段）。成功续段来自 oracle 纠正后的冻结策略或更强 agent 的续跑，经终局 verifier 确认。
2. 训练：同一开源 GUI 模型，先 SFT 到第二次尝试的输入格式，再做 LaMer 式 cross-episode GRPO，reward 为第二次尝试终局成功，并对 Harm 加惩罚。
3. 对照：同 base 冻结模型 prompt 注入同样内容（即 Phase 2 的 A5/A6）；UI-Voyager 式把同样纠正蒸馏进权重但推理时不给上一次尝试，用于区分增益来自"条件化"还是"多了训练数据"。
4. 指标：\(\Delta\)、Harm、以及在 held-out app 上的泛化。

### Phase 4b：单轨迹 localizer（可学习组件二）

1. Qwen3-VL-8B 级别模型，输入单条失败轨迹，输出 root-cause step。标签来自 CUAErrorBench 204 条、CUA-Recovery 标注与 Phase 1 的人工加 counterfactual 标注。
2. 评测 step-exact 与 ±1 准确率，再接入 A6，看 \(\Delta\) 在 P2 曲线上回收到哪一点。
3. 它同时是 step-level verifier，也可作 [[Ideas/MismatchTriage-LongHorizonRecovery-GUI]] selector 的输入。

### Phase 5：跨任务衰减（可选）

把 A5 的纠正三元组按状态而非 goal 检索，测 same-task → 同模板变体 → 同 app 异任务 的 \(\Delta\) 衰减曲线。这一步接近"有效性门控经验复用"的已有工作，只有 Phase 2 到 4 成立后才值得做。

### 成本粗估

Phase 2 按 150 任务 × 10 臂 × 2 重置（仅定位臂）× 2 seed，约 4,000 个第二次尝试 episode，每条 15 步左右，约 6 万环境步。两个 base agent 翻倍。Phase 4a 的 RL 在 8B 模型上为单机多卡量级。

## Expected outcome

若假设成立，应观察到：

1. 内容排序 A5 > A4 > A1 ≈ A0，A2 ≤ A0 且 Harm 显著大于 0；A0' 不追平 A5。
2. A7 到 A6 到 A5 的 \(\Delta\) 随定位准确率单调上升；A5' 与 A5 差距小于 A5 与 A2 的差距，说明定位比纠正文本更重要。
3. Phase 4a 训练后的模型在同样内容下 \(\Delta\) 高于冻结注入 ≥5pp，且高于无条件蒸馏对照。
4. 快照恢复在 \(\Delta\) 持平下减少 ≥30% 环境步数。

若为正，贡献为：GUI 上失败条件化重试的形式定义与 paired 协议；slot、内容、定位、重置四因子的首次分解；"定位主导"的机制结论；条件于上一次尝试的 GUI policy 与 localizer 两个可部署组件。若 Phase 3 kill，贡献降为在明确 base agent、快照覆盖与功效边界下，给"喂回失败轨迹"这一普遍做法一个 GUI 上的可信负结论。

## Risk

- **强邻居。** LaMer、PivoARL 已定义训练与定位重试，RoboRetry 已做分解，EvoSkill-GUI 已在 GUI 上做带对照的反思重试。论文必须以 GUI 上的四因子 \(\Delta\) 分解与定位主导结论为第一贡献，训练入口为第二贡献；如果 Phase 2 发现 A2 ≈ A5，机制假设不成立，这个 idea 就是 RoboRetry 的 GUI 复现，应当停止。
- **oracle 泄漏。** 人工的 corrective strategy 可能包含任务解法。控制：A5 的纠正限一行且只针对第 \(k\) 步；A5' 只给步号与截图；另抽样人审纠正文本是否越界。
- **快照不等价。** 远端后端、时间、网络、账号状态不在快照内。Phase 0 的 restore divergence 是前置 gate；不过关的任务剔除并报告比例。
- **预算假象。** 条件化臂天然多消耗 token。A0' 必须有，并同时报告 cost-aware 与 success-only 两套结果。
- **标注成本与一致率。** CUADebug 的 step 一致率 85.8% 是上界参考；若我们的一致率低于 75%，A5 不再是 oracle，改报 inter-annotator 区间。
- **功效不足被包装成负结果。** 预注册 \(\delta=3\)pp 的 practically meaningful margin，CI 横跨 3–8pp 记为 inconclusive，不记为 negative。
- **Phase 4a 的分布偏移。** 训练后的模型只见过自己 base 的失败分布；做 leave-one-base-agent-out，不默认跨 agent 泛化。
- **与 vault 既有 idea 的边界。** [[Ideas/ForkPoint-CreditAssignment-GUI]] 因训练期 credit assignment 赛道重叠暂停；本 idea 的定位用途是推理时喂给第二次尝试并有 oracle 与盲重试对照，若 Supervisor 认为仍属延伸，应在 Phase 2 前否决而非 Phase 4b 后。

## Evaluation（自评，2026-11-03）

| Dimension | Score | Notes |
|:----------|:-----:|:------|
| Novelty | 3/5 | 四个强邻居各占一块；交集可守但不宽，依赖 GUI 特有机制假设被 Phase 2 证实 |
| Feasibility | 4/5 | Phase 2 零训练、现成 agent、现成标注语料；快照装置与 MismatchTriage 共用 |
| Impact | 3/5 | 若成立，改变"喂回失败轨迹"这一普遍做法，并给 recovery、verifier、memory 三条线一个共同入口；若 kill，是一个有用的负结论 |
| Risk | 3/5 | 主要风险是 A2 ≈ A5 使机制假设落空，以及 oracle 泄漏 |
| Evidence | 3/5 | 定位难、原始轨迹有害、入口需训练三条都有间接证据，但均来自非 GUI 或非配对设置 |
| **Total** | **16/25** | 建议：先做 Phase 0–3，约三到四周，再决定是否投入训练 |

## Evidence boundary / 待核查

- 本文引用的 LaMer、PivoARL、PivotOPD、VRL-Bench、RoboRetry、AnchorGUI、CCRM、EvoSkill-GUI、CUADebug、CUA-Recovery、AgentRewind、Terminal-Bench RSI 2608.24876 均为网络核对，vault 尚无 Papers 笔记，建议先 paper-digest 后再引用进 survey。RoboRetry 目前只有项目页，无 arXiv 号。
- MemGUI-Bench 的 61.6% 是任务难度同质假设下的独立重采样上界，不是期望值；用于说明 pass@k 不能归因，不用于证明"没有学习"。
- CUA-Recovery 的 15.6% 对 12.2% 是 agent 自己察觉与否的分组，不是外部告知的 slot 实验；GUI 上 slot 存在效应尚无任何数字。
- 相关 survey 位置：[[Topics/CUA-Survey]] §6.9 Memory、§6.10 Verification and Error Recovery、§10.11 D2；[[Topics/SelfEvolvingAgents-Survey]] §5 Memory/Context Evolution。
