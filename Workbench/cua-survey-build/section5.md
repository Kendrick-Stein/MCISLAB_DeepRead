### 5.1 GUI Understanding Data

GUI understanding data 是监督颗粒度最粗的一层：它不直接监督坐标或动作，只要求模型"看懂"界面构成——元素类型、布局、功能描述、跨帧状态转移——为下游 grounding 与 trajectory 学习提供语义基座。这一层最早以图文对/VQA 形式规模化，但最新证据显示 understanding 层的高分并不自动传导为端到端能力，理解与行动之间存在明确断层。

| 数据集/模块 | 规模 | 覆盖内容 | 证据与边界 |
|:--|:--|:--|:--|
| GUICourse（GUIEnv/GUIAct/GUIChat）[[Papers/2400-GuicourseFromGeneralVision]] | 规模未在现有摘录中给出可核实数字 | 三段式课程：OCR+定位（GUIEnv）、导航指令（GUIAct）、多轮对话（GUIChat），面向把通用 VLM 升级为 GUI agent | 具体准确率数字疑似模板化生成，不采信；仅课程结构（OCR/定位→导航→对话）可信 |
| ScaleCUA-Understanding [[Papers/2509-ScaleCUA]] | 471K | 元素级外观/OCR/布局/意图标注 + 截图级 Interface Captioning + Screen Transition Captioning，跨 6 平台 | 32B 模型 MMBench-GUI L1-Hard 达 94.4，超过 GPT-4o（53.5）；但同一模型端到端 OSWorld 仅 17.7%——understanding SOTA 不等于 acting 能力 |
| GUI-World [[Papers/2400-GuiWorldVideoBenchmark]] | 精确视频/片段数未在摘录中给出 | 面向动态 GUI 视频理解：时序操作、跨窗口切换、弹窗，并基于此微调出 GUI-Vid | 作者报告 image-LLM 与 video-LLM 在动态 GUI 场景普遍表现弱，GUI-Vid 微调后有提升但仍与可靠 GUI agent 有明显差距——这是论文自己承认的负结果，而非 cherry-pick |

ScaleCUA 把三层监督（understanding/grounding/trajectory）放进同一个数据管线对比，其"understanding 分数高但 OSWorld 低"的结果本身就是一个方法论信号：静态截图理解和多步动作执行是两种不同难度的能力，不能用同一份 understanding 数据的 scale 去外推 agent 的实际可靠性。GUI-World 进一步指出理解层还有一个尚未被规模化的维度——时间/视频维度，当前数据供给几乎全部停留在单帧截图，跨帧状态跟踪缺乏对应体量的监督。

### 5.2 GUI Grounding Data

Grounding data 把"看懂"收窄为"指哪打哪"：给定 instruction 和 screenshot，输出目标元素坐标。这条数据线最早被规模化，也最先形成"数据量→性能"的清晰曲线；但近期证据表明规模不是唯一杠杆——标注密度与采集来源（自动化 pipeline vs 人工标注）同样决定上限。

| 数据集 | 规模 | 采集方式 | 证据与边界 |
|:--|:--|:--|:--|
| OS-Atlas [[Papers/2410-OSAtlas]] | 13M elements / 2.3M screenshots，跨 Win/macOS/Linux/Android/Web | Web 用 FineWeb URL 整页截图切片；desktop/mobile 用 AndroidEnv/OSWorld + A11y tree（pyatspi/pywinauto/ApplicationServices）DFS/random walk 自动遍历 | ScreenSpot 7B 平均 82.47（standard）/85.14（GPT-4o planner），显著超 SeeClick/UGround-7B；但纯 web 预训练难以 transfer 到 desktop grounding，desktop 数据有独立价值 |
| GroundCUA [[Papers/2511-GroundCUA]] | 87 apps、56K screenshots、3.56M elements，人工标注 | 真人录制 desktop 任务 → 提取 keyframe → 标注每个可见元素 bbox+文本标签+类别（50% 元素）→ MLLM 合成 Direct/Functional/Spatial 三类指令 | GroundNext-7B 在 5 个 grounding benchmark 平均 70.5（vs JEDI-7B 56.1）；700K 高质量样本击败 9M+ 自动化样本，是"数据质量>规模"针对 scale-only 路线的直接反例 |
| ScaleCUA-Grounding [[Papers/2509-ScaleCUA]] | 17.1M（point/bbox/action 三种监督格式，LLM 增广） | agent-environment 自动探索 + agent-human 混合双环 pipeline，跨 6 平台 | ScreenSpot-Pro 59.2、OSWorld-G 60.6 开源 SOTA；但同一模型端到端 OSWorld 仅 17.7% |
| AGUVIS grounding+planning 语料 [[Papers/2400-AguvisUnifiedPureVision]] | 规模数字未在现有摘录中验证 | 纯视觉多模态 grounding+推理标注，两阶段课程（先 grounding 再 planning/reasoning） | 具体准确率数字疑似模板化生成，不采信；仅两阶段课程设计（grounding 先于 reasoning）可信 |

