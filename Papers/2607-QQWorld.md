---
title: "QQWorld: Quantile-Quantile Matching for World Model Regularization"
authors: [Zhoushun Yu, Xiaoyu Hu, Xiangyu Xu]
institute: ["Xi'an Jiaotong University"]
date_publish: 2026-07-30
venue: arXiv
tags: [world-model, RL]
url: "https://arxiv.org/abs/2607.28415"
arxiv_id: "2607.28415"
doi:
cite_key: yu2026qqworld
code:
rating: 3
content_scope: full-text
verification_status: source-checked
date_added: 2026-08-03
---
## Summary

QQWorld 指出 LeWM 用来把 latent 拉向各向同性 Gaussian 的 Epps–Pulley (EP) 正则，其恢复梯度对远离 bulk 的孤立尾部样本超指数衰减，因此重尾偏差长期得不到纠正。作者把 EP 换成 quantile–quantile (QQ) matching 损失——把投影后 latent 的 order statistics 直接对齐到 rank-matched Gaussian quantile，梯度幅度随 quantile 偏差线性增长而不衰减——并提出 cross-batch QQ 用历史 detached 样本扩大排序池。在 Two-Room / Reacher / PushT / OGBench-Cube 四个 control 环境（6 seeds）上，平均 planning 成功率从 LeWM 的 79.75% 提升到 85.08%，同时 KS / EP 统计量与 radial tail rate 均下降。

## Problem & Motivation

Latent world model 的 planning 质量依赖 latent 分布的质量。近期一条路线（Balestriero & LeCun 的 LeJEPA、Maes et al. 的 LeWM）不再只约束低阶矩（如 VICReg 的方差项），而是把完整的 normality test 当作可微惩罚，给出 distribution-level 的训练信号；LeWM 具体采用基于 characteristic function 的 Epps–Pulley 检验。

作者的出发观察是：即便显式惩罚了 non-normality，LeWM 学到的 latent 仍呈现明显重尾（Figure 1 Right，radial tail rate 0.315 vs Gaussian reference 0.10）。重尾在 world model 里是有害的——极端 latent 会把 dynamics 推到表示稀疏的区域，在多步 rollout 中放大误差。由于惩罚项存在而现象仍在，问题被定位到「这个统计量作为训练目标时的优化几何」，而不是正则强度不够。

这引出论文真正的问题表述：一个适合**检验**分布差异的统计量，未必是适合**训练**的目标；判据是它能否在整个优化过程中提供有信息量、不消失的梯度。

## Method

**统一框架：sliced normality。** 沿随机一维方向 u ~ Uniform(S^{d-1}) 取投影 x_n = <u, z_n>，惩罚其偏离 N(0,1)，对 S 个方向平均（Eq. 1）。由 Cramér–Wold 定理，有限方向版本可视为对 sliced discrepancy 的 Monte Carlo 近似，目标是联合分布而非各维边缘。论文的贡献只在于替换 per-slice discrepancy L。

**诊断 EP 的梯度几何。** 先用 Rustamov (2021) 的等价关系把 EP 统计量写成以 Gaussian kernel k(x,y)=exp(-(x-y)^2/2) 为核、参考分布固定为 N(0,1) 的平方 MMD（Eq. 3）；EP 中的 Gaussian weighting w(t) 直接决定了 kernel 在样本域上的有限交互尺度。对单个坐标求导（Eq. 4）得到两项：pairwise repulsive term（防坍缩）与 center-attraction term（拉回原点）。**Proposition 1（Vanishing restoring force）**给出解析形式：当 x_n = h → ∞ 而其余样本落在 bulk {|x_m| ≤ R} 内时，pairwise 项为 O(h·exp(-(h-R)^2/2)) 可忽略，恢复力为 sqrt(π)·h·exp(-h^2/4)·(1+o(1))，在 h = sqrt(2) 处取极大后超指数衰减。即：latent 一旦跑出 kernel 的交互尺度，EP 就「看不见」它了。

