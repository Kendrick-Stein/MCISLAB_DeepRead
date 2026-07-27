---
title: "WebAgent RL 训练方法对比：采样、输入输出与 Loss 公式逐篇核对"
date: 2026-07-27
tags: [web-agent, agentic-RL, report]
---

# WebAgent RL 训练方法对比：采样、输入输出与 Loss 公式

> **数据来源说明**：所有公式均逐字抄自论文原文（arXiv LaTeX 源码或官方 HTML；WebGym 无 arXiv 版，公式转写自 CVF PDF 渲染版并经交叉核对）。论文没写的内容（如某些超参数值）明确标注"原文未披露"，不做编造。面向 RL 初学者写作，每个公式都配大白话解释。

---

## 0. 先认识四个"标准零件"

这些论文的 loss 都是由下面四个零件拼出来的。先看懂零件，后面每篇只需要看"它改了哪里"。

### 零件 1：概率比值 + 截断（PPO clip）

$$\rho = \frac{\pi_\theta(a \mid s)}{\pi_{\text{old}}(a \mid s)}, \qquad \min\Big(\rho \cdot A,\ \text{clip}(\rho,\ 1-\epsilon,\ 1+\epsilon)\cdot A\Big)$$

**大白话**：$\pi_\theta$ 是正在更新的模型，$\pi_{\text{old}}$ 是采数据时的旧模型。$\rho$ 衡量"新模型生成这个 token 的概率相对旧模型变了多少"。$A$ 是这个 token 的"好坏分"（正 = 鼓励，负 = 抑制）。clip 把 $\rho$ 限制在 $[1-\epsilon, 1+\epsilon]$ 窗口内，再取 min——效果是**每次更新对单个 token 概率的改动幅度有上限**，防止一步改太猛把模型改坏。几乎所有 GRPO/PPO 方法都用这个零件。

### 零件 2：组内归一化的好坏分（GRPO advantage）

$$A_i = \frac{r_i - \text{mean}(r_1,\dots,r_G)}{\text{std}(r_1,\dots,r_G)}$$

**大白话**：同一个任务让模型试 $G$ 次得到 $G$ 条轨迹，各自的分数 $r_i$（通常成功 1 / 失败 0）减去组平均、再除以组内波动。结果是"这条轨迹比同组同伴好多少"：全组都成功或都失败时分子为 0，学不到东西——所以很多论文要专门处理"全对/全错的组"。**在线方法里，整条轨迹的所有 token 共用同一个 $A_i$**（不区分轨迹内哪步好哪步坏）。

### 零件 3：KL 正则（别跑太远）

在 loss 里加一项惩罚 $\beta\, D_{\text{KL}}(\pi_\theta \,\|\, \pi_{\text{ref}})$，衡量新模型和参考模型（通常是训练起点）的输出分布差多远。**大白话**：给模型拴根绳子，防止为了刷分把原有能力练没了。注意：不少论文（ARPO、AsyncWebRL、OpenWebRL）实测后**干脆去掉了**这一项。

### 零件 4：DPO（好坏配对）

$$\mathcal{L}_{\text{DPO}} = -\mathbb{E}\left[\log \sigma\Big(\beta \log\frac{\pi_\theta(a^w \mid s)}{\pi_{\text{ref}}(a^w \mid s)} - \beta \log\frac{\pi_\theta(a^l \mid s)}{\pi_{\text{ref}}(a^l \mid s)}\Big)\right]$$

**大白话**：不在线试错。给定同一个局面 $s$ 下的一个好动作 $a^w$ 和一个坏动作 $a^l$，让模型"相对参考模型提高好动作的概率、压低坏动作的概率"，$\sigma$ 是 sigmoid，$\beta$ 控制力度。收集完数据离线训练即可。

---

## A. 视觉截图路线（输入是 screenshot）

### A1. WebGym（CVPR 2026）— 最简单的：只模仿成功轨迹

**采样**：从 29.2 万个真实网站任务抽题，Qwen3-VL-8B 自己开浏览器做，每条轨迹按难度限 10/20/30 步。GPT-4o 拿任务专属检查清单（rubric）看轨迹截图，**所有要点全满足才给 1 分，否则 0 分**。

**每步输入**：当前截图 + 任务 + 模型上一步自己写的备忘录（memory）文本；历史截图全不保留。**输出**：思考 + 更新后的备忘录 + 一个坐标动作（click/type/scroll/…）。

**Loss（supplement §F, Eq. 1）**：

$$\max_\theta\ \mathbb{E}_{\mathcal{T}}\left[\mathbb{E}_{o_{0:\tau},\,a_{0:\tau-1}\sim\pi_\theta}\left[\Big(\sum_{t=0}^{\tau-1}\log\pi_\theta(a_t \mid o_{\le t},\mathcal{T})\Big)\cdot \mathbb{1}\big[R(o_{0:\tau},\mathcal{T})=1\big]\right]\right]$$