GroundCUA 与 OS-Atlas/ScaleCUA 之间的对比构成了这一层最有信息量的张力：自动化 pipeline（A11y 遍历、agent 探索）能便宜地把元素数量堆到千万级，但平均每张截图的标注密度低；GroundCUA 用真人标注把密度做到平均每图 64 个元素（3× OS-Atlas、6× UGround），覆盖到自动化流程常漏掉的 icon/toolbar/control，最终以 13 倍小的数据量反超。这说明 desktop grounding 的真正瓶颈不是截图数量，而是密集小元素的标注覆盖，这一结论目前只在 GroundCUA 单篇工作中被验证，尚未被独立复现。

### 5.3 Atomic Action Data

Atomic action data 监督单步、至多短程的 observation→action 映射，不要求跨 app、跨 session 的状态维护。这一层最早确立的 canon 是 AITW 与 AndroidControl（现有综述已将其列为离线 step-wise 评测三件套之二），随后 AMEX 提高了单 app 内的标注密度，GUI-Odyssey 把范围从单 app 扩展到跨 app。

| 数据集 | 规模 | 层级 | 证据与边界 |
|:--|:--|:--|:--|
| AITW / AndroidControl（canon） | — | single-app 单步/短程动作 | 已确立为社区 canon 训练/评测数据，但 vault 内未见对应原始论文的独立笔记，无法核实其精确规模数字，见 gaps |
| AMEX [[Papers/2400-AmexAndroidMultiAnnotation]] | 104K+ 高分辨率截图 | 三层标注：GUI 交互元素定位 + 屏幕/元素功能描述 + 复杂指令-GUI 操作链 | 在 SPHINX agent 上验证有效；针对性解决 AITW/AndroidControl 类数据集"标注不准确、任务多样性不足"的问题 |
| GUI-Odyssey [[Papers/2400-GuiodysseyComprehensiveDatasetCross]] | 8,334 episodes、平均 15.3 步、6 设备、212 apps、1,357 种 app 组合 | cross-app 导航，每步带 semantic reasoning 标注 | 相比 AITW/AndroidControl 的 single-app 限制，首次系统覆盖跨应用上下文迁移；配套 OdysseyAgent 的 history resampler 对 in-domain 与 out-of-domain 跨 app 任务均有提升 |

AMEX 与 GUI-Odyssey 的分工体现了 atomic action 层的演化方向：前者在单 app 内把标注密度做深，后者把动作序列的边界从单 app 推到跨 app 组合，两者共同暴露的问题是——原子动作数据的"原子性"本身是相对的，跨 app 切换点才是长程任务失败最常见的断裂处，而这恰恰是本层数据历史上覆盖最弱的部分。

### 5.4 Interaction Trajectory Data

多步交互轨迹数据经历了从 human demonstration 到规模化自动生成的演化：tutorial replay 与 interaction-first exploration 最先降低采集成本；reverse task synthesis 把"先定任务再采集"反过来，从环境里 actually executable 的 transition 反推任务，从根源上避免"想象的任务在 UI 里不可达"；task/state/verifier co-generation 进一步解决可执行性问题；最新路线开始把昂贵的 state-space exploration 与廉价的 trajectory composition 分开，并依据当前 policy 动态供给任务。数据单位也随之从单条轨迹扩展为可复用的 transition graph 与 task factory：高价值训练单元至少要包含 task、initial state、observation、action、transition evidence 与 validator，缺其中任一项都很难支持 counterfactual learning、可靠 reward 或失败恢复。

