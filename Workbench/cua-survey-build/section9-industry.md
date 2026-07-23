# §9 Industry Landscape — staged drafts (from Claude web-research fleet, 2026-07-23)

<!-- ===== group: 9.3-9.5 ===== -->

### 9.3 Enterprise Automation and RPA

传统 RPA 厂商在 2024–2025 集体从"确定性脚本自动化"转向"agentic automation"：把 LLM/CUA 作为**推理层**接入，让 RPA bot 退居为受治理的**确定性执行层**，并新增编排控制平面协调 agent、bot 与人。这一路线的共识是——**RPA 提供可审计、可回滚、合规的动作执行，LLM agent 负责意图理解与非确定性决策**；同时 vision-based computer use 正逐步替代脆弱的 selector-based 脚本。四家主流厂商（UiPath、Automation Anywhere、Microsoft、SS&C Blue Prism）均被列为 2025 Gartner RPA Magic Quadrant Leader（报告于 2025-06-23 发布，评估 13 家厂商，2024 年市场规模 $3.8B、同比 +18%）（as of 2026-07，来源：UiPath/Automation Anywhere newsroom、Gartner MQ 2025）。

| 厂商 | 传统 RPA 资产 | Agentic / CUA 能力 | 编排控制平面 | 模型策略 |
|:--|:--|:--|:--|:--|
| **UiPath** | Studio / Robots / Orchestrator | Autopilot（自然语言构建/执行）、IXP agentic document processing（Extraction/Validation Agent）、Healing Agent（UI 测试自愈） | **Maestro**（2025 推出，编排 agent+robot+人的端到端流程控制面） | BYOLLM；Autopilot 可选 Gemini 2.5 Flash/Pro、实验性 GPT-5 系列；Test Cloud 支持自带 LLM 订阅（2025-12） |
| **Automation Anywhere** | Automation 360 / bots | Agentic Process Automation（APA）、**Process Reasoning Engine (PRE)** 理解企业上下文并 goal-driven 编排、AI Agent Studio（low-code 建 agent） | **Mozart Orchestrator**（多 agent 协调、异常处理） | 不自托管模型；AI Agent Studio 连接 Amazon Bedrock、Google Vertex AI、Azure OpenAI、OpenAI |
| **Microsoft** | Power Automate（desktop/cloud flows） | **Computer use in Copilot Studio**：vision+reasoning 直接操作 Web/桌面应用（点击/选单/输入），无 API 也能自动化，可自适应 UI 变化 | Copilot Studio agent flows；Windows 365 托管浏览器免配置执行 | 多模型：Anthropic Claude Sonnet 4.5、OpenAI Computer-Using Agent，preview 增 Mistral Medium 3.5 |
| **SS&C Blue Prism** | Blue Prism RPA | RPA→agentic 平台（RPA 作可靠执行层 + 内嵌 AI 处理判断型工作）、vertical/domain-specific agents（如金融犯罪合规） | 内置 governance/orchestration | 支持接入 gen AI / RAG / agentic 扩展工作流 |

**融合路线的技术共性。** 各家均把"agent 自生成工具"视为 PoC 级做法，生产环境坚持**预定义、确定性、合规的 tool/micro-automation**（UiPath 明确"永不把密码交给 LLM"）；编排层（Maestro、Mozart、Copilot Studio flows）成为新的竞争焦点，承担 agent–bot–人之间的决策、依赖与异常管理。Microsoft 的 computer use 代表最"纯 CUA"的一端：用视觉+推理导航 live UI，直接瞄准 vendor portal、内部 Web app、遗留 line-of-business 系统这类**既无 API 又难以用 selector 脚本稳定自动化的长尾流程**（客户案例：Graebel 的 Global Connect 系统由 agent 直接操作 UI 完成录入与交易；厂商自述）。

**成熟度与部署节奏。** Microsoft computer use 走过 2025-04 首发预告 → 2025-09 US 环境 public preview → 2026 GA 并扩展至全部商用地区的节奏（as of 2026-07，来源：Microsoft Copilot blog / techcommunity）。整体来看，RPA 厂商的 agentic 转型仍强调**人在环、rightsizing、可度量结果**（SS&C Blue Prism 2025 AI Agent Trends Report 观察到企业正从"实验"转向"验证"），而非全自治——这与消费级 CUA 产品（§9.2）追求端到端自动化的取向形成对照。

### 9.5 Vertical and Professional Agents

垂直/专业 agent 是 CUA 商业化最快的一端：它们把通用 computer-use 能力收敛到单一领域的软件栈与 SOP 上，用领域数据、outcome-based 定价和企业级 governance 换取可靠性。成熟度呈明显梯度——**编码与客服**已进入规模化生产并产生可观营收，**QA/测试**正从脚本自动化转向 agentic，**金融后台与医疗**受合规约束仍以 human-in-the-loop、点解决方案为主。

| 垂直领域 | 代表产品 / 公司 | 交互形态 | 成熟度（as of 2026-07） |
|:--|:--|:--|:--|
| **编码 / SWE** | Cognition **Devin**、GitHub **Copilot coding agent**、OpenAI **Codex**、Anthropic **Claude Code**（架构见 [[Papers/2604-ClaudeCode]]） | shell + editor + browser 的沙盒工作区；异步交付 PR | 高：多家已 GA / 规模化，进入受监管企业 |
| **客服 / CX** | **Sierra**、**Decagon**、Salesforce **Agentforce 360** | 对接 CRM/工单/知识库，可执行系统内动作（非纯问答）；文本+语音 | 高：营收/客户规模化，outcome-based 计费 |
| **QA / 软件测试** | Tricentis **Tosca**（Agentic Test Automation + Vision AI）、Applitools、mabl、ContextQA | 自然语言生成用例；Vision AI 像素级操作 SAP GUI/Citrix/遗留桌面 | 中：从脚本自动化转向 agentic，头部厂商已产品化 |
| **金融后台 / 会计** | **Pilot**（"AI Accountant"）、**Coasty**、Akira AI、Vic.ai、Docyt | computer-use agent 直接操作会计/ERP UI 做发票录入、对账、PO 匹配 | 新兴：多为 vendor 早期方案，重人工复核 |
| **医疗行政** | prior-authorization agents：Latent Health、Tandem、Innovaccer **Flow**、Cohere Health | 从 EHR 抽数、填 payer 表单/提交；voice agent 导航 payer IVR 电话系统 | 新兴：受监管，AI 不得单独作医疗必要性拒付 |

**编码 agent——最成熟的专业垂直。** Cognition Devin 是自主 SWE 代表：在 Dev Box（Linux shell + 编辑器 + 浏览器 + agent）内规划/写/测/调/部署代码，数据可全程留在客户 VPC；Devin 2.0（2025-04）把入门价从 $500/月降到 $20/月，并称 per-ACU 完成的初级任务量较 1.x 提升 83%（厂商自述）。企业侧的标志性验证是 Goldman Sachs 于 2025-07 试点，与 12,000 名工程师组成"hybrid workforce"、宣称 ~20% 效率提升（Goldman/Cognition 自述，未独立验证，且需数周知识库配置与专人管理）；Cognition 2025-07 收购 AI-native IDE Windsurf，估值从 2025-03 的 $4B 升至约 $10.2B，并于 2026-05 前后洽谈以 $25B pre-money 融资（as of 2026-07，来源：Contrary Research、SiliconANGLE）。平台侧，GitHub Copilot coding agent 于 2025-09 GA（接 issue → 自主开 draft PR，需人工 review 才触发 CI/CD），并通过 Agent HQ 把 Anthropic Claude、OpenAI Codex 作为可选 agent 纳入同一平台（2026-02 起对 Business/Pro 开放）；OpenAI 称 Codex 周活超 500 万（来源：分析媒体，非官方一手，待核）。架构层面的一个 grounding：逆向 Claude Code 源码显示仅约 1.6% 是 AI 决策逻辑、其余 98.4% 是确定性基础设施（权限门控、上下文管理、恢复机制），印证"生产级 agent 竞争壁垒已从模型转向 harness"（见 [[Papers/2604-ClaudeCode]]）。

