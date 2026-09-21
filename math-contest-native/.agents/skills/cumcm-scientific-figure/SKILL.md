---
name: cumcm-scientific-figure
description: 生成、修改和验收中文科研论文的定量曲线、多面板、流场、模态图、验证图与物理示意图。使用可复现数据和代码，支持中文宋体、Times 和数学混排及 PDF/SVG/PNG。用于论文科研图，不用于商业仪表盘或 draw.io 技术路线图。
---

# 中文科研论文图

这是 math-contest-native 的自有补充技能，真源为 `.agents/skills/cumcm-scientific-figure`，无需 app 或投影。先读项目 `docs/FIGURES_ZH.md` 与 `docs/PAPER_FIGURE_STYLE_SPEC_20260921.md`。采用 `jfs_zh_reference_v1` 作为论文参考风格，不声称是 JFS/Elsevier 官方要求。原生论文默认 `native_zh_12pt_v1`，保留12 pt成品字号；数学字体另按实际论文核验，STIX近似不自动等于正文一致。定量位置、数据、刻度和公式必须由代码生成。真实数据须保存来源、单位、处理方法和绘图脚本；缺数据不能用合成数据冒充结果。仅在用户要求示例/回归时使用明确标记的 synthetic 输入。

## 选择与使用

默认使用项目 Python + Matplotlib。先确认图表达的结论、输入和最终宽度；不依赖本机个人路径或 Zotero。选择模板：

| 模板 | 使用场景 |
|---|---|
| schematic | 计算域、物理尺寸、局部网格；黑灰主体、细箭头 |
| parametric_curve | 参数响应、log 轴、模态带、阈值及机制标注 |
| time_phase_spectrum | 两个响应各占一行的 2×3 时历/相图/单边 PSD |
| flow_field | 2×2 有符号场、细流线、共用水平色标 |
| regime_map | log-log 离散模态、空心/实心 marker、理论线与区间 |
| convergence_validation | coarse/baseline/refined 和解析 reference 固定角色 |
| dual_axis_frequency | 频率/比值、锁定区间、黑色双轴 |

完整资源目录存在时，先读 [references/api.md](references/api.md)，通过 `scripts/scientific_figure` 公共接口作图，在 `style_context()` 内创建和导出。集中风格源为 [references/profile.json](references/profile.json)；不要在调用脚本重新定义字体和配色。依赖见 `requirements.txt`，仅安装到执行项目的环境。字体不随包分发；Times New Roman 或中文 serif 缺失时明确失败，不能静默换 Arial/DejaVu。

回归命令（将 `<skill-root>` 替换为当前可访问的完整资源目录）：

```text
python <skill-root>/scripts/regression.py --out <new-output-directory>
python -B -m unittest discover -s <skill-root>/tests -p test_*.py
```

资源随本技能目录保存，路径从本 SKILL.md 或当前 Git 根推导，不依赖外部开发仓库。默认 `style_context()` 是12 pt原生profile；明确使用参考尺寸时调用 `style_context('jfs_zh_reference_v1')`。数学字体可显式选 `math_fontset='cm'` 或 `'stix'`，须在实际论文PDF中比较，不能只看配置。缺资源明确报告，不请求启动 app。原有六步流程与 mathmodel-figure-templates 的模板ID、命令保持不变；本技能作为新的定量/物理图辅助入口，不替换4drawio的技术路线图职责。

## 参考风格视觉合同

- 白底、黑框、无装饰标题、无默认 grid、无渐变卡片或 3D 柱图。所有文字按最终印刷尺寸设计：参考profile单栏85 mm、双栏175–180 mm；刻度8.5 pt，图例8 pt，轴标签10 pt，panel10.5 pt，标注8.5 pt。原生论文profile各类基准均12 pt，空间不足拆图或增大最终宽度，禁止缩小字号绕过合同。
- 字体族按顺序 `[Times New Roman, SimSun]`：Latin/数字先匹配 Times，中文缺字才进 SimSun；中文替代只能是 Source Han Serif SC / Noto Serif CJK SC。Matplotlib `mathtext.fontset='stix'`。变量斜体，数字/单位及 `\sin`、`\cos`、`\exp`、`\min`、`\max` 正体，单位在数学区用 `\mathrm{}`。不要把整段标签指定为中文字体。示例：`平均倾角 $\bar{\theta}$ (°)`、`雷诺数 $Re$`、`时间 $t/T$`。科学计数用数学指数，不把 `1e-3` 写成终稿标签。
- 轴线和主/次刻度0.8 pt；主曲线1.45 pt；参考线1.0 pt；marker边缘0.9 pt、大小5 pt；流线0.55 pt。四边 spine、朝内刻度、top/right与minor开启；log使用数学 `10^n`。双轴只显示对应侧y刻度，不染色轴线。
- primary红 `#B80000`/实线/空心圆；secondary蓝 `#004890`/虚线/实心方块；third绿 `#33A02C`/点划线/空心三角；reference灰 `#404040`/点线/实心菱形。解析理论为黑/灰点划线。coarse=secondary，baseline=reference，refined=primary。数据语义跨面板稳定，灰度可凭线型或marker识别。
- 模态/锁定区用低饱和浅蓝 `#BCD9E8`、alpha0.2、位于数据下层。signed field用以零为中心的对称 RdBu_r，禁止 rainbow。离散模态不能画成连续热图。
- 图例无框、字号小于轴标签，保留line+marker语义，放空白区；检查所有双轴系列，不能遮住峰值、转捩或机制标注。中文说明用黑字和0.8 pt细黑箭头，禁止气泡框。
- 1×2、2×1、2×2、2×3等宽等高布局，统一间距；`(a)(b)…` 位于每个子图y轴左侧顶部，归一化位置(-0.18,1)，ha=right、va=top。字母顶端与上框齐平，不超过上框，统一偏移与字号，不能压住刻度、数据或被画布裁切。共享轴减少重复标签，若数据不宜共享范围，不强行共享。紧凑流场配共用水平色标。
- PDF字体嵌入（fonttype42）；SVG默认字形转矢量轮廓，跨机不依赖安装字体，但文字不再可编辑。PNG≥600 dpi。场可栅格化，标签/线保留矢量。不要用tight裁剪改变最终物理宽度；不得裁切标签。
- 外部右上角不放文字说明。时刻、统一条件、各panel含义集中放专门解释段，与标号逐一对应；图片外仅留左上角panel标号。caption/解释段放独立文件：对象/结论→panel→line/marker/fill→inset/理论线→固定参数，不烧进图；科学事实不得从回归样例继承。

## 验收

检查真实字体/数学字形（不只查 rcParams）、中英混排、线宽、坐标轴和次刻度、图例遮挡、panel编号/尺寸/间距、文本裁切、数学语义和指数、灰度编码、最终印刷尺寸。重新打开 PDF/SVG/PNG 检查字体嵌入和跨格式一致性。自动报告不能代替检查渲染图及真实结论。

完整资源导出写 `.qa.json`：失败非PASS；视觉审查、人工确认分别记录，不能伪造队员批准。先打开彩色与灰度输出逐图检查，再反馈真实通过范围和剩余限制。输出目录必须是新目录，保留失败证据。A–F回归输入明确合成，不作为实验数据或 submission_ready 证据。