| 生成层级 | 机制 | 代表工作 | 证据与边界 |
|:--|:--|:--|:--|
| Tutorial replay | 从教程或演示重放得到轨迹 | [[Papers/2412-AgentTrek]]、[[Papers/2500-TonguiInternetScaleTrajectories]] | 成本低，受教程覆盖和 replay 成功率限制 |
| Interaction-first exploration | 先探索，再 hindsight 标注任务 | [[Papers/2410-NNetNav]] | 消除不可行任务；沙盒到 live 仅 9.5% |
| Reverse task synthesis | 先乱点收集 `<s_pre, a, s_post>` transition，再反推 low/high-level 指令 | [[Papers/2412-OSGenesis]] | AndroidWorld 上 Qwen2-VL-7B 从 task-driven 9.82% 升到 17.41%，WebArena overall 从 7.05% 升到 10.79%，与 human 数据 SR retention >80%；但 exploration、reverse synthesis、执行、reward modeling 四环节均依赖 GPT-4o，开源 VLM 尚接不上这条 pipeline |
| Live task proposal | proposer–agent–judge 在真实网站采集 | [[Papers/2502-InSTA]] | 150K sites、2.2M trajectories、$521；judge 82.6%，任务偏只读 |
| Structured exploration | 网站/界面建图，从中间态采样 | [[Papers/2506-GoBrowse]] | reset 频率直接影响 coverage，环境能力进入数据质量 |
| Accessibility-driven crawling | 用 a11y 接口系统探索桌面应用，组织成层次化状态图（MacApp Tree） | [[Papers/2500-GuirillaScalableFrameworkAutomated]] | 量化了平台代表性缺口：macOS 界面在既有 grounding 语料 OS-Atlas 中仅占 0.06% 样本，在自动采集 desktop UI 整体中约占 2.45%；自身采集规模（应用数/状态数/转移数）未披露 |
| Stochastic exploration + intent-aware reasoning | 随机探索模拟试错，再任务导向补全并回顾性标注 | [[Papers/2500-GuiRewalkMassiveData]] | 作者声称提升交互流覆盖率与用户意图真实性，但论文未给出可核实的规模数字 |
| Transition-graph composition | 先构建 screen/element transition graph，再组合多 subgoal path | [[Papers/2607-SEE]] | 47K steps、平均 14.8 步；可解释并抑制 spurious cycles/redundant oscillations，但 composition 不等于真实失败/恢复 |
| Task/state/verifier co-generation | 同时生成可执行任务、状态与 validator | [[Papers/2601-EvoCUA]]、[[Papers/2603-AgentSynth]] | hard-task generation 由 11% 提到 52%；validator 质量是上限 |
| Policy-frontier task factory | 生成 executable judge，并按当前成功率动态供给任务 | [[Papers/2607-SCALECUA]] | 24K+ candidates、近 3K RL tasks；抽样审计 human-valid 仅 58.3–82.0% |
| Data-environment co-scaling | mock app、sandbox 与 real device 联合供给 | [[Papers/2607-HyMobileAgent]] | 2,000+ 实例、34,242 mock tasks；组件捆绑且真机 benchmark 私有 |
| Human demonstration infrastructure | 跨 OS 非侵入式采集工具 + 反思式 CoT 标注 | [[Papers/2508-OpenCUA]] | AgentNet 22.6K desktop trajectories；放宽"全对轨迹"要求，把标注错误留作 reflection 训练信号 |
| Simulator experience | world model/experience model 合成 transition 与 reward | [[Papers/2507-WebSynthesis]]、[[Papers/2511-DreamGym]] | 可控且便宜；fidelity、reward hacking 与 sim-to-real 需单独审计 |

