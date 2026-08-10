---
title: "Agentic Test-Time Scaling for WebAgents"
authors: ["Nicholas Lee", "Lutfi Eren Erdogan", "Chris Joseph John", "Surya Krishnapillai", "Michael W. Mahoney", "Kurt Keutzer", "Amir Gholami"]
institute: []
date_publish: 2026-02-12
venue: arXiv
tags: [web-agent, gui-agent, LLM]
url: "https://arxiv.org/abs/2602.12276"
arxiv_id: "2602.12276"
doi:
cite_key: lee2026agentic
code:
rating: 4
content_scope: full-text
verification_status: partial
date_added: 2026-08-10
---
## Summary

系统测量了 web agent 的 per-step test-time scaling 曲线：WebArena-Lite 上 majority vote 从 N=1 的 38.8% 涨到 N=10 的 43.2% 即饱和，N=20 反降到 43.0%（token 从 920K 翻到 1.8M），Plan-and-Act 架构同样非单调；LLM Arbiter 相对 majority vote 只多 0.4–0.8 点，且会推翻高一致性决策——至少发生一次 $\Delta_t>0.7$ override 的任务成功率 35.0%，零 override 的 46.9%。作者由此提出 CATTS：只在 vote 分布的 entropy（或 $1-\Delta_t$）超过阈值 $\tau$ 时才调用 arbiter，WebArena-Lite 47.9% / 745K token（对 majority vote 43.2% / 920K），GoBrowse 90.2% / 422K。真正的贡献是"compute 应该花在会改变决策的地方"这条可测量的分配原则，但 abstract 的 +9.1% 是对 ReAct N=1（96K token）而言，绝非 matched compute。

## Problem & Motivation

问题设得很干净：single-shot reasoning 的 test-time scaling 配方（多采样 + majority voting / verification）直接搬到 multi-step agent 上，就是"每步采 N 个候选动作再选一个"，这给出一个诱人的 compute 旋钮。作者指出这个直接类比有两处失配——**easy step 上的浪费**（大量步骤的下一步动作是显然的，继续填表、点提交，多采样只产生重复）与**high-variance step 上的失效**（票分散到多个互相竞争的动作时，计数本身不提供选择信号）。

这个 framing 的价值在于它把"agent harness 里的 compute 分配"当成一个可测量的经验问题，而不是又一个 prompting 技巧。作者没有训练任何东西——base agent 固定，只研究推理期怎么花 token。与之配套的第二个动机来自 overthinking 文献（Cuadron et al. 2025）：加一个 reranker LLM（论文称 arbiter）在候选集已经高度一致时会推翻共识，额外 compute 不是自动有益的。

论文对自己边界的表述是诚实的："我们假设一个固定的 base agent，只关注推理期 compute 怎么分配"，动机落在部署成本（latency、cost、energy）而非 SOTA。

## Method

**观测与动作.** ReAct prompting，base model 为 gpt-oss-120b，观测是清洗后的 HTML，动作空间 8 个 tool（click / type_text / hover / scroll / select_dropdown_option / search / go_back / exit），元素用注入 DOM 的整数 id 定位。5 个 error check（必须恰好一个 tool call、schema 校验、element 存在性、必须给 reasoning、重复动作循环检测），失败最多重试 5 次。

**Action clustering.** 每步采样 $N$ 个候选 $\tilde a_t^{(i)}\sim M(\cdot\mid o_t)$，解析成结构化动作后聚类，得到 $p_t(a)=n_t(a)/N$。关键前置步骤是一个轻量 **semantic deduplicator LLM**：把 "N/A" vs "Not found" 这类语义等价但文本不同的候选并入同一 cluster。这不是可选项——不做 dedup 时 GoBrowse 上 majority vote 会随 $N$ 增大而变差（$N{=}1$ 83.3% → $N{=}32$ 80.1%，C22），因为等价动作分票导致 argmax 选到错误的少数派。

**三种选择规则.**