**客服 agent——营收与规模化最快。** Sierra（Bret Taylor 与 Clay Bavor 联创）以 Agent OS + 语音 agent 驱动增长，2025-11 越过 $100M ARR、进入第三年时 ARR >$150M、服务超 40% 的 Fortune 50；融资从 2024 年 $4.5B 估值一路到 2025-09 的 $10B（$350M 轮）与 2026-05 的 $15.8B（$950M E 轮）（as of 2026-07，来源：Sacra、CMSWire、Axios）。Decagon 用第三方（OpenAI/Anthropic/Cohere）+ 自研微调模型做文本与语音客服，2025-06 完成 $131M C 轮、估值 $1.5B，客户含 Hertz、Duolingo、Chime（Chime 报告联络中心成本降 60%，客户自述）。Salesforce Agentforce 360 于 2025-10-13 GA，基于超 12,000 次 Agentforce 实施；客户 Reddit 报告 46% 案件 deflection、解决时间降 84%（厂商/客户自述）。值得注意的反直觉信号：Salesforce Agentic Enterprise Index 显示 2025 上半年 agent 主导对话量增 22×，但**升级到人工的比例从 Q1 的 22% 升到 Q2 的 32%**——规模化伴随更多而非更少的 human handoff。三家共性是 outcome-based 定价（按 conversation/resolution 计费），把商业模式与 agent 实际成效绑定。

**QA/测试、金融、医疗——差异化的成熟度。** 测试领域，Tricentis 把 Agentic Test Automation 嵌入 Tosca（自然语言自动生成用例），其 Vision AI 以像素级图像识别操作 SAP GUI、Citrix 虚拟桌面与遗留企业应用——这是传统 Web 自动化框架够不到的场景（Tricentis 获 2025 Gartner AI-Augmented Software Testing MQ Leader，来源：Tricentis blog / 分析媒体）。金融后台与会计出现明确的 computer-use 叙事：agent 像人一样"看屏幕、动鼠标键盘"直接操作会计软件做发票录入/PO 匹配/对账，规避 API 集成与 selector 脚本脆弱性（Pilot 于 2026-02 宣称推出首个 SMB"全自主 AI Accountant"；Coasty 提供操作真实桌面/浏览器的 computer-use agent）——但此处证据多来自 vendor blog，成本/效率数字（如手工发票 $18–$40/张、Gartner 预测 2027 年底 40%+ agentic 项目被取消）应视为方向性而非独立核实。医疗行政以 prior authorization 为主战场（Menlo Ventures 估该类工具支出从 2024 的 $10M 十倍增至 2025 的 $100M）：agent 从 EHR 抽取临床文档、填 payer 表单并提交，voice agent 自主导航 payer IVR 电话；但监管是硬约束——Texas（2025）、Arizona、Maryland 立法禁止仅凭自动化系统作出医疗必要性拒付，CMS-0057-F 自 2026-01-01 起生效，使该垂直**结构性地保留 human-in-the-loop**（来源：Innovaccer、Forbes Councils、Healthcare Huddle）。

**横向判断。** 垂直 agent 的落地深度与两个变量强相关：(1) 任务是否有可验证的成功信号（编码有测试/CI、客服有 resolution，故最快成熟）；(2) 领域是否受合规约束（医疗、金融判断型任务被立法钉在 human oversight）。这解释了为何 2026-07 时点上编码与客服已产生规模化营收与受监管企业部署，而金融后台与医疗仍停留在点解决方案 + 重人工复核阶段。

<!-- ===== group: 9.4 ===== -->

### 9.4 Open-Source and On-Device Agents

与 §9.1–9.3 的闭源 Operator / Claude Computer Use 平行，开源与端侧构成产业格局的第二条主线，其逻辑与闭源阵营正交：可下载权重把 grounding/planning 能力商品化，model-agnostic 的编排框架把"用哪个 LLM"与"如何驱动 GUI"解耦，而端侧部署则用小模型换取隐私、延迟与离线可用性。本节按三层展开——开源基础/grounding 模型、开源 agent 框架/编排层、端侧部署可行性。需要提醒的是，本节的 star 数、许可、benchmark 分数均为时点信息，随版本迭代快速变化。

#### 9.4.1 开源基础模型与 grounding 模型

这一层是"训练一个权重可下载的模型"。主流路线高度收敛：以 Qwen2-VL / Qwen2.5-VL / Qwen3-VL 或 InternVL 为 backbone，堆大规模跨平台 GUI grounding + action 数据做 SFT/RL。截至 2026-07，开源阵营已在若干 benchmark 上追平甚至反超闭源 CUA——OpenCUA-72B 在 OSWorld-Verified 上 45.0% 为开源 SOTA 并逼近 Claude（厂商自述，来源见下）。

| 模型 | 机构 | Backbone | 规模 | 权重许可 | 定位 / 关键 claim（时点） |
|:---|:---|:---|:---|:---|:---|
| [[Papers/2501-UITARS|UI-TARS]] / UI-TARS-1.5 / [[Papers/2509-UITARS2|UI-TARS-2]] | ByteDance | Qwen2-VL | 2B/7B/72B（SFT+DPO），1.5-7B | 1.5-7B 为 Apache-2.0；1.5 的 72B/32B 仅开放 research access（邮件申请） | native end-to-end agent；1.5 引入 RL 推理 |
| [[Papers/2410-OSAtlas|OS-Atlas]]-Base | Shanghai AI Lab / SJTU / HKU / MIT | InternVL2-4B / Qwen2-VL-7B | 4B/7B | Apache-2.0 | grounding foundation；13M 跨平台 corpus + ScreenSpot-V2，已成 de facto baseline |
| [[Papers/2400-NavigatingDigitalWorldAs|UGround]]-V1 | OSU-NLP + Orby AI | Qwen2-VL | 2B/7B/72B | Apache-2.0 | ICLR'25 Oral；发布时 ScreenSpot-Pro 18.9→31.1 SOTA |
| OpenCUA | XLANG Lab (HKU) | Qwen2.5-VL | 7B/32B/72B | MIT | NeurIPS'25 Spotlight；OSWorld-Verified 开源 SOTA（32B 34.8% / 72B 45.0%）；含 AgentNet 22.6k 轨迹数据集与全栈 |
| [[Papers/2400-AguvisUnifiedPureVision|Aguvis]] | HKU / Salesforce | Qwen2-VL | 7B/72B | 开源权重（HF） | pure-vision 统一动作空间，两阶段训练 |
| [[Papers/2506-ShowuiOneVisionLanguage|ShowUI]] | NUS Show Lab | Qwen2-VL | 2B | 开源权重（HF） | 轻量级、面向小模型 grounding |
| [[Papers/2501-InfiGUIAgent- A Multimodal Generalist GUI Agent with Native Reasoning and Reflection|InfiGUIAgent]] | InfiX 等 | — | 2B | 开源权重 | native reasoning + reflection |
| GUI-Owl / Mobile-Agent-v3(.5) | Alibaba Tongyi | Qwen2.5-VL / Qwen3-VL | 2B/4B/8B/32B/235B | 开源权重（HF） | 多尺度、多平台 fundamental agent 族 |
| [[Papers/2606-XiaomiGUI0|Xiaomi-GUI-0]] | Xiaomi | Qwen3-VL-30B-A3B | 30B（A3B active） | technical report（权重发布状态未检索到明确说明） | 真实设备闭环训练的 mobile agent |

关键观察：开源阵营的护城河越来越是"数据 + infra"而非架构——OS-Atlas 的价值在其 13M 跨平台 grounding corpus 与合成工具链，OpenCUA 的价值在 AgentNetTool 采集器 + 22.6k 真实轨迹 + 可复现评测，两者都把权重之外的整条 pipeline 一起开源。许可上主力项目普遍采用 Apache-2.0 / MIT 等宽松协议，商用友好；但顶配模型常保留（UI-TARS-1.5 的 72B 仅 research access），形成"小模型全开、大模型半开"的分层策略。

#### 9.4.2 开源 agent 框架与编排层

与"训练模型"正交的是"编排层"：这类项目多为 model-agnostic，接任意 LLM/VLM，靠 prompt、工具与流程编排而非自有权重取胜，因此迭代快、社区体量大（browser-use 的 star 数已超过任一开源模型 repo 一个数量级）。