**QQ matching 损失。** L_QQ = Σ_n (x̂_n − q_n)^2，其中 x̂_1 ≤ … ≤ x̂_N 为投影 batch 的 order statistics，q_n = Φ^{-1}((n−0.5)/N)（Eq. 6）。它是平方 2-Wasserstein 距离的 quadrature 近似（Eq. 7）。**Proposition 2** 给出梯度 ∂L_QQ/∂x_n = 2(x_n − q_{ρ(n)})：方向直指 rank-matched quantile，幅度随偏差线性增长。QQWorld 即用 L_QQ 替换 LeWM 的 EP 项，其他一律不动。

**排序不可微的处理。** 两个相邻 rank 的样本换序时梯度会跳变。作者用 Eq. 10–13 的局部分析说明：在 tie 配置（δ→0）处单侧方向导数为 −2(q_{k+1} − q_k) < 0，即 tie 边界是**排斥**的，梯度下降会主动拉开两个样本，因此排序引起的梯度不连续在实践中不构成障碍。

**QQ 与 EP 的单向控制。** **Proposition 3**：存在与 X、N 无关的常数 C，使 L_EP ≤ C·(L_QQ + log N / N)，故 L_QQ → 0 ⟹ L_EP → 0；反向不成立——EP 的 Gaussian kernel 贡献随距离饱和，L_EP → 0 时 L_QQ 仍可能 → ∞。

**Cross-Batch QQ。** 维护一个 FIFO 队列保存前 K 次迭代的投影特征（detached），排序池 M = (K+1)N，但只对当前 batch 的 N 个样本回传梯度（Eq. 17–18），从而把 ranking-pool 规模与 backprop batch 规模解耦。Section 3.3.1 给出**近似** MSE 分解（Eq. 21）：目标估计误差 ≈ [Ft(x)(1−Ft(x))/(N(K+1)) + (F̄_{t,K}(x) − Ft(x))^2] / φ(q(x))^2，前项是 rank-estimation variance（随 K 增大从 1/N 降到 1/(N(K+1))），后项是 representation-staleness bias。结论是 cross-batch QQ 主要在 small-N regime 有用，batch 足够大时基础 QQ 更好。

## Key Results

**Planning（Table 1，四环境 × 6 seeds，沿用 LeWM 的数据预处理、训练与 CEM goal-conditioned 评测协议）**

| Method | Two-Room | Reacher | PushT | OGBench-Cube | Avg. |
|:--|:--|:--|:--|:--|:--|
| LeWM | 84.33±4.23 | 82.67±4.42 | 84.67±6.53 | 67.33±5.01 | 79.75 |
| Sub-JEPA | 93.67±4.27 | 81.00±2.10 | 89.00±5.33 | 69.00±8.69 | 83.17 |
| SD-JEPA | 86.33±6.12 | 85.00±5.02 | 89.67±4.27 | 69.67±5.13 | 82.67 |
| SMWM | 88.67±7.12 | 73.00±4.69 | 86.00±2.53 | 84.33±4.97 | 83.00 |
| DINO-WM (w/o proprio.) | 100.00 | 79.00 | 74.00 | 86.00 | 84.75 |
| **QQWorld** | 93.67±3.44 | 85.33±5.16 | 91.00±5.76 | 70.33±7.31 | **85.08** |

平均成功率 85.08%，比 LeWM 高 5.33 个百分点，四个环境逐一优于 LeWM。**证据边界**：逐环境看，Reacher（+2.66）与 OGBench-Cube（+3.00）的增益均小于两方各自报告的标准差，只有 Two-Room（+9.34）和 PushT（+6.33）的差距明显超出 std；论文未报告显著性检验。DINO-WM 与 PLDM 的数字因无官方 checkpoint，直接引自 LeWM 论文而非本文复现，且无 std——QQWorld 对 DINO-WM (w/o proprio.) 的平均领先仅 0.33 pp，且在 Two-Room（93.67 vs 100.00）与 OGBench-Cube（70.33 vs 86.00）上落后。

