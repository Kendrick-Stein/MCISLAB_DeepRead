---
title: "Agent-Friendly 浏览器交互接口规则：有证据的、只是惯例的、以及被证伪的"
date: 2026-07-27
tags: [report, web-agent, agent-interface, browser-protocol, action-space, grounding, prompt-injection]
related:
  - "[[Reports/2026-07-27-WebAgent-RL-and-Context-Landscape]]"
  - "[[Topics/CUA-Survey]]"
---

# Agent-Friendly 浏览器交互接口规则

只有九条浏览器交互规则拿到了受控实验支撑，它们全部落在 harness 侧；被引用最广的那条"用元素编号而不是像素坐标"在有同条件对照的地方被证伪，而所有要求站点改造的协议方案迄今没有一条在提案者不控制的真实站点上被验证过。

---

## 0. 证据口径

全文按四档标注 grounding，分档依据是对照设计而非结论强度：

| 档 | 含义 |
|:---|:-----|
| **跨底座受控** | 同 harness、同任务集，只改一个变量，且在 ≥2 个 backbone 上同向 |
| **受控消融** | 同 harness、同任务集，只改一个变量，单 backbone |
| **单点/方向性** | 单一切分、自建 benchmark、或 backbone 与对照臂不匹配 |
| **无证据** | 论文只有设计论证、案例演示或部署建议，没有任何量化对照 |

所有数值均为**作者自报**，未独立复现。凡注明"已核原文"的条目，指其数字与边界条件回到 arXiv/仓库一手材料逐条对过；其余为摘要级核对。**"未检索到"不等于"无人研究"**——第 5 节列出的空白只表示在本轮覆盖的文献与协议文档中没有找到测量，不构成不存在的断言。

---

## 1. 规则表

### A 档：有受控证据，可以当规则写

| # | 规则 | 谁强制 | 证据强度 | 不遵守会怎样失败 |
|:--|:-----|:-------|:---------|:-----------------|
| R1 | 动作空间先删后加：删掉需要具身知识或语义可被替代的原语（hover / press / tab_focus / go_forward / goto） | harness | 跨底座受控 | 模型在语义等价的动作之间反复摇摆；scroll 未禁时陷入 looping |
| R2 | 观察里的元素顺序必须确定，且与空间局部性一致；SoM 标号同步重排 | harness | 受控消融（内容严格不变的置换） | 顺序打乱掉分与删掉全部可交互元素文本同量级 |
| R3 | 观察必须是被裁剪过的短候选集；动作只能引用本步候选集里的 ID，由 harness 把 ID 解析成真实句柄 | harness | 受控消融 | 整棵 DOM 平均 2,473 节点而单页动作中位数只有 6，模型在噪声里选错 |
| R4 | 不要让语言头直接吐像素坐标 | 模型训练方 **或** harness（两种处方互不兼容） | 跨底座受控（仅否定形式成立） | 通用 VLM 的显式坐标 grounding 塌到个位数，尽管其隐式定位能力远高于此 |
| R5 | 动作执行后必须对照预先声明的期望做三值判定（Success / NoChange / Fail），不能假设"下发即执行" | harness | 受控消融 | 把失败的点击当成功继续往下走，并过早宣称任务完成 |
| R6 | 跨步状态（plan、约束、最近观察与动作）必须每一步重新出现在窗口里 | harness | 跨底座受控 | 动作重复、重复提交、遗忘约束 |
| R7 | 不可信内容在渲染进 agent 上下文之前做结构性隔离，而不是靠检测或提示词防御 | harness（+ 信任边界标注） | 受控消融（单模型单站点） | 提示词级防御无效：恶意弹窗测试里最鲁棒的模型仍有 86.6% 的任务点了诱饵 |
| R8 | 页面内暴露的工具面必须绑定 origin 且 tool_id 不可变，注册后不可被第三方脚本改写或注销 | 浏览器厂商 / 规范层 | 受控消融（跨 6 个模型世代） | 第三方脚本抢注同名工具，agent 调用后凭据与数据直接外泄，ASR 100% |
| R9 | 动作签名必须携带副作用类型，WRITE 在重试与重放中必须恰好一次 | 站点 / 服务端（+ harness） | 受控消融 | 重试导致重复下单、重复提交；无幂等键时无法安全回滚 |

### B 档：单点或方向性证据，能用但不是定律

| # | 规则 | 谁强制 | 证据强度 | 已知的反例或代价 |
|:--|:-----|:-------|:---------|:-----------------|
| R10 | 优先给高层类型化动作，原语作为兜底；工具通过测试输入后才注册 | 站点 / harness | 方向性（三底座开关，但对照臂不匹配） | 原语仍被大量使用；并列设计引入新的决策负担 |
| R11 | 批量多动作必须在每个动作前用可信系统 API 重新校验前置条件 | harness | 单点（桌面侧） | 回滚代价从未被测量：无 undo、无早停频率、无副作用报告 |
| R12 | 观察按语义分区并给摘要，而不是扁平整棵树 | harness | 单点，且有净负反例 | 一篇诚实报告净负；两篇报告降 token 同时涨分；机制解释互相矛盾 |
| R13 | 削减的收益随主模型能力单调衰减——强模型少削，弱模型多削 | harness | 三条独立路径同向 | 削减本身可能比不削减更慢；相对 SR 代价 11%–16% |
| R14 | 削减器可以复用为注入过滤器 | harness | 单点，效应量大 | popup ASR 90.4%/81.6% → 1.0%/0.9%，无攻击时不掉分 |
| R15 | 异常清单必须被接口显式覆盖并可注入测试（传输 / HTTP 状态 / 资源 / 覆盖层 / 布局 / DOM / 执行 / 语义 / 工具层 / 自报层） | harness + benchmark | 两篇实证，严重度排序不一致 | 提示词约定不可移植：同一条 refresh 提示救回一个 benchmark 却让另一个更糟 |

### C 档：行业惯例，没有任何测量

