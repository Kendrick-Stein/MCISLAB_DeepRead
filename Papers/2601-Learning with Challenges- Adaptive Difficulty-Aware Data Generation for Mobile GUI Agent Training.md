---
title: "Learning with Challenges: Adaptive Difficulty-Aware Data Generation for Mobile GUI Agent Training"
authors: ['Linjia Kang', 'Zhimin Wang', 'Yongkang Zhang', 'Duo Wu', 'Jinghe Wang', 'Ming Ma', 'Haopeng Yan', 'Zhi Wang']
year: 2026
venue: "None"
url: "http://arxiv.org/abs/2601.22781v1"
tags: ["GUI Agent"]
status: pending
date_added: 2026-04-14
---

# Learning with Challenges: Adaptive Difficulty-Aware Data Generation for Mobile GUI Agent Training

## Abstract

Large-scale, high-quality interaction trajectories are essential for advancing mobile Graphical User Interface (GUI) agents. While existing methods typically rely on labor-intensive human demonstrations or automated model exploration to generate GUI trajectories, they lack fine-grained control over task difficulty. This fundamentally restricts learning effectiveness due to the mismatch between the training difficulty and the agent's capabilities. Inspired by how humans acquire skills through progressively challenging tasks, we propose MobileGen, a novel data generation framework that adaptively aligns training difficulty with the GUI agent's capability frontier. Specifically, MobileGen explicitly decouples task difficulty into structural (e.g., trajectory length) and semantic (e.g., task goal) dimensions. It then iteratively evaluates the agent on a curated prior dataset to construct a systematic profile of its capability frontier across these two dimensions. With this profile, the probability distribution of task difficulty is adaptively computed, from which the target difficulty for the next round of training can be sampled. Guided by the sampled difficulty, a multi-agent controllable generator is finally used to synthesize high-quality interaction trajectories along with corresponding task instructions. Extensive experiments show that MobileGen consistently outperforms existing data generation methods by improving the average performance of GUI agents by 1.57 times across multiple challenging benchmarks. This highlights the importance of capability-aligned data generation for effective mobile GUI agent training.

## Source

- URL: http://arxiv.org/abs/2601.22781v1
- Venue: None