**Normality（Table 2 + Figure 1，20,000 个 latent 沿 6,144 个固定随机单位方向投影）**：KS 0.038 → 0.032（−15.8%），EP 119.909 → 82.294（−31.4%），四环境平均。值得注意的是 QQWorld 的 EP 统计量反而低于**直接用 EP 训练的** LeWM。Figure 1 的数值演示：mean QQ RMSE 0.157 → 0.121；radial tail rate P(‖z‖²₂ > q₀.₉₀(χ²₁₉₂)) 0.315 → 0.123（Gaussian reference 0.10）。Figure 2 给出 Two-Room 上 40k 训练步的 tail 演化曲线，QQWorld 的 tail 逐步逼近 Gaussian 参考而 LeWM 全程维持重尾。**证据边界**：Table 2 未报 std 与 seed 数。

**机制断言的证据形态**：「EP 对尾部样本的 corrective gradient 迅速消失」既有**解析结论**（Proposition 1，给出闭式渐近梯度与 h=sqrt(2) 极大点），也有**数值演示**（Figure 1 Right 的 tail rate、Figure 2 的训练过程 tail 曲线）。但 Proposition 1、2、3 在正文中均只有陈述与简短论述，13 页 PDF 无附录、无完整证明。

**Physical state probing（Table 3，PushT，6 seeds）**：QQWorld 与 LeWM 差距极小——agent location Linear MSE 0.042 vs 0.041；block angle 0.176 vs 0.172（r 0.908 vs 0.910）。作者的结论只是「QQ 正则没有破坏 task-relevant 信息」，这个读法与数据相符；未报 std。

**Cross-Batch QQ（Table 4）**：N=32 时 K+1 = 1/2/3/4 对应成功率 65.42 / 80.67 / 83.50 / 81.75，GPU 显存几乎不变（3434.7 → 3435.1 MB）。N=32, K+1=3（83.50%）超过 LeWM（79.75%），相对大 batch QQWorld（N=128, 85.08%, 12747.1 MB）把 batch 缩 4×、显存降 73%。收益非单调：队列从 3 加到 4 反而降到 81.75；N=64、N=128 加历史 batch 均不改善（81.83→81.00、85.08→80.83）。这与 Eq. 21 的 bias–variance 分析方向一致。

**Novelty 定位**：论文称 QQ-based 目标此前很少用于 latent world model 正则；并发工作 Wu et al. 2026 (VISReg) 用 sliced Wasserstein matching 做 JEPA 训练，但聚焦自监督表示学习而非 world modeling / planning，且需额外 variance 项做尺度控制。

## Evidence Ledger