| # | 规则 | 现状 |
|:--|:-----|:-----|
| R16 | 动作后等多久再重新观察 | 无人测过；实践是固定 sleep（10 s 量级）。已被观测到的后果是 capture race |
| R17 | 接口主动返回动作结果 | 无人提出。Playwright 已抛类型化异常，但只被当作离线错误分析，且明确排除网络失败与超时 |
| R18 | 域名白名单 | 只有一句部署建议，零测量；且它是"站主诚实"的前提条件，不是防注入手段 |
| R19 | 敏感动作二次确认 | 只在别人的工作里被引用一句，提出方自己没实现也没测 |
| R20 | 元素 ID 跨步稳定 | 唯一有量化增益的方案直接绕过（ID 只在本步有效），并把无法分配 ID 的元素从数据里删掉 |
| R21 | 虚拟滚动 / 懒加载 / shadow DOM / iframe 下四种寻址方案的失效率 | 六篇寻址论文零实验 |
| R22 | 站点侧权限清单（Permission Manifests） | 零实验，且与 R7/R8 冲突——它把站点自撰的自然语言送进 agent 的推理循环 |

---

## 2. A 档规则的证据与边界

### R1 动作空间：删比加重要，但这条常被引错

AgentOccam 是唯一提供跨底座受控增量的工作。WebArena 全量 812 任务上，Vanilla 16.5 → 删动作 25.9（+9.4）→ 禁滚动改喂整页 31.7（+5.8）→ 观察格式压缩 37.1（+5.4）→ 历史筛选 38.2（+1.1）→ 加规划 43.1（+4.9）。删掉的是 hover、press、tab_focus、go_forward、goto 这类要么需要具身知识、要么语义上可被别的动作替代的原语。在 190 任务的 dev 子集上，GPT-4-Turbo 与 Gemini-1.5-Flash 两个底座的 ↓Actions 增益**恰好都是 +11.6**，这是全表最可复现的一格。

这条规则被广泛引作"观察削减有效"的证据，是误引，而且被论文自己的表直接否定：完整版每步观察 token 2,930.9，比 Vanilla 的 2,210.2 **高 32.6%**；唯一一次 token 下降（2,210.2→1,652.0）来自动作裁剪而非观察处理，随后禁滚动把它推到 3,376.2，观察压缩只是部分偿还方法自己制造的膨胀。作为"削减"的两个观察组件里，History 只有 +1.1，在 n=812 上的非配对差值标准误约 2.3pp，落在噪声内，论文并明确记录它使 shopping −3.2、Reddit −6.0。

能站得住的只有序数结论：**单一最大组件是纯动作裁剪，且它本身大于两个无争议观察组件之和（5.4+1.1=6.5）**。精确配比不成立——消融严格累积、只有一个顺序、无 leave-one-out、无 seed、无误差棒，且分桶敏感：branch/prune 虽以动作实现但机制是裁剪 context，若整体划归观察侧配比从 76%/24% 变成 57%/43%，把禁滚动也划过去则翻转为 35%/65%。可承受的区间是 57%–76%。（已核原文；[[Papers/2410-AgentOccam]] 第 42 行的图读中间值 26.1/26.5/28.6/31.8 全部错误，权威数据在附录 Table 17，实际为 25.9/31.7/37.1/38.2。）

### R2 元素顺序：内容不变，只改排列就能腰斩成功率

这是全表设计最干净的一次受控实验——同一元素集合做置换，图上的 Set-of-Mark 标号同步重排，信息内容严格不变。GPT-4V 从 74.07 掉到 44.44，Gemini-1.5 从 64.03 掉到 37.04。同一张表里，同时删掉可交互元素文本与静态文本得 35.18，所以打乱顺序的破坏力与删掉全部可见文本处在同一量级。

但"顺序比内容更重要"这个流传更广的强版本不成立：删掉**整个**文本表示是 3.70，比打乱严重一个量级。成立的是"在同粒度的单个属性里，序是最贵的那个"。排序方案有实测差异——有 DOM 时用前序遍历；强模型配难任务时用 (x,y) 坐标的 t-SNE 一维投影；元素稀少时 raster（y 按 8 px 分箱后再按 x）最好。元素数越多，顺序的影响越大。

两个必须带上的边界：被打乱的是文本 observation 里的元素列表，视觉侧只是标号跟着重排，**纯图像表示下顺序是否还重要，作者明说没做**；该文正文 Table 4 与附录 Table 12/Table 2 对 GPT-4V 的 Random/Raster 数字互相矛盾（37.04/53.70 vs 44.44/44.44），GPT-4V 那一列应当降权。同一篇还给出一条被低估的结论：截图加 SoM 在桌面与网页上不能替代文本表示，Gemini-1.5 在纯视觉下掉到 3.70%——这与手机端得出的相反结论直接冲突。

### R3 短候选集 + 本步 ID：46.80% → 88.28%

Prune4Web 的动作空间只接受本步 top-20 候选里的整数 element_id，引擎通过 DOM 哈希表把它解析成 XPath/CSS 并以 dispatchEvent 兜底，其余一律判为 invalid action。成功率 46.80%→88.28%，oracle 上限 90.28%，即裁剪本身几乎吃掉了全部可得增益。裁剪的必要性有两处独立测量支撑：页面平均 2,473 个 DOM 节点而单页动作数中位数只有 6、90 分位 13；UI 表示占 prompt 总 token 的 79.8%–99.0%（Mind2Web 上 51,648/52,146）。

它证明的是**候选集必须短**，不是 ID 寻址优于坐标寻址——后者是一个未被该论文测量的附加断言（见第 3 节）。而且增益随底座能力单调衰减：GPT-4o 42.1→42.1 完全无增益，GPT-4o-mini 26.3→31.6，Qwen2.5VL-3B 0.0→5.2。它的定性失效清单同样有信息量：没有 tag/role 的 `<div>` 假按钮、没有 text/aria-label 的纯图标元素、source 与 render 不一致；最长 10,000 px 的截图按 1080 px 切片，无目标的切片一律标 SCROLL。

### R4 坐标不该从语言头出来——两种处方互不兼容

只有否定形式被确立。GUI-Actor 换掉架构与训练目标，同底座下 ScreenSpot-Pro 40.7 vs 点监督 15.6 vs 框监督 13.8，在线 OSWorld-W 12.2% vs 4.0%。2509.11548 什么都不改，只往输入图像上叠坐标网格，Gemini-3.1-Pro 在 ScreenSpot-v2 上 11.72→95.20，Web 子域 4.26→93.59。两条路径的效应量都很大，处方却完全对立：一个要求重训模型，一个要求改 harness 的图像预处理。

