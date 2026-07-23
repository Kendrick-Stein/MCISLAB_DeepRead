### 2.1 Definition of Computer-Use Agents

Computer-Use Agent（CUA）指以自然语言目标为输入、以人类在 Web / Mobile / Desktop 上实际使用的 GUI（screenshot、DOM/AXTree）为主要观察与操作通道、通过点击/输入/滑动等低级动作序列完成任务的智能体，必要时可辅以 API/CLI 调用，但 GUI 仍是其定义性的交互通道——这一点把 CUA 与"纯文本/纯代码工具调用 agent"区分开（见 §2.3）。

这一定义可用 POMDP 形式统一表达：给定 instruction $i$，agent 每步依据 observation $o_t$ 采样动作 $a_t\sim\pi(\cdot\mid o_t,i)$，并引入两个工程化算子——observation simplification（$o_t\to o_t^*$，如降采样/结构化 screenshot）与 action grounding（$a_t^*\to a_t$，把"点击提交按钮"这类语义动作解析为 `click(x,y)`）[[Papers/2501-ACUSurvey]]。这套形式化把 GUI Agent、Web Agent、Mobile Agent 与 Desktop/OS Agent 统一到同一个 loop 里，彼此的差异只在于 domain（Web/Android/PC）决定的 observation 与 action 具体实现，而非机制分歧（详见 §2.2）。

screenshot-native grounding 常被视为 LLM 时代的产物，但这一范式的起点早于 LLM：[[Papers/0910-Sikuli]]（UIST 2009）已经用 GUI 元素截图同时做检索与鼠标键盘定位，确立了"看像素、按图操作、不依赖 API/坐标"的路线——这正是当前 CUA 的核心交互范式。但 Sikuli 本质是纯外观模板匹配（MSER+SIFT），无语义泛化：它只能匹配确切的截图、无法解析"点击提交按钮"这类语义指令，因而是 visual macro 而非 agent。RPA 与 programming-by-demonstration 是同一时期的另一条工业界路线——录制固定操作序列、按规则重放，同样不具备语义泛化，是 LLM-based agent 目前在产业界正逐步取代的对象（见 §2.3）。LLM/VLM 补上的正是语义理解与 planning 能力，而 pixels-in / keyboard-mouse-out 的底层交互范式自 Sikuli 起未变。把这条 pre-LLM 谱系纳入定义，是为了纠正"视觉操作 GUI 是 LLM 发明"的时序错觉：LLM 改变的是 agent 能否理解与规划，而不是交互通道本身。

### 2.2 CUA vs GUI Agent / Web Agent / Mobile Agent / OS Agent

CUA、GUI Agent、Web Agent、Mobile Agent 与 OS Agent 在文献中并非互斥范畴，而是同一交互范式在不同 platform 边界上的命名分歧——差异主要来自研究社区的历史起点（web navigation/HCI vs. mobile accessibility service vs. desktop OS 自动化）与目标平台的观察-动作原语，而非机制本身的分歧。下表按术语的典型平台范围、历史起点与代表 survey/benchmark 做横向定位：

| 术语 | 典型平台范围 | 历史起点/社区 | 观察-动作原语 | 代表 survey / benchmark |
|:--|:--|:--|:--|:--|
| GUI Agent | Platform-agnostic，强调"看 GUI、做操作"这一范式本身 | LLM agent 社区，随 VLM 兴起（2023 起） | screenshot / DOM+AXTree 皆可，不预设平台 | [[Papers/2400-LargeLanguageModelBrained]] |
| Web Agent | 限定浏览器内 DOM/网页 | Web navigation / IR 社区，早于 LLM 时代已有结构化导航研究 | DOM/AXTree/element-ID 为主，screenshot 为辅 | [[Papers/2307-WebArena]]、[[Papers/2412-BrowserGymAgentLab]] |
| Mobile Agent | Android/iOS | 移动 HCI + accessibility service 社区 | screenshot + accessibility tree + touch/gesture | [[Papers/2605-MobileGym]]、[[Papers/2512-MobileWorld]] |
| Desktop / OS Agent | 完整操作系统（跨应用、文件系统、shell） | 桌面自动化 + OS 研究社区 | screenshot + OS API + files/shell | [[Papers/2409-WindowsAgentArena]]、[[Papers/2508-OSAgentsSurvey]] |
| CUA | Web/Mobile/Desktop 的跨平台统称 | Anthropic 等厂商的产品命名 + ACU 学术综述 | 上述三类原语的并集，platform 由具体系统决定 | [[Papers/2501-ACUSurvey]] |

