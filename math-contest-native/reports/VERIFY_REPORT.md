# NPU 2025 A 第三版验证与验收

日期：2026-09-21。按`.agents/skills/6verity/SKILL.md`、writing-guide-1、native-quality-3/internal-v3及SCORING_ANCHORS执行。评审为root自审。

## 结论

**工程检查PASS；内容REVIEWED_MINOR_EDITS；正式提交NOT_READY。** 三种结论不合并。论文质量24项及30个逐问评分格见`reports/PAPER_QUALITY_REVIEW.md`；唯一总分未完成，S=82.17/U=2。

最终PDF：`paper/NPU_2025_A_revision3.pdf`，29页。
SHA-256：`28eb3429c3bfe60d038d8a6383c07d721637044ff0a4a532ebe748d9aa66dbf7`。
源：`paper/revision3/main.tex`。完整的数值与文件指纹记录：`reports/npu-r3-evidence/verification.json`。

## 检查项

| 项目 | 结果 | 实际范围与证据 |
|---|---|---|
| 并发保护 | PASS | 开始及验收再次检查相关可见任务均idle；新建revision3，不覆盖旧源/PDF/005；无法断言不可见的外部Harness绝无活动 |
| 章节结构 | PASS | 9个正文一级节、1附录、摘要与文献；12个input、10个section文件均存在且顺序正确 |
| 文本门禁 | PASS + 5 WARN已审 | writing-check.txt；无占位符/内部路径/缺图；2个短节和3个标题字符串告警按真实内容核查，详质量报告 |
| 图表引用 | PASS | 5图、16表、20编号公式；3张新增过程图+2张保留结果图；全部有引文/题注，无未定义引用 |
| 新分析 | PASS | 读取原始JSON与005附件；12完整方案重放、6份问一序列核对；独立递归穷举126个九节点拓扑序 |
| 表格/数字 | PASS | 九组结果表逐行六图比对；9条事件和8条等待记录从章节读回与实际trace逐项比对；峰值、搬运、时间、百分比及手算一致 |
| 手算与异常检测 | PASS | hand-checks.json：并行20/复用30周期、已知峰值4、两种搬运4/188及8/346，非法重叠/拓扑/边界/重复被拒绝 |
| 编译 | PASS | 最终XeLaTeX两遍compile5/6.txt；main.log无Overfull/Underfull/Missing character/undefined |
| PDF与视觉 | PASS | A4、29页非空；29页2倍渲染逐页查看；最后图5白边修改仅p25图像改变并复查，其余28页哈希相同 |
| 官方格式 | WARN/不符合正式用途 | 已读2025官方格式；阅读版12pt/18pt及研究封面不等同官方模板；未组装RAR正式包 |
| 科研质量 | REVIEWED_MINOR_EDITS | 同哈希逐问矩阵+24项+逐页事实，不把运行退出码当论文质量 |
| AI与队员确认 | UNVERIFIED | 历史精确模型/版本和队员独立复核未完成，无代填 |
| 旧成果保护 | PASS | 首版PDF 0f23f5ff…，第二版b4429e1c…完整SHA在verify脚本中核对；005输入/源码和旧分析指纹保持 |

## 执行与可复算范围

- `.venv/Scripts/python.exe -B scripts/analyze_npu_revision3.py`：本轮真实执行，唯一目录`results/runs/npu-paper-r3-analysis-001`。脚本默认拒绝覆盖该目录；复算时应新建run路径，不能原地覆盖记录。
- `.venv/Scripts/python.exe -B scripts/figures_npu_revision3.py`：由保存的轨迹生成3图3表，不使用模拟数据代替六图结果。
- `scripts/check_npu_revision3_writing.py`：运行实际上游writing_check.sh内嵌Python检查逻辑；适配Windows解释器和LaTeX图片路径相对主文件解析，未改硬门禁规则。原Git Bash调用失败且无诊断输出，未算通过，随后适配调用通过。
- 在`paper/revision3`执行`D:/texlive/2026/bin/windows/xelatex.exe -interaction=nonstopmode -halt-on-error -output-directory=build main.tex`两遍。
- bundled Python执行`inspect_npu_revision3.py`及`verify_npu_revision3.py`：PDF页面/字体/间距提取、逐页PNG、九组表格与trace数值核对、旧文件指纹比对、最终PDF复制与绑定。

没有重新运行所有启发式候选搜索：原005六图方案及r2候选对照作为已记录基线保持；本轮真实新增工作是方案重放、结构/轨迹统计、精确小例与写作。没有执行新容量扰动、硬件测量或官方评价器。JSON文件存在和哈希匹配只证明溯源一致，不单独证明数学正确。

## 内容修复与版面闭环

问一增加前沿峰值推导、收缩证明细节、完整状态更新、126序列小例及峰值组成；问二增加连续空间判据、评分手算/碎片恢复、有限性、类型及重复换出、真实地址事件；问三增加A/P就绪区分、复用链与20/30例、列表步骤、两支路收益和具体节点等待。反复防御性说明合并到条件定义和8.3，保留科学必要边界。

首轮图文被挤到三处浮动页，已改邻接；图例贴近轨迹、下界表列距不足已改；最后局部流水加指令边界。最终p10等少数图前余白属于不可拆分图表换页，未用强制空白凑页。逐页观察与最终字体实测见质量报告，不以缩略图代替。

## 尚未核验与后续

内容只需局部润色：摘要数字密度、少量同义词及图前留白。科研延伸（更紧H/D界、新图泛化、官方/硬件交叉验证）不在本轮结果内，现稿已经限制相应主张。正式使用前还需官方格式转换、真实AI工具历史记录和队员独立核验；本轮不假造这些完成状态。

所有旧报告先存`reports/npu-r3-evidence/previous-*.md`；未stage、commit或push。