后者的机制诊断解释了为什么效应量能这么夸张：Gemma-3-12B 的 Pointing Game 隐式定位能力已有 47.56，而显式坐标输出只有 9.59——脚手架修的是**输出格式失配**，不是空间理解。这也解释了它的三条边界：对已经过 grounding 微调的 Qwen2-VL-7B 反而掉点（47.56→28.38）；高分辨率下仍崩（ScreenSpot-Pro 最好 47.80）；代价是两次模型调用，每样本 27.00 s vs 直推 7.18 s。它只做单步 grounding，没有任何多步端到端证据。

### R5 动作结果必须被判定，而不是被假设

当前接口的默认语义是"下发即执行"，这个假设本身是失败源。显式重新推断动作结果把 zero-shot 成功率从 28.1% 提到 45.9%，同时把过早停止从 68.9% 压到 16.3%。另一条独立消融显示去掉前置/后置条件检查后 SR 从 84.0 掉到 72.0、从 80.0 掉到 70.0。

规则的可执行形式是：动作发出前声明期望的页面变化，动作后把实际观察与期望比对，判定为 Success / NoChange / Fail 三值之一，NoChange 与 Fail 走不同的恢复路径。天花板要说清楚——模型自我推断在难例上只有 61.3%，能准确描述"错在哪"的只有 25.9%，所以这条规则的正确落点是 harness 提供比对，而不是让模型自己反省。

### R6 跨步状态每步重发——但重发 plan 本身不够

注入 agent 上下文的 plan 信号在**一个动作-观察周期内**衰减 4.1×（ALFWorld 0.453→0.110，HotpotQA 12.4×），被驱逐后成功率从 56.7% 掉到 22.0%。独立的一条线得到同向结论：没有历史会导致动作重复，加 4–9 步历史几乎对所有模型有益（最高 +10.9pp），且以 diff 形式承载只花约 1/3 的 token。

这里有一条重要的负结果，它把规则的边界划死了：**只把 plan 精准重注回去不够**。probe 门控每 run 平均 6.1 次在 plan 信号衰减时重注，成功率 24.7% vs naive 22.0%（p=0.67），离未压缩的 56.7% 差得很远；作者的诊断是被压缩删掉的其实是最近的观察和动作，"plan-protection alone is not a compression fix"。方法本身还有硬约束——它要求白盒隐状态、可逐 token 确定性回放的轨迹、以及一段可整体删除的注入 span；网页观察不满足最后一条，因为页面每步都在变，无法"回放同一 observation 但抽掉页面表示"。能搬过来的是跨步稳定的注入物：系统提示、约束、tool schema、摘要块。时序形状也不普适——同族的 Qwen3-32B-native 呈持续漂移而非 spike-then-decay，二值 AUROC 只有 0.616。

### R7 不可信内容做结构性隔离，不是检测

UCM 的做法是把不可信 DOM 区域在渲染前替换成带 ID 的占位符，agent 只能通过一个隔离模型以 (占位符 ID, 问题, 返回类型) 三元组去读，返回类型限定在 bool / int / float / enum / date，每元素 ≤5 次查询、enum ≤10 个选项；需要自由文本时必须逐项人工批准。在 strengthened WASP 上 ASR 0±0%，对照无防御 17±8%、WASP 提示词防御 8±8%（后两者作者自称是下界）。效用代价 1.05×–1.84×，信任边界自动推断 F1 0.840–0.997，每站 15–30 条 CSS selector 就够。

对照面上，提示词级防御的失败是压倒性的：在恶意弹窗测试里最鲁棒的模型仍有 86.6% 的任务点了诱饵，GPT-4o 97.3%、GPT-OSS 98.2%。这是"结构性隔离而非内容检测"这条规则的主要论据。

边界比结论窄得多，必须逐条写死（已核原文）：安全数字只有一处——Claude Sonnet 4 + GitLab WebArena + 12 个攻击目标；正文明写"we do not seed webpages with prompt injection attacks"，10 个自建站点、3 个模型的实验只测效用与成本，不测 ASR。**单个元素误标就把 ASR 从 0 拉回 6±5%**，即保证不是退化而是消失，退回启发式防御档位。威胁模型排除恶意站主、XSS/active-content 导致的 DOM 逃逸、可用性攻击、浏览器/OS 失陷；保护对象只是 control flow——作者自己红队给出成功的 data-flow 攻击（selection hijacking、单值篡改），攻击者仍能让 agent 在"合法"动作上作用于错误对象。4 个 GitLab 模板在类型化通道下不可解（需要自由文本的姓名/邮箱/文件内容），恢复功能要靠人工批准，此时安全性转嫁给人类判断。保证的性质是架构不变式而非形式化证明——全文无定理、无证明。

未被隔离掉的一条通道：语义 UI 图标注入。攻击用的是内容无害、能通过过滤、且受 IoU 约束不遮挡原控件的**合法图标**，Claude-Sonnet-4.6 攻击成功率 22.24% vs 随机基线 3.23%，GUI-Owl-7B 与 OpenCUA-7B 达 50%–52%；L1/L2 分层是决定性的（随机注入 L2 0.45%–0.75% vs 策略注入 15.95%–22.73%），且跨架构迁移。该文提出的防御是未实现、未评测的收尾段。它的证据边界也要带上：885 个样本是从公开 grounding 数据集筛出的静态截图，图标离线合成到图像上，是单步 grounding 攻击而非活体端到端任务。

### R8 页面内工具面必须绑 origin——模型升级对此完全无效

WebMCP 把工具面放进页面 JS 之后，页面内容的可信度问题变成了工具元数据的可信度问题，而元数据被 agent 更直接地信任。注册竞态在三个 SOTA 模型上 ASR 100% 且 100% 数据外泄；description 投毒 93%、readOnlyHint 投毒 87%、两者合用 100%、中性对照 0%。AbortSignal 劫持只在 agent 循环开始前（P1）有效，P2/P3/P4 全部 0%。

