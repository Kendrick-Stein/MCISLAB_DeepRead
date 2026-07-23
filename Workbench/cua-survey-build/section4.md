### 4.1 Task Taxonomy

现有 GUI/CUA benchmark 各自定义任务分类，尚无共享的报告卡；但把它们放在一起看，任务复杂度沿三条基本独立的轴展开——**能力层级**（完成任务需要哪种能力）、**平台**（可利用的结构与主要难点）、**结构形状**（步数、跨应用范围、是否只读、指令是否完整）。早期 benchmark 把这三轴都锁定在最简单的一点：单页面、单步、完全指定指令；后续工作分别沿单一轴推高难度，而不是提出一个笼统的"更难"，这也是为什么跨 benchmark 的分数不能直接横向比较（另见 §6、§8）。

能力层级本身构成一条从局部到系统性的梯度：

| 层级 | 要求的能力 |
|:--|:--|
| 1. Grounding accuracy | 定位单个元素 |
| 2. Step/action correctness | 单步动作是否符合意图 |
| 3. Task outcome | 端到端功能是否达成 |
| 4. Long-horizon / cross-app completion | 多步骤、跨应用组合 |
| 5. Error awareness 与 recovery | 察觉动作未生效并纠正 |
| 6. Clarification、abstention 与 proactive restraint | 指令不完整时主动澄清或拒绝 |
| 7. Privacy、safety 与 side effect | 后果预测与不可逆操作规避 |

这一梯度在 §6.1 被用作评测报告必须绑定的强制维度；这里仅作为任务复杂度的组织坐标，不重复其评测方法论讨论。

平台是第二条轴，决定了同一算法证据强度的来源与边界：

| 平台 | 可利用的结构 | 主要难点 | 代表 setting |
|:--|:--|:--|:--|
| Web | DOM / AXTree / screenshot / network state | live drift、bot detection、transactional state、prompt injection | WebArena、VisualWebArena、Online-Mind2Web |
| Mobile | screenshot / accessibility / emulator state / real device | 小目标、系统弹窗、账号与权限状态、真机漂移 | AndroidWorld、AndroidLab、RealMobile |
| Desktop | screenshot / OS API / files / shell / app state | 跨应用、长程专业 workflow、隐私与不可逆操作 | OSWorld、WindowsWorld、SaaSBench |
| Hybrid | GUI + API / CLI / SDK | 工具路由、语义对齐、权限边界 | [[Papers/2508-ComputerRL]]、[[Papers/2606-WeaveBench]] |

第三条轴是任务的结构形状，它把"更难"拆成四对可分别度量的二元维度。**单步/长程**上，[[Papers/2604-WindowsWorld]] 在同一套系统内把 single-app 任务的 46% 压到 cross-app 任务的 14%；[[Papers/2605-SaaSBench]] 的专业跨系统工作流把最强模型压到 3.8% resolved（vs 43.9% checkpoint），说明"部分推进"与"完整闭环"之间存在巨大落差，checkpoint 式打分不能代替端到端判定。**单应用/跨应用**是这条轴在数据侧的具体化：[[Papers/2400-GuiodysseyComprehensiveDatasetCross|GUIOdyssey]] 用 8,334 个 episode、212 个 app、1,357 种 app 组合定义了 mobile 上的跨应用导航任务集合，平均 15.3 步，明确区别于单页面操作数据。**只读/事务性**上，[[Papers/2502-InSTA]] 因禁止状态修改而系统性偏向信息检索任务，学不到下单、提交表单这类 transactional 操作——这恰是最难也最有价值的部分；WorkArena 的 open << closed 对比进一步显示，同一分类内部"组合"本身就是独立的难度来源，不是长度的线性函数。**完整指令/模糊指令**是最新加入的一轴：[[Papers/2512-MobileWorld]] 把 22.4%（45/201）的任务设计成刻意省略关键信息的 Agent-User-Interaction 类型，逼迫 agent 主动澄清而非幻觉补全；同类信号也出现在 AmbiBench 的四级模糊度设计中（非交互 agent 在最模糊设置下 TSR 为 0，见 §7.3）。