| 符号 | 含义 |
|---|---|
| $\mathcal{T}$ | 任务 |
| $a_t,\ o_t$ | 第 $t$ 步的动作、观测（截图） |
| $\tau$ | 轨迹终止步（模型发 ANSWER 或到步数上限） |
| $R \in \{0,1\}$ | 整条轨迹的成败（GPT-4o rubric 判定） |
| $\mathbb{1}[\cdot]$ | 指示函数：成功 = 1，失败 = 0 |

**大白话**：这是 REINFORCE 的最简形式——把指示函数展开看，**失败轨迹权重为 0（整条扔掉），成功轨迹权重为 1（整条当范文，最大化每一步输出的概率）**。没有零件 1 的 clip、没有零件 2 的组内比较、没有负梯度。论文自己说这等价于 "online filtered behavior cloning"（在线筛选式模仿学习）。

**一个额外过滤**：如果某一步执行后截图和上一步完全一样（动作没生效），这一步会被从求和里剔除，即使它在成功轨迹里——这就是论文的 repeated-action penalty（它是过滤，不是 reward 里的负分）。

**关键数值**：lr 1e-6，每轮 rollout 1800 条，成绩 26.2% → 42.9%。

---

### A2. AsyncWebRL（arXiv:2606.05597）— WebGym 续作：GRPO + 三处手术

**采样**：环境同 WebGym。全异步系统：浏览器持续采数据、GPU 持续训练，互不等待，因此训练用的数据可能来自旧几版的模型（这带来第 2 处手术要解决的问题）。每任务采 $G=8$ 条轨迹，reward 仍是 GPT-4o rubric 的 0/1。

**每步输入**：只有上一张截图 + 模型自己上一条完整回答（备忘录写在回答里）。

**Loss（Eq. 1，红色标注即原文对标准 multi-step GRPO 的三处改动）**：

$$\mathcal{J}(\theta)=\mathbb{E}_{\tau\sim\pi_{\text{behave}}}\left[\frac{1}{G\cdot k}\sum_{i=1}^{G}\sum_{j=1}^{|\tau_i|}\sum_{t=1}^{|\tau_{i,j}|}\min\left(\frac{\pi_\theta}{\pi_{\text{behave}}}\hat A_i,\ \frac{\pi_{\text{prox}}}{\pi_{\text{behave}}}\cdot\text{clip}\left(\frac{\pi_\theta}{\pi_{\text{prox}}},1-\epsilon,1+\epsilon\right)\hat A_i\right)\right]$$

$$\hat A_i = \big(r_i - \text{mean}(\mathbf{r})\big)/\text{std}(\mathbf{r})$$

| 符号 | 含义 |
|---|---|
| $G$ | 每任务轨迹数（8）；三重求和 = 组内每条轨迹 → 每一步 → 每个 token |
| $\pi_{\text{behave}}$ | 当初生成这条数据的旧模型（异步训练下可能落后好几版） |
| $\pi_{\text{prox}}$ | 本次参数更新开始时的模型快照 |
| $\pi_\theta$ | 正在更新的模型 |
| $\hat A_i$ | 零件 2：轨迹级组内归一化分，整条轨迹所有 token 共享 |
| $k$ | 固定常数 10 |

**大白话（三处手术）**：
1. **$1/k$ 替换 $1/|\tau_i|$**（最重要的发现）：标准做法是每条轨迹的 loss 除以自己的步数，让每条轨迹总权重为 1。但失败轨迹平均 12.5 步、成功轨迹平均 5.1 步——除以步数后，**长的失败轨迹每个 token 挨的罚被稀释约 2.4 倍**，模型学不会"停止磨蹭"，还学出越写越长的备忘录。改成除以固定常数 $k=10$ 后，每条轨迹的权重变成 $|\tau_i|/k$（越长权重越大），长失败轨迹被足额惩罚。就这一行改动，成绩 42.9% → 45.4%。
2. **比值拆两段**：因为数据来自旧模型，直接算 $\pi_\theta/\pi_{\text{behave}}$ 会把"数据旧"和"这次更新改了多少"混在一起，clip 频繁误触发。拆成 $\frac{\pi_\theta}{\pi_{\text{behave}}} = \frac{\pi_\theta}{\pi_{\text{prox}}}\cdot\frac{\pi_{\text{prox}}}{\pi_{\text{behave}}}$，**clip 只卡"这次更新改了多少"那一段**，"数据旧"那段原样保留当权重。论文报告 clip 误触发率约减半。
3. **去掉 KL 项**（零件 3 不要了），另加 dual-clip 给负分 token 的梯度设下限（附录 Eq. 2，常数 $c=3.0$）。

**关键数值**：$G=8$，$\epsilon=0.2$，$k=10$，lr 5e-6；全对/全错的组直接跳过，凑满 128 条混合轨迹才更新。

---

### A3. OpenWebRL（arXiv:2606.02031）— 真实互联网上的 MM-GRPO