这一簇里最有信息量的一格是：**从 GPT-4o / Claude 3.5 换到 GPT-5.4 / Opus 4.6 / Gemini 2.5，ASR 变化 0%**。协议层的洞不会因为模型变强而收窄，这直接决定了它必须在浏览器/规范层修，而不是靠模型对齐。两个已实现的防御（origin 绑定的不可变 tool_id、数据流限制）把 36%–100% 的 ASR 全部打到 0%。实验跑在 Node.js ProxyClient 而非原生浏览器，这是它的主要外推限制。

### R9 副作用类型与 exactly-once——一个系统性空洞

唯一有消融的是 ToolPro：关掉 effect 标注后 17.92 s → 21.45 s（+19.7%），强制回退从 0/15 变成 3/15。可执行的规则形式是：动作签名声明 READ / WRITE；重放时若某次修复改变了已提交 WRITE 前缀的参数或顺序，则禁止重放；端点没有幂等键且行为非确定时 fail closed。

真正值得记住的不是这个效应量，而是它周围的空白。同簇其余六篇动作空间论文没有任何一篇做副作用类型标注或 exactly-once 保证。页面内标注方案里，只有 web verbs 提出了 preconditions / postconditions / policy tags / permission manifests，而它是撤掉了 v1 量化结果的纯立场文；webMCP 只有 HTTP 语义层面的 `action.kind`；VOIX 只有一个表示"会有返回"的 `return` 属性，没有任何幂等性或破坏性标记。**副作用是整个 agent-friendly 接口谱系里最一致的缺失项。**

这条规则还揭示了一个方向性冲突：一旦你要 exactly-once 的写语义和沙箱隔离，纯 agent 侧自足就不够了。反推出来的接口（从流量学到的 shadow API、从无障碍树反推的导航面）只能安全地承担读，写操作的正确性需要被调用方参与。

---

## 3. 被广泛相信但站不住的四条

### 3.1 "带编号的元素索引比像素坐标更可靠"——证伪

同条件对照是存在的，结论与该信念相反或至少不支持它。

最干净的一次：MAG 在同一 harness、同一 WebArena 六站点、同一 174 任务 test split 上只切换 grounding 方案，其余 pipeline 完全一致。GPT-5.5 坐标 .374 vs SoM .356（p=0.69）；Claude Sonnet 4.6 坐标 .270 vs SoM .276（p=1.0）；Gemini 3.5 Flash SoM .345 vs 坐标 .207（+13.8，p<0.001）；Qwen3.5-9B 经 GRPO 后 SoM .132 vs 坐标 .081。论文原文写的是 grounding preference is model specific，必须逐模型测。同 planner 换臂的对照给出同样结论：Multimodal-Mind2Web 上 GPT-4 + HTML 候选选择 42.3 vs 纯截图坐标 44.8；AndroidControl 上 a11y 树选择 42.1/55.0 vs 坐标 46.2/58.0；AndroidWorld 上文本选择 30.6、SoM 25.4、坐标 31.0–32.8。再一例：AITW 上 GPT-4o 配坐标式 intent grounding 48.9% vs 配 SoM 42.1%。

这个信念的历史来源确实存在，但边界很窄。SeeAct 在 GPT-4V 上测出 DOM 文本候选选择 39.1/32.7/42.0 远高于截图叠编号框的 SoM 20.3/13.9/23.7，并给了错误分解（54% 凭空捏造 label、46% box-label 错配）。注意**被打败的是"截图上的编号"，胜出的是"DOM 文本候选"，而对照组里根本没有坐标臂**——2024 年初的 GPT-4V 不能可靠吐坐标。把它外推成"索引 > 坐标"是跨了对照组。

仍然成立的窄条件有三条，且都要写死：Gemini 3.5 Flash 在 WebArena 六站点上 SoM 显著优于坐标；小模型 RL 只有在 SoM 动作空间下 GRPO 才能涨（Qwen3.5-9B 6.9%→13.2%，p=0.035；坐标空间 p≥0.63）；2024 年初没有专用 grounder 的通用 VLM 上，DOM 文本候选优于当时可用的替代方案。反向的窄条件是：坐标臂的优势普遍依赖专门训练过的 grounding 模型或 2026 年的 frontier 模型。

坐标寻址同样**不是**避风港：在结构通道被污染时，坐标 agent 仍会对只存在于结构里的注入节点动手，比例 0.84–1.00。

### 3.2 "SoM 类视觉标注能可靠提升网页 grounding"——证伪

被引原文根本没测网页。全文检索不到 GUI / web page / browser，量化实验只有 COCO（100 图/567 实例）、ADE20K、Flickr30K、RefCOCO/RefCOCOg、DAVIS，唯一的 navigation 是室内平面图；GUI 内容全部是附录里的定性 case study。标记区域由 SAM/SEEM/MaskDINO 这类通用分割器产生，不是由 DOM 元素边界产生。SoM 成为 web agent 事实标准，是下游工作追认的结果。

作者自己写下的两条失效条件恰好正对网页：满屏数字的图会干扰数字标记，"document screenshots need non-alphabetic marks"，而动态选择标记类型这件事在文中并未实现；小区域会被 mark 本身盖住。移动端的独立测量给出同向结果：SoM 无收益，小模型上 10.63% 反不如原图 + a11y 拼接的 15.94%。

标记该长什么样本身还有一处未被裁决的分歧：SoM 主张字母数字符号"可以被读出来"，而 2509.11548 的 anchor 消融在同一底座上发现真实数字坐标胜过符号索引（Scaffold Prompting 50.8 vs Mark-Grid 95.2）。

### 3.3 "结构化通道（DOM / AXTree）的值可以直接信"——证伪，且这是最危险的一条

模型把截图读对了（Acc_img 0.85–0.93），但当结构与像素的值冲突时，它把信念交给结构（pfg 0.30–0.75）。在 38 个真实站点上，零编辑的陈旧快照最高有 0.88 的比例被当作现状跟随；114 个经人工确认已滚出屏幕的移动端元素，仍被报告为可见，比例 0.75–0.99。

动作格式扫描给出了直接的操作性后果——**在结构通道里点名动作会大幅放大这个问题**：同一模型下，坐标 0.11 → element id 0.64 → index 0.90 → text label 0.98。也就是说，R3 那条"只引用候选集 ID"的规则在安全维度上是有代价的，两条规则之间存在真实张力。