| 结构维度 | 对比 | 代表数字 |
|:--|:--|:--|
| 单步 / 长程 | single-app vs cross-app | [[Papers/2604-WindowsWorld]] 46% vs 14% |
| 原子 / 组合 | atomic vs compositional | WorkArena open << closed |
| 只读 / 事务性 | informational vs transactional | [[Papers/2502-InSTA]] 系统性偏只读 |
| 完整指令 / 模糊指令 | fully-specified vs ambiguous | [[Papers/2512-MobileWorld]] Agent-User-Interaction 占 22.4%；AmbiBench 非交互 TSR 0% |

### 4.2 Web Environments

环境研究的角色经历了三步变化，这条线索贯穿 Web、Mobile、Desktop 三个平台，本节先给出统一框架，4.2–4.4 再分平台报告供给谱系。第一代环境是 benchmark container，负责初始化、执行动作与终态评分；第二代环境成为 trainer-facing infrastructure，把 reset、parallel rollout、snapshot/fork 和 programmatic reward 纳入 RL 系统；第三步开始向 agent 暴露 semantic target、action affordance、verification cue 与 provenance，形成 agent-facing runtime——这一步目前只有零星证据（见 4.4）。Trainer-facing 的并行、reset 和 deterministic judge 已相对成熟，真正早期的是 agent-facing runtime：它是否能在不泄漏 gold answer 的前提下，把软件状态变成模型可利用、可核验、可回滚的执行接口，仍缺 frozen-policy 因果实验。

GUI 环境同时追求 realism、controllability 与 scalability，但三者存在结构性冲突，现有供给形态实际上是同一三角约束下的不同取舍。Live / real-device 把 realism 推到最高，代价是难以 reset、并行、复现和安全探索，等于让渡了 controllability 与 scalability 的大部分；self-hosted real software 居中，可控且有真实功能，但站点/应用覆盖有限、维护成本高，scalability 成为它让渡的轴；functional simulator / synthetic environment 走向另一端，易 scale、易 fork，却可能丢失真实后端、异常态和视觉分布，把损失集中在 realism 一侧。三者没有绝对优劣，只是把冲突转移到不同的轴上；因此环境工作应按能力规格比较，而不是只按"真实/合成"二分。

六轴构成环境的能力规格语言：任何环境都应沿这六条轴声明自己提供什么、缺什么。训练与评测对每轴的需求并不相同——训练侧优先 rollout throughput 与稳定 reward 信号，评测侧优先可复现与防污染——同一环境因此可能胜任训练供给而不胜任评测，反之亦然。

| 轴 | 最低能力 | 训练价值 | 评测价值 | 典型失败 |
|:--|:--|:--|:--|:--|
| Init / Reset | 可编程初始状态、episode 级清理 | 课程生成、重复采样 | 可复现与难度控制 | 状态污染、手工 reset |
| Verify / Reward | 可查询的 outcome / progress / side effect | RL reward、数据过滤 | functional correctness | LLM judge 假阳性、rule 漏判 |
| Parallelism | 独立实例、资源隔离、异步调度 | 提升 rollout throughput | 多配置可比 | browser 泄漏、慢样本拖全组 |
| Fork / Rollback | checkpoint、clone、branch、replay | tree rollout、counterfactual data | 重试与失败定位 | 只能 URL 回退，后端状态丢失 |
| Task Supply | task + state + validator 同步生成 | policy-aware curriculum | 覆盖与难度审计 | 不可执行任务、只读偏置 |
| Determinism / Isolation | 固定版本、时间、网络与账号边界 | 稳定训练信号 | 可复现与防污染 | live drift、跨 episode 泄露 |

在这套框架下，Web 是供给谱系最先成熟、也最先分化的平台：

