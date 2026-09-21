# 行距与标题专项核验

2026-09-21。评审者 Codex root，自审。用途为历史真题研究阅读版。

## 结论

本轮正文行距与标题修正完成。排版专项 PASS，官方单倍行距等效性 UNVERIFIED，整稿语言仍 NEEDS_REVISION；不重新评分、不继承旧稿得分。正式提交 NOT_READY。

新版 `paper/NPU_2025_A_typography_revised.pdf` 共32页，源文件为 `paper/typography-revision/main.tex`。PDF SHA-256为 `ebfe4b6f2105ba070e75676e8aa059f880acc97e09394fbd87c89da6bcb7b6cf`，本目录 `verification.json` 与 `paper/typography-revision/bindings.json` 绑定同一成品。旧版 `paper/NPU_2025_A_figure_centered.pdf` 和旧源目录均保留。

## 依据与实测

实际全文读取：`.agents/skills/5writing/SKILL.md`、`C:/Users/62470/.codex/skills/pdf/SKILL.md`、`docs/HARNESS.md`、`docs/PAPER_WRITING_GUIDE.md` writing-guide-2、`docs/PAPER_QUALITY_STANDARD.md` native-quality-4、`docs/paper-quality/SCORING_ANCHORS.md` internal-v3.1、`docs/FIGURES_ZH.md` figure-style-2；全文提取本地官方 `provenance/official2025/format.pdf`。

