## 队内共享发布布局

本目录是研究工作目录，Git 根在上一层；下文所有研究相对路径以本目录为准。先读 docs/TEAM_MOUNT.md。PROJECT_STATE.json 为发布接入状态，原研究状态保存在 provenance/SOURCE_PROJECT_STATE_20260921.json。历史论文仅展示架构能力，不是优秀案例，不默认续跑。

# 数模竞赛原生工作区

本目录是独立竞赛主工作区。所有相对路径以本 Git 根为基准。Codex、DSH 和其他 Harness 共享文件事实，不共享聊天记忆。

## 开始与恢复

先读 `PROJECT_STATE.json`、`docs/WORKSPACE_SPEC.md`，再读当前 `team/tasks/<task>.json` 和 `team/handoffs/<task>.json`。核对 Git 状态，保护队友和其他会话改动。读 `docs/SKILLS.md` 与 `agents/README.md` 选择阶段和职责，按需读取技能全文。

skills 与 agents 的规范以用户指定的 GitHub MathModelAgent 系列仓库为主。准确来源、固定版本及本地适配见 `provenance/UPSTREAM.md`；不可把 app 自撰规范替代指定上游。Harness 适配只处理路径、可用工具和恢复机制，不静默改变研究阶段的含义。

## 研究与证据

用户 2026-09-21 追加论文质量要求：保留 MathModelAgent 六步流程，写作先全文读取 `docs/PAPER_WRITING_GUIDE.md`（writing-guide-2），按研究内容单元和正向表达要求形成初稿；写作和验收同时全文读取 `docs/PAPER_QUALITY_STANDARD.md`，记录实际路径与版本。上述文件是用户授权的本地质量补充，不冒充上游原文。近期参考统计和表达模板在 `docs/paper-quality/`；同题内容比较见 `reports/PAPER_ORGANIZATION_AND_LANGUAGE_20260921.md`。

论文评分使用 internal-v3.1，必须全文读取 `docs/paper-quality/SCORING_ANCHORS.md`，先逐问检查内容充分性再评分。论文交付必须有同一 PDF 哈希对应的逐项质量评审。文本检查、编译、图表存在、数值绑定分别报告，不能合并为论文质量 PASS。章节短或图后解释不足若反映模型、推导、实验分析缺失，必须返修；不能只记软提示后交付。旧 `reports/VERIFY_REPORT.md` 的首版 PASS 不构成新版论文质量认可。

- 未确认赛事、题号、截止时间、AI 使用规则与论文格式保持 null/unknown；不能从目录名或旧模板推断。
- 原题与官方附件只读保存；清洗输出到派生目录，记录来源、单位、缺失值处理、版本与哈希。
- 模型、求解、验证、绘图分模块；实现共享接口先写 `code/interfaces/`，不把所有逻辑堆入单一入口。
- 每次运行新建目录；记录输入/源码/配置指纹、依赖版本、随机种子、命令、结果与失败。不得覆盖旧实验制造成功记录。
- PASS 必须对应真实执行与明确覆盖；退出码 0 不等于数学正确。无执行证据写 NOT_RUN/UNVERIFIED。
- 论文数字和图表关联确定 run 与产物；文献回到原始来源核验。不得编造实验、引用、人工审查或 AI 声明。
- 所有图内文字使用中文，公式、变量和数学符号保留原写法；绘图和验收须读 `docs/FIGURES_ZH.md`，此用户定制覆盖上游按论文语言切换图内文字的约定。
- 具体赛事规则以当年官方材料及适用赛区要求为准；所有规范核验记录 URL/文件、访问日期与适用年份。

## 协作与授权

三名队员各自工作副本，用 Git 同步。任务文件明确 owner、写范围与依赖；多人或多 Harness 同时工作时不写同一个任务文件。共享 `PROJECT_STATE.json`、论文绑定与接口由当班集成人串行维护。模型选择与最终提交由用户/队员按当前授权裁定，聊天授权可以作为记录来源，不要求 app UI。

常规授权工作自主推进；不因阶段编号反复要求批准。停止条件是用户暂停、关键输入缺失、越权边界、预算耗尽或无新信息的重复失败。提交前只 stage 本任务文件，不执行破坏性 Git 操作，不自动 push。

每次交接写任务、分支/commit、未提交内容、已读输入、真实验证与证据、失败尝试、下一动作、未决项，并先重读 revision。全局状态只保留集成事实；不依赖本机私有会话目录恢复。

## 运行边界

原生 Harness 直接读写此目录。无需启动 app，也不使用 app 的 pipeline 工具、环境变量、数据库或 UI 确认。个人登录与模型设置沿用用户自己的 Harness；不得复制凭证、覆盖全局配置或替用户降低权限。角色文件是职责说明，不意味着任何 Harness 已注册同名子 agent。

第三方资产保留来源、许可与署名；工作区和竞赛提交包分别管理。提交包按明确允许清单组装，排除 skills/agents、凭证、会话、.git、环境目录与身份信息，具体以赛事规则为准。
