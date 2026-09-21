# 方案

## 用户偏好与范围
- 题目：2025 年中国研究生数学建模竞赛 A 题《通用神经网络处理器下的核内调度问题》，以用户提供 DOCX 正文确认。
- 排版引擎：LaTeX（用户本任务明确选择）；论文语言：中文。
- 本赛题共 3 个子问题；按历史真题研究处理，无当前参赛截止时间，不代替队员提交。
- 原题只读，复制到 data/raw/npu2025，来源和 SHA-256 记入 provenance/npu2025_inputs.json。
- 工作区为 math-contest-native，PROJECT_ID 标记 local_identity_only，中央注册表未查到该项目，不切换到旧 app 工作区。

## 工作流
1. `2analysis-modeling`：三问分析、歧义、模型与接口，输出 reports/ANALYSIS_MODELING_REPORT.md。
2. `3coding-visual`：通用拓扑调度、连续地址分配、换入换出、流水评价与验证，六图实验，输出 code/、results/runs/、figures/、reports/RESULTS_REPORT.md。
3. `4drawio`：按实际解释需求决定是否绘制非数据图，记录 DRAWIO_REPORT.md。
4. `5writing`：仅使用验证后的数值撰写 LaTeX 论文，输出 paper/。
5. `6verity`：重放交付附件、复现与编译检查，输出 reports/VERIFY_REPORT.md。

## 算法路线与风险
先建立可独立重放的基准，再比较缓存压力启发式和流水优先启发式。保持六个输入统一算法与参数，不按算子名称硬编码。问题一优化所有缓存合计驻留峰值；问题二按类型限制和连续区间管理；问题三严格不增加选定问题二的搬运量作为“不显著增加”的保守解释。

没有最优性证明时仅称候选中最佳。官方论文格式、AI 使用规则和提交资格待核验；科学结果与正式提交就绪分开记录。SPILL 期间的地址复用按驻留段解释，并显式记录附录 C 对该情形描述不完整的边界。
