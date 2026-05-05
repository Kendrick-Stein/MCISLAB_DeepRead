# SnapGuard: Lightweight Prompt Injection Detection for Screenshot-Based Web Agents

> Du, Mengyao; Fang, Han; Ma, Haokai; Chen, Jiahao; Xu, Kai; Yin, Quanjun; Chang, Ee-Chien
> National University of Defense Technology; University of Science and Technology of China; National University of Singapore; Zhejiang University
> arXiv:2604.25562v1 [cs.CR] 28 Apr 2026
> [link](http://arxiv.org/abs/2604.25562v1)

## Abstract

Web agents have emerged as an effective paradigm for automating interactions with complex web environments, yet remain vulnerable to prompt injection attacks that embed malicious instructions into webpage content to induce unintended actions. This threat is further amplified for screenshot-based web agents, which operate on rendered visual webpages rather than structured textual representations, making predominant text-centric defenses ineffective. Although multimodal detection methods have been explored, they often rely on large vision-language models (VLMs), incurring significant computational overhead. The bottleneck lies in the complexity of modern webpages: VLMs must comprehend the global semantics of an entire page, resulting in substantial inference time and GPU memory usage. This raises a critical question: can we detect prompt injection attacks from screenshots in a lightweight manner? In this paper, we observe that injected webpages exhibit distinct characteristics compared to benign ones from both visual and textual perspectives. Building on this insight, we propose SnapGuard, a lightweight yet accurate method that reformulates prompt injection detection as multimodal representation analysis over webpage screenshots. SnapGuard leverages two complementary signals: a visual stability indicator that identifies abnormally smooth gradient distributions induced by malicious content, and action-oriented textual signals recovered via contrast-polarity reversal. Extensive evaluations across eight attacks and two benign settings demonstrate that SnapGuard achieves an F1 score of 0.75, outperforming GPT-4o-prompt while being 8x faster (1.81s vs. 14.50s) and introducing no additional memory overhead.

## Key Contributions

1. Investigate distinctive visual and textual characteristics of injected webpages relative to benign ones, showing these signals can support prompt injection detection from screenshots
2. Propose SnapGuard, a lightweight detection method combining visual stability indicator with action-oriented textual cues without relying on large VLMs for full-page semantic understanding
3. Extensive evaluation on benchmark datasets with eight prompt injection attacks and two benign settings, achieving F1=0.75 (vs. GPT-4o-prompt 0.71) with 1.81s runtime and zero memory overhead

## Method

### Overview

SnapGuard reformulates prompt injection detection as multimodal representation analysis over webpage screenshots, combining:
- **Visual Stability Indicator (VSI)**: captures structural anomalies at visual level
- **Textual Signal Extraction**: contrast-polarity reversal + OCR + action-oriented pattern detection

### Visual Stability Indicator (VSI)

Key insight: malicious content designed to influence agent actions tends to introduce spatially diffuse perturbations that suppress local structural variation, in contrast to benign content which exhibits diverse local structures and gradient distributions.

Given screenshot `x`, VSI computes variance of gradient magnitudes:
- `φ(x) = E[||∇x||²] - (E[||∇x||])²`
- Malicious injections produce abnormally low `φ(x)` values (spatially uniform screenshots)
- Threshold `τ` determined by fixing FPR at predefined level `α` on benign dataset

Computational cost: `O(HW)` time, no learnable parameters.

### Textual Signal Extraction

#### Contrast-Polarity Reversal (CPR)
Preprocessing to enrich feature contrast of textual regions:
- Selectively invert near-white regions (threshold `γ=240`)
- Preserve semantic content while improving visibility for text extraction

#### Text Extraction
- Apply OCR on both original and inverted images: `T(x) = O(x) ∪ O(I(x))`
- Lightweight OCR systems preferred for efficiency

#### Action-Oriented Pattern Detection (APD)
Identify functional intent rather than surface lexical form:
- Interaction triggers
- Credential requests
- Link invitations
- Control-override instructions
- Taxonomy is extensible, inherently interpretable

## Evaluation

### Setup
- Eight prompt injection attacks: WebInject, Pop-up, WASP, VWA-Adv, EIA, VPI-Bench, REDTEAM-CUA, classic attacks
- Two benign settings: normal webpage screenshots
- Baselines: Embedding-I, JailGuard, GPT-4o-prompt, LLaVA-1.5-7B, LLaVA-1.5-7B-ft

### Main Results

| Method | FPR | TPR | F1 | Time | Memory |
|--------|-----|-----|-----|------|--------|
| SnapGuard | 0.09 | 0.66 | 0.75 | 1.81s | 0 |
| GPT-4o-prompt | 0.00 | 0.55 | 0.71 | 14.50s | High |
| Embedding-I | - | 0.44 | 0.52 | - | - |
| JailGuard | 0.28 | 0.08 | - | - | - |

### Ablation

| Variant | TPR | FPR | F1 |
|---------|-----|-----|-----|
| Full | 0.66 | 0.09 | 0.75 |
| w/o VSI | 0.49 | 0.05 | 0.56 |
| w/o CPR | 0.57 | 0.08 | 0.64 |
| w/o APD | 0.37 | 0.18 | 0.56 |

- APD plays decisive role: removing it causes both lower recall and higher FPR
- VSI and CPR provide supporting signals for visual/textual cues

### Robustness

- Robust to different OCR/VLM extraction interfaces (Tesseract variants, LLaVA, Qwen3-VL, GPT-4o)
- OCR-based pipelines: 1.8s time, stable F1
- VLM-based: higher F1 (0.76) but 15-16s time
- Robust to Gaussian noise perturbations: maintains ~0.8 F1 even under strong noise

## Limitations

1. F1=0.75 leaves 25% detection gap - not production-ready for high-security scenarios
2. VSI relies on assumption that malicious content suppresses local structural variation - may not hold for all attack types
3. APD uses rule-based pattern matching - may miss novel attack patterns or adversarial text obfuscation
4. OCR-based extraction may fail on visually complex/stylized text
5. No evaluation on real-world agent deployments or end-to-end agent safety

## Personal Notes

- 方法确实 lightweight，但 F1 只有 0.75 对于安全场景来说差距太大
- VSI 的"梯度方差"假设是否成立需要更多验证 - 攻击者完全可以设计保持梯度结构的注入
- 与 GPT-4o-prompt 对比有点不公平：GPT-4o 用的是 prompt 方式而非专门优化的检测器
- 真正的价值在于"lightweight + screenshot-based"这个定位，但代价是检测精度不足
- text-based defense 在 screenshot setting 下失效这个 observation 是有价值的 insight

## Tags

#PromptInjection #WebAgent #Security #ScreenshotBased #VLM #Detection #Lightweight