三篇独立撰写的已发表 survey——[[Papers/2400-LargeLanguageModelBrained|LLM-Brained]]（环境-推理-执行-反馈闭环）、[[Papers/2508-OSAgentsSurvey|OS Agents]]（environment/observation space/action space 三组件 + understanding/planning/grounding 三能力）与 [[Papers/2501-ACUSurvey|ACU]]（domain × observation/action 的 POMDP taxonomy）——各自独立收敛到"平台 × 观察/动作原语"这同一组织坐标，这是跨作者、跨机构的共识性证据，而非单篇 survey 的一家之言，本综述沿用这一坐标作为 §4-§9 的底层分类依据。但三者在"是否把 CLI/API 调用也算进 action space"上并不统一：OS Agents 的 extended operations 与 ACU 的 code action 都承认这类动作存在，却未把它当作与 GUI action 平级的一等公民——这正是 §2.3 要单独厘清的边界。

### 2.3 Relationship with Tool Agents, CLI Agents, and RPA

Tool-use agent（泛指任意 function-calling/API 调用的 LLM agent）、CLI/terminal/coding agent 与 RPA 三者与 CUA 共享"自主执行多步动作完成任务"这一底层定义，但在**交互通道是否为人类可见的 GUI** 这一维度上与 CUA 分道——这也是本综述划定核心研究对象与邻接证据的关键轴（表见下）：

| 类别 | 交互通道 | 与 CUA 的关系 | 代表工作 |
|:--|:--|:--|:--|
| Tool-use / function-calling agent | 结构化 API schema，无 GUI | 更广泛的父类；CUA 可视为"工具即操作系统本身"的特例 | — |
| CLI / terminal / coding agent | Shell 命令、文件系统、代码执行，无视觉输入 | 与 CUA 平行发展的姊妹范式，动作粒度更粗、无 grounding 问题 | [[Papers/2604-ClaudeCode]]、[[Papers/2607-LongHorizonTerminalBench]] |
| GUI + API/CLI hybrid | 以 GUI 为默认通道，按需路由到 API/CLI | 属于 CUA 内部的一种 action space 设计，非独立范畴 | [[Papers/2508-ComputerRL]]、[[Papers/2606-WeaveBench]] |
| RPA / programming-by-demonstration | 录制的固定 GUI 操作序列，规则重放 | CUA 的历史前身与产业界替代对象，非语义泛化系统 | [[Papers/0910-Sikuli]] |

GUI 与 CLI 并非互斥而是可比较、可路由的两条通道，二者的取舍在同一系统内已有直接实验证据：[[Papers/2508-ComputerRL]] 在 GPT-4o 上做框架消融，纯 GUI 通道 OSWorld 11.2% 提升到 GUI+API 混合通道 26.2%（+134%，Office 域从 6.2%→27.9%），说明相当一部分 desktop 任务的上限来自可用的 API 注入而非算法本身；[[Papers/2605-OpenComputer]] 则在同一 14 应用、343 个 CLI 兼容任务上直接对比两条纯通道——GUI agent 通过率更高（75.2% vs. CLI 67.2%），但 CLI agent 显著更快（141s vs. GUI 的 288–622s），因为绕开了 screenshot-action 循环。这组对照支撑一个具体判断：**GUI 与 CLI 不是竞争关系而是互补的动作通道**，谁更优取决于任务是否需要视觉反馈校验——这正是 [[Papers/2607-Tactile]] 等 semantic action runtime 试图显式建模的路由问题（见 §2 已迁移内容 / 主报告 §2.2）。

CLI/coding agent 领域也存在与 CUA 不直接重叠、只作邻接证据的部分：[[Papers/2605-EnvTrustBench]] 把"agent 把观察到的一条 claim 当成证据却不核对当前环境真实状态"的失败模式（evidence-grounding defect）形式化，在 6 个 LLM backbone × 5 个 coding/CLI scaffold 共 14 个 stack、3,850 次受控 run 上测得 83.3% 的聚合 Environmental Misgrounding Rate；但该工作明确将 scope 限定为通用软件/CLI agent（阅读文件、查 API、跑脚本），**非 GUI-specific**，因此本综述只将其作为"belief provenance 缺失是通用 agent 问题而非 GUI 独有"的邻接证据，不纳入核心对象。

### 2.4 Inclusion and Exclusion Criteria

纳入判据是"是否直接研究 UI observation、GUI action、computer-use environment、GUI verifier，或部署期 safety/HCI"；不满足者即便共享模型 backbone 或算法术语也不纳入，只作邻接证据引用。下表把这条边界具体化为可操作的类别判定：