[[Papers/2607-SEE]] 把 exploration 得到的 transition graph 当成可复用资产，再从图上组合长路径；Qwen3-VL-4B 在 disjoint-app SEE-Test 上的 step success 从 62.61% 提到 77.29%，说明 graph-composed supervision 能提升跨 app 的 step-level generalization，但这一结论目前只来自该工作自身的探索实验，且跨到 AndroidControl 时部分 grounding 会下降，尚不能推广为共识。更重要的是，数据质量不是静态属性，而是相对于当前 policy、environment version 与 verifier coverage 的关系；[[Papers/2607-SCALECUA]] 的 frontier sampling 与 [[Papers/2607-EvoCUA15]] 的 policy-relative data 都指向这一点——同一批轨迹对弱 policy 是有效监督，对强 policy 可能已是冗余甚至噪声。

### 5.5 Planning and Reasoning Traces

这一层监督的不是坐标或动作本身，而是动作之前的显式推理——任务分解、里程碑识别、错误反思。它比 atomic action/trajectory 数据出现得更晚，因为其前提是模型已经具备可靠的 grounding 与执行能力，推理监督才有意义；目前最完整的公开方案来自 [[Papers/2508-OpenCUA]] 的三层 CoT 体系。

OpenCUA 把推理标注分成 L1（reasoning）、L2（planning+reflection）、L3（observation）三层，并用 reflector/generator/summarizer 的合成 pipeline 生成反思式思维链。其核心发现是：仅在 state-action pair 上做 SFT 几乎不 scale（OSWorld 4.4%），但加入 reflector 合成的 reflection thought 后才解锁数据 scaling 收益（提升至 18.5%+）——这意味着错误标注不是训练噪声，只要能被识别，就能教会模型 error recovery。论文还报告 L2 优于 L1/L3，这与更早的 Aguvis 系列"L1 最优"的结论相反，作者将差异归因于自己的 L2 包含更多 planning+reflection 内容，而 L3（observation）反而引入了与任务无关的视觉干扰；这是单篇工作的反直觉发现，尚待独立复现。

vault 内另可见两个更早期、抽象层级的推理数据合成尝试：[[Papers/2501-InfiGUIAgent- A Multimodal Generalist GUI Agent with Native Reasoning and Reflection]] 采用两阶段 SFT，第一阶段做 GUI understanding/grounding，第二阶段用合成数据训练 hierarchical reasoning 与 expectation-reflection 能力；[[Papers/2500-UI-TARS- Pioneering Automated GUI Interaction with Native Agents]] 提出 System-2 Reasoning（任务分解、反思思维、里程碑识别等多种推理模式）并配合"数百台虚拟机上自动采集-过滤-反思精炼"的迭代训练。这两篇笔记目前只基于 abstract，具体标注规模、CoT 质量的量化审计均未获取，只能作为方法方向的佐证，不作为数字依据。

### 5.6 Failure and Recovery Data

失败轨迹曾被视为噪声直接丢弃，这一层数据供给的核心转变是把失败重新定位为暴露 grounding、planning、工具使用、恢复缺陷的结构化证据。目前的做法分两类：一类是把失败轨迹转成可复用的训练信号（reward 建模、SFT 数据），另一类是把失败诊断转成 inference-time 的运行时修复，不需要重新训练。

[[Papers/2606-LearningFromFailure]] 是后一类的代表：不丢弃 OSWorld 上的失败轨迹，而是让 Claude 4.5 Sonnet 作为 meta-controller 诊断失败模式，归纳出四类可执行修复策略——grounding 错误配 visual search（裁剪目标周围 400×400 patch 放大标红圈）、能力缺口配 terminal execution、知识缺陷配外部 knowledge support、重复循环配 repetition warning。基于 OpenCUA-72B，该 loop 把 OSWorld 100-step 成功率从 42.3% 提升到 48.9%，无需额外训练；作者报告超过 97% 的 LLM 生成修复建议无需人工修改即可接受，人工修改平均少于 3% 的行数——这是单篇工作的结果，且诊断质量高度依赖所用 meta-controller（论文比较了 Claude/GPT-5.2/Gemini/Qwen3-VL，认为 Claude 最稳定）。

