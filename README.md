# CUMCM 2026 数学建模国赛三人协作工程

本项目为全国大学生数学建模竞赛（CUMCM）三人团队协同脚手架，采用 **“GitHub 私有仓库承载共享源码和持续协作，Release 承载精简部署包”** 的轻量化协作体系。

## 快速指引

- **新手与队员必读**：请直接阅读 [START_HERE.md](START_HERE.md) 完成 2 分钟一键部署与开工。
- **AI 智能体指引**：服务于各队员的 Agent 请遵循 [AGENTS.md](AGENTS.md)。
- **三人协作机制**：参见 [team/README.md](team/README.md)（任务分配、不可变 Runs 目录、result.json 与数字冻结）。
- **竞赛流水线指南**：参见 [code/pipeline/runbook.md](code/pipeline/runbook.md)。

## 目录结构

```text
cumcm-2026/
├── AGENTS.md                  # 面向 AI 智能体的通用协作与行为约束
├── START_HERE.md              # 队员与 Agent 开箱快速部署与上手指南
├── requirements-core.txt      # 经实测锁定的 Python 核心依赖
├── scripts/
│   └── bootstrap.py           # 跨平台一键部署与就绪检查脚本
├── code/
│   ├── pipeline/              # 数据清洗、门禁、数字冻结与验证核心工具
│   └── vendor/                # 引用的第三方开源算法库与方法树（只读）
├── data/                      # 赛题官方资料、中间数据与独立运行结果 (runs/)
├── docs/                      # 协作规范、部署合同与方法论文档
├── paper/                     # 论文源文件、LaTeX 模板与编译图件
└── team/                      # 团队任务卡、结果交付模板与 AI 使用记录
```

## 核心流水线自检

在项目局部虚拟环境就绪后，可随时执行流水线端到端健康检查：

```bash
# Windows
.venv\Scripts\python.exe code\pipeline\tests\smoke_test.py

# Linux / macOS
.venv/bin/python code/pipeline/tests/smoke_test.py
```
（全部 7 项测试通过即代表环境完备）。
