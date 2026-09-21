# 来源与适配记录

2026-09-21 科研图技能：用户将本轮目标纠正为math-contest-native。新增本地自有 `.agents/skills/cumcm-scientific-figure/`，按用户指定PAPER_FIGURE_STYLE_SPEC独立实现，不复制第三方技能正文/脚本/字体。只读审查原工作区figure-router、paper-diagram、nature-figure及本工作区mathmodel-figure-templates；上游原件未改。docs/SKILLS与FIGURES_ZH接入辅助入口；不改六步流程，12 pt论文合同保留，参考风格不冒充期刊强制标准。loader探针由固定9条改为与磁盘技能集合比对，以支持新增技能且检查遗漏。

2026-09-21 本轮本地适配：writing-guide-2、native-quality-4/internal-v3.1、figure-style-2 增加用户指定的正向表达、零修辞引号、具体动作句和图下 TeX 说明。修改 5writing/6verity 的本地入口；24项评分权重不变，上游快照与模板保持原字节。依据与适用范围见 docs/PAPER_POLICY_REVISION_20260921.md 及图件来源记录。现存三版论文和前两轮规则以 ef8211d 首次归档；此提交是恢复快照，不是追造历史提交。

主来源：[jihe520/MathModelAgent](https://github.com/jihe520/MathModelAgent)。用户本轮明确指定其 skills 和 agents 规范为主。

- 固定提交：`487f35085271f2f5bac5c0bad0b30c64b7b889f9`；2026-09-20 通过 `git ls-remote ... HEAD` 核对仍为当前 HEAD。
- skills：从原开发仓库已固定的同版本快照复制 618 个文件，原来源和现文件 SHA-256 逐项见 `skill-files.json`。
- agents：从同一 commit 的 `backend/app/core/prompts/{coordinator,modeler,coder,writer,shared}.py` 下载原始文本，保存在 `upstream/`；只作参考，不 import、不执行平台后端。四类职责在 `agents/` 形成原生文件版。
- 授权依据：原项目 `docs/decisions/LICENSE_AUTHORIZATIONS_20260917.md` 已登记主理人获作者同意用于本人和队友科研学习/定制。此次按当前请求建立本机工作区；不发布公开仓库或打包对外分发。上游声明原文保留于 `upstream/License.md`。
- 上游二次加工模板的独立来源链未全部核实；包含模板资源不等于证明其适用当年赛事或可公开再分发。采用时单独核验，不将 skill 库并入竞赛提交包。

## 精确适配范围

1. 九份可执行 SKILL.md 保留上游工作步骤；移除 Claude 专属 `allowed-tools` 名称白名单，增加原生兼容说明链接。原入口保存在 `upstream/skill-entrypoints/`。
2. `_references/SKILL.md` 改为 `_references/REFERENCE.md`，知识库正文路径不变，避免把不可执行且名称含下划线的参考库注册成技能。
3. `mathmodel-figure-templates` 入口的 `/home/user/.claude/skills/...` 改为项目相对路径；渲染脚本和图件模板保持上游字节不变。
4. 根 `docs/HARNESS.md` 明确 Windows 命令等价映射、真实输入核对、已确认偏好复用，以及不能把“未编译/未看 PDF”计成竞赛总体 PASS。此为工作区适配差异，不冒充上游原文。
5. 角色说明保留协调/建模/编码/写作职责，并路由到六步技能；未复制后端 API、虚构工具、全局配置或固定模型型号。上游 modeler 模型速查和 writer 章节占比作为参考，实际以题面及当年规则为准。
6. 用户明确要求绘图定制：图内文字统一中文、公式符号除外。已修改 3coding-visual、4drawio、mathmodel-figure-templates、5writing、6verity 及共享规范的语言/检查约定，统一指向 docs/FIGURES_ZH.md。上游模板脚本本体未改，使用时在复制出的脚本中中文化；合成演练脚本已实际中文化并检查缺字警告。

## 自有补充

2026-09-21：用户指出原生工作区 11 页 NPU 论文过于基础、版式紧密且此前质量标准未生效。按本轮授权增加 `docs/PAPER_QUALITY_STANDARD.md`，并在 AGENTS、5writing、6verity、writer 和技能索引设置必读入口；保留六步流程与原始上游快照。本地 internal-v2 是用户先前授权制定的质量补充，不是上游原文。参考统计和 18 条项目自撰表达模板从 cumcm-2026/docs/research/paper-quality 复制到 docs/paper-quality，后者可独立读取，无 app 依赖。本次不改上游模板或历史原始快照；skill-files.json 保持初始导入基线，新增差异以本段登记，不宣称当前入口字节仍等同导入值。

根入口、任务/交接与结果清单吸收 cumcm-2026 通用协作脚手架的做法；Python 运行记录工具和环境检查在本目录独立实现。app 状态、训练数据、会话、.venv、vendor 平台与其他许可不明个人技能未复制。

后续更新先固定新 commit、比较差异和许可，再更新技能及清单；不自动追随远端 main。正文可由各 Harness 编辑，修改后更新来源差异，不能仍宣称与上游逐字一致。

## 2026-09-21 内容组织与正向表达适配

再次核对远端 main 为固定提交 487f35085271f2f5bac5c0bad0b30c64b7b889f9。新增本地原创 PAPER_WRITING_GUIDE、12 条功能改写和同题组织分析，接入根入口、5writing、6verity、writer 与索引。internal-v2 权重不变；未修改 upstream 原始快照。既有本科语料只迁移段落功能，未分发原文库。

## 2026-09-21 评分锚点修订

核对上游 main 树及6verity：固定提交未变化；该入口提供工程和成品检查，没有百分制评分量表。用户授权新增 internal-v3 逐问证据矩阵、24项锚点、分数与缺陷一致性检查。权重沿用v2，历史报告保持原版本；修改本地入口，不修改upstream快照。

## 2026-09-21 队内共享授权
用户本轮明确授权将完整原生流程上传 haonanhui/CUMCM2026 供队友访问挂载。已核实该仓库为 PRIVATE；本次仅私有小队共享，不改变上游许可或授权范围。原本机不发布表述由本次明确的私有队内发布授权补充。保留上游来源、模板边界与许可文件。

