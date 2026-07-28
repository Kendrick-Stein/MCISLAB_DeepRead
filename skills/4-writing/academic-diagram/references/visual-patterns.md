# 视觉模式库：高质量 TikZ 绘制范例

本文件提供具体的 TikZ 代码片段，展示如何绘制**丰富、精细**的视觉元素。
生成图时**必须参考这些模式**，不要退化为"一个框写两行字"的简陋画法。

## 模式 1：节点内部子结构（hero 模块）

核心模块不能只写文字——必须展开内部组件。用一个大外框 + 内部多个小节点。

```latex
% ── hero 模块示例：Multi-Head Attention 内部结构 ──
\node[blue_node, minimum width=6cm, minimum height=4.5cm, inner sep=8pt] (mha) at (0,0) {};
\node[font=\footnotesize\bfseries, anchor=north] at (mha.north) {Multi-Head Attention};

% 内部子节点（用 smallbox 风格，紧凑排列在 hero 框内）
\node[blue_node, minimum width=1.2cm, minimum height=0.6cm, font=\scriptsize]
    (q) at ([yshift=-1.8cm, xshift=-1.8cm]mha.north) {Linear};
\node[blue_node, minimum width=1.2cm, minimum height=0.6cm, font=\scriptsize]
    (k) at ([yshift=-1.8cm]mha.north) {Linear};
\node[blue_node, minimum width=1.2cm, minimum height=0.6cm, font=\scriptsize]
    (v) at ([yshift=-1.8cm, xshift=1.8cm]mha.north) {Linear};
\node[font=\scriptsize, anchor=north] at (q.south) {$\mathbf{Q}$};
\node[font=\scriptsize, anchor=north] at (k.south) {$\mathbf{K}$};
\node[font=\scriptsize, anchor=north] at (v.south) {$\mathbf{V}$};

% 注意力公式（嵌在框内）
\node[font=\scriptsize, anchor=south] at ([yshift=0.3cm]mha.south)
    {$\text{Attention} = \text{softmax}\!\left(\frac{\mathbf{Q}\mathbf{K}^\top}{\sqrt{d_k}}\right)\mathbf{V}$};
```

**要点**：hero 框 minimum width ≥ 5cm，minimum height ≥ 3.5cm，内含 ≥ 3 个子节点 + 公式。

## 模式 2：N×N 热力图/注意力矩阵

用 `\fill` 循环画彩色方格，不要用节点。适合注意力权重、邻接矩阵、混淆矩阵。

```latex
% ── 5×5 注意力热力图 ──
% 数据：0=浅色, 1=深色
\def\heatdata{
    {1.0, 0.3, 0.1, 0.2, 0.0},
    {0.2, 0.9, 0.4, 0.1, 0.1},
    {0.0, 0.3, 1.0, 0.5, 0.2},
    {0.1, 0.0, 0.4, 0.8, 0.3},
    {0.0, 0.1, 0.2, 0.3, 1.0}
}
\foreach \row [count=\i from 0] in \heatdata {
    \foreach \val [count=\j from 0] in \row {
        \fill[drawBlueLine!\val!white, draw=white, line width=0.3pt]
            ({\j*0.5}, {-\i*0.5}) rectangle ++(0.5, 0.5);
    }
}
% 行列标签
\foreach \label [count=\i from 0] in {$v_1$,$v_2$,$v_3$,$v_4$,$v_5$} {
    \node[font=\tiny, anchor=east] at (-0.05, {-\i*0.5+0.25}) {\label};
    \node[font=\tiny, anchor=south] at ({\i*0.5+0.25}, 0.05) {\label};
}
% 色标
\shade[left color=white, right color=drawBlueLine] (0,-3.0) rectangle (2.5,-2.7);
\node[font=\tiny, anchor=north west] at (0,-3.0) {Low};
\node[font=\tiny, anchor=north east] at (2.5,-3.0) {High};
```

**要点**：方格尺寸 0.4-0.6cm，加行列标签，加色标（Low/High）。整个矩阵 ≥ 2.5cm×2.5cm。

## 模式 3：嵌入式折线图（训练曲线/收敛曲线）

在框内画坐标轴 + 贝塞尔曲线，有轴标签和图例。