| 规则 | 定义 | 每步 LLM 调用 |
|:--|:--|:--|
| Majority vote | $a_t=\arg\max_a p_t(a)$ | $N$ |
| Arbiter | $a_t=\textsc{Arbiter}(o_t,\mathcal A_t,\{n_t(a)\})$，与 agent 同模型，输入观测 + 每 cluster 一个代表动作 + 票数 | $N{+}1$ |
| Arbiter scaling | $K$ 个独立 selector 再做 majority vote | $N{+}K$ |

**不确定性统计.** 从 $p_t(\cdot)$ 算两个标量：entropy $H_t=-\sum_a p_t(a)\log p_t(a)$，top1/top2 margin $\Delta_t=p_t(a_t^{(1)})-p_t(a_t^{(2)})$。高共识 = 低 $H_t$ + 高 $\Delta_t$。

**CATTS 分配规则（Eq. 9）.** 只有一行：

$$a_t=\begin{cases}\arg\max_a p_t(a), & U_t\le\tau\\ \textsc{Arbiter}(o_t,\mathcal A_t,\{n_t(a)\}), & U_t>\tau\end{cases}$$

两个变体 $U_t^{(\mathrm{ent})}=H_t$、$U_t^{(\mathrm{mrg})}=1-\Delta_t$，$\tau$ 在 $\{0.2,0.3,\dots,0.8\}$ 上网格搜索。注意 CATTS **不调节 $N$**——它只 gate 第二阶段的 arbitration，候选采样预算在所有步骤上仍是均匀的。这一点对理解后面的 token 账很关键。

## Key Results

**1. 均匀 per-step scaling 的饱和点（Table 1，C1）**

| Budget | WA-Lite Success | WA Tokens | GoBrowse Success | GB Tokens |
|:--|--:|--:|--:|--:|
| $N{=}1$ | 38.8% | 96K | 86.9% | 47K |
| $N{=}5$ | 42.4% | 460K | 87.8% | 249K |
| $N{=}10$ | **43.2%** | 920K | **88.0%** | 481K |
| $N{=}20$ | 43.0% | 1.8M | 87.8% | 995K |

饱和点在 **$N{=}10$**：WebArena-Lite 上 $N{=}1\to10$ 拿到 +4.4 点，$N{=}10\to20$ 在 token 翻倍下**倒退 0.2 点**。GoBrowse 更早饱和——$N{=}1\to5$ 只有 +0.9，之后完全平坦且非单调。正文把 $N{=}10\to20$ 描述为 "produces only 0.2% additional gain"，但表里是 43.2%→43.0% 的下降，措辞与数据不符（C2）。Plan-and-Act 上同样非单调：$(P,A)$ 从 $(1,1)$ 到 $(2,4)$（8× 预算）GoBrowse 反而 83.3%→80.6%（C3）。

**2. Arbiter 相对 naive majority voting 的增量很小（Table 2，$N{=}5$，C4）**

| Method | WA Success | WA Tokens | GB Success | GB Tokens |
|:--|--:|--:|--:|--:|
| Majority vote | 42.4% | 460K | 87.8% | 249K |
| Arbiter $K{=}1$ | 42.8% | 442K | 88.6% | 227K |
| Arbiter scaling $K{=}5$ | 44.2% | 645K | 88.2% | 351K |
| Arbiter scaling $K{=}10$ | **44.6%** | 899K | 88.7% | 541K |
| Arbiter scaling $K{=}20$ | 42.0% | 1.4M | **89.6%** | 733K |

单次 arbitration 相对 majority vote 只有 **+0.4（WA）/ +0.8（GB）**。把 arbiter 本身 scale 到 $K{=}10$ 在 WA 拿到 44.6%，但那已是 899K token，与 majority vote $N{=}10$ 的 920K 基本持平——**matched compute 下 arbiter 的真实增量是 +1.4 点**（44.6 vs 43.2），不是表头看起来的 +2.2。

