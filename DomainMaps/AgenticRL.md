---
title: Agentic RL Domain Map
last_updated: "2026-04-28"
status: active
paper_count: 90
survey: "[[Topics/CUA-Survey]]"
---

## 核心定义

**Agentic RL** = 将强化学习应用于智能体训练，通过环境交互、反馈信号、策略优化提升执行能力。核心是从"模仿学习驱动"向"可验证策略优化驱动"的范式转型。

## 技术架构

```mermaid
mindmap
  root((Agentic RL))
    Paradigm
      GRPO
      Self-Improving
      Credit Assignment
      Test-Time RL
    Challenge
      Sparse Reward
      Long-Horizon
      Data Efficiency
      Verifier Bias
    Application
      GUI Agent
      Web Agent
      Embodied Agent
```

## 研究路线

### 1. GRPO-based Training (主流)

**突破**: UI-R1 仅用 **136 条任务** + rule-based reward 达到 +22.1% ScreenSpot

**代表工作**:
- UI-R1: Rule-based RL 首次系统应用
- MobileRL (ADAGRPO): 80.2% AndroidWorld
- CRAFT-GUI: Curriculum + GRPO
- ClawGUI: 首个开源 RL infrastructure

**核心设计**: action type + coordinate + format 三类可验证奖励

**关联**: [[2500-UiR1EnhancingEfficient]], [[2604-ClawGUI]]

### 2. Credit Assignment (拥挤赛道)

**问题**: 稀疏终点奖励无法分配到中间步骤

**方案**:
- SOLAR-RL: First failure point detection + 三阶段 alignment
- UI-Voyager GRSD: Fork point from 成组 rollout
- ADMIRE: Adaptive milestone reward

**关键洞察**: 该方向窗口迅速关闭（5+ concurrent works 2026年初）

**关联**: [[2604-SOLAR-RL]], [[2600-UiVoyagerSelfEvolving]]

### 3. Self-Improving Agent

**核心原则**: Verifier-First — 先解决可验证性，再扩张数据

**代表工作**:
- UI-Genie: Unified reward model + self-improvement
- GenericAgent: Context density maximization + SOP evolution（100% 完成率，token 仅 15%-35%）

**风险**: Reward model 偏差可能被自增强放大

**关联**: [[2500-UiGenieSelfImproving]], [[2604-GenericAgent]]

### 4. Test-Time RL

**创新**: 推理阶段 RL 式优化，无需额外标注

**方案**:
- GUI-RCPO: Region consistency reward（1,272 无标注数据）
- PND: Contrastive decoding for grounding

**优势**: Training-free, plug-and-play

**关联**: [[2500-TestTimeReinforcementLearning]], [[2604-AdaptiveGrounding]]

## Benchmarks

| Benchmark | 平台 | SOTA |
|-----------|------|------|
| AndroidWorld | Mobile | MobileRL: 80.2% |
| ScreenSpot | Multi | UI-R1: +22.1% |
| ScreenSpot-Pro | Multi | Orcust: +23.9% |
| SOP-bench | General | GenericAgent: 100% |

## 关键洞察

### Pattern 1: 数据效率 10x+
RL 直接优化执行成功而非模仿文本，136 条 > 大规模 SFT

### Pattern 2: Credit Assignment 是核心瓶颈
长程任务稀疏奖励下步级监督不足，多方案覆盖大部分设计空间

### Pattern 3: Verifier-First 原则
先构建可靠 verifier，再扩张数据

### Pattern 4: Outcome vs Process 权衡
Outcome 保真度高但稀疏，Process 密集但易 bias

## 待解决问题

1. 长程任务 credit assignment 在高噪声场景的稳定性
2. Self-improving 系统性偏差纠错机制
3. Rule-based reward 对模糊指令的泛化
4. 真实环境评测覆盖率不足

## 下一步

| 方向 | Action |
|------|--------|
| GRPO | 研究 UI-R1 rule reward 设计 |
| Credit Assignment | 读 SOLAR-RL/ProxMO 确认差异化 |
| Self-Improving | 监控 UI-Genie/SGV 进展 |
## 近期格局变化