后果是不可恢复的：≥2 步的 episode 上，一次错误信念给出 0.97–1.00 的最终失败率，自恢复概率 ≤0.03。可行的缓解是来源感知的一致性门，代价是每步多 1.8–2.0 次查询，密集移动端屏幕上 3.3–5.5 次。（跨底座受控。）

### 3.4 "非 HTML 暴露（MCP / NLWeb / RAG）在效果与成本上都优于读 HTML"——证伪

这是一条"效果 AND 成本"的合取式断言，效果那一半在原文自己的表里就被推翻。Vague Product Search 上 HTML 0.63 > RAG 0.61、MCP 0.59，只输给 NLWeb 0.66；Cheapest Product Search 上 HTML 0.61 > NLWeb 0.60；Sonnet 4 在 vague 上 HTML 0.60 同时击败 RAG 0.41 / MCP 0.53 / NLWeb 0.55。摘要那句 9 分平均差几乎全部由 Specific Product Search 与 Action&Transaction 两类贡献，聚合掩盖了反转。

对照本身也被混淆：三个非 HTML agent 由作者自建，具备 multi-query 与 self-evaluation & iteration，且共用同一套 OpenAI embedding + Elasticsearch 后端；HTML 臂用的是现成 baseline，只能用店内关键词搜索框。三个非 HTML 架构彼此只差 0.02 F1，说明真正的自变量是**有没有语义索引与跨店聚合**，不是暴露协议。此外任务集有未披露删减——两次声称使用全部 91 个任务，四类计数 23+19+26+15 = 83，恰好整类漏掉 End-to-End 的 8 题，而那正是 HTML 端在同基准新版上拿到 75% CR / 84.26 F1 的那一类。成本口径上，论文自陈不用 prompt caching，而 HTML 恰恰是长前缀、input-skewed 的负载，是 prompt caching 收益最大的形态；token 比值（225k vs 47k–122k，约 3×）方向可信、机制清楚，美元比值不可用。

能存活的窄化版本是：在离线、静态、schema.org 干净、可被完整爬取的多店商品目录上，对意图明确的检索与加购/结账任务，语义检索接口比通用浏览 agent 逐页读 AXTree 更准（+13~15 F1）且省约 3 倍 token；对开放式与带价格约束的任务没有效果优势，部分配置下更差。（已核原文。）

同一支上还有两条被证伪的强断言，一并记录：**"agent 不需要站点配合，从流量里学 shadow API 即可"**——该文声称基线是 CSS selector 定向抽取"not raw DOM dump"，但作者自己发布的 benchmark 脚本里 Playwright 路径是 `goto` → `wait_for_timeout(2000)` → `inner_text("body")`，既没有任何 selector，又硬插了 2,000 ms 无条件 sleep；扣掉这 2 秒重算，均值加速 3.58×→1.49×、中位 5.35×→1.97×，21/94 个域名反而更慢，"94/94 全胜"随之崩掉；全文无任何 task success rate，而作者自家 README 写着 "Playwright has 100% success as a brute-force baseline"、"47% of Unbrowse 'failures' were disambiguation issues"。**"声明式页面内标注是可行的落地形态"**——该文测的是开发者人机工效：3 天线下 hackathon、16 人 6 队、作者全程在场指导并设奖金，量化指标只有 SUS 72.34 与 TOAST 主观量表，没有任何 agent 任务成功率；6 个应用全是现场从零写的 demo；唯一的 agent 侧硬数据是附录延迟表，n=1、跨模型混淆（一臂 Qwen3-235B、一臂 GPT-5-mini、一臂商业黑箱）、只报延迟不报语义正确性、成功与否由作者非盲目视确认。（均已核原文。）

---

## 4. 未被裁决的分歧

以下七处是真实的技术冲突，各方都有论据，且**没有一处做过交叉实验**——它们是接口设计里当前最值得下注的位置。

| 分歧 | 一方 | 另一方 | 为什么没法裁决 |
|:-----|:-----|:-------|:---------------|
| 动作是否绑定确定性实现 | ActionEngine / WALT / Web Verbs：绑到 Playwright selector、元素哈希 + URL 参数、类型化签名，并提议 `stable-public-locator` HTML 属性，理由是可靠与可审计 | AgentProg：步骤故意留在自然语言以求"语义容错"，举 AutoDroid-V2（AndroidWorld 26.0）当反例 | 不同平台、不同 benchmark；AgentProg 从未消融自己的 DSL |
| 分区边界该学还是该用规则 | WebChallenger：纯规则——递归下降 DOM，命中 tag 集合 / 包围盒阈值 / list section 即终止，≥4 个同 tag+class 兄弟无条件合成 | Region4Web：明确否定规则路线（"what each region is for varies with the page even for structurally repeated patterns"），训 536K 参数 EdgeClassifier 逐边判 merge/cut | 隔一个月出现在 arXiv，互不引用，各自的对照臂都不是对方 |
| 截图里什么是冗余 | AQuaUI：删掉约 30% visual token（Web Text 子集 −1.28 pt，Mobile Text −14.48 pt） | 2509.11548：补与页面内容无关的坐标网格 | 方向相反；AQuaUI 损失最集中的正是细粒度文本目标 |
| 结构在推理时构造还是训练时蒸馏 | MolmoWeb：纯 viewport 截图，不碰 HTML/AXTree，把 grounding 训进权重，WebVoyager 78.2% | SoM Agent 同表 o3 79.3、GPT-5 90.6 全面在其之上；Online-Mind2Web 35.3 vs 57.7 | 无人做过同 backbone 的 SoM vs no-SoM 消融；MolmoWeb 的 AxTree teacher（85.6%）还高于自家学生 |
| 取回正确内容是否足够 | STITCH：按意图检索能挽回长程退化（Large 子集 Prec 0.616 vs 最强基线 0.282） | Plans Don't Persist：精准重注 plan 不够（24.7% vs 22.0%，p=0.67，未压缩 56.7%） | 设定不同（4,096 token 检索预算的合成长程 QA vs keep_recent=4 的 20 步 ALFWorld），但对同一问题给出相反的经验答案 |
| 异常的严重度排序 | WAREX | StressWeb | 两篇的排序不一致，无人调和；且 WAREX 自己的 refresh 提示词把一个 benchmark 救回 −2%，却让另一个从 −73% 恶化到 −79% |
| 拓扑图 vs 世界模型 | WebNavigator 等：检索已探索的页面转移图 | WMA / DynaWeb：把下一页生成能力放进模型 | 无同条件对拍；WebNavigator 抄了 WMA 的 16.6% 当基线但预算不同（max 5 actions vs max 20 steps）。唯一硬对照是 WMA vs Tree search：16.6% vs 19.2%，但 \$0.4 vs \$2.7、140.3 s vs 748.3 s——模拟换来的是成本而非精度 |

