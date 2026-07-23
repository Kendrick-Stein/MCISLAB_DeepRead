---
title: "WebForge: Breaking the Realism-Reproducibility-Scalability Trilemma in Browser Agent Benchmark"
authors: [Peng Yuan, Yuyang Yin, Yuxuan Cai, Zheng Wei]
institute: [Tencent BAC, Tsinghua University]
date_publish: 2026-04-13
venue: arXiv
tags: [gui-agent, web-agent]
url: https://arxiv.org/abs/2604.10988
arxiv_id: "2604.10988"
doi:
cite_key:
code:
rating: 4
date_added: 2026-07-21
---
## Summary
提出 browser agent benchmark 的 "realism–reproducibility–scalability trilemma"，并用 Plan→Generate→Refine→Validate 四 agent 全自动流水线生成自包含静态网站环境来同时满足三者，产出 934 任务、7 domain × 3 难度的 WebForge-Bench，配七维难度控制实现聚合分数无法提供的能力画像。

## Problem & Motivation
现有 browser agent benchmark 陷入三难：真实网站类（WebVoyager、Mind2Web）有 realism 但 content drift 使任务持续失效——Mind2Web 约一半任务两年内过期，WebVoyager 有 22.3% 的答案 non-deterministic；受控环境类（WebArena、EntWorld）可复现但过于"干净"（无弹窗、cookie 对话框、网络延迟），且依赖昂贵人工标注（TheAgentCompany 175 个任务耗约 3,000 person-hours）；自动生成类（BenchAgents、AutoBencher、DyVal）只能处理非交互任务。任务多样性不足还会虚高分数：Browser Use 在 WebVoyager 报 ~90%，但在 Online-Mind2Web 更广的 136 网站 benchmark 上经严格人评仅 30%。评测本身也不可靠——BrowserArena 发现 GPT-4o 作 judge 与人类一致率仅 68%。

## Method
四 agent 流水线，端到端零人工标注：
- **Plan Agent**：双阶段规划——高温（T=2.0）创意模型起草任务 + 低温（T=1.0）精确模型精修（至少改 30–50%），输出含七维难度向量 δ∈{1,2,3}⁷ 的任务蓝图。七维为 jump depth / jump breadth / page interaction / visual complexity / info complexity / reasoning-calculation / risk factor。
- **Generation Agent**：把蓝图实例化为完整可运行的自包含静态网站（HTML/CSS/JS + localStorage 状态管理支持购物车、表单等有状态交互），从真实网站搜集视觉参考与真实数据嵌入；内置 anti-cheating 机制（加密数据存储、deceptive error code、代码混淆）。
- **Refinement Agent**：按质量规则清单做 Assess→Plan→Execute→Verify，关键是注入 real-web noise（弹窗广告、cookie consent、模拟网络延迟），弥合"无菌"环境与真实网页的差距。
- **Validation Agent**：在与被测 agent 相同的 Chromium 引擎中以 Observe–Reason–Act 循环重放 solution path（≤50 步，3-retry），只有最终状态与 ground truth 严格一致的任务保留。
评测采用 final-state paradigm：只比对最终输出与 ground truth（Direct Answer / Operation Code / Mixed 三种答案类型），evaluator LLM 只做直接比较，不做复杂语义判断。部署只需打开 HTML 文件，无外部服务。