| 项目 | 机构 | 类型 | 许可 | Stars（时点） | 特点 |
|:---|:---|:---|:---|:---|:---|
| browser-use | Browser Use Inc. | 浏览器自动化库 | MIT | 106k（as of 2026-07） | 已从 Playwright 转向 CDP 直连；接任意 LLM，可本地/自托管；自述 Odyssey leaderboard 87.4%（厂商自述） |
| Skyvern | Skyvern-AI | 浏览器 workflow 自动化 | AGPL-3.0（core） | 20k+（as of 2026-07） | swarm-of-agents + 视觉，抗 layout 变化；RPA-adjacent；Docker 自托管、MCP-ready、支持 Ollama 本地模型 |
| [[Papers/2504-AgentS2|Agent-S]] / S2 / S3 | Simular AI | CUA compositional 框架 | Apache-2.0（pip `gui-agents`） | 10.9k（as of 2026-04） | Manager-Worker + Mixture-of-Grounding；S3 首次在 OSWorld 超人类（72.60%，arXiv 2510.02250） |
| OpenAdapt | MLDSAI Inc. | 桌面 process automation（demo→replay） | MIT | 未检索到明确 star 数 | 录制人类演示学习自动化；on-prem、内置 PII/PHI 脱敏；面向受监管行业 |
| OpenCUA stack（AgentNetTool / AgentNetBench） | XLANG Lab | 数据采集 + 离线评测 | MIT | 见 9.4.1 | 跨 Win/macOS/Ubuntu 演示采集 + 可复现评测 |

早期的 [[Papers/2401-WebVoyager|WebVoyager]]（multimodal web agent + benchmark）是这条线的先驱开源 baseline，为后续 browser-use / Skyvern 等生产级框架提供了任务与评测范式。整体上，编排层与模型层形成互补生态：browser-use / Skyvern / Agent-S 可挂载 UGround / UI-TARS / OpenCUA 等开源 grounder，也可接闭源 API，用户据此在"成本、隐私、能力"三角上自由取舍。

#### 9.4.3 端侧 / On-Device 部署

端侧动机清晰：隐私（截图不出设备）、低延迟、离线可用、无 per-call 成本——Apple 的 [[Papers/2500-FerretUiLiteLessons|Ferret-UI Lite]] 明确把"避免云端大模型的高延迟、弱隐私、依赖网络"列为 3B 端侧模型的立项理由。可行性证据正在积累：

- **小模型 grounding 已接近可用**：Ferret-UI Lite（Apple，3B）在 ScreenSpot-V2 / ScreenSpot-Pro / OSWorld-G 上达 91.6% / 53.3% / 61.2%，grounding 上反超多个更大模型；[[Papers/2601-ZonUI3B|ZonUI-3B]]（WACV'26）证明单张 RTX 4090 即可训出 ScreenSpot 84.9% 的 3B grounder；UGround / UI-TARS / ShowUI 均提供 2B 档，Qwen2.5-VL-3B 被官方定位为 edge AI 方案。
- **long-horizon 仍是端侧短板**：同一 Ferret-UI Lite 在多步导航上仅 AndroidWorld 28.0% / OSWorld 19.8%，作者直言小模型 long-horizon reasoning 是固有挑战。这与"grounding 可小模型化、planning 仍需大模型"的整体判断一致。
- **分级/云端接力成为务实折衷**：OpenPhone（Qwen2.5-VL-3B）默认端侧执行、仅把复杂子任务实时上抛云端，显著降低云成本；GUI-Owl-1.5 / Mobile-Agent-v3.5 提供 2B（edge）到 235B（cloud-only）的连续尺度谱系；[[Papers/2606-XiaomiGUI0|Xiaomi-GUI-0]] 则走真实设备闭环路线，把异常态恢复能力烘焙进 30B-A3B（激活 3B）权重。
- **本地部署 infra 已成熟**：上述开源权重普遍支持 vLLM（OpenCUA 官方支持 7B/32B/72B）与 Ollama 本地服务；编排层 browser-use / Skyvern / OpenAdapt 均可本地/on-prem 运行，端侧模型 + 本地编排可构成完全离线的 CUA 栈。

小结：截至 2026-07，端侧 CUA 的现实形态是"端侧小模型负责 grounding / 单步交互 + 云端大模型补 planning / 长程"的混合架构；纯端侧、全离线的长程 agent 尚未达到实用成功率，是明确的开放问题。


<!-- ===== group: 9.6-9.7-infra-credentials ===== -->

### 9.6 Browser, VM, and Sandbox Infrastructure

Computer-Use Agent 的能力上限由模型决定，但**可用性上限由运行时基建决定**：agent 需要一个能被程序驱动、可弹性扩容、能抗反爬指纹、可被人类实时接管的浏览器或操作系统实例。围绕这一需求，2024–2026 年间形成了一个专门为 agent 供给运行时的基础设施层——把"如何维护一支浏览器/VM 舰队"从每个 agent 团队的自建负担，变成按会话计费的托管服务。供给形态大致分三档：**云端浏览器（cloud/headless browser）**、**代码/microVM 沙箱（code sandbox）**、以及**完整桌面 VM（virtual desktop）**；三者按"重量"递增，覆盖从纯网页操作到运行任意桌面软件的不同任务面。

**云端浏览器服务**是最活跃的一档，其价值主张是把 Playwright/Puppeteer/Selenium 的远程会话、stealth/反 bot 指纹、residential proxy、CAPTCHA 求解、认证态保持、以及供人类调试/接管的 live view 打包为一个 API。

| 服务 | 形态 / 开源 | 关键能力 | 时点信息（as of 2026-07） |
|:--|:--|:--|:--|
| **Browserbase** | 闭源托管；开源 SDK **Stagehand**（Playwright+AI）| 云端 Chrome 会话、stealth/反指纹、residential proxy、自动 CAPTCHA、认证态、live view+录制回放、MCP server | 2024 年由 Paul Klein IV 创立；2025-06 完成 $40M B 轮（约 $300M 估值，Notable Capital 领投，CRV/Kleiner Perkins 跟投），累计约 $68M；厂商自述 2025 年处理 50M+ 会话、1,000+ 客户 |
| **Steel** | **开源**浏览器 API（`steel-dev/steel-browser`）+ 托管云 | RESTful 会话管理、Stealth Browser、专用 IP、auth-walled 站点访问、CAPTCHA、Session Viewer；Rust/Go/原生 SDK；单会话最长 24h | 定位"开源、透明的浏览器层"；厂商自述同区域会话冷启 <1s（其自published benchmark 对自身有利，需谨慎） |
| **Hyperbrowser** | 闭源托管 | stealth-first、云原生、高并发容器化浏览器，面向 agentic 用例打包 | 主打"路线图明确 agentic"的差异化定位 |
| **Anchor Browser** | 闭源托管 | 云端浏览器自动化、stealth、proxy fingerprinting、session management、CAPTCHA | 厂商自述 WebVoyager 89% 任务完成率；免费档 $10/月额度 + 100 浏览器小时 |
| **Cloudflare Browser Run**（原 Browser Rendering）| 闭源，随 Cloudflare 平台 | 全球网络上的 headless Chrome、Live View、**Human in the Loop**、CDP 访问、session recording、WebMCP | 2026-04-15 更名/重构；2026-05 迁移至 Cloudflare Containers，并发 30→120、响应快 50%；属其"六层 agent 基建栈"的 browsing 层 |
| **Kernel** | 托管浏览器基建 | 面向 agent 的远程浏览器 | 独立公司，公开细节有限（见 uncovered）|

**代码沙箱与桌面 VM**面向"agent 需要执行不受信代码或操作 GUI 之外的桌面软件"的场景，核心竞争点是**隔离模型**与**冷启延迟**的权衡。

