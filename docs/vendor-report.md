# Vendor 资产报告（版本与完整性基线）

> 基线建立：2026-09-10。vendor 目录只读；文件被改动时用本文哈希校验并登记原因。

## 校验方法

```bash
# 单资产整体指纹（文件清单+逐文件 sha256 的聚合 hash）
find code/vendor/<name> -type f -exec sha256sum {} + | sha256sum
```

## 资产清单

| 资产 | 上游 | 许可证 | 文件数 | 聚合 sha256 | 引入内容 |
|---|---|---|---|---|---|
| math-modeling-skills | github.com/xuec699-sudo/math-modeling-skills（v5.8.1） | MIT | 122 | `128bd86c50eec3f6e62d5cc3a60a784c2364e7f2b035d79ada8812f7a495e975` | G1-G6 门控语义、60+ 脚本（build_docx / quality_gate / plot_figures_nature / check_data 等）、7 类算法库、角色指南、选题分流（已清理嵌套克隆） |
| LLM-MM-Agent-hmml | Fast-MM 项目（github.com/bluemoon-o2/Fast-MM）的方法库部分 | CC BY-NC | 11 | `2bc811f3514b24cf4abe27a117feb2b7ff9c815bae73ad8c99472f8f006b4997` | HMML.json 方法层级树（5 大类→子域→叶子方法，含 modeling_method/core_idea/application）+ stage prompts |

## 调研记录（2026-09-10）

社区主流数模 agent 实现盘点：

| 项目 | 形态 | 结论 |
|---|---|---|
| jihe520/MathModelAgent | Docker+Redis+WebUI 平台 / skill 版 | **不引入**：平台形态与本项目"harness 内跑 runbook"冲突；增量（Typst 模板、决策树）已被现有资产覆盖 |
| bluemoon-o2/Fast-MM | 多 agent DAG + Actor-Critic | **部分引入**：HMML 方法树（见上） |
| xuec699-sudo/math-modeling-skills | Codex/Agent skill | **全量引入** |

## 本项目使用边界

- vendor 代码只在比赛流水线中被调用/引用，**禁止原地修改**；需要定制时在 `code/pipeline/lib/` 里包一层。
- CC BY-NC（HMML）：仅限竞赛内部使用，论文引用方法时注明来源。
- 若 vendor 升级：先跑本文校验方法重建基线，再更新本表。
