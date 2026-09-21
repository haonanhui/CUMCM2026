 > **队内共享版（2026-09-21）**：先读 [挂载指南](docs/TEAM_MOUNT.md)。现有论文仅供了解架构能力，**不是优秀参考案例**，见 [说明](paper/REFERENCE_ONLY.md)。当前发布状态为等待队友接入；下方早期未预置论文的描述仅属初始历史。

# 数模竞赛原生工作区

直接在 Codex、DSH 或其他本地 Harness 中打开这个目录，即可按 MathModelAgent 的技能流程工作。项目内容不依赖桌面 app；这是独立主工作区。

首次使用读 [START_HERE.md](START_HERE.md)。技能以 **jihe520/MathModelAgent @ 487f35085271** 为主要来源，保留六步工作流、共享数学建模规范、绘图资源和 Typst/LaTeX 模板。角色按上游协调、建模、编码、写作职责适配；来源和差异见 [provenance/UPSTREAM.md](provenance/UPSTREAM.md)。

```text
.agents/skills/           共用的技能正文与配套资源
agents/                  跨 Harness 角色说明
plan.md、todo.md          上游约定的方案与阶段待办
reports/                 分析建模、结果、DrawIO、验收报告
data/                    官方原件与派生数据
code/                    研究代码与模块接口
results/runs/            每次独立运行及其证据
figures/                 论文采用的图件及来源说明
paper/                   main.tex 或 main.typ、章节和数字绑定
team/                    任务与跨会话交接
scripts/                 本地复现/检查工具
submission/              按允许清单组装候选和冻结文件
```

当前未绑定赛事，不预置虚构论文或竞赛结果。环境/验收实况见 [docs/ACCEPTANCE.md](docs/ACCEPTANCE.md)；真正赛前演练见 [docs/PREFLIGHT.md](docs/PREFLIGHT.md)。
