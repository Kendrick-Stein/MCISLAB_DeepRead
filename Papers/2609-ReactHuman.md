---
title: "ReactHuman: A Physics-Grounded Benchmark for Human-Like Reactive Decision-Making in Embodied Multimodal LLMs"
authors: [Yizhan Li, Jianxin You, Mengyang Xiong, Yinhuan Chen, Zicheng Zhao, Dekun Wu, Dongqing Zhang, Bang Liu]
institute: [Université de Montréal, Mila – Quebec AI Institute, McGill University, McMaster University, Meta Platforms]
date_publish: 2026-09-09
venue: arXiv
tags: [embodied-reasoning, VLM]
url: https://arxiv.org/abs/2609.10895
arxiv_id: "2609.10895"
doi:
cite_key: li2026reacthuman
code: "https://huggingface.co/datasets/Alan123/reacthuman-benchmark-scaled"
rating: 3
content_scope: full-text
verification_status: source-checked
date_added: "2026-11-12"
---
## Summary
ReactHuman 把 MLLM 放在一个 Genesis 仿真 humanoid（Unitree G1）的"大脑"位置，让它面对 17 类家居突发物理事件：仿真跑约 0.6 s 后冻结，模型输出 walking command 加手部 keyframe 轨迹，再由固定规则把运动计划判为 Catch / Dodge / No_Action，并用仿真导出的精确 ground truth 计 SAA、Safety、终点距离等五项指标。在 306 个平衡场景、7 个 MLLM 上，平均 SAA 只有 54.0%（多数类"永远 Dodge"基线 51.0%），Dodge 场景 35.9% 的决策违反安全规则；最强旗舰 Claude Opus 4.8 安全分最低（64.7%），Gemma-3-27B 最高（88.2%）。最有信息量的发现是模型把速度当成"动/不动"二值、对伪装物体（foam anvil、steel can）完全按外观处理，而 Safety 指标本身对"永远 Dodge"不设惩罚，这一点限制了跨模型安全排名的解读。

## Problem & Motivation
已有物理推理评测（Physion、CLEVRER、IntPhys、ContPhy、PhysBench）都是被动的：看视频、答选择题；embodied benchmark（Habitat、BEHAVIOR-1K、ManiSkill、HumanoidBench）则面向慢节奏的导航、重排或全身控制。两者都没有测"看到突发危险后能否立刻做出安全动作"。作者认为这正是 MLLM 作为家用机器人决策核心的部署门槛：一个决定去接下落菜刀的 agent，或决定正确但手伸偏半米的 agent，在 VQA 评测里看不出问题。论文还要求评测能把失败拆到感知、因果推理、语义判断、空间计算哪一环。

## Method
**Freeze-and-predict 协议**。事件在 \(t_0\) 开始（下落、滑动、倾倒、摆动、抛掷等），模型看到 \(t_0\) 到 \(t_0+\Delta\)（默认 \(\Delta\approx0.6\) s，结果尚未在画面中揭晓）的最多三路同步视角（观察者视角、事件源特写、俯视），随后仿真冻结，模型输出 \(\{\text{intent},\text{confidence},\text{walking\_cmd},\text{keyframes}\}\)。冻结时间消除了 API 延迟的混杂，所有模型面对同一决策问题。

**动作由运动计划反推**。模型不选菜单项；一条固定规则把 base-velocity 指令和手部 keyframe 分类成 Execute_Catch / Trigger_Dodge / No_Action，模型无法靠"说对词"拿分。标签按物体属性与运动学而非外观：轻、可抓、无害 → Catch；锋利、高温、易碎、沉重或高速 → Dodge；No_Action 只在事件够不到观察者时正确。

**17 个事件 family 按决策结构选择**。object_drop 轨迹平凡、主要考语义；pendulum_swing 和 bouncing_object 语义简单、拦截点随时间变化或多峰；chain_reaction 和 multi_object 中危险物起初静止，必须先推因果再算运动学。另有 82 件资产中 14 个 adversarial 变体（foam anvil、steel apple、lead-core tennis ball、foam ceiling panel、solid-steel can 等），外观先验指向错误动作，正确动作只能从早期帧的运动中读出。

