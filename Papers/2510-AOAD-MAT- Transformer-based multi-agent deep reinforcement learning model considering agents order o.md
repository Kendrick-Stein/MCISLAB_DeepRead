---
title: "AOAD-MAT: Transformer-based multi-agent deep reinforcement learning model considering agents' order of action decisions"
authors: ['Shota Takayama', 'Katsuhide Fujita']
year: 2025
venue: "None"
url: "http://arxiv.org/abs/2510.13343v1"
tags: ["GUI Agent"]
status: pending
date_added: 2026-04-14
---

# AOAD-MAT: Transformer-based multi-agent deep reinforcement learning model considering agents' order of action decisions

## Abstract

Multi-agent reinforcement learning focuses on training the behaviors of multiple learning agents that coexist in a shared environment. Recently, MARL models, such as the Multi-Agent Transformer (MAT) and ACtion dEpendent deep Q-learning (ACE), have significantly improved performance by leveraging sequential decision-making processes. Although these models can enhance performance, they do not explicitly consider the importance of the order in which agents make decisions. In this paper, we propose an Agent Order of Action Decisions-MAT (AOAD-MAT), a novel MAT model that considers the order in which agents make decisions. The proposed model explicitly incorporates the sequence of action decisions into the learning process, allowing the model to learn and predict the optimal order of agent actions. The AOAD-MAT model leverages a Transformer-based actor-critic architecture that dynamically adjusts the sequence of agent actions. To achieve this, we introduce a novel MARL architecture that cooperates with a subtask focused on predicting the next agent to act, integrated into a Proximal Policy Optimization based loss function to synergistically maximize the advantage of the sequential decision-making. The proposed method was validated through extensive experiments on the StarCraft Multi-Agent Challenge and Multi-Agent MuJoCo benchmarks. The experimental results show that the proposed AOAD-MAT model outperforms existing MAT and other baseline models, demonstrating the effectiveness of adjusting the AOAD order in MARL.

## Source

- URL: http://arxiv.org/abs/2510.13343v1
- Venue: None
