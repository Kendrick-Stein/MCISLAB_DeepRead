---
name: blender-figure
description: >
  当 Supervisor 需要论文用的 3D 渲染图时使用：SMPL/FBX/OBJ mesh 渲染、多角色 teaser、
  方法对比（blue=ours/red=baseline）、3D skeleton 可视化、bbox+mesh。
  触发词："3D render"、"渲染"、"三维"、"SMPL"、"FBX"、"mesh render"、"Blender"、
  "teaser figure"、"skeleton render"。
  注意：纯 2D 结构图/流程图/架构图/pipeline 图不用本 skill——用 academic-diagram。
argument-hint: "<数据文件路径 FBX/OBJ/NPZ> [teaser/comparison/skeleton/module] [帧号列表]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Blender Figure — 论文 3D 渲染图

## Purpose

用 Blender 为学术论文生成出版级 3D 渲染图：多角色 teaser、单 mesh 模块插图、方法对比、
skeleton 可视化。输入是 mesh/动作数据文件（FBX/OBJ/NPZ）与构图需求，输出是渲染好的
JPEG/PNG 与可复现的 Python 脚本（基于本 skill 自带的 `blender_utils` 工具库）。

与其他图表 skill 的分工：
- **academic-diagram**：2D TikZ/draw.io 结构图、架构图、流程图（含 survey 配图）
- **tikz-figure-code**：TikZ 代码正确性地基
- **paper-figures**：matplotlib 数据图表
- **本 skill**：需要 3D 渲染的一切；Hybrid 模式下与 academic-diagram 协作（见 Steps 末尾）

**前置依赖**：Blender 3.x+（`BLENDER_PATH` 环境变量，或装在 `/Applications/`，或在 PATH）。

## Steps

### Step 1：理解可视化需求

确定 use case 并提取参数：

| Use Case | 说明 | 模板 |
|----------|------|------|
| **Teaser** | N 个角色沿 X 轴排布，渐变材质，地面 + 雾 + 轨迹线 | `templates/blender/template_teaser.py` |
| **Pipeline Module** | 单 mesh 透明背景渲染，供 TikZ 图嵌入 | `templates/blender/template_single_render.py` |
| **Comparison** | 2+ 角色不同配色（blue=ours, red=baseline） | `templates/blender/template_comparison.py` |
| **Skeleton** | 3D 关键点球体 + limb 圆柱 | `references/blender_recipes.md` Recipe D |
| **Bbox + Mesh** | mesh 外的线框 bbox | `references/blender_recipes.md` Recipe E |

从需求中提取：数据文件路径（FBX/OBJ/NPZ）、动画帧号、角色/实例数量、风格偏好（配色、相机角度、有无地面）。

### Step 2：与用户确认构图

用结构化摘要向用户确认（一轮通常足够）：

```
Figure type: Multi-character teaser
Data: motion.fbx, frames [1, 30, 60, 90, 120, 150]
Layout: 6 characters along X-axis, spacing 1.5m
Camera: Wide shot, focal 85mm / Lighting: Studio three-point
Material: Gradient blue clay / Ground: Checkerboard / Fog: Yes / Trajectory: Yes
Output: 2048x1024 JPEG
```

### Step 3：生成 Blender 脚本

1. Read `references/blender_api.md`（函数签名）+ `references/blender_recipes.md`（对应 recipe）。
2. 生成完整、自包含的 Python 脚本，import 自 `blender_utils.*`。
3. 脚本**必须支持 `--preview` flag**（two-pass 设计）：
   - **Preview**：Eevee 引擎（`set_eevee_renderer`）、1/2–1/4 分辨率、PNG、输出文件名加 `_preview` 后缀
   - **Final**：Cycles 引擎（`set_cycles_renderer`，samples 256+）、全分辨率
   - argparse 处理 `--` 之后的参数（`sys.argv[sys.argv.index('--') + 1:]`）
4. 写入工作目录（如 `render_teaser.py`），通过以下命令运行：
   ```bash
   bash skills/4-writing/blender-figure/scripts/render_blender.sh <script.py> -- [args]
   ```

### Step 4：Preview 渲染 + 自检

**永远先渲 preview，不许直接跑 Cycles。**

