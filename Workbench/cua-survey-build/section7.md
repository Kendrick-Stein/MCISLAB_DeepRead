### 7.1 Pre-training

GUI agent 的 pre-training 已从通用视觉语言建模转向跨平台 GUI grounding：先学习元素、指令与坐标之间的对应关系，再通过 action fine-tuning 接入可执行动作空间。这一步解决视觉—动作先验不足的问题，但不会自动带来长程规划与错误恢复能力。

某工作发现，OS-ATLAS 使用覆盖 web、mobile 与 desktop 的 13.58M GUI elements、约 2.3M screenshots 构建 grounding corpus；其消融显示 web-only pre-training 不能充分迁移到 desktop/mobile，说明跨平台覆盖比单纯扩大单域数据更关键。随后使用 unified action space 做 multi-task action fine-tuning，使 grounding prior 能进入不同平台的动作接口。该证据来自单一工作，不能升格为所有 backbone 的通用 scaling law。[[Papers/2410-OSAtlas]]

### 7.2 SFT

SFT 仍是 GUI agent 获得动作语法、输出格式、界面知识与基本轨迹模式的主要入口；它把通用模型变成能被环境执行的初始 policy，却难以覆盖恢复行为和长尾状态。当前发展方向不是取消 SFT，而是让监督目标更贴近 action token、grounding token 与部署时的 context policy。

OS-ATLAS 在 grounding pre-training 后使用跨数据集 action fine-tuning，将平台异构动作统一为共享语义。[[Papers/2410-OSAtlas]] GUI-Libra 进一步混合 reasoning-then-action 与 direct-action 数据，并提高 action/grounding token 的训练权重，以缓解长 CoT 对 grounding 的干扰；这是某工作的条件性发现，不代表 reasoning 普遍有害。[[Papers/2602-GUILibra]] EvoCUA 则把 cold-start SFT 限定为行为先验注入，随后才由 rejection sampling 与 preference optimization 消费 agent 自身产生的经验。[[Papers/2601-EvoCUA]]

### 7.3 Behavior Cloning

Behavior Cloning 的关键作用不是重复一般 SFT，而是在目标动作不属于当前 policy support 时，把 teacher correction 直接写入可采样行为。它解决 sparse reward 无法强化"从不出现的正确动作"的冷启动问题，随后才适合用 policy optimization 调整这些动作的概率。

TeachStop 的 SA-OPSD 将 clipped GRPO 与 advantage-gated behavior cloning 结合：GRPO 抑制已采样的坏动作，behavior cloning 注入 verifier teacher 给出的 correction。该工作中，reward-only 无法安装 base policy 从不生成的 `done()` 行为，而 distillation signal 可以；这一结果来自单一 35B policy 与确定性 web mirrors，应表述为支持边界，而非领域共识。[[Papers/2607-TeachStop]]

### 7.4 Curriculum and Multi-Task

Curriculum 已从预设的任务难度排序演进为 policy-relative task allocation：固定 multi-task 训练先解决平台与动作空间异构，失败驱动课程再扩充学习材料，online frontier sampling 最后根据当前成功率动态分配 rollout。每一步提高了训练信号密度，同时暴露出新的问题——静态难度会随 policy 更新而失效，生成任务也可能可执行但语义无效。

OS-ATLAS 用 unified action space 支撑跨平台 multi-task fine-tuning。[[Papers/2410-OSAtlas]] WebRL 将失败轨迹转成下一轮课程任务，并联合 ORM、KL 约束和经验回放稳定在线更新。[[Papers/2411-WebRL]] AgentGym-RL 通过逐步扩大 interaction horizon，避免初期直接训练长轨迹导致优化崩溃。[[Papers/2509-AgentGymRL]] SCALECUA 与 EvoCUA-1.5 则按当前 policy 的 success frontier 选择任务。[[Papers/2607-SCALECUA]] [[Papers/2607-EvoCUA15]] 已知（多篇独立支持）：task difficulty 是 policy-relative 变量；未知的是不同环境中可学习区间能否由统一阈值描述。

### 7.5 Preference Optimization

Preference optimization 将失败经验从轨迹级排序细化到关键决策点，使监督集中在"从哪里开始走错"而非整段输出的总体优劣。它降低了长轨迹中的信用稀释，但依赖可比较状态、可靠分叉定位以及对 action aliasing 的处理。

EvoCUA 在成功与失败轨迹的首个分叉点构造两类 step-level offline DPO 数据：Action Correction 比较错误动作与正确动作，Reflection & Recovery 比较恢复策略与盲目继续。[[Papers/2601-EvoCUA]] 该方法说明失败轨迹可以转化为边界监督，但不能证明单一示范动作是某状态下唯一正确选择；GUI-Libra 所揭示的 partial verifiability 正是这种离线偏好数据的主要边界。[[Papers/2602-GUILibra]]

