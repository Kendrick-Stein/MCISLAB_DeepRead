---
title: "Failure-Conditioned Retry：GUI Agent 第二次尝试的接口定义、匹配预算下的增益测量与可训练入口"
tags: [gui-agent, computer-use, error-recovery, memory, retry, research-idea]
status: raw
linked_project:
date_updated: "2026-11-12"
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
| CUADebug / CUAErrorBench（[[Papers/2608-CUADebug]]，[arXiv 2608.02643](https://arxiv.org/abs/2608.02643)） | 204 条 OSWorld 失败轨迹的 root-cause step、corrective strategy 人工标注（step 一致率 85.8%）；ReAct 式 debugger。**并有 RCA-guided re-rollout 实验**：从 root-cause step 前一步重放并注入修复，固定预算，Claude 4.5 Sonnet 的 144 条失败上 Baseline（无提示重放）13.9 / Self-debug 15.3 / Machine RCA 28.5 / CUADebugger 29.9 / Human oracle 31.9；continual 变体（第 51 步起）12.5 / 13.9 / 21.5 / 25.7 / 29.2；machine RCA 的 step-exact 29.2%、±2 步 45.1% | 11-03 记为"只诊断不重试"是笔误（2026-11-12 核对改正）：它已做了 \(\rho=k-1\) 下盲重放 / A4 / A6 / A5 的比较。仍缺：从 \(s_0\) 的盲重试臂与 token 匹配臂；定位与纠正内容捆绑成 package 未拆开。同时它给出一条反向证据：step-exact 仅 29.2% 的 machine RCA 与人工 oracle 只差 3.5 pp，定位准确度的剂量效应可能很平（见 Risk） |
| CUA-Recovery（[arXiv 2610.27645](https://arxiv.org/abs/2610.27645)） | 2,250 个自发错误状态、接管深度 0–25、root-cause 与首次可见步标注；恢复轨迹微调 | 从错误处不带提示继续，不研究第二次尝试条件于第一次 |
| On the Reliability of Computer Use Agents（[[Papers/2604-ReliabilityCUA]]，[arXiv 2604.17849](https://arxiv.org/abs/2604.17849)） | OSWorld，benchmark 评测器判失败后触发 Retry(Binary) 与 Retry(Clarify)，最多 5 次，是否重置到初始状态未写明；Pass^1 / Pass^3：GPT-5 .576/.454 → .645/.557 → .730/.632，Claude .702/.612 → .732/.668 → .774/.706，Kimi .508/.357 → .623/.496 → .727/.634，McNemar / Wilcoxon 检验 | A1（只给失败标志）臂在 OSWorld 已有数字且带显著性检验，但失败标志来自 oracle 评测器；Retry(Clarify) 的反馈方读得到评测器源码与期望文件，强于 A5。无成本记账、无 token 匹配、无内容形式分解 |
| 代码域 placebo 对照（[arXiv 2607.26117](https://arxiv.org/abs/2607.26117)、[arXiv 2611.06863](https://arxiv.org/abs/2611.06863)、[arXiv 2607.28576](https://arxiv.org/abs/2607.28576)，2026-11-12 新增） | 预算匹配的 Resample / Placebo / Feedback / Reflect 臂；2607.26117 的 placebo 在 1.5B/3B 上 −6.1/−6.9 pp（anchoring）；2611.06863 Compiled 85.3 ≈ Different-Label 86.1 ≈ Fixed Template 86.1 ≫ Resample 68.3，Reflection 56.0，结论"匹配粗标签无额外收益"，并建议 mismatched-feedback 与 static-guidance 对照 | 非 GUI，但协议正是 Phase 2 要立的；其 null 结果（内容是否对应本次失败不重要）直接威胁 P2/P3。本工作应把 mismatched / static 臂设为必做臂 |
| AgentRewind（[arXiv 2608.14380](https://arxiv.org/abs/2608.14380)）/ DART（[arXiv 2605.23311](https://arxiv.org/abs/2605.23311)）/ Recoverability（[arXiv 2609.13672](https://arxiv.org/abs/2609.13672)），2026-11-12 新增 | SWE/terminal 与 FSM 工具环境的回退到 checkpoint 重试；AgentRewind w/o Rewind Memory 51.2 vs 完整 87.8，Restart with Experiences 78.0 | 重置方式（重开 vs 回退）因子在非 GUI 已有数字，GUI 无；快照保真是 GUI 特有问题 |
| [[Papers/2611-SCOPE]]（2026-11-12 新增） | web 文本环境训练期：restore-to-frontier + failure-conditioned action，再蒸馏为无条件 policy | 训练期、文本；无部署期 \(\Delta\) 与定位剂量实验；是 Phase 4a "条件化 vs 蒸馏为无条件"的直接对照先例，比 LaMer 更近 |
| Self-Adaptive VLA（[arXiv 2609.30092](https://arxiv.org/abs/2609.30092)，2026-11-12 新增） | 真实机器人上以 AdaLN 上下文 token 接收先前尝试的信息 | 训练入口的非 GUI 先例；GUI 模型上仍未检索到 |
| AnchorGUI（[arXiv 2609.15457](https://arxiv.org/abs/2609.15457)，ECCV 2026） | 跨 trial 蒸馏，非对称记忆只保留 mismatch 处截图。AndroidWorld、Qwen3-VL-8B、K=3、每次 trial 重置到同一初始状态、3 seeds temp 0.7。Table 3 自带配对基线（trial 1/2/3）：Memoryless Retry 57.3/61.2/62.9（+5.5）、Episodic Memory 57.3/60.5/62.6、Reflexion 57.3/63.1/64.4、Asymmetric Distillation 57.3/65.4/69.2（+11.9）；跨 trial token 24.4k vs Reflexion 66.5k | **已有盲重试对照**（11-03 记为"无盲重试对照"是笔误，2026-11-12 核对 Table 3 改正）。它已在 GUI 上配对比较了 A0、A2 的近似（Episodic）、A4 与自家 \(\phi\)。仍缺：总预算匹配臂 A0'（只报成本未配预算）、CI、定位因子、重置因子、Rescue/Harm 分解 |
| [[Papers/2600-UiVoyagerSelfEvolving]] | GRSD 用 SSIM 在成功/失败组之间找 fork 点并蒸馏进权重 | 训练期、需多条轨迹；是 Phase 4a 的"蒸馏而不条件化"对照 |
| [[Papers/2604-SOLAR-RL]] / [[Papers/2602-ProxMO]] | first failure point 与 state similarity 用于训练期 credit assignment | 用途不同：本工作是推理时单轨迹定位喂给第二次尝试；[[Ideas/ForkPoint-CreditAssignment-GUI]] 因与它们重叠暂停，这里的差异点是用途与对照，不是定位算法 |
| [[Papers/2600-UiMemSelfEvolving]] / [[Papers/2606-NaiveVisualMemory]] | 失败模式模板与 correction guideline；独立 recovery memory | 均为 goal 检索的记忆系统，无 paired 对照；本工作把"定位后的纠正三元组"作为可控内容臂 |
| [[Papers/2606-LearningFromFailure]] | 失败诊断成 code patch 注入 CUA | 入口是 harness 代码而非策略；含人工校验 |
| [[Papers/2606-SRC]] / [[Papers/2410-ExACT]] | rollback 与 search 产生训练数据再蒸馏 | train-with-fork 先例；本工作的训练目标是条件于上一次尝试，不是无条件 policy |
| [[Papers/2604-VeriGUI]] / [[Papers/2505-BacktrackAgent]] / [[Papers/2608-StepReflect]] | episode 内每步验证与回退一步 | 同一 episode 内的恢复，不涉及第二次尝试；可作 base agent 自带恢复的对照 |
| [[Ideas/MismatchTriage-LongHorizonRecovery-GUI]] | 同 checkpoint 全分叉测恢复动作的 counterfactual value | 研究 episode 内第一次 alert 后选哪种恢复；本工作研究 episode 之间传什么。两者共用快照分叉装置与 Rescue/Harm 口径，定位结果可作 MismatchTriage selector 的输入 |

**Novelty（自评 2026-11-03；2026-11-12 idea-evaluate 下调至 2/5，见文末 Evaluation）**: 3/5 — closest works: LaMer、PivoARL、RoboRetry、EvoSkill-GUI。失败条件化重试的形式定义、paired blind-retry 协议、slot 与内容分解、pivotal step 定位与前缀复用，在文本环境、VLA 和 GUI skill 系统里都分别有先例。可守的是三者交集：**真实 GUI 上同预算配对的 \(\Delta\) 四因子分解（slot、内容形式、定位准确度、重置方式）+ 定位主导的机制假设及其 GUI 特有理由 + 条件于上一次尝试的 GUI policy 训练与冻结注入的直接对比**。

更安全的 claim：

> 据我们所知，尚无工作在真实 GUI 环境中，以同 task 同 seed 配对、**总 token 预算匹配**的盲重试（A0'）为对照，把第二次尝试的增益拆成 Rescue 与 Harm，并同时操控失败信息形式、定位准确度（含扰动定位与 mismatched 纠正）与重置方式；也没有工作比较"训练出接收入口的 GUI 模型"与"向冻结模型 prompt 注入同样内容"。GUI 上已有的配对比较——AnchorGUI 的 Memoryless Retry / Episodic / Reflexion、2604.17849 的 Retry(Binary)、CUADebug 的 RCA-guided re-rollout——都未做预算匹配、未拆因子、未报 Harm。（2026-11-12 收窄；11-03 版本的"系统比较失败信息形式与重置方式"已被上述三项部分占住）

不再声称：

- 从自己的失败中学习第二次尝试无人研究；
- GUI agent 完全没有跨尝试记忆；
- pivotal step 定位本身是新方法；
- pass@k 的提升证明或否定了学习；
- GUI 上没有盲重试对照（AnchorGUI Table 3、2604.17849 已有）；
- 推理时定位加重试在 GUI 上无人做过（CUADebug 已做 \(\rho=k-1\) 下的 oracle / machine 定位重放）。

## Prior-art 检索记录（2026-11-03）

| 查询 | 命中 | 判定 |
|:--|:--|:--|
| retry / learn from own failure / second attempt GUI agent | EvoSkill-GUI、UI-Voyager、UI-Mem、AnchorGUI、Learning-from-Failure、BacktrackAgent、StepReflect | 有反思重试与跨 trial 记忆，无 paired blind-retry 对照与内容分解 |
| pass@k vs resampling / retry baseline / matched budget | VRL-Bench、Terminal-Bench RSI 2608.24876、PAST-Bench 2608.04003、SkillMemoryBudget | 协议在文本与 web 环境已立，GUI 上未有 |
| pivotal / fork / first-error step localization + retry | PivoARL、PivotOPD、SRC、HDL 2609.36864、SOLAR-RL、ProxMO、LACL-GUI、2610.39251、UI-Voyager、CUADebug、CatchBench、DiagEval | GUI 上的定位全在训练期或只诊断；推理时单轨迹定位加重试仅见文本环境 |
| cross-episode / in-context RL / meta-RL LLM agent | LaMer、MR-Search、2602.04089、MAGE | 入口需训练的证据在文本环境；无 GUI 模型 |
| failure-conditioned retry interface, slot vs content | RoboRetry（VLA）、CCRM、AgentRewind | 分解与反面模型存在；GUI 无 |
| GUI model fine-tuned to take previous failed trajectory as input | 未检索到 | 推测为空白，待 Phase 4a 前再核一次 |

## Prior-art 检索记录（2026-11-12，idea-evaluate）

反向检索：按 11-03 记录里每个"无 X"断言去找 X。命中均打开原文核对表格，不以摘要为准。

| 查询 | 命中 | 判定 |
|:--|:--|:--|
| memoryless retry / reflexion baseline, AndroidWorld, multi-trial | AnchorGUI 2609.15457 Table 3 | **推翻** 11-03 的"无盲重试对照"：Memoryless Retry / Episodic / Reflexion 三个配对基线，重置到同一初始状态，3 seeds；无 A0'、无 CI |
| root-cause guided re-rollout / replay from cutoff, OSWorld | CUADebug 2608.02643 §re-rollout（单次与 continual 两种） | **推翻** 11-03 的"只诊断不重试"：\(\rho=k-1\) 下 Baseline / Self-debug / Machine RCA / CUADebugger / Human oracle 五臂；无从 \(s_0\) 盲重试、无 token 匹配 |
| retry on failure signal, pass^k, computer use reliability | On the Reliability of CUAs 2604.17849（[[Papers/2604-ReliabilityCUA]]） | A1 臂在 OSWorld 已有，含 McNemar / Wilcoxon；无成本与内容分解 |
| budget-matched resample vs feedback, placebo feedback, code repair | 2607.26117、2611.06863、2607.28576 | 预算匹配 + placebo 协议成熟；2611.06863 的 label-mismatch null 直接威胁 P2/P3 |
| rewind / restart from checkpoint, agent retry, recoverability | AgentRewind 2608.14380、DART 2605.23311、Recoverability 2609.13672、Fail-Fast Restart-Smart 2608.03222 | 重置因子在 SWE / FSM 工具环境已有数字；GUI 无 |
| failure-conditioned policy, restore to frontier, distill to unconditional | [[Papers/2611-SCOPE]]、PivoARL、LaMer、MAGE、MR-Search | 训练期先例全在文本；SCOPE 是 Phase 4a 最近邻 |
| conditioning on previous attempt, context token, VLA / robot retry | Self-Adaptive VLA 2609.30092、RoboRetry（CVPR 2026 workshop，FailureSlot 1,334 条，仍无 arXiv 号）、FAR、FLARE、ReCoVLA | 训练入口在机器人已有；GUI 模型未检索到（与 11-03 一致） |
| GUI failure diagnosis then recovery, software evaluation | DiagEval 2605.17439（DiagEval×1 45.6–47.0% vs naive retry 17.5–46.2%）、REFLECT 2606.09071、EchoTrail-GUI 2512.19396 | 诊断引导重试在 GUI 软件评估场景有数字，对照不配预算 |
| GUI model fine-tuned on previous failed trajectory as policy input | 仍未检索到（arXiv 直链核验 2026-11-12） | 空白维持；Phase 4a 前再核 |

vault 覆盖：上表命中中 [[Papers/2611-SCOPE]]、[[Papers/2609-AnchorGUI]]、[[Papers/2608-CUADebug]]、[[Papers/2604-ReliabilityCUA]] 有 Papers 笔记（后三篇 2026-11-12 入库）；2611.06863、2607.26117、2608.14380、2605.23311、2609.30092 均无笔记，数字来自原文核对。

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
- **定位剂量效应可能很平（2026-11-12 新增）。** CUADebug 上 step-exact 29.2% 的 machine RCA 与 100% 的人工 oracle 只差 3.5 pp（28.5 vs 31.9）；2611.06863 在代码域发现匹配粗标签无额外收益。若 A7（扰动定位）≈ A5，P2 不成立，"定位主导"退为"任何结构化纠正提示都有效"。对策：A7 分 ±1 / ±3 / 随机步三档，并加 mismatched-feedback 臂（给另一任务或另一步的纠正三元组）与 static-template 臂。
- **第一贡献的表述已被先例抵消（2026-11-12 新增）。** "GUI 上无盲重试对照"不成立（AnchorGUI、2604.17849、CUADebug）。第一贡献须改为预算匹配下 \(\Delta\) 的 Rescue/Harm 分解与定位剂量曲线，不是对照的存在性。
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

## Evaluation — 2026-11-12 (idea-evaluate, autoresearch round 1)

| Dimension | Score | Notes |
|:----------|:-----:|:------|
| Novelty | 2/5 | 11-03 自评"可守交集"有两块已被 GUI 先例占住：AnchorGUI Table 3 在 AndroidWorld 上配对比较了 Memoryless Retry / Episodic Memory / Reflexion / 自家蒸馏（对应 A0 / A2 近似 / A4 / \(\phi\)）；2604.17849 在 OSWorld 上做了 Retry(Binary)（A1）；CUADebug 做了 \(\rho=k-1\) 下盲重放 / Self-debug / Machine RCA / Human oracle（A4 / A6 / A5）。剩余交集：总预算匹配 A0' + Rescue/Harm 配对分解 + 定位剂量（A7 扰动、mismatched 臂）+ 训练入口 vs 冻结注入 |
| Feasibility | 4/5 | 不变。CUADebug 的 re-rollout 装置与 CUAErrorBench 标注可直接复用为 \(\rho=k-1\) 与 A5 臂；AnchorGUI 的 AndroidWorld 同初始状态重置协议可复用为 \(\rho=s_0\) 臂 |
| Impact | 3/5 | 不变。预算匹配的 \(\Delta\) 分解仍是 GUI 上缺的数字；但若 P2 被证伪，结论退为"结构化纠正提示 > 原始轨迹"，这在 AnchorGUI / CUADebug 已可读出，增量变小 |
| Risk | 2/5 | 下调。机制假设 P2"定位准确度主导"已有两条反向证据：CUADebug 上 step-exact 29.2% 的 machine RCA 与人工 oracle 只差 3.5 pp；2611.06863 在代码域发现匹配粗标签无额外收益。第一贡献"GUI 无盲重试对照"的表述已不成立 |
| Evidence | 4/5 | 上调。P1 的排序（原始轨迹 ≈ 盲重试 < 反思 < 定位后纠正）现在有 GUI 直接数字：AnchorGUI Episodic 62.6 ≈ Memoryless 62.9 < Reflexion 64.4；CUADebug Self-debug 15.3 ≪ Machine RCA 28.5。仍缺预算匹配与 CI |
| **Total** | **15/25** | 11-03 自评 16/25 → 15/25。建议 pivot 第一贡献，不淘汰 |

**Novelty**: 2/5 — closest works: [[Papers/2609-EvoSkillGUI]]、[[Papers/2611-SCOPE]]、[[Papers/2600-UiVoyagerSelfEvolving]]、[[Papers/2606-NaiveVisualMemory]]（vault 内）；AnchorGUI [arXiv 2609.15457](https://arxiv.org/abs/2609.15457)、CUADebug [arXiv 2608.02643](https://arxiv.org/abs/2608.02643)、On the Reliability of CUAs [arXiv 2604.17849](https://arxiv.org/abs/2604.17849)、[arXiv 2611.06863](https://arxiv.org/abs/2611.06863)（vault 无笔记，原文核对）。Prior-art 状态：**PARTIALLY_ADDRESSED**——配对盲重试对照、失败标志臂、RCA 引导的 \(k-1\) 重放在 GUI 上均已有工作；未被占住的是预算匹配下的四因子 \(\Delta\) 分解、定位剂量响应与训练入口对比。

**Reasoning**: 11-03 自评把 AnchorGUI 记成"无盲重试对照"、把 CUADebug 记成"只诊断不重试"，这两处错记直接撑起了"更安全的 claim"，核对原文后该 claim 必须收窄到预算匹配与因子分解。GUI 直接证据同时让 P1 更可信（原始轨迹记忆不优于盲重试、反思增益小、定位后纠正增益大）又让 P2 更可疑（人工 oracle 与 29% step-exact 的机器定位差距很小）。idea 仍值得做，但第一贡献须从"GUI 上第一个对照"改为"预算匹配下 \(\Delta\) 的 Rescue/Harm 分解与定位剂量曲线"，并把 2611.06863 式的 mismatched / static 对照臂设为必做臂，否则 Phase 2 的正结果无法区分"定位"与"任何纠正模板"。

**Suggestions**:
1. Phase 2 臂表新增 A8 mismatched-feedback（另一任务或另一步的纠正三元组）与 A9 static-template（固定的"检查上一步是否点错"提示）；A7 扰动定位分 ±1 / ±3 / 随机步三档。P2 判据改为 A5 − A8 与 A5 − A7 随扰动幅度的斜率，而非 A5 − A2。
2. 第一个实验不做全因子：在 CUADebug 公开的 144 条 Claude 4.5 Sonnet 失败子集上复现其 Baseline / Machine RCA / Human oracle 三臂，补 A0' 与 A8，六臂约 900 次 rollout，直接检验"定位主导"。
3. paper-digest AnchorGUI（2609.15457，已入库 [[Papers/2609-AnchorGUI]]）、CUADebug（2608.02643，已入库 [[Papers/2608-CUADebug]]）、On the Reliability of CUAs（2604.17849，已入库 [[Papers/2604-ReliabilityCUA]]）进 Papers/；[[Topics/CUA-Survey]] §6.10 与 §10.11 D2 当前只有间接证据，这三篇是 D2 的直接数据点。
4. Phase 4a 的对照先例改为 [[Papers/2611-SCOPE]]（条件化 → 蒸馏为无条件）与 Self-Adaptive VLA 2609.30092（AdaLN 上下文 token），LaMer 退为文本域背景。
5. 若 Supervisor 接受 pivot，status 可转 developing；若坚持原第一贡献表述，建议淘汰。

## Evidence boundary / 待核查

- 本文引用的 LaMer、PivoARL、PivotOPD、VRL-Bench、RoboRetry、CCRM、EvoSkill-GUI、CUA-Recovery、AgentRewind、Terminal-Bench RSI 2608.24876 均为网络核对，vault 尚无 Papers 笔记，建议先 paper-digest 后再引用进 survey（AnchorGUI、CUADebug、2604.17849 已于 2026-11-12 入库）。RoboRetry 目前只有项目页，无 arXiv 号（2026-11-12 再核：CVPR 2026 workshop，仍无 arXiv 号）。2026-11-12 新增引用的 2604.17849、2611.06863、2607.26117、2607.28576、2608.14380、2605.23311、2609.13672、2609.30092、2605.17439、2606.09071 同样无 Papers 笔记，数字为原文核对。
- MemGUI-Bench 的 61.6% 是任务难度同质假设下的独立重采样上界，不是期望值；用于说明 pass@k 不能归因，不用于证明"没有学习"。
- CUA-Recovery 的 15.6% 对 12.2% 是 agent 自己察觉与否的分组，不是外部告知的 slot 实验；GUI 上 slot 存在效应尚无任何数字。
- 相关 survey 位置：[[Topics/CUA-Survey]] §6.9 Memory、§6.10 Verification and Error Recovery、§10.11 D2；[[Topics/SelfEvolvingAgents-Survey]] §5 Memory/Context Evolution。
