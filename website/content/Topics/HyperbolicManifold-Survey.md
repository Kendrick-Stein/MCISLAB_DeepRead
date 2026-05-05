---
title: Hyperbolic Manifold Survey
tags: [hyperbolic, manifold, optimization, geometry, neural-network, embedding]
date_updated: "2026-04-28"
year_range: 2017-2026
papers_analyzed: 10
---
## Overview

Hyperbolic Geometry 与 Manifold Learning 将深度学习扩展到 curved spaces，利用非欧几何的特性处理 hierarchical data、scale-free networks、constrained optimization。核心洞察：**hyperbolic space 的 volume 随半径指数增长 ≈ tree/hierarchy 的结构特性**。

**核心理论**：
- **Poincaré Ball Model**: 常用 hyperbolic space 表示，边界处距离趋于无穷
- **Lorentz Model**: 另一种表示，计算更稳定
- **Riemannian Optimization**: 在 manifold 上的 gradient descent（考虑 curvature）

**整体趋势**：
1. 从 foundational theory（Poincaré Embeddings, 2017）走向 architecture integration（Hyperbolic GNNs, Transformers）
2. 应用场景从 knowledge graphs 扩展到 biological networks、NLP、robotics
3. Optimization efficiency 是主要瓶颈（Riemannian operations cost 高）

## 技术路线

### 1. Hyperbolic Embeddings (Foundational)

**代表工作**：[[1700-PoincareEmbeddings]] (🔥 Rating 5, NeurIPS 2017)

**核心洞察**: Hyperbolic space volume exponential growth ≈ tree depth exponential growth

**关键结果**：
- 5-dim Poincaré ≈ 100-dim Euclidean on WordNet
- 20x+ dimensionality reduction
- Link prediction SOTA

**理论基础**：
- Distance function: d(x,y) = arcosh(1 + 2||x-y||² / ((1-||x||²)(1-||y||²)))
- Riemannian SGD for hyperbolic gradient descent

### 2. Hyperbolic Neural Networks

**代表工作**：[[2400-HyperbolicNeuralNetworksSurvey]] (Rating 4)

**核心思路**: 将标准 neural layers 改写为 hyperbolic 版本

**技术挑战**：
- Linear operations 在 hyperbolic space 不自然（需要 tangent space 映射）
- Attention mechanism 的 hyperbolic extension 不成熟
- 初始化敏感

**应用**：
- Knowledge graph embeddings
- Word embeddings (semantic hierarchy)
- Hierarchical image classification

### 3. Hyperbolic Graph Neural Networks

**代表工作**：[[2400-HyperbolicGNN]] (Rating 3)

**核心思路**: 利用 hyperbolic geometry 处理 scale-free networks

**设计**：
- Hyperbolic message passing
- Hyperbolic attention
- Manifold-aware aggregation

**优势**：
- Scale-free networks（citation, social）上超过 Euclidean GNN
- 更好捕捉 hub node importance
- 参数效率更高

**局限**：
- Tangent space ↔ manifold 映射 cost 高
- 只在特定 graph types 上验证

### 4. Riemannian Optimization

**代表工作**：[[2400-RiemannianOptimization]] (Rating 3)

**核心思路**: 在 manifold constraints 上做 gradient descent

**关键 Manifolds**：
- **Stiefel Manifold**: Orthogonal matrices（{X: X^T X = I}）
- **Grassmann Manifold**: Subspaces（low-rank constraints）
- **Positive Definite Manifold**: Covariance matrices

**操作**：
- Riemannian gradient（在 tangent space 计算）
- Retraction（从 tangent space 回到 manifold）
- Natural gradient（与 information geometry 关联）

**应用**：
- Orthogonal RNNs（stability）
- Low-rank training（parameter efficiency）
- Positive definite estimation

### 5. Lorentz Graph Neural Networks

**代表工作**：[[2405-LorentzGNN]] (Rating 3)

**核心思路**: 将 Lorentz symmetry（相对论核心对称性）嵌入 GNN 架构

**设计**：
- Lorentz-equivariant message passing
- Respect boosts/rotations 等物理变换
- Particle physics graph structure 适配

**应用**：
- Particle jet classification（高能物理）
- Physics-inspired equivariance

**亮点**: Equivariance 提升泛化，减少 training data 需求

### 6. Hyperbolic Contrastive Learning

**代表工作**：[[2501-HyperbolicGraphContrastive]] (Rating 3)

