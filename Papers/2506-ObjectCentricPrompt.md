---
title: "CrayonRobo: Object-Centric Prompt-Driven Vision-Language-Action Model for Robotic Manipulation"
authors: ["Xiaoqi Li", "Lingyun Xu", "Mingxu Zhang", "Jiaming Liu", "Yan Shen", "Iaroslav Ponomarenko", "Jiahui Xu", "Liang Heng", "Siyuan Huang", "Shanghang Zhang", "Hao Dong"]
institute: ["School of Computer Science, Peking University", "PKU-Agibot Lab"]
date_publish: 2025-05-04
venue: "CVPR 2025"
tags: [VLA, manipulation, instruction-following]
url: "https://openaccess.thecvf.com/content/CVPR2025/html/Li_Object-Centric_Prompt-Driven_Vision-Language-Action_Model_for_Robotic_Manipulation_CVPR_2025_paper.html"
arxiv_id: "2505.02166"
doi: ""
cite_key: li2025crayonrobo
code: ""
rating: 4
date_added: 2026-06-26
---
## Summary

CrayonRobo 提出一种 object-centric visual-language prompt 接口：在 RGB 图像上用蓝/红/绿/黄 crayon prompt 显式标注 contact point、gripper z-axis、gripper y-axis 和 contact 后 moving direction，并让 VLA 预测 SE(3) contact pose 与 3D movement direction。核心价值不是端到端自动规划，而是把 long-horizon manipulation 拆成可解释的 key-frame prompt sequence，在仿真与真实机器人上验证这种 prompt-driven 控制接口的有效性。

## Problem & Motivation

机器人任务目标可以用 language、goal image 或 goal video 表达，但论文指出三类输入各有问题：language 容易模糊或过长，goal image/video 往往包含 background 和 unrelated object 等冗余细节，generated video 还依赖生成质量。已有 visual prompt 方法更接近作者想要的接口，但 RT-Sketch 只画最终状态，缺少 intermediate key frames；RT-Trajectory 给 end-effector path，却主要提供 position information，缺少 action directional information，长轨迹重叠时也会让 planning 变得混乱。本文要解决的问题是：能否用更简洁、非冗余的 object-centric prompt 同时表达「在哪里接触」「如何接触」和「接触后怎么动」，并把多个 key-frame 串起来完成 long-horizon manipulation。

## Method

CrayonRobo 的输入是一张带 crayon visual prompts 的 RGB 图像和对应 language prompt。颜色语义固定：blue 表示 2D contact point，red 表示 gripper z-axis 2D direction，green 表示 gripper y-axis 2D direction，yellow 表示 contact 后 moving direction；为避免视觉 prompt 重叠造成歧义，language prompt 还写入这些 2D 坐标/方向向量的数值。模型输出 contact point 对应的 3D position、gripper z/y 轴方向，以及可选的 3D moving direction。

训练数据来自 SAPIEN + PartNet-Mobility。作者用 rule-based interaction 记录成功的 3D contact pose、z/y axis direction 和 moving direction，再投影到 2D 生成训练 prompt。模型架构沿用 open-source VLA/ManipLLM 路线：CLIP visual encoder 提取图像特征，LLaMA tokenizer 编码文本，multi-modal projection 对齐两种表示；训练时冻结主干参数，只 fine-tune LLaMA 中注入的 adapters 和 multi-modal projection module。

训练目标把 pose prediction 组织成 language modeling：连续 3D direction 被离散到 100 个 bins，用 Text Supervision Loss 约束输出格式和数值；Orthogonal Loss 约束 z-axis 与 y-axis 的几何正交关系；Projection Loss 把预测 3D direction 重新投影到 2D，与输入的 2D visual prompt 对齐。训练输入按信息量递增设计为 contact-only、contact+z、contact+z+y、contact+z+y+moving direction，使模型能处理不同 prompt 组合。

推理阶段有两种 prompt 生成方式：用户可以手动画 crayon prompt，也可以自动生成。自动流程先用 Grounded-DINO 检测目标 object bounding box 并取中心作为 blue contact point，再生成 32 个均匀方向候选，由 GPT-4 选择 z-axis、y-axis 和 moving direction 对应的线。Long-horizon task 则输入一串 key-frame visual prompts，逐步执行每个 sub-goal；有些 primitive 如 place/move 不需要 yellow moving prompt，rotate 类任务用两个 key-frame pose 表达旋转方向。

## Key Results