**采样**：真实网站（非沙盒），每条轨迹一个独立 K8s 容器浏览器。先用 412 条老师模型成功示范做 SFT 热身，再 RL。每任务 $G=5$ 条轨迹；**全组 reward 相同（全 0 或全 1）的组整组丢弃**，凑满 48 个有效组才更新。

**每步输入**：最近 1 张截图 + 全部历史思考文本 + 环境从 DOM 变化提取的一句反馈（"输入成功/页面没变"）。

**Reward（Appendix A.4，三层组合）**：

$$R(\tau_i)=\begin{cases}-1, & \text{反复格式错误导致终止}\\ 0, & \text{格式检查不过}\ (F(\tau_i)=0)\\ J(\tau_i)\in\{0,1\}, & \text{否则由 VLM judge 判成败}\end{cases}$$

judge 输入 = 任务 + 最终答案 + 最近 3 张截图 + 动作历史，输出含 "SUCCESS" 记 1、否则 0。

**Loss（Section 4.4, MM-GRPO）**：

$$\mathcal{L}=-\frac{1}{G}\sum_{i=1}^{G}\sum_{t=0}^{T_i-1}\frac{\sum_k m_{i,t,k}\cdot\min\Big(\rho_{i,t,k}A_i,\ \text{clip}\big(\rho_{i,t,k},\,1-\epsilon_{\text{low}},\,1+\epsilon_{\text{high}}\big)A_i\Big)}{\max\big(\sum_k m_{i,t,k},\,1\big)}$$

$$\rho_{i,t,k}=\frac{\pi_\theta(y_{i,t,k}\mid h_{i,t},\,y_{i,t,<k})}{\pi_{\theta_{\text{old}}}(y_{i,t,k}\mid h_{i,t},\,y_{i,t,<k})}, \qquad A_i=\frac{R_i-\mu_G}{\sigma_G+\epsilon}$$

| 符号 | 含义 |
|---|---|
| $T_i$ | 轨迹 $i$ 的对话轮数；$y_{i,t,k}$ = 第 $t$ 轮回答的第 $k$ 个 token |
| $h_{i,t}$ | 第 $t$ 轮时管理过的多模态上下文（1 张截图 + 历史思考文本） |
| $m_{i,t,k}$ | **mask：只有模型自己生成的回答 token 记 1**，观测/历史上下文 token 记 0，不进 loss |
| $\epsilon_{\text{low}}=0.2,\ \epsilon_{\text{high}}=0.28$ | 非对称截断：向上放得比向下松 |
| $A_i$ | 零件 2，赋给该轨迹**所有轮**的所有回答 token |

**大白话**：骨架就是零件 1 + 零件 2，有三个值得注意的细节。①每轮的 loss 先在**本轮 token 内**取平均（分母），但**轮与轮之间直接相加、不除以轮数**——论文明说：如果除以轮数，步数多的难任务信号会被稀释。这和 AsyncWebRL 的 $1/k$ 手术是同一个问题的两种解法。②clip 上界（1.28）比下界（0.8）松：允许模型更大胆地提升低概率动作的概率，抑制时保守——抄自 DAPO。③KL 项和 entropy 项都不要。

**关键数值**：$G=5$，lr 1e-6，PPO epochs 2，前 90 轮限 15 步、后 50 轮放宽 30 步；成绩 39.3 → 52.0（SFT）→ 68.4（RL）。

---

### A4. ZeroGUI（arXiv:2505.23762）— 全自动任务 + 全自动判分的 GRPO

**采样**：任务由 GPT-4o 看环境截图自动生成；成败由 Qwen2.5-VL-32B 看轨迹**全部截图**判定——**问 4 次、temperature 1.0，4 次全说成功才给 1 分**（故意压低误报，因为误报比漏报危害大；judge 不看 agent 自己的文字回复，防止被"我做完了"的幻觉骗到）。每任务 $G=64$ 条轨迹。两阶段：先在生成任务上训 1 epoch，再在目标测试任务上做 test-time training 1 epoch（judge 照旧，不用环境真值）。

**Loss（Eq. 3–5）**：每条轨迹第 $t$ 步的动作序列 $a_t^{(i)}$ 单独算一份目标，再对所有序列平均：

$$\mathcal{J}_t^{(i)}(\theta)=\frac{1}{|a_t^{(i)}|}\sum_{k=1}^{|a_t^{(i)}|}\left(\min\Big(r_{t,k}^{(i)}\hat A^{(i)},\ \text{clip}\big(r_{t,k}^{(i)},1-\epsilon,1+\epsilon\big)\hat A^{(i)}\Big)-\beta\, D_{\text{KL}}(\pi_\theta\|\pi_{\text{ref}})\right)$$