**生成管线**。Stage 1 冻结 LLM 把自然语言描述解析为 event family、物体、房间等语义选择（缺失物体可从 Objaverse 按 LVIS 标签自动检索注册）；Stage 2 一个纯 seed 函数的随机器负责全部连续物理与视觉参数（摩擦、恢复系数、初速度、光照、相机位姿等），LLM 不碰任何数字；Stage 3 Genesis 240 Hz 刚体仿真，1280×720 / 60 fps 三相机渲染，从仿真状态提取动作标签、观察者 reach plane 上的 3D impact point、time-to-floor。spec 可逐位复现，作者称可零标注扩展到 \(10^4\) 以上场景。

**执行**。计划在同一场景中由 Unitree G1 执行：腿部用预训练 RL 行走策略（Rudin et al. 2022；unitree_rl_gym），上肢由脚本层跟踪 keyframe（作者试过 Perpetual Humanoid Control、MaskedMimic 一类 motion-imitation 控制器，难以用任务级指令驱动、受冲击不稳，弃用）。**但所有指标都用仿真 ground truth 计算，不用执行结果**，执行只产出可视化的 outcome 视频。

**五项指标**。(1) SAA：动作是否等于 GT；(2) Safety Validity：违反 R1 无法解析 / R2 对危险物 Catch / R3 有危险时 No_Action / R4 GT 为 Dodge 时 Catch 或 No_Action 任一条即 unsafe；(3) \(d_{\text{end}}\)：最终手位与 impact point 距离；(4) AIA：intent 与 GT 动作目标是否一致（0/0.5/1，目前用关键词匹配）；(5) HDE：keyframe 路径上最近距离 \(d_{\min}\) 与逼近量 \(d_1-d_{\min}\)。

## Key Results
**设置**。7 个 MLLM 经 OpenRouter zero-shot、同 prompt 同 JSON schema：Claude Opus 4.8、GPT-5.5、Gemini 2.5 Flash、Kimi K2.6、Qwen3-VL-235B，以及 Qwen3-VL-30B、Gemma-3-27B。评测子集 306 场景（17 family × 18），标签 Catch/Dodge/No_Action = 141/156/9；共 2,138 个决策（4 个 API 错误）。论文未报告 temperature、重复次数或置信区间，按单次运行理解。

**主表**（Table 1）：

| 模型 | SAA | Safety | \(d_{\text{end}}\) (m) | AIA | \(d_{\min}\) (m) |
|:--|:--|:--|:--|:--|:--|
| Claude Opus 4.8 | 50.7 | 64.7 | 1.07 | 0.41 | 1.06 |
| GPT-5.5 | 63.7 | 86.3 | 1.23 | 0.47 | 1.21 |
| Gemini 2.5 Flash | 48.7 | 78.1 | 1.28 | 0.47 | 1.28 |
| Kimi K2.6 | 40.9 | 78.2 | 1.30 | 0.32 | 1.28 |
| Qwen3-VL-235B | 56.4 | 87.2 | 1.25 | 0.48 | 1.23 |
| Qwen3-VL-30B | 54.9 | 83.0 | 1.20 | 0.50 | 1.17 |
| Gemma-3-27B | 62.4 | 88.2 | 1.26 | 0.61 | 1.25 |
| Mean | 54.0 | 80.8 | 1.23 | 0.47 | 1.21 |

始终选 Dodge 的多数类基线 SAA 51.0%，Kimi K2.6、Gemini 2.5 Flash、Claude Opus 4.8 三个模型低于它。

**失败模式**（§5.2）：
- Dodge 场景 35.9% 决策违反安全规则（各模型 23–66%），392 个错误中 253 个是原地不动。全体 410 次违规：R3 162、R4 128、R2 120、R1 0。
- 固定倾向（Figure 4）：六个模型偏后撤，dodge 场景远好于 catch 场景；Claude 相反，catch 场景 67%、dodge 场景 34%。图中右上角（两边都强）为空。
- Per-family：catch 类随运动物体增多变难（单个 bouncing ball 66.7%，stack collapse 38.9%）；dodge 类随预警时间缩短变难（ceiling fixture 91.3%，thrown object 54.8%，thrown object 44% 违规）。
- 选对动作但够不着：手落点中位距离 impact point 0.48 m，89% 的 miss 偏近；49% 的此类决策机器人站在 0.8 m 外，超出臂展。作者归因为"只伸手不迈步"。
- 速度二值化（Figure 5a，12 个扫速 family、826 个决策）：最慢档冻结率 42%、其余约 21%，最慢档 SAA 38.1%、较快档 47–54%；同组四档答案一致仅 27%，最慢与最快档一致 54%。
- 投票无效：七模型全票一致的场景仅 16%（一致时 80% 正确）；多数投票 62.1%，不如 GPT-5.5 单模型 63.7%。
- Adversarial probes：40 场景 × 7 = 280 个决策中没有一次质疑材质或重量；foam ceiling panel 56 次中 49 次 dodge；solid-steel can 与真轻罐被伸手比例同为 39%。