| 环境/系统 | 类型 | 关键能力 | 已知边界 |
|:--|:--|:--|:--|
| [[Papers/2307-WebArena]] | self-hosted real software | functional correctness、可复现任务 | 站点少，RL reset/并行成本高 |
| [[Papers/2412-BrowserGymAgentLab]] | unified web gym | screenshot/DOM/AXTree/SoM 与统一 action API | 统一接口不等于 agent-friendly state access |
| [[Papers/2510-WebServ]] | snapshot engine | 1.78s clone、28 MiB/instance、200+ 并发、运行中 fork | 尚无端到端 GUI RL 因果实验 |
| [[Papers/2509-AgentGymRL]] | multi-environment RL stack | full reset、并行 Chromium、horizon curriculum | 环境改造成本转移到框架维护 |
| [[Papers/2606-OpenWebRL]] | live RL stack | K8s isolation、retry、failure taxonomy、80–100 并发 | 51% 失败仍来自 bot detection/封锁/网络 |
| [[Papers/2502-InSTA]] | live task proposal | 150K sites、2.2M trajectories、$521；judge 82.6% | 任务偏只读，init/reset/事务性缺失 |
| [[Papers/2506-GoBrowse]] | structured exploration | 界面建图，reset 频率调节覆盖（1 reset/30 任务→183 URL vs 15 reset/2 任务→260 URL） | reset 依赖共享沙盒，两个 affordance 目前只在训练管线里用 |
| [[Papers/2600-WebHarbor]] | self-hosted mirror | coding agent 生成 15 个 WebVoyager 网站的 Docker 镜像，sub-second reset，模型排序与 3 个 live-web benchmark 一致 | task-driven scoping 只覆盖任务所需功能，非完整站点；验证仍偏初步 |
| [[Papers/2504-REAL]] | deterministic web replica | 112 tasks / 11 sites，localStorage state diff + rubric | 副本覆盖有限，非动态站点 |

环境供给谱系呈现出清晰的成熟度梯度。Trainer-facing 能力已相对成熟：[[Papers/2510-WebServ]] 把 fork 成本压到 1.78s clone、28 MiB/instance 并支撑 200+ 并发，reset 与并行已不再是主要瓶颈。Live 供给的主要损耗依旧发生在环境本体之外：[[Papers/2606-OpenWebRL]] 的 51% 失败仍来自 bot detection/封锁/网络，说明 realism 一侧的缺口主要是漂移与对抗，而非接口设计。[[Papers/2502-InSTA]]、[[Papers/2600-WebHarbor]]、[[Papers/2504-REAL]] 代表同一"live↔mirror"权衡的三个不同取舍点——InSTA 用真实站点换规模、放弃 init/reset/事务性；WebHarbor 与 REAL 用本地镜像换可控与可复现，代价是只覆盖任务定义所需的功能面而非完整站点。[[Papers/2506-GoBrowse]] 则把 reset 成本直接变成显式的数据质量旋钮：reset 越勤，覆盖越广，但对共享沙盒的污染风险也越高。

### 4.3 Mobile Environments

Mobile 没有 Web 式的单一 reset-cheap backend，覆盖需要同时组合 functional simulator、mock app、sandbox 与真机，这使得 mobile 供给谱系天生是混合形态而非单一路线的迭代。

| 环境/系统 | 类型 | 关键能力 | 已知边界 |
|:--|:--|:--|:--|
| [[Papers/2605-MobileGym]] | functional mobile simulator | JSON state fork、deterministic judge、95.1% sim-to-real gain retention | agent-facing 仍以 screenshot + primitive action 为主 |
| [[Papers/2607-HyMobileAgent]] | mock + sandbox + real-device mixture | 2,000+ 实例；PhoneWorld 34 apps / 34,242 tasks | AndroidWorld 82.6% 到私有真机 42.0%；高风险状态被过滤 |
| [[Papers/2512-MobileWorld]] | 开源应用替身 + agent-user interaction / MCP-augmented | 201 tasks / 20 apps，直连 PostgreSQL 后端做 deterministic 验证 | 子类样本偏薄（MCP 40、User-Interaction 45）；开源替身 UI 不等于真实商业 app 分布 |
| [[Papers/2500-A3AndroidAgentArena]] | live dynamic online app | "essential-state"程序化评估，100 tasks / 20 apps | 依赖 MLLM 作 reward model；动态在线应用维护成本高 |