| Claim ID | Claim | Type | Source locator | Evidence excerpt | Status |
|:--|:--|:--|:--|:--|:--|
| C1 | Proposition 1 给出解析结论：EP 恢复力 = sqrt(π)·h·e^{-h²/4}(1+o(1))，在 h=sqrt(2) 取极大后超指数衰减 | causal-mechanism | Sec 3.1, Proposition 1, Eq. 5, p.4 | "∂LEP/∂h = √π h e−h2/4(1 + o(1)) ... attains its maximum at h = √2 and decays super-exponentially thereafter" | source-verified |
| C2 | Proposition 1/2/3 在正文只有陈述与简短论述，13 页 PDF 无附录、无完整证明（pp.11-13 为 References） | causal-mechanism | pp.4-6 (Props 1-3), pp.11-13 (References) | "Proposition 3 shows that QQ matching provides a stronger form of distributional control than EP matching" | source-verified |
| C3 | Figure 1 数值演示：mean QQ RMSE 0.157→0.121；radial tail rate 0.315→0.123（Gaussian ref 0.10） | number | Figure 1 caption, p.2 | "reduces the mean QQ RMSE from 0.157 to 0.121 ... QQWorld reduces the tail rate from 0.315 to 0.123" | source-verified |
| C4 | four control environments = Two-Room / PushT / Reacher / OGBench-Cube；沿用 LeWM 的预处理、训练与 CEM 评测；6 seeds | benchmark-setting | Sec 4.1, p.7; Table 1 caption, p.8 | "including Two-Room, PushT, Reacher, and OGBench-Cube" ... "mean ± standard deviation across six random seeds" | source-verified |
| C5 | 平均成功率 85.08% vs LeWM 79.75%，+5.33 pp，四环境逐一优于 LeWM | number | Sec 4.2, p.8; Table 1 | "achieves the highest average success rate of 85.08%, improving the LeWM baseline by 5.33 percentage points" | source-verified |
| C6 | 逐环境 mean±std 见 Table 1；Reacher(+2.66) 与 OGBench-Cube(+3.00) 的增益小于双方各自 std | number | Table 1, p.8 | "LeWM 84.33±4.23 82.67±4.42 84.67±6.53 67.33±5.01 79.75 ... QQWorld 93.67±3.44 85.33±5.16 91.00±5.76 70.33±7.31 85.08" | source-verified |
| C7 | QQWorld 平均仅比 DINO-WM (w/o proprio.) 高 0.33 pp；DINO-WM/PLDM 数字引自 LeWM 而非本文复现，无 std | comparison | Table 1, p.8; Sec 4.2 | "Since official checkpoints for PLDM and DINO-WM are not available, we cite their success rates directly from LeWM" | source-verified |
| C8 | Table 2 四环境平均：KS 0.038→0.032 (−15.8%)，EP 119.909→82.294 (−31.4%)；QQWorld 的 EP 低于用 EP 训练的 LeWM；无 std/seed 数 | number | Table 2 + caption, p.8; Sec 4.3 | "0.038 119.909 / 0.032 82.294 / Relative reduction (%) 15.8 31.4 ... lower EP statistic even though LeWM is trained directly with the EP objective" | source-verified |
| C9 | 增益只在 LeWM 单一 backbone 上验证；论文无把 QQ 正则插入其他 world model（DINO-WM/PLDM/Sub-JEPA/SD-JEPA/SMWM）的实验 | benchmark-setting | Sec 4.1, p.7; Secs 4.2-4.6 | "QQWorld differs from LeWM only by replacing the EP regularizer with the proposed QQ objective" | source-verified |
| C10 | Table 4：N=32 下 K+1=1/2/3/4 → 65.42/80.67/83.50/81.75；N=32,K+1=3 超过 LeWM，batch 缩 4×、显存降 73%；队列收益非单调 | number | Table 4, p.10; Sec 4.6 | "N = 32, K + 1 = 3 outperforms LeWM (83.50% versus 79.75%) ... reducing the training batch size by 4× and GPU memory usage by 73%" | source-verified |
| C11 | bias–variance trade-off 以近似闭式 MSE 分解（Eq. 21）给出：variance ~ 1/(N(K+1)) + staleness bias，并由 Table 4 的非单调结果经验支撑 | causal-mechanism | Sec 3.3.1, Eq. 21-22, p.7; Sec 4.6, p.10 | "rank-estimation variance ... representation-staleness bias ... consistent with the bias–variance trade-off analyzed in Eq. 21" | source-verified |
| C12 | Novelty 断言 + 并发工作 Wu et al. 2026 (VISReg) 用 sliced Wasserstein 做 JEPA 训练，聚焦自监督表示学习且需额外 variance 项 | sota-novelty | Sec 2.3, p.3; References p.13 | "QQ-based objectives have rarely been explored for regularizing latent world models. Concurrent with our work, Wu et al. (2026) uses sliced Wasserstein matching" | source-verified |
| C13 | Normality 评估用 20,000 latent × 6,144 固定随机单位方向；latent 维度 192 | benchmark-setting | Sec 4.3, p.8; Figure 1 caption, p.2 | "we randomly sample 20,000 latents and project them along 6,144 random unit directions" | source-verified |
| C14 | 论文正文未给出任何代码 / GitHub / project page 链接 | license-code | whole document, pp.1-13 | "[no http/github/project-page string appears anywhere in the extracted text]" | source-verified |
| C15 | QQ 正则权重对所有环境固定为 3.5；论文宣称不引入新超参、无需额外调参 | benchmark-setting | Sec 4.1, p.7; Intro contributions, p.2 | "We set the QQ regularization weight to 3.5 for all environments ... QQWorld does not have new hyperparameters or require extra tuning" | source-verified |
| C16 | Table 3 probing 差距极小（agent location 0.042 vs 0.041；block angle 0.176 vs 0.172, r 0.908 vs 0.910），6 seeds 平均、未报 std | number | Table 3, p.9; Sec 4.4 | "Agent location LeWM 0.042 0.979 ... QQWorld 0.041 0.979 ... Block angle LeWM 0.176 0.908 ... QQWorld 0.172 0.910" | source-verified |
| C17 | 作者 Zhoushun Yu / Xiaoyu Hu / Xiangyu Xu，单位 Xi'an Jiaotong University，后两位为通讯作者 | benchmark-setting | p.1 author block | "Zhoushun Yu, Xiaoyu Hu∗, Xiangyu Xu∗ / Xi'an Jiaotong University / ∗Corresponding author" | source-verified |

