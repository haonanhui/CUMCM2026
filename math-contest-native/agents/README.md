# 角色入口

依据上游 `backend/app/core/prompts/` 的四类职责，加上同仓库六步 skills 适配。原始提示词留在 `provenance/upstream/` 供溯源，不直接执行后端 Python。

| 角色文件 | 负责 | 主要技能 |
|---|---|---|
| coordinator.md | 题意完整传递、计划、角色协调、交接与阶段状态 | 1start-mathmodel |
| modeler.md | 问题分析、数学表达、求解与验证方案 | 2analysis-modeling |
| coder.md | 可复现实现、约束检查、数值结果和数据图 | 3coding-visual |
| writer.md | 基于真实结果撰写、图示衔接、排版与修订 | 4drawio、5writing |

最终验收直接使用 `6verity`，条件允许时交由未参与该结果生成的会话或队员执行。本目录不把“独立验证”伪装成上游第五种 agent。

调用时给角色文件、当前任务、必要输入与独占写范围；模型/effort 沿用用户配置，不写死供应商或型号。主会话阅读角色即可工作；角色文件可在所有 Harness 中编辑，没有专属数据库。
