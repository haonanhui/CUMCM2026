# 原生工作区队内发布检查（2026-09-21）

本次用户授权：将 math-contest-native 完整流程、现有演练论文和近年参考资料上传到 haonanhui/CUMCM2026，供队友挂载。发布前已确认仓库 PRIVATE。

源工作区基线 `1d4fc98ee93d6971cb30d127cab4e9b2c791a359`，包含发布时磁盘上的未提交图件/论文/技能改进；两处原工作区均未切分支、清理或提交。独立克隆以远端 main `23ef08789236c67c1a8f384b08f1d06d6d910002` 为基础新增内层原生工作区，保留外层旧文件并改入口路由。未改研究算法或科学阈值。

已读：两工作区 AGENTS/PROJECT_STATE、原项目 AGENT_PROJECT_MAP、原生 WORKSPACE_SPEC、SKILLS、角色索引、typography task/handoff、UPSTREAM 和原授权记录。工作区不依赖本机中央治理身份文件。

## 实际结果

- PASS：发布副本 selfcheck 六项，包括独立运行复现、重复 ID 拒绝、失败记录、路径越界、输入变化和空期望拒绝。
- PASS：发布副本 Codex loader 返回磁盘对应的 10 项技能，enabled=true、errors=[]；创建独立短命 app-server，模型调用为 0。未触动共享 Desktop。
- PASS：合成计算→中文图→XeLaTeX 两遍编译→1 页 PDF；无缺字警告，渲染后检查中文、数学符号和曲线可见。PDF SHA-256 `82b996181cdbf8507bb5218992884ee7cc6c5be9d4c0f3f4163b58d34dffc89f`。
- PASS：八个参考压缩包内 1,248 项逐文件字节数与 SHA-256 对应原文件。剔除一个隐藏 Word 锁文件，不修改原资料目录。
- PASS：最新演练论文保持原 PDF SHA-256，新增醒目的非优秀案例声明。
- PASS：本轮新写接入文档的 staged whitespace 检查；整个引入快照保留源字节，源文件 CRLF/既有空白不为发布而重写。
- UNVERIFIED：队友真机、全新 Python 依赖下载安装、TeX Live 全新安装、DSH 本轮 loader、真实模型执行全流程、正式赛事资格。上述自检使用维护者现有 Python 3.9 环境和 TeX Live，不能宣称队友环境已通过。

## 保存与清理

未上传凭证、.venv、.local、个人全局配置和机器专属 PROJECT_ID。现有实验/图件/论文版本属于可追溯研究材料，保留；新自检临时沙箱由脚本自行清理，编译证据保留在发布副本 .local，资料 ZIP 保留为发布工件。队友挂载将重新验证，不继承历史 PASS。

资料年度限于本地现存 2022—2025 年研究生赛题与优秀论文集。来源名称保留，不宣称逐篇复核奖项或通用于本科赛事。
