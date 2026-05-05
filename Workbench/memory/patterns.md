# Patterns

> Memory file for observed patterns in research

## Architectural Patterns

### Pattern 1: Multimodal LLM Core
- Most GUI Agents use VLM/LLM as central reasoning component
- Screen understanding → Planning → Action execution pipeline
- Examples: CogAgent, MobileFlow, SeeClick

### Pattern 2: Hierarchical Planning
- High-level task decomposition + low-level action grounding
- Reduces complexity by separating task-level from action-level
- Examples: MobileUse, AmapAgent

### Pattern 3: Self-Improving Loop
- Collect execution traces → Learn from failures → Improve policy
- Requires memory and reflection mechanisms
- Examples: UI-Genie, Continual GUI Agents

## Evaluation Patterns

### Dataset Types
- Static benchmark datasets (GUIOdyssey, GUIWorld)
- Interactive environments (WebCanvas, mobile simulators)
- Real-world deployment tests

### Metrics
- Task completion rate (primary)
- Action efficiency (steps taken)
- Grounding accuracy

## Research Gaps Patterns

- Few works on cross-platform transfer
- Limited exploration of multi-agent coordination
- Safety/privacy concerns rarely addressed → now emerging as systematic area (VLASafety survey, EVA red-teaming), [[Workbench/logs/2026-04-28]]

---

### [2026-04-28] RL methods show high data efficiency for GUI Agent training

- **observation**: RL-based GUI Agent training (GRPO-style) achieves competitive results with surprisingly small datasets — UI-R1 uses only 136 tasks, ClawGUI shows +6.0% over baseline with rule-based rewards
- **occurrences**: [[Workbench/logs/2026-04-28]]
- **confidence**: low
- **needs_verification**: yes

### [2026-04-28] Evaluation methodology shifting from binary success to multi-dimensional diagnosis

- **observation**: New benchmarks (AutoGUIv2, ProBench, ReVSI) move beyond binary success/failure to process-level evaluation, multi-dimensional capability diagnosis, and systematic failure mode analysis
- **occurrences**: [[Workbench/logs/2026-04-28]], [[Workbench/logs/2026-05-03]] (Claw-Eval-Live 四路证据 triangulation, Visual Generation Taxonomy critique of perceptual-only evaluation)
- **confidence**: medium
- **needs_verification**: no
- **status**: → promoted to insight ([2026-05-03])

### [2026-04-28] VLM capabilities are fragmented across sub-tasks

- **observation**: AutoGUIv2 reveals that different VLMs have complementary strengths — Qwen3-VL excels at grounding while Gemini excels at captioning — suggesting no single model dominates all GUI Agent sub-tasks
- **occurrences**: [[Workbench/logs/2026-04-28]]
- **confidence**: low
- **needs_verification**: yes

### [2026-04-28] Small specialized models can match large models on GUI grounding

- **observation**: GoClick (230M parameters, encoder-decoder architecture) achieves grounding accuracy comparable to much larger VLMs, suggesting grounding may not require general-purpose reasoning capacity
- **occurrences**: [[Workbench/logs/2026-04-28]]
- **confidence**: low
- **needs_verification**: yes

---
*Last distilled: 2026-05-03*

### [2026-05-03] Latent-space agent communication significantly reduces token overhead

- **observation**: Multi-agent systems using latent-space (而非 text-based) communication 可实现 75%+ token reduction，同时保持 accuracy 提升——latent transfer 避免了中间 agent 的文本生成解码开销
- **occurrences**: [[Workbench/logs/2026-05-03]] (RecursiveMAS +8.3% accuracy, 75.6% token reduction)
- **confidence**: low
- **needs_verification**: yes

### [2026-05-03] Production deployment cost becoming primary bottleneck for computer-use agents

- **observation**: Computer-use/GUI agent 研究焦点从"提升成功率"转向"降低部署成本"——Step-level cascade 用 event-driven escalation 实现 74.6% cost reduction，production 视角的 real problem framing
- **occurrences**: [[Workbench/logs/2026-05-03]] (Step-level Optimization), [[Workbench/logs/2026-04-28]] (ClawGUI infrastructure)
- **confidence**: low
- **needs_verification**: yes

### [2026-05-03] Workflow automation on real-world tasks has <70% success rate

- **observation**: Workflow automation benchmark 显示 frontier models 最高 pass rate 仅 66.7%，live Internet long-horizon tasks 仅 44.5%——远未 saturation，真实场景远比 curated benchmark 更难
- **occurrences**: [[Workbench/logs/2026-05-03]] (Claw-Eval-Live 66.7%), [[Workbench/logs/2026-04-28]] (Odysseys 44.5%)
- **confidence**: medium
- **needs_verification**: no