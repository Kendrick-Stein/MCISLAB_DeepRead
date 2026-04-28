---
title: "SeedPolicy: Horizon Scaling via Self-Evolving Diffusion Policy for Robot Manipulation"
authors: ['Youqiang Gui', 'Yuxuan Zhou', 'Shen Cheng', 'Xinyang Yuan', 'Haoqiang Fan', 'Peng Cheng', 'Shuaicheng Liu']
year: 2026
venue: "None"
url: "http://arxiv.org/abs/2603.05117v2"
tags: ["GUI Agent"]
status: pending
date_added: 2026-04-14
---

# SeedPolicy: Horizon Scaling via Self-Evolving Diffusion Policy for Robot Manipulation

## Abstract

Imitation Learning (IL) enables robots to acquire manipulation skills from expert demonstrations. Diffusion Policy (DP) models multi-modal expert behaviors but suffers performance degradation as observation horizons increase, limiting long-horizon manipulation. We propose Self-Evolving Gated Attention (SEGA), a temporal module that maintains a time-evolving latent state via gated attention, enabling efficient recurrent updates that compress long-horizon observations into a fixed-size representation while filtering irrelevant temporal information. Integrating SEGA into DP yields Self-Evolving Diffusion Policy (SeedPolicy), which resolves the temporal modeling bottleneck and enables scalable horizon extension with moderate overhead. On the RoboTwin 2.0 benchmark with 50 manipulation tasks, SeedPolicy outperforms DP and other IL baselines. Averaged across both CNN and Transformer backbones, SeedPolicy achieves 36.8% relative improvement in clean settings and 169% relative improvement in randomized challenging settings over the DP. Compared to vision-language-action models such as RDT with 1.2B parameters, SeedPolicy achieves competitive performance with one to two orders of magnitude fewer parameters, demonstrating strong efficiency and scalability. These results establish SeedPolicy as a state-of-the-art imitation learning method for long-horizon robotic manipulation. Code is available at: https://github.com/Youqiang-Gui/SeedPolicy.

## Source

- URL: http://arxiv.org/abs/2603.05117v2
- Venue: None