## Key Results
- 流水线生成 1,260 任务（7 domain × 3 level × 60），Validation 后保留 934，pass rate 74.1%；ablation：去掉 Plan 精修降到 59.5%，再去 Refinement Agent 降到 51.4%。
- 14 个模型配置评测：Gemini-3-Pro 最高 75.9%，Claude-4.5-Sonnet 69.9%，Gemini-3-Flash 67.1%；开源最强 Kimi-K2.5 66.4%，超过闭源 GPT-5.2（59.5%）。整体区间 12.7–75.9%，既不随机也不饱和。
- 难度分层有效：L1 多数模型 ≥73%，L3 最强弱差 56 pt（Gemini-3-Pro 58.0% vs Qwen3-Omni-30B 2.4%）。
- 视觉输入 ablation：去掉 screenshot 只给 DOM，整体掉 16–17 pp（Gemini-3-Pro 75.9%→59.2%），且难度越高差距越大（L1 约 6 pt，L3 20+ pt）。
- Cross-domain：Info Retrieval（56.9%）与 Content Creation（57.2%）最易，Consumer Transaction 与 Content Moderation 最难（均 48.3%）；9/14 模型的最差 domain 是 D1 或 D2。
- 成本随难度超线性：L1→L3 prompt token 增长 5–8×（Claude-4.5-Sonnet L3 平均 1608K prompt tokens/task）。
- 七维分解中 Visual Complexity 的 L1→L3 下降最陡，Reasoning/Calc 最能区分强弱模型（L3 上 Gemini-3-Pro 58.3% vs GPT-5-Nano 6.4%）。

## Strengths & Weaknesses
**亮点**：(1) trilemma 表述精准命中了 GUI/Web 评测领域的核心矛盾，并用引证数字（Mind2Web 半数过期、Browser Use 90% vs 30%）把问题严重性量化；(2) "生成自包含静态网站"是解 trilemma 的一个简洁路径——可复现性由 self-contained 保证，realism 由真实数据 + noise injection 逼近，scalability 由全自动流水线保证；(3) a priori 七维难度控制比事后标注的难度维度（VisualWebArena、EntWorld）更可控，per-dimension 分析确实给出聚合分数看不到的能力画像；(4) Validation Agent 在与评测相同的浏览器栈中重放，能抓 rendering 依赖 bug，这是纯源码检查做不到的。
**局限**：(1) "realism" 是生成出来的近似——LLM 生成的静态站点与真实生产网站的分布差距（sim-to-real gap，作者在附录 C 中自己承认）未被量化，noise injection 覆盖的干扰类型也由规则清单决定；(2) final-state evaluation 对过程不做约束，无法评测 safety/副作用类行为（如中途误操作后自我恢复），且 Operation Code 机制依赖网站内嵌 judge，本质上信任生成代码的正确性；(3) 难度七维承认不完全正交（高难度任务多维同时抬升），per-dimension 结论的归因有混杂；(4) 任务由 LLM 设计，可能系统性偏向 LLM 自己"想得出"的任务分布，与真实用户需求分布的偏差未验证。对领域的影响：为 GUI/Web agent 评测提供了"自动生成可复现环境"这条与 live-web 维护（Online-Mind2Web 路线）互补的路径，也自然延伸到训练数据生产（作者已在 Limitations 中点出）。

## Mind Map
```mermaid
mindmap
  root((WebForge))
    Problem
      Benchmark trilemma
        Real web: content drift
        Controlled: 无 noise + 人工贵
        Auto-gen: 非交互
      聚合分数掩盖能力画像
    Method
      四 agent 流水线
        Plan 双阶段规划
        Generate 自包含静态站
        Refine noise 注入
        Validate 浏览器重放
      七维难度向量 δ∈{1,2,3}⁷
      Final-state 评测 + anti-cheating
    Results
      934 任务 74.1% pass
      Gemini-3-Pro 75.9% 最高
      视觉输入 16-17pp
      L3 强弱差 56pt
```

## Notes
- 与 [[2401-WebVoyager]]（被批判的 live-web 基线）、[[2400-WebcanvasBenchmarkingWebAgents]]（报告 Mind2Web 任务 12% 一年内过期）构成 GUI 评测可靠性证据链；trilemma 数字（半数两年过期、22.3% non-deterministic、90% vs 30%）可直接入 GUI survey 的 evaluation 章节。
- 关键疑问：生成环境上的排名与 live-web 排名的相关性未报告——如果两者排名一致性低，"realism" claim 需要打折。
