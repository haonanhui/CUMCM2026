# Stage 04 — 求解与验证（Solve + Verify）

输入：建模方案.md + novelty_gate.json + 附件数据。
目标：跑通全部求解，产出可复现的结果表/图，冻结数字。
出口条件（G4）：每问结果脚本可一键重跑；复现清单.json 数字与论文一致。

## 执行步骤

1. **代码落盘**：每问一个脚本（`code/solve/q<N>.py`），自包含：
   - 读数据路径用相对 config 的方式（不硬编码绝对路径）
   - 输出到 `data/contest/<contest>/<题号>/04_solve/q<N>/`
   - 产物：`result.csv`（数值表）、`fig_*.png/svg`（图）、`log.txt`（求解日志/收敛曲线）
2. **求解执行**：按 DAG 拓扑序跑；若问间有依赖，前一问结果文件作为后一问输入。
3. **验证**（`lib/verify.py`）：
   - 重跑确认：清空输出目录 → 重跑 → diff 结果（数值容差 1e-6）
   - 合理性检查：结果量纲/数量级是否在物理/工程常识范围内（如面积>0、概率∈[0,1]）
   - 敏感性分析（若建模方案要求）：关键参数 ±10% 扰动，记录输出变化
4. **冻结数字**（`lib/frozen_numbers.py`）：
   把论文要用到的所有数字（目标值、最优解、误差、指标）提取到 `04_solve/frozen_numbers.json`，
   格式 `{数字: {value, source_file, source_line, tolerance}}`。
   论文写作阶段只能引用此文件中的数字，禁止手填或凭记忆写。
5. **复现清单**：生成 `04_solve/复现清单.json`：
   ```json
   {
     "environment": "python 3.13 / venv path",
     "scripts": ["q1.py", "q2.py"],
     "commands": ["python code/solve/q1.py --config ..."],
     "expected_outputs": ["result.csv", "fig_q1.png"],
     "rerun_verified": true,
     "frozen_numbers_hash": "sha256..."
   }
   ```
6. 产出汇总：`04_solve/求解结果报告.md`（每问：方法简述→关键数字→图→异常说明）。

## 异常处理

- 求解失败（超时/不收敛）：记录失败原因 → 查 `03_model/risks.md` 兜底方案 → 切备选方法 → 重跑。
- 数字异常（量级不对）：先查数据单位/量纲 → 再查模型公式 → 最后查求解器参数。
- 所有异常与切换决策写入 `04_solve/incident_log.md`。

## 纪律

- 图表风格统一用 `code/vendor/math-modeling-skills/scripts/plot_figures_nature.py` 的 Nature 风格模板。
- 代码注释写"为什么"不写"是什么"。
- 禁止在论文里写任何不在 frozen_numbers.json 里的数字。