**核心思路**: 在 hyperbolic space 中引入 contrastive learning，利用 hierarchical positive sampling

**关键设计**：
- Hierarchical positive sampling（按 hierarchy 采样 positives）
- Geometry-aware contrastive loss
- Curvature-aware gradient handling

**应用**：
- Node classification SOTA
- Graph property prediction
- Few-shot learning

### 7. Scalable Hyperbolic Knowledge Graphs

**代表工作**：[[2502-ScalableHyperbolicKG]] (Rating 3)

**核心思路**: 大规模 KG 的 scalable hyperbolic embedding

**工程突破**：
- Mini-batch training in hyperbolic space
- Efficient curvature learning（data-adaptive）
- Scalable RSGD 实现

**结果**：
- 百万实体 KG embedding feasible
- Link prediction improved
- Curvature learning stable

**意义**: Scalability 是 hyperbolic embedding 的核心痛点，mini-batch 是重要工程突破

### 8. Hyperbolic Attention Networks

**代表工作**：[[2503-HyperbolicAttention]] (Rating 3)

**核心思路**: Hyperbolic attention 机制捕捉 long-range dependencies

**设计**：
- Distance-based attention in hyperbolic space
- Hyperbolic distance better encodes hierarchical distance
- Geometry-aware positional encoding

**理论基础**：
- Attention weight = exp(-hyperbolic distance)
- Distance ≈ hierarchy distance

**应用**：
- Document-level translation improved
- Long-context language modeling better

**关联**: Hierarchical planning 可能受益于 hyperbolic attention

### 9. Accelerated Riemannian Optimization

**代表工作**：[[2502-AcceleratedRiemannianOptimization]] (Rating 3)

**核心思路**: 多 geometric constraints 同时优化

**挑战**：
- 多 constraints 的 manifold intersection
- Retraction 在 complex manifold 上复杂

**应用**：
- Orthogonal + low-rank 同时约束
- Positive definite + Stiefel 组合

### 10. Fixed-Rank Matrix Manifolds

**代表工作**：[[2502-RiemannianFixedRank]] (Rating 3)

**核心思路**: 研究 fixed-rank manifold 上不同 Riemannian metrics 的影响

**理论贡献**：
- Riemannian metrics family 分析
- Geometry-to-algorithms pipeline
- Metric 选择对收敛速度的影响

**应用**：
- Matrix completion
- Low-rank factorization

## Datasets & Benchmarks

| Dataset | 类型 | SOTA | 特点 |
|:--------|:-----|:-----|:-----|
| WordNet | Taxonomy | Poincaré Embeddings | Hierarchical structure |
| Freebase | Knowledge Graph | Hyperbolic KG Embeddings | Multi-relational |
| Citation Networks | Scale-free Graph | Hyperbolic GNN | Power-law degree |
| Social Networks | Scale-free Graph | Hyperbolic GNN | Hub nodes |

## Key Takeaways

1. **Hyperbolic ≈ Hierarchy**: 双曲几何的 exponential volume growth 天然匹配 hierarchical/tree-structured data
2. **维度效率惊人**: Poincaré Embeddings 证明 5-dim hyperbolic ≈ 100-dim Euclidean
3. **Scale-free networks benefit**: Hyperbolic GNN 在 power-law degree graphs 上表现优异
4. **Optimization 是瓶颈**: Riemannian operations cost 高，限制了大规模应用
5. **Curvature learning 是趋势**: Data-adaptive manifold curvature estimation 正在兴起

## Open Problems

1. **大规模 Scalability**: Riemannian optimization 在大规模 distributed training 上的效率？
2. **Attention in Hyperbolic Space**: Transformer 的 hyperbolic extension 如何设计？
3. **Curvature Learning**: 如何自动选择 manifold curvature？
4. **Dynamic Hierarchies**: 动态变化的 hierarchy 如何处理？
5. **Multimodal Hyperbolic**: VLM/Agent 的 hyperbolic embedding 应用？
6. **Optimization Speed**: 如何加速 Riemannian operations？

## 调研日志

- **调研日期**: 2026-04-28
- **论文统计**: 10 篇笔记（4 foundational + 6 近期 papers）
- **覆盖范围**: Hyperbolic embeddings, GNN, Contrastive Learning, Attention, Riemannian Optimization, Lorentz symmetry
- **近一个月论文**: 通过多 agent 搜索获取（部分 WebSearch 受限，使用 domain knowledge 补充）