- **2026-08-05｜"演化步的验收 gate 是收益来源"降为条件性结论，条件是 gate 之外有没有一个冗余的部署选择器**：[[Papers/2607-HarnessBank]] 去掉 2σ 验收 gate 后 test Pass@1 ±0.0——因为 train-argmax 已经在同一训练侧数据上选中了同一个赢家，gate 的天花板贡献被完全挤到零；它真正买到的是假精英 2→0 与收敛轮数 >20→10。[[Papers/2606-SkillNb]] 同向（去 gate 只掉约 6 分 SR，而回归率 3.3%→18.6%）。对立面是 [[Papers/2605-GRASP]] 的 88.8%→63.5%，但那里闸门本身即部署决策，且该记录为 legacy（无 Evidence Ledger / verification_status），不能与两处台账齐备的自身消融等量齐观。可判别的写法因此是：**gate 扛的是地板不是天花板，除非它同时充当部署决策者**。另需分清两类证据——"无闸门循环会交付回归"成立，但依据来自跨方法对照（DGM 在 Omni-MATH 交付 −1.1%），HarnessBank 自身去 gate 后并未产生回归，只是停不下来（[[Topics/SelfEvolvingAgents-Survey]] §6.2）
- **2026-08-05｜自演化增益被首个跨方法受控析因证明不是普遍属性**：[[Papers/2608-AgentStream]] 在 5 方法 × 3 底座 × 3 种任务流的 45 个计数单元里，测到 11–17 个单元跑输不演化的同一模型；增益随底座能力非单调，最优方法不跨底座保序。问题形态由此从"某方法能涨多少"改写成"自演化的收益在什么条件下存在"。**数值不可承重**：效应量小于其自身 seed 间标准差，全文无显著性检验——可引用的是形态，不是分数（[[Topics/SelfEvolvingAgents-Survey]] §9.2/§12）
- **2026-08-05｜演化产物被测定为 model-specific correction，而非普适更优配置**：[[Papers/2607-HarnessBank]] 的 cross-model dissociation——匹配 patch +15.4、错配 +1.2、反向叠加 −15.7——把"演化产物可迁移吗"细化成"两个模型的失败模式是否同构"；[[Papers/2608-AgentStream]] 的方法排名不跨底座迁移是同一现象在方法层的投影。推论是任何 harness/skill 库的复用都应先测失败模式相似度，而不是直接套用（[[Topics/SelfEvolvingAgents-Survey]] §6.2/§9.2）
- **2026-08-05｜归因缺口新增第四种形态：组件的功劳被系统内的冗余机制吃掉**：此前三种是预算未配平（MANTA +28K token）、外部 teacher 未分离（Frontis-MA1）、组件自身未隔离（[[Papers/2608-RoMeRL]]）；HarnessBank 补上第四种——gate 的增益其实归最终选择器。补法与前三者一样便宜：固定判决规则、只换掉最终选择器再跑一遍。四种形态合起来构成一份可直接套用的自演化工作审阅清单（[[Topics/SelfEvolvingAgents-Survey]] §11）
- **2026-08-04｜"自演化组件本身"开始被要求做关掉对照，第一次做了的结果对外挂路线不利**：[[Papers/2607-SESA]] 训练时全程带技能库，评测时把库关掉跑了一遍——SESA-Off 相对 SSP 已拿到 +1.8/+2.2，重开同一最终库只再加 +0.5/+1.0，即收益主要沉淀在训练期塑造的分布里而非部署期检索；[[Papers/2608-RoMeRL]] 则是反面例子（四个记忆坐标只有一个用到学到的 Q，却没跑纯启发式臂）。与既有的预算未匹配（MANTA +28K token）、teacher 未分离（Frontis-MA1）合成同一条诊断：**报出的是联合效应，写下的是单一归因**；关库/关组件对照成本极低，缺席本身是信号（[[Topics/SelfEvolvingAgents-Survey]] §6.3/§11）
- **2026-08-04｜可验证性从任务固有属性被改述为可设计属性，但判分负担只是被转移**：[[Papers/2607-SpyRL]] 的 RLSVR 用"环境注入隐变量 → agent 在被条件化的观测上执行原任务 → 仅凭输出回答关于隐变量的问题 → 规则核对"四步给无 verifier 的域造出 ground truth，与 GRPO 正交且原则上可迁移到 GUI/agent 轨迹质量这类同样缺 verifier 的问题；但其实例中真正塑造生成质量的 reward 等于得票数、由被训练的同一模型扮演 detector 投出（论文 Algorithm 1 自标 non-verifiable），开放式生成上对 GPT-4o-RaR 整体胜率停在 48.9%/48.2%——省掉的是 verifier 成本，不是 judge 本身（[[Topics/SelfEvolvingAgents-Survey]] §3.4/§4.4）