[[Papers/2605-MobileGym]] 用可 fork 的 JSON state 与确定性 judge 把 mobile 环境的可复现性做到接近 web 的水平，但它面向 agent 暴露的接口仍是 screenshot + primitive action，没有把内部状态变成可核验的执行接口。[[Papers/2607-HyMobileAgent]] 是目前唯一同时覆盖 mock app、sandbox 与真机三层的供给方案，规模到 2,000+ 实例，但 AndroidWorld 82.6% 到私有真机骤降至 42.0% 说明 sim-to-real 缺口尚未被这套组合真正弥合，且高风险状态被主动过滤而非解决。[[Papers/2512-MobileWorld]] 走另一条路径：不用真实商业 app（不可控、不可复现），而是部署工业标准的开源替代品（如 Mattermost 替 Slack），换取可直连数据库的确定性验证，并首创 agent-user interaction 与 MCP-augmented 两类任务，把动作空间从纯 GUI 扩展到"发起用户交互"与"MCP 调用"。[[Papers/2500-A3AndroidAgentArena]] 则直接在真实在线 app 上运行，用"基本状态"程序化评估应对静态评估无法捕捉动态状态变化、连锁失败与替代路径的问题，但代价是评估准确性系于 MLLM reward model 本身的可靠性。

### 4.4 Desktop and OS Environments

Desktop 供给最先在大规模 VM 并行与可验证状态上成熟，随后沿跨应用组合、专业工作流、个性化上下文与更长 horizon 四个方向分化出专门挑战。

| 环境/系统 | 类型 | 关键能力 | 已知边界 |
|:--|:--|:--|:--|
| [[Papers/2508-ComputerRL]] | RL 训练基建 | 千级并行 Ubuntu VM（qemu-in-docker + gRPC）+ API-GUI 混合动作 | 环境改造针对特定 app 集合构建，跨 OS 未验证 |
| [[Papers/2607-SCALECUA]] | desktop RL/task factory | 100+ task workers、600 并发 VM、capability-frontier rollout | 50-turn cap、Ubuntu-only；抽样 task validity 仍需人工 audit |
| [[Papers/2605-OpenComputer]] | verifiable software world | app-specific 程序化 verifier，33 apps / 1,000 tasks，94.1% 人类对齐（LLM judge 仅 79.2%） | 高质量 verifier 依赖可观测内部状态 |
| [[Papers/2604-Crab]] | sandbox runtime | agent-facing rollback；步数 −29%，branch token −40–64% | 仅 shell/FS/process，不是 GUI 全栈先例 |
| [[Papers/2604-WindowsWorld]] | cross-app long-horizon | single-app 46% vs cross-app 14% | 181 tasks / 16 personas，样本偏小 |
| [[Papers/2605-SaaSBench]] | professional SaaS workflow | 23 个可本地部署开源 SaaS 系统，106 tasks | resolved 3.8% vs checkpoint 43.9%，partial 打分掩盖端到端失败 |
| [[Papers/2606-MyPCBench]] | personalized long-horizon desktop | 17 个模拟 web app + 184 个源自真实社区请求的任务，预登录账号与历史数据 | Claude Opus 4.6 fully-solved 仅 55.4%，失败集中在 long-horizon/multi-app |
| [[Papers/2606-OSWorld2]] | checkpointed long-horizon | 108 tasks / 31 sites | binary 20.6% / partial 54.8%，分差反映"过程正确但终态未达成" |

环境内部有 state、snapshot 和 verifier，不代表 agent 能利用它们。两者应明确区分：**Trainer-facing** 指 rollout scheduler、reset、parallel、ground-truth reward、hidden validator；**Agent-facing** 指 task-agnostic 的 `observe()`、`ground()`、`act()`、`feedback()`、`checkpoint()`、`rollback()` 等能力，它不能泄露 gold action 或直接给出 task success。Trainer-facing 一侧已相对成熟：[[Papers/2607-SCALECUA]] 已能调度 600 并发 VM，[[Papers/2605-OpenComputer]] 的 app-specific verifier 做到 94.1% 人类对齐。相比之下 agent-facing runtime 刚起步：[[Papers/2604-Crab]] 的 agent-facing rollback 仅覆盖 shell/FS/process。[[Papers/2607-Tactile]] 把 accessibility semantics、OCR text 与 visual fallback 编译成带 source label、geometry、affordance 和 verification cue 的 action object，使 runtime 从"鼠标驱动"变成 `observe–ground–act–verify` contract，在 macOSWorld-style tasks 上把 Codex Success@100 从 41.1% 提到 50.0%；但 AX-adapted 提升 10.04 个百分点，Limited-AX 只有 5.55 个百分点，canvas、remote desktop 与 stale metadata 仍会退回坐标歧义，说明 semantic action 的上限受环境结构质量约束，还不是 browser/mobile/desktop 全栈先例。