"arbitration is not uniformly beneficial" 这条结论**只在 WebArena-Lite 成立**：WA 上 $K{=}10\to20$ 从 44.6% 崩到 42.0%，而 GoBrowse 上 $K{=}20$ 恰恰是最好的 89.6%。但 GoBrowse 这一列并非单调——MV 87.8 → $K{=}1$ 88.6 → $K{=}5$ **88.2** → $K{=}10$ 88.7 → $K{=}20$ 89.6，只有端点在改善，Table 2 caption 的 "steady improvement" 是对非单调数据的平滑（C5）。完整网格（Appendix F Table 7，$N\times K$ 各 4 档）里，以 Appendix H caption 的 MV baseline 计，16 格中有 6 格低于同 $N$ 的 baseline、1 格持平（改用 Table 1 的 baseline 则为 12 格中 4 格）（C6）；最好的单格是 $N{=}3,K{=}20$ 的 45.7%，与 $N$、$K$ 都不存在单调关系。

**3. Arbiter 推翻高共识的代价（C8）**

作者取 495 个 task-run（= WebArena-Lite 165 任务 × 3 次运行，overall success 44.0% 恰为 always-arbitrate 的数字），按"是否在任一 $\Delta_t>0.7$ 的步骤上推翻多数票"分组：

| override 次数 | 任务成功率 |
|:--|--:|
| 0 | 46.9% |
| 恰好 1 | 36.6% |
| ≥ 2 | 29.6% |
| ≥ 1（合并） | 35.0% |

零 override 与 ≥1 override 差 **11.9 点**，$p=0.026$（Fisher's exact），呈剂量-反应，且"在全部五个网站类别上一致"。这是全文对该失败模式唯一的量化。

配套的分箱结果（Figure 4，C9）：按轨迹平均 entropy 分组比较 arbiter 与 majority vote 的净胜率差，**低熵区间 0.0–0.3 上 arbiter 净劣势 −4.4%**，更高熵区间净优势 **+4–6%**。

**4. 不确定性与 success 的"correlation"：论文没有报告任何相关系数或 AUC（C10）**

这一点必须明确——parent 问的 correlation / AUC 在原文中**不存在**。全文关于 "correlate with downstream success" 的全部证据是三块：(a) Figure 2 的定性曲线，成功轨迹早期 margin $\approx0.7$、entropy $\approx0.3$，失败轨迹全程更高熵更低 margin 且后期差距扩大（C11）；(b) 上面那个 Fisher exact $p=0.026$；(c) Figure 4 的分箱净优势。没有 Pearson/Spearman $r$，没有 ROC/AUC，没有把 $\bar H$、$\bar\Delta$ 当预测器做过任何判别性评估。abstract 里 "correlate with downstream success" 这个词是靠均值曲线分离支撑的。

Appendix I 给了票分布的形状（$N{=}10$、WA，C21）：约 **42% 的步骤 top-1 概率 > 0.9**，mean top-1 = 0.762；normalized entropy 双峰，均值 0.474，约 **40% 步骤零熵**、约 **49% 步骤熵 > 0.6**。这是"两个 regime"论断的实际经验基础。

**5. CATTS 主结果与 matched-compute 对照（Table 4，$N{=}10$，C13）**

| Method | WA Success | WA Tokens | GB Success | GB Tokens |
|:--|--:|--:|--:|--:|
| Majority vote | 43.2% | 920K | 88.0% | 481K |
| Always-arbitrate | 44.0% | 762K | 88.3% | 443K |
| CATTS ($H$, best $\tau$) | **47.9%** | 745K | **90.2%** | 422K |
| CATTS ($\Delta$, best $\tau$) | **47.9%** | 405K | **90.4%** | 372K |

按 token 预算重排成 accuracy-at-matched-compute（WebArena-Lite）：