$$\hat A^{(i)}=\frac{R^{(i)}-\text{mean}(\{R^{(i)}\}_{i=1}^G)}{\text{std}(\{R^{(i)}\}_{i=1}^G)}, \qquad \mathcal{J}(\theta)=\frac{1}{\sum_i T^{(i)}}\sum_{i=1}^G\sum_{t=1}^{T^{(i)}}\mathcal{J}_t^{(i)}(\theta)$$

**KL 项换零件（Eq. 6）**：标准 GRPO 的 k3 估计 $\frac{\pi_{\text{ref}}}{\pi_\theta}-\log\frac{\pi_{\text{ref}}}{\pi_\theta}-1$ 在 $\pi_\theta \ll \pi_{\text{ref}}$ 时梯度指数爆炸，换成 k2 估计：

$$D_{\text{KL}}=\frac{1}{2}\big(\log\pi_\theta - \log\pi_{\text{ref}}\big)^2$$

**大白话**：主体 = 零件 1 + 零件 2 + 零件 3。轨迹级的 $\hat A^{(i)}$ 直接**广播**给该轨迹每一步的动作序列（原文："we assign each prediction sequence $a_t^{(i)}$ with advantage $\hat A^{(i)}$"）。KL 那个改动本质是把"距离惩罚"从一个容易数值爆炸的形式换成对数概率差的平方（像 MSE 一样温和线性）。另外实现上每轮 rollout 后只做一次梯度更新，此时 $\pi_\theta=\pi_{\theta_{\text{old}}}$、比值恒为 1，min/clip 实际不起作用（附录自己承认）。

**关键数值**：$G=64$，$\beta=0.1$，lr 2e-6，rollout temperature 0.5；clip $\epsilon$ 数值原文未披露。

---

### A5. ARPO（arXiv:2505.16282）— GRPO + 成功经验回放（OSWorld 桌面）

**采样**：先筛任务——UI-TARS-1.5 每任务试 16 次，至少成功 1 次的任务才保留（128 个）：太难的全失败、太容易的全成功，都没有组内对比信号。每任务 $G=8$ 条轨迹，256 个并行虚拟机。

**Reward**：任务成功 $r_t=1$、失败 0（OSWorld 环境脚本判定）；输出格式不能解析则 $r_f=-1$。总目标 $\max_\theta\ \mathbb{E}[r_t+r_f]$（Eq. 2）。

**每步输入**：**整条轨迹**的全部历史截图 + 动作（≤15 张 1080P 图塞进 64K 上下文，episode 硬限 15 步）——它是唯一不裁剪历史截图的方法。整条轨迹编码为**一个连续序列**。

**Loss（§3.1，标准 GRPO）**：

$$J_{\text{GRPO}}(\theta)=\frac{1}{G}\sum_{i=1}^{G}\frac{1}{|o_i|}\sum_{t=1}^{|o_i|}\min\left(\frac{\pi_\theta(o_i(t)\mid o_{i,<t})}{\pi_{\text{old}}(o_i(t)\mid o_{i,<t})}\hat A_{i,t},\ \text{clip}\left(\frac{\pi_\theta(o_i(t)\mid o_{i,<t})}{\pi_{\text{old}}(o_i(t)\mid o_{i,<t})},1-\varepsilon,1+\varepsilon\right)\hat A_{i,t}\right)$$

$$\hat A_{i,t}=\frac{r_i-\mu}{\sigma} \quad\text{（整条轨迹所有 token 同一个值）}$$

**独有零件——经验回放**（§3.5，原文规则）：**当一个组的 8 条轨迹全部失败时**（组内全 0，零件 2 失效），从该任务此前存下的成功轨迹缓存里取一条，**随机替换掉组内一条失败轨迹**——人为制造出组内对比。缓存固定容量、满了淘汰最旧的。

**大白话**：loss 本身就是教科书 GRPO（零件 1 + 零件 2），创新全在数据侧：任务筛选保证组内有方差、经验回放在方差消失时人工补一条成功样本。KL 项去掉（省掉参考模型）。

**关键数值**：$G=8$，DAPO 非对称 clip $\varepsilon_{\text{low}}=0.2 / \varepsilon_{\text{high}}=0.3$，lr 1e-6，训 15 epochs。原文未披露：回放缓存容量；observation token 是否 mask（全文没提）。

---

### A6. UI-TARS v1（arXiv:2501.12326）— 主体是模仿，RL 只是一小步 DPO

**采样**：几百台虚拟机自动跑任务 → 过滤好轨迹 → SFT → 再跑（迭代）。DPO 数据来自"反思"标注：找到轨迹里出错的那一步 $\tau$，标注出该局面下的修正动作 $a'_\tau$，与原错误动作 $a_\tau$ 配成对。

**每步输入（Eq. 3）**：最近 $N=5$ 张截图 + **全部**历史思考和动作文本：

$$P\big(t_n, a_n \mid \text{instruction},\ t_1, a_1, \cdots, (o_{n-i}, t_{n-i}, a_{n-i})_{i=1}^{N},\ o_n\big)$$