> Verifier 补注：C13 中 latent 维度 192 是通过 Figure 1 对 ‖z‖²₂ 使用 χ²₁₉₂ 参考推出的，论文没有一句独立的「latent dim = 192」表述。C10 的 4×/73% 是相对 N=128 的大 batch QQWorld 配置（12747.1 MB）而言。source-verified 仅表示原文确实包含该信息，不表示结果已被独立复现。

## Strengths & Weaknesses

**亮点**

1. **问题表述对**。论文最有价值的一句在结论：「一个能有效**度量**分布差异的统计量，未必是有效的**训练目标**——它还必须在整个优化过程中给出有信息量、行为良好的梯度」。这把 LeJEPA 一系「用 normality test 当可微惩罚」的做法从「选哪个检验统计量更 powerful」重新框成「选哪个目标的梯度场更合适」，是可迁移到其他 distribution-matching 正则的判据。
2. **诊断链条干净**。EP → MMD 等价 → 显式求梯度 → 分离 pairwise repulsive 与 center-attraction 两项 → 证明后者超指数衰减，每一步都是可检查的，而不是把「重尾」直接归因于「正则不够强」。
3. **改动极小、无新超参**。QQWorld 相对 LeWM 只换一项损失，且 Proposition 3 的单向控制（L_QQ→0 ⟹ L_EP→0，反之不成立）给出了替换的理论理由而非仅仅经验偏好。QQWorld 的 EP 统计量低于直接优化 EP 的 LeWM，是这条链条上最有说服力的一个自洽验证。
4. **对排序不可微的处理是正面回答而非回避**。Eq. 10–13 说明 tie 边界是排斥的，与 anti-collapse 这一 JEPA 核心需求恰好同向。

**局限**

1. **单一 backbone**。所有增益都来自 LeWM 这一个 world model 的 EP→QQ 替换（C9）。论文把 QQ 描述成 drop-in replacement，但没有在 DINO-WM、PLDM 或任何非 LeWM 架构上做同样替换。「QQ 优于 EP」目前只是「在 LeWM 这个配置下 QQ 优于 EP」。
2. **小规模 control benchmark，增益有一半在噪声量级内**。四个环境 × 6 seeds，Reacher 与 OGBench-Cube 的提升（+2.66 / +3.00）都小于各自 std（C6），真正稳的是 Two-Room 与 PushT。5.33 pp 的平均增益主要由这两个环境驱动。论文没做显著性检验，也没做 seed 数的敏感性分析。
3. **与非 LeWM 系 baseline 的比较优势很薄**。QQWorld 对 DINO-WM (w/o proprio.) 只领先 0.33 pp，且后者的数字是转引的、无 std（C7）；OGBench-Cube 上 SMWM（84.33）和 DINO-WM（86.00）都远超 QQWorld（70.33）。所以「最高平均成功率」这一表述成立，但不足以支撑「QQWorld 是这批方法里更好的 world model」。
4. **命题无证明**。Proposition 1 与 3 是全文机制论证的支点，但 13 页正文没有附录也没有证明（C2）。Proposition 1 的渐近形式从 Eq. 4 出发不难信，Proposition 3 中那个与 X、N 无关的常数 C 和 log N / N 项则完全没有推导可查。
5. **bias–variance 分析是近似而非严格**。Eq. 21 是一个带 `≈` 的一阶 MSE 展开，且 staleness bias 项没有任何可估计的界；实际支撑「非单调」的是 Table 4 的 8 行经验数据（C11）。这个分析解释得通结果，但不能预测最优 K。
6. **无代码**（C14）。QQ 损失本身几行就能复现，但 LeWM 训练与 CEM 评测协议的完整复现成本不低。