| ~token 预算 | 方法 | Success |
|:--|:--|--:|
| 96K | ReAct $N{=}1$ | 38.8% |
| ~405–460K | Majority vote $N{=}5$ (460K) | 42.4% |
| | DeepConf bottom% $N{=}5$ (409K) | 42.6% |
| | **CATTS ($\Delta$) (405K)** | **47.9%**（与 Table 10 冲突，见 C15） |
| ~745–920K | Majority vote $N{=}10$ (920K) | 43.2% |
| | Always-arbitrate (762K) | 44.0% |
| | Arbiter scaling $K{=}10$ (899K) | 44.6% |
| | DeepConf avg-trace $N{=}10$ (828K) | 43.8% |
| | **CATTS ($H$) (745K)** | **47.9%** |
| 1.4–1.8M | Majority vote $N{=}20$ (1.8M) | 43.0% |
| | Arbiter scaling $K{=}20$ (1.4M) | 42.0% |
| | DeepConf avg-trace $N{=}20$ (1.8M) | 39.8% |

**在 matched compute 下 CATTS 确实领先**：745K 档位上 47.9% vs 同档最好的 44.6%，即 +3.3；且 majority vote 即使花到 1.8M（2.4×）仍停在 43.0%。最干净的一组是 always-arbitrate 762K/44.0% 对 CATTS($H$) 745K/47.9%——预算差 2%，精度差 3.9 点。论文也确实画了完整的 accuracy–compute frontier（Figure 5）。

**但 abstract 的 headline 不是 matched compute（C17）**："up to 9.1% over React" = 47.9% − 38.8%，而 ReAct $N{=}1$ 只花 96K token，CATTS 花 405–745K，即 **4.2–7.8× 更多 token**。abstract 把它与 "up to 2.3× fewer tokens than uniform scaling" 并列，但后者对标的是另一个 baseline（majority vote $N{=}10$ 的 920K÷405K≈2.27，C18）。两个数字来自两个不同的比较基准，并排放在一句话里会让人读成"更准且更省"，实际是"比最弱 baseline 更准（且贵 4–8×）"+"比最贵 baseline 更省"。

**6. 阈值选择（C14）** best-$\tau$ 的 47.9% 是在**评测集上**扫出来的（WA 用 $\tau{=}0.2$、GB 用 $\tau{=}0.5$），没有 held-out 调参集。论文给了无偏一些的数字：全阈值平均 **45.6%（+2.4）**。但这个数字无法从 Appendix H 复算：Table 9 的 $N{=}10$ entropy 列均值为 **46.17%（+3.0）**，45.6 只有在把 entropy 与 margin 两列合并（45.46）时才接近。论文没有说明 45.6 的口径。所以**该方法可辩护的增益是 +2.4 而非 +4.7**。

**7. 其他 baseline** RSA（Venkatraman et al. 2025）在最多 80 calls/step 下只到 43.6%，不如单轮 arbitration 的 44.0%；PlanRSA 崩到 35.2%，且 arbiter-select 与 random-select 完全同分，说明瓶颈在 plan 聚合本身（C23）。DeepConf 在 GoBrowse 上 avg-trace $N{=}20$ 达 **90.3% / 968K**，与 CATTS 的 90.2%/90.4% **精度基本持平**（C24）——即 CATTS 在 GoBrowse 上的优势是效率（2.3–2.6× 更省），不是精度上限。CATTS 对 DeepConf 的真实卖点是不需要 token-level logprob，因而适用于 API-only 模型。

**8. Benchmark 与 backbone 覆盖（C19、C20）** 两个评测：WebArena-Lite 165 任务 / 程序化判定 / 平均 8–12 步 / 成功率区间 40–47%；GoBrowse 采样 341 任务 / LLM-as-judge（Qwen3-VL-30B-A3B-Instruct）/ 平均 4–6 步 / 成功率区间 86–90%。judge 与人类约 90% 一致，但这是**引自 GoBrowse 原论文的 validation，本文没有自测**。**backbone 只有 gpt-aoss-120b 一个**，且 agent、arbiter、deduplicator 全部同模型——没有任何跨模型证据。两个 agent 架构（ReAct、Plan-and-Act）上验证过 scaling 非单调性，但 CATTS 本身只在 ReAct 上测。

## Evidence Ledger

> 状态来自一次独立 verifier pass（只给 primary source、claim package 与状态定义，不给本笔记的分析与优缺点判断）。`source-verified` 仅表示原文确实包含该信息，不表示结果已被独立复现。