联网核验的官方2025年公告：[开赛公告及附件](https://cpipc.acge.org.cn/cw/contestNews/detail/4/2c90801b9914a68201994b1403512e96?page=1)，访问2026-09-21。附件2要求题目三号黑体、一级标题四号黑体、均居中；其余汉字小四宋体，单倍行距。该条款没有指定一级标题的数字体系，也没有给定单倍行距的固定磅值。

[Microsoft Word 文档](https://learn.microsoft.com/en-us/office/vba/api/word.paragraphformat.space1)说明单倍行距的实际间距与段落最大字号有关。LaTeX 的 `linespread` 乘的是字号命令的基础基线距离，数值1不是跨排版软件的统一物理量。本地 `D:/texlive/2026/texmf-dist/tex/latex/ctex/ctexart.cls` 可核对其行距实现。不能把 `linespread=1` 直接用作Word单倍行距等效证明。

对四篇同年同题参考稿，从各自正文起始页连续抽取8页，以含18个以上汉字、字号约12pt的文本行为样本，比较相邻基线，排除大于35pt间隔。`reference-measurements.json` 保留路径、哈希、间距频次与标题证据；逐块与跨块统计有重合，频次不能当独立样本数。下表报告稳定主间距，公式和段落间距不混称正文行距。PDF中的pt指1/72英寸（TeX的bp）。参考目录奖项未逐篇另行核验。

| 文稿 | 抽样物理页 | 正文主要基线间距 | 一级/次级编号 |
|---|---|---:|---|
| 修改前 | 2–9 | 14.40pt | 1. / 2.1 |
| 2025 A题-1 | 4–11 | 19.87–19.88pt | 1 / 1.1 |
| 2025 A题-2 | 4–11 | 19.87–19.88pt | 一、 / 1.1 |
| NPU核内调度算法设计与优化研究 | 7–14 | 19.87–19.88pt | 1 / 1.1 |
| 面向Davinci架构的NPU核内调度算法研究 | 5–12 | 15.48–15.60pt | 一、 / 1.1 |
| 修改后 | 全文逐页测量 | 19.87–19.88pt | 一、 / 2.1 |

参考PDF可证明实际版面，不能反推出Word设置或证明官方单倍行距等效。用户明确要求加大行距并参照优秀论文，本版采用A题-2的中文一级编号与版面密度。具体实现为 `linespread=1.38`，12pt正文基础行距14.4pt，最终为19.872pt；这是经测量的样本匹配选择，不标为官方唯一标准，也不声称LaTeX的1.38等于Word的1.38倍。

一级标题14pt黑体居中，中文数字后加顿号；二级和预设三级标题12pt宋体加粗、左对齐，分别采用1.1和1.1.1。宋体加粗由局部AutoFakeBold实现，西文编号用Times New Roman Bold，正文不受影响。实际稿只有二级标题，没有为展示样式增加空三级节。附录采用附录A。标题段距统一，正文保持自然分页；`raggedbottom`避免撑满页面时拉伸段间空白。字号、页边距、五图165mm嵌入宽度保持。

## 验证与限制

- XeLaTeX运行两遍。第二遍无Overfull、Underfull、Missing character、undefined reference；只保留原稿已有的SimSun字体族重复声明提示，实际字体提取正常。
- 所有正文节、摘要、参考文献、表格和图注源文件逐字节一致；只有main.tex中的版式命令变化。科学内容、数值和图片无需因本轮排版重新运行求解。图件及来源文件的哈希一致性另见verification.json。
- 最终中文字体组合为16pt SimHei题目、14pt SimHei一级标题、12pt SimSun其余文字；局部宋体加粗经页面检查可见。字体嵌入及页内边界检查通过。
- 32页全部渲染，全部联系图检查；原尺寸放大检查p2、5、11、18、24、26、27、32。一级标题完整、次级标题左对齐、附录标签正确。五图在p11/18/24/26/27，均和图题、说明同页，既有居中布局保留。
- p10图前有较明显余白：保留下一页双面板图与说明为整体所致；不是新增强制分页。附录按旧稿单独起页。未以页数增加宣称内容或质量提升。
- 工程验证：PASS。文字内容未作语言重写，已有修辞引号、防御性表达与研究内容补充仍待原任务处理。正式封面、AI完整记录和队员复核仍未闭合。本轮不宣称全稿质量PASS。

## 同哈希24项范围记录

等级、得分和总分均为null。下面只记录本轮实际覆盖范围，科学质量未重新评价。

| 项 | 新版位置及覆盖 |
|---|---|
| A1 | p5–28三问原文保持；未重验题面答案覆盖 |
| A2 | p9–12、16–19、23–28结果内容保持；未重评解释充分性 |
| A3 | p2–4、19问间衔接保持；未重新评分 |
| B1 | p5符号表字体及版面检查；定义正确性未重审 |
| B2 | p6、13、19–20公式内容保持；约束未重审 |
| B3 | p7–8、20–21推导保持；未重新证明 |
| B4 | p8–9、14–15、21–23算法保持；方法选择未重审 |
| C1 | 所有研究TeX与图件哈希一致；没有重跑数值验证 |
| C2 | p9–10、25基线及下界保留；未重算 |
| C3 | p28–30敏感性与验证保持；未新增实验 |
| D1 | p1摘要同文、单页、字号正常；摘要内容未重评分 |
| D2 | 原图文顺序和章节内容保持；三问论证链未重评 |
| D3 | 26页自然重排32页；p10余白记录，页数不计质量增益 |
| E1 | 标题编号与字号统一；正文用词未全面审读 |
| E2 | p2等原有预防性表达仍在，语言修订待办 |
| E3 | 原有引号与把字句仍在，NEEDS_REVISION |
| F1 | p11/18/24/26/27原图未变；科学图型与尺度不重评 |
| F2 | 五图各自与图题和说明同页，原正文分析顺序保留 |
| F3 | 图宽165mm、中文12pt、既有视觉居中保留 |
| G1 | 字体字号/标题结构已核对；19.87pt是样本参照，官方单倍等效性UNVERIFIED |
| G2 | 全文编译引用已解析，公式编号保持；符号表和多列表未见溢出 |
| G3 | 32页渲染及边界检查，8页放大检查；p10图前余白如实记录 |
| H1 | p31参考文献源文件保持；文献科学对应关系未重审 |
| H2 | p32仍缺AI精确历史记录与队员复核，正式提交NOT_READY |

## 复现、失败与保留

在 `paper/typography-revision` 执行 `D:/texlive/2026/bin/windows/xelatex.exe -interaction=nonstopmode -halt-on-error -output-directory=build main.tex` 两遍。使用项目.venv中的PyMuPDF提取字号和行坐标并渲染，Pillow生成联系图。

首次测量脚本只统计块内相邻行，部分参考稿每行独立成块，故没有得到间距；改为补充同页跨块行基线统计。第一次输出官方PDF文本时控制台GBK不能编码符号，改为UTF-8输出后全文读取成功。这两项均未影响原始PDF。首次编译有正常的交叉引用待解析提示，第二遍全部消失。

一次性测量脚本及新build目录中的aux/out缓存在收尾清理。最终PDF、编译日志、渲染页、测量与核验JSON保留作证据。未提交、未push；既有并发改动保留。
