# 队友 Agent 自动接入

当前唯一竞赛入口是仓库的 `math-contest-native/`，不安装旧桌面 app，不执行旧根目录 bootstrap。仓库为小队私有共享；使用队友自己的 GitHub 账号与 Harness 登录，不复制维护者配置。

## 发给 Agent 的 prompt

```text
请自动接入 https://github.com/haonanhui/CUMCM2026 的 math-contest-native 原生数模工作区。先读仓库 docs/NATIVE_TEAM_SETUP.md。首次只集中询问本地仓库保存位置、TeX Live 安装位置（推荐非系统盘；已安装则询问现有位置）。获得回答后持续完成克隆、项目局部 Python 环境与依赖安装、技能/角色接入、资料下载和验收，不逐步索要确认。工作目录必须是 math-contest-native；读取该目录 AGENTS.md、START_HERE.md、docs/TEAM_MOUNT.md，按六步流程准备就绪。推荐安装完整 TeX Live：先检查是否已有可用安装；缺少时按官方说明在用户指定位置自动安装，再配置本地 toolchain.json 并真实编译中文样例。下载 native-team-20260921 Release 的历年赛题和优秀论文，按清单核验 SHA-256。现有 NPU 论文仅供了解架构能力，不是优秀参考案例，不自动续写或冒充正式参赛结果。保留现有全局配置和文件；登录/系统权限确需本人操作时一次说明。最后报告真实通过项、未验证项、工作目录及下一次启动方式。
```

## 接入步骤

1. 检查 GitHub 私有仓库访问权限；缺权限时请仓库所有者添加 collaborator，不能绕过认证。已有克隆先检查 remote 与未提交修改，禁止覆盖或 reset。新克隆使用 `git clone https://github.com/haonanhui/CUMCM2026.git <用户目录>`。
2. 进入 `math-contest-native`，按 `docs/TEAM_MOUNT.md` 执行。Git 根是外层仓库，研究命令的相对路径基准是内层目录；不把内层 `.agents` 投放到全局。
3. 在 Codex/DSH 中把工作目录设为该内层目录。读取技能正文与角色文件；分别验证文件可读、loader 发现、真实模型使用，不能混报。登录使用本人账号，已有 Harness 不擅自替换。
4. 下载 [资料 Release](https://github.com/haonanhui/CUMCM2026/releases/tag/native-team-20260921)。私有资产须通过已登录的 `gh release download native-team-20260921 --repo haonanhui/CUMCM2026 --dir <内层目录>/.local/references-download` 获取。按 `references/assets.json` 核验每个压缩包的字节数与 SHA-256，再解压到外层仓库的 `references/library/<压缩包名>/`，不要覆盖已有资料。
5. 返回实际检查结果。环境就绪后等待队友指定正式赛题，禁止自动启动历史 NPU 论文修订。三人各用自己的克隆与任务分支，通过 Git 同步。

TeX Live 安装依据：[官方安装入口](https://tug.org/texlive/acquire-netinstall.html)、[install-tl 参数](https://tug.org/texlive/doc/install-tl.html)。推荐完整 scheme-full；profile 支持无人值守安装，portable 避免系统集成。实际参数以下载的安装器 `--help` 为准。
