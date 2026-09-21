# 声明与授权登记（事实记录）

- 日期：2026-09-17
- 记录人：主 agent
- 性质：**事实记录**。不构成法律意见，不改动任何上游条款。

## 1. 已登记的声明

| # | 内容 | 记录位置 |
|---|---|---|
| 1 | 主理人声明：**仅供科研学习使用，不盈利，不外传，自行承担相关法律责任** | `OWNER_USE_INTENT_20260917.md` |
| 2 | 队友亦已出具自担责任声明 | 本表（主理人告知） |
| 3 | 主理人已向 **jiehe（jihe520）** 申请：*"能否把仓库中所有内容拿来自己科研学习，定制化自己的 app 并打包给我和我的队友使用"*；**jiehe 表示理解并同意，并立字据说明一切法律责任由小队自行承担** | 本表（主理人告知） |

**证据保管**：声明与字据的原件由主理人保管。本文件只记录事实与范围，**不再重复索取**。

## 2. 第 3 条的**范围**（按上游归属，纯事实）

jiehe 的同意覆盖 **jihe520 名下仓库的内容**：

| 资产 | 上游 | 是否在 jiehe 可授权范围内 |
|---|---|---|
| `code/skills/paper-search` / `data-search` / `doctor` | MathModelAgent（jiehe） | ✅ 在范围内 |
| `code/skills/paper-diagram` | `jihe520/sci-box`（jiehe） | ✅ 在范围内 |
| `paper-diagram/assets/icons/tabler/**` | Tabler Icons（Paweł Kuna），MIT | ⚠️ 第三方，**notice 随文件保留**（与本授权无关） |
| `paper/templates/cumcmthesis-2026` | `latexstudio/CUMCMThesis` | ❌ 独立上游 |
| `code/vendor/math-modeling-skills` | `xuec699-sudo/...` | ❌ 独立上游 |
| `code/vendor/LLM-MM-Agent-hmml` | `bluemoon-o2/Fast-MM` | ➖ 已有 **CC BY-NC**（本项目非商业 ⇒ 可用） |

> 这一个范围划分是**纯技术事实**（谁拥有哪个上游），不涉及对任何声明的怀疑。

## 3. 打包与提交的当前处置

- **不随包分发的资产清单**：`support/not-packaged/manifest.json`（清单由主理人维护）。
- **提交归档允许清单**：`paper/build/*.pdf`、`paper/src/*`、自有图表、自有代码。
- **论文独立性**（与许可无关，仍须遵守）：论文内容由队员自行产出。

## 4. 待办（由主理人处理，不阻塞其他工作）

1. `paper/templates/cumcmthesis-2026`（无 LICENSE）与 `code/vendor/math-modeling-skills`（无 LICENSE 文件）—— 两条路：向对应作者申请，或**改用 CUMCM 官方当年发布的模板**（官方模板即为参赛使用而发布，且 `runbook.md:58` 本就要求核验"模板来源与当年官方格式"）。
2. 是否把 jiehe 已覆盖的四项 `code/skills` 从 `not-packaged` 清单中移出 —— 由主理人决定，清单由主理人维护。