### 7.6 Reward and Process Models

长程 GUI task 的核心矛盾是 outcome reward 可信但稀疏，process reward 密集却容易受到 judge bias、partial observability 与 reward hacking 污染。现有路线可按对 outcome-only reward 的改造深度形成一条因果链。

改动最小的是 first-failure 或 fork-point 定位：不改变 reward 形式，只把成功与失败轨迹的最早分叉转为局部监督，但需要可比较的成对轨迹。[[Papers/2601-EvoCUA]] Milestone/progress reward 进一步把可验证中间状态转成中间信用，信号更密集，却可能奖励与最终目标脱钩的局部进展。Tree rollout 利用兄弟子树的 outcome 差异生成 step-level signal，把 reward-design 成本转移到环境的 fork、reset 与并行能力。最后，interactive verifier 主动读取截图、文件、进程或 GUI 状态，以更高验证成本换取 hidden evidence。[[Papers/2602-VAGEN]]

AgentRewardBench 表明 rule-based evaluator 与通用 LLM judge 会分别产生漏判和误判，因此 reward model 不能默认等同于 ground truth。[[Papers/2504-AgentRewardBench]] EvoCUA-1.5 进一步报告 PRM score 上升而 executable outcome 停滞的负结果，说明 process score 必须锚定环境状态变化。[[Papers/2607-EvoCUA15]] VAGEN 支持主动取证路线，但只验证了 evaluator 与 Best-of-N，尚未证明其成本与攻击面能承受大规模 RL 闭环。[[Papers/2602-VAGEN]]

### 7.7 Offline RL

Offline optimization 通过静态轨迹、rejection sampling 与 preference pairs 降低真实环境 rollout 成本，适合 reset 困难或交互昂贵的 GUI 系统。它解决经验利用问题，却无法直接观察当前 policy 导致的新状态、恢复路径与分布漂移。

EvoCUA 的离线路线依次使用 cold-start SFT、成功轨迹 RFT 与首分叉 step-level DPO，并强调数据价值取决于生成它的 policy。[[Papers/2601-EvoCUA]] GUI-Libra 面对离线 step-wise verification 的 partial verifiability，保留 KL trust region 并缩放不可靠负梯度；其结论是"去 KL"只适用于 reward 充分可验证的条件，不能直接迁移到多解 GUI 状态。[[Papers/2602-GUILibra]] 已知的是 offline learning 能高效消费已有经验；未知的是离线 step metric 在何种 verifier coverage 下足以预测 live end-to-end success。

### 7.8 Online and Multi-Turn RL

Online RL 把策略更新置于真实状态转移中，能够学习恢复、终止和长程决策，却同时放大环境吞吐、reset、reward coverage 与统计方差问题。算法名称不是首要选择依据；应先诊断 policy support、任务边界、rollout group 和环境可靠性。

下表是前置诊断清单而非 optimizer 排名。任何一项不满足时，应先补数据、修 verifier 或改环境，而不是继续调整 policy-gradient 变体。

| 前置变量 | 诊断 | 失败时优先选择 | 证据 |
|:--|:--|:--|:--|
| Sampling headroom | base policy 的 pass@k 是否明显高于 pass@1 | 无 headroom 时补 SFT、mid-training 或 expert data | [[Papers/2607-GRPONullWebAgent]] |
| Group reward variance | rollout group 是否全失败或全成功 | 全失败时注入 expert trajectory 或做 curriculum | [[Papers/2607-MAG]] |
| Reward coverage | validator 是否覆盖关键中间态与副作用 | 先改 verifier，不把噪声直接放进梯度 | [[Papers/2504-AgentRewardBench]] |
| Environment throughput | reset、并行与失败恢复是否可承受 | 先改环境、用 simulator，或转 offline/distillation | [[Papers/2509-AgentGymRL]]、[[Papers/2511-DreamGym]] |
| Policy-relative data | 数据对当前 policy 是否仍有学习信号 | 动态筛选或重生任务，不复用静态高质量集 | [[Papers/2607-EvoCUA15]] |
| Verifiable task frontier | task 是否可执行、可判定且成功率接近学习边界 | 先做 task/validator audit，再按 capability 动态分配 rollout | [[Papers/2607-SCALECUA]] |
| Replication variance | 增益是否跨 data draw、run 与 seed 保持方向 | 报告 crossed data-draw × seed，而不是单次最好结果 | [[Papers/2607-TeachStop]] |

