 > **首次挂载优先读 [docs/TEAM_MOUNT.md](docs/TEAM_MOUNT.md)**。本机环境不会随 Git 复制。示例论文不是优秀参考案例；不要自动恢复历史论文任务。

# 开始使用

## Codex

在 Codex Desktop 把本目录添加为项目并在这里新开任务，或在终端进入本目录执行 `codex`。按客户端提示信任你确认过的工作区。不要从旧 app 的启动器进入。

## DSH

在终端进入本目录执行 `dsh --profile tui`（需要已配置可用的 tui profile），或使用自己的 DSH 界面并将工作目录选为本目录。使用已有登录配置；本工作区不拷贝或改写个人密钥。其他 profile 是否包含文件、技能插件须分别验证。

两者都可直接发送：

> 读取 AGENTS.md、PROJECT_STATE.json、agents/coordinator.md 和 .agents/skills/1start-mathmodel/SKILL.md。按 MathModelAgent 工作流恢复当前任务；已有事实从文件读取，缺少实际题面时不要开始虚构求解。

如果技能未出现在客户端菜单，先按精确文件路径读取；这能继续工作，但“自动发现技能”一项保持待验证。菜单缺失与文件不能读写是不同故障。

## 接续另一 Harness 的任务

先由当前 owner 更新 `team/handoffs/<任务>.json`，保留命令、输入/输出、未提交改动和下一动作。在另一个 Harness 打开同一工作副本，读根规则、当前任务与 handoff，核对文件后接续；不得把它当成新题从头开始。不要让两个活跃会话同时修改同一任务写范围。

## 本地工具

本机已建立独立 `.venv`；在 PowerShell 中先执行 `. ./Enter-Workspace.ps1`，仅为当前会话接入项目 Python 与 `.local/toolchain.json` 指定的 TeX。然后运行 `codex` 或 `dsh --profile tui`，子进程继承该 PATH。Desktop 会话未继承此 PATH 时明确使用 `.venv/Scripts/python.exe` 和实际 TeX 路径。

队友设备先用自己的 Python 3.9 建立 `.venv`，再用 `.venv/Scripts/python.exe -m pip install -r requirements.lock.txt` 重建此次已验证环境；不同 Python 版本应单独解析与验证，不覆盖共享锁文件。TeX 实际路径填入本机 `.local/toolchain.json`，格式 `{"tex_bin":"D:/texlive/2026/bin/windows"}`，按该设备安装位置修改。本目录不依赖旧仓库 `.venv`。

```powershell
python scripts/doctor.py
python scripts/selfcheck.py
python scripts/run.py --config examples/mean/config.json --id practice-001
```

同一 run id 不可覆盖。配置说明见 [docs/RUNS.md](docs/RUNS.md)。合成样例只验工具链，不是竞赛数据或科学结论。

数值/排版依赖按实际题目与引擎准备；Windows LaTeX 优先使用赛前完整安装到非 C 盘的 TeX Live，按实际安装位置配置当前终端 PATH。不要在比赛期间才首次安装完整工具链。
