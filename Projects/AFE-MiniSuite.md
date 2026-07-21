---
title: "AFE-MiniSuite: Agent-Facing Web Runtime Affordance 的因果消融"
tags: [gui-agent, web-agent, computer-use, environment, agent-facing-runtime]
status: active
date_started: "2026-07-21"
---
## Goal

验证 agenda primary direction（Agent-Facing Environment Runtime）的核心假设：把环境后台已有的 state / map / rollback / verifier 能力以 task-agnostic、non-oracle 的 agent-facing affordance 暴露给 frozen web agent，能在 zero-training 条件下显著提升 task success 与 wrong-turn recovery、降低 false completion，且该收益不能被 prompt-only baseline（C2）或 evaluator-only oracle（C2.5）复现。实验设计已冻结于 [[Experiments/2026-06-25-AgentFacing-WebRuntime]]（C0–C7 九条件对照），本项目负责落地执行。

## 执行计划

竞争窗口在收窄（Crab 已做 sandbox 域 agent-facing rollback、AgenticExplorationSystems 表明系统社区入场），目标 6–8 周内出 Web-only 因果结论。

| Milestone | 内容 | 时长 |
|:--|:--|:--|
| **M0 substrate 决策** | 确认环境底座：WebHarbor mirror（开源可用性待核查）vs CUA-Gym-Hub mock apps vs 自建 3 个轻量 self-hosted app（shopping / booking / issue-tracker，Flask+SQLite 级别即可——backend verifier 与 checkpoint 只需 DB snapshot）。判据：全栈状态 fork 的实现成本与保真度 | 1 周 |
| M1 affordance adapter | `observe_state()` / `get_world_map()` / `list_affordances()` / `checkpoint()·restore()` / `verify_probe()` / `guard()` 六接口 + leak/shortcut 埋点；observe 返回 schema 参照 [[Papers/2606-OpenRath]] Session 契约 | 2 周 |
| M2 任务集 | 40–60 任务 × backend verifier × partial checkpoints；hidden verifier 与 agent-safe probe 三层分离 | 1–2 周 |
| M3 全量 rollout | 9 条件 × 任务 × 3 seeds，单一 frozen 基座 + 固定 scaffold；bootstrap CI + per-affordance ablation delta | 1–2 周 |
| M4 falsification 分析 | C7 vs C2 / C2.5 主对照；leak rate、shortcut rate 审计；三种否证情形各有预注册处理路径（见实验文件 Next Steps） | 1 周 |

## 关键依赖（需 Supervisor 确认）

- **基座模型与预算**：单一 frontier VLM，9 条件 × ~50 任务 × 3 seeds ≈ 1350 rollouts × 长程 step 数——API 成本需要预算上限。
- **WebHarbor / CUA-Gym artifact 可用性**：若均不可得，M0 直接走自建轻量 app 路线（成本可控，且全栈 fork 保真度反而最高）。

## Papers

- [[Papers/2600-WebHarbor]] / [[Papers/2606-CUAGym]] — 候选环境底座
- [[Papers/2412-BrowserGymAgentLab]] — harness 与 observation/action API
- [[Papers/2604-Crab]] — sandbox 域 agent-facing rollback 先例（只测效率不测 success，本实验补 success 因果）
- [[Papers/2606-PolicyGuard]] / [[Papers/2602-VAGEN]] — verify affordance 的精度边界参照（judge/RM 70–85% 区间）
- [[Papers/2606-OpenRath]] — observe affordance 的接口工程参照

## Ideas

- [[Ideas/AgentFacing-WebRuntime]]（validated, 18/25）— 底层 idea
- [[Ideas/HybridVerifier-GUIRuntime]]（18/25）— verify affordance 成立后的合并方向

## Progress Log

- 2026-07-21: 立项（Supervisor 指令）。实验设计沿用 [[Experiments/2026-06-25-AgentFacing-WebRuntime]] v2026-06-26，不改 C0–C7 结构；第一行动项 = M0 substrate 决策。
- 2026-07-21: **M0-1 完成**——两候选均开源可用。CUA-Gym-Hub（github.com/xlang-ai/CUA-Gym，Apache 2.0）：94 mock web apps + 16 desktop apps，HTTP `/go` `/post` `/state` 端点原生支持 state injection/retrieval（= exact checkpoint/restore），每任务带 `initial_setup.py` + `reward.py` 程序化 verifier。WebHarbor（github.com/aiming-lab/WebHarbor，**license 未标明**）：docker image `battalion7244/webharbor:latest` 含 15 个 WebVoyager 网站 mirror（Amazon/Booking/GitHub 等，全栈 auth+DB），控制面 `/reset/<site>` 亚秒级 reset，但 episode 中途 checkpoint 需容器/DB 级快照自行实现。**M0 初步倾向**：CUA-Gym-Hub 为主 substrate（fork 保真度最高、verifier 现成、license 干净），WebHarbor 做 realism transfer 对照；自建路线取消。

## TODOs

- [x] M0-1: 核查 WebHarbor / CUA-Gym-Hub 开源 artifact 可用性（代码、docker image、license）✅ 2026-07-21，两者均可用，详见 Progress Log
- [ ] M0-2: 本地拉起 CUA-Gym-Hub 2-3 个 mock app，实测 `/state` get→set 往返的状态等价性（fork fidelity 冒烟测试）
- [ ] M0-3: substrate 决策报告 → 冻结 M1 接口设计
- [ ] 与 Supervisor 确认基座模型与 API 预算上限

## Results & Findings

## Notes

- 差异化聚焦三条剩余空白：web 全栈状态 fork、success/recovery 因果增益（含 prompt-only 强对照）、affordance 组合消融。
- 与 [[Projects/MismatchTriage]] 共享 checkpoint/restore 基建思路；若 C5 rollback affordance 成立，其 recovery 数据可反哺 MismatchTriage 的 web 域扩展。