前一类的代表是 [[Papers/2500-UiGenieSelfImproving]]：其 UI-Genie-RM-517k reward 数据集不只收集正例，还系统性构造难负例——规则验证提供初始监督、controlled trajectory corruption 人为篡改单步或多步动作制造"接近正确但实际错误"的轨迹、hard negative mining 从模型易混淆样本中挑选困难案例；配套的 UI-Genie-Agent-16k 轨迹数据则用于 agent/reward model 联合迭代自增强。同样把失败纳入训练闭环的还有 [[Papers/2508-OpenCUA]]（放宽"全对轨迹"要求，保留标注错误作 reflection 信号）以及 [[Papers/2603-CAPTCHA Solving for Native GUI Agents- Automated Reasoning-Action Data Generation and Self-Correctiv]]（用失败的 CAPTCHA 交互轨迹构造 self-correction 数据，作者报告 CAPTCHA 求解成功率从约 30% 提升到 80%，但该数字仅来自论文 abstract，全文证据未核实）。

当前 vault 内失败数据的共同特征是：每篇工作都自建了自己的失败分类体系（four failure modes / hard negative / self-correction），彼此之间没有统一的 failure taxonomy 或可复用的标注 schema，系统性、跨方法可比的失败语料仍然稀缺。

### 5.7 Preference and Safety Data

Preference data 把"哪条轨迹更好"变成可学习的相对信号，主要服务于 DPO/reward model 训练；safety-oriented preference data 则进一步把"什么该做/不该做"的人类判断固化为对齐信号。这条数据线比失败恢复数据更早成熟，因为偏好对不要求精确定位错误发生的具体步骤，只需要相对排序。

[[Papers/2408-AgentQ]] 是较早的完整闭环：用 guided MCTS 在网页上探索，同一 LLM 对候选动作做 AI 过程监督排序得到 Q 值，再用 |Q(h,a^w)−Q(h,a^l)|≥θ 的节点构造 step-level 偏好对，做 off-policy DPO。这套方法把失败轨迹也变成了监督来源（RFT 只能扔掉失败）：WebShop 上从 xLAM 零样本 28.6% 经 RFT 31.3%、outcome-only DPO 40.6% 提升到 Agent Q 50.5%（≈人类均值 50.0%）；真实网站 OpenTable 上从零样本 18.6% 一天训到 81.7%（+MCTS 达 95.4%），GPT-4o 零样本仅 62.6%。[[Papers/2500-UiGenieSelfImproving]] 的 UI-Genie-RM-517k（见 §5.6）同样属于这一层——其难负例构造方式本质是为 reward model 生产偏好对。

Safety 方向的代表是 [[Papers/2606-PrivacyAlign]]：其数据集包含 1,350 个 agentic 场景、来自 599 个独立标注者的 3,516 条详细标注，核心 insight 是 privacy violation 不只是被标注的，更是被人类判断所定义的——因此把人类标注同时用于 annotation-conditioned reward modeling/RL 训练和 annotation-conditioned LLM judge 评估，试图解决"规则匹配/敏感词过滤"这类 proxy 指标与真实人类判断脱节的问题。该笔记目前仅基于 abstract，方法细节与训练结果尚未核实。

### 5.8 Personalized User Data

个性化数据要求 agent 在带有用户历史、偏好与账户状态的环境里工作，而不是在无个人上下文的干净沙盒里执行通用任务。这条数据线目前几乎全部以评测集形式出现，专门为训练构建的大规模个性化语料仍然稀少。

