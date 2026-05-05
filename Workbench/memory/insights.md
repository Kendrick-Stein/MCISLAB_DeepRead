# Insights

> Memory file for distilled research insights

## Key Insights

- GUI Agent field is rapidly evolving with 2024-2025 seeing significant advances
- Most systems use multimodal LLMs as the core reasoning engine
- Evaluation benchmarks vary significantly (WebCanvas, GUIOdyssey, etc.)

## Method Observations

- Action grounding is a core challenge across approaches
- Some systems use coordinate-based actions, others use semantic/element-based
- Self-improving agents (UI-Genie) show promise for continual learning

## Performance Insights

- Dataset quality significantly impacts agent performance
- Screen understanding (OCR, element detection) is a bottleneck
- Cross-app transfer remains challenging

---

*Last distilled: 2026-05-03*

### [2026-05-03] GUI Agent evaluation shifting from binary success to process-level multi-dimensional diagnosis

- **claim**: GUI Agent/Workflow automation benchmark 正从 binary success/failure 演进为 process-level evaluation、multi-dimensional capability diagnosis、和 systematic failure mode analysis——这种 shift 是 field mature 的必要阶段
- **evidence**: 
  - [[Workbench/logs/2026-04-28]] (AutoGUIv2 multi-dimensional, ReVSI frame budget variant)
  - [[Workbench/logs/2026-05-03]] (Claw-Eval-Live 四路证据 triangulation, Visual Generation Taxonomy critique of perceptual-only metrics)
  - [[Workbench/logs/2026-05-04]] (AutoGUI-v2 VLM dichotomy: grounding vs captioning 能力分离，irregular region + complex interaction 失败分析，plausible distractors trick 模型)
- **confidence**: medium (↑ from low，AutoGUI-v2 提供 dichotomy + failure mode 分析的细粒度 evidence)
- **source**: cross-validation
- **impact**: GUI Agent benchmark design，evaluation protocol 标准化，model selection（开源 grounding 强，商业 captioning 强）
- **status**: validated (↑ from provisional，AutoGUI-v2 的 systematic failure mode 分析证实 multi-dimensional diagnosis 的必要性)

### [2026-05-04] VLM grounding vs captioning capability dichotomy

- **claim**: Open-source models fine-tuned on agent data（Qwen3-VL）在功能性 grounding（"where"）上超越商业模型，但商业模型（Gemini-2.5-Pro）在功能性 captioning（"what"）上更强——说明 fine-tuning 的 value proposition 对 grounding task 有显著增益，但 deep functional understanding（transition logic、uncommon actions）仍是所有模型的短板
- **evidence**: [[Papers/2604-AutoGUIv2]] (AutoGUI-v2 benchmark evaluation on 2,753 tasks across 6 OS)
- **confidence**: medium
- **source**: single-paper
- **impact**: Model selection for GUI Agent（开源模型更适合 grounding-heavy task，商业模型更适合 reasoning-heavy task），training strategy（fine-tuning on agent data 对 grounding 有利）
- **status**: provisional