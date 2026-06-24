---
title: "CUA-Gym: Scaling Verifiable Training Environments and Tasks for Computer-Use Agents"
authors: ["Bowen Wang", "Dunjie Lu", "Junli Wang", "Tianyi Bai", "Shixuan Liu", "Zhipeng Zhang", "Haiquan Wang", "Hao Hu", "Tianbao Xie", "Shuai Bai", "Dayiheng Liu", "Que Shen", "Junyang Lin", "Tao Yu"]
institute: []
date_publish: "2026-06-08"
venue: "arXiv"
tags: [agentic-RL, computer-use, gui-agent]
url: "https://arxiv.org/abs/2605.25624"
code: "https://github.com/xlang-ai/CUA-Gym"
rating: "5"
date_added: "2026-06-24"
---
## Summary

CUA-Gym 提出一个为 Computer-Use Agent 合成 verifiable RLVR training data 的 pipeline：自动共同生成 task instruction、initial/golden environment state 和 programmatic reward function，并构建 110 个 desktop+web 环境、32,112 个 verified training tuples。用这些数据做 GSPO 训练后，CUA-Gym-A3B 在 OSWorld-Verified 从 54.5 提升到 62.1，CUA-Gym-A17B 达到 72.6，同时在 held-out WebArena 上也有迁移提升。

## Problem & Motivation

RLVR 在 math、tool-use、software engineering 上成功，很大原因是存在可规模化的 verifiable reward：数学有答案，代码有 tests，SWE 有 issue/test suites。但 GUI / CUA 没有天然语料、没有统一 verifier，也很难在真实 app 上大规模 reset 和并行 rollout。

已有路线各有缺口：人工构造 benchmark reward fidelity 高，但覆盖应用少、成本高；LLM-as-judge 数据集可以扩展，但 reward 不稳定，容易把“看起来完成”误判为完成。CUA-Gym 的核心目标是把 CUA 的 RLVR 数据三元组 `(task, environment, reward)` 规模化，同时保持 deterministic / programmatic reward。

## Method

**1. Verifiable RLVR tuple**

每个训练样本不是单独的 instruction，而是完整 bundle：

- `task.json`：自然语言任务和环境元数据。
- `initial_setup.py | .sh | .xlsx | .docx | .pptx`：构造初始状态。
- `golden_patch.py`：构造理想完成状态，用于 reward 校验。
- `reward.py`：程序化检查 agent 是否完成任务。

**2. Generator-Discriminator-Orchestrator co-generation**

CUA-Gym 用三个 agent 协作生成每个 tuple：

- **Generator / setup-gen**：构造 initial environment state 和 golden environment state。
- **Discriminator / reward-gen**：仅从 task description 写 `reward.py`，不看 Generator 代码。这个 information barrier 防止 reward 只是复述 setup 实现细节。
- **Orchestrator**：执行两者输出并迭代，直到 `reward(golden)=1.0` 且 `reward(initial)=0.0`。

这点是方法核心：不是先独立生成任务、环境、reward 再事后过滤，而是在执行循环中共同生成并强制三者一致。

**3. Filtering**

生成的 tuple 还要过两层过滤：

- **LLM majority-vote filter**：检查 reward 是否 fragile、ambiguous、inconsistent，覆盖 consistency、executability、hack-risk、clarity、difficulty 等维度。
- **Teacher rollouts**：用 teacher agent 运行任务，结合 reward log 和 VLM-as-judge 做 alignment check，进一步排除不可靠任务。

**4. CUA-Gym-Hub**

为解决训练环境少的问题，作者合成 CUA-Gym-Hub：一组 self-contained mock web applications，面向 productivity、communication、development、commerce、finance、analytics、media 等真实知识工作分布。GitHub README 说 CUA-Gym 覆盖 110 environments：16 desktop applications 和 94 synthesized mock web applications；作者 blog 页面另称 CUA-Gym-Hub 有 99 mock applications，可能是项目页面与 arXiv/README 版本差异。

Mock app 的关键设计：

- **Unified state API**：每个 mock 支持 state injection、reset、retrieval、diffing。
- **Task-specific JSON initial state**：同一个 app 可以承载大量不同 task world。
- **Session isolation**：URL 携带 session id，多个 RL worker 并行训练时互不污染状态。
- **Programmatic reward**：`reward.py` 直接检查环境 state，而不是依赖 screenshot 或人工标签。

## Key Results

**Dataset scale**

| Dataset | Platform | Data size | Env size | Reward | Open |
|---|---|---:|---:|---|---|
| GUI-Genesis | Mobile | 969 | 1 | Programmatic | No |
| WebArena-Infinity | Web | 1,260 | 10 | Programmatic | Yes |
| InfiniteWeb | Web | 600 | - | Programmatic | Partial |
| UltraCUA | Desktop | 17,000 | 9 | Programmatic | Partial |
| Gym-Anything | Desktop | 7,277 | 193 | VLM | Yes |
| CUA-Gym | Desktop + Web | 32,112 | 110 | Programmatic | Yes |

**Model results**

GitHub README / arXiv v2 报告：

| Model | OSWorld-Verified | WebArena |
|---|---:|---:|
| Claude Sonnet 4.6 | 72.9 | 65.6 |
| Claude Opus 4.7 | 78.0 | - |
| GPT-5.5 | 78.7 | - |
| Kimi-K2.6 | 73.1 | - |
| Qwen3.5-35B-A3B base | 54.5 | 40.8 |
| Qwen3.5-397B-A17B base | 62.2 | 54.0 |
| CUA-Gym-A3B | 62.1 | 44.5 |
| CUA-Gym-A17B | 72.6 | 56.0 |