第 12 条规则（语义分区）之所以只能进 B 档，是因为它内部就有冲突数字：LineRetriever 诚实报告净负（WorkArena L1 52.7→48.2/44.8，WebArena 32.3→24.9，保结构版 30.2 仍低于什么都不做的 32.3），而 Region4Web（−43% token、+2.3%p SR）与 UIFormer（Mind2Web −88% token、Step SR 41.23→53.71）报告降 token 同时涨分。一个自然的调和是"保不保留层级"——LineRetriever 恰好提出裁剪后的 AXTree 落到模型分布外、恢复结构救回 5 个点；但 UIFormer 的排序消融在同一批已优化的树上得到 Random 43.20 / 扁平 DFS 44.00 / 保层级 44.40，只差 1.2 点，直接掐掉了这个解释。簇内的机制解释与簇内的实验互相矛盾，无人处理。

---

## 5. 完全没有测量的空白

这五处是接口规范里最该被填、却连一个数字都拿不到的地方。

**动作后的等待时机。** 没有任何工作测过"动作发出后等多久再重新观察"，实践是固定 sleep（10 s 量级）。已被观测到的后果是 capture race——DOM 先被抓取、页面随后更新、截图最后拍，三者对应不同时刻的页面状态，而模型无从知道。

**接口主动返回动作结果。** 没有任何工作提出这件事。BrowserGym/Playwright 已经抛出类型化异常（Not Found、Wrong Type、Option Not Found、Intercepted、Invalid URL），但唯一使用它们的工作只把它们当离线错误分析素材，并且**明确排除了网络失败与超时**——恰恰是最值得返回给 agent 的两类。

**元素 ID 的跨步稳定性。** 唯一有量化增益的方案直接绕开了这个问题（ID 只在本步有效），并把无法分配 ID/XPath 的 ground-truth 元素从数据里删掉，即问题被排除出评测而非被解决。工程侧有精确的失效描述——批量动作在 type 触发 DOM 变化后不重新快照、selector_map 陈旧导致点错元素——但只是单例 bug report，没有频率。

**四种寻址方案在动态页面下的失效率。** 滚动、虚拟列表、懒加载、shadow DOM、iframe 下的像素坐标 / SoM 编号 / AXTree-DOM element ID / CSS selector-XPath 四条路线，六篇寻址论文零实验。所有对照都在静态或半静态页面快照下进行（离线数据集、自托管站点、录制轨迹）。这一块是 convention，不是 evidence。

**标注覆盖率随时间的演化。** 所有站点侧标注方案论证的都是"标注若存在则有效"。而唯一有真实生态规模证据的一篇论证的是相反命题："标注在真实世界中大规模不存在"——59% 的屏幕存在无法匹配到任何无障碍元素的标注，94% 的 app 至少有一屏如此，而 WAI-ARIA 这类标准已推行二十年；其引用的 Interaction Proxies 与 Social Accessibility for the Web 都因需要持续志愿维护而未能规模化。两个命题可以同时为真，而没有任何一篇提供覆盖率随时间演化的证据。同样地，站点改版后拓扑图/shadow API 如何失效，全簇零测量——有的写了周期性校验与自动下线机制，但作者自承"尚未接入验证循环"。

---

## 6. 这些规则能落在什么协议上

规范层的现状比生态叙事悲观得多。

**W3C WebDriver BiDi 仍是 Working Draft**（TR 版 2026-06-29，ED 2026-07-20），**尚未进入 Candidate Recommendation**；CR 跟踪 issue 自 2025-04-14 打开至今未闭，卡在尚未撰写的隐私/安全考量以及待做的 a11y/i18n 横向评审。模块覆盖 session / browser / browsingContext / network / script / storage / log / input / emulation / webExtension。实现侧（browser-compat-data，2026-07-27）：Chrome 126 起大批落地，Firefox 从 92 到 126 渐进补齐，**Safari 全线 `version_added: false`**——唯一的相关线索是 locateNodes 挂着一个 WebKit bug 链接，未检索到 Apple 官方的支持声明或时间表。响应体读取（`network.addDataCollector` + `getData`）是 Chrome 140 partial / Firefox 143 / Safari 无。Edge 在 BCD 中一律是 `mirror`，是推定值不是实测。

**最关键的缺口：BiDi 没有 accessibility 模块。** 唯一相关的是 `browsingContext.locateNodes` 的 accessibility locator（按 role/name 定位节点，不是导出树），Firefox 自 127 支持。"Accessibility module in WebDriver BiDi?" 这个 issue 2023-06-06 开启、2025-12-12 最后更新、至今 open、无任何路线图。**2026 年 7 月想拿 AXTree，只能走 CDP。** 而 CDP 的 Accessibility 域**全域标记 EXPERIMENTAL**——`getFullAXTree` / `getPartialAXTree` / `queryAXTree` 等全部在内。也就是说，整个浏览器 agent 生态的"标准观察格式"建在一个实验性、非标准、单引擎的私有协议域上；Puppeteer 在 BiDi 模式下 accessibility 明确 unsupported，调用会抛 `UnsupportedOperation`。

这不是历史包袱，是当前选择：browser-use（106k star，依赖 `cdp-use`，依赖列表里**没有** playwright）、Stagehand（23.6k star）、chrome-devtools-mcp（Puppeteer → CDP）都在直接用 CDP；Playwright 仓库里有完整的 BiDi 后端，但只有 channel 以 `bidi-` 开头才路由过去，非默认、未作为正式文档特性，对应的功能请求 issue 已于 2024-12-06 关闭。

