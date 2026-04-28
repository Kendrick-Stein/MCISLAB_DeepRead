---
title: "CAPTCHA Solving for Native GUI Agents: Automated Reasoning-Action Data Generation and Self-Corrective Training"
authors: ['Yuxi Chen', 'Haoyu Zhai', 'Chenkai Wang', 'Rui Yang', 'Lingming Zhang', 'Gang Wang', 'Huan Zhang']
year: 2026
venue: "None"
url: "http://arxiv.org/abs/2603.23559v1"
tags: ["GUI Agent"]
status: pending
date_added: 2026-04-14
---

# CAPTCHA Solving for Native GUI Agents: Automated Reasoning-Action Data Generation and Self-Corrective Training

## Abstract

GUI agents are rapidly shifting from multi-module pipelines to end-to-end, native vision-language models (VLMs) that perceive raw screenshots and directly interact with digital devices. Despite rapid progress on general GUI tasks, CAPTCHA solving remains a major challenge. On the other hand, although specialized CAPTCHA solving pipelines exist, they cannot handle general GUI tasks. To address this gap, we introduce ReCAP: a CAPTCHA-capable native GUI agent that can robustly solve modern, interactive CAPTCHA challenges, while preserving their performance as a general GUI agent. We first develop a dynamic CAPTCHA system spanning seven representative CAPTCHA types, designed to stress primitive and complementary capabilities for CAPTCHA solving (e.g., robust OCR under heavy noise and text stylization, fine-grained visual understanding, and precise control). Then, we develop an automated data collection and curation pipeline that generates large-scale CAPTCHA interaction trajectories paired with reasoning traces. As CAPTCHA solving often requires multi-step interaction and recovery from intermediate mistakes, we further leverage failed trajectories to construct self-correction data, training agents to reflect on errors and correct their actions online. Across held-out test sets, ReCAP improves CAPTCHA-solving success from roughly 30\% to 80\%, while maintaining strong performance on general GUI-agent benchmarks.

## Source

- URL: http://arxiv.org/abs/2603.23559v1
- Venue: None
