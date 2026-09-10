# Stage 03 — 建模与新颖性门控（Model + Novelty Gate）

输入：候选方法表 + 题目分析报告。
目标：确定每问的主模型（含数学定义、求解路径），并通过新颖性门控。
出口条件（G3）：建模方案.md 落盘；novelty_gate 记录每问 delta 声明 + 裁定（PASS/WARN/FAIL）。
**停点**：模型路线须真人确认后才进入 04。

## 执行步骤

1. **确定主模型**：对每问从候选表选 1 个主推方法，补充：
   - 决策变量 / 目标函数 / 约束（优化类）或 输入→输出映射（预测/评价类）
   - 求解算法（精确 or 启发式，写明工具：scipy/pulp/pymoo/cvxpy…）
   - 数据接口（哪些附件表、哪些列、如何代入）
   - 预期输出形态（数值表/曲线/方案）
2. **新颖性门控**（`lib/novelty_gate.py`）：
   - baseline 定义：从候选表里选"先例频率=高"的方法作为 baseline（烂大街方法）。
   - delta 声明：写明主模型相对 baseline 的数学差异（至少一条）：
     a. **方法层**：用了更先进的算法（如 multi-objective NSGA-III 替代加权 LP）
     b. **模型层**：加了被 baseline 忽略的约束/耦合项（如时空耦合、非线性损耗）
     c. **数据层**：引入了 baseline 没用的数据维度或特征工程
     d. **验证层**：交叉验证/敏感性分析超出常规范围
   - 裁定规则：
     - 有 ≥1 条 b/c/d delta → PASS（模型层创新最有说服力）
     - 仅有 a delta 且先例频率=高 → WARN（算法换皮，撞车风险中等）
     - 无 delta → FAIL（必须换方案或补角度，不允许进入 04）
   - 把 delta 声明与裁定写入 `03_model/novelty_gate.json`。
3. **依赖 DAG**：如果问与问之间有依赖（问2需要问1的输出），画 DAG（拓扑序），
   确定求解顺序。可参考 `code/vendor/math-modeling-skills/references/` 下的 model-formulation-guide。
4. **风险登记**：把模型可能崩的点写进 `03_model/risks.md`（规模爆炸/非凸/数据不足/数值不稳定）+ 兜底方案。
5. 产出 `data/contest/<contest>/<题号>/03_model/建模方案.md`：
   - 每问一节：数学模型（公式 + 符号表）+ 求解算法 + 新颖性 delta + 风险
   - 末尾：DAG 图（mermaid 或文字拓扑序）

## 停点交互

向真人汇报：
```
题号 X 主模型：<方法名>
新颖性 delta：<1-2 句>
baseline：<烂大街方法>
裁定：PASS / WARN
```
真人确认后进入 04。若 WARN，真人可选择接受或要求换方案。

## 纪律

- 公式用 LaTeX 行内/行间写法，与论文一致；符号表必须完整。
- 不堆方法：每问主模型 1 个，最多 1 个备选（写在 risks.md 的兜底方案里）。
- 新颖性不是"用了新名词"：delta 必须是可验证的数学差异，不是宣传语。