**a11y 文本快照 + 稳定引用 ID 已是事实上的观察格式，但没有跨栈标准。** Playwright 的 ARIA snapshot 是 YAML，节点语法 `- role "name" [attr=value]`，属性含 checked/disabled/expanded/invalid/level/pressed/selected；文档明确其值"derived from ARIA attributes or calculated based on HTML semantics"——它是浏览器原生 a11y 语义的**再计算与序列化**，不是原生 AXTree 的直接转储。playwright-mcp 在此之上加元素句柄 `[ref=e1]`，chrome-devtools-mcp 加 `uid`，**两家主力实现的格式与 ID 命名不兼容**，没有任何规范定义它。

动作原语本身已经高度收敛：navigate / click / type(fill) / hover / drag / select / upload / press_key / handle_dialog / wait_for / snapshot / screenshot / evaluate。playwright-mcp 69 个工具 10 组（v0.0.78，2026-07-09，35.5k star），chrome-devtools-mcp 52 个工具 10 类（v1.6.0，2026-07-14，47.7k star，官方只支持 Chrome / Chrome for Testing）。差异全在观察侧：前者偏 a11y 快照 + ref + 断言/存储/路由，后者偏 a11y 快照 + uid + trace/heap/network/Lighthouse。值得注意的是，R5（动作结果判定）在 playwright-mcp 里有对应工具面（`browser_verify_element_visible` / `browser_verify_text_visible` / `browser_verify_value`，需 `--caps=testing`），而 R9（副作用类型）在两家都完全没有对应物。

站点侧唯一真正的新东西是 **WebMCP**：Chrome 149（2026-06-02）起 origin trial，孵化于 W3C WebMachineLearning CG（非 Recommendation track），消费侧 chrome-devtools-mcp 已有 `list_webmcp_tools` / `execute_webmcp_tool`（需实验开关）。扩展 API 侧 2025–2026 的变更是常规演进，没有为扩展新增 AXTree 访问、动作原语或 agent 权限。

一个反向信号值得记下：Microsoft 在 playwright-mcp README 顶部主动把 coding agent 引导去 playwright-cli + SKILLS，理由是 MCP "avoid loading large tool schemas and verbose accessibility trees into the model context" 的成本。"MCP 是浏览器 agent 的默认接口"这一判断，在发布方自己那里已经出现松动。

---

## 7. 谁必须动：采纳负担与证据强度成反比

这是横跨全部材料的最强 pattern，也是判断任何一条接口提案成色的最好尺子：**要求越多外部协调的方案，越是以纯设计论证的形式存在。**

harness 层自足的方案（动作空间裁剪、DOM 剪枝、不可信内容遮蔽、观察格式对齐）都有受控消融，因为它们不需要任何人点头就能做实验。要求站点动的（Agent-Ready Websites、Permission Manifests、AWI、Agent-First Web）要么零评测，要么只在作者同时构造的两版原型上比——89.3% vs 49.3% 这个 40pp 的差距，基线把商品数据埋在 JS 里，逐特性消融被列为未来工作，成分归因未知。要求 OS 或应用动的（DMI 44.4%→74.1%，n=27）效应真实，但绑死在三个已适配的应用上，每应用约 1.5 人日人工建模、绑定具体版本、零 held-out application，非覆盖应用收益直接归零、退回 GUI 基线。要求标准组织动的只有 origin trial 和采纳顺序建议。**在提案者不控制的真实第三方站点上做过 agent-native 改造对照的，一篇也没有。**

三条从这里推出的判断：

**语义接口的收益与让渡的权限大体等价交换。** 走无障碍 API 的路线能力弱但普通权限即可；走 CLI/adb 的路线能力强，但代价是预 root 镜像、特权 shell、可直连后端数据库与容器的运维级通道——那不是"接口范式更优"，是"权限更大"。同一批实验里，控制模型后 GUI 反而更强（同一个 Opus 4.7 驱动 GUI 56.4 vs 驱动 CLI 51.9）。

**天花板由任务是否本质依赖像素决定，而非接口设计的精巧度。** CLI 路线的 oracle 上限是 88.8%/86.3%，剩下的十几个任务正是拍照、录音、手绘。语义接口的收益集中在信息提取、聚合、多约束筛选，在本质需要像素的任务上为零。

**工具发现的成本会吃掉大部分协议收益，而且随生态规模上升。** 唯一量化它的工作显示：给定 ground-truth 工具时相对浏览器平均 +13.79 分、成本降 54%；一旦改成从 18,000+ 工具里自己检索，净增益缩到 +5.39（约 61% 被吃掉），检索 recall 只有 32.8%–69.7%，GPT-5-mini 甚至跌破自己的浏览器基线（32.11 vs 33.36）。这把其余协议类实证工作的定位钉死了——它们的工具集都是几十量级且已给定，等价于 oracle 条件，与真实检索条件不可比。同一篇的真实企业环境（16,837 工具）根本没有浏览器对照，且复合任务全模型最高 1/7。

---

## 8. 如果现在要写一份 harness 规范

按"能不能落"排序，只列 A 档与代价已知的 B 档。

| 规则 | 落在哪一层 | 现在能落吗 |
|:-----|:-----------|:-----------|
| R1 动作空间裁剪 | harness 动作定义 | 能，零依赖 |
| R2 元素顺序确定且与空间局部性一致 | harness 观察序列化 | 能，零依赖 |
| R3 短候选集 + 本步 ID + harness 解析句柄 | harness 观察 + 动作校验 | 能；与 R7/§3.3 存在张力，需配来源感知一致性门 |
| R5 动作结果三值判定 | harness 执行层 | 能；playwright-mcp 的 testing 工具组可直接复用 |
| R6 跨步状态每步重发（diff 形式） | harness 上下文装配 | 能，零依赖；但不要指望只重发 plan |
| R13 按底座能力调削减强度 | harness 配置 | 能；先测本底座的 no-reduction 基线再决定削多少 |
| R14 削减器复用为注入过滤器 | harness 观察 | 能，效应量大且无攻击时不掉分 |
| R15 异常注入测试 | benchmark / CI | 能；十层清单已有两套开源实现 |
| R7 不可信内容结构性隔离 | harness + 每站 15–30 条选择器 | 能，但标注必须零漏标，且只防 control-flow |
| R4 不让语言头吐坐标 | 模型训练 **或** harness 图像预处理 | 后者能立刻落，代价是两次调用与 3.8× 延迟 |
| R11 批量动作逐个校验前置条件 | harness + 可信系统 API | 桌面能（UIA）；浏览器侧没有等价的可信 `is_enabled()` |
| R9 副作用类型 + exactly-once WRITE | 站点/服务端声明 + harness 重放器 | **不能**，现有协议栈无任何对应物 |
| R8 origin 绑定的不可变 tool_id | 浏览器 / 规范层 | **不能**，WebMCP 仍在 origin trial |
| R20/R21 跨步 ID 稳定性与动态页失效率 | harness | **不能**，先要有测量 |