### 4.5 Observation Spaces

环境向 agent 暴露的 observation 有三种基本形态，对应一条清晰的发展线。最早的 web 环境依赖结构化输出——DOM / AXTree / element ID token-efficient 且便于精确操作，先解决了把自然语言目标转成可执行 navigation 的问题；但这一表示对 canvas、远程桌面和跨平台迁移脆弱，随着研究对象从 self-hosted web 扩展到 mobile 与 desktop，screenshot-only 取而代之成为通用路线：它与人类可见状态一致，跨平台性最强，代价是小目标、密集布局和动态页面使 grounding 成为显式瓶颈。工程实践因此收敛到 hybrid observation：screenshot + DOM/AXTree + bbox/SoM 兼顾语义和视觉，是工程上的主流折中。这条谱系的 pre-LLM 根基比通常认为的更早：[[Papers/0910-Sikuli]]（UIST 2009）已用 GUI 元素截图同时做检索与鼠标键盘定位，确立"看像素、按图操作、不依赖 API/坐标"路线，只是它是纯外观模板匹配、无语义泛化。[[Papers/2312-CogAgent]] 用 dual-resolution 视觉架构证明高分辨率 screenshot-only 输入可以超过 HTML-based 大模型；[[Papers/2408-OmniParser]] 代表把 detector、OCR 与 icon caption 组合成可插拔 perception layer 的路线。

hybrid observation 并非没有代价：多通道叠加暴露了新问题——若没有 provenance、freshness 与一致性检查，更多通道会把 stale structure 变成更强的错误证据。[[Papers/2607-GUIStateBelief]] 用 735 个跨 Web、Mobile、Desktop 的 paired probes 证明这一点：模型在 image-only 读取接近饱和时，仍会在冲突下跟随 stale structure，真实网页中的结构跟随率最高达 0.88；在最多六步的 MiniWoB++ click-style episodes 中，首步冲突导致 structure-following error 后，self-recovery 不超过 0.03。这一发现改变了"通道更多、因而更可靠"的默认判断——环境暴露多少种 observation 通道，不等于模型能安全地整合它们。

与视觉/结构侧的表示重构平行，web agent 有一条独立成型的 **observation reduction** 线，针对 raw DOM/HTML 常达 10k–100k token 的问题优化喂给 agent 的观察。四条路线已固化：程序化剪枝（[[Papers/2511-Prune4Web]]，候选削减 25–50×，low-level grounding 46.8→88.28）、LLM 选行检索（[[Papers/2510-FocusAgent]]，削减 >50%）、规则式结构重构（[[Papers/2605-A11yCompressor]]，OSWorld input token 压到约 22% 的同时 success +5.1pp）、与"缩短"正交的表示对齐（[[Papers/2410-AgentOccam]]）。这条线最有价值的产出是三个跨论文的校正性发现：其一，**优化 ≠ 省 token**——AgentOccam 每步观察 token 反而从 vanilla 的 2210 升到 2930，杠杆是"对齐 LLM 预训练分布 + 降噪"而非缩短长度；其二，**压缩并非普遍有益、且高度依赖底座**——[[Papers/2604-ReadMoreThinkMore]] 显示强模型（gpt-5.1、claude-sonnet-4-6）用完整 HTML 反而 +14.6~17.5pp、弱开源模型用 HTML 大幅退化（gpt-oss-20b −18.8pp）；其三，**收益随模型变强而蒸发**——Prune4Web 对 GPT-4o 零提升、FocusAgent 在 WebArena 反低于全观察（32.3 vs 36.5）。该子领域已成熟到自建廉价评测代理（[[Papers/2605-MFSCoverage]]），侧面印证方法层面接近饱和。