```latex
% ── 训练损失曲线（嵌在 5cm×3.5cm 的框内）──
% 坐标轴
\draw[-{Stealth[length=3pt]}, line width=0.4pt] (0,0) -- (0,2.5)
    node[left, font=\tiny] {Loss};
\draw[-{Stealth[length=3pt]}, line width=0.4pt] (0,0) -- (4.0,0)
    node[below, font=\tiny] {Epoch};

% 训练曲线（蓝色，下降后趋稳）
\draw[drawBlueLine, line width=0.8pt]
    (0.1,2.2) .. controls (0.8,1.4) and (1.5,0.8) ..
    (2.5,0.5) .. controls (3.0,0.4) and (3.5,0.35) .. (3.8,0.3);

% 验证曲线（红色，略高于训练）
\draw[drawRedLine, line width=0.8pt, dashed]
    (0.1,2.3) .. controls (0.8,1.6) and (1.5,1.0) ..
    (2.5,0.7) .. controls (3.0,0.6) and (3.5,0.55) .. (3.8,0.5);

% 图例
\draw[drawBlueLine, line width=0.8pt] (2.8,2.3) -- (3.3,2.3)
    node[right, font=\tiny] {Train};
\draw[drawRedLine, line width=0.8pt, dashed] (2.8,2.0) -- (3.3,2.0)
    node[right, font=\tiny] {Val};

% 刻度
\foreach \y/\lab in {0.5/0.5, 1.0/1.0, 1.5/1.5, 2.0/2.0} {
    \draw[gray, line width=0.2pt] (-0.05,\y) -- (0.05,\y);
    \node[font=\tiny, anchor=east] at (-0.08,\y) {\lab};
}
```

**要点**：轴用 Stealth 箭头，曲线用 `.. controls ..` 贝塞尔，两条线不同颜色+线型，加图例，加刻度。

## 模式 4：嵌入式柱状图（对比实验）

```latex
% ── 准确率对比柱状图 ──
% 坐标轴
\draw[-{Stealth[length=3pt]}, line width=0.4pt] (0,0) -- (0,2.8)
    node[left, font=\tiny, rotate=90, anchor=south] {Accuracy (\%)};
\draw[line width=0.4pt] (0,0) -- (4.5,0);

% 柱子（3 组对比）
\fill[drawBlueFill, draw=drawBlueLine, line width=0.4pt]
    (0.3,0) rectangle (0.9, 2.0);  % 85.1%
\fill[drawGreenFill, draw=drawGreenLine, line width=0.4pt]
    (1.3,0) rectangle (1.9, 2.2);  % 87.4%
\fill[drawRedFill, draw=drawRedLine, line width=0.4pt]
    (2.3,0) rectangle (2.9, 2.5);  % 89.7% (ours)
\fill[drawGreyFill, draw=drawGreyLine, line width=0.4pt]
    (3.3,0) rectangle (3.9, 2.7);  % 93.2%

% 数值标注
\node[font=\tiny, drawBlueLine] at (0.6, 2.15) {85.1};
\node[font=\tiny, drawGreenLine] at (1.6, 2.35) {87.4};
\node[font=\tiny\bfseries, drawRedLine] at (2.6, 2.65) {89.7};
\node[font=\tiny, drawGreyLine] at (3.6, 2.85) {93.2};

% x 轴标签
\node[font=\tiny, anchor=north] at (0.6,-0.05) {Single};
\node[font=\tiny, anchor=north] at (1.6,-0.05) {Multi};
\node[font=\tiny, anchor=north] at (2.6,-0.05) {Ours};
\node[font=\tiny, anchor=north] at (3.6,-0.05) {Teacher};

% y 轴刻度
\foreach \y/\lab in {0.5/80, 1.0/85, 1.5/90, 2.0/95} {
    \draw[gray!50, line width=0.15pt] (0,\y) -- (4.5,\y); % 网格线
    \node[font=\tiny, anchor=east] at (-0.05,\y) {\lab};
}
```

**要点**：柱宽 0.5-0.7cm，柱间距 0.3-0.5cm，数值标注在柱顶上方，y 轴加网格线。Ours 柱用强调色。

## 模式 5：特征矩阵/权重矩阵可视化

```latex
% ── 特征矩阵 X（8×4），用颜色深浅表示值大小 ──
\node[font=\scriptsize\bfseries, anchor=south] at (1.0, 2.2)
    {Feature Matrix $\mathbf{X}$ ($8 \times 4$)};
% 列标签
\foreach \col [count=\j from 0] in {Deg, Chg, Hyb, $\sigma$} {
    \node[font=\tiny] at ({\j*0.5+0.25}, 2.0) {\col};
}
% 行标签 + 色块
\foreach \row [count=\i from 0] in {$c_1$,...,$c_8$} {
    \node[font=\tiny, anchor=east] at (-0.05, {1.75-\i*0.45}) {\row};
    \foreach \j in {0,...,3} {
        \pgfmathsetmacro{\intensity}{rnd*70+20}
        \fill[drawGreenLine!\intensity!white, draw=white, line width=0.2pt]
            ({\j*0.5}, {1.55-\i*0.45}) rectangle ++(0.5, 0.4);
    }
}
```

## 模式 6：分子图/网络图结构

