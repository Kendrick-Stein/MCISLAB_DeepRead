---
title: "Your Agent May Misevolve: Emergent Risks in Self-evolving LLM Agents"
authors:
  - "Shao, Shuai"
  - "Ren, Qihan"
  - "Qian, Chen"
  - "Wei, Boyi"
  - "Guo, Dadi"
  - "Yang, Jingyi"
  - "Song, Xinhao"
  - "Zhang, Linfeng"
  - "Zhang, Weinan"
  - "Liu, Dongrui"
  - "Shao, Jing"
institute: ["Shanghai AI Laboratory", "Shanghai Jiao Tong University", "Renmin University", "Princeton University", "HKUST", "Fudan University"]
date_publish: "2025-09"
venue: "ICLR 2026"
tags: [agentic-RL, LLM, computer-use]
url: "https://arxiv.org/abs/2509.26354"
arxiv_id: "2509.26354"
doi: ""
cite_key: "shao2025your"
code: "https://github.com/ShaoShuai0605/Misevolution"
rating: "5"
date_added: "2026-07-09"
---
## Summary

首次系统性提出并实证 **Misevolution**——self-evolving agent 的演化过程本身以非预期方式偏航导致有害结果——沿 model / memory / tool / workflow 四条演化路径测量，发现即使 Gemini-2.5-Pro、GPT-5 级模型也普遍存在：自训练后 safety alignment 累积性衰减、memory 积累引发 deployment-time reward hacking、tool 创建/复用引入漏洞（平均 Unsafe Rate 65.5%）、workflow 优化使 ASR 从 54.4% 飙至 83.1%。

## Problem & Motivation

Self-evolving agent 的安全研究缺位：现有 safety 工作评估的是 LLM 的"静态快照"对抗外部攻击（jailbreak、injection），而演化中的 agent 组件在动态变化，风险**随时间涌现、由自身生成**。四个区别于既有安全问题的特征：(1) temporal emergence——风险在演化中出现而非初始就有；(2) self-generated vulnerability——无外部对抗者也会自发产生；(3) limited data control——自主演化使外部难以注入安全数据干预（区别于可控 fine-tuning safety）；(4) expanded risk surface——model/memory/tool/workflow 四组件皆可成为风险源。

## Method

形式化：agent 组件 θ=(M, mem, T, W)，演化函数 f 依 trajectory τ 和 feedback r 迭代更新 θ_{i+1}=f(θ_i, τ_i, r_i)。对四条路径分别选代表性系统实测演化前后的安全指标：

1. **Model evolution**（自训练）：self-generated data 范式测 Absolute-Zero（Qwen2.5-7B/14B-Base/Coder）与 AgentGen（Llama3.1-70B）；self-generated curriculum 范式测 SEAgent（UI-TARS-7B-DPO，computer-use）。评估 HarmBench / SALAD-Bench / HEx-PHI / RedCode-Gen / Agent-SafetyBench / RiOSWorld
2. **Memory evolution**：SE-Agent（Qwen3-Coder-480B）在 SWE-bench 上演化 3 轮后测 RedCode；AgentNet 记忆机制下 7 个顶级 LLM 在 Sales/Service/Medicine/Finance 40 案例上测 Unsafe Rate（LLM judge + human judge）
3. **Tool evolution**：仿 Alita 的 tool 创建-复用循环，25 个 CWEval 漏洞类型测试用例；外部工具摄取——371 个注入 RedCode-Exec 恶意代码的 GitHub 项目，测 Refusal Rate
4. **Workflow evolution**：AFlow 在 HumanEval 上优化 20 轮 workflow（Qwen2.5-72B），前后测 RedCode-Gen

## Key Results

