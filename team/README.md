# CUMCM 2026 三人团队轻量协作规范

本项目采用 **“GitHub 私有仓库承载共享源码和持续协作，Release 承载精简部署包”** 的协作体系。无需搭建中心服务器或复杂审批平台，通过确定性的文件规范与 Git 分支机制保证高效、并行、零冲突的竞赛协作。

## 1. 成员槽位与主要职责

| 成员槽位 | 默认主要职责 | 典型交付 |
|---|---|---|
| `member-01` | 模型统筹与成果集成（当班集成人） | 模型合同 (`docs/model-contract.md`)、任务分配、正式结果发布 (`frozen_numbers.json`)、论文统筹 |
| `member-02` | 数据处理、算法开发与数值实验 | 核心求解代码、独立运行产物、参数与指标、误差与灵敏度检验 |
| `member-03` | 论文撰写与独立核验 | 论文骨架、图表编排、约束与单位核对、AI 工具使用说明 |

*注：成员职责可根据队员专长灵活互换。每项任务由唯一负责人闭环推进。*

## 2. 任务卡机制（Task Cards）

当班集成人在 `team/tasks/` 下建立或更新任务卡：
- 文件命名：`team/tasks/<task_id>.json`（参考 `team/tasks/template.json`）
- 任务必须指明：负责人 (`owner`)、目标 (`goal`)、基线提交 (`base_commit`)、依赖交付物 (`depends_on`)、允许写路径 (`write_paths`)、验收标准 (`acceptance`)。
- 任务分支：各成员基于 `main` 或前置依赖创建分支 `work/<member-id>/<task-id>`。

## 3. 独立运行目录与不可变结果（Runs & Result Manifest）

为了避免多人同时求解导致相互覆盖：
- 每次实验/计算使用独立目录：  
  `data/contest/<contest>/<problem>/04_solve/runs/<member_id>-<task_id>-<run_id>/`
- 每个运行目录必须生成一个不可变元数据文件 `result.json`（参考 `team/templates/result.example.json`）：
  - 记录输入哈希 (`inputs`)、参数配置 (`parameters`)、输出指标 (`metrics`)、图表与文件路径 (`artifacts`)、复现命令行 (`reproduce_argv`)、自测结果与真人核验状态 (`validation`)。
  - 同一 `run_id` 的结果一旦交付即不可变；调参或修复使用新的 `run_id`。

## 4. 正式数字发布与论文汇合

- **单写者发布**：只有当班集成人有权将已验收的任务指标从各个 `result.json` 汇总进 `04_solve/frozen_numbers.json`。
- **冲突检测**：若不同运行包针对同一指标键给出了不同数值，工具将拒绝合并并发出冲突警告，禁止静默覆盖。
- **论文引用**：论文源文件统一使用占位符（如 `{{NUM:metric_name}}`），通过构建脚本在副本中注入数字，避免源文件占位符被永久污染。

## 5. 竞赛 AI 工具使用合规记录

依据全国组委会《全国大学生数学建模竞赛人工智能工具使用规定（2026年试行）》：
- 队员在每项任务中涉及 AI 工具时，如实填写 `team/ai_usage/<member_id>_<task_id>.json`（参考 `team/ai_usage/template.json`）。
- 记录实际工具与模型版本、使用目的、典型 Prompt、采纳内容与人类审查修正记录。
- 最终由论文负责人统一导出为支撑材料中的 `AI工具使用详情.pdf`。
