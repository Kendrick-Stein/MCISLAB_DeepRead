---
title: "Android in the Zoo: Chain-of-Action-Thought for GUI Agents"
authors: ['Jiwen Zhang', 'Jihao Wu', 'Teng Yihua', 'Minghui Liao', 'Nuo Xu', 'Xiao Xiao', 'Zhongyu Wei', 'Duyu Tang']
year: 2024
venue: "None"
url: "https://openalex.org/W4404792858"
tags: ["GUI Agent"]
status: pending
date_added: 2026-04-14
---

# Android in the Zoo: Chain-of-Action-Thought for GUI Agents

## Abstract

Large language model (LLM) leads to a surge of autonomous GUI agents for smartphone, which completes a task triggered by natural language through predicting a sequence of actions of API.Even though the task highly relies on past actions and visual observations, existing studies typically consider little semantic information carried out by intermediate screenshots and screen operations.To address this, this work presents Chain-of-Action-Thought (dubbed CoAT), which takes the description of the previous actions, the current screen, and more importantly the action thinking of what actions should be performed and the outcomes led by the chosen action.We demonstrate that, in a zero-shot setting upon three off-the-shelf LMMs, CoAT significantly improves the action prediction compared to previous proposed context modeling.To further facilitate the research in this line, we construct a dataset Android-In-The-Zoo (AITZ), which contains 18,643 screen-action pairs together with chainof-action-thought annotations.Experiments show that fine-tuning a 1B model (i.e.AUTO-UI-base) on our AITZ dataset achieves on-par performance with CogAgent-Chat-18B.

## Source

- URL: https://openalex.org/W4404792858
- Venue: None
