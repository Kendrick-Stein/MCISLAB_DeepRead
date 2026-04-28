---
title: "OmniActor: A Generalist GUI and Embodied Agent for 2D&3D Worlds"
authors: ['Longrong Yang', 'Zhixiong Zeng', 'Yufeng Zhong', 'Jing Huang', 'Liming Zheng', 'Lei Chen', 'Haibo Qiu', 'Zequn Qin', 'Lin Ma', 'Xi Li']
year: 2025
venue: "None"
url: "http://arxiv.org/abs/2509.02322v1"
tags: ["GUI Agent"]
status: pending
date_added: 2026-04-14
---

# OmniActor: A Generalist GUI and Embodied Agent for 2D&3D Worlds

## Abstract

Multimodal large language models are evolving toward multimodal agents capable of proactively executing tasks. Most agent research focuses on GUI or embodied scenarios, which correspond to agents interacting with 2D virtual worlds or 3D real worlds, respectively. However, many complex tasks typically require agents to interleavely interact with these two types of environment. We initially mix GUI and embodied data to train, but find the performance degeneration brought by the data conflict. Further analysis reveals that GUI and embodied data exhibit synergy and conflict at the shallow and deep layers, respectively, which resembles the cerebrum-cerebellum mechanism in the human brain. To this end, we propose a high-performance generalist agent OmniActor, designed from both structural and data perspectives. First, we propose Layer-heterogeneity MoE to eliminate the conflict between GUI and embodied data by separating deep-layer parameters, while leverage their synergy by sharing shallow-layer parameters. By successfully leveraging the synergy and eliminating the conflict, OmniActor outperforms agents only trained by GUI or embodied data in GUI or embodied tasks. Furthermore, we unify the action spaces of GUI and embodied tasks, and collect large-scale GUI and embodied data from various sources for training. This significantly improves OmniActor under different scenarios, especially in GUI tasks. The code will be publicly available.

## Source

- URL: http://arxiv.org/abs/2509.02322v1
- Venue: None
