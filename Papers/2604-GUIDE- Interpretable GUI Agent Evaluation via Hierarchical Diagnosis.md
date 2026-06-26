---
title: "GUIDE: Interpretable GUI Agent Evaluation via Hierarchical Diagnosis"
authors: ['Yuwen Zhai', 'Runze Li', 'Liang Wang', 'Nian Shi', 'Liwu Xu', 'Wei Zhang', 'Ran Lin', 'Bo Xu', 'Benlei Cui']
year: 2026
venue: "None"
url: "http://arxiv.org/abs/2604.04399v1"
tags: ["GUI Agent"]
status: pending
date_added: 2026-04-14
---

# GUIDE: Interpretable GUI Agent Evaluation via Hierarchical Diagnosis

## Abstract

Evaluating GUI agents presents a distinct challenge: trajectories are long, visually grounded, and open-ended, yet evaluation must be both accurate and interpretable. Existing approaches typically apply a single holistic judgment over the entire action-observation sequence-a strategy that proves unreliable on long-horizon tasks and yields binary verdicts offering no insight into where or why an agent fails. This opacity limits the utility of evaluation as a diagnostic tool for agent development. We introduce GUIDE (GUI Understanding and Interpretable Diagnostic Evaluation), a framework that decomposes trajectory assessment into three sequential stages mirroring the compositional structure of GUI tasks. Trajectory Segmentation partitions the full trace into semantically coherent subtask units. Subtask Diagnosis evaluates each unit in context, assigning a completion verdict and generating a structured error analysis with corrective recommendations. Overall Summary aggregates per-subtask diagnoses into a task-level judgment. By operating on bounded subtask segments rather than full trajectories, GUIDE mitigates the context overload that degrades existing evaluators as task complexity grows. We validate GUIDE on three benchmarks: an industrial e-commerce dataset of 932 trajectories, AGENTREWARDBENCH spanning five web agent tasks with 1302 trajectories, and AndroidBench for mobile device control. Across all settings, GUIDE substantially outperforms existing evaluators-achieving up to 5.35 percentage points higher accuracy than the strongest baseline-while producing structured diagnostic reports that directly inform agent improvement.

## Source

- URL: http://arxiv.org/abs/2604.04399v1
- Venue: None
