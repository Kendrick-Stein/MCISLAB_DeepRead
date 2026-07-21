---
title: "Recovery-Selection Gap：GUI Agent 的固定恢复策略留下多少可收回的成功率"
tags: [gui-agent, computer-use, research-idea]
status: developing
linked_project: "[[Projects/MismatchTriage]]"
date_updated: "2026-07-21"
---

## Hypothesis

GUI agent 检测到"执行结果与预期不符"（mismatch）后，现有方法的恢复行为是固定的（重试或回退一步）。假设：**最优恢复动作随 mismatch 点而变，固定策略因此留下可测量的成功率差距（recovery-selection gap）**。

该假设不依赖任何错误分类学。可证伪预测：

- 用 emulator 快照在每个 mismatch 点分叉执行全部候选恢复动作，逐点最优选择（oracle）与最强固定策略之间的任务成功率差距 ≥8pp；
- 一个运行时 selector（prompted 起步，分叉数据可供训练）能收回该差距的 ≥50%；
- **Kill criterion**：若某单一恢复动作在 ≥85% 的 mismatch 点上属于最优集合，则固定恢复已足够，假设证伪——差距测量本身作为负结果报告。

候选恢复动作集（有限动作空间，非分类学）：① 原样重试；② 重新定位目标后重试；③ 等待后重新截屏、继续原计划；④ 关闭当前浮层、继续原计划；⑤ 回退上一屏；⑥ 重读当前页面、更新任务状态记录后重新决策。

> [!important] v4 范围校准
> 核心假设保留，但文献边界必须收窄：recovery selection 本身已有先例；本工作研究的是**固定 detector 的 alert 分布上，异质 recovery operators 的 matched-state counterfactual value**。主实验在原六个 recovery macro 之外加入 `Continue / 不干预`，并以置信区间版本的 kill criterion 取代上面的 85% 单条件。旧条件保留在这里仅作为 v3 历史记录。

## Refined one-liner

在固定 detector 的 alert 分布上，恢复不是"统一重试"的单动作问题，而是包含"不干预"在内的受约束动态决策：**同 checkpoint 全分叉测量每个 recovery operator 的真实终局价值，再把这张 counterfactual outcome matrix 蒸馏成部署时无需分叉的 selector。**

工作标题可收紧为：**MismatchTriage: Measuring and Closing Recovery-Selection Regret in GUI Agents**。

## Motivation：已知、推测与待测量量

### 已知

- [[Papers/2505-BacktrackAgent]] 的恢复固定为回退一步并重写动作。其 detection precision / recall 为 75.12% / 43.58%；全部动作中 8.48% 是被检测到的真错，只救回 2.37%，另有 0.78% 原本正确的动作被恢复机制改坏；input 动作 IoU / Text 分别下降 1.60 / 2.00。恢复既能救回，也能净伤害。
- [[Papers/2604-VeriGUI]] 显示 1,265 次执行中 72.3% 的失败来自重复无效动作导致的 timeout，但其 failure idempotency 设定主要覆盖"动作失败且屏幕不变"，不覆盖 unintended navigation、partial transition、crash 等 non-idempotent mismatch。
- [[Papers/2605-GUIRobustEval]] 已把恢复能力独立成 1,216 个 case、11 类错误、depth 0/1/3/5 的 benchmark，并用分支合成约 80 万恢复样本；即便专门训练，Error Awareness 仍只有 58.8%，depth-5 Post-Error Success 只有 33.2%。这证明 recovery 是实问题，但不证明异质恢复动作之间存在 selection gap。
- [[Papers/2607-TSR]] 的 transition-aware state update 在 MobileWorld 提升 9–12pp，却在 AndroidWorld 的一个 backbone 上下降 3.45pp，且移除 transition component 反而超过 baseline。恢复性干预的价值具有明显条件性，这是 selection heterogeneity 的间接证据。
- [[Papers/2605-SaaSBench]] 中最强模型 checkpoint success 43.9%，最终 resolved 仅 3.8%；checkpoint 数从 6 增至 18 时得分约 65%→27%。它支持长程错误累积的重要性，但不能被用来推断 recovery-selection gap 的大小。

