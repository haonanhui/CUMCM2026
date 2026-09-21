# 上游规范的原生 Harness 适配

研究工作流以固定版本的 MathModelAgent skills 为主，保留阶段名、报告名与模板布局。本文件只说明平台差异和竞赛证据边界；不引入另一套建模流程。

- `Bash/Read/Write/Edit/Grep/Glob/Agent/WebSearch/WebFetch/AskUserQuestion` 是上游工具语义。使用当前 Harness 对应能力；无同名工具不等于无法执行。Windows 原生 PowerShell 不能直接执行 Bash 片段，需真实 Git Bash 或转换等价命令。不得假造工具调用。
- `.agents/skills` 是唯一技能正文。DSH 已安装 filesystem skill provider 的源码/文档明确支持此目录；Codex 原生技能列表另做实测。根 `AGENTS.md` 同时给出手动读取入口。
- 角色说明位于 `agents/`。主会话可以承担角色；只有 Harness 支持且任务适合委派时才调用原生子 agent，并明确写范围。Markdown 角色文件不被冒充成 DSH preset 或已注册 Codex agent。
- 上游后端“文件预上传、不检查存在”只适用于它的沙箱。本地必须验证输入真实存在；上游固定章节比例和模型选型速查是参考，不能替代当年赛事规则与数据适用性判断。
- 保留 `plan.md`、`todo.md`、`reports/`、`results/`、`figures/`、`paper/`；其中 `results/runs/<id>/` 保存不可覆盖的运行证据，论文采用的图表通过清单关联其来源。研究代码可在 `code/` 内按模块拆分。
- 已经明确的引擎、语言等用户偏好直接沿用；关键偏好未知时再问。不重复确认已获授权的普通阶段动作。
- 上游 6verity 允许“说明不可编译/无法视觉检查原因”后给 PASS；本工作区收紧表述：未执行项保持 UNVERIFIED，总体竞赛提交就绪不成立，不能把解释当验收。文本检查和文件哈希不证明科学正确或视觉质量。
- 上游模板保留作候选资源；来源链、当年官方格式与适用许可必须在采用时核对。模拟绘图模板数据只能演示，不能作为实测结果进入论文。
- 上游 doctor 的安装命令是参考；不自动执行系统安装，不写全局 PATH。Python 依赖装项目 `.venv`；TeX Live 采用用户既定非 C 盘方针。环境检查脚本不调用该 skill 的安装流程。

本轮不修改个人 CODEX_HOME/DSH_HOME，也不注册全局服务；各 Harness 的全局规则仍可能被加载。工作区可移植不等于模型、配额、网络和服务权限相同。