| 服务 | 隔离模型 | 形态 | 时点信息（as of 2026-07） |
|:--|:--|:--|:--|
| **E2B** | **Firecracker microVM**（内核级隔离）| 开源（主仓 Apache-2.0）云沙箱；含 **E2B Desktop**（带 GUI 桌面环境，供 computer use）| 沙箱创建 <200ms；支持 Python/JS/TS/R/Java/Bash；BYOC（AWS/GCP）；2025-07 完成 $21M A 轮（Insight Partners 领投），累计约 $32.5M；厂商自述 88% Fortune 100 注册、2025-03 达 15M 沙箱/月（较 2024-03 增 375×）|
| **Modal** | **gVisor** 容器隔离，deny-by-default 入站 | Python 原生 serverless 云，支持 A100/H100 GPU | 厂商自述支持 100,000+ 并发沙箱 |
| **Daytona** | 默认 **Docker 容器**，可选 Kata/Sysbox 加固 | 沙箱生命周期自动化（auto-stop/archive/delete）、warm-start | 2025-02 从 dev-environment 转型为 agent 代码运行时；2026-02 完成 $24M A 轮；**2026-06 生产代码闭源**（开源仓归档）|
| **Fly Machines** | microVM | 低层原始 primitive，供自建 | 供团队自搭沙箱 |
| **Vercel Sandbox** | Firecracker | 面向 agent 的托管代码执行 | 见 uncovered（细节未充分核实）|
| **Scrapybara** | 完整 VM / 桌面 | **Ubuntu / Windows / Mac** + 纯 browser 三档实例；Act SDK；ComputerTool/BashTool | YC F24；厂商自述 <1s 启动、可扩至数百实例；对接 OpenAI CUA API；按用量计费（Windows/Mac 为 early-access/企业档）|

从这张图景可以提炼三条 pattern。**其一，隔离模型是安全与延迟的核心 trade-off**：Firecracker（E2B、Vercel）给每个沙箱独立内核，隔离最强但冷启略高；gVisor（Modal）居中；Docker（Daytona 默认）启动最快但共享宿主内核、边界最弱——这直接决定了"能否安全运行 agent 生成的不受信代码"。**其二，能力正在同质化**：stealth 反指纹、residential proxy、CAPTCHA 求解、**认证态/会话持久化**、live view + Human-in-the-Loop 接管，已从差异化卖点变成入场券（Browserbase、Steel、Cloudflare Browser Run 均已具备），竞争转向延迟、并发规模与计量计费精度。**其三，开源与托管两条路线并存**：Browser Use（Magnus Müller / Gregor Žunič，Playwright 之上的开源 agent 库，2025-01 已 21k+ stars）与 Stagehand、Steel 提供开源运行时/SDK，让团队可自托管；而 Browserbase/Scrapybara 则以托管舰队 + 按会话计费取胜。值得注意 Daytona 在 2026-06 反向从开源转闭源（理由是"AI 辅助漏洞挖掘对公开仓库的风险"），暗示安全基建的开源合规边界仍在拉扯。

### 9.7 Credential and Permission Management

当 agent 要替用户完成"登录邮箱、下单、转账"这类任务时，它必须以某种方式持有登录态与执行权限——这既是 CUA 落地的刚需，也是其最大的安全暴露面。核心矛盾一句话概括：**agent 需要足够权限完成任务，但任何被 agent 直接持有的原始凭证都会因 prompt injection、日志泄露、跨会话残留而放大 blast radius**。2026 年的业界共识因此是"**agent 不应直接持有原始 secret**"——凭证应由外部 vault/工具层持有，agent 只在运行时申请一枚**范围受限、短时效**的 token。围绕这一原则，实践中形成了四类互补机制。

| 机制 | 做法 | 代表实现 | 出处 |
|:--|:--|:--|:--|
| **人类接管闸门（human takeover）** | 遇登录/支付时暂停，让用户在 agent 不截屏的模式下手动输入凭证，再交回控制权 | OpenAI Operator/ChatGPT agent "takeover mode"；Claude for Chrome 高风险动作确认 | 厂商文档 |
| **会话/认证态持久化** | 用户登录后保存 session cookie / auth state，跨步骤复用，避免反复登录 | Browserbase、Scrapybara、Steel 的 authenticated sessions | 厂商文档 |
| **委托式 OAuth + token vault** | vault 存储并轮换凭证，per-user/per-provider 加密隔离，运行时按需签发 scoped token，**凭证从不暴露给 LLM** | Arcade.dev（JIT consent）、Auth0 Token Vault、Nango（开源，800+ API）、HashiCorp Vault（动态 secret + user attribution）、1Password | 厂商文档/媒体 |
| **网站侧权限声明 + 动作 gating** | 网站以机器可读 manifest 声明"允许读什么/做到哪步/哪些需人工审批"；agent 侧对高风险动作强制确认或 step-up 认证 | [[Papers/2512-PermissionManifestsWebAgents|agent-permissions.json]]（`human_in_the_loop` modifier）；Auth0 step-up（5 分钟单动作 elevated token）| 论文 + 厂商文档 |

**人类接管**是当前消费级 CUA 的主力方案，也是"agent 永不见密码"的实现路径。OpenAI Operator 在遇到登录或支付时进入 takeover mode，由用户亲自输入且系统不截取该过程；对邮箱、金融等敏感站点则启用 watch mode 要求用户实时监督；在提交订单、发送邮件等重要动作前要求确认——据其 system card，确认机制把模型犯错风险降低约 90%（as of 2026-07，来源 OpenAI system card）。但 Operator 的一个关键 caveat 揭示了该方案的边界：**登录后它会保留 session cookie 并跨任务保持登录态，直到用户显式登出或清 cookie**——即"agent 不见密码"并不等于"agent 无持久访问权"，撤销访问需额外动作。Anthropic 的 Claude for Chrome 走站点级权限 + 动作确认路线：用户可随时按站点授予/撤销访问，对发布、购买、分享个人数据等高风险动作要求确认，并对金融/成人/盗版内容默认拦截；其红队数据显示无防护时注入攻击成功率 23.6%，加入 safeguard 后自主模式降至 11.2%、对特定 browser-specific 攻击降至 0%（as of 2026-07，来源 Anthropic blog）。

**委托式 OAuth + token vault** 是面向生产/企业 agent 的方向，把凭证处理从 agent 进程"下推到工具层"。其纪律是 least-privilege 与 just-in-time：不再给 agent 静态 secret，而是在每次工具调用时按角色签发 scoped、短时效 token，任务结束即失效；授权也从"一次认证"转为"每次调用做动态 scope 评估 + 上下文策略"（continuous authorization）。MCP 生态把这一模式标准化——其授权规范建立在 **OAuth 2.1 + PKCE** 之上，含 scope-based 权限、用户 consent 与动态客户端注册（DCR/CIMD）。这一转向的驱动力是量级问题：多方报告称企业中非人类身份（NHI）已以 40:1 以上倍数超过人类身份，且 GitGuardian 在公开 GitHub 的 MCP 配置文件中就发现约 24,000 个泄露 secret，使"环境变量塞凭证"成为明确的反模式（as of 2026-07，来源 Descope/Nango/Strata 等厂商与安全报告，属行业观察）。

综合看，这两个子节共同勾勒出 CUA 落地的"隐性栈"：运行时基建（§9.6）解决"agent 在哪里跑、如何抗封与被接管"，凭证/权限层（§9.7）解决"agent 以谁的身份、多大权限跑"。二者的交汇点正是**会话持久化**——它既是基建的核心卖点，又是权限治理最难收敛的残留态：一枚被托管浏览器保存的 auth cookie，在便利与"最小权限/可撤销"之间制造了持续张力。学术侧的 [[Papers/2512-PermissionManifestsWebAgents|Permission Manifests]] 与 [[Papers/2605-EnvTrustBench|EnvTrustBench]]（把 action gating 列为环境接地的独立控制层）等工作，正在尝试把这些工程惯例形式化为可评测、可执行的治理原语，但 enforcement 仍主要依赖合规激励而非强制机制。


<!-- ===== group: industry-9.1-9.2 ===== -->

### 9.1 Foundation Model and API Providers

