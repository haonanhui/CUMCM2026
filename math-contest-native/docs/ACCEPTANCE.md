# 工作区验收（2026-09-20）

结论：独立文件工作区已建立，本机基础工具链及原生技能加载通过。可在此开展原生 Harness 工作；真实模型跨会话接续、队友设备和特定赛事提交资格尚未验收。

## 已执行证据

| 检查 | 结论 | 证据与实际覆盖 |
|---|---|---|
| 上游版本 | PASS | GitHub HEAD = 487f35085271f2f5bac5c0bad0b30c64b7b889f9，与引入快照一致 |
| 618 文件来源/适配清单 | PASS | provenance/skill-files.json；当前文件逐个哈希核对 0 不匹配；不代表正文全部精读 |
| 九项技能格式 | PASS | skill-creator quick_validate.py 以 Python UTF-8 模式逐项执行，9/9 |
| Codex 原生 loader | PASS | evidence/codex-loader.json；真实 skills/list 返回 9 项 enabled=true，0 errors；没有模型回合 |
| DSH 原生 provider | PASS | evidence/dsh-provider.json；已安装 dsh-skill-filesystem 原生 list/get 逐项发现并读取 9 份正文，0 warnings；用测试上下文调用 provider，非完整 DSH 模型会话 |
| 原生角色文件 | PASS（文件层） | agents/ 四类职责可直接读写、引用真实技能路径；未宣称注册为 Harness 原生子 agent |
| 独立环境 | PASS | 项目 .venv，Python 3.9.13，requirements.lock.txt，pip check 无依赖冲突；不引用旧仓库运行环境 |
| 运行证据边界 | PASS | evidence/selfcheck.json；两次独立 run 得到均值 5，重复 ID/路径逃逸/空 expect 被拒，失败命令和输入变更被记录 |
| 中文论文合成链 | PASS | evidence/paper-smoke.json、synthetic-paper.pdf、synthetic-paper-page.png；数据→solver→图→XeLaTeX 两次→1 页 PDF；页面实际查看，无缺字、重叠、裁切 |
| 上游验收脚本入口 | PASS（help 范围） | D:/Git/bin/bash.exe 执行 6verity/scripts/writing_check.sh --help 成功；未声称其所有论文检测语义已验证 |

当前最新合成 run：`results/runs/paper-smoke-20260920T153524148148/`。它明确为 synthetic；不是实际赛题结果。详细编译日志/中间文件留在同名 `.local/` 目录，关键 PDF、页面和回执已复制到本目录 evidence。

用户追加的图内中文定制已落地：数据图、DrawIO、模板复刻、写作嵌图、最终验收及共享规范同步约束。最新示例采用 Microsoft YaHei；轴名和图例中文、数学均值符号保留，缺字警告为零，实际渲染页面已检查。旧英文演练只保留为历史证据。

## 未验证与限制

- **UNVERIFIED**：Codex 新模型会话写 handoff → DSH 模型接续并回写 → Codex 恢复。这一轮未发送真实模型任务，未消费模型生成预算。
- **UNVERIFIED**：队友机克隆重现、断网准备、真实赛题完整求解、当年赛事规则及官方模板、最终提交。
- **WARN**：PATH 未发现 Typst/DrawIO；XeLaTeX 已实跑，可用于论文；需要 Typst 或 DrawIO 导出时另行准备并验证。不能把未安装工具标成可用。
- **WARN**：上游模板的独立来源链未全部核实；只保留候选，采用和分发需按实际范围核验。
- **范围**：run 工具校验声明文件和输出，不沙箱化 solver，不证明数学正确；未声明依赖、模型账号/网络/配额、全局 Harness 指令不在此验收范围。

## 已纠正的本轮问题

1. DSH provider 会把技能根 README.md 当 flat skill，产生缺 YAML 警告；索引改放 docs/SKILLS.md 后原生探测 0 警告。
2. skill-creator 的验证脚本默认按 Windows GBK 读文本失败；改为 `-X utf8`，九项均通过；未改第三方验证器。
3. 最初 PATH 无编译器不代表机器未装；实查找到 D:/texlive/2026，通过当前工作区会话 PATH 接入并实际编译。

临时 selfcheck 沙箱自动清理；Python/Matplotlib 自建缓存已按精确文件清理。保留 .venv 作为独立依赖，保留三个合成 run 和编译目录作为证据。未修改原 app 仓库、已有 math-contest-workspace、全局配置；未 push。

后续按 PREFLIGHT.md 做真实双 Harness 接力和队友实机演练，之后才可提升对应准备状态。