（$o$ = 截图，$t$ = 思考，$a$ = 动作；只有截图限最近 5 张，思考/动作文本全保留。）

**Loss（§4.5，即零件 4 原样）**：

$$\mathcal{L}_{\text{DPO}}(\theta)=-\mathbb{E}_\tau\left[\log\sigma\left(\beta\log\frac{\pi_\theta(a'_\tau\mid s_\tau)}{\pi_{\text{SFT}}(a'_\tau\mid s_\tau)}-\beta\log\frac{\pi_\theta(a_\tau\mid s_\tau)}{\pi_{\text{SFT}}(a_\tau\mid s_\tau)}\right)\right]$$

| 符号 | 含义 |
|---|---|
| $s_\tau$ | 出错那一步的局面（指令 + 到该步为止的交互历史） |
| $a_\tau / a'_\tau$ | 原错误动作 / 标注修正后的动作 |
| $\pi_{\text{SFT}}$ | 参考模型 = SFT 后的模型 |

**大白话**：单步级的好坏配对——"同样的局面，修正动作比犯错动作好"。不是在线 RL，没有 rollout 组、没有 advantage。$\beta$ 数值原文未披露。

---

### A7. UI-TARS-2（arXiv:2509.02544）— 换成正经 PPO，明确弃用 GRPO

**采样**：在线多轮 rollout（一步 = 思考 + 动作 + 观测的完整循环）。Reward 分三类：可程序判定的域（如游戏用脚本查分数）给 0/1；GUI-Browsing 有参考答案，用 LLM-as-Judge 对照判；无法验证的 GUI 任务用自家模型训的 reward model（ORM）打分——ORM 输入全部文本历史 + 最近 5 张截图。个别场景加格式分和长度惩罚。

**Loss（Eq. 4，PPO + DAPO 式非对称 clip）**：

$$\mathcal{J}_{\text{PPO}}(\theta)=\mathbb{E}\left[\min\left(\frac{\pi_\theta(o_t\mid q,o_{<t})}{\pi_{\theta_{\text{old}}}(o_t\mid q,o_{<t})}\hat A_t,\ \text{clip}\left(\frac{\pi_\theta(o_t\mid q,o_{<t})}{\pi_{\theta_{\text{old}}}(o_t\mid q,o_{<t})},1-\varepsilon_{\text{low}},1+\varepsilon_{\text{high}}\right)\hat A_t\right)\right]$$

**和 GRPO 的本质区别在 $\hat A_t$ 怎么来**：GRPO 用零件 2（组内比较，整条轨迹一个分）；PPO 额外训练一个**价值网络**预测每个位置的期望回报，$\hat A_t$ 由 GAE 从价值网络算出——**每个 token 有自己的分**，能区分"这条失败轨迹里其实前 5 步走得对"。

**两个稳定性技巧**：①**价值网络预热**：先固定策略离线把价值网络训到收敛（用 $\lambda=1.0$ 即蒙特卡洛回报）再开始 PPO——因为他们发现直接训时价值估计和真实 reward 甚至负相关；②**按长度自适应的 GAE**：$\lambda_{\text{policy}}=1-\frac{1}{\alpha l}$（$\alpha=0.05$，$l$ 为序列长度），序列越长越偏向多步回报。

**记忆机制（Eq. 2–3）**：上下文 = 最近 $N$ 步的原始（思考, 动作, 观测）+ 更早历史的文字摘要：$P(t_n, a_n \mid \text{instruction}, \mathcal{W}_n, o_n, \mathcal{E}_n)$，$\mathcal{W}$ = Working Memory（高保真近期），$\mathcal{E}$ = Episodic Memory（压缩摘要）。

**大白话**：论文明说 "PPO consistently outperforms GRPO by a clear margin"，代价是要多训一个价值网络、还得先给它预热。原文未披露：$\varepsilon_{\text{low}}/\varepsilon_{\text{high}}$、$N$、$\gamma$ 的数值；loss 无 KL 项。

---

## B. HTML 文本路线（输入是网页 HTML 文字，不看图）

### B1. WebRL（ICLR 2025）— 不是 GRPO：把 RL 变成一个回归问题

**采样**：WebArena-Lite 沙盒。循环：模型做任务 → 训练过的判分模型（ORM）看最终页面 HTML 判 0/1 → **失败的任务交给 GPT-4o 改写生成 500 条难度相近的新任务**进入下一 phase 题库（失败变考题）→ 成功轨迹存入回放缓存反复用。

**每步输入**：任务 + 当前页面精简 HTML（元素编 ID）+ 历史动作文字列表（历史页面 HTML 全丢）。

**推导链（Eq. 1→2→4→5）**：从"最大化 reward 且不偏离上一版模型 $\pi_{\text{ref}}$ 太远"的目标出发，可以解出最优策略的闭式（Appendix Eq. 10）：

$$\pi^*(a\mid s,I)=\pi_{\text{ref}}(a\mid s,I)\exp\Big(\tfrac{1}{\beta}A^*(s,a,I)\Big)$$