> Status 列为占位（`pending`）：本笔记由 Finder 起草，按 Finder ≠ Verifier 约束不得自判 `source-verified`，等独立 verifier 逐条定位后回填。

| Claim ID | Claim | Type | Source locator | Evidence excerpt | Status |
|:--|:--|:--|:--|:--|:--|
| C1 | Table 1 均匀 majority-vote scaling：WA 38.8/42.4/43.2/43.0%（96K/460K/920K/1.8M），GB 86.9/87.8/88.0/87.8%（47K/249K/481K/995K） | number | Table 1 | "N=1 38.8% 96K 86.9% 47K ... N=20 43.0% 1.8M 87.8% 995K" | source-verified |
| C2 | 正文称 N=10→N=20 "produces only 0.2% additional gain"，Table 1 实为 43.2%→43.0%（下降 0.2 点），措辞与数据不符 | number | §3.2 vs Table 1 | "the doubling compute from N=10 to N=20 produces only 0.2% additional gain" | source-verified |
| C3 | Plan-and-Act 也非单调：GoBrowse (1,1) 83.3% → (2,4) 80.6%（8× 预算），(4,4) 81.5% | number | Appendix E Table 6 | "performance decreases from 83.3% to 80.6% when moving from budget C=1 to C=8" | source-verified |
| C4 | Table 2（N=5）：MV 42.4%/460K；Arbiter K=1 42.8%/442K；K=5 44.2%/645K；K=10 44.6%/899K；K=20 42.0%/1.4M（WA） | number | Table 2 | "Majority vote (N=5) 42.4% 460K ... Arbiter scaling (K=20) 42.0% 1.4M" | source-verified |
| C5 | arbiter scaling 的崩塌只在 WA 出现；GoBrowse 上 K=20 最优（89.6%），但该列本身非单调（87.8→88.6→88.2→88.7→89.6），caption 的 "steady improvement" 是平滑后的描述 | comparison | Table 2 + caption | "On GoBrowse, scaling yields steady improvement from 88.6% (K=1) to 89.6% (K=20)" | source-verified（原表述"全程单调"被独立 verifier 判为 contradicted，已改） |
| C6 | 完整 N×K 网格中，以 Appendix H caption 的 MV baseline 计 16 格有 6 格低于同 N baseline、1 格持平（改用 Table 1 baseline 则为 12 格中 4 格）；最优单格为 N=3,K=20 的 45.7% | number | Appendix F Table 7 + Table 9 caption | "N=3 43.0% 41.2% 43.4% 45.7% ... N=20 43.2% 42.8% 44.0% 43.6%" | source-verified（baseline 口径由独立 verifier 补齐） |
| C7 | Appendix H caption 的 MV baseline（N=5 42.8%、N=20 43.8%）与 Table 1（42.4%、43.0%）不一致 | number | Table 9/10 caption vs Table 1 | "Baseline majority vote success rates: N=3: 40.2%, N=5: 42.8%, N=10: 43.2%, N=20: 43.8%" | source-verified |
| C8 | 495 task-run 上，零高共识 override 任务成功 46.9%，≥1 次 35.0%，差 11.9 点，p=0.026 Fisher exact；剂量-反应 46.9/36.6/29.6 | number+causal-mechanism | §4.1 + Figure 3 | "succeed at 46.9%, compared to 35.0% ... a significant 11.9% difference (p=0.026, Fisher's exact test)" | source-verified |
| C9 | 按轨迹平均 entropy 分箱：低熵 0.0–0.3 时 arbiter 净劣势 −4.4%，高熵时净优势 +4–6% | number | §4.1 + Figure 4 | "At low entropy (0.0–0.3), the arbiter shows a net disadvantage of −4.4%" | source-verified |
| C10 | 全文未报告任何相关系数（Pearson/Spearman）或 AUC/ROC；"correlate with downstream success" 仅由 Figure 2 均值曲线、Fisher p 值与分箱净优势支撑 | sota-novelty | 全文（§4.1、Abstract、Figures 2–4） | "vote-derived uncertainty is correlated with task success and can guide dynamic compute allocation" | source-verified |
| C11 | Figure 2：成功轨迹早期 margin ≈0.7、entropy ≈0.3；失败轨迹全程更高熵更低 margin，后期差距扩大 | number | Figure 2 caption | "Successful tasks maintain high margins (≈0.7) and low entropy (≈0.3) early on" | source-verified |
| C12 | CATTS 规则：U_t ≤ τ 走 argmax，U_t > τ 调 arbiter；U=H_t 或 1−Δ_t；τ 网格 {0.2..0.8}；arbiter 触发约 40–60% 步骤 | causal-mechanism | Eq. 9–10 + §4.3 | "the selector is invoked on approximately 40–60% of steps on average" | source-verified |
| C13 | Table 4（N=10）：WA MV 43.2%/920K，always-arbitrate 44.0%/762K，CATTS(H) 47.9%/745K，CATTS(Δ) 47.9%/405K；GB 88.0/481K, 88.3/443K, 90.2/422K, 90.4/372K | number | Table 4 | "CATTS (H, best τ) 47.9% 745K 90.2% 422K / CATTS (Δ, best τ) 47.9% 405K 90.4% 372K" | source-verified |
| C14 | best-τ 在评测集上选取（WA τ=0.2、GB τ=0.5），全文无 held-out 调参集；论文自报全阈值平均 45.6%（+2.4），但按 Table 9 的 N=10 entropy 列自算为 46.2%（+3.0），两者对不上 | benchmark-setting | §4.3 + Table 4 caption + Appendix H Table 9 | "Averaging across all thresholds in our sweep, CATTS achieves 45.6%, which is still a consistent 2.4% gain" | source-verified（自报值可核；45.6 不可由 Table 9 复算，独立 verifier 复算为 46.17%） |
| C15 | Table 4 报 CATTS(Δ) 在 N=10 达 47.9%，但 Appendix H Table 10 的 N=10 列最高只有 46.1%（τ=0.4 与 0.8）——直接矛盾 | number | Table 4 vs Table 10 | Table 10 N=10 列 "45.5% 42.4% 46.1% 44.8% 44.2% 44.2% 46.1%" | source-verified |
| C16 | Table 8 记 CATTS 为 ~7 calls/step，但按 N=10 + 40–60% arbitration 应为 ≈10.5；论文未解释 | number | Appendix G Table 8 | "CATTS (entropy, best) 10 1 – 47.9% ∼7" | source-verified |
| C17 | abstract 的 "up to 9.1% over React" = 47.9%−38.8%（WA），而 ReAct N=1 仅 96K token、CATTS 405–745K，非 matched compute | comparison | Abstract + Table 1 + Table 4 | "improves performance on WebArena-Lite and GoBrowse by up to 9.1% over React" | source-verified |
| C18 | "up to 2.3× fewer tokens than uniform scaling" 对标 majority vote N=10 的 920K vs CATTS(Δ) 405K（比值 2.27） | comparison | Abstract + Table 4 + §4.3 | "reducing the number of tokens by 56% compared to majority voting (920K tokens)" | source-verified |
| C19 | 唯一 backbone 为 gpt-oss-120b，agent 与 arbiter 同模型；评测为 WebArena-Lite 165 任务（程序化）与 GoBrowse 采样 341 任务（Qwen3-VL-30B-A3B-Instruct 判分） | benchmark-setting | §3.1 + §3.3 | "uses gpt-oss-120b as the base model ... the arbiter uses the same model as the agent" | source-verified |
| C20 | Appendix C：WA 平均 8–12 步、成功率 40–47%；GB 平均 4–6 步、成功率 86–90%；judge 与人类约 90% 一致系引自 GoBrowse 原论文而非本文自测 | benchmark-setting | Appendix C | "Based on validation studies reported in that work, the judge achieves approximately 90% agreement" | source-verified |
| C21 | 票分布（N=10, WA）：~42% 步骤 top-1 prob > 0.9，mean top-1 = 0.762；normalized entropy 双峰均值 0.474，~40% 零熵、~49% > 0.6 | number | Appendix I + Figure 6 caption | "∼42% of steps have near-deterministic consensus (top-1 probability >0.9), and mean top-1 probability is 0.762" | source-verified |
| C22 | semantic dedup 是必要前置：无 dedup 时 GoBrowse N=1 83.3% → N=32 80.1%；dedup 后 N=8 由 83.3% 升至 84.5%，Reddit 84.8%→94.9% | number | Appendix D Table 5 | "accuracy drops from 83.3% at N=1 to 80.1% at N=32" | source-verified |
| C23 | RSA 最多 80 calls/step 只到 43.6%，低于单轮 arbitration 的 44.0%；PlanRSA 35.2%，arbiter-select 与 random-select 同分 | number+comparison | Appendix G Table 8 | "RSA 16 4 4 43.6% 80 ... PlanRSA (arbiter select) 35.2% ... (random select) 35.2%" | source-verified |
| C24 | GoBrowse 上 DeepConf avg-trace N=20 达 90.3%/968K，与 CATTS 的 90.2%/90.4% 精度持平；CATTS 优势在 token（372–422K） | comparison | Table 3 + Table 4 | "on GoBrowse, average trace at N=20 reaches 90.3%" | source-verified |
| C25 | Table 4 caption 把 405K 说成 GoBrowse 的数字，但表内 405K 属 WebArena-Lite 列（GB 的 Δ 变体是 372K） | number | Table 4 caption vs Table 4 | "achieves similar performance on GoBrowse (90.4%) while using only 405K tokens" | source-verified |
| C26 | 全文主表无 error bar / CI，仅称 "averaged across three different seeds"；WA 165 任务下 1 个任务 = 0.61 点 | benchmark-setting | §3.1 + Tables 1/2/4 | "All results are averaged across three different seeds unless otherwise noted." | source-verified |
| C27 | 论文把 WebArena-Lite 引作 (Koh et al., 2024)，该文实为 VisualWebArena——引用错配 | benchmark-setting | §3.1 + References | "We evaluate on WebArena-Lite (Koh et al., 2024), which has 165 tasks" | source-verified |
| C28 | Appendix J 的旗舰 failure case 报 H_t≈0.3、Δ_t=0.6，低于其自身 Δ_t>0.7 的 high-consensus 判据 | number | Appendix J + Figure 7 | "the normalized entropy is low (Ht≈0.3) and the margin is high (Δt=0.6)" | source-verified |

