# 研究实现

沿用上游逐问题实现并运行的方式。任务复杂时按 `data_io/`、`models/`、`solvers/`、`validation/`、`reporting/` 拆模块，共享接口放 `interfaces/`。这些目录随实际任务创建，不预造空实现。

当前只有 `examples/mean/` 的合成演练，不含实际赛题模型。实现接口、输入版本、参数、停止条件和验收口径先在分析建模报告说明；结果与图件来源写 RESULTS_REPORT。