| 数据集/benchmark | 规模 | 个性化维度 | 证据与边界 |
|:--|:--|:--|:--|
| PSPA-Bench [[Papers/2603-PSPA-Bench- A Personalized Benchmark for Smartphone GUI Agent]] | 12,855 条个性化指令，覆盖 10 个日常场景、22 个 mobile app | 真实用户行为衍生的个性化指令 | 作者报告 11 个 SOTA GUI agent 在个性化设置下普遍表现差；论文目前 abstract-only，聚合分数未核实 |
| PersonaVLM [[Papers/2603-PersonaVLM]] | 30k+ 交互、500 personas 合成训练集 + 2000+ case 评测集 | 长期 memory（core/semantic/episodic/procedural）+ Big Five 人格向量的 persona 建模 | Persona-MME 上比 baseline +22.4%、超 GPT-4o +5.2%（128k 设置）；是本节唯一同时发布大规模合成训练集的工作 |
| MyPCBench [[Papers/2606-MyPCBench]] | 17 个模拟 web app 的完整 Linux 桌面（预登录账号、历史数据）+ 184 个源自真实社区请求的任务 | 登录态、个人文件、跨 app 生活上下文 | 最强模型 Claude Opus 4.6 也仅 fully-solve 55.4%，失败集中在 long-horizon、multi-app 任务 |
| AgentCIBench [[Papers/2606-AgentCIBench]] | multi-app personal workspace 场景（contextual integrity 框架） | 信息流是否符合 sender/recipient/transmission principle 规范，而非"是否敏感" | 无 adversary 的正常使用中测得平均 contextual leakage 67.9%——任务完成本身就会过度披露个人状态 |
| PIRA-Bench [[Papers/2603-PIRABench]] | 100 条 mobile/desktop trajectories，平均约 32 张截图，每条搭配 3 个不同 socio-economic/preferences profile | 依赖 profile 的 proactive intent 推断 + 纯噪声负样本 | 最佳模型 final score 仅 28.05，远低于人类 90.35，主要差距来自 false positive（过度主动）而非 recall |
| AndroidInteraction [[Papers/2500-AgentInitiatedInteractionPhone]] | 规模数字未在摘录中给出 | 基于 AndroidControl 衍生，标注"何时该主动询问用户、问什么" | 论文承认标注人数、IAA、筛选阈值等实现细节"摘录未充分提供"，只能确认存在系统性标注流程 |

这六份材料共享一个结构：几乎都是评测集，PersonaVLM 是唯一明确发布大规模（30k+）可训练合成语料的工作。个性化数据与隐私数据高度纠缠——MyPCBench 需要真实登录态、AgentCIBench 直接把"过度披露"作为核心指标——这意味着构建更大规模个性化训练语料的同时，几乎必然放大隐私风险，两者目前没有被同一份数据集系统地联合处理。

### 5.9 Human, Synthetic, and Agent-Generated Data

把前几节的代表工作按数据来源重新归类，可以看到 CUA 数据供给中三种范式的分工正在从互相替代走向互补组合。人工示范提供最高保真度但成本随覆盖面线性甚至超线性增长；规则/agent 驱动的自动化探索把成本压到接近零，但受限于探索策略本身的偏差；模型驱动的 reverse synthesis 与 hybrid loop 试图在两者之间找平衡点。

| 数据来源范式 | 代表工作 | 成本/覆盖特征 | 关键发现 |
|:--|:--|:--|:--|
| 人工示范 | [[Papers/2511-GroundCUA]]、[[Papers/2508-OpenCUA]] | 标注密度最高，规模随人力线性增长 | GroundCUA 用 700K 人工标注击败 9M+ 自动化数据；OpenCUA 的 AgentNet Tool 是首个跨 OS 非侵入式自然采集工具 |
| 规则/accessibility 驱动的 agent 探索 | [[Papers/2410-OSAtlas]]、[[Papers/2500-GuirillaScalableFrameworkAutomated]]、[[Papers/2509-ScaleCUA]] | 规模可到千万级元素，但标注密度低、依赖平台 accessibility 支持质量 | ScaleCUA 发现 VLM-driven agent 探索因模型固有 bias 导致轨迹多样性不足，改用 rule-driven random-walk 后覆盖面显著更广 |
| Reverse task synthesis（模型驱动） | [[Papers/2412-OSGenesis]] | 成本低于 live 人工采集，多样性高于 task-driven 合成 | 与 human 数据 SR retention >80%，但该 gap 是否在更大 scale 依然成立未被验证；pipeline 核心引擎仍是 GPT-4o，尚不能纯开源复现 |
| 混合闭环（human + rule + model） | [[Papers/2509-ScaleCUA]]、[[Papers/2607-HyMobileAgent]] | 用人工补采 goal-directed 轨迹弥补自动化探索的目标缺失 | ScaleCUA 明确报告"完全依赖 VLM agent 探索多样性不足"是促使其转向混合方案的直接原因 |

