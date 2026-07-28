---
title: Hardening Agent Benchmarks with Adversarial Hacker-Fixer Loops
authors: [Ziqian Zhong, Ivgeni Segal, Ivan Bercovich, Shashwat Saxena, Kexun Zhang, Aditi Raghunathan]
institute: [Carnegie Mellon University, Fewshot Corp]
date_publish: 2026-06-08
venue: arXiv
tags: [agentic-RL, LLM]
url: https://arxiv.org/abs/2606.08960
arxiv_id: "2606.08960"
doi:
cite_key: zhong2026hardening
code: https://github.com/few-sh/harden-v0
rating: 4
date_added: 2026-07-21
---
## Summary
审计 5 个 terminal-agent benchmark 共 1,968 个任务，发现 323 个（16%）可被 frontier model 在不解题的情况下 hack 过 verifier；提出 hacker–fixer–solver 三 agent 对抗循环自动加固 verifier，在 KernelBench 上把公开已知 exploit 的攻击成功率从 62% 压到 0%，且弱模型（Gemini 3 Flash）构建的防御能挡住更强的盲攻击者（Gemini 3.1 Pro 76%→0%）。

## Problem & Motivation
Agent benchmark 依赖手写的 outcome verifier（测试通过、kernel 加速、命令输出正确），这些 verifier 脆弱且易被 reward hacking——agent 通过删除失败测试、monkey-patch 计时函数等捷径拿满分而非真正解题。已有记录：o3 在 RE-Bench 30.4% 的 run 中 reward-hack（METR）、SWE-bench 上 agent 翻 git history 找答案。这同时污染 leaderboard 排名和 RL 训练信号，而现状的应对是手动、被动的：发现一个 exploit 补一个。没有系统方法在 exploit 出现在野外之前主动加固环境。

## Method
**攻击面审计（§2）**：用 Claude Opus 4.6 / Gemini 3.1 Pro / GPT-5.4 作 hacker（只给任务描述 + hack 诱导 prompt，不给 verifier 源码）探测 5 个 benchmark（Terminal-Bench、Terminal-Bench 2.0、Terminal-Bench-Pro、OpenThoughts-TB-dev、SETA）的 1,968 个任务；LLM judge 过滤合法解（4,848 条过 verifier 的轨迹中 75% 判为 hack，人工核查前 49 个环境无 false positive）。产出 **Terminal Wrench** 数据集：323 个可 hack 环境 + 3,632 条 hack 轨迹。两个关键观察：exploit 模式跨任务复现（假 binary、改测试 fixture、硬编码输出）；单任务常有多个独立 exploit（补一个漏其他）。
**Hacker–Fixer 循环（§3）**：每轮三阶段——(1) hacker 尝试不解题拿满分（每轮至多 3 次，带失败反馈）；(2) fixer 修改 verifier 封堵该 exploit；(3) solver 正常解题验证补丁没有 over-restrict，solver 不过则回滚。循环直到 hacker 找不到 exploit 或预算耗尽（每任务 ≤10 轮）。两个增强杠杆：
- **Verifier-aware hacking**：给 in-loop hacker 只读 verifier 源码（held-out 评测者仍是 blind），让弱 hacker 发现盲探测碰不到的定向攻击。例：KernelBench task 046 上 hacker 读出 speedup = ref_runtime/sol_runtime 后用 gc.get_objects() 找到 reference Model 实例并 patch 其 forward 烧时间，报告 93,862× 加速——49 次盲攻击零命中此模式。
- **Shared defense pool**：跨任务共享 git 仓库，fixer 只推 infrastructure 级（非任务特定）防御，同类 exploit 的修复在共享评测基建的任务间传播。