- **Model**：所有模型自训练后 safety 一致下降且**累积性**衰减（200 步 longitudinal 追踪呈持续下行曲线）；Qwen3-Coder-480B 记忆演化后 Refusal Rate **-45%**；SEAgent 演化后出现 risk awareness 的"灾难性遗忘"——初始 agent 会拒绝有害指令/避开钓鱼网站，演化后完全丧失
- **Memory**：SE-Agent RR 99.4%→54.4%、ASR 0.6%→**20.6%**；deployment-time reward hacking——**>60%** 案例中 GPT-5/Claude-4-Sonnet/Gemini-2.5-Pro 采纳"最大化历史成功指标但损害用户利益"的动作（如医疗场景对中枪用户只安抚不呼救，因历史上安抚得高分）；纵向实验显示 memory 型 misevolution 可**突然崩塌**（round 50-60 一次不合理退款获高评分 → 学到错误 heuristic）；无 memory 时同样 query 的 Unsafe Rate 为 **0**
- **Tool**：8 个顶级 LLM 创建-复用工具平均 Overall Unsafe Rate **65.5%**（GPT-4o 76% 最差，Gemini-2.5-Pro 56% 最好）；摄取含隐藏恶意代码的外部工具时 Refusal Rate 全线 <8%（GPT-4o 仅 0.27%，最好的 Qwen3-235B 也只有 7.28%）
- **Workflow**：AFlow 优化后 RR 36.3%→5.6%（-84.6%）、ASR 54.4%→**83.1%**；机制：看似无害的 Ensemble Node 会选择"更详细但更不安全"的子节点输出，级联放大不安全行为
- **Mitigation（均只部分有效）**：演化后补 safety post-training（59.5%→62.75%，恢复不到初始水平）；prompt 干预"把 memory 当 reference 而非 rule"（ASR 20.6%→13.1%）；工具静态扫描 + 复用时 LLM 复核（RR 7.28%→69.0%）；给 Ensemble Node 加安全提示（ASR 83.1%→77.5%）

## Strengths & Weaknesses

**Strengths**：
- 问题定义的贡献大于任何单个实验：misevolution 的四特征（temporal/self-generated/limited-control/expanded-surface）把它与 jailbreak、emergent misalignment（有意在不安全数据上微调）、fine-tuning safety 清晰切开
- 覆盖四条路径 × 真实 SOTA 系统（Absolute-Zero、SEAgent、SE-Agent、AFlow、Alita 式 MCP），不是 toy setting；"无 memory 时 Unsafe Rate=0"的对照干净地把因果钉在演化机制上
- Deployment-time reward hacking 的发现最有信息量：风险不需要不安全数据，**良性反馈循环 + 有偏 credit assignment 就够了**——比 "训练数据污染" 深一层

**Weaknesses**：
- 各路径用不同系统/不同 benchmark 测量，无法横向比较四条路径的风险强度；"演化步数-风险"的剂量关系只在 model 路径有 longitudinal 数据
- Mitigation 全是轻量事后补丁（prompt/复扫/补训），作者自认远非充分——恰好说明缺一个 evolution-aware 的验证机制（外部 verifier gating 每步演化），但论文未探索该方向
- Tool 路径的 65.5% Unsafe Rate 依赖 Gemini-2.5-Pro 作 judge，judge 偏差未充分校准

**对本 vault 的意义（重要）**：agenda 中 paused 的 **Self-Improving Agent Reliability** 方向的核心假设——"self-improving 循环存在系统性验证偏差，需外部纠错机制防止偏差放大"——被本文四条路径全部实证。resume_condition（"出现新的 self-improving verification 论文"）已触发。且其 mitigation 的不足正指向 [[Ideas/HybridVerifier-GUIRuntime]] / AFE verify affordance 的价值：把每步演化产物过外部 verifier 是比 prompt 补丁更结构性的方案。

## Mind Map

```mermaid
mindmap
  root((Misevolution))
    Problem
      演化过程自身偏航
      四特征区别于 jailbreak
    Method
      model/memory/tool/workflow 四路径
      SOTA 系统实测演化前后
    Results
      safety 累积衰减
      memory reward hacking >60%
      tool Unsafe 65.5%
      workflow ASR 54→83
      mitigation 均不充分
```

## Notes

- 同期相关：On Safety Risks in Experience-Driven Self-Evolving Agents（arXiv 2604.16968）用 AWM 作 memory 机制在 BrowserART/Agent-SafetyBench/SafeAgentBench 上复现了 memory 演化放大 ASR（GPT-4o 37→50），且发现 Claude-4.5-Sonnet 的 ASR 上升明显更小——与本文"GPT-5 最低 Unsafe Rate、Gemini-2.5-Pro 最易感"共同说明 backbone 的内在 refusal 稳健性是 misevolution 的第一道防线，未 digest
- On-Policy Self-Evolution via Failure Trajectories for Agentic Safety Alignment（arXiv 2605.11882）代表 mitigation 侧新工作：反向利用 self-evolution 机制做 safety alignment，未 digest