三种范式的分工并非静态：GroundCUA 的"质量>规模"结论目前只在 desktop grounding 单一任务上成立，尚不清楚是否推广到 trajectory 层；OS-Genesis 的 synthetic-human gap 收窄证据来自 1K 量级的特定 backbone 实验。跨方法在同一 benchmark 上直接对比数据效率曲线的研究目前不存在，这是本节最大的空白（见 gaps）。

### 5.10 Data Processing and Mixture

数据处理与配比决定的是同一批语料在训练中被如何组合、稀释、去重，而不是采集了什么。这条线索在 CUA 语境下刚开始被显式讨论，此前的处理决策大多埋在训练细节里而非作为独立研究问题。

[[Papers/2509-ScaleCUA]] 报告了一个具体的配比选择：通用多模态数据在训练中的占比随模型尺寸递增（3B 25%、7B 50%、32B 75%），理由是大模型记忆容量更大，能容纳更多通用知识而不严重稀释 GUI 专有能力；这是单点工程决策，论文未给出配比消融实验。跳出 GUI 语境，通用 VLM 数据 curation 的系统性证据来自 [[Papers/2606-DataCompVLM]]：汇集 160 个公开数据集、6T token 的数据池，在 1B-8B 四档规模上系统比较 filtering 与 mixing 策略，核心结论是 mixing 而非 filtering 才是主要杠杆——产出的 DCVLM-Baseline 在 33 任务 Core 套件上达 63.6%，超 FineVision +5.4pp。这一发现并非 GUI 专用，但直接呼应 ScaleCUA 式的"通用数据比例"决策：如果 mixing 比 filtering 更重要，那么 CUA 训练中通用多模态数据与 GUI 专有数据的配比本身就应该是一个被系统消融的变量，而不是凭经验设定的固定比例。

处理流程的另一维度是迭代式在线精炼：[[Papers/2500-UI-TARS- Pioneering Automated GUI Interaction with Native Agents]] 报告其数据瓶颈应对方式是"在数百台虚拟机上自动收集、过滤、并反思性精炼新的交互轨迹"，通过迭代训练让模型持续从自己的错误里学习；这一描述目前仅来自论文 abstract，具体过滤规则和精炼算法未见展开。[[Papers/2607-SCALECUA]] 则在训练数据侧做了 exact instruction、JSON 与 near-duplicate 审计，直接把去重作为降低 benchmark contamination 风险的处理步骤（详见 §5.11）。

### 5.11 Data Quality, Privacy, and Contamination

数据质量问题在 CUA 语境下呈现三种彼此独立的形态：benchmark contamination（训练/测试环境或任务重叠导致分数虚高）、恶意数据投毒（训练语料本身被植入后门）、以及隐私标注体系的缺口（模型知道有隐私风险但无法精确定位）。三者的应对手段完全不同，不能用同一套"数据清洗"处理。

Contamination 方面，[[Papers/2606-CUAGym]] 指出一个具体风险：其 16 个 desktop apps 来自 OSWorld environment pool，并在 OSWorld-Verified 上评测，尽管任务不同，环境熟悉度仍可能贡献部分分数提升，作者认为更干净的证据来自增幅较小的 WebArena transfer。[[Papers/2607-SCALECUA]] 采取的对策是训练数据侧的 exact instruction、JSON 与 near-duplicate 审计，用以降低训练语料与评测任务直接重叠的可能性；但这类审计目前只在个别工作中出现，尚未成为行业标配，也没有面向 GUI trajectory 语料的公开污染检测工具。

数据投毒是一个更少被讨论的风险面：[[Papers/2606-IAG]] 展示了针对 VLM-based visual grounding 的 input-aware backdoor 攻击——攻击者在下游模型常见的开放平台分发的预训练权重中注入少量 poisoned 样本，用 text-conditioned U-Net 根据攻击目标描述生成动态 trigger，使模型在触发条件下无视用户 query、转而定位攻击者指定目标，同时尽量维持 clean accuracy。这一威胁模型直接指向 CUA 数据供给链的一个薄弱环节：现有 grounding 数据集（如 §5.2 列出的开源语料）本身依赖公开权重与公开数据的组合，攻击面尚未被系统评估。

