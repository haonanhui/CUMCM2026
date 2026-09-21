# 科研论文生图 Skill 强化规范（JFS 中文适配）

版本：1.0  
日期：2026-09-21  
本地适配：用户本轮纠正执行目标为 math-contest-native。本副本 §1、§10 的 app/config/catalog 落点由 `.agents/skills/cumcm-scientific-figure/` 原生唯一真源与 Codex/DSH loader 验收替代，不改 app 投影。其余参考风格与 A–F 验收要求保持。原生论文最终使用仍受 `FIGURES_ZH.md` 的 12 pt 和正文数学字体合同约束；JFS profile 用于参考及专项回归，不静默替代该合同。

目标：将论文生图能力升级为可复用、可验证的中文科研绘图 skill。视觉基线来自 Zhang, He & Zhang, *Journal of Fluids and Structures* 92 (2020) 102787 的图形组织与矢量样式；这是**参考论文反推的风格 profile**，不声称为 Elsevier/JFS 官方强制规范。

参考原文（本机）：`D:\Downloads\1-s2.0-S0889974619303706-main.pdf`

## 1. 归属与改动边界

- **禁止原地修改** `code/skills/**`、`code/skills-collected/**`、vendor 与其他第三方资产。
- 可读取并借鉴：
  - `code/skills-collected/paper-figure-style-router/**`
  - `code/skills/paper-diagram/**`
- 强化后的权威实现应落在 app 自有层，优先新建：
  - `config/skills/cumcm-scientific-figure/SKILL.md`
  - `config/skills/cumcm-scientific-figure.json`
  - 其自有 references/scripts/tests 按需放在同一 skill 目录或项目自有测试目录。
- 若发现已有 app 自有 skill 已覆盖同一职责，可在不破坏兼容性的前提下重构；不得复制第三方正文后宣称原创。
- 风格配置、字体、颜色、线宽、导出、QA 应集中管理，避免散落硬编码。

建议 style profile id：`jfs_zh_reference_v1`。

## 2. 核心视觉规范

### 2.1 总体气质

- 白底、黑色坐标框、serif 字体、高数据墨水比。
- 图内不放装饰性大标题；默认无背景 grid。
- 颜色克制，线型/marker/fill state 与颜色共同编码信息。
- 多子图严格对齐，panel 使用 `(a) (b) (c)...`。
- 图例紧凑、无边框，优先放在数据空白区域。
- 禁止默认使用：Arial/Calibri 风格、灰色绘图区、彩虹 colormap、阴影/渐变/圆角卡片、3D 柱状图、商业 dashboard 风格。

### 2.2 字体与中英混排

图中文字说明以中文为主；变量、数字、单位、缩写、公式保持标准科学排版。

| 内容 | 默认字体/规则 |
|---|---|
| 中文正文标签 | SimSun；缺失时 Source Han Serif SC / Noto Serif CJK SC |
| Latin 字母、数字、英文缩写、刻度 | Times New Roman |
| 数学公式/Greek | STIX / STIX Two Math / TeX Gyre Termes Math 等 Times-compatible math |
| 数学变量 | italic |
| 数字、单位、数学函数 max/min/sin/cos/exp | upright |
| panel label | Times New Roman / Times-like serif |

必须防止中文字体接管数字、Latin、Greek 和上下标，也要避免 DejaVu Sans/Arial 等意外 fallback。

示例：`平均倾角 $\bar{\theta}$ (°)`、`雷诺数 $Re$`、`弯曲刚度 $\gamma$`、`无量纲时间 $t/T$`。

科学计数使用真正的数学指数（如 `10^{-3}`），禁止将 `1e-3` 直接作为终稿标签。

### 2.3 线宽、坐标轴、刻度

从参考 PDF 矢量对象量得的基线：

- axes / tick stroke：约 **0.81 pt**
- main data curve：约 **1.46 pt**

实现默认值：

- `axes.linewidth = 0.8 pt`
- `data.linewidth = 1.45 pt`
- reference/helper line：约 0.8–1.3 pt
- marker edge：0.8–1.0 pt
- marker size：约 5 pt（常用范围 4.5–6 pt）

坐标轴默认：
- 四边 spine 可见；
- ticks inward；
- top/right ticks 开启；
- major + minor ticks；
- log axis 使用规范 `10^n`；
- 无默认 grid。

### 2.4 参考配色

从 PDF 矢量对象提取并标准化：

- blue：`#004890`
- green：`#33A02C`
- red：`#B80000`（原图约 #B00000–#B90000）
- dark gray：`#404040`
- black：`#000000`

语义建议：
- red：主响应/第一对象；
- blue：第二响应/第二对象；
- green：第三变量/自然频率/分支；
- gray/black：理论、参考、ratio、baseline。

颜色不能成为唯一信息通道。同步使用 solid/dashed/dash-dot、circle/square/triangle、open/filled 等编码。

动力学区间/参数区域使用低饱和 pastel（pale blue/green/gray），建议 alpha 0.15–0.25，置于数据下层。

## 3. 图例、标注与多面板

### 图例
- 默认 `frameon=False`；
- 置于 axes 内部空白区；
- 字号略小于 axis label；
- sample 同时保留 line + marker 语义；
- 不遮挡峰值、转捩区、关键涡结构或 annotation。

