# CUMCM 2026 AI 智能体协作指引 (AGENTS.md)

本指引适用于服务于各参赛队员的 AI 智能体（Codex、Antigravity、Claude、ChatGPT、Cursor 等）。
本项目为全国大学生数学建模竞赛（CUMCM）三人团队协作环境，采用 **“GitHub 私有仓库承载共享源码和持续协作，Release 承载精简部署包”**。

## 1. 核心原则与边界

- **项目根自包含**：所有代码、配置与数据路径必须推导自当前工作区根目录（通过相对路径），严禁在任何脚本或配置文件中硬编码特定机器的绝对路径。
- **无中央治理依赖**：本项目独立自洽，不依赖维护者机器的私有环境、全局配置或特定框架。
- **零凭证泄漏**：严禁将任何 API Key、Token、密码、代理配置或 `.env` 文件写入代码或提交至 Git。
- **不可变运行结果**：任何计算输出必须放入独立的运行目录，严禁覆盖历史运行目录或其他队员的成果。
- **谨慎 Git 提交**：严禁直接使用未经筛选的 `git add .`。每次提交前必须检查 staged diff，确保仅提交授权和必要的文件。
- **Vendor 资产只读**：`code/vendor/` 为第三方参考库与基线工具，一律保持只读，禁止原地修改。

## 2. 团队槽位与职责划分

| 槽位 | 角色定位 | 核心工作 |
|---|---|---|
| `member-01` | 模型统筹与当班集成人 | 维护模型合同、分配任务卡、单写者发布正式指标 (`frozen_numbers.json`)、统筹论文大纲与最终提交 |
| `member-02` | 数据算法与数值计算 | 题面数据清洗、算法设计与求解、收敛性与灵敏度分析、产出独立运行目录及 `result.json` |
| `member-03` | 论文撰写与独立核查 | 论文排版、图表绘制与嵌入、物理量纲/约束/公式独立核查、整理 AI 工具使用详情 |

## 3. 标准任务工作流

1. **认领任务**：
   - 检查 `team/tasks/<task_id>.json`，确认任务目标、依赖交付物与输入哈希。
   - 创建或切换至任务分支：`git checkout -b work/<member_id>/<task_id>`。

2. **本地环境**：
   - 使用项目局部虚拟环境 `.venv` 运行 Python 代码。
   - 核心测试入口：`python code/pipeline/tests/smoke_test.py`。

3. **代码编写与独立求解**：
   - 算法与求解脚本放置于 `code/`（例如 `code/models/<task_id>/`）。
   - 计算输出统一写入专属运行目录：  
     `data/contest/<contest>/<problem>/04_solve/runs/<member_id>-<task_id>-<run_id>/`
   - 必须在运行目录下生成符合格式的 `result.json`（参考 `team/templates/result.example.json`），包含指标数值、参数、复现命令行与验证状态。

4. **合规登记**：
   - 根据全国组委会《全国大学生数学建模竞赛人工智能工具使用规定（2026年试行）》，在 `team/ai_usage/<member_id>_<task_id>.json` 中如实登记智能体使用过程（工具型号、提示词概要、人工核验修改）。

5. **提交与交接**：
   - 明确暂存并提交修改的文件：`git add code/models/... team/tasks/... team/ai_usage/...`
   - 提交信息格式：`feat(<task_id>): [member_id] 简述交付内容`
   - 推送分支并通知当班集成人集成。

6. **正式指标发布与论文引用**：
   - 当班集成人（member-01）统一将已核验的指标写入 `04_solve/frozen_numbers.json`。
   - 论文统一使用占位符 `{{NUM:metric_key}}`，严禁在论文源中手工填入未冻结字面量。