Computer-use 能力已从研究原型收敛为几家前沿实验室以 **API/工具**形态对外提供的标准化接口：模型输出屏幕坐标级动作（click/type/scroll/drag/keypress + screenshot），由开发者侧的 harness（浏览器、VM、桌面）执行并回传截图，形成 agent loop。三家美国前沿实验室（OpenAI、Anthropic、Google DeepMind）各自提供原生 CU 基础模型，Amazon 与 Microsoft 则以云服务/企业平台形态封装（Microsoft 直接复用 OpenAI 与 Anthropic 的模型）。开源权重路线（ByteDance UI-TARS [[Papers/2501-UITARS]] [[Papers/2509-UITARS2]]、OS-Atlas [[Papers/2410-OSAtlas]]、OpenCUA [[Papers/2508-OpenCUA]]）见 §9.3，此处只覆盖闭源 API/平台供给方。

| 供给方 | 模型 / 接口 | 形态 | 支持环境 | 可用性状态（as of 2026-07） |
|:--|:--|:--|:--|:--|
| OpenAI | `computer-use-preview`（CUA）；新版 computer use tool | Responses API 内置工具 / Agents SDK | 浏览器、VM/Docker、X11 桌面（开发者自建 harness） | 公开可用；新版 CU 训练进 `gpt-5.4` 及后续模型（官方文档） |
| Anthropic | computer use tool（beta） | Claude API 工具（beta header），亦上架 AWS Bedrock / Google Vertex | 桌面沙箱（截图+鼠标+键盘），可与 bash / text-editor 工具组合 | Beta；2024-10 首发（Claude 3.5 Sonnet），现支持 Sonnet 5、Opus 4.8/4.7/4.6/4.5、Sonnet 4.6（官方文档） |
| Google DeepMind | Gemini computer use（原独立 Gemini 2.5 Computer Use 模型 → 内建于 Gemini 3.5 Flash） | Gemini API / AI Studio / Vertex AI 内置工具 | 主打浏览器（官方称非为 OS 级控制优化）；3.5 Flash 起扩至 mobile/desktop | 2.5 版 2025-10 preview；computer use 于 2026-06-24 成为 Gemini 3.5 Flash 内置工具（官方 blog） |
| Amazon | Nova Act（`nova-act` SDK / AWS 服务） | Python SDK + AWS 托管服务，基于 Playwright 驱动浏览器 | 浏览器 UI workflow，支持 MCP / Strands 等框架 | research preview 2025-03 → GA（AWS 服务）2025-12-02（GitHub/官方） |
| Microsoft | Copilot Studio "computer-using agents" | 企业 agent 构建平台（非自研 CU 基座，复用 OpenAI CUA + Claude Sonnet 4.5） | 浏览器 + Windows 桌面应用（desktop 为 preview） | GA 2026-05-13，覆盖全部商用 Power Platform 地域（官方 Tech Community） |

**OpenAI.** OpenAI 的 Computer-Using Agent（CUA）最初随 Operator 于 2025-01 亮相，官方 CUA 页自述在 OSWorld 达 38.1%、WebArena 58.1%、WebVoyager 87%（厂商自述，as of 2026-07，来源 openai.com/index/computer-using-agent）。开发者侧现有两条路径：早期的 `computer-use-preview` 模型，以及新版 computer use tool——后者官方文档将 CU 训练并入 `gpt-5.4` 及后续模型，通过 Responses API 内置 loop 或自建 harness（Playwright/Selenium/VNC）调用（官方文档，as of 2026-07）。计价方面仅检索到第三方聚合站将 `computer-use-preview` 列为 input $3 / output $12 每百万 token（未经官方页确认，as of 2026-07，来源 economize.cloud），官方价目需人工复核。

**Anthropic.** Claude 的 computer use tool 自 2024-10（Claude 3.5 Sonnet）起以 beta 形态提供，是最早对外开放的 CU 开发者接口之一。官方文档（as of 2026-07）显示当前经 `computer-use-2025-11-24` beta header 支持 Claude Sonnet 5、Opus 4.8/4.7/4.6/4.5、Sonnet 4.6，经 `computer-use-2025-01-24` 支持 Sonnet 4.5、Haiku 4.5 等；工具提供截图、鼠标、键盘与桌面自动化，可与 bash、text-editor 工具组合成完整自动化链，并同时上架 AWS Bedrock 与 Google Vertex。相较 OpenAI，Anthropic 的差异化在于把同一套能力延伸到"在你自己机器上工作"的产品形态（Claude Code / 桌面产品，见 §9.2）。

**Google DeepMind.** Google 起初以独立的 **Gemini 2.5 Computer Use** 模型（2025-10-07 preview，经 Gemini API / AI Studio / Vertex AI 提供）进入 CU 竞争，官方明确其"主打浏览器控制、未针对 OS 级控制优化"，并以 Browserbase harness 上的 Online-Mind2Web 自述领先延迟/质量（厂商自述）。2026-06-24 起，computer use 不再是独立模型而成为 **Gemini 3.5 Flash 的内置工具**，官方称扩展到 browser/mobile/desktop 环境（官方 blog，as of 2026-07）。这一路径与被关停的消费级 Project Mariner（见 §9.2）互补——Mariner 的 CU 技术亦被官方描述为"并入 Gemini API / Vertex AI"。

**Amazon 与 Microsoft.** Amazon **Nova Act** 于 2025-03 以 research preview + `nova-act` SDK 出场，2025-12-02 升级为 GA 的 AWS 托管服务，用 Playwright 驱动浏览器、用自然语言+Python 定义 workflow，官方自述在早期客户构建的浏览器 UI 自动化上达到约 90% 可靠性（厂商自述，as of 2026-07）。Microsoft 走平台路线：Copilot Studio 的 "computer-using agents" 于 2026-05-13 GA（官方 Tech Community），本身不自研 CU 基座，而是复用 OpenAI CUA 与 Claude Sonnet 4.5，配合 Azure Key Vault 凭据托管、Purview 审计与 human-in-the-loop，Windows 桌面应用自动化仍为 preview——定位是把 CU 作为 legacy 系统"无 API 也能自动化"的 RPA 替代（官方博客，as of 2026-07）。

### 9.2 Consumer Computer-Use Products

面向终端用户的 CU 产品在 2025–2026 经历了一轮明显的**形态收敛**：独立品牌（OpenAI Operator、Google Project Mariner、乃至 OpenAI 自家的 Atlas 浏览器）纷纷被关停并折叠进主力聊天产品或浏览器扩展，反映厂商判断"CU 更适合作为主产品内的一个 agent 模式，而非单独 app"。当前活跃形态有三类：主聊天产品内的 **agent mode**（ChatGPT Agent、Gemini Agent）、**浏览器扩展/侧栏**（Claude for Chrome）、以及 **agentic 浏览器**（Perplexity Comet；OpenAI Atlas 正在退场）。

| 产品 | 提供方 | 形态 | 平台 | 可用性 / tier（as of 2026-07） |
|:--|:--|:--|:--|:--|
| ChatGPT Agent | OpenAI | ChatGPT 内 agent mode（自带虚拟机+浏览器） | ChatGPT（web/desktop） | 2025-07 上线；Plus / Pro / Team / Business / Enterprise |
| ChatGPT Atlas | OpenAI | agentic 浏览器（含 agent mode） | macOS（Windows 后续） | 2025-10-21 上线 → **2026-08-09 停止运行**（并入 ChatGPT 桌面端+Chrome 扩展；TechCrunch） |
| ChatGPT Work | OpenAI | ChatGPT 内长任务 agent（GPT-5.6） | ChatGPT 桌面端 | 2026-07-09 发布，先 Pro/Enterprise/Edu 后扩至 Plus/Business（TechCrunch/The Register） |
| Claude for Chrome | Anthropic | Chrome 扩展 + 侧栏 | Chrome | research preview 2025-08-26（1000 Max 用户）→ **2025-12 扩至全部付费计划** |
| Gemini Agent | Google | Gemini app 内 agent（承接 Mariner） | Gemini app | 承接 Project Mariner 能力；Mariner 独立产品 2026-05-04 停运 |
| Project Mariner | Google | 独立 agentic 浏览器扩展（Gemini 2.0/2.5） | Chrome 扩展 | 2024-12-11 prototype → **2026-05-04 discontinued**（Wikipedia/Digital Trends） |
| Comet | Perplexity | agentic 浏览器（Comet Assistant 侧栏） | macOS/Windows/Android/iOS | 2025-07 Max 独占 → **2025-10 全球免费**；Android 2025-11、iOS 2026-03 |

