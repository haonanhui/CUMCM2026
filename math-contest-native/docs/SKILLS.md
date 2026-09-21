# MathModelAgent 技能入口

2026-09-21 科研图补充：`.agents/skills/cumcm-scientific-figure/SKILL.md` 为用户授权的本地自有辅助技能，服务3coding-visual、5writing和6verity中的定量/物理图任务，不改变上游六步流程。完整脚本、profile、QA与A–F回归保存在同一目录，无app依赖。最终论文遵循FIGURES_ZH的12 pt与数学字体合同；JFS参考profile用于明确要求的参考风格及专项回归。原mathmodel-figure-templates与4drawio命令不变。

2026-09-21 质量补充：5writing、6verity 及 writer 均强制读取 `docs/PAPER_WRITING_GUIDE.md`（writing-guide-2）与 `docs/PAPER_QUALITY_STANDARD.md`；按正向内容计划生成正文，采用 internal-v3.1 质量评审，保留上游六步流程。文件已接线不等于未来模型已读取，交付报告须有实际阅读和逐项核验记录。

主要来源：jihe520/MathModelAgent，固定 commit `487f35085271f2f5bac5c0bad0b30c64b7b889f9`。

按需读取对应目录的 SKILL.md：

1. `1start-mathmodel`：偏好、plan/todo、阶段编排。
2. `2analysis-modeling`：题意、附件、假设、数学模型、代码接口。
3. `3coding-visual`：求解、验证约束、结果报告、数据图。
4. `4drawio`：真实方法的非数据图示，按需制作。
5. `5writing`：真实结果驱动的论文与双引擎模板。
6. `6verity`：文本、结构、数值、复现、编译、视觉验收。

辅助：`doctor`（显式请求环境安装向导时）、`mathmodel-figure-templates`（模拟绘图模板）、`typst-author`（Typst 写作）。`_references` 是共享知识库，按需读取，不作为第十项可执行技能。

原生工具/Windows 路径适配见根 `docs/HARNESS.md`，来源、修改清单与模板边界见 `provenance/UPSTREAM.md`。此处的技能目录是可编辑真源，不由 app 自动覆盖。
