---
title: "GUI-Eyes: Tool-Augmented Perception for Visual Grounding in GUI Agents"
authors: ['Chen Chen', 'Jiawei Shao', 'Dakuan Lu', 'Haoyi Hu', 'Xiangcheng Liu', 'Hantao Yao', 'Wu Liu']
year: 2026
venue: "None"
url: "http://arxiv.org/abs/2601.09770v1"
tags: ["GUI Agent"]
status: pending
date_added: 2026-04-14
---

# GUI-Eyes: Tool-Augmented Perception for Visual Grounding in GUI Agents

## Abstract

Recent advances in vision-language models (VLMs) and reinforcement learning (RL) have driven progress in GUI automation. However, most existing methods rely on static, one-shot visual inputs and passive perception, lacking the ability to adaptively determine when, whether, and how to observe the interface. We present GUI-Eyes, a reinforcement learning framework for active visual perception in GUI tasks. To acquire more informative observations, the agent learns to make strategic decisions on both whether and how to invoke visual tools, such as cropping or zooming, within a two-stage reasoning process. To support this behavior, we introduce a progressive perception strategy that decomposes decision-making into coarse exploration and fine-grained grounding, coordinated by a two-level policy. In addition, we design a spatially continuous reward function tailored to tool usage, which integrates both location proximity and region overlap to provide dense supervision and alleviate the reward sparsity common in GUI environments. On the ScreenSpot-Pro benchmark, GUI-Eyes-3B achieves 44.8% grounding accuracy using only 3k labeled samples, significantly outperforming both supervised and RL-based baselines. These results highlight that tool-aware active perception, enabled by staged policy reasoning and fine-grained reward feedback, is critical for building robust and data-efficient GUI agents.

## Source

- URL: http://arxiv.org/abs/2601.09770v1
- Venue: None