局部 grounding 与结构压缩之外，还有一条正交的推理期效率线——当 observation 与历史轨迹撑大 context 时如何在不掉精度下压缩存储。[[Papers/2606-StarKV]] 用 spatial mutual-information prior 替代通用 KV cache 压缩的单一 saliency 先验，在 40% 预算下与 full cache 持平；[[Papers/2601-CompressToFocus]] 把压缩折进多轮 RL，GUI-Odyssey 长程 SR +21.4pp；[[Papers/2603-STLiteKV]] 的更硬贡献是诊断——GUI 注意力在所有层都均匀高稀疏，导致分层预算先验（PyramidKV/VL-Cache）在低预算下崩溃。这条线与前述 belief-source 讨论正交：它按 attention/redundancy 启发式决定留哪些 token，而非按证据来源或新鲜度决定，裁剩的 token 不保证仍反映当前 UI state。

### 4.6 GUI Action Spaces

动作表示的发展线是从裸坐标走向携带更多语义与验证信息的动作对象：coordinate action 以平台无关、与 screenshot 对齐为起点，element-ID 与 structured GUI action 换取精确与易验证，semantic action object 进一步把 target、affordance、provenance 与 verification cue 一体化。贯穿这条线的核心分歧是平台无关性与可验证性的取舍——越依赖像素越可跨平台，越依赖结构越可核验、也越受 DOM/AXTree 可用性约束。

| 表示 | 优点 | 主要失败模式 | 代表工作 |
|:--|:--|:--|:--|
| Coordinate action | 平台无关、与 screenshot 对齐 | 分辨率变化、细小目标、坐标文本生成错位 | [[Papers/2400-SeeclickHarnessingGuiGrounding]] |
| Region / action head | 直接在 visual patch 上预测可交互区域，避免文本坐标生成 | patch 粒度限制；需要额外 head / verifier | [[Papers/2500-GuiActorCoordinateFree]] |
| Relative tool token | 离散相对移动可跨分辨率并形成 coarse-to-fine path | 多步定位增加 latency，online 长程收益未验证 | [[Papers/2602-ToolTok]] |
| Element-ID action | 精确、token-efficient、易验证 | 依赖 DOM/AXTree 与 stable ID | [[Papers/2307-WebArena]]、[[Papers/2412-BrowserGymAgentLab]] |
| Structured GUI action | click/type/scroll/drag 语义清晰 | 长尾交互 modality 覆盖不足 | [[Papers/2605-CUActSpot]] |
| Semantic action object | target、affordance、provenance、verification cue 一体化 | 依赖可用 AX/OCR；canvas 与 remote desktop 会退回视觉歧义 | [[Papers/2607-Tactile]]（详见 §4.4） |

统一 Agent 不等于统一动作 token。跨平台模型必须保留 platform convention 或显式路由，否则 mixed-SFT 会让 desktop/mobile 的交互规则相互污染；[[Papers/2607-UIMOPD]] 的 platform-conditioned distillation 就是在解决这一冲突——desktop teacher 与 mobile teacher 各自 SFT 后，再按 rollout 来自哪个平台施加对应的 on-policy 蒸馏监督，在 OSWorld / MobileWorld 上分别达 38.2% / 12.0%。长尾交互 modality 仍是这条线最薄弱的一环：[[Papers/2605-CUActSpot]] 的 206 eval + 50M synthetic 长尾 action grounding 数据上，最强的 Phi-Ground-Any-4B 也只有 44.4%；单篇工作 [[Papers/2601-SwipeGen- Bridging the Execution Gap in GUI Agents via Human-like Swipe Synthesis|SwipeGen]] 把 swipe 手势分解为多个可量化维度、自动合成 human-like swipe 数据，其 GUISwiper 达到 69.07% 的 swipe 执行准确率（较已有 VLM baseline +214%），指出当前 GUI action 覆盖的另一个缺口是执行层面的手势精细度，而非仅是定位精度。

### 4.7 CLI, Code, API, and MCP Actions