GRPONull 的受控阴性结果给出 support 边界：SFT 已掌握的任务上 GRPO 没有可信提升，而在仍有 sampling headroom 的任务上，同一 pipeline 增加 22 percentage points。RL 因而更像已有行为分布的重塑器，而不是可靠的零起点技能注入机制；该结论目前只在论文测试的小模型与 MiniWoB 条件下成立。[[Papers/2607-GRPONullWebAgent]]

TeachStop 将复现性提升为训练方法的一部分：最难 cell 中 data draw 解释 48% 方差，单 run 约有 30% 概率进入 failure mode，在论文测得的高方差 regime 中，同量级 improvement 约三分之一概率会报告错误方向。固定 `done()` token 的 held-out emission 为 0.97±0.06，coordinate grounding 为 0.53±0.35，开放式 generative fill 仅为 0.14±0.04；局部修复也只有在它是任务唯一剩余 blocker 时才转化为 end-to-end success。[[Papers/2607-TeachStop]]

### 7.9 RLVR

RLVR 将训练扩展性建立在可自动判定的 reward 上：输出可解析、状态可检查、任务可重复执行时，agent 可以在较少人工标注下获得大量策略更新。其瓶颈已从 optimizer 转向 verifiable task supply、validator coverage 与 environment throughput。

UI-R1 代表局部结构化动作上的 rule-based RLVR：action type、coordinate 与 format 可以直接计算 reward，但该证据主要覆盖单步 action prediction，不能外推到任意长程任务。[[Papers/2500-UiR1EnhancingEfficient]] GUI-Libra 则给出反例条件：当多个动作都可能正确而 verifier 只认可示范动作时，step-wise RLVR 只有 partial verifiability，KL trust region 反而有助于限制错误负梯度。[[Papers/2602-GUILibra]]

SCALECUA 展示了 algorithm–data–system co-design 的正面上限：VeriGen 生成 24K+ candidate tasks 并筛成近 3K RL tasks，Frontier Sampling 将 rollout 分配给 success rate 接近 0.5 的学习边界，Visual Context Segmentation 同时改善信号与吞吐。Qwen3.5-9B 在 OSWorld 达到 68.7%，训练加速 2.83 倍；移除 VeriGen 后降至 43.9%，说明 headline gain 的主要来源是 verified task supply，而非更换 policy-gradient 公式。160 条跨 domain 生成轨迹的人类审计中，task validity 在 OSWorld 与 ScienceBoard 分别只有 82.0% 和 58.3%，因此"judge 可执行"不能等同于"任务有效"。[[Papers/2607-SCALECUA]]

### 7.10 Self-Training and Rejection Sampling

Self-training 把当前 policy 生成的经验重新变成监督数据，rejection sampling 则用 verifier 选择值得学习的成功或恢复轨迹。它们解决人工 demonstration 不可扩展的问题，但 selector bias 会被重新写入 policy，静态 off-policy 样本也会随能力变化而失去学习价值。

EvoCUA 按任务难度分配 rollout budget，对成功轨迹做 step-level 去噪并执行 rejection sampling fine-tuning；失败轨迹不直接混入成功集合，而是保留 reasoning 与 failure termination，再转成首分叉偏好对。[[Papers/2601-EvoCUA]] VAGEN 用 interactive verifier 支持 Best-of-N rejection sampling，但没有进行真实 RL 训练，因此只能证明 verifier-guided selection 的可行性，不能证明长期 self-training 不会放大 verifier bias。[[Papers/2602-VAGEN]]

### 7.11 Data Flywheel and Self-Evolution

Data flywheel 将 rollout、验证、筛选、更新与新任务生成闭合为循环；self-evolution 则把改进对象从 model weights 扩展到 memory、tool/skill 和 workflow/harness。扩展改进对象可以降低频繁参数更新的成本，却使验证独立性成为共同约束。

下表回答不同 self-improvement 路线究竟修改什么，以及错误会在哪里累积。

| 路线 | 改进对象 | 代表机制 | 主要风险 |
|:--|:--|:--|:--|
| Parameter update | model weights | RFT、online RL、self-distillation | verifier bias 被固化进权重 |
| Context / memory | retrieved experience | workflow、failure pattern、state memory | 错误抽象与检索漂移 |
| Tool / skill | executable asset | API skill、runtime patch | 权限扩大、跨版本失效 |
| Workflow / harness | control flow | planner、retry、visual search、terminal assist | benchmark overfitting 与安全偏航 |

EvoCUA 将 task、initial state 与 executable validator 共生成，再用异步 sandbox rollout 产生新经验；EvoCUA-1.5 进一步说明 task value 与 PRM reliability 都随 policy 改变。[[Papers/2601-EvoCUA]] [[Papers/2607-EvoCUA15]] 因而不能把"生成更多数据"等同于"形成正向 flywheel"，每轮更新都需要独立、可追溯且难以被当前 policy 操纵的 gate。

