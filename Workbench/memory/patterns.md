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
- **occurrences**: [[Workbench/logs/2026-04-28]]
- **confidence**: low
- **needs_verification**: yes

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
*Last distilled: 2026-04-28*