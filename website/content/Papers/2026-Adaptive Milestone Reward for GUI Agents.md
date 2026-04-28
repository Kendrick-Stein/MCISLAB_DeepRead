---
title: "Adaptive Milestone Reward for GUI Agents"
authors: ['Congmin Zheng', 'Xiaoyun Mo', 'Xinbei Ma', 'Qiqiang Lin', 'Yin Zhao', 'Jiachen Zhu', 'Xingyu Lou', 'Jun Wang', 'Zhaoxiang Wang', 'Weiwen Liu']
year: 2026
venue: "arXiv (Cornell University)"
url: "https://openalex.org/W7128864794"
tags: ["GUI Agent"]
status: pending
date_added: 2026-04-14
---

# Adaptive Milestone Reward for GUI Agents

## Abstract

Reinforcement Learning (RL) has emerged as a mainstream paradigm for training Mobile GUI Agents, yet it struggles with the temporal credit assignment problem inherent in long-horizon tasks. A primary challenge lies in the trade-off between reward fidelity and density: outcome reward offers high fidelity but suffers from signal sparsity, while process reward provides dense supervision but remains prone to bias and reward hacking. To resolve this conflict, we propose the Adaptive Milestone Reward (ADMIRE) mechanism. ADMIRE constructs a verifiable, adaptive reward system by anchoring trajectory to milestones, which are dynamically distilled from successful explorations. Crucially, ADMIRE integrates an asymmetric credit assignment strategy that denoises successful trajectories and scaffolds failed trajectories. Extensive experiments demonstrate that ADMIRE consistently yields over 10% absolute improvement in success rate across different base models on AndroidWorld. Moreover, the method exhibits robust generalizability, achieving strong performance across diverse RL algorithms and heterogeneous environments such as web navigation and embodied tasks.

## Source

- URL: https://openalex.org/W7128864794
- Venue: arXiv (Cornell University)
