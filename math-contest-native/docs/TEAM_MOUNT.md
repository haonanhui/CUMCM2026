# 原生工作区挂载与验证

发布入口为外层仓库 `docs/NATIVE_TEAM_SETUP.md`。本目录是研究工作目录，Git 根在上一层；原文中“本 Git 根”在此发布布局中指本目录的研究路径基准。任何运行命令均从这里执行。无需旧 app、中央注册表或维护者用户目录。

## 环境

- 检查实际 Python 版本。原环境使用 Python 3.9，锁文件保留原记录；优先用兼容解释器建立本目录 `.venv`，运行 `.venv/Scripts/python.exe -m pip install -r requirements.lock.txt`。若当前 Python/索引无法满足锁文件，记录具体错误，用 `requirements.in` 在独立本地环境解析兼容依赖并运行验收，保存解析结果到 `.local/`，不覆盖共享锁文件，不声称复现了原锁环境。
- `. ./Enter-Workspace.ps1` 只影响当前 PowerShell。不要覆盖全局 PATH、模型设置、权限策略或登录凭证。
- 读取 `AGENTS.md`、`docs/SKILLS.md`、`agents/coordinator.md` 和 `.agents/skills/1start-mathmodel/SKILL.md`。技能菜单不可见时可按路径使用，自动发现仍记 UNVERIFIED。角色文件不等于客户端已经注册子 agent。

## TeX Live

先询问安装位置，推荐非系统盘；检测已有安装并优先复用，不重复安装。若用户拒绝，记录 LaTeX 编译未就绪，其余挂载继续。

缺少时从 TUG 官方入口下载 Windows install-tl 安装器，记录来源与哈希，核对其帮助。使用固定可达 CTAN 镜像或用户已有离线仓库，选择 scheme-full 和 portable；按选定根路径设置 TEXDIR、TEXMFLOCAL、TEXMFSYSVAR、TEXMFSYSCONFIG、TEXMFHOME、TEXMFVAR、TEXMFCONFIG，禁用系统 PATH 集成。安装前检查磁盘空间，留存 profile 与日志到 `.local/`。按当前安装器的 profile 无交互方式安装；失败保留日志和可恢复状态，不删除现有安装、不报假成功。下载缓存也放在用户指定盘。

在 `.local/toolchain.json` 写 `{"tex_bin":"<实际安装目录>/bin/windows"}`，重新 dot-source `Enter-Workspace.ps1`，检查 `xelatex --version`、`latexmk -v`、`bibtex --version`。真实运行 `python scripts/paper_smoke.py --tex-bin <实际bin目录>`，检查中文字体、PDF 页面及日志；仅找到 exe 不算编译通过。Linux/macOS 按其官方安装方式和路径适配，现有 Windows paper_smoke.py 不直接冒充跨平台验收。

## 验收与恢复

运行 `python scripts/doctor.py`、`python scripts/selfcheck.py`，保存输出到 `.local/`。doctor 是清单，不会因缺包自动失败，必须检查所有必需依赖字段。嵌套发布布局的 `git_root_present` 可能为 false，另以 `git rev-parse --show-toplevel` 验证外层仓库。

用当前 Agent 实际读取六个 SKILL.md 并报告各阶段职责，写读一个 `.local/` 临时文件再清理，证明当前会话具备访问能力。需要验证其他 Harness 时单独执行，不能继承本会话结论。完成后记录本机验收与启动方式；不把历史报告的 PASS 当本机结果。

当前论文、plan/todo、results 和原状态均是历史演练材料。发布状态指向队友挂载任务；开始新赛题前确认题面、附件、赛事规则、截止时间与允许的 AI 使用方式，创建新任务与新 run，保留历史材料。