### annotation
- 中文机制/模态说明使用黑字；
- 箭头细、黑色、与轴线接近；
- 允许区间箭头、阈值、Mode/模态编号；
- 禁止气泡式 callout、彩色大文本框。

### 多面板
优先支持 1×2、2×1、2×2、2×3。共享轴时减少重复 label，panel label 位置一致。用户本轮最终明确：字母标号放在各子图y轴左侧的最上方，字母顶端与上框齐平，一般不超过上框。各 panel 尺寸、边距、gap 必须统一。

## 4. 必须支持的图型模板

1. **schematic**：物理模型/计算域/网格示意。黑灰主体、细箭头、尺寸线、数学符号；网格疏密表达 refinement。
2. **parametric_curve**：参数扫描、响应曲线、bifurcation。支持 log 轴、marker、mode shading、reference line。
3. **time_phase_spectrum**：时历 + 相图 + PSD；典型 2×3 组织，颜色角色稳定。
4. **flow_field**：流场/涡量/streamlines 多快照。紧凑排版、细流线、简洁 horizontal colorbar；signed field 默认选择科学合理的 diverging 或参考式克制蓝白方案，禁用 rainbow。
5. **regime_map**：参数空间/模态图。类别用 marker 与 fill state；理论区间用 pastel band；理论线用 gray/black dash-dot；类别数据不得伪装成连续 heatmap。
6. **convergence_validation**：网格/时间步/域无关性与解析解验证。固定 reference/baseline/coarse/refined 的视觉角色。
7. **dual_axis_frequency**：频率与比值/第二量纲组合。右轴保持黑色体系，数据颜色承担变量语义，避免把整条轴染色。

## 5. 最终尺寸与导出

默认以最终印刷尺寸设计，而非先画超大图再缩小。

建议：
- single column：约 85 mm
- double column：约 175–180 mm
- tick/legend：8–9 pt
- axis label：9.5–11 pt
- panel label：10–11 pt
- annotation：8–9.5 pt

导出：
- 曲线/示意图优先 PDF + SVG，PNG 预览；
- flow/contour 可 raster field + vector text/line overlay；
- 必须纯栅格时 >=600 dpi；
- PDF/SVG 应嵌入字体，文字/公式尽可能保持 vector；
- 避免 label clipping；
- caption 默认不烧进图片。

## 6. Caption 与中文要求

图内说明文字应中文化；变量、公式、单位、VIV/PSD 等公认缩写保持科学记号。

若生成 caption，建议组织顺序：
1. 图表达的对象/结论；
2. 各 panel 含义；
3. marker/line/fill 语义；
4. inset 或理论线说明；
5. 固定参数。

caption 与图片文件默认分离。
用户本轮补充：外部右上角不出现文字说明，统一文字说明放在专门解释段中；时刻等分面信息按(a)、(b)…对应。

## 7. QA 与自动验收

skill 至少提供或调用以下检查：

1. **font**：中文 serif、Latin/数字 Times New Roman、math Times-compatible；无意外 sans fallback。
2. **stroke**：axes≈0.8 pt，main curve≈1.45 pt，无异常粗线。
3. **axes**：四边、inward ticks、minor ticks、无默认 grid。
4. **legend**：无 frame，不遮挡关键数据。
5. **panel**：编号一致、尺寸/间距一致、无 clipping。
6. **math**：变量 italic、单位/数字 upright、上下标及 `10^n` 正确。
7. **mixed text**：中文不会污染 Latin/数字字体。
8. **export**：PDF/SVG/PNG 可正常打开，字体嵌入，视觉一致。
9. **grayscale**：灰度下仍可凭 line style/marker 区分系列。
10. **final-size**：缩放到真实投稿宽度后仍清晰可读。

## 8. 回归样例

至少生成并保存 6 个 synthetic regression figures：

- A：log-x 双曲线 + mode shading + 中文 annotation；
- B：2×3 time history / phase portrait / PSD；
- C：2×2 flow field + streamlines + shared colorbar；
- D：log-log regime map + hollow/filled markers + theoretical line/band；
- E：coarse/baseline/refined convergence；
- F：dual-axis frequency/ratio + lock-in region。

所有样例须同时验证中文 + Times/数学混排。

## 9. 参考论文视觉 spot check

实现结束后**无需重新通读全文**。仅在回归图与规范存在视觉歧义时检查原 PDF 的这些页：

- p2：Fig.1 schematic
- p4：Fig.2 mesh
- p5：Fig.3 参数曲线/区间/marker
- p6：Fig.4–5 时域-相图-频谱与 wake
- p10：Fig.9–10 复杂多面板
- p11：Fig.11–12 flow + regime map
- p14：Fig.16–17 混合曲线/双轴/参数图
- p16–17：Appendix A.1–A.3 验证图与线宽

优先执行本 spec；原 PDF 用于视觉复核，不要求再次提炼整篇。

## 10. 完成条件

- 项目自有 scientific figure skill 与 catalog 定义存在并可被 app 发现；
- 第三方/collected skill 未被原地修改；
- style profile 与绘图模板解耦，字体/颜色/线宽集中配置；
- 6 个 regression figures 均生成并通过 QA；
- 至少包含字体、线宽、导出与多面板布局自动检查；
- 现有相关调用若被替换，提供兼容入口或明确迁移；
- 更新必要文档/测试，但不顺手扩围到无关 Workbench 功能；
- 最终报告列出：改动文件、架构、支持图型、QA 结果、兼容性、尚存限制。