GUI 之外，computer-use agent 可用的动作通道还包括应用内建/自动构建的 API、CLI/Code 脚本以及通过 Model Context Protocol（MCP）调用的外部工具。这些通道的共同动机是绕开重复低效的界面操作，代价是工具选择、权限与副作用管理更复杂。

| 通道 | 暴露的能力 | 优点 | 已知边界 | 代表工作 |
|:--|:--|:--|:--|
| API（应用内建/自动构建） | 直接调用应用功能，跳过 UI 渲染 | 一步替代多步点击，减少 grounding 错误累积 | 需工程化构建 workflow API，覆盖仅限已建功能 | [[Papers/2508-ComputerRL]] |
| CLI / Code | 脚本化操作文件系统、配置、后台进程 | 精确、可复现、天然可验证 | 无法触达纯视觉/渲染层交互；依赖沙盒权限 | [[Papers/2606-WeaveBench]] |
| MCP（外部工具协议） | 标准化调用第三方服务/数据源 | 复用既有工具生态，无需重建 API | 返回内容体量大，易撑爆 context window | [[Papers/2512-MobileWorld]] |
| GUI（兜底通道） | 处理必须可视化交互的前端操作 | 通用、无需应用专属集成 | 慢、脆弱、误差随步数累积 | 见 §4.6 |

[[Papers/2508-ComputerRL]] 把 API 通道系统化为工程流程：为应用自动构建 workflow API（103 个 API，覆盖 Code/Chrome/LibreOffice 三件套/VLC 共 6 类应用），在 system prompt 里同时暴露 API 函数和 10 个 GUI 原语，让 agent 自行选择；GPT-4o 上的框架消融显示纯 GUI 11.2% 到 API+GUI 26.2%（+134%），Office 域从 6.2% 升到 27.9%，说明相当一部分收益来自工程化的 API 注入而非策略本身。[[Papers/2606-WeaveBench]] 则从 benchmark 侧证实了单一通道的系统性不足：114 个覆盖 8 个真实工作领域的长 horizon 任务上，GUI-only 与 CLI-only 两种单通道设置全面崩溃（GUI-only ≤1.8%，CLI-only ≤3.5%），Hybrid 达到 41.2% 的最高通过率，最佳 rollout 中位数 76 次工具调用、16 次 GUI↔CLI 通道切换；trajectory-aware judge 相比 outcome-only grading 系统性拉低 10–20 个百分点，失败分析显示 35.2% 的失败源于 reward hacking 而非能力不足。MCP 作为最新一类通道，vault 内证据仍然稀薄：[[Papers/2512-MobileWorld]] 首创的 MCP-Augmented 任务类别（40/201，19.9%）显示混合工具调用与 GUI 操作是真实 mobile 使用中被现有 benchmark 忽略的能力维度，最优框架在该类别达 51.6% SR，但最主要的失败模式是 context overflow——MCP 工具返回内容过大，直接撑爆 agent 的 context window。生产级参考架构上，[[Papers/2604-ClaudeCode]] 对 Claude Code 源码的逆向分析显示，其扩展机制按上下文代价分四层递增：Hooks（零成本）→ Skills（极低成本）→ Plugins（中等成本）→ MCP Servers（高成本，8+ 传输协议的远程工具墙），这一层级结构本身即说明 MCP 在生产系统中被当作最昂贵、需要最谨慎路由的扩展手段，而非默认通道。

### 4.8 Hybrid Action Routing

谁在每一步决定该走 GUI 还是 Code/API/MCP，是与"有没有这些通道"独立的问题。当前证据分别来自训练侧联合 policy、prompt 侧多 agent 编排与规则式静态 fallback 三种范式，尚无同 backbone、同环境下的直接因果对照。