## Strengths & Weaknesses

**值得记住的三件事.** 其一，这是目前对"web agent 每步采样何时饱和"最直接的一条测量曲线（$N{=}10$，之后倒退），并且在两种 agent 架构上都成立——对 harness 设计而言这是一个可以直接引用的经验边界。其二，"高共识时不要让 reranker 介入"这条约束被量化了：46.9% vs 35.0%、剂量-反应、$p=0.026$。多数 agent 系统论文只会定性地说 verifier "有时会犯错"。其三，分配规则简单到只有一个阈值判断，不需要 token-level logprob（这是它相对 DeepConf 唯一站得住的结构性优势），也不需要训练——这符合"simple, scalable"的取向。

**证据强度撑不住 headline.** 可辩护的增益是全阈值平均的 **+2.4**，不是被反复引用的 +4.7 / +9.1。$\tau$ 在评测集上选，没有 held-out split；主表没有 error bar；WebArena-Lite 上 1 个任务 = 0.61 点，而单看 Table 9 里 $N{=}10$ 一列随 $\tau$ 的波动就有 44.2–47.9（3.7 点），这个波动幅度本身就吞掉了大部分声称的增益。abstract 把两个不同基准的数字（对 ReAct 的 +9.1%、对 uniform scaling 的 2.3× token）并排陈述，会让读者误读为同一比较。

