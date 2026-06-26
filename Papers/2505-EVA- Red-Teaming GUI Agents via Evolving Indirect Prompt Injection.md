---
title: "EVA: Red-Teaming GUI Agents via Evolving Indirect Prompt Injection"
authors: ['Yijie Lu', 'Tianjie Ju', 'Manman Zhao', 'Xinbei Ma', 'Yuan Guo', 'ZhuoSheng Zhang']
year: 2025
venue: "None"
url: "http://arxiv.org/abs/2505.14289v1"
tags: ["GUI Agent"]
status: pending
date_added: 2026-04-14
---

# EVA: Red-Teaming GUI Agents via Evolving Indirect Prompt Injection

## Abstract

As multimodal agents are increasingly trained to operate graphical user interfaces (GUIs) to complete user tasks, they face a growing threat from indirect prompt injection, attacks in which misleading instructions are embedded into the agent's visual environment, such as popups or chat messages, and misinterpreted as part of the intended task. A typical example is environmental injection, in which GUI elements are manipulated to influence agent behavior without directly modifying the user prompt. To address these emerging attacks, we propose EVA, a red teaming framework for indirect prompt injection which transforms the attack into a closed loop optimization by continuously monitoring an agent's attention distribution over the GUI and updating adversarial cues, keywords, phrasing, and layout, in response. Compared with prior one shot methods that generate fixed prompts without regard for how the model allocates visual attention, EVA dynamically adapts to emerging attention hotspots, yielding substantially higher attack success rates and far greater transferability across diverse GUI scenarios. We evaluate EVA on six widely used generalist and specialist GUI agents in realistic settings such as popup manipulation, chat based phishing, payments, and email composition. Experimental results show that EVA substantially improves success rates over static baselines. Under goal agnostic constraints, where the attacker does not know the agent's task intent, EVA still discovers effective patterns. Notably, we find that injection styles transfer well across models, revealing shared behavioral biases in GUI agents. These results suggest that evolving indirect prompt injection is a powerful tool not only for red teaming agents, but also for uncovering common vulnerabilities in their multimodal decision making.

## Source

- URL: http://arxiv.org/abs/2505.14289v1
- Venue: None
