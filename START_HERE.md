# CUMCM 2026 团队快速上手指南 (START_HERE.md)

欢迎加入 CUMCM 2026 数学建模协作！
本项目通过 **GitHub 私有仓库**（源码版本与日常协作）与 **GitHub Release 精简包**（一键部署与备份）实现三人高效协同。无论使用何种操作系统（Windows / macOS / Linux）或哪种 AI 辅助工具，均可一键完成本地环境部署并立即投入任务。

---

## 1. 快速部署（两分钟就绪）

### 途径 A：通过 Git 克隆（推荐日常协作）
```bash
git clone https://github.com/haonanhui/CUMCM2026.git
cd CUMCM2026
python scripts/bootstrap.py --member-slot member-02   # 请替换为您负责的成员槽位
```

### 途径 B：从 GitHub Release 下载精简包（首登或离线备选）
1. 从 [Releases](https://github.com/haonanhui/CUMCM2026/releases) 下载 `cumcm-team-<version>.zip` 并解压。
2. 在解压后的目录中打开终端，执行：
```bash
python scripts/bootstrap.py --member-slot member-02
```

> **自动化部署脚本所做工作**：
> - 自动识别当前根路径并生成匹配本机的本地配置（不覆盖已有工作）；
> - 创建项目局部虚拟环境 `.venv`；
> - 自动安装已验证的核心依赖包（`requirements-core.txt`）；
> - 自动运行核心流水线 smoke test 确保 100% 可靠性；
> - 探查本机排版能力（缺少 LaTeX 不影响建模与计算）；
> - 生成并输出部署回执 `bootstrap_receipt.json`。

---

## 2. 队员直接发给各自 Agent 的启动 Prompt

将项目交给您的 AI 助手（Codex、Claude、ChatGPT、Cursor、Antigravity 等）时，**直接复制以下提示词发送给它**：

```text
你正在协助我参与 CUMCM 2026 数学建模竞赛。
请首先阅读项目根目录下的 `START_HERE.md`、`AGENTS.md` 和 `team/README.md`。
请确认我的成员槽位（member-01: 统筹与集成 / member-02: 数据与计算 / member-03: 论文与核验），
并检查环境就绪状态（检查 bootstrap_receipt.json 是否存在，若无请运行 python scripts/bootstrap.py）。

在整个协作过程中，请严格遵循：
1. 所有代码与配置必须使用相对路径，严禁硬编码绝对路径或提交 API Key 等敏感信息；
2. 任务从 team/tasks/ 认领，分支命名为 work/<member_id>/<task_id>；
3. 每次计算输出必须写入独立的运行目录（data/.../04_solve/runs/<member_id>-<task_id>-<run_id>/），并附带标准的 result.json；
4. 按照国赛 2026 AI 规定在 team/ai_usage/ 中如实登记智能体使用记录；
5. 禁止未经筛选执行 git add .。

现在请汇报当前环境就绪情况，并告诉我我们可以开始的第一项任务。
```

---

## 3. 队员槽位与日常协作规范

| 成员槽位 | 默认分工 | 日常交付物 |
|---|---|---|
| `member-01` | 模型统筹与当班集成人 | 赛题模型合同、任务卡 (`team/tasks/`)、合并正式指标 (`04_solve/frozen_numbers.json`) |
| `member-02` | 数据处理与算法求解 | 算法代码、独立运行目录、不可变结果包 (`result.json`)、参数与误差分析 |
| `member-03` | 论文撰写与独立验证 | 论文源稿 (`paper/`)、图表嵌入、公式量纲核对、整理支撑材料《AI工具使用详情.pdf》 |

### 核心协作四步法：
1. **任务与分支**：从 `team/tasks/<task_id>.json` 认领任务，创建分支 `work/<member-id>/<task-id>`。
2. **独立运行与结果交付**：计算输出写入专属目录 `data/.../04_solve/runs/<member_id>-<task_id>-<run_id>/`，并生成 `result.json`。
3. **指标冻结**：由 member-01 汇总至 `frozen_numbers.json`，杜绝数字冲突与静默覆盖。
4. **论文引用**：论文源文件中使用 `{{NUM:metric_name}}` 引用确定版本的指标快照。

---

## 4. 常见问题解答

- **Q: 我的电脑上没有安装 LaTeX 或 XeLaTeX，可以参与吗？**  
  A: 完全可以！`scripts/bootstrap.py` 探查到无排版引擎时会正常标记核心计算就绪。负责计算的队员可以无障碍开展数据处理与数值实验，最终论文由负责排版的队员统一编译。
- **Q: 重复运行 `scripts/bootstrap.py` 会覆盖我已有的修改吗？**  
  A: 不会。脚本具备写保护机制，对已存在的 `PROJECT_ID.json`、`contest.yaml` 等本地修改和工作成果保持原样保留。
- **Q: 怎样确认流水线正常？**  
  A: 随时可以在项目根目录下执行：
  ```bash
  .venv\Scripts\python.exe code\pipeline\tests\smoke_test.py  # Windows
  # 或
  .venv/bin/python code/pipeline/tests/smoke_test.py          # Linux/macOS
  ```
  7 项测试输出 `[PASS]` 即表示核心模块完全正常。