**token 账目未被拆解，且与 call 数对不上.** 最实质的问题在这里。CATTS 按 Eq. 9 并不减少候选采样量（仍是 $N{=}10$），只是少调 arbiter；那么它在 WA 上的 405K / 745K 怎么会低于 majority vote $N{=}10$ 的 920K？唯一自洽的解释是 token 按 **per-task 总量**统计，而更好的决策让轨迹更早终止（同一逻辑也解释了 always-arbitrate 明明每步多一次调用却只花 762K）。如果成立，"2.3× fewer tokens" 就主要是**成功导致的短轨迹**这一 outcome-mediated 效应，而非 per-step 分配本身的节省——论文从头到尾没有报告轨迹长度，也没做这个拆解。更糟的是 Table 8 把 CATTS 记为 ~7 calls/step，这在 $N{=}10$ 加 40–60% arbitration 下算术上不可能（应为 ≈10.5），论文未加解释（C16）。

**内部一致性有多处裂缝.** Table 4 的 CATTS($\Delta$) @ $N{=}10$ = 47.9% 被 Table 10 同格的 46.1% 上限直接否定（C15）；Appendix H 的 MV baseline 与 Table 1 对不上（C7）；Table 4 caption 把 WA 的 405K 记成 GoBrowse（C25）；正文把 −0.2 说成 "+0.2 gain"（C2）。这些单个都不致命，累积起来会让人对没有原始数据可核的数字（尤其是 token 列）打折扣。