隐私标注体系方面，[[Papers/2601-GUIGuardBench]] 提供了目前 vault 内最完整的标注 schema：241 条 Android/PC 真实 agent trajectories、4,080 张截图，每个 privacy element 标注 bounding box、三档风险等级、六类语义类别以及 task-necessity 标签。其核心发现——平均 binary privacy detection 在 Android/PC 达 89.0%/63.3%，但 strict full match 仅 8.8%/0.6%——说明"知道存在隐私风险"和"精确指出哪些信息不该披露"是两种不同难度的标注目标，现有数据体系在后者上几乎没有覆盖。[[Papers/2606-PrivacyAlign]]（见 §5.7）从另一个方向回应这一缺口：用人类标注本身（而非规则/关键词）作为隐私判断的 ground truth。

### 5.12 Open Problems

本章尚未解决的核心分歧是 **compositional long horizon** 与 **causal long horizon** 的区别。前者只需把可行的 transition edge 接成一条长路径（§5.4 中 transition-graph composition、policy-frontier task factory 等大多数自动化方案属于此类）；后者必须包含状态依赖、不可逆副作用、失败分支与恢复，并由独立 verifier 判断最终后果。当前没有任何一份 vault 内的数据工作声称同时满足这两个条件，多数"长程"数据集的"长"指的是步数而非因果复杂度。

未来的数据报告应当同时给出 state/transition coverage、task feasibility、validator validity、recovery coverage、benchmark overlap 与 cross-domain transfer 六个维度，而不是只报轨迹数和平均步数——这是对整章材料的横向观察：§5.4 的代表工作大多只报告其中一到两个维度（如 SEE 报 step success、EvoCUA 报 hard-task 比例），没有一份工作提供全部六项，使得跨工作的数据质量比较缺乏共同尺度。

分层级看，薄弱环节集中在三处。第一，§5.3 的 atomic action 层仍依赖 AITW/AndyroidControl 这类未被 vault 独立消化的原始论文作为 canon，规模数字只能通过二手引用推断。第二，§5.6/§5.7 的失败与偏好数据几乎每篇工作各自定义 taxonomy，缺乏可复用、跨方法可比的标注 schema，"失败恢复"作为监督信号的价值被反复验证（OpenCUA、UI-Genie、Learning from Failure 独立得出相似结论），但从未被统一到同一套语料里。第三，§5.8 的个性化数据与 §5.11 的隐私标注在结构上互相拉扯——更真实的个人上下文（登录态、历史数据）天然放大隐私风险，但目前没有工作把"个性化收益"和"隐私成本"放进同一份数据集的联合评估里。

### 调研日志

- 迁移来源：`Topics/GUIAgent-Survey.md` §4"数据、任务与经验生成"全部内容（10 行生成层级表、SEE 段落、policy-relative 共识段落、compositional/causal 长程区分段落），按 12-way TOC 重新拆分并补充新证据。
- vault 挖掘：以 grounding/trajectory synthesis/preference DPO/personalized/data mixture/contamination/synthetic data 等关键词检索 Papers/，新增 23 篇此前未被 GUIAgent-Survey 引用的笔记，覆盖 understanding（GUICourse、GUI-World）、grounding（OS-Atlas、GroundCUA、AGUVIS）、atomic action（AMEX、GUI-Odyssey）、trajectory（OS-Genesis、GUIrilla、GUI-ReWalk、OpenCUA）、reasoning traces（InfiGUIAgent、UI-TARS）、failure/recovery（Learning from Failure、UI-Genie、ReCAP/CAPTCHA）、preference/safety（AgentQ、PrivacyAlign）、personalized（PSPA-Bench、PersonaVLM、AndroidInteraction）、mixture（DataComp-VLM）、contamination/poisoning（CUAGym、IAG）。
- 质量把关：对 abstract-only 或无 Evidence Ledger 的笔记（GUICourse、AGUVIS、InfiGUIAgent、UI-TARS、PSPA-Bench、CAPTCHA/ReCAP、AndroidInteraction、PrivacyAlign）严格降级为定性表述或明确标注"未核实"，未采用其具体百分比数字（如 GUICourse/AGUVIS 中疑似模板化的 85%/92%/15% 等）。