1. `bash skills/4-writing/blender-figure/scripts/render_blender.sh <script.py> -- --preview`
2. 渲染失败 → 读错误输出修脚本重试（常见问题见「Common Pitfalls」）。
3. 用 Read 查看 `*_preview.png`，自检：物体可见且位置正确 / 相机角度清晰 / 光照合理 /
   材质已应用（非默认灰）/ 背景干净 / 角色间距与布局正确。
4. 有问题 → 修脚本重渲 preview。**不给用户看坏图。**

### Step 5：用户确认 preview

1. 展示 preview 图，说明这是 Eevee 快速预览（final Cycles 渲染的光照/材质/抗锯齿会更好）。
2. 用 AskUserQuestion 确认：渲 final / 调整相机·光照·间距 / 换帧·换角色。
3. 用户要改 → 修脚本重渲 **preview**（不是 final），直到用户认可。

### Step 6：Final 渲染

用户认可 preview 后才执行：

1. `bash skills/4-writing/blender-figure/scripts/render_blender.sh <script.py>`（无 `--preview`，耗时长属正常）
2. Read 查看结果并展示给用户。
3. 还要调整 → 回 Step 5 的 preview 迭代，不要反复跑慢的 Cycles。

### Hybrid：TikZ 图嵌 3D 渲染模块

当 2D pipeline 图中某模块需要 3D 插图（如 "3D Pose Estimation" 框内放渲染 mesh）：

1. 用本 skill 的 **Pipeline Module** recipe 渲出透明背景 PNG（走 Step 3–6）。
2. 2D 图本身交给 **academic-diagram**（TikZ 代码正确性遵循 tikz-figure-code），在 TikZ 中引用：
   ```latex
   \node[inner sep=0pt] at (module_center) {\includegraphics[width=2.5cm]{rendered_module.png}};
   ```
3. 编译可用 `bash skills/4-writing/blender-figure/scripts/compile_tikz.sh <file.tex>`。

## Guard

- **禁止跳过 preview 直接 Cycles final 渲染**——迭代必须在便宜的 Eevee preview 上做。
- **不给用户看 broken figure**：渲染失败或自检不过时先修，不展示。
- 生成的脚本必须**完整、自包含、可独立运行**——不输出片段。
- 不修改 `blender_utils/` 工具库本身；版本兼容问题在生成脚本里用 try/except 处理
  （Principled BSDF 输入名在 Blender 3.x/4.x 间有变化，见 Common Pitfalls）。
- 2D 结构图需求不在本 skill 内处理——路由到 academic-diagram，不要用 Blender 硬画 2D。
- 学术论文审美：clean、professional、understated；拿不准时选更简单的方案。

## Verify

- [ ] Preview 与 final 渲染图都用 Read 亲眼查看过
- [ ] 材质已应用（无默认灰 mesh）、构图与用户确认的摘要一致
- [ ] Final 渲染前用户已认可 preview
- [ ] 交付物包含最终图像路径 + 可复现的 .py 脚本路径

## Common Pitfalls

1. **PYTHONPATH**：`render_blender.sh` 自动设置；手动跑需 `export PYTHONPATH=<skill目录>:$PYTHONPATH`。
2. **版本兼容**：Principled BSDF 输入名用 try/except——`Emission Color`(4.0+) vs `Emission`(3.x)、
   `Subsurface Weight` vs `Subsurface`、`Specular IOR Level` vs `Specular`、`Coat Weight` vs
   `Clearcoat`、`ShaderNodeMix`(3.4+) vs `ShaderNodeMixRGB`。
3. **透明背景 + 雾冲突**：`setup_mist_fog()` 的 compositor 会覆盖 Film > Transparent；要雾就
   `use_transparent_bg=False`。
4. **焦距**：30mm=广角（透视夸张）、50mm=标准、85mm=长焦（多角色 teaser 适用）。
5. **GPU**：`set_cycles_renderer()` 自动检测；慢或失败时 `prefer_gpu=False` 回退 CPU。
6. **材质顺序**：先 load mesh 再上材质，先 `mesh_obj.data.materials.clear()`。
7. **地面尺寸**：有雾的 teaser 用 `plane_size=100`（雾遮边缘），单角色特写用 `plane_size=10`。
8. **黑图/空图**：检查相机是否设置、物体是否在视野内。