- **SAPIEN + PartNet-Mobility manipulation success rate**：作者收集约 10,000 training samples，仿真环境交互约 1,500 object shapes；Appendix 中 seen objects 分为 1,037 training shapes 和 489 testing shapes，unseen categories 有 274 shapes。Table 1 中 Ours(s) 在 seen/unseen AVG 为 **0.80/0.79**，高于 Flowbot3D **0.43/0.38**、ManipLLM **0.51/0.47**、Implicit3D **0.55/0.39**；Ours(f) 为 **0.74/0.72**，高于 replicated RT-Trajectory **0.57/0.52**。
- **Automatic prompt generation**：自动生成 prompt 时 seen/unseen success rate 为 **0.64/0.62**，作者指出 bounding-box center 可能与真实 contact point 不对齐，但模型仍能一定程度修正 prompt noise。多步骤仿真任务（如先 pull door 再 push）达到 **0.69/0.68** seen/unseen。
- **Prompt ablation (Table 2)**：只给 contact point 得到 **0.42/0.37** seen/unseen；加入 z-axis 后为 **0.55/0.50**；再加入 y-axis 为 **0.70/0.68**；完整加入 moving direction 为 **0.74/0.72**。去掉 visual prompt、只保留 language prompt 中的指示信息时为 **0.69/0.68**，说明 visual 与 language prompt 同时存在更强。
- **Loss ablation (Table 4)**：仅 Text Supervision Loss 为 **0.68/0.57**；加入 Orthogonal Loss 为 **0.71/0.70**；再加入 Projection Loss 达到 **0.74/0.72**，支持几何约束和 2D-3D 投影对齐的有效性。
- **Noise robustness (Figure 5)**：direction prompt 加 10% 噪声时约为 **0.73/0.71**，20% 为 **0.70/0.66**，30% 为 **0.66/0.63**，40% 为 **0.56/0.52**；作者认为 30%-40% 已接近人类绘制时明显不合理的方向偏差。
- **Real-world without sim-to-real finetuning (Table 3)**：Franka Emika + RealSense 415 上，手动画 prompt 的 Open trashcan / Open microwave / Lift lid / Wipe table / Heat toaster 成功率分别为 **9/10、7/10、5/5、8/10、3/5**；自动 prompt 分别为 **8/10、6/10、5/5、8/10、2/5**。用首次成功执行的 key frames fine-tune 后，w/o prompt 的 Open microwave 与 Wipe table 分别为 **5/10** 和 **6/10**。

## Strengths & Weaknesses

**已知**：论文的最强证据来自 prompt granularity ablation 和 loss ablation，而不只是主表涨点；contact、axis、moving direction 每一类 prompt 都有可量化增益。方法的 interface 也很清楚：它不是让 VLA 从自然语言里隐式猜动作，而是把 object-centric interaction intent 显式放进图像和文本两种 prompt 中。

**已知**：局限也比较明确。论文承认方法不能直接 avoid obstacles，只建议未来可接入 curobo 这类 collision-free motion planner；failure analysis 中，Open microwave 的 push button step 受过大反作用力影响失败，Heat toaster 的 slide lever step 受 gripper fingers 太短影响，说明当前系统仍受硬件接触条件和 motion planning 约束。

**推测**：这类 prompt-driven VLA 对 embodied agent 的价值更像是一个可控的 action-specification layer，而不是 autonomous task planner。它可能适合把 high-level planner 的中间结果落到 robot action 上，但如果 prompt 需要人手画或依赖 Grounded-DINO + GPT-4 选线，系统能力的一部分被转移到了 prompt generation。

**不知道 / 未报告**：论文正文没有报告 code link、模型权重、推理延迟、prompt 绘制耗时，也没有系统比较人工 prompt 与自动 prompt 在真实世界中的失败类型差异。RT-Trajectory 因代码不可用是作者复现版本，这使 visual-prompt baseline 的可比性依赖复现质量；goal-video baseline AVDC 只报告 generated video task success ratio **10.2%**，不是同表里的完整执行 policy 对比。

## Mind Map

```mermaid
mindmap
  root((CrayonRobo))
    Problem
      Language ambiguous
      Goal image/video redundant
      RT-Sketch lacks key frames
      RT-Trajectory lacks directional action
    Method
      Crayon visual prompts
        Blue contact point
        Red z-axis
        Green y-axis
        Yellow moving direction
      VLA pose prediction
        CLIP visual encoder
        LLaMA adapters
        SE(3) contact pose
      Training losses
        Text supervision
        Orthogonal loss
        Projection loss
      Key-frame execution
        Manual prompt
        Grounded-DINO + GPT-4 auto prompt
    Results
      SAPIEN PartNet-Mobility
        Ours(s) 0.80 seen
        Ours(s) 0.79 unseen
      Prompt ablation
        Full prompt 0.74/0.72
        Contact only 0.42/0.37
      Real world
        No sim-to-real finetuning
        Manual and auto prompts
```

## Notes

对 GUI-agent/VLM 方向的启发：CrayonRobo 的关键不是「画线」本身，而是把 ambiguous goal 转换成 model-interpretable prompt schema，让模型在视觉输入里看到操作目标、在文本输入里看到结构化数值。这与 GUI grounding 里显式标注 target element、drag direction、intermediate waypoint 的问题有相似性，但本文证据只覆盖 robotic manipulation，不能直接外推到 GUI/web agent。

需要继续追问的问题：automatic prompt 的 contact point 来自 bounding-box center，这对 articulated object 未必可靠；如果 prompt generator 出错，VLA 到底是在纠错还是在被错误 prompt 带偏？此外，key-frame sequence 的高层分解目前由人工/外部流程给出，论文没有证明模型能自己发现 bottleneck key frames。