**OpenAI 产品线的三次折叠。** Operator 于 2025-01-23 作为 research preview 面向美国 ChatGPT Pro（$200/月）推出，2025-07 被 **ChatGPT Agent** 取代并于 2025-08-31 关停——CU 能力自此以 ChatGPT 内 "agent mode" 形态提供给 Plus/Pro/Team 等付费层（官方，运行在带浏览器/终端的虚拟机中，执行高风险动作前请求确认）。2025-10-21 OpenAI 又推出 agentic 浏览器 **ChatGPT Atlas**（macOS，agent mode 面向 Plus/Pro/Business 预览）；但不到一年，2026-07-09 OpenAI 宣布把 Atlas 的 agentic browsing 能力并回 ChatGPT 桌面端与一个 Chrome 扩展，**Atlas 于 2026-08-09 停止运行**，同时推出基于 GPT-5.6、跑数小时长任务产出成品文档的 **ChatGPT Work**（TechCrunch / The Register，as of 2026-07；这些为 2026-07 时点信息，建议投稿前复核）。这条时间线本身即是 §9.2 开头"品牌收敛"论断的最强证据。

**Anthropic：从扩展到"在你机器上工作"。** **Claude for Chrome** 于 2025-08-26 以 research preview 形态放给 1000 名 Max 用户（其余排 waitlist），Anthropic 公开的红队数据显示无防护时浏览器攻击成功率 23.6%、加固后降至 11.2%、部分浏览器专属攻击从 35.7% 降至 0%（厂商自述），并配套高风险站点拦截、逐站授权、管理员 allow/blocklist 等机制。该扩展于 2025-12 从 Max 独占扩展到全部付费计划（Pro/Max/Team/Enterprise，as of 2026-07）。与浏览器沙箱路线并行，Anthropic 还把 CU 延伸到用户本机（Claude Code / 桌面产品由产品侧管理会话与授权升级），形成"沙箱 API vs 本机产品"两套执行契约。

**Google：Mariner 退场、能力并入 Gemini app。** **Project Mariner** 2024-12-11 作为研究原型发布，2025-05 面向美国 Google AI Ultra 订阅者开放，是最早的消费级 agentic 浏览器之一；但作为独立产品于 **2026-05-04 停运**（Wikipedia / Digital Trends），官方称其技术"航行到了其他 Google 产品"——web 自动化任务（收邮件、订位、多步流程）现由 Gemini app 内的 **Gemini Agent** 承接，底层 CU 能力则进入 Gemini API / Vertex AI（见 §9.1）。这与 OpenAI 关停 Operator/Atlas 是同一模式。

**Perplexity Comet：反向扩张的异类。** 与前三家"收敛进主产品"相反，Perplexity 的 agentic 浏览器 **Comet** 走了独立扩张路线：2025-07 以 Max（$200/月）独占上线，waitlist 达数百万，2025-10 起**全球免费**并陆续补齐 Windows/macOS/Android（2025-11-20）/iOS（2026-03-18）四端（CNBC / Wikipedia，as of 2026-07）。核心是每个新标签页侧栏常驻的 Comet Assistant（可跨 tab 导航、汇总、执行用户发起的任务）；免费层提供实时问答与页面摘要，付费层（Max）解锁更强模型与可后台异步跑多步任务的 Background Assistant / Email Assistant。需注意 Comet 截至 2026-07 尚未公开完整独立安全审计（媒体观点）。


<!-- ===== group: industry-9.8-9.10 ===== -->

### 9.8 Observability, Auditing, and Governance