**大白话**：最优策略 = 上一版模型 × 按"动作好坏分 $A^*$"放大缩小的系数。好动作概率乘一个 >1 的数，坏动作乘一个 <1 的数，$\beta$ 控制放大力度。于是训练不用策略梯度，直接**回归**到这个目标——

**Policy loss（Eq. 5，均方误差）**：

$$\mathcal{L}(\pi_\theta)=\mathbb{E}_\nu\left[\left(\beta\log\frac{\pi_\theta(a\mid s,I)}{\pi_{\text{ref}}(a\mid s,I)}-A^*(s,a,I)\right)^2\right]$$

**大白话**：让"新模型相对上一版对这个动作的概率提升量（对数刻度，乘 $\beta$）"去逼近"这个动作的好坏分"。好动作（$A>0$）→ 概率提升到位为止；坏动作（$A<0$）→ 概率压低到位为止。对梯度求导（Eq. 6）会发现它就是"(好坏分 − 已提升量) × 模仿学习梯度"——**提升到位后梯度自动归零**，这就是内置的"绳子"（零件 3 的效果，但不是加法惩罚而是回归目标自带）。off-policy，可以吃回放缓存里的老数据。

**Advantage（Eq. 8）**：训练一个价值网络 $V$（用交叉熵学"这个状态最终能成功的概率"，Eq. 7），然后

$$A(s_t,a_t,I)=\lambda\big(\underbrace{r+V(s_{t+1},I)-V(s_t,I)}_{\text{走这一步后成功率涨了多少}}\big)+(1-\lambda)\big(\underbrace{r(s_T,a_T,I)-V(s_t,I)}_{\text{最终成败-当时的预期}}\big),\quad \lambda=0.5$$

**回放过滤**：只存成功轨迹；用上一版模型算每个动作的 perplexity，只取 perplexity 在 $[1/0.95,\ 1/0.5]$ 区间的动作——**太熟的（≈1）没信息，太生的（>2）学不动**，回放量限当轮新数据的 2 倍。

**关键数值**：$\lambda=0.5$，$\gamma=0.9$，lr 1e-6；**$\beta$ 的最终取值原文未披露**（只有消融扫描）。

---

### B2. WebAgent-R1（EMNLP 2025）— 多轮版 GRPO（M-GRPO）

**采样**：先 SFT 热身（不做的话初始成功率仅 6.1%）。每任务 $G$ 个并行浏览器各采一条完整轨迹；reward 用 WebArena 自带规则（字符串匹配 / URL 匹配 / 程序执行），成功 1 失败 0，无 reward model。

**每步输入 + 上下文压缩（§2.3）**：轨迹是一个连续对话 $h_t=(s'_1,a_1,s'_2,a_2,\ldots,s_t)$——**旧观测被替换成字面占位符 $s'_i=$ "Simplified HTML"（就几个 token），只有当前观测 $s_t$ 保留完整 HTML，动作全保留**。每收到新观测，就把上一个完整观测降级成占位符。

**Loss（§2.3）**：

$$\mathcal{L}_{\text{M-GRPO}}(\theta)=-\frac{1}{G}\sum_{i=1}^{G}\frac{1}{|\tau_i|}\sum_{j=1}^{|\tau_i|}\left(\frac{1}{|a_{i,j}|}\sum_{t=1}^{|a_{i,j}|}\Big[\tilde A_{i,j,t}-\beta\,\mathbb{D}_{\text{KL}}(\theta)\Big]\right)$$

$$\tilde A_{i,j,t}=\min\Big(r_{i,j,t}(\theta)A_{i,j},\ \text{clip}\big(r_{i,j,t}(\theta),1-\epsilon,1+\epsilon\big)A_{i,j}\Big), \qquad A_{i,j}=\frac{r_i-\text{mean}(\mathbf{r})}{\text{std}(\mathbf{r})}$$

**大白话**：零件 1 + 零件 2 + 零件 3 的标准组装，三层平均：组内平均 → 轨迹内按动作数平均 → 动作内按 token 数平均。注意它**保留了** $1/|\tau_i|$ 步数归一化——正是 AsyncWebRL 后来诊断有问题、OpenWebRL 明确弃用的那一项（这是这批论文间一个真实的分歧点）。$A_{i,j}$ 是轨迹级的：轨迹 $i$ 内**所有**动作共用一个分。loss 只算在动作 token 上（观测 token 用 mask 剔除，随上下文压缩动态更新 mask）。

**关键数值**：$\beta=0.001$，$\epsilon=0.2$，lr 1e-6；$G$ 与 max steps 的数值原文未披露（正文只有符号）。

---

### B3. Agent Q（arXiv:2408.07199）— 搜索树造数据 + DPO

**采样（不是重复试错，是建树）**：每个页面局面让模型提 $K$ 个候选动作，按 UCB1 规则选择扩展（Eq. 7）：