| 路由范式 | 机制 | 代表工作 | 关键数字 |
|:--|:--|:--|:--|
| RL 训练联合 policy | 同一 policy 在 system prompt 中同时看到 API 函数与 GUI 原语，由 RL 学会选择 | [[Papers/2508-ComputerRL]] | GUI-only 11.2%→API+GUI 26.2%（+134%），Office 域 6.2%→27.9% |
| LLM 多 agent 编排 | Orchestrator 逐子任务动态派发给 Programmer（写代码）或 GUI Operator | [[Papers/2508-CoAct1]] | OSWorld 60.76% SOTA；ablation Programmer-only 35.73%（均 1.14 步）/GUI-only 50.68%（11.20 步）/Hybrid 60.76%（10.15 步） |
| 规则式静态 fallback | "能 CLI 就 CLI，否则退回 GUI"的确定性规则 | [[Papers/2604-ClawGUI]] | 定性描述，无受控 ablation |

[[Papers/2508-CoAct1]] 的 backbone ablation（Orchestrator/Programmer 用 o4-mini/o4-mini 得 43.43%，o3/o3 得 58.72%，o3/o4-mini 得 60.76%）表明路由质量的瓶颈在于负责分派的 Orchestrator 的推理能力，而非执行子任务的模块本身；同时它在 OSWorld 上把平均步数从 GTA-1 的 15.22 步降到 10.15 步，用一段脚本替换长串易错点击序列，同时提升成功率与效率。[[Papers/2606-WeaveBench]] 的 interface ablation（GUI-only ≤1.8%，CLI-only ≤3.5%，Hybrid 35.1%）是一个跨系统、跨范式的收敛证据：无论路由决策由谁做出，排除任一通道都是灾难性的，这与 CoAct-1 的模态 ablation（代码单独 35.73% / GUI 单独 50.68% / 混合 60.76%）指向同一结论——两种模态互补而非替代。

这一路由问题与 §4.5 讨论的混合观察融合问题结构对称：前者要决定该用哪个通道执行，后者要决定该信任哪个证据来源，两者都需要一个显式的仲裁策略，简单地把所有通道/证据都暴露给模型并不自动带来更好结果。[[Papers/2606-WeaveBench]] 的失败分析给出了这一对称性的反例——当模型可以自由选择通道时，35.2% 的失败属于 reward hacking（包括伪造渲染、CLI 绕过 GUI 检查等），说明自由路由有时会被模型用来选择最容易伪造证据的通道，而非功能上正确的通道；这是路由侧的失败模式，与 [[Papers/2607-GUIStateBelief]] 在观察侧发现的 stale-structure-following 是同一类"多通道仲裁缺位"问题的两个实例。

### 4.9 Open Problems

**任务分类缺乏共享 schema。** §4.1 的能力层级、平台、结构形状三条轴目前分散在不同 benchmark 的自定义标签里（informational/transactional、single/cross-app、GUI-only/Agent-User-Interaction/MCP 等），没有一张能同时标注这三条轴、供跨 benchmark 对照任务难度的报告卡。缺少这张卡，"benchmark A 比 benchmark B 更难"这类判断就无法被系统核验。

**MCP 作为 GUI/computer-use 专属动作通道的研究仍然稀薄。** vault 内除 [[Papers/2512-MobileWorld]] 的 context-overflow 观察与 [[Papers/2604-ClaudeCode]] 的生产级 harness 案例外，没有针对 GUI agent 场景下 MCP tool-selection policy、权限边界或 MCP-specific reward hacking 的受控研究；MobileWorld 的 MCP 子类样本仅 40 个任务，统计噪声较大。

**三种路由范式尚无同环境对照。** [[Papers/2508-ComputerRL]]（RL 联合 policy）、[[Papers/2508-CoAct1]]（LLM 编排）与 [[Papers/2604-ClawGUI]]（规则式 fallback）来自三个不同 backbone、三个不同 benchmark，无法判断固定 backbone 与环境下哪种路由范式更优、或路由本身贡献了多少收益（相对于单纯拥有更多通道）。

**Agent-facing runtime 仍是 desktop 局部证据，未覆盖全平台栈。** [[Papers/2604-Crab]] 的 agent-facing rollback 仅覆盖 shell/FS/process，[[Papers/2607-Tactile]] 的 semantic action object 仅验证于 desktop；browser/mobile/desktop 全栈的 `observe–ground–act–verify–checkpoint–rollback` contract 尚未在同一 frozen policy 下与 screenshot-only baseline 做因果对比。
