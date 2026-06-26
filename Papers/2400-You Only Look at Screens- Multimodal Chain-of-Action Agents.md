---
title: "You Only Look at Screens: Multimodal Chain-of-Action Agents"
authors: ['Zhuosheng Zhang', 'Aston Zhang']
year: 2024
venue: "None"
url: "https://openalex.org/W4402670435"
tags: ["GUI Agent"]
status: pending
date_added: 2026-04-14
---

# You Only Look at Screens: Multimodal Chain-of-Action Agents

## Abstract

Autonomous graphical user interface (GUI) agents aim to facilitate task automation by interacting with the user interface without manual intervention.Recent studies have investigated eliciting the capabilities of large language models (LLMs) for effective engagement in diverse environments.To align with the input-output requirement of LLMs, most existing approaches are developed under a sandbox setting where they rely on external tools and application-specific APIs to parse the environment into textual elements and interpret the predicted actions.Consequently, those approaches often grapple with inference inefficiency and error propagation risks.To mitigate the challenges, we introduce Auto-GUI, a multimodal solution that directly interacts with the interface, bypassing the need for environment parsing or reliance on applicationdependent APIs.Moreover, we propose a chainof-action technique-leveraging a series of intermediate previous action histories and future action plans-to help the agent decide what action to execute.We evaluate our approach on a new device-control benchmark AITW with 30K unique instructions, spanning multi-step tasks such as application operation, web searching, and web shopping.Experimental results show that Auto-GUI achieves state-of-the-art performance with an action type prediction accuracy of 90% and an overall action success rate of 74%.

## Source

- URL: https://openalex.org/W4402670435
- Venue: None