$$a_t^*=\arg\max_a\left[Q(h_t,a)+c_{\text{exp}}\sqrt{\frac{\log N(h_t)}{1+N(h_{t+1})}}\right]$$

**大白话**：优先点"目前看起来分高的"和"还没怎么试过的"动作，$c_{\text{exp}}$ 调节探索倾向。轨迹走到底拿 0/1 reward（OpenTable 上由 GPT-4V 按 4 条标准判定），沿树往上回传更新每个节点的均值（Eq. 8）。

**节点打分（Eq. 10）——两个来源混合**：

$$Q(h_t,a_t^i)=\alpha\,\tilde Q(h_t,a_t^i)+(1-\alpha)\,\hat Q(h_t,a_t^i)$$

$\tilde Q$ = 树搜索实测的成功率；$\hat Q$ = 让模型自己给 $K$ 个候选动作反复排序得出的"AI 过程评分"。消融显示混合比只用实测高 6.5 个百分点。

**配对构造**：同一个局面下、都实际探索过、且分差够大（$|Q(h_t,a^w)-Q(h_t,a^l)|\ge\theta_{\text{threshold}}$）的两个动作 → 一好一坏配对。

**Loss（Eq. 5，零件 4 的 node 级版本）**：

$$\mathcal{L}_{\text{DPO}}=-\mathbb{E}_{(h,a^w,a^l)}\left[\log\sigma\left(\beta\log\frac{\pi_\theta(a^w\mid h)}{\pi_{\text{ref}}(a^w\mid h)}-\beta\log\frac{\pi_\theta(a^l\mid h)}{\pi_{\text{ref}}(a^l\mid h)}\right)\right]$$

$h_t=(a_1,\ldots,a_{t-1},o_t)$ = 全部历史动作 + 仅当前观测（论文明说 HTML 太长装不下历史页面）。参考模型不用单独加载——回放缓存里存了生成时的概率值直接用。

**未披露**：$\alpha,\beta,c_{\text{exp}},\theta_{\text{threshold}},K$ 全部只有符号没有数值（arXiv 版无实现附录）。

---

## C. 对照组：不开浏览器的离线单步 GRPO

### C1. HiconAgent（arXiv:2512.01763）

**采样**：从人类轨迹数据集 AMEX 随机抽 3000 个"单步"。每个单步输入 $q=(I, H_t, s_t)$（指令 + 历史 + 当前截图），让模型生成 $G=8$ 个候选回答 $o_i=(\text{思考}_i, \text{动作}_i)$——**GRPO 的"组"是同一步的 8 个回答，不是 8 条轨迹**。

**Reward（Eq. 7，纯规则对照标准答案）**：

$$r=r^f+r^t+r^v$$

$r^f$：输出格式对 = 1；$r^t$：动作类型和标准答案一致 = 1；$r^v$：动作值分——文本值算 F1（>0.5 记 1），点击坐标算与标准答案的欧氏距离 $d$，给连续分 $r^v=1-d$。

**Loss（Eq. 1）**：标准 GRPO（零件 1 + 零件 2 + 零件 3），只是分组对象是单步的 $G$ 个回答。论文另提出 HCPO：同一批数据跑"完整历史"和"压缩历史"两个分支各算一份 GRPO loss，再加一项 KL 让压缩分支对齐完整分支（完整分支当老师，Eq. 3–6）。

**大白话**：这是"GRPO"一词的另一种用法——没有环境交互、没有轨迹、reward 是和标准答案打分。和 A/B 节的在线方法只共享数学形式，问题设定完全不同。放在这里是提醒：**看到 "GRPO 训练 GUI/Web agent" 要先问一句：组内比较的是 G 条轨迹还是 G 个单步回答？**

---

## D. 总对比表

