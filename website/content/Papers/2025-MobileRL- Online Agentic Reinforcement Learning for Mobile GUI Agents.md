---
title: "MobileRL: Online Agentic Reinforcement Learning for Mobile GUI Agents"
authors: ['Yifan Xu', 'Xiao Liu', 'Xinghan Liu', 'Jiaqi Fu', 'Hanchen Zhang', 'Bohao Jing', 'Shudan Zhang', 'Yuting Wang', 'Wenyi Zhao', 'Yuxiao Dong']
year: 2025
venue: "ArXiv.org"
url: "https://openalex.org/W4416257382"
tags: ["GUI Agent"]
status: pending
date_added: 2026-04-14
---

# MobileRL: Online Agentic Reinforcement Learning for Mobile GUI Agents

## Abstract

Building general-purpose graphical user interface (GUI) agents has become increasingly promising with the progress in vision language models. However, developing effective mobile GUI agents with reinforcement learning (RL) remains challenging due to the heavy-tailed distribution of task difficulty and the inefficiency of large-scale environment sampling. We present an online agentic reinforcement learning framework MobileRL to enhance GUI agents in mobile environments. Its core component is the Difficulty-ADAptive GRPO (ADAGRPO) algorithm. In ADAGRPO, we design difficulty-adaptive positive replay and failure curriculum filtering to adapt the model to different task difficulties. We introduce the shortest-path reward adjustment strategy to reshape rewards concerning the task length in multi-turn agentic tasks. Those strategies jointly stabilize RL training, improve sample efficiency, and generate strong performance across diverse mobile apps and tasks. We apply MOBILERL to two open models (Qwen2.5-VL-7B-Instruct and GLM-4.1V-9B-Base). The resultant MOBILERL-9B model achieves state-of-the-art results in terms of success rates on both AndroidWorld (80.2%) and AndroidLab (53.6%). The MOBILERL framework is open-sourced at: https://github.com/THUDM/MobileRL.

## Source

- URL: https://openalex.org/W4416257382
- Venue: ArXiv.org