最后一条不在表里，但它决定前面所有条目的可移植性：**R8 那格显示的"模型升级对协议层漏洞完全无效"，反过来说明这张表里凡是标"harness"的规则都不会被下一代模型自动吸收掉。** 它们是工程契约，不是提示词技巧——而标"提示词约定"的东西已经被证明不可移植（同一条 refresh 提示救回一个 benchmark 却让另一个恶化）。

---

## 9. 附录：completeness critic 回收的线索（全部未独立核验）

报告成稿后，两个 completeness critic 返回了各自认为被系统性遗漏的工作。以下条目**只经过 critic 的一次阅读，我没有回原文核过任何一个数字**，因此不进规则表、不改任何一条规则的档位；列在这里是因为其中几条一旦核实，会直接移动本报告的结论。

**会改变已有条目的四条。**

| 线索 | 涉及本报告哪里 | 核实后会怎样 |
|:-----|:---------------|:-------------|
| 2507.14799：prompt injection 可以走 accessibility tree 注入 | §3.3、R7、R14 | §3.3 目前只论证了结构通道的**值不可信**（陈旧快照、已滚出屏幕仍报可见）。若这条成立，结构通道同时是**注入面**，则"改用 AXTree 就顺带更安全"这一顺带主张也被否掉，R14（削减器复用为注入过滤器）要额外覆盖结构通道而不只是渲染文本 |
| WebAIM Million 2026 年度普查：95.9% 首页存在可检测的 WCAG 失败，平均每页 56.1 个错误，且带 ARIA 的页面平均 59.1 个错误、不带的 42 个 | §5「标注覆盖率」空白、全部依赖 AXTree 的寻址规则 | §5 现在只有移动端数据（59% 屏幕 / 94% app）。若 web 侧数据成立，"a11y 树是已经存在的免费语义层"这个几乎所有 harness 都默认的前提，在 web 上有一个可引用的上界；且 ARIA 越多错误越多意味着标注量与标注质量不同向 |
| 2602.14878（103 个 server 的 856 个工具中 97.1% 存在描述缺陷）、2602.03580（约 13% 的描述与代码不一致、可执行未记录的操作）、2509.25292（8401 个 MCP 项目中过半无效或低价值） | §6 协议栈、§7 工具发现成本 | 这三条测的是**常态质量分布**，不是攻击。R8 目前只覆盖了恶意注册竞态；若常态偏离率就是两位数，那么"声明式接口 = 可信接口"在没有运行时契约核验的情况下不成立，这会给 R8 加一条非安全动机 |
| 2606.06460：agent 对带内治理信号的服从率——入口处依模型在 55%–100% 之间，任务中途叫停 0/40，向操作者上报警告 0/100 | §7、permission manifest 一族 | §7 现在的论证是"要求站点动的方案零评测"。若这条成立，论证要再进一步：即便站点动了，声明侧也没有强制力，因此 permission manifest 的问题不是采纳率低而是**即使被采纳也不改变 agent 行为** |

**只补强、不改结论的。** 2504.01382（Online-Mind2Web：既有 benchmark 系统性高估真实站点上的性能）给全表的效应量加一个统一折扣，方向与本报告已有的"self-built testbed 归类"一致；2412.05467（BrowserGym 统一 observation/action space）指出了 §4 那七处分歧**技术上**为什么无法裁决——各家在各自的动作空间上报数，缺一层共同底座；2104.04116（22.7 万篇新闻页 1998–2016 的纵向测量：social card metadata 2016 年达 95% 采纳，同期 schema.org / Dublin Core 远远落后）给 §7 提供了唯一一条有纵向数据支撑的采纳判据——决定自愿标注能否铺开的不是语法或本体复杂度，而是标注是否带来即时、可归因到本页的分发收益，按这条判据本报告 §6 里的站点侧提案没有一个具备；2510.10315（正规站点对 AI 爬虫的屏蔽率 2023-09 约 23% → 2025-05 约 60%）与 2606.30119（多层指纹可高准确率识别 agent）说明站点侧当前的实际投入方向是识别与拦截，"站点不合作"是可执行策略而非被动状态；2607.12575（x402 结算的链上测量：21.20% 虚构交易、63.78% 关联簇内部转账、Gini 大于 0.98）给出了采纳类指标的通用警告——注册数、调用数、server 数衡量的是可制造性而非采纳。

两个 critic 之外还有一处方法学提醒值得原样记下：按干预层次（页面 / 客户端 / OS / 协议 / 法律）分类然后宣称某一层"更有前景"，是先验分类学上的无终点细分——每一层**内部**从 position-only 到 controlled-comparison 的证据强度差异，远大于层与层之间的差异。这正是本报告按证据档而非按层次排序的理由。

---

## 相关

- [[Reports/2026-07-27-WebAgent-RL-and-Context-Landscape]] — 两轴文献地图，本报告的规则来自其中轴 B 的 §2.1/§2.2/§2.3 与 §2.6
- [[Topics/CUA-Survey]] — GUI/CUA canonical survey，其动作表示一节把索引 vs 坐标正确地写成"平台无关性 vs 可验证性"的取舍而非可靠性排序
- [[Papers/2410-AgentOccam]] · [[Papers/2511-Prune4Web]] · [[Papers/2510-FocusAgent]] · [[Papers/2607-MAG]] · [[Papers/2401-SeeAct]] · [[Papers/2604-GoClick]] · [[Papers/2512-MobiBench]] · [[Papers/2607-UCM]] · [[Papers/2512-PermissionManifestsWebAgents]] · [[Papers/2500-GuiActorCoordinateFree]] · [[Papers/2512-AgentProg]] · [[Papers/2606-LUMOS]]