| 判定 | 类别 | 说明 | 边界案例 |
|:--|:--|:--|:--|
| 纳入 | 核心 CUA 研究 | 直接产出 GUI observation/action/environment/verifier 或部署 safety/HCI 证据 | [[Papers/2307-WebArena]] |
| 邻接（不纳入） | 纯 Deep Research / 通用 Agentic RL / 通用 VLM-World Model / Embodied Agent | 不因共享 backbone、RL 算法或"agent"术语纳入 | — |
| 条件纳入 | 通用 LLM/CLI/coding agent | 仅当显式对比 GUI vs. CLI 或构造 GUI+CLI 混合动作空间时纳入 | [[Papers/2605-OpenComputer]] 纳入；[[Papers/2605-EnvTrustBench]]（纯 CLI，无 GUI 交互证据）仅邻接 |
| 硬排除 | 命中 `hard_exclude_keywords`（如 browsecomp） | 无条件排除，不受论文自身 tag 覆盖 | — |

实现上采用"关键词打分 + 硬性覆盖"两层机制：`keywords`（gui-agent / gui grounding / computer-use / computer use agent / cua / web agent / browser agent / mobile agent / desktop agent / os agent）命中加分优先纳入；`exclude_keywords`（deep research / information seeking / browsecomp / research agent / search agent）命中降权；`exclude_tags: [deep-research]` 对打了该 tag 的论文直接降权；但若论文自身带 `exclude_override_tags`（gui-agent / computer-use），即便命中普通 exclude_keyword 也不硬排除——这一层是为了防止"GUI agent 论文里提到一句 information seeking"被误杀；只有 `hard_exclude_keywords`（browsecomp）命中时才无条件排除，不受 override 挽回。

已发表的 [[Papers/2501-ACUSurvey|ACU survey]] 采用了相近但独立制定的边界——明确排除 game-playing、coding agent、software testing 与纯 RPA。这与本综述的边界高度重合，可作外部校准证据，但这是该单篇 survey 自身的选择，不构成跨综述共识。

### 2.5 Literature Search and Selection

检索遵循 vault-first 原则：先审计已有论文清单与既有 survey 覆盖度、定位结构性缺口，再针对缺口做定向外部检索，而非对相似主题重复召回。检索沿两条互补通道执行——OpenAlex 主题检索（覆盖期刊/顶会，零 token 成本）与 WebSearch（覆盖 arXiv 新预印本），并按九类 query 角度分工：核心主题、主流技术路线、既有 survey、benchmark/数据集、应用场景五类"覆盖角度"，加上矛盾检索、负结果检索、邻域检索、术语漂移检索四类"证据完整性角度"；后者即使返回"未发现反例"也要记录，因为"缺矛盾"本身是覆盖信号。

本综述的前身 [[Topics/GUIAgent-Survey]] 经过多轮检索迭代：2026-07-21 一轮围绕模型/状态、RL、数据、环境/runtime、评测、Safety/HCI 六个主题执行 4 组 arXiv API、5 组 OpenAlex 与 4 组 WebSearch 查询，纳入 10 篇新论文；2026-07-22 一轮针对性检索 11 篇已发表 GUI/CUA survey 做 taste 校准，同时核对 SOTA/baseline canon 与社区 reviewer 关注点；随后的覆盖度审计确认盲点不在 frontier（已饱和）而在结构性根基——pre-LLM 自动化谱系（RPA/PbD/Sikuli）零覆盖、HCI oversight 仅由 GUI 论文自身支撑、accountable-state 论断主要靠单一时间窗口的 preprint 支撑——据此触发术语漂移（Sikuli/RPA/PbD）、邻域（Horvitz mixed-initiative、Parasuraman automation bias）、矛盾/负结果三类 gap-driven 检索并补入相应论文。截至本文构建时，可解析且去重的 `Papers/` wikilink 为 111 篇，覆盖年份范围 1997–2026（起点由 pre-LLM 谱系论文决定）。

所有候选论文经 paper-digest 生成 Evidence Ledger 后进入 verification gate：会进入 Overview、benchmark 横向比较、Key Takeaways 或 Open Problems 的高影响 claim，由不同于抽取者的独立 verifier 核对，统一标注为 `source-verified / unsupported / contradicted / not-checkable / abstract-only` 五态之一，只有 `source-verified` 的 claim 可无保留进入关键结论；跨论文横向比较还需核对 environment、verifier、step budget、backbone 与数据集 split 是否可比，不可比时禁止写成横向胜负。

### 2.6 Paper Coding Scheme

每篇纳入综述的论文按两组正交字段编码：一组是内容分类字段，决定它落在新 12 节结构的哪个位置；一组是证据质量字段，决定它能支撑多强的结论。内容分类字段如下：

| 字段 | 允许取值 | 用途 |
|:--|:--|:--|
| `platform` | web / mobile / desktop / cross-platform / hybrid GUI+API/CLI | 对应 §2.2 的平台坐标 |
| `task_level` | grounding / step / app workflow / cross-app long-horizon / interactive-proactive | 能力层级（见主报告能力阶梯） |
| `primary_section` | model-architecture / training-RL / data-task / environment-runtime / evaluation-verifier / reliability-safety-HCI | 论文的唯一主归属章节 |
| `environment_setting` | offline / self-hosted / live / real-device | 决定其 claim 的可迁移性边界 |
| `verifier_type` | programmatic / interactive agent / visual-rubric judge / human / none | 决定其成功率数字的可信度基线 |
| `evidence_strength` | direct end-to-end / component-only / adjacent transferable evidence | 决定它能否支撑核心结论还是仅作旁证 |

