---
title: WebGym 与 AsyncWebRL 阅读报告
date: 2026-06-23
tags: [report, web-agent, gui-agent, agentic-RL, environment]
sources:
  - "[[2601-WebGym]]"
  - "[[2606-AsyncWebRL]]"
  - "[[2605-MobileGym]]"
  - "[[2307-WebArena]]"
  - "[[2400-WebcanvasBenchmarkingWebAgents]]"
  - "[[2600-InfinitewebScalableWebEnvironment]]"
---

# WebGym 与 AsyncWebRL 阅读报告

## 结论先行

WebGym 和 AsyncWebRL 是一组连续工作：**WebGym 解决 visual web agent RL 的训练环境规模与 rollout throughput，AsyncWebRL 进一步解决这个环境上的 multi-step RL 系统效率和 loss pathology**。

它们确实回答了“有没有 WebGym 这样的工作”：有，而且已经很接近 web agent RL training infra。但它们和 [[2605-MobileGym]] 的关键思想并不完全相同：

- **MobileGym**：controlled functional simulator，核心是 JSON state / EFSM transition / state forking / deterministic verifier。
- **WebGym**：large-scale real website task environment，核心是真实网站任务分布 / rubric evaluator / high-throughput rollout。
- **AsyncWebRL**：WebGym 上的 training system，核心是 fully async rollout / screenshot handling / GRPO normalizer 修复。

所以，你的 insight 仍然成立，而且是一个空白点：**Web 领域已有 WebGym，但还缺一个真正 MobileGym-style 的 transition-faithful web simulator**。也就是不追求 pixel-perfect，而追求 UI/backend/session state transition 的 functional fidelity。

## 两篇工作分别做了什么

### WebGym

**定位**：web agent RL training environment。

**核心组件**：

1. 聚合 10 个 web task sources，生成近 **292K tasks / 127K websites**。
2. 用 GPT-4o 为任务生成 rubric fact groups，并通过 fact group decomposition 扩展不同 difficulty。
3. 用 rubric-based evaluator 作为 binary reward。
4. 构建高吞吐 rollout system：128 CPUs + 24 H100 下 30 分钟收集 1,800 trajectories，平均 13.2 steps。
5. 用简单 REINFORCE-like online RL 训练 Qwen3-VL-8B-Instruct。

**核心结果**：

- Qwen3-VL-8B-Instruct OOD test：26.2% -> **42.9%**
- 超过 GPT-4o agent 27.1% 和 GPT-5-Thinking agent 29.8%
- test split 只包含未见过网站，说明不是简单记忆网站模板

**真正贡献**：不是模型结构，而是证明 visual web agent 可以沿着 **task distribution scaling + rollout throughput scaling + simple RL** 这条路提升。

### AsyncWebRL

**定位**：WebGym 上的 efficient multi-step RL framework。

**系统贡献**：

1. **Everlasting rollout pool**：browser workers 不在 iteration 边界重建，rollout / update / policy refresh 连续重叠。
2. **Lightweight screenshot handling**：截图留在专门 in-memory actor，只传 reference，避免 shared object store 被高分辨率视觉轨迹拖垮。
3. **Decoupled off-policy correction**：async rollout 的 stale policy 通过 decoupled importance ratio 修正，clip-trigger rate 大约减半。

**算法贡献**：

multi-step GRPO 的 `1/|tau_i|` step normalizer 会低估长失败轨迹的负梯度。WebGym 中失败轨迹平均 12.5 steps，成功轨迹 5.1 steps，因此失败 token 被约 2.4x down-weight。模型于是学会在 append-only Memory JSON 里不断添加 generic slots，导致 token / step 膨胀。

把 `1/|tau_i|` 替换为常数 `1/k` 后，长失败轨迹获得足够惩罚，trajectory 和 memory 都收缩。

**核心结果**：

| Model | Method | Easy | Medium | Hard | Avg |
|:--|:--|--:|--:|--:|--:|
| Qwen3-VL-8B-Instruct | Base | 32.5 | 11.2 | 0.0 | 26.2 |
| Qwen3-VL-8B-Instruct | WebGym sync REINFORCE | 50.9 | 24.1 | 4.8 | 42.9 |
| Qwen3-VL-8B-Instruct | AsyncWebRL full | **52.4** | **34.3** | **7.1** | **45.4** |
| Qwen3-VL-8B-Thinking | Base | 37.4 | 24.3 | 1.2 | 32.0 |
| Qwen3-VL-8B-Thinking | AsyncWebRL full | **51.8** | **35.1** | **11.3** | **44.4** |

系统吞吐上，AsyncWebRL 约 **2.4-2.9x** end-to-end speedup，项目页报告约 3,100 traj/h，对比 sync WebGym 的约 1,300 / 1,050 traj/h。

## 和 MobileGym 的核心差异

| 维度 | MobileGym | WebGym | AsyncWebRL |
|:--|:--|:--|:--|
| 目标 | mobile GUI simulation + RL | web task scaling + RL | WebGym 上高效 RL |
| 环境来源 | browser-hosted Android-like functional model | real website tasks / broad web distribution | 复用 WebGym |
| 状态建模 | world data / runtime state / OS runtime state | 任务 + rubric，未显式建模 backend state transition | 不涉及环境建模 |
| Transition | EFSM + guards + updates | 真实网站运行时转移，非可控规范 | 复用真实网站转移 |
| Forking | 支持任意 state fork | 不强调 state forking | 不解决 |
| Reward | AnswerSheet / deterministic state verifier | rubric-based evaluator，偏 LLM judge | 复用 WebGym reward |
| 核心数字 | 95.1% sim-to-real retained gain | 26.2 -> 42.9 OOD SR | 42.9 -> 45.4 OOD SR，2.9x speedup |
| 关键 insight | interaction fidelity > pixel-perfect | task distribution + rollout scaling | async system + loss shape matters |