**对领域的影响（推测）**：短期最可能被吸收的不是 QQWorld 这个模型，而是那条判据——LeJEPA / LeWM 之后一批「拿统计检验当正则」的工作都可以照着「梯度在尾部是否消失」重新审一遍自己的目标函数。cross-batch QQ 的 ranking-pool 与 backprop batch 解耦则是一个更工程化但更容易复用的技巧，在把 world model 往更大分辨率/更长序列 scale 时价值会放大。

## Mind Map

```mermaid
mindmap
  root((QQWorld))
    Problem
      LeWM 用 EP test 正则 latent 至 isotropic Gaussian
      仍出现明显重尾 tail rate 0.315 vs ref 0.10
      重尾把 dynamics 推向表示稀疏区 放大 rollout 误差
      症结在优化几何而非正则强度
    Method
      Sliced normality
        随机一维投影 + Cramer-Wold
      EP 诊断
        EP 等价于单位带宽 Gaussian kernel MMD
        Prop 1 恢复力 h·exp(-h²/4) 在 h=√2 后超指数衰减
      QQ matching loss
        order statistics 对齐 Gaussian quantile
        Prop 2 梯度 2(x_n − q_ρ(n)) 随偏差线性增长
        tie 边界排斥 排序不可微不构成障碍
        Prop 3 L_QQ→0 蕴含 L_EP→0 反向不成立
      Cross-Batch QQ
        FIFO 队列 detached 历史特征扩排序池 M=(K+1)N
        Eq21 近似 MSE 分解 variance 降 + staleness bias
    Results
      Planning 四环境 6 seeds 79.75 → 85.08
      逐环境 Reacher/OGBench 增益小于 std
      KS -15.8% EP -31.4% QQ RMSE 0.157→0.121
      tail rate 0.315→0.123
      Cross-batch N=32 K+1=3 达 83.50 显存降 73%
      仅在 LeWM 单一 backbone 验证 无代码
```

## Notes

- **可迁移的判据**：把「统计量能否分辨分布」与「统计量的梯度场是否处处有信息」拆开，是这篇最值钱的东西。同类可复查对象：任何把 kernel-based discrepancy（MMD、EP、energy distance）当训练正则的工作，其 kernel bandwidth 天然设定了一个「看不见的尾部区域」；相比之下 quantile / Wasserstein 系目标的梯度不随距离饱和。反过来讲，QQ 的线性增长梯度对**真正的离群观测**也会用力拉，这在数据本身就该有重尾时可能是错的先验——论文没有讨论这个失效条件。
- **一个可做的直接实验**：把 QQ 正则插到 DINO-WM 或 PLDM 上。这是论文自己声称的 drop-in 性质，也是当前最大的证据缺口（C9）；如果换 backbone 后增益消失，那说明「重尾」是 LeWM 特定训练配置的产物而非 EP 目标的普遍缺陷。
- **cross-batch 与 memory bank 的关系**：Eq. 17–18 的 FIFO detached 队列本质上是对比学习里 MoCo memory bank 的思路搬到 rank estimation 上，staleness bias 也是同一个问题。MoCo 用 momentum encoder 缓解 staleness——这里似乎也可以，论文未尝试。
- **与 vault 内相关笔记**：[[Papers/2506-VJEPA2]]（JEPA 系 world model）、[[DomainMaps/WorldModel]]（latent world model 与 planning 的地图）。LeWM (arXiv:2603.19312)、LeJEPA (arXiv:2511.08544)、DINO-WM (ICML 2025) 目前 vault 内无独立笔记，是这条线的前置缺口。
- **待核实**：Table 2 的 KS / EP 统计量是四环境平均但未给 std 与 seed 数；若要在 survey 中引用「QQWorld 的 EP 低于用 EP 训练的 LeWM」这一反直觉结论，应注明它只有单点数字支撑。