- **2026-07-21｜环境工程被确立为与算法同级的 agentic RL 瓶颈**：三个独立团队一手证词（[[Papers/2511-DreamGym]] 4 并发上限、[[Papers/2509-AgentGymRL]] 改造清单、[[Papers/2606-OpenWebRL]] 51% 失败在环境层）；解法对偶分化为"引擎做便宜"（[[Papers/2510-WebServ]]/[[Papers/2604-Crab]]）vs"引擎做没"（DreamGym 合成经验）（[[Topics/CUA-Survey]] §4.2/§7.8）
- **2026-07-21｜树结构 rollout 收敛为新范式，有状态 fork 是双侧空白**：[[Papers/2509-TreeGRPO]] 证明 intra-tree GRPO ≡ step-DPO，与 [[Papers/2408-AgentQ]] 两代方法结构收敛——outcome reward 可免费产出步级过程信号；但树方法目前只在无状态环境成立（[[Topics/CUA-Survey]] §7.6）
- **2026-07-21｜RL 增益从默认叙事变为条件化命题**：[[Papers/2607-GRPONullWebAgent]] 受控 null（headroom 前提）+ [[Papers/2607-MAG]] 零方差 stall + [[Papers/2602-GUILibra]] partial verifiability 下 KL 必要——"先测 headroom / reward variance 再决定投 RL 还是蒸馏"应成为默认流程（[[Topics/CUA-Survey]] §7.8）
- **2026-07-21｜"监督资产是 policy 相对的"成为跨域收敛结论**：skill（[[Papers/2607-SEED]] 静态库 −7.4）、tool 边界（[[Papers/2607-SearchGenBoundary]]）、训练数据（[[Papers/2607-EvoCUA15]] Table 5）、reward 锚点（[[Papers/2602-ADMIRE]]）四个独立域同一结论——静态构建的监督资产随 policy 演化必然失效；skill 路线由此分岔为内化（SEED 蒸参数）vs 外挂（[[Papers/2607-KnowActGUIClaw]] library，跨 backbone 可迁移 +3.1pts 但跨演化阶段过期）（[[Topics/CUA-Survey]] / [[Topics/SelfEvolvingAgents-Survey]]）
- **2026-07-21｜Verifier 从被动 judge 转向主动 agent**：[[Papers/2602-VAGEN]] 交互取证 92.9% acc，第一性依据是验证不对称性（verify 83.1% vs solve 55.9%）；与 [[Papers/2510-CUARewardBench]] UPE ensemble 弃权构成 verifier 可靠性两条工程分支（[[Topics/CUA-Survey]] §8.12）
- **2026-07-21｜Self-improving 系统性偏差从假设变实证**：[[Papers/2509-Misevolution]] 四路径实测（memory reward hacking >60%、workflow ASR 54→83）——触发 agenda 中 paused 方向 Self-Improving Agent Reliability 的 resume_condition，Discussion Topic 2026-07-15 待 Supervisor 决策（[[Topics/SelfEvolvingAgents-Survey]]）
- **2026-07-24｜演化步 verifier gating 从方法空白转为实证家族，收益归因反转**：[[Papers/2605-GRASP]]（编辑级 held-out 探针+硬回归预算，消融把收益几乎全归于闸门）与 [[Papers/2606-SkillNb]]（步骤级运行时 gate，去 gate 后回归 3.3%→18.6%）两个独立数据点同指"收益在验收闸门、不在写技能"；[[Papers/2512-ASGSI]] 补第三方审计维度（无实证）；开放前沿移到 gate 自身可信性——precision 未测、replay-relative、verifier 可被攻破（[[Topics/SelfEvolvingAgents-Survey]] Takeaway 4 / Open Problem 已改写）
- **2026-07-24｜majority-voting 共识奖励的劣化获得第一方量化**：[[Papers/2606-VisPlay]] 无标注自举收益真实（3B 平均 30.61→47.27）但同批图像逐代 pseudo-label 准确率 72→61——SpatialEvo 对"共识信号继承自身误差"的批评从推测变实测，缺 deterministic verifier 的域 internal 信号"越训越脏"有了剂量数据（[[Topics/SelfEvolvingAgents-Survey]] Takeaway 2）
- **2026-07-28｜长程 agent 的 context 管理路线成型，训练非平稳性被形式化**：heuristic masking 增益为 regime 依赖（倒 U，饱和转负 [[Papers/2605-MaskingRegimeMap]]）；learned 路线两种 formulation（编辑动作 [[Papers/2510-MemAct]] / branch-return 折叠 [[Papers/2510-ContextFolding]]）以 10× 小上下文追平或超大上下文 baseline，但 [[Papers/2512-FoldAct]] 证明 summary 进入未来 observation 违反平稳观察假设→训练崩溃（step 173 实证），稳定化三手段（process reward/consistency KL/分离 credit）尚无合并对照（[[Topics/WebAgent-Survey]] §4 与 Takeaway 4）
- **2026-07-29｜RL 是否扩展能力被改写为二维条件命题**：[[Papers/2604-PassKT]] 以 Pass@(k,T) 区分采样宽度与交互深度；静态推理复现 boundary null，组合 bridge 检索中 RL 曲线在 `k≈4` 后分离，而同数据 SFT 收缩边界——task structure 与 base policy support 共同决定 RL 是否有 headroom（[[Topics/WebAgent-Survey]]）
- **2026-08-02｜Topology 演化出现 inference-time 分支，"演化信号不接触结果"首次被定量**：[[Papers/2607-MANTA]] 把通信拓扑从部署前搜索目标改成执行中可写对象（无状态 agent + append-only 存储 + 读取期解析可见性 ⇒ 突变零迁移零重算），等 token 下 74.0 vs Voting 64.7；其 Trace Auditor 明确不看答案，无 flag run 正确率 83.2% vs flagged 62.5%，但作为错误检测器 precision 仅 0.38、分域从 PlanCraft 1/90 到 BrowseComp 83/90——self-gate 的退化有"恒过"与"恒不过"两种形态，rubber-stamp 命题由此从二元判断细化为分域现象（[[Topics/SelfEvolvingAgents-Survey]] §3.4/§7.1/§10.2）
- **2026-08-02｜RSI 谱系的瓶颈坐实在"选法"，而"递归"仍无实物**：DGM 即时分数 / HGM clade 聚合（CMP 0.778 vs 0.285）/ [[Papers/2607-FrontisMA1]] 多因子固定权重效用（quality + 相对父进步 + method-family novelty）/ MANTA 纯过程 flag 四种 parent-selection 信号同时出现且从未在同一 testbed 对照；同时以 RSI 为题的工作实际做到 generation ≥2 的库内一篇也没有——Frontis-MA1 六件 artifact 全开源却只训到 generation 1，演化系统本身按其自述 largely fixed，增益又与外部 teacher（GLM-4.7）蒸馏未分离（[[Topics/SelfEvolvingAgents-Survey]] §7.2/§7.3/§7.5）
- **2026-07-29｜Relevance 从内容选择器变成 execution prior**：[[Papers/2607-RARG]] 用 document order、entry point 与 match visibility 三级 guidance 控制 corpus interaction；RARG++ 在 depth-first QA 更强、RARG+ 在 breadth-first BRIGHT 更好，表明 relevance granularity 需随任务与 budget 自适应（[[Topics/WebAgent-Survey]]）