所以，WebGym 不是“Web 版 MobileGym”。更准确地说：

> WebGym 是 Web 侧大规模 RL 训练任务环境；MobileGym 是 mobile 侧可控 functional simulator。

二者共同说明：GUI/web agent 的瓶颈正在从单个模型转向 **环境、reward、rollout system**。但它们选择的环境哲学不同。

## 对你的想法的直接启示

你说“仿真界面 pixel perfect 不是重点，重点是模拟界面转化的过程”，这个判断我认为是对的，而且可以进一步形式化：

**界面仿真的对象不是 screenshot，而是 action-conditioned state transition。**

对 Web 来说，transition 至少包括四层：

1. **Rendered UI state**：用户能看到什么，元素如何出现、消失、更新。
2. **DOM / component state**：React/Vue state、form state、route state、modal state。
3. **Backend / database state**：购物车、订单、用户设置、评论、issue、权限等。
4. **Browser/session state**：cookie、localStorage、history、tab、auth、cache。

Pixel-perfect 只是 rendered UI 的一个投影。真正决定 agent 是否学会任务的是：

- action 后哪些 state 变了？
- 哪些变化可见，哪些隐藏？
- 哪些变化可 verifier 检查？
- 哪些变化是 reversible，哪些会产生 side effect？
- state 是否可 reset / fork / branch rollout？

这就是 MobileGym 比普通 emulator 更有 insight 的地方，也是 WebGym 还没完全解决的地方。

## 可以做的研究题

### 题目 1：Transition-Faithful WebGym

**一句话**：构建一个 Web functional simulator，不追求真实网站像素级复刻，而是用 declarative state machine + backend state model 精确模拟 web task 的关键 transition。

**核心假设**：

> 对大多数 web automation 任务，agent 训练所需的是 action-conditioned functional transition fidelity，而不是 pixel-perfect layout fidelity。

**最小实现**：

- 选 3-5 类 web apps：shopping、forum、issue tracker、CMS、booking。
- 每类做 10-20 个 task templates。
- 每个 app 用：
  - `world_data`: 商品、帖子、issue、用户等只读数据
  - `runtime_state`: cart、form、draft、settings、created records
  - `browser_state`: URL、history、tab、session
  - `transition_spec`: click/type/submit/navigation 的 guarded updates
  - `verifier`: programmatic checker + partial credit
- 和真实 WebArena / live websites 做 sim-to-real 或 sim-to-benchmark transfer。

**关键指标**：

- task success transfer retention
- state divergence after matched action traces
- verifier coverage
- rollout throughput
- reward hacking rate

### 题目 2：Functional Fidelity Boundary for Web Agents

**一句话**：系统研究 Web 任务中哪些交互可以 functional model，哪些必须 live / pixel / backend。

**任务 taxonomy**：

- static information lookup
- form filling
- search / filter / sort
- cart / checkout-like state changes
- authentication / permission
- dynamic recommendation / ads
- real-time chat / notification
- canvas / drag-and-drop / visual editor

**核心实验**：

同一批任务在不同 fidelity 下训练/评估：

1. text-only state
2. DOM / accessibility state
3. rendered screenshot
4. functional transition simulator
5. live website

看哪些任务的性能依赖像素，哪些只依赖 transition。

### 题目 3：Verifier-Grounded Web RL

**一句话**：把 WebGym 的 rubric evaluator 替换或增强成 programmatic verifier，研究 reward fidelity 对 RL 的影响。

**动机**：WebGym 能 scale，但 reward 主要来自 rubric evaluator；MobileGym/OpenComputer 说明 deterministic verifier 可能更可靠。

**实验设计**：

- 构建一组任务，同时有 LLM rubric judge 和 programmatic checker。
- 对比 RL 训练后：
  - success rate
  - false positive reward
  - reward hacking
  - partial credit learning
  - OOD transfer

这个方向比“再做一个 WebGym 大任务集”更有 insight。

## 我的研究判断

**WebGym / AsyncWebRL 已经覆盖了：**

- 大规模 visual web task training
- online RL recipe
- rollout throughput
- multi-step GRPO 的长度归一化问题

**还没有充分覆盖：**

- transition-level functional fidelity
- deterministic web state verifier
- state forking / branch rollout
- backend state + rendered state 一致性
- sim-to-live transfer 的机制解释
- reward hacking / side-effect / reversibility

所以，如果沿着 MobileGym 的启示继续做，我不建议直接复刻 WebGym 的“更多任务 + 更快 RL”。更值得做的是：

> 用更小但更可控的 web apps，证明 transition-faithful functional simulation 能产生可迁移的 web agent 能力，并量化 fidelity boundary。

这会比“我们也做了 30 万任务”更有 research taste。

## 相关文件

- [[2601-WebGym]]
- [[2606-AsyncWebRL]]
- [[2605-MobileGym]]
- [[2307-WebArena]]
- [[2400-WebcanvasBenchmarkingWebAgents]]
- [[2600-InfinitewebScalableWebEnvironment]]