SKILL.nb 是非参数路线的具体实例：workflow step 只有通过 environment-observable gate 才被固化，并按 repair burden 自动 demote 或 retire。在 GitLab 版本漂移测试中，frozen-vs-fresh 差距为 −1.7/+0.6 percentage points；去掉 gates 后，hard subset 的回归率由完整系统的 3.3% 上升到 18.6%，说明收益主要来自验收闸门，而不是单纯生成可执行 skill。[[Papers/2606-SkillNb]]

### 7.12 Continual Learning

当前 vault 覆盖薄弱，见 gaps

### 7.13 Distillation and On-Device

Distillation 在训练侧用于把 policy support 之外的 teacher correction 写入较小模型，on-device 路线则试图降低运行时参数量、延迟与外部服务依赖。两者的共同问题是压缩不能只保持单步 grounding，还必须保留长程状态、恢复和安全边界。

TeachStop 表明 self-distillation 可以安装 sparse reward 无法自行发现的 correction，但开放式生成行为的稳定性显著弱于固定动作。[[Papers/2607-TeachStop]] Ferret-UI Lite 探索 compact end-to-end on-device GUI agent，并结合混合数据、RL 与 inference-time visual tools；当前笔记足以支持其研究定位，却缺少 source-verified latency、energy、memory footprint 与长期真机评测，因此不能把小参数模型直接表述为已完成可部署验证。[[Papers/2500-FerretUiLiteLessons]]

### 7.14 Inference-Time Planning, Reflection, Search

Inference-time optimization 不修改权重，而是通过规划、主动验证、局部搜索、回退与 workflow fallback 改变一次任务中的控制流。它能在训练覆盖之外处理错误，却会增加环境交互成本，并受到不可逆动作与 verifier 误判的约束。

BacktrackAgent 在每步动作后检查 outcome page，由 rule verifier 与 learned judger 决定是否回到执行前状态并重写动作；其证据支持"真实状态转移比 simulated outcome 更适合驱动 reflection"，但回退深度固定为一步，且 benchmark 环境绕开了真实 GUI 的不可逆操作。[[Papers/2505-BacktrackAgent]] VAGEN 将验证者本身变成能够调用 screenshot、shell、Python 与 GUI action 的 agent，使 inference-time search 可以主动获取 hidden evidence。[[Papers/2602-VAGEN]] SKILL.nb 则在 code、natural-language procedure 与裸意图之间执行 gate-conditioned fallback，将 search 从动作级提升到 workflow implementation 级。[[Papers/2606-SkillNb]]

当前证据支持的是受控环境中的局部 backtracking、主动取证和分层 fallback，而不是任意深度的通用 GUI tree search。未知问题包括：如何在发送、删除、支付等不可逆动作后安全回滚，以及如何把搜索预算分配给真正存在分支价值的 decision point。

### 7.15 Open Problems

Learning and Optimization 的主要未解问题不是缺少更多 optimizer，而是无法可靠区分 skill deficit、credit failure、validator error、environment fault 与 stale context。相同的 0 reward 可能对应完全不同的干预，错误归因会把数据、reward 或系统故障直接写入 policy。

- **Support-aware method selection**：在训练前报告 pass@k、group reward variance 与 teacher-action coverage，区分应使用 SFT/behavior cloning 还是 RL。[[Papers/2607-GRPONullWebAgent]] [[Papers/2607-MAG]] [[Papers/2607-TeachStop]]

- **Verifier validity beyond executability**：同时审计 false positive、false negative、side effects 与 task semantic validity；程序可运行、judge 可判定和用户目标合理是三个不同条件。[[Papers/2504-AgentRewardBench]] [[Papers/2607-SCALECUA]]

- **Outcome-anchored credit assignment**：PRM、milestone 与 tree-derived signal 都应回到 executable state change 或 counterfactual outcome 检查，避免 process score 自我强化。[[Papers/2607-EvoCUA15]]

- **Replication as a training requirement**：最低报告协议应包含 held-out trajectories、multi-seed、multi-data-draw、run-to-run variance 与 state-level oracle；单次最好结果不足以支持算法因果结论。[[Papers/2607-TeachStop]]

- **Continual and deployment evidence**：跨 UI version、domain、resolution 与 device constraint 的长期适应证据仍薄弱；需要同时测新分布适应、旧能力保持、回归、安全与真实运行成本。

- **Joint algorithm–data–system accounting**：应分别报告 optimizer、task supply、sampling policy、context policy、verifier 与 rollout infrastructure 的边际贡献，避免把系统级扩展收益归因于单一 RL objective。[[Papers/2607-SCALECUA]] [[Papers/2607-EvoCUA15]]