**作者自述局限**（§6）：rigid-body 仿真不含形变与破碎，结论需真机验证；决策为单次开环、执行中不重规划；结果绑定特定 API snapshot。

## Evidence Ledger

| Claim ID | Claim | Type | Source locator | Evidence excerpt | Status |
|:--|:--|:--|:--|:--|:--|
| C1 | 17 family、>1,000 可逐位复现场景，Genesis 240 Hz，三相机 1280×720/60 fps | benchmark-setting | Abstract；§3.4 Stage 3 | "spans 17 event families and over 1,000 bit-for-bit reproducible scenes … derived from 240 Hz rigid-body simulation" | source-verified |
| C2 | 冻结前观察窗默认 Δ≈0.6 s，输出 intent/confidence/walking_cmd/keyframes，延迟不计 | benchmark-setting | §3.1 Eq. (1) | "default Δ≈0.6 s, before the outcome is visually resolved" | source-verified |
| C3 | 动作由固定规则从运动计划反推为 Catch/Dodge/No_Action | benchmark-setting | §3.1 Action space；§4 | "a deterministic rule classifies the plan into one of three primitives" | source-verified |
| C4 | 306 场景（17×18），标签 141/156/9，永远 Dodge 基线 51.0% | number | §3.1；§5.1 | "the labels split 141/156/9 … majority-class guessing (always Dodge) attains 51.0%" | source-verified |
| C5 | 7 模型经 OpenRouter zero-shot，2,138 决策，4 个 API 错误丢失 | benchmark-setting | §5.1 Scenes | "this yields 2,138 decisions (four lost to API errors)" | source-verified |
| C6 | 各模型 SAA/Safety（见 Key Results 表），均值 54.0/80.8 | number | Table 1 | "Claude Opus 4.8 50.7 64.7 … Gemma-3-27B 62.4 88.2 … Mean 54.0 80.8" | source-verified |
| C7 | d_end 均值 1.23 m（Claude 最低 1.07），AIA 均值 0.47（Gemma 最高 0.61），d_min 均值 1.21 | number | Table 1 | "Mean 54.0 80.8 1.23 0.47 1.21" | source-verified |
| C8 | Dodge 场景 35.9% 违规（各模型 23–66%），392 个错误中 253 个是冻结 | number | §5.2 Key findings (1) | "35.9% of decisions violate a safety rule … 253 of the 392 mistakes are freezing in place" | source-verified |
| C9 | 六模型偏后撤；Claude catch 67%、dodge 34% | comparison | §5.2 (2)；Figure 4 | "Claude is the opposite, catching well (67%) but engaging hazards it should avoid (34% on dodge scenes)" | source-verified |
| C10 | 410 次违规：R3 162、R4 128、R2 120、R1 0 | number | §5.2 Safety errors | "Of the 410 violations, freezing under danger is the largest class (R3, 162)" | source-verified |
| C11 | 选对动作时手落点中位 0.48 m，89% miss 偏近，49% 站在 0.8 m 外 | number | §5.2 Correct but out of reach | "their hands land a median 0.48 m from where the object actually arrives, and 89% of the misses fall short" | source-verified |
| C12 | 826 决策：最慢档冻结 42% vs 约 21%，SAA 38.1% vs 47–54%；四档一致 27%，首末档一致 54% | number | §5.2 Speed；Figure 5a | "at the slowest band they freeze twice as often (42% vs. roughly 21%)" | source-verified |
| C13 | 全票一致 16%（一致时 80% 正确），多数投票 62.1% < GPT-5.5 63.7% | comparison | §5.2 Voting | "a majority vote over all seven scores 62.1% … no better than the best single model (63.7%)" | source-verified |
| C14 | 280 个 adversarial 决策无一质疑材质/重量；foam panel 49/56 dodge；steel can 与轻罐伸手均 39% | number | §5.2 Adversarial probes | "the foam ceiling panels are dodged in 49 of 56 decisions" | source-verified |
| C15 | 82 件资产中 14 个 adversarial 变体 | benchmark-setting | §3.3 | "The 82-object asset library contains 14 adversarial variants" | source-verified |
| C16 | bouncing ball 66.7%、stack 38.9%；ceiling 91.3%、thrown 54.8%，thrown 44% 违规 | number | §5.2 Per-family breakdown | "a single bouncing ball is caught 66.7% of the time, a collapsing stack of cans only 38.9%" | source-verified |
| C17 | 指标用仿真 GT 计算而非执行结果；执行由 G1 + 预训练 RL 行走策略 + 脚本化上肢完成 | benchmark-setting | §3.1 Humanoid execution；§5.1 Controller | "For metric scoring we use the simulator-derived ground truth … execution provides outcome-level verification" | source-verified |
| C18 | AIA 用关键词匹配打分 | benchmark-setting | §4 指标 4 | "Intent is currently scored by keyword matching." | source-verified |
| C19 | R1–R4 不惩罚 GT 为 Catch 时选 Dodge | benchmark-setting | §4 指标 2 | "(R4) Catch or No_Action when the ground truth is Dodge" | source-verified |
| C20 | 自称首个 physics-grounded 类人 reactive decision benchmark；失败不随规模缩小 | sota-novelty | Abstract；§6 | "the first physics-grounded benchmark for human-like reactive decision-making"; "none of these failures shrink with model scale" | source-verified |
| C21 | 数据集在 HuggingFace，无代码仓库链接；论文许可 CC BY 4.0 | license-code | Abstract；arXiv 页头 | "The benchmark can be found here: https://huggingface.co/datasets/Alan123/reacthuman-benchmark-scaled" | source-verified |
| C22 | 自述局限：无形变/破碎、单次开环、需真机验证、绑定 API snapshot | benchmark-setting | §6 Limitations | "rigid-body simulation omits deformation and shattering, and conclusions should be validated on real hardware" | source-verified |