**override 分析是观察性的，且样本不独立.** 495 = 165 × 3，同一批任务重复三次，Fisher's exact 的独立性前提不成立。更要紧的是混淆：override 次数与轨迹步数正相关，而长轨迹本身就更容易失败——"override 越多成功率越低"的剂量-反应完全可以由"难任务步数多、既更容易触发 override 也更容易失败"解释。要支撑因果解读需要的是同一步上 override / 不 override 的配对反事实（或直接随机化 gate），论文没有做。作者用 "predicts" 而非 "causes" 措辞尚属克制，但 Figure 3 的呈现方式邀请因果读法。

**泛化证据比看起来窄.** 只有一个 backbone（gpt-oss-120b，还身兼 arbiter 与 deduplicator——同源模型的一致性偏差没有被讨论）。名义上两个 benchmark，但按 Table 5 的分站点表头（GitLab / Map / Reddit / Shopping / Shopping Admin），GoBrowse 与 WebArena-Lite 跑在**同一套五个 WebArena 站点**上，所以这是同一环境族上的两个任务分布，不是两个独立环境（此为笔记依表头推断）。而且关键结论在两者间并不一致：arbiter scaling 的崩塌只出现在 WA，GoBrowse 上 $K$ 一路涨到 20 都在改善（C5）。

**对领域的影响.** 我认为这篇的持久价值在于"饱和点 + 高共识 override 代价"这两条测量，而不是 CATTS 本身——单阈值 gate 是这些测量的最小可行推论，任何人拿到同样的曲线都会写出 Eq. 9。真正被这篇打开的问题是：既然 42% 的步骤 top-1 概率 > 0.9，为什么还要在这些步骤上采满 $N{=}10$？把 gate 前移到**候选采样阶段**（自适应 $N$、逐个采样直到 margin 达标）在信息论上明显比只 gate 第二阶段的 arbitration 更有杠杆，而这恰恰是本文没做的部分。

## Mind Map

```mermaid
mindmap
  root((CATTS))
    Problem
      per-step uniform scaling saturates
      easy steps waste compute
      arbiter overrules consensus
    Method
      sample N then cluster
      semantic dedup before voting
      entropy and top1-top2 margin
      gate arbiter when U over tau
    Results
      WebArena-Lite saturates at N=10
      arbiter gains only 0.4 to 0.8
      high-consensus override 46.9 to 35.0
      CATTS 47.9 at 745K tokens
      threshold-averaged gain only 2.4
    Caveats
      single backbone gpt-oss-120b
      no correlation coefficient or AUC
      tau tuned on eval set
      token account not reconciled
