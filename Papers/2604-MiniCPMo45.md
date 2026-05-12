---
title: "MiniCPM-o 4.5: Towards Real-Time Full-Duplex Omni-Modal Interaction"
authors: []
institute: ["OpenBMB", "Tsinghua University"]
date_publish: 2026-04
venue: arXiv
tags: [VLM]
url: https://arxiv.org/abs/2604.27393
code:
rating: "2"
date_added: 2026-05-12
---
## Summary

9B 参数的全模态模型，提出 Omni-Flow 统一流式框架，将视觉/音频/文本输入输出沿共享时间轴对齐，实现 real-time full-duplex 交互。LLM backbone (Qwen3-8B) 只生成 text token（3-4 tokens/s），语音由轻量 Llama decoder (~0.3B) + CosyVoice flow-matching 合成。TAIL 策略自适应对齐语音播放与交互时间线。<12GB RAM 边缘部署。

## Problem & Motivation

现有全模态模型面临效率与交互性的矛盾：直接生成 speech token 的方式虽然端到端，但效率退化严重（3-4 tokens/s vs 文本的 30+ tokens/s）。此外，真正的 full-duplex 交互需要模型能同时处理输入和输出，而不仅是"全双工"的假象（如 VAD-based 轮流说话）。

## Method

核心设计：

1. **Omni-Flow 统一框架**：将视觉/音频/文本输入输出沿共享时间轴对齐，实现真正的流式处理
2. **Text-only LLM backbone**：Qwen3-8B 只生成 text token（3-4 tokens/s），避免直接生成 speech token 带来的效率退化
3. **Lightweight speech decoder**：Llama decoder (~0.3B) + CosyVoice flow-matching 合成语音，计算开销低
4. **TAIL 策略**：Time-Aware Interleaved Learning，自适应对齐语音播放与交互时间线
5. **Proactive behavior**：在预定义场景下实现主动行为（如打断、澄清）

## Key Results

| 指标 | MiniCPM-o 4.5 | Qwen3-Omni-30B | 备注 |
|:-----|:--------------|:---------------|:-----|
| 参数量 | 9B | 30B | 3.3x 更小 |
| 延迟 | 1.0s chunk | - | 实时翻译场景 |
| RAM | <12GB | - | 边缘部署 |
| AlpacaEval | 3.56 | - | chunk size 1.0s |
| AlpacaEval (0.2s) | 1.22 | - | chunk size 降低时崩溃 |

## Strengths & Weaknesses

**Strengths:**

- **边缘部署友好**：<12GB RAM，9B 参数量适合 mobile/edge 场景
- **效率优化思路清晰**：text-only LLM + lightweight speech decoder 的分离设计避免了直接生成 speech token 的效率问题
- **Omni-Flow 时间轴对齐思想**：统一的流式处理框架有参考价值

**Weaknesses:**

- **Full-duplex 实际成熟度被高估**：1.0s chunk size 的延迟在实时翻译等场景下捉襟见肘，chunk size 从 1.0s 降到 0.2s 时模型几乎崩溃（AlpacaEval 3.56→1.22）
- **Proactive behavior 靠数据驱动**：本质上靠预定义场景的 instruction data 驱动，真正的开放环境主动行为仍是空中楼阁
- **回避关键对比**：论文大篇幅对比同 scale 模型（Qwen3-Omni-30B），却巧妙回避了与 GPT-4o 等闭源模型全双工能力的正面比较
- **学术 novelty 有限**：Omni-Flow 框架设计有参考价值，但 full-duplex 的实际成熟度被高估，9B 做边缘部署的工程亮点大于学术 novelty

## Notes

- Omni-Flow 的时间轴对齐思想本身是好的，但 ablation table 暴露了 chunk size 敏感性问题
- 9B 做边缘部署的工程价值大于学术 novelty
- 与 Qwen3-Omni 的对比不公平——30B vs 9B，scale 差异太大
- 需要全文确认：TAIL 策略的具体实现细节、proactive behavior 的触发机制