| 方法 | 算法 | 组/优化单位 | Loss 一句话 | Advantage/权重 | Reward 谁给 | KL 项 | 已披露关键超参 |
|---|---|---|---|---|---|---|---|
| **WebGym** | REINFORCE（= 筛选式模仿） | 整条轨迹 | 成功轨迹整条最大化似然，失败轨迹权重 0 | 无（indicator 0/1） | GPT-4o rubric，0/1 | 无 | lr 1e-6，每轮 1800 条 |
| **AsyncWebRL** | multi-step GRPO 改版 | 整条轨迹（G=8） | 零件 1+2；除以常数 k 而非步数；clip 只卡本次更新 | 轨迹级组内 z-score，全 token 共享 | GPT-4o rubric，0/1 | 去掉 | k=10，ε=0.2，dual-clip c=3.0 |
| **OpenWebRL** | MM-GRPO | 整条轨迹（G=5） | 零件 1+2；轮内平均、轮间求和不除轮数；非对称 clip | 轨迹级组内 z-score，全 token 共享 | 格式规则 + VLM judge（-1/0/1） | 去掉 | ε=0.2/0.28，全同组丢弃 |
| **ZeroGUI** | GRPO | 整条轨迹（G=64） | 零件 1+2+3；轨迹分广播到每步序列 | 轨迹级组内 z-score | VLM 判 4 次全过才 1 | k2 估计（β=0.1） | G=64，lr 2e-6 |
| **ARPO** | GRPO | 整条轨迹（G=8） | 教科书 GRPO；创新在全失败组塞成功轨迹 | 轨迹级组内 z-score | OSWorld 脚本 0/1，格式错 -1 | 去掉 | ε=0.2/0.3，任务先筛过 |
| **UI-TARS v1** | DPO（+ 迭代 SFT 为主体） | 单步配对 | 零件 4：修正动作 vs 错误动作 | 无 | 反思标注产生配对 | DPO 内含 | N=5 帧截图；β 未披露 |
| **UI-TARS-2** | PPO | 整条轨迹，token 级信用 | 零件 1（非对称）+ 价值网络给每 token 单独估分 | GAE（价值网络先离线预热） | 脚本 / LLM judge / 自训 ORM | 无 | α=0.05；ε 值未披露 |
| **WebRL** | 自定义回归式更新 | 单步（off-policy） | (β·概率提升量 − 好坏分)² 的均方误差 | 价值网络 TD/MC 混合（λ=0.5） | 训练过的 ORM，0/1 | 回归目标内置 | λ=0.5，γ=0.9；β 未披露 |
| **WebAgent-R1** | M-GRPO | 整条轨迹 | 零件 1+2+3，三层平均（保留 1/step 归一化） | 轨迹级组内 z-score | WebArena 规则 0/1 | β=0.001 | ε=0.2；G 未披露 |
| **Agent Q** | MCTS + DPO | 树节点配对 | 零件 4：同局面分差大的动作对 | Q = α·实测成功率 + (1-α)·AI 自评 | 末端 0/1（GPT-4V 判） | DPO 内含 | 数值超参全部未披露 |
| **HiconAgent** | 离线单步 GRPO | 单步 G 个回答 | 零件 1+2+3，组 = 同一步的 8 个候选 | 步级组内归一化 | 规则对标准答案（格式+类型+坐标距离） | 有 | G=8，lr 1e-6 |

## E. 三个跨论文的要点

1. **"步数归一化"是这批论文里一个真实的技术分歧**。WebAgent-R1 的 loss 里有 $1/|\tau_i|$（每条轨迹总权重 1）；AsyncWebRL 诊断出它让长失败轨迹欠罚、换成常数 $1/k$；OpenWebRL 独立地得出同样结论（"除以轮数会稀释难任务的信号"）直接不除。引用这些 loss 时值得把这一项单独核对。
2. **KL 项正在被抛弃**。ARPO、AsyncWebRL、OpenWebRL 都明确去掉 KL（省参考模型、省显存）；保留的 ZeroGUI 也要把估计式换成更温和的 k2。只有多轮对话式的 WebAgent-R1 用很小的 β=0.001 保留。
3. **组内没方差就学不到，各家补法不同**：ARPO 往全失败组里塞历史成功轨迹；OpenWebRL/AsyncWebRL 把全同组直接丢弃再多采；ZeroGUI 用 DAPO 动态采样过滤；WebRL 干脆绕开分组，用价值网络逐步给分。

## F. 抄录与缺失清单（引用前必读）

- **逐字抄录（LaTeX 源级）**：AsyncWebRL、OpenWebRL、ZeroGUI、HiconAgent、WebRL、Agent Q、WebAgent-R1、ARPO、UI-TARS v1/v2 的全部上列公式。
- **渲染版转写**（无 LaTeX 源，逐符号对照 PDF）：WebGym Eq. (1)。
- **论文确实没写（勿引用为已知）**：WebRL 的 β 取值；Agent Q 的全部数值超参；WebAgent-R1 的 G 和 max steps 数值及 KL 展开式；ARPO 的回放缓存容量与 observation mask 有无；ZeroGUI 的 clip ε 值；UI-TARS v1 的 DPO β；UI-TARS-2 的 ε_low/ε_high、Working Memory 的 N。
- 原文自身的两处记号瑕疵：WebRL Eq. 7 的 $V(s,a,I)$ 与他处 $V(s_t,I)$ 不一致；Agent Q 的 UCB 分母用 $1+N(h_{t+1})$（非常见的 $N(h_t,a)$）、配对阈值正文用 ≥ 而 Algorithm 1 用 >。

---

*相关笔记：[[Papers/2411-WebRL]] · [[Papers/2408-AgentQ]] · [[Papers/2606-WebGym]] · [[Papers/2606-AsyncWebRL]] · [[Papers/2606-OpenWebRL]] · [[Papers/2500-ArpoEndEndPolicy]] · [[Papers/2500-UI-TARS- Pioneering Automated GUI Interaction with Native Agents]] · [[Topics/CUA-Survey]]*