主要结论：

- A3B 从 54.5 到 62.1，在约 10x 更少 active parameters 下接近 A17B base。
- A17B 从 62.2 到 72.6，达到开源 CUA 的强结果区间。
- WebArena 没有进入训练集，但 A3B 从 40.8 到 44.5，A17B 从 54.0 到 56.0，说明 synthetic web mocks 可能学到可迁移的 browser interaction 能力。
- 作者 blog 提到 RL 后出现 action batching，matched success 下有效轨迹长度减少 33-45%。这点很有意思，但在 arXiv abstract/README 摘要中不是主表结果，后续需要核对论文正文。

**版本差异备注**

作者 blog（2026-05-10）写 A17B 从 62.2 提升到 70.2；arXiv v2 / GitHub README 写 CUA-Gym-A17B 为 72.6。笔记采用较新的 arXiv v2 / README 数字，同时保留这个 discrepancy 作为版本差异。

## Strengths & Weaknesses

**Strengths**：

- **把 CUA RLVR 的数据瓶颈拆对了**：不是只生成 instruction，而是生成 task、environment state、reward 三元组。这个 formulation 比普通 synthetic instruction 数据更接近 RL 训练所需的闭环。
- **information barrier 是关键设计**：Discriminator 不看 Generator 代码，迫使 reward 从 task semantics 出发，降低 reward 过拟合 setup 实现或直接泄漏答案的风险。
- **programmatic reward + state API 有训练价值**：相比 LLM-as-judge，程序化 reward 更适合大规模 RL rollout、rejection sampling 和 regression testing。
- **环境多样性实证有效**：110 environments、32K tuples 带来 OSWorld 和 WebArena 的双提升，尤其 WebArena OOD transfer 说明 mock web 不是完全过拟合。
- **开源价值高**：pipeline、dataset、CUA-Gym-Hub 和模型计划开源，可能成为后续 CUA RL 的数据底座。

**Weaknesses**：

- **mock environment 的真实性边界**：CUA-Gym-Hub 是仿真实 app 的 mock web applications，不是真实 SaaS。统一 state API 对训练很友好，但可能让 agent 学到“可控 app”的分布，而不是生产环境中的异常、延迟、权限和长尾 UI。
- **reward correctness 仍是核心风险**：`reward(golden)=1` / `reward(initial)=0` 只能排除最基本错误，不能保证 reward 覆盖所有语义要求。Majority-vote 和 teacher rollout 是过滤，不是形式化证明。
- **query/task realism 仍未解决**：作者 blog 明确说，当 reward 和 environment 自动化后，瓶颈转向 query：好任务不仅是 well-formed instruction，还要有真实初始上下文、合适难度和明确能力目标。
- **可能存在 benchmark contamination 风险**：16 desktop apps 来自 OSWorld environment pool，并在 OSWorld-Verified 上评测，虽然任务不同，但环境熟悉度可能贡献一部分分数提升。WebArena transfer 是更干净的证据，但增幅较小。
- **RL regression 仍存在**：blog 的 per-domain breakdown 显示 A17B 在 Thunderbird 上从 80.0 降到 66.7，说明 RL data 并非单调改善所有 domain。

**Impact**：

CUA-Gym 是当前最值得关注的 CUA RLVR 数据工作之一。它把环境合成、任务合成、reward 合成统一成可执行 pipeline，直接连接到 agentic-RL。对后续研究而言，关键问题不再是“能否生成 GUI 任务”，而是“如何证明 reward 真的测到了目标能力、mock 环境是否迁移、数据多样性与训练收益的 scaling law 是什么”。

## Mind Map

```mermaid
mindmap
  root((CUA-Gym))
    Problem
      CUA缺自然语料
      真实app难以大规模rollout
      缺统一verifier
      LLM-as-judge不稳定
    Method
      RLVR tuple
        task
        initial state
        reward.py
      Generator
        initial and golden state
      Discriminator
        reward from task only
      Orchestrator
        reward(golden)=1
        reward(initial)=0
      CUA-Gym-Hub
        mock web apps
        unified state API
        session isolation
    Results
      32112 tuples
      110 environments
      A3B 54.5 to 62.1
      A17B 62.2 to 72.6
      WebArena transfer
    Risks
      mock realism
      reward loopholes
      task realism bottleneck
      OSWorld environment familiarity
```

## Notes

- 和 [[Papers/2600-WebHarbor|WebHarbor]] 的关系：WebHarbor 更接近真实网站 mirror，强调 visual fidelity 和 deep features；CUA-Gym 更偏 RLVR 训练数据，强调 state API、reward.py 和可并行 rollout。
- 和 [[Papers/2605-SaaSBench|SaaS-Bench]] 的关系：SaaS-Bench 是 evaluation benchmark，揭示真实 SaaS 长程工作流 resolved score 极低；CUA-Gym 是 training data pipeline，目标是用大量 verifiable tuples 改善 agent 能力。
- 一个值得做的 follow-up：把 WebHarbor mirror 接到 CUA-Gym 的 unified state API / reward generation pipeline，形成“更真实 web surface + 可验证 RL reward”的训练环境。
- 另一个 follow-up：研究 reward exploit taxonomy。CUA-Gym 需要系统报告 reward.py 被 agent 钻空子的案例，否则 programmatic reward 的可靠性很难判断。