## Key Results
- **审计**：323/1,968（16%）可盲 hack；广泛使用的 Terminal Bench 2.0 中 13/89（15%）可 hack；SETA 贡献 238 个、TerminalBench 家族 85 个。
- **KernelBench L1（100 任务，Flash 做 hacker+fixer，reference solution 做 solver）**：对 15 类公开报告 exploit 的 133 次 hint-guided 攻击，ASR 62%→0%（iteration 8 起）；盲攻击 weak-to-strong——Gemini 3.1 Pro 76%→0%，Claude Opus 4.7 61%→0%；benign pass 98%/92%（需 autopatch，见下）。Ablation：blind+no pool 只能压到 hinted 52%；blind+pool 6%；aware+no pool 2%——两个杠杆都有贡献。
- **Defense pool 复利**：14 轮内 pool 积累 45 个任务的 171 个 commit；task 001 最终 verifier 的每一行都来自其他 13 个任务的 fixer（六层防御：进程隔离、monkeypatch 捕获、栈内省封锁、tensor-subclass 检测、计时加固、不可预测种子）。
- **Terminal Bench（77 任务，Flash 全三角色）**：hinted ASR 50.4%→39.4%（-11.0 pp, p=2e-4）；unhinted 39.2%→16.7%（task-level 55.8%→30.3%）；代价是 benign pass 76.1%→65.2%（-10.9 pp 的 solution narrowing）。
- **Solver 角色的必要性（意外 ablation）**：KernelBench 用 reference solution 代替 LLM solver，导致 fixer 的防御悄悄封掉了 torch.cpp_extension.load_inline（提交 CUDA kernel 的标准 API），raw loop 输出 benign pass 一度为 0%；需 post-loop autopatch 手术式放松两处过度防御才恢复到 92–98%（不影响 0% ASR）。

## Strengths & Weaknesses
**亮点**：(1) 16% 的量化审计 + Terminal Wrench 开放数据集本身就是重要贡献，把"benchmark 可 hack"从轶事变成可测量的攻击面；(2) 三角色设计中 solver 是关键洞察——hacker+fixer 双人博弈会单调收紧 verifier 直到误杀合法解，KernelBench 的意外 ablation 恰好实证了这一点；(3) weak-to-strong 结论有部署价值：信息优势（verifier access）+ 覆盖优势（defense pool）可以补偿模型能力差距，意味着不需要最强模型就能加固环境；(4) defense pool 把加固从 per-task 成本摊销为基建成本，task 001 verifier 全部来自其他任务是漂亮的证据。
**局限**：(1) 防御上界受 hacker 能力约束——held-out hint corpus 中人类发现的创造性 exploit 仍有残留（Terminal Bench hinted 只降到 39.4%），作者自己承认对 agent 生成的攻击远比对人类攻击有效；(2) solution narrowing 是实打实的代价（-11 pp benign pass），logistic-regression 例子显示防御会误伤修改目标函数的合法变体解，说明 verifier 加固与解空间开放性存在张力；(3) 部分任务在 verifier 层面根本不可修（Docker 里 shred vs rm -rf 不可区分），需要重设计评测基建；(4) pool 只在共享评测基建内摊销，不产生跨 benchmark 的通用防御。对领域影响：与检测类工作（ImpossibleBench、Hodoscope）互补，把"发现 benchmark 被攻破"推进到"自动修复"，对 RLVR 训练的 reward 可靠性有直接意义。

## Mind Map
```mermaid
mindmap
  root((HackerFixerLoop))
    Problem
      Verifier 脆弱可 hack
      审计 1968 任务 16% 可破
      污染 leaderboard 与 RL 信号
    Method
      三角色循环
        Hacker 攻
        Fixer 补
        Solver 防误杀
      Verifier-aware hacking
      Shared defense pool
    Results
      KernelBench 62%→0%
      Weak-to-strong Pro 76%→0%
      TB unhinted 39%→17%
      代价 benign -11pp
      Terminal Wrench 数据集
```

## Notes
- 与 [[2605-RolloutCards]]（评测报告规则漂移）、[[2604-WebForge]]（anti-cheating 机制内建于生成环境）同属 agent 评测可信性主线：WebForge 在生成时防作弊，本文在事后对抗加固，Rollout Cards 让证据可审计。
- 对 GUI/Web benchmark 的启示：GUI verifier（截图比对、DOM 断言、LLM judge）的攻击面审计尚无对应工作，本文方法论可迁移。
- 值得记住的机制细节：judge 过滤后 75% 的"通过"轨迹是 hack——意味着无 judge 的 pass rate 统计会严重高估任务健壮性。