每篇论文只允许一个 `primary_section`，最多再向 1–2 个其他章节 cross-link，避免同一证据在多处被重复计为独立支持；与本综述主题明显无关的候选论文（keyword 打分误报）直接跳过，不勉强归入任何字段。证据质量字段则复用 paper-digest 的既有产出：`rating`（1–5，按内容质量与相关性打分）与 Evidence Ledger 的 `verification_status`（`source-checked` / `partial` / `unverified` / `abstract-only`）；后者决定该笔记的数字能否被写入 survey 正文——`abstract-only` 或缺 Evidence Ledger 的 legacy 笔记只能作为论文存在性与主题归类证据，不得凭它新增关键数字、共识判断或 Key Takeaway。

`primary_section` 当前取值沿用 [[Topics/GUIAgent-Survey]] 的六层结构（该结构是本综述 §4–§9 的直接前身）；本次重排为 12 节结构后，需要把六层字段值 remap 到新的章节编号，remap 规则尚未形式化，见 gaps。

## 调研日志

- **迁移来源**：[[Topics/GUIAgent-Survey]] §1 Overview 的 scope 边界段（Deep Research/通用 Agentic RL/通用 VLM/Embodied 排除）与 §2.1 首段 pre-LLM 谱系（Sikuli/RPA/PbD），以及"调研日志"中 2026-07-21/07-22/07-23 三轮检索方法记录；`Topics/CUA-Survey.md` frontmatter 的 keywords/exclude_keywords/exclude_tags/hard_exclude_keywords/exclude_override_tags 字段；`skills/1-literature/survey-refresh/SKILL.md` Step 3 的六字段编码表与 verification_status 定义。
- **vault 新挖**：`Papers/2501-ACUSurvey`（提供 POMDP 形式化与独立制定的 exclusion 边界，对本 section 价值最高）、`Papers/2400-LargeLanguageModelBrained`（补第三篇独立 survey 佐证坐标共识）、`Papers/2605-OpenComputer` 的 GUI vs CLI 直接对照数字（75.2% vs 67.2%，141s vs 288–622s）、`Papers/2508-ComputerRL` 的 GUI vs GUI+API 消融（11.2%→26.2%）、`Papers/2605-EnvTrustBench`（非 GUI-specific 的边界反例）、`Papers/2607-LongHorizonTerminalBench`、`Papers/2604-ClaudeCode`（CLI/coding agent 代表作）、`Papers/2409-WindowsAgentArena`（Desktop/OS Agent 代表 benchmark）。
- **未解决**：programming-by-demonstration 作为独立技术路线（区别于 RPA 规则脚本）在当前 vault 中没有专门 digest 的代表论文，2.1/2.3 中的 PbD 表述仍只依赖 [[Topics/GUIAgent-Survey]] 既有转述，未溯源到 PbD 原始文献；见 gaps。

## Key Evidence Matrix（本 section 新增行）

| Claim | State | Locator | 边界 |
|:--|:--|:--|:--|
| Sikuli 为纯模板匹配、无语义泛化，是 visual macro 而非 agent | source-verified | [[Papers/0910-Sikuli]] | 单一历史工作，非当代基准比较 |
| GPT-4o 框架消融：纯 GUI 11.2% → GUI+API 26.2%（OSWorld，Office 域 6.2%→27.9%） | source-verified | [[Papers/2508-ComputerRL]] §Key Results | 单一 backbone（GPT-4o）+ 单一系统内消融，非跨系统通用结论 |
| 14 应用/343 任务上 GUI 75.2% vs CLI 67.2%，CLI 更快（141s vs 288–622s） | source-verified | [[Papers/2605-OpenComputer]] Ablation: GUI vs. CLI Agents | 单一 benchmark 内对照，未跨其他平台复现 |
| EnvTrustBench 83.3% 聚合 Environmental Misgrounding Rate，跨 14 个 model-scaffold stack | source-verified | [[Papers/2605-EnvTrustBench]] | scope 为通用 CLI/coding agent，非 GUI-specific，仅作邻接证据 |
| LLM-Brained / OS Agents / ACU 三篇独立 survey 收敛于"平台 × 观察-动作原语"坐标 | 跨来源收敛（3 篇独立 survey），非单篇共识声明 | [[Papers/2400-LargeLanguageModelBrained]]、[[Papers/2508-OSAgentsSurvey]]、[[Papers/2501-ACUSurvey]] | 三者对"CLI/API action 是否算一等公民"未统一，见 §2.3 |
