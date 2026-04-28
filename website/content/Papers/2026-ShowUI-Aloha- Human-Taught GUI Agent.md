---
title: "ShowUI-Aloha: Human-Taught GUI Agent"
authors: ['Yichun Zhang', 'Xiangwu Guo', 'Yauhong Goh', 'Jessica Hu', 'Zhiheng Chen', 'Xin Eric Wang', 'Difei Gao', 'Mike Zheng Shou']
year: 2026
venue: "ArXiv.org"
url: "https://openalex.org/W7124117737"
tags: ["GUI Agent"]
status: pending
date_added: 2026-04-14
---

# ShowUI-Aloha: Human-Taught GUI Agent

## Abstract

Graphical User Interfaces (GUIs) are central to human-computer interaction, yet automating complex GUI tasks remains a major challenge for autonomous agents, largely due to a lack of scalable, high-quality training data. While recordings of human demonstrations offer a rich data source, they are typically long, unstructured, and lack annotations, making them difficult for agents to learn from.To address this, we introduce ShowUI-Aloha, a comprehensive pipeline that transforms unstructured, in-the-wild human screen recordings from desktop environments into structured, actionable tasks. Our framework includes four key components: A recorder that captures screen video along with precise user interactions like mouse clicks, keystrokes, and scrolls. A learner that semantically interprets these raw interactions and the surrounding visual context, translating them into descriptive natural language captions. A planner that reads the parsed demonstrations, maintains task states, and dynamically formulates the next high-level action plan based on contextual reasoning. An executor that faithfully carries out these action plans at the OS level, performing precise clicks, drags, text inputs, and window operations with safety checks and real-time feedback. Together, these components provide a scalable solution for collecting and parsing real-world human data, demonstrating a viable path toward building general-purpose GUI agents that can learn effectively from simply observing humans.

## Source

- URL: https://openalex.org/W7124117737
- Venue: ArXiv.org