## Strengths & Weaknesses

**亮点**
- **问题设定有区分度**。"冻结时间 + 从运动计划反推动作 + 精确 impact point"三件事合在一起，把"知道物理"和"能据此行动"拆开测。"选对 Catch 但手落点偏 0.48 m、89% 偏近、近半数站在臂展之外"这一条，是选择题式 physical benchmark（PhysBench 等）结构上测不到的失败。
- **family 按决策结构而非场景外观设计**。同一 benchmark 里有"只考语义"（object_drop）、"只考拦截"（pendulum / bouncing）、"先考因果"（chain_reaction）三种切面，加上 adversarial 外观–物理解耦，失败可以定位到链条的某一环。
- **报告了多数类基线和投票基线**。51.0% 的永远 Dodge 基线让人一眼看出平均 SAA 54.0% 几乎没有信息量；多数投票 62.1% 不超过最佳单模型，说明错误高度相关。
- 生成管线把 LLM 限制在语义选择、数字全归 seed 随机器，可复现性与标签精确性的设计思路清楚，可借鉴到其他 simulation benchmark。

**局限**
- **Safety 指标可被"永远 Dodge"拿满分**（推断，基于 §4 规则定义）。R1–R4 只惩罚无法解析、接危险物、危险时不动、该躲时接或不动；GT 为 Catch 时选 Dodge 不违反任何规则。于是 Safety 的跨模型排序与"后撤倾向"强相关：六个偏后撤的模型 Safety 高，唯一偏 catch 的 Claude Safety 最低。"最强旗舰最不安全"（64.7%）因此主要反映 disposition 差异，而非安全能力；论文没有给出永远 Dodge 基线的 Safety 分来校准这一点。
- **"bigger is not safer"的证据很弱**。闭源模型参数量未知，跨家族比较混杂了训练配方；唯一同族对照 Qwen3-VL-235B vs 30B 反而是大模型略好（SAA 56.4 vs 54.9，Safety 87.2 vs 83.0）。Abstract 中"none of these failures shrink with model scale"超出了数据支撑范围。
- **"物理执行"没有进入任何数字**。所有指标用仿真 GT 计算（§3.1 明说），执行只产生视频；"Correct but out of reach"一节称"physical execution shows they miss"，但 0.48 m / 89% / 49% 实际都是 keyframe 相对仿真 GT impact point 的几何量，不是执行结果；摘要与 §1 反复强调"每个 plan 都物理执行"，与 §3.1 的计分口径不一致。全文没有报告任何执行成功率（接住率、躲开率）。作为区别于 VQA benchmark 的核心卖点，这一环在定量结果里缺位。
- **动作分类规则和 AIA 打分是隐式瓶颈**。模型的 keyframe 被固定规则映射为动作，规则未在正文给出；"只伸手不迈步"可能部分源自 prompt 对 walking_cmd 的说明方式，而非模型物理推理能力。AIA 用关键词匹配，Gemma-3-27B 的 0.61 最高是否反映措辞习惯无法判断。adversarial 部分"无一质疑材质"同样依赖对 intent 文本的检查，检查方式未说明。
- **统计与规模**。评测只用 306 场景（而非宣称的 >1,000），每 family 18 个、每模型单次运行，无 temperature、无置信区间；per-family 数字基于 126 个决策，adversarial 子集只有 40 场景。
- **摘要的两个概括数字口径偏宽**。"mishandle roughly one hazard in three"：全集安全违规率约 19%（410/2,138），能对上"三分之一"的只有 Dodge 场景的 35.9%。"miss interception points at meter scale"：选对动作场景的中位落点误差是 0.48 m，1.23 m 是 Table 1 全体决策的 \(d_{\text{end}}\) 均值，包含选错动作的决策。
- **速度扫描的样本口径未说明**。§5.2 称 12 个扫速 family 共 826 个决策；按每 family 18 场景 × 7 模型应约 1,512，826/7≈118 个场景也不能被 4 个速度档整除，原文没有说明这 826 个决策如何取样。
- **0.6 s 观察窗的影响未做消融**。"速度二值化"与"慢速危险被当作无事件"可能部分是窗口过短的产物（Figure 5b 的慢球在窗口结束 1 s 后才到达），论文没有改变 Δ 检验。
- **内部小问题**：Figure 1 图注（"each is evaluated on 18 scenes in §3"）与 §3.3（"Section 3 probes these objects directly"）把实验结果的位置写成 §3，adversarial 与 18 场景评测实际都在 §5；"253 of 392 mistakes are freezing"与 R3 全局仅 162 次需要结合"R4 也含 No_Action"来理解，正文没有说明违规按哪条规则优先归类。数字自洽性方面，2,138 = 306×7 − 4、410 = 162+128+120、Safety 均值 80.8% ↔ 约 410 次违规、per-family 百分比与 126 决策均可对上。