Computer-use agent 的失败不发生在单次 API 调用，而潜藏在"观察 → 推理 → 动作"的多步因果链里：系统可以在架构层"优雅失败"（不抛异常、返回 HTTP 200）却做出错误甚至危险的动作，因此传统 APM 无法暴露 agent 的失效模式，产业界在 2023–2024 年催生出"agent observability"这一独立品类（[Confident AI, 2026-07 检索](https://www.confident-ai.com/knowledge-base/compare/best-ai-agent-observability-tools-2026)）。本节梳理三条正在成型的产业能力：trace/回放工具、遥测标准化、以及审计与合规治理。三者对 computer-use agent 尤为关键——因为它执行的是提交表单、删除数据、下单付款等不可逆的真实世界动作（[[Papers/2500-TowardsTrustworthyGuiAgents]]）。

**（1）Observability / trace 工具生态。** 主流平台已形成"开源 vs 闭源 × 框架绑定 vs 中立"的分层格局。下表信息为二手对比评测（2026 年）与厂商文档的综合，定位判断为评测方观点而非厂商自述：

| 平台 | 开源/闭源 | 定位与特点 | 与 computer-use 相关性 |
|:--|:--|:--|:--|
| LangSmith | 闭源（self-host 仅企业版） | LangChain/LangGraph 生态最深；LangGraph Studio 支持 checkpoint 状态回退与可视化调试 | 状态回退/回放对多步 GUI 轨迹调试有用 |
| Langfuse | 开源（MIT） | prompt/eval/dataset 管理强，token 级成本追踪；2026-01 被 ClickHouse 收购，代码仍维护 | token 级成本追踪贴合 agent 高消耗特性 |
| Arize Phoenix | 开源 | OTel-native，采用 OpenInference 语义约定，评测导向 | 标准化 trace，易接入 whole-stack APM |
| Datadog LLM / Agent Observability | 闭源 | 原生支持 OTel GenAI semantic conventions（v1.37+），与基础设施 APM 打通 | 生产级 session trace + 基础设施关联 |
| AgentOps / Braintrust / Helicone / Laminar | 混合 | 分别偏 agent-first 监控 / eval / gateway / 调试 | 覆盖 agent 调试与评测细分需求 |

（来源：[Latitude 2026-07 检索](https://latitude.so/blog/best-llm-observability-tools-agents-latitude-vs-langfuse-langsmith)、[Confident AI 2026-07 检索](https://www.confident-ai.com/knowledge-base/compare/best-ai-agent-observability-tools-2026)）一个反复出现的评测结论是：agent observability 与基础设施 observability 是两层，LLM trace 平台通常要与传统 APM 配套使用；且不同平台开销差异显著（某多步旅行规划工作流下 Langfuse/AgentOps 引入约 15%/12% 额外开销，而 LangSmith 近乎无可测开销——单一评测结果，非普适结论）。

**（2）遥测标准化：OpenTelemetry GenAI Semantic Conventions。** 产业正收敛到 OTel 作为 agent 遥测的统一层。OpenTelemetry 于 2024-04 成立 GenAI SIG，最初仅覆盖 LLM 客户端调用，现已扩展到 agent 编排、MCP 工具调用、内容捕获与质量评估；其 span 结构为顶层 `invoke_agent` span 下嵌 `chat`（每次 LLM 调用）与 `execute_tool`（每次工具调用）子 span，标准属性含 `gen_ai.request.model`、`gen_ai.usage.input/output_tokens`、`gen_ai.response.finish_reasons` 等（[OpenTelemetry 官方 blog, 2026-07 检索](https://opentelemetry.io/blog/2026/genai-observability/)；[GenAI semconv repo, 2026-07 检索](https://github.com/open-telemetry/semantic-conventions-genai)）。该约定由 CNCF 背书，其设计目标被明确表述为"捕获 agent 的决策图（decision graph）而非仅 I/O 边界"；Datadog、Honeycomb、New Relic 及 LangChain、CrewAI、AutoGen 等框架已原生或经 instrumentation 输出合规 span（[Datadog, 2026-07 检索](https://www.datadoghq.com/blog/llm-otel-semantic-convention/)）。这是"厂商各自为政的 trace 格式"走向可互操作审计基础设施的关键一步。

**（3）审计与治理：从"事后看日志"到"执法即审计"。** 监管压力正把 observability 从工程可选项抬升为合规硬约束。EU AI Act 的高风险义务（含 Article 12 自动事件日志，最低保留 6 个月）将于 2026-08-02 进入可执法阶段；对 computer-use agent 这类跨系统、代表用户认证并执行动作的系统，传统"谁认证了谁负责"的问责模型失效——orchestrator → sub-agent → API → 数据库的委托链使问责分散，业界提出的技术对策是不可篡改审计轨迹 + 签名日志，并强调"若治理层只是事后看日志的独立观察者，对高风险系统已属不合规"（二手厂商/咨询解读，非监管原文，[Zylos Research, 2026-07 检索](https://zylos.ai/research/2026-05-01-ai-agent-governance-compliance-2026/)；[DigitalApplied, 2026-07 检索](https://www.digitalapplied.com/blog/ai-agent-governance-policy-compliance-2026)）。AI agent 治理被定位在 EU AI Act、NIST AI RMF 1.0、ISO/IEC 42001:2023、SOC 2、GDPR 五套框架的交叉点上。

学术侧为此提供了词汇表与方法学：[[Papers/2606-AgentTracesToTrust]] 把 execution provenance（一次运行的 typed graph）与 evidence tracing（其在 evidence-support 关系上的投影）作为 process-level accountability 的基础，指出 final-answer accuracy 只观测执行终点、无法解释"哪条证据支撑哪个 claim、tool call 是否正当、failure 从何而起"，并规范化了 memory 的 temporal validity 与 provenance-aware retrieval trace（arXiv 2606.04990）。而 [[Papers/2510-HAL]] 用 LLM 驱动的日志分析（Docent）对 21,730 次 rollout 做规模化审计，实证了审计的价值：它抓出了人工难以发现的 benchmark 答案泄露、以及 web agent 用错误信用卡下单这类"部署级灾难动作"——后者与"弃答"在 accuracy 上同记 0 分却代价迥异，说明可观测性必须把 catastrophic action 检测作为一等维度（arXiv 2510.11977）。综合判断（本文推断）：computer-use agent 的审计需求比一般 LLM agent 更刚性——因为动作不可逆、且直接触达受监管数据——但目前跨组件、端到端的 provenance 评测仍不成熟（[[Papers/2606-AgentTracesToTrust]] 自陈为最大 gap）。

### 9.9 Cost, Latency, and Business Value

Computer-use agent 的经济学有一个反直觉的核心：单 token 价格持续暴跌，per-task 账单却在上涨。原因是架构性的——一次用户任务在 agent 化工作流下会触发 10–20 次模型调用（检索、推理、工具调用、验证、自纠），token 消耗是简单问答的 5–30 倍（[Cockroach Labs, 2026-07 检索](https://www.cockroachlabs.com/blog/agentic-ai-costs-at-scale/)）。本节从成本结构、延迟、以及商业价值三个角度展开，并接续 cost-accuracy Pareto 的产业含义。

**（1）成本结构：单价降、用量升。** 据 Ramp 企业支出数据，主流厂商每百万 token 均价一年内从约 \$10 降至 \$2.50，但账单仍升（[Cockroach Labs, 2026-07 检索](https://www.cockroachlabs.com/blog/agentic-ai-costs-at-scale/)）。EY 量化了编排如何抬高单次交互成本：2023 年简单线性工作流约 \$0.04/交互，2026 年含工具/推理/迭代循环的编排系统升至约 \$1.20/交互，约 30 倍（[EY, 2026-07 检索](https://www.ey.com/en_us/insights/ai/agentic-ai-token-costs)）。per-task token 用量的产业估计（二手指南，量级参考）：

| 任务类型 | 每任务 token（产业估计） |
|:--|:--|
| 简单问答 | 500–2,000 |
| 简单 tool-calling agent | 5,000–15,000 |
| 完整 agentic 工作流 | 15,000–80,000 |
| 复杂 multi-agent | 200,000–1,000,000+ |

（来源：[ValueStream AI, 2026-07 检索](https://valuestreamai.com/blog/cost-of-ai-agents-2026)、[Kunal Ganglani, 2026-07 检索](https://www.kunalganglani.com/blog/ai-agent-cost-per-task-2026)）对 computer-use / browser automation 这一子类，产业给出的两个专属优化是：用结构化输出（native markdown/JSON）替代原始 HTML 可降约 67% token，用 semantic locator 替代完整 DOM 树可省约 93% context（同上二手指南，厂商实践声明）。运行成本的最大杠杆是 model routing：某 Q1-2026 对 24 亿次企业 API 调用的分析显示，分层路由的中位混合成本 \$2.31/M token，而全量走 frontier 模型为 \$18.40/M token，差 87%（二手，[Cockroach Labs, 2026-07 检索](https://www.cockroachlabs.com/blog/agentic-ai-costs-at-scale/)）。

对 computer-use agent，成本与"完成度"深度纠缠：OSWorld 2.0 的前沿显示，Claude Opus 用极大 token 预算换取最高完成率，而 GPT 系更省 token 但更早触顶（详见 §9.10 数字），意味着"必须完成"与"必须便宜"是两条不同曲线。[[Papers/2510-HAL]] 进一步实证 scaffold 造成数量级成本差：Online Mind2Web 上 SeeAct+GPT-5 花 \$171、BrowserUse+Claude Sonnet 4 花 \$1,577（9× 差距）而 accuracy 只差 2 个百分点；且该 benchmark 单次评测平均 >\$450（arXiv 2510.11977）。

**（2）延迟：被忽视却是生产落地的首要障碍。** OSWorld-Human（首个 computer-use agent 时间性能研究）给出最直接的证据：即便最好的 agent 也比人类最优轨迹多花 2.7–4.3× 步数；planning/reflection/judging 的大模型调用占了整体延迟的大头；且随任务变长，后续每一步可比开头慢 3×，导致端到端延迟高达数十分钟，而人类完成同任务只需几分钟——作者据此断言"效率而非准确率才是 computer-use agent 生产落地的首要障碍"（[OSWorld-Human, arXiv 2506.16042, 2026-07 检索](https://arxiv.org/abs/2506.16042)）。值得注意的是，[[Papers/2510-HAL]] 因大规模并行 + API 限速导致 latency 方差过大而未纳入评测，说明产业级 latency 基准仍是空白（arXiv 2510.11977）。

**（3）定价模型与 cost-accuracy Pareto 的产业含义。** 消费级 computer-use 产品的计价仍在演化：OpenAI Operator（2025-01-23 发布、2025-08-31 关停）从未按任务计费，而是打包进 ChatGPT Pro 订阅；其继任者 ChatGPT agent 对消费者按订阅 + 月度用量上限（如 Plus 约 400 次 agent run），对企业/Workspace 则于 2025-07 转向 token/credit 计价（[OpenAI Operator 维基, 2026-07 检索](https://en.wikipedia.org/wiki/OpenAI_Operator)；[OpenAI 官方介绍, 2026-07 检索](https://openai.com/index/introducing-operator/)；[ChatGPT Rate Card, 2026-07 检索](https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu)）。这印证了 [[Papers/2407-AgentsThatMatter]] 与 [[Papers/2510-HAL]] 的方法学警告在产业上的现实意义：(a) accuracy 可被 retry 等"科学上无意义"的手段刷高，HumanEval 上 LATS 成本比简单 warming 策略高 50× 而 accuracy 无实质差异（arXiv 2407.01502）；(b) 最贵模型极少落在 accuracy-cost Pareto 前沿（9 个 benchmark 仅 1 个），提高 reasoning effort 在 36 个组合中 21 个"持平或更低"，且 per-token 成本作为 proxy 高度误导（token 前沿 ≠ 美元前沿；o3 发布后 3 个月价格跌 80%）——对采购方意味着"按当前价规划长期策略不可靠"（arXiv 2510.11977）。产业含义（本文推断）：computer-use agent 的选型不应看 leaderboard 峰值 accuracy，而应报"cost–accuracy Pareto + scaffold 匹配 + per-task 延迟"三联指标。

**（4）商业价值与 ROI。** 需坦诚区分：目前最响亮的企业 agent ROI 案例多为对话式/客服 agent 而非 computer-use agent，直接可比的 computer-use production ROI 数据仍稀缺（见 uncovered）。作为邻近证据：McKinsey State of AI 2025 显示 AI 采用率约 78%，但仅 23% 在至少一个职能中 scaling AI agents，仅 6% 属"AI 高绩效者"（EBIT 影响 ≥5%），39% 报告企业级 EBIT 影响——价值高度依赖工作流重构而非简单替换人力（[McKinsey, 2026-07 检索](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)）。Klarna 常被引为标杆：其 OpenAI 驱动的客服助手上线首月处理 2/3 客服对话，官方称相当于 700 名全职坐席、预计 2024 年增利 \$40M、平均对话时长从 11 分钟降到 2 分钟（[Klarna 官方新闻, 2026-07 检索](https://www.klarna.com/international/press/klarna-ai-assistant-handles-two-thirds-of-customer-service-chats-in-its-first-month/)；均为厂商自述、未经独立审计）——但 2025-05 CEO Siemiatkowski 向 Bloomberg 承认"砍人过深、质量下降"，重新招募人工坐席（二手报道），这一反转本身是"AI-first scoping"教训的重要 datapoint。综合判断：ROI 真实存在但强烈依赖 scoping 与工作流重设计，"按 chatbot 时代 token 假设算出的 ROI 会系统性低估真实成本"（[Cockroach Labs, 2026-07 检索](https://www.cockroachlabs.com/blog/agentic-ai-costs-at-scale/)）。

### 9.10 Industry Maturity and Deployment Gaps

综合各方证据，computer-use / agentic AI 目前处于"高期望、低落地"的阶段：投资与试点激增，但规模化生产部署稀少，且失败主因是治理/成本/价值而非单纯模型能力。本节给出成熟度快照，再逐一拆解阻碍生产落地的 gap。

**（1）成熟度快照。** Gartner 预测超过 40% 的 agentic AI 项目将在 2027 年底前被取消，主因是成本攀升、商业价值不清、或风险控制不足；并指出大量供应商在做"agent washing"（把 assistant/RPA/chatbot 重新贴牌），估计数千家自称 agentic 的供应商中只有约 130 家名副其实（[Gartner 新闻稿, 2025-06-25, 2026-07 检索](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027)）。Gartner 分析师 Anushree Verma 明言"多数 agentic AI 提案缺乏显著价值或 ROI，因当前模型不具备自主达成复杂业务目标的成熟度与 agency"（同上）；2025-01 一项 3,412 人的 Gartner 网研会调查中，仅 19% 称已做重大投资、42% 保守投资、31% 观望（同上）。Gartner 2026 Hype Cycle 将 agentic AI 置于"Peak of Inflated Expectations"，并称迄今仅约 17% 组织真正部署过 AI agent、逾 60% 预计两年内部署（二手转引，[DigitalApplied, 2026-07 检索](https://www.digitalapplied.com/blog/ai-agent-governance-policy-compliance-2026)）。独立佐证来自 MIT NANDA "The GenAI Divide: State of AI in Business 2025"：基于 52 场高管访谈 + 153 份调查 + 300 个公开部署的分析，95% 的 GenAI 试点未带来可测的 P&L 影响，核心症结不是模型质量而是企业集成的"learning gap"（该 95% 数字有方法学争议，需谨慎；[Legal.io 转载, 2026-07 检索](https://www.legal.io/blog/5719519/MIT-Report-Finds-95-of-AI-Pilots-Fail-to-Deliver-ROI-Exposing-GenAI-Divide)）。

**（2）部署 gap 逐项拆解。** 下表汇总当前主要 gap 与证据（严重度为本文综合判断）：

| Gap 维度 | 证据 | 严重度 |
|:--|:--|:--|
| 长程可靠性 | OSWorld 2.0：任务中位需人类约 1.6 小时；agent 完成率随任务变长急剧下降，>163 分钟任务归零；"current agents are still far from professional-level computer use"，最佳的 Claude Opus 4.8（max thinking）仅完成 20.6%、GPT-5.5 约 14%（[OSWorld 2.0, 2026-07 检索](https://osworld-v2.xlang.ai/)） | 高 |
| Benchmark 高估生产就绪度 | OSWorld-Verified 上短、窄、1–2 应用的自足任务可达 80%+，"高准确率因此高估了真实进展"；失败模式为丢失约束、错过中途信息、猜而不问、跳过验证（[OSWorld 2.0, 2026-07 检索](https://osworld-v2.xlang.ai/)） | 高 |
| 效率/延迟 | 端到端数十分钟 vs 人类几分钟；步数 2.7–4.3×；后续步骤慢 3×（[OSWorld-Human, 2026-07 检索](https://arxiv.org/abs/2506.16042)） | 高 |
| 成本可预测性 | scaffold 造成 9× 成本差、per-token≠per-dollar、价格 3 月跌 80%（[[Papers/2510-HAL]], arXiv 2510.11977） | 中-高 |
| 安全/不可逆动作 | 审计发现 web agent 用错误信用卡下单等 catastrophic action；defense 研究显著落后于 attack（[[Papers/2510-HAL]]；[[Papers/2508-OSAgentsSurvey]]） | 高 |
| 动作可逆性建模 | 真实 web 存在不可逆 destructive action，主流 tree-search agent 却假设动作可逆；可逆性需靠启发式猜（预标记仅约 37% 被确认）（[[Papers/2512-WebOperator]], arXiv 2512.12692） | 中-高 |
| 治理/审计合规 | EU AI Act 高风险日志义务 2026-08-02 可执法；委托链使问责分散，多数部署既无 hard/soft gate 记录也无签名审计（二手，[Zylos, 2026-07 检索](https://zylos.ai/research/2026-05-01-ai-agent-governance-compliance-2026/)） | 中-高 |
| 商业价值/ROI | 40% 项目预计 2027 前取消；95% 试点无 P&L 影响；仅 6% 企业为 AI 高绩效者（[Gartner, 2026-07 检索](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027)；[McKinsey, 2026-07 检索](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)） | 中-高 |

**（3）能力弧线与厂商姿态。** computer-use 能力的进步是真实且快速的：Anthropic 于 2024-10-22 首发通用 computer use（public beta），自陈"仍属实验性——时而笨拙、易出错"，Claude 3.5 Sonnet 在 OSWorld screenshot-only 仅 14.9%、放宽步数 22.0%（[Anthropic, 2024-10-22, 2026-07 检索](https://www.anthropic.com/news/3-5-models-and-computer-use)）；到 2025 年底，Claude Sonnet 4.5 报 61.4%、Claude Opus 4.5 系统卡报约 66% OSWorld（[Anthropic Sonnet 4.6, 2026-07 检索](https://www.anthropic.com/news/claude-sonnet-4-6)；[Claude Opus 4.5 System Card, 2026-07 检索](https://www.anthropic.com/claude-opus-4-5-system-card)）。但产品生命周期短暂本身就是不成熟信号：OpenAI Operator 从发布到关停仅约 7 个月（2025-01→2025-08，并入 ChatGPT agent），说明形态与商业模式仍在剧烈迭代（[OpenAI Operator 维基, 2026-07 检索](https://en.wikipedia.org/wiki/OpenAI_Operator)）。

**（4）成熟化路径（产业共识）。** 跨来源反复出现的判断是：瓶颈主要在管理与工作流而非模型能力。Gartner 建议只在有清晰 ROI 处推进 agentic AI、并主张"从头重构工作流"而非嵌入遗留系统（[Gartner, 2026-07 检索](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027)）；MIT 报告称成功的 5% "为摩擦而设计"——深度嵌入高价值工作流、配备 memory 与学习闭环，且内外部专家混编团队成功率 67% 远高于纯 IT 自建的 22%（[Legal.io 转载, 2026-07 检索](https://www.legal.io/blog/5719519/MIT-Report-Finds-95-of-AI-Pilots-Fail-to-Deliver-ROI-Exposing-GenAI-Divide)）；McKinsey 亦发现高绩效者更可能"从根本重设工作流"（[McKinsey, 2026-07 检索](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)）。本文综合判断：computer-use agent 距离"professional-level、长程、跨应用"的生产可靠性仍有实质差距，短期最可落地的形态是"窄范围、高价值、人在环、带审计与成本护栏"的工作流，而非通用自主 agent。

