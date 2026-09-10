# CUMCM 2026 比赛日 Runbook（流水线唯一入口）

> 用途：赛题放出后，任何 agent 会话冷启动读本文件即可推进完整流程：分析 → 建模 → 求解 → 论文 → 审计。
> 工作方式：Agent 模式 + Manual checkpoint（关键决策停点由真人确认），默认全自动推进到每个 gate。
> 可审计性：每个阶段产出物落盘、记录 provenance 与 sha256；结论标注 PASS / WARN / UNVERIFIED，禁止编造数字。

## 0. 冷启动（赛题放出后立即执行）

1. 读取本文件与 `stages/` 下全部 playbook（按需加载，不整仓扫描）。
2. 建立竞赛工作目录 `data/contest/<contest>/<题号>/`（如 `data/contest/cumcm2026/A/`），并复制官方赛题+附件到 `data/contest/<contest>/<题号>/official/`（原文件只读）。
3. 填写 `config/contest.yaml`：队号、赛事、截止时间、路径。
4. 从 `stages/00_ingest.md` 开始，按阶段执行；每阶段结束产出物必须存在再进下一阶段。

## 1. 阶段编排与门禁

| # | 阶段 | playbook | 核心产出 | 门禁（G） | 停点（需真人确认） |
|---|---|---|---|---|---|
| 00 | 赛题入库 | stages/00_ingest.md | manifest.json + 全文 md + 附件 csv | G1 题目解析完整 | 无 |
| 01 | 分析拆题 | stages/01_analyze.md | 题目分析报告.md | G1 | 选题（若多题可选） |
| 02 | 方法检索 | stages/02_retrieve.md | 候选方法表 | G2 方法齐备 | 无 |
| 03 | 建模+新颖性 | stages/03_model_novelty.md | 建模方案.md + novelty_gate 记录 | G3 模型可求解、novelty PASS/WARN | **模型路线** |
| 04 | 求解+验证 | stages/04_solve.md | 结果表/图 + 复现清单.json | G4 数字可复现 | 无 |
| 05 | 论文写作 | stages/05_paper.md | LaTeX 源码 + 编译 PDF | G5 格式合规 | **摘要/结论定稿** |
| 06 | 审计提交 | stages/06_audit.md | 审计报告 + 提交包 | G6 完整合规 | **最终提交** |

门禁语义（对齐 vender 资产 math-modeling-skills G1-G6，详见其 `references/` 与 `scripts/gate_contracts.py`）：
- G1 PROBLEM_PARSED：题目解析+分类+附件盘点完成。
- G2 METHOD_VALIDATED：每问候选方法 ≥2 且方法-数据匹配。
- G3 MODEL_SOLVABLE：模型有明确定义、可数值求解、新颖性检查已记录。
- G4 RESULT_REPRODUCIBLE：结果脚本可一键重跑，数字与论文一致（frozen numbers）。
- G5 PAPER_COMPLIANT：LaTeX 编译通过、格式符合官方规范。
- G6 SUBMISSION_READY：承诺书/AI 报告/命名/打包全部就绪。

## 2. 时间盒（72h 参考，国赛实际按官方日程）

| 时间 | 阶段 | 备注 |
|---|---|---|
| T0–T0+3h | 00+01 | 选题定死，拆题完成；**只许花 3h** |
| T0+3h–T0+12h | 02+03 | 主模型定稿（含 novelty 声明）；12h 内不回头 |
| T0+12h–T0+36h | 04 | 全部求解+验证跑通，数字冻结（freeze） |
| T0+36h–T0+60h | 05 | 论文主体完成，图表全部替换为最终图 |
| T0+60h–T0+66h | 05 | 摘要+结论精修 |
| T0+66h–T0+70h | 06 | 审计+提交包 |
| T0+70h–DDL | 缓冲 | 编译/查重/网速问题兜底 |

## 3. 硬规则（任何阶段不得违反）

1. **不编数字**：论文每个数值必须有 04 阶段产物或数据文件 provenance；没有验证的结论标 UNVERIFIED 并提示真人。
2. **选题/模型路线/最终提交 三处停点**：必须真人确认才继续（Manual checkpoint）。
3. **联网边界**：允许检索公开方法/文献；禁止直接搜索当年赛题现成题解并照抄（学术诚信 + 撞车风险）。
4. **新颖性不是口号**：每个主模型必须产出 delta 声明（相对 baseline 的数学差异），见 `lib/novelty_gate.py`。
5. **AI 使用报告如实填写**：2025 起竞赛规则普遍要求披露 AI 工具使用情况；最终稿必须附报告（见 stages/06）。
6. 代码、数据、论文各归各目录（code/ data/ paper/），禁止交叉放置。

## 4. 资产地图（只读引用，禁止改动 vendor）

| 资产 | 位置 | 用途 |
|---|---|---|
| 官方 LaTeX 模板（2026） | `paper/templates/cumcmthesis-2026/` | 论文 LaTeX（cumcmthesis.cls + cumcm2026.sty） |
| 数模工业级 skill（MIT） | `code/vendor/math-modeling-skills/` | 算法库、选题分流、角色指南、质量门控、图/文规范 |
| MM-Agent HMML 方法库（CC BY-NC） | `code/vendor/LLM-MM-Agent-hmml/` | 建模方法检索（英文层级树）与 stage prompts |
| 华数杯 2026 官方文件 | 仓库根 `2026年第七届华数杯数学建模竞赛赛题/` | 格式规范实测样本（DOCX 模板+规范 PDF，国赛未出前以它为准） |
| 2018 优秀论文 | 仓库根 `2018年优秀论文/` | 获奖论文写法/常用方法对照（分析对手盘） |

vendor 版本与 sha256 见 `docs/vendor-report.md`；vendor 文件被改过时用 `lib/common.py hash` 校验。

## 5. 快速执行路径

赛题一出、选题已定的情况：
```text
1. cp -r 官方赛题目录 data/contest/cumcm2026/<题号>/official/   # 或直接让 ingest 从 official_dir 复制
2. 改 code/pipeline/config/contest.yaml（contest/problem/official_dir/deadline）
3. python code/pipeline/lib/ingest.py --config code/pipeline/config/contest.yaml
4. python code/pipeline/lib/gates.py --config code/pipeline/config/contest.yaml   # 冷启动自查当前进度
5. 按 stages/01 -> 02 -> 03 逐文件执行，03 结束向真人汇报模型路线
6. 后续按阶段推进；每个 stage md 的"出口条件"满足即前进
```

比赛日开工前 30 秒自检（验证流水线本身没坏）：
```bash
python code/pipeline/tests/smoke_test.py   # 7 项全 PASS 才开工
```

### lib 工具速查

| 工具 | 用途 |
|---|---|
| `lib/ingest.py --config ...` | 赛题入库：manifest + problem.md + 附件转 CSV |
| `lib/gates.py --config ...` | G1-G6 状态自查（冷启动看进度） |
| `lib/novelty_gate.py --input deltas.json --config ...` | 新颖性裁定（PASS/WARN/FAIL） |
| `lib/verify.py --config ... --scripts q1.py [q2.py ...]` | 重跑 diff（容差 1e-6）+ 数值范围 sanity |
| `lib/frozen_numbers.py freeze/list/check/refreeze` | 数字冻结与论文一致性检查 |
| `lib/inject_numbers.py --config ... --tex main.tex` | {{NUM:key}} 占位符注入 |

Python 解释器：`C:\Users\62470\.workbuddy\binaries\python\envs\default\Scripts\python.exe`（依赖已装齐：pypdf/python-docx/openpyxl/pandas/pyyaml）。