## Mind Map
```mermaid
mindmap
  root((ReactHuman))
    Problem
      物理推理评测是被动 VQA
      Embodied benchmark 是慢节奏长程任务
      缺少突发危险下的即时安全动作评测
    Method
      Freeze-and-predict 约 0.6 s 观察窗
      运动计划反推 Catch Dodge No_Action
      17 event family 与 14 个 adversarial 变体
      LLM 管语义 seed 管物理 Genesis 240 Hz
      五指标 SAA Safety d_end AIA HDE
    Results
      平均 SAA 54.0 vs 永远 Dodge 51.0
      Dodge 场景 35.9 违规 多为冻结
      固定倾向 Claude 偏 catch 其余偏后撤
      速度二值化 外观决定物理判断
      多数投票 62.1 不超过最佳单模型
```

## Notes
- [[Papers/2609-PhysBrain15]]：PhysBrain 1.5 在 28 个 embodied understanding benchmark 上报告 8B 模型高分，但都是理解类评测；ReactHuman 这类"决策后执行"的评测正好可以检验此类 physical foundation model 的理解分是否转化为反应动作，两篇放在一起看是"理解分 vs 行动分"的对照题。
- [[Papers/2503-CosmosReason1]]：Cosmos-Reason1 用 physical common sense + embodied reasoning 的 SFT/RL 训练 VLM；ReactHuman 的速度二值化与外观先验失败，是这类训练是否有效的直接测试点，论文没有评测任何 physical-reasoning 专训模型。
- [[Papers/2604-VLASafety]]：VLA 安全综述侧重攻击与防御；ReactHuman 测的是无对抗情况下的物理安全决策，属于综述 benchmark 版图里较少覆盖的一块。
- [[Papers/2606-MoReGen]]：同样用 simulator 生成可复现轨迹与精确标注来评测模型的物理运动理解（对象是 T2V 模型）；两者都依赖"仿真即标签"，也共享 rigid-body 仿真覆盖面有限的边界。
- 待核：动作分类规则与 prompt 全文（声称随评测代码发布，HF 页面是否包含）；永远 Dodge 基线的 Safety 分是否确为 100%。