```latex
% ── 分子图：5 个原子节点 + 键 ──
\foreach \name/\x/\y/\color/\label in {
    a1/0/0/drawBlueLine/C,
    a2/1.2/0.6/drawBlueLine/C,
    a3/1.2/-0.6/drawBlueLine/C,
    a4/2.4/0/drawRedLine/O,
    a5/-1.0/0.5/drawGreenLine/N
} {
    \node[circle, draw=\color, fill=\color!15, line width=0.6pt,
          minimum size=0.5cm, font=\tiny\bfseries] (\name) at (\x,\y) {\label};
}
% 化学键
\draw[line width=0.6pt] (a1) -- (a2);
\draw[line width=0.6pt] (a1) -- (a3);
\draw[double, line width=0.4pt] (a2) -- (a4); % 双键
\draw[line width=0.6pt] (a1) -- (a5);
% 键类型图例
\draw[line width=0.6pt] (-1.5,-1.2) -- (-1.0,-1.2) node[right, font=\tiny] {Single};
\draw[double, line width=0.4pt] (-1.5,-1.5) -- (-1.0,-1.5) node[right, font=\tiny] {Double};
```

## 模式 7：雷达图（多维评估）

```latex
% ── 5 维雷达图 ──
\def\radarN{5}
\def\radarR{1.5}  % 半径
\def\radarLabels{{"Accuracy","Speed","Memory","Scalability","Privacy"}}
% 网格
\foreach \level in {0.33, 0.66, 1.0} {
    \draw[gray!30, line width=0.2pt]
        \foreach \i in {0,...,4} {
            ({90+\i*360/\radarN}:{\level*\radarR}) --
        } cycle;
}
% 轴
\foreach \i in {0,...,4} {
    \draw[gray!50, line width=0.3pt] (0,0) -- ({90+\i*360/\radarN}:\radarR);
    \pgfmathsetmacro{\lab}{\radarLabels[\i]}
    \node[font=\tiny, anchor={mod(90+\i*72+180,360)>180?"north":"south"}]
        at ({90+\i*72}:{\radarR+0.3}) {\lab};
}
% Ours（实线填充）
\def\oursData{0.9, 0.85, 0.7, 0.8, 0.95}
\fill[drawGreenFill!40, draw=drawGreenLine, line width=0.7pt]
    \foreach \val [count=\i from 0] in \oursData {
        ({90+\i*72}:{\val*\radarR}) --
    } cycle;
% Baseline（虚线）
\def\baseData{0.8, 0.6, 0.5, 0.7, 0.4}
\draw[drawRedLine, line width=0.6pt, dashed]
    \foreach \val [count=\i from 0] in \baseData {
        ({90+\i*72}:{\val*\radarR}) --
    } cycle;
```

## 模式 8：Stage 标题标签

每个 zone 左上角放一个带颜色的圆角小标签。

```latex
% Stage 标签（放在 zone 背景左上角内侧）
\node[fill=drawBlueLine!80, text=white, font=\scriptsize\bfseries,
      rounded corners=2pt, inner sep=3pt, anchor=north west]
    at ([xshift=5pt, yshift=-5pt]zone_nw) {Stage 1: Encoding};
```

## 模式 9：底部 Pipeline 总结条

在图的最底部放一条横向链条，总结整个流程。

```latex
% ── 底部 pipeline 总结条 ──
\foreach \stage/\color/\x in {
    Input/drawBlueFill/0,
    Encode/drawGreenFill/2.8,
    Process/drawOrangeFill/5.6,
    Predict/drawPurpleFill/8.4,
    Output/drawRedFill/11.2
} {
    \node[fill=\color, draw=\color!80!black, rounded corners=2pt,
          minimum width=2.2cm, minimum height=0.5cm,
          font=\tiny\bfseries] (pipe_\stage) at (\x, -12) {\stage};
}
% 连接箭头和标注
\foreach \a/\b/\lab in {
    Input/Encode/{STFT},
    Encode/Process/{$\mathbf{h}$},
    Process/Predict/{$\hat{y}$},
    Predict/Output/{Post}
} {
    \draw[-{Stealth[length=3pt]}, line width=0.5pt, gray]
        (pipe_\a.east) -- (pipe_\b.west)
        node[midway, above, font=\tiny, gray] {\lab};
}
```

## 使用原则

1. **每张图至少用 3 种以上模式** — 不能全是纯文字框
2. **hero 模块必须用模式 1** — 内含子结构 + 公式
3. **有数值对比就用模式 4（柱状图）或模式 3（曲线图）** — 不要只写数字
4. **有矩阵/权重就用模式 2（热力图）或模式 5（特征矩阵）** — 不要只写维度
5. **复杂图底部加模式 9（pipeline 总结条）** — 帮读者理清主线
6. **zone 标签用模式 8** — 每个分区左上角标明 Stage 名