### 尚未被现有证据证明

BacktrackAgent 的误伤、VeriGUI 的覆盖局限、TSR 的跨 setting 符号翻转只说明"统一干预未必总有益"。它们**没有直接证明**：在同一个 GUI mismatch 分布上，oracle 对异质恢复动作的逐点选择比最强固定策略高 ≥8pp。这个量必须由 matched-state intervention 测出，不能由 failure case 拼接推断。

### 问题拆解

```text
detect mismatch → select remedy → execute recovery macro → verify outcome
```

VeriGUI / OS-Oracle 主要研究第一层，WebRollback 研究是否 rollback 以及 rollback 到哪里，GUI-RobustEval / RoTS 研究从脏状态能否恢复。本工作只把第二层作为主贡献；detector、macro executor 与 outcome verifier 均固定并单独审计。

## Related Work 与 novelty 边界

| Work | 已经做了什么 | 本工作仍可守住的差异 |
|:--|:--|:--|
| [[Papers/2607-RobustExecAgenticRL]] | 在 frozen VLA 上用 PPO/MLP 从 `{Execute, Retry, Repair, Reset}` 中选择；LIBERO-Long 标准/扰动平均最高 +13.7/+39.2 | 非 GUI；无同状态全动作 outcome vector；无 oracle-vs-best-fixed gap；没有最强 fixed / rule baseline |
| [[Papers/2504-WebRollback]] | agent 决定 `continue / rollback`，并选择回退目标；live web +3–6pp | 只在 rollback 这一 operator family 内决策，URL 恢复也无法还原表单、购物车和 backend state |
| [ScreenAgent](https://www.ijcai.org/proceedings/2024/711) | 每步反思后在 `success / retry / reformulate` 间决定 | free-form reflection；无 matched-state counterfactual labels、best-fixed gap 或 terminal outcome matrix |
| [Human-Guided Harm Recovery](https://arxiv.org/abs/2604.18847) | 生成多个 recovery plans，再由 rubric verifier / learned reward model 重排 | 面向 harmful-action remediation；标签来自 human/judge preference，而非同 checkpoint 的环境终局 |
| [LongHorizonUI](https://kane2kang.github.io/LongHorizonUI/) | coordinate compensation → local replan → snapshot rollback → restart 的 staged fallback | 强 fixed escalation protocol；应成为 baseline，而不是被归为单一动作 |
| [[Papers/2604-VLAA-GUI]] | Loop Breaker 三级固定升级（2 次同动作→换模态、3 次同屏→换策略、SWITCH→拉黑重复动作），OSWorld 77.5% 当前 SOTA | 阈值硬编码、零 per-mismatch 自适应，fixed-escalation 家族最强新成员 = 必引 baseline；其消融正是 selection heterogeneity 的间接证据（Loop Breaker 在 Sonnet@100 仅 +0.04pp、Flash@15 反而 −6.15pp——固定协议价值高度条件化） |
| [[Papers/2602-VAGEN]] | verifier agent 在轨迹终态在线交互取证（shell/python/computer-use），OSWorld 判定 92.9% acc / 94.0% precision，破 judge ≤70% 天花板 | 不做恢复选择；但可直接用作本工作分叉测量的 outcome verifier \(V\)（终局判定精度是 \(Q_i(a)\) 估计的地基），比静态 judge 显著降低测量噪声 |
| [[Papers/2605-GUIRobustEval]] | 分支发现错误并合成恢复轨迹，建立 recovery benchmark | 不穷举同一点的异质 recovery operators，也不测 selection regret |
| [[Papers/2606-SRC]] / [[Papers/2410-ExACT]] | 用 rollback/search 产生训练数据，再蒸馏为无搜索 policy | `train-with-fork, deploy-fork-free` 已有先例；本工作的差异是完整 recovery-intervention matrix 与 terminal value supervision |
| [[Papers/2505-BacktrackAgent]] / [[Papers/2604-VeriGUI]] / [[Papers/2606-OSOracle]] | 检测失败后固定回退、self-correct 或 regenerate | 构成 shared-detector fixed baselines；不代表全部已有 recovery work |

**Novelty**: 3/5 — closest works: [[Papers/2607-RobustExecAgenticRL]], [[Papers/2605-GUIRobustEval]], [[Papers/2504-WebRollback]]。广义的 learned recovery selection、branching-for-recovery-data、search-to-policy distillation 都已有先例；可守的新颖性是三者的组合：**GUI 同 checkpoint 全 recovery intervention matrix + oracle-vs-best-fixed headroom 的直接测量 + outcome-value selector 的 fork-free 部署**。

更安全的 claim：

> 据我们所知，现有 GUI/computer-use 工作尚未在同一 detected-mismatch checkpoint 上，对一组预定义、语义不同且可执行的 recovery operators 进行可恢复快照分叉，以 terminal environment outcome 估计完整 counterfactual recovery vector；也未据此直接量化 candidate-set oracle 与最优固定恢复协议之间的 recovery-selection headroom。

不再声称：

- recovery action selection 本身无人研究；
- 所有现有方法都硬编码成一个动作；
- train-with-fork / deploy-fork-free 本身是新范式；
- counterfactual supervision 在 GUI 中无先例。

## Formal problem：先测 headroom，再测 deployable gain

令冻结的 base agent 为 \(\pi\)，固定 alert detector 为 \(D\)，每个 episode 的首次 alert 时刻为 \(\tau\)。selector 只能看到部署时可用的信息：

\[
X_\tau=(o_{\tau-1},a_{\tau-1},\hat e_{\tau-1},o_\tau,h_\tau,D_\tau),
\]

其中 \(\hat e_{\tau-1}\) 是动作执行前锁定的 expected effect，而不是看到结果后补写的解释。候选集 \(\mathcal A(X)\) 经过仅依赖可观察状态的 feasibility mask；它是预注册候选集，不宣称覆盖所有可能 recovery。

对每个 alert state \(x_i\) 和 macro \(a\)，从同一完整 checkpoint 分叉，之后统一使用冻结 continuation policy \(\pi_c\)，估计：

\[
Q^{\pi_c}_i(a)=P(\text{task success} \land \neg\text{harmful side effect}\mid do(a),x_i,\pi_c).
\]

主实验的 \(\pi_c\) 在首次 alert 干预后关闭额外 recovery，或使用所有分支共享的预注册 fallback，以隔离第一次 recovery choice。若有随机 rollout，action selection 与 value estimation 使用独立 replicates / cross-fitting，避免把随机好运当成 oracle 能力。

对 task template 等权后，分叉装置测得的是：

\[
H_{\text{fork}}=
\mathbb E_i\!\left[\max_{a\in\mathcal A(x_i)}Q_i(a)\right]
-\max_{\rho\in\mathcal K}
\mathbb E_i\!\left[Q_i(\rho(x_i))\right],
\]

其中 \(\mathcal K\) 只包含在相同单次干预算下返回一个 feasible macro 的 fixed policy（单一 macro 或 fixed feasible-action ranking）；best fixed 在 validation fold 选择后冻结。LongHorizonUI-style 多级 escalation 作为强 end-to-end baseline 单列，除非把它预注册成同预算的 composite candidate 并一并 fork，否则不混入 \(H_{\text{fork}}\) 的分母。\(H_{\text{fork}}\) 是 **fork-measured counterfactual headroom**，不是自动可部署的 task-SR 增益。逐点取单次 rollout 最大值的 realized oracle 只是 lottery ceiling，放附录，不作为主结果。

selector 不做普通 7-way hard classification，而是预测完整 value vector，并选择：

\[
\rho_f(x)=\arg\max_{a\in\mathcal A(x)}
\left(\widehat Q_f(x,a)-\lambda C(a)-\mu R_{\text{side-effect}}(a)\right).
\]

这自然处理 ties、动作成本、feasibility 与 `Continue` 最优的 false-alert 情形。同一 first-alert / frozen-continuation 协议下的 gap closure 为：

\[
R_f=
\frac{V_{\text{fork}}(\rho_f)-V_{\text{fork}}(\rho_{\text{fixed}})}
{V_{\text{fork}}(\rho_{\text{oracle}})-V_{\text{fork}}(\rho_{\text{fixed}})}.
\]

真正的部署收益另从任务起点闭环评测：

\[
G_{\text{deploy}}=V(\rho_f;\pi,D)-V(\rho_{\text{best-fixed}};\pi,D),
\]

每个任务只计一次，selector 在每次 alert 都可被调用。不能用局部 \(H_{\text{fork}}\) 作分母、用 end-to-end SR 作分子。

## Recovery macro set v4

| ID | Macro | 可执行定义与约束 |
|:--:|:--|:--|
| 0 | **Continue / accept** | 不执行 state-changing recovery；交还 frozen base agent。用于 detector false positive，也是 BacktrackAgent 误伤必须有的 control |
| 1 | **Retry exact** | 原动作语义与目标不变，只执行一次；文本输入使用 clear-and-set；submit / send / delete 等不可逆动作默认 mask |
| 2 | **Re-ground and retry** | 对同一语义目标重新运行 grounding，再执行一次；grounding 失败也计入 outcome |
| 3 | **Wait and re-observe** | 固定等待窗口后重新截图/读取 AX tree，不额外重放原动作；等待长度预注册并做小消融 |
| 4 | **Dismiss interruption** | 用固定 overlay detector + grounder 关闭顶层浮层一次；无可见浮层时 infeasible，而不是 oracle no-op |
| 5 | **Rollback / back** | 只使用部署时真实可用的 UI back 或显式 checkpoint API；训练期 emulator restore 不能冒充部署期 recovery action |
| 6 | **Reconcile and replan** | 一次固定 schema、固定 token cap 的 TSR/AgentProg-style state update，然后由同一 base agent 重决策；不得获得无限额外 reasoning budget |

每个 macro 必须版本化记录：输入、前置条件、最多 env steps、LLM calls、token cap、timeout、失败 fallback。fixed baseline 是固定 action ranking，选择最高优先级的 feasible macro；另报告共同可行子集，避免 gap 只来自"某动作在该点根本不可执行"。

## Experimental design v4

### Phase 0：fork fidelity 与 power pilot（先于所有算法）

1. 在 [[Papers/2605-MobileGym]] 的 JSON state fork 上做高内在效度 pilot；在 AndroidWorld + AW-Extend emulator 上做 realism transfer。MobileGym 不含真实广告、风控、推荐漂移和 latency spike，不能作为唯一 mismatch 来源。
2. 预注册完整可回滚任务子集。对同一 checkpoint 重复 restore/replay，比较 screenshot、AX tree、back stack、clipboard、app DB/files、OS state 与 task verifier；再做 branch-isolation test，报告 restore divergence rate 与剔除比例。
3. primary unit 是 task template；seed / episode 是重复测量，alert 是嵌套事件。先做 MDE / power analysis，再决定任务与 seed 数，不再把 300–500 个 alert 当作 300–500 个独立样本。
4. 成本重新按 `alerts × 7 macros × suffix steps × replicates` 预算。300–500 点、20 步 suffix 即使单次也约 4.2–7 万步；三次重复约 12.6–21 万步，不能预先承诺"4 万步、1–2 天"。

### Phase 1：alert state bank

1. 两个 base agents 分别运行任务。每步先生成结构化 expected effect，再执行动作；固定 stabilization rule 后由 no-change detector + expected-effect verifier 触发 alert。
2. 主研究对象明确写成 detector-alert distribution \(D_{\pi,D}\)，不外推到 detector 漏掉的全部 mismatch。从未触发 transition 随机抽样审计，报告 detector precision / recall，并按 app、action type、horizon 分层。
3. natural alerts 与 controlled / injected mismatch 分开报告；all alerts（含 false positives）是主分析，经独立确认的 true mismatch 是纯 recovery-selection 次分析。
4. first-alert-only 是主反事实样本，避免一条长失败轨迹贡献大量相关点；后续 alerts 只进顺序决策扩展实验。

### Phase 2：matched-state counterfactual matrix

1. 对每个 first alert，从同一 parent checkpoint 分叉所有 feasible macros，使用完全相同的 \(\pi_c\) 续跑到 terminal 或统一 step cap。
2. 对随机 continuation 使用 common environment seeds 与 adaptive replication；用独立 rollout 选 action 和估值，估计 \(Q_i(a)\) 及 CI，而不是把单次成败变成 one-hot 标签。
3. 保存完整矩阵：terminal success、unexpected side effect、恢复后 loop/timeout、env steps、LLM calls/tokens、latency、feasible mask。
4. 所有 sibling branches、相邻 screenshots、同 task template 与 seed 必须位于同一 split。

### Phase 3：gap / kill 决策（零训练）

比较：`Continue`、六个 fixed macro、validation-selected fixed ranking、LongHorizonUI-style fixed escalation、base-agent native recovery、candidate-set expected-outcome oracle。主表报告 conditional task success、Rescue vs Continue、Harm vs Continue、\(H_{\text{fork}}\)、feasible coverage、成本与 task-cluster 95% CI。

其中：

\[
\text{Rescue}_a=P(Y_a=1,Y_{\text{Continue}}=0),\qquad
\text{Harm}_a=P(Y_a=0,Y_{\text{Continue}}=1).
\]

### Phase 4：outcome-value selector

1. **Rule baseline**：screen-diff、overlay confidence、target visibility、elapsed time、action reversibility 的浅层 tree / threshold router。它回答 learned selector 是否只是规则就够。
2. **Prompted selector**：只看部署时的 \(X\)，输出 macro 与理由；few-shot examples 仅来自 train fold。
3. **Learned selector**：预测每个 macro 的 \(\widehat Q\) 与 side-effect / cost，不做单一 argmax class 标签。训练目标直接最小化 counterfactual regret。
4. 泛化测试至少三种：held-out task family、held-out app、leave-one-base-agent-out；再做一次 selector-on-policy recollection，检查 baseline-state-bank 的 distribution shift。

### Phase 5：end-to-end deployment

从 task reset 开始比较：recovery disabled、base-agent native recovery、best fixed ranking、fixed escalation、ScreenAgent-style free-form reflector、rule router、prompted selector、learned selector。BacktrackAgent / VeriGUI 若完整复现，放在独立 systems table，不把 shared-detector 的单 macro 冒充它们的完整系统。

主指标：task SR、\(\Delta\) best fixed、loop/timeout rate、unexpected side effects、alerts/task、env steps、LLM calls/tokens、latency。AndroidWorld / AW-Extend、两个 base agents 分开报告，再等权汇总；统计用 paired hierarchical bootstrap（task → seed），不把 alert 当 iid。

### Phase 6：事后分析

按 recovery outcome vector / \(\epsilon\)-near-optimal action set 聚类，只把类别作为实验输出。分析 error depth、action type、app、first/later alert 与 selector regret；不把聚类类别反过来当先验 taxonomy。

## Outcome-grounded supervision：准确说法

[[Papers/2607-EvoCUA15]] 的 Fig. 7 表明 PRM 分数可以上升而 terminal outcome 停滞甚至下降。本工作不使用 model-judged process score 作为 selector 标签，而使用同 checkpoint 分叉后的 state-based terminal verifier；这**移除了 EvoCUA-1.5 暴露的特定 PRM hacking 通道**。

但它不"免疫 reward hacking"：task verifier 仍可能 misspecify completion、遗漏副作用，emulator snapshot 也可能不等价。[[Papers/2605-MobileGym]] 发现 VLM judge 在 118 条 signal-bucket 轨迹中有 10.2% 错误，同时也单列了 4.7%–14.5% Unexpected Side Effects。因而标签必须联合 `completion + no harmful side effect`，并随机抽样做人审或第二 verifier 审计。

## Pre-registered decision rule

设 practically meaningful margin \(\delta=3\)pp，原始目标仍是 \(H_{\text{fork}}\ge8\)pp：

- **Gap confirmed / Go**：\(H_{\text{fork}}\) 点估计 ≥8pp，且 task-cluster 95% CI 下界 >3pp；随后训练 selector。
- **Fixed sufficient / Kill**：\(H_{\text{fork}}\) 的 95% CI 上界 <3pp，并且该结论在两个 base agents 与主要 benchmark / app strata 上成立。某单一动作在 ≥85% 点属于 \(\epsilon\)-near-optimal set 只作辅助描述，不能单独触发 kill。
- **Inconclusive**：CI 横跨 3–8pp、fork fidelity 未过关、detector audit 不足或主要 strata 方向冲突。不能把 power 不足包装成负结果。

如果大量点所有动作都失败，则它们会形成宽 tie，但不再虚假证明固定恢复足够：primary gap 只由 task-balanced expected outcome 与 CI 决定；另报告 recoverable-point coverage。

## Expected contribution if positive

1. **Measurement**：首次直接测量 GUI same-checkpoint heterogeneous recovery 的 candidate-set oracle / best-fixed headroom，并给出 Rescue/Harm 分解。
2. **Method**：用完整 counterfactual value vector 训练 cost- and side-effect-aware recovery router，而非普通 hard classifier。
3. **Protocol**：first-alert fork study + end-to-end deployment study 两层协议，避免把 hindsight oracle headroom冒充可部署增益。
4. **Artifact**：带 parent checkpoint、feasibility mask、七维 outcome vector、成本和副作用的 recovery state bank。

如果结果为 fixed sufficient，贡献降为：在明确 detector、可回滚任务覆盖和统计功效边界下，给 recovery-selection 研究一个可信负结论。若 fidelity / power 不足，则不宣称 negative result。

## Main risks after refinement

- **Novelty 已有强邻居**：RobustExec 已完成跨域 learned recovery selection；Human-Guided Harm Recovery、ScreenAgent、WebRollback 也否定宽 claim。论文必须以 matched-state gap measurement 为第一贡献，以 selector 为第二贡献。
- **Detector-conditioned scope**：selection 上限可能被低 recall detector 压住。用 all-alert / confirmed-mismatch / injected-mismatch 三层结果分离，不把 detector 问题偷偷算给 selector。
- **Fork 不完整**：remote backend、wall clock、network queue、auth/session、push 与外部副作用可能不在 emulator snapshot 内。fork fidelity 是前置 gate，不是事后 limitation。
- **Outcome sparsity / winner's curse**：长 suffix 可能使七个 macro 全失败；用 expected outcomes、独立 selection/evaluation replicates、adaptive replication 与 recoverable coverage 控制。
- **Macro 不同层级与成本**：额外 cognition 可能靠更多 token 获胜。预注册 macro budget，并报告 cost-aware 与 success-only 两套结果。
- **Policy shift**：selector 介入后会访问 baseline state bank 未覆盖的新状态。做 on-policy recollection，不默认跨 agent 泛化。
- **Verifier misspecification**：环境标签优于 PRM，但仍可能漏 side effect 或被 benchmark shortcut exploit；联合 USE 指标并审计。

## Evaluation — 2026-07-20 (v4, paper-library + novelty refresh)

| Dimension | Score | Notes |
|:----------|:-----:|:------|
| Novelty | 3/5 | RobustExec 已直接学习 recovery-operator selection；WebRollback、ScreenAgent、Human-Guided Harm Recovery 进一步压缩宽 claim。same-checkpoint all-operator outcome matrix + gap measurement 仍可守 |
| Feasibility | 4/5 | MobileGym 提供 exact JSON fork，零训练即可完成核心测量；但 Android emulator 的 full-state fidelity、10万级以上交互与统计功效必须先 pilot |
| Impact | 4/5 | gap 数字能裁决 GUI recovery routing 是否值得投入；positive / well-powered negative 都有方法学价值 |
| Risk | 3/5 | 核心假设未验证，且 detector bias、fork fidelity、winner's curse、policy shift 均可能改变结论；分阶段 gate 能控制沉没成本但不能消除风险 |
| Evidence | 4/5 | BacktrackAgent 误伤、TSR 符号翻转、GUI-RobustEval 低 recovery、RobustExec 跨域收益共同支持问题；没有论文直接证明 GUI 的 selection gap ≥8pp |
| **Total** | **18/25** | 原 21/25 高估了 Novelty、Evidence 与工程确定性；v4 的 claim 更窄，但更可证伪、更难被 closest work 击穿 |

**Reasoning**：idea 值得做，但不再是"发现一个无人研究的决策问题"，而是为一个已有零散方案、却缺少可识别比较的问题建立 counterfactual measurement。最强贡献取决于 Phase 0–3 能否证明 restore fidelity、统计功效和 \(H_{\text{fork}}\) 同时成立；selector 只有在这之后才值得训练。

**Suggested next action**：先做 30–50 个 first-alert checkpoints 的 no-training pilot，只回答四个问题：fork 是否等价、`Continue` 是否频繁最优、best fixed 与 candidate-set oracle 差多少、需要多少 task/seed 才能把 3pp 与 8pp 区分开。任何一个答案不理想，都应在训练 selector 前 pivot。

## History

- **v1（2026-07-16 上午）**：三分类先验 + 归因混淆率。
- **v2（同日下午）**：五分类 + 完备性三重验收。
- **v3（同日）**：去除分类学依赖，改为分叉测量 recovery-selection gap；评估 21/25。
- **v3.1（2026-07-20 上午）**：加入 EvoCUA-1.5 的 PRM failure、train-with-fork / deploy-fork-free 与第二轮 novelty search。
- **v4（2026-07-20，本版）**：发现 RobustExec、WebRollback、GUI-RobustEval、ScreenAgent、Human-Guided Harm Recovery 等近邻后收窄 novelty；加入 `Continue`、形式化 estimand、first-alert / end-to-end 双协议、expected-outcome oracle、fork fidelity gate、强 fixed protocol、cost-aware value selector 与 CI kill criterion。评分从 21/25 调整为 18/25。

## Evidence boundary / 待核查

- 原 v3 使用的 [[Papers/2605-MobileWorldModelGUI]] `verification pollution / -0.8` 数字未出现在当前 Paper 笔记中；正式写作前必须回查原文，本版不再用它支撑 claim。
- Learning to Explore / EAPO（[2605.08978](https://arxiv.org/abs/2605.08978)）已有 environment-verified rollback invocation learning，但 vault 尚无独立 Paper 笔记；它不覆盖异质 recovery matrix，却足以否定"learned recovery invocation 无先例"。
- `Reflection & Recovery` preference pairs 属于 EvoCUA（[2601.15876](https://arxiv.org/abs/2601.15876)），不是 EvoCUA-1.5；本版已删除该错误归因。
