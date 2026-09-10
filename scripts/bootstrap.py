#!/usr/bin/env python3
"""CUMCM 2026 自动化部署与环境就绪检查脚本 (Bootstrap Script)

支持 Linux / macOS / Windows。
执行流程：
  1. 识别并校验项目根目录
  2. 探测主机环境与 Python 版本
  3. 创建项目局部虚拟环境 (.venv)
  4. 从 requirements-core.txt 安装核心依赖
  5. 安全生成本地配置文件（不覆盖已有文件）
  6. 运行核心流水线 smoke test
  7. 探查可选排版能力 (xelatex / pdflatex)
  8. 输出结构化部署回执 (bootstrap_receipt.json)
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_project_root() -> Path:
    # 依据脚本自身所在路径向上推导
    root = Path(__file__).resolve().parents[1]
    if (root / "code" / "pipeline").exists():
        return root
    # fallback 到当前工作目录
    cwd = Path.cwd()
    if (cwd / "code" / "pipeline").exists():
        return cwd
    raise RuntimeError(f"无法确定项目根目录，请在项目根目录下执行脚本: {root}")


def get_venv_python(venv_dir: Path) -> Path:
    if platform.system() == "Windows":
        candidates = [
            venv_dir / "Scripts" / "python.exe",
            venv_dir / "python.exe",
        ]
    else:
        candidates = [
            venv_dir / "bin" / "python",
            venv_dir / "python",
        ]
    for c in candidates:
        if c.exists():
            return c
    # 默认返回标准路径
    return venv_dir / ("Scripts" if platform.system() == "Windows" else "bin") / ("python.exe" if platform.system() == "Windows" else "python")


def run_cmd(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, proc.stdout, proc.stderr


def check_tool_available(tool_name: str) -> bool:
    return shutil.which(tool_name) is not None


def main() -> int:
    parser = argparse.ArgumentParser(description="CUMCM 2026 团队部署脚本")
    parser.add_argument("--skip-tests", action="store_true", help="跳过流水线测试")
    parser.add_argument("--no-venv", action="store_true", help="不创建局部虚拟环境，使用当前解释器")
    parser.add_argument("--member-slot", default=None, choices=["member-01", "member-02", "member-03"], help="指定本地成员槽位")
    args = parser.parse_args()

    project_root = get_project_root()
    print("=" * 70)
    print("  CUMCM 2026 三人协作脚手架 — 自动化部署与就绪检查")
    print(f"  项目根目录: {project_root}")
    print(f"  操作系统:   {platform.platform()}")
    print(f"  主解释器:   {sys.executable} (Python {platform.python_version()})")
    print("=" * 70)

    receipt = {
        "schema_version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "project_root": str(project_root),
        "platform": platform.platform(),
        "host_python": f"{sys.executable} ({platform.python_version()})",
        "member_slot": args.member_slot or "unassigned",
        "venv_created": False,
        "venv_python": None,
        "dependencies_installed": False,
        "local_configs_generated": [],
        "smoke_test": {"executed": False, "passed": False, "details": None},
        "capabilities": {
            "core_computation": False,
            "latex_typesetting": False,
            "git_version_control": False,
        },
        "notes": [],
    }

    # 1. 检查 Git
    if check_tool_available("git"):
        receipt["capabilities"]["git_version_control"] = True
        rc, out, _ = run_cmd(["git", "status", "--porcelain"], cwd=project_root)
        print("[OK] Git 工具已就绪")
    else:
        print("[WARN] 本机未检测到 Git 命令行工具，仍可进行离线文件操作与本地计算")
        receipt["notes"].append("Git not detected in PATH")

    # 2. 虚拟环境处理
    venv_dir = project_root / ".venv"
    if args.no_venv:
        venv_python = Path(sys.executable)
        print(f"[INFO] 依据参数跳过 venv 创建，使用当前解释器: {venv_python}")
    else:
        venv_python = get_venv_python(venv_dir)
        if not venv_python.exists():
            print(f"[STEP 1/5] 创建项目局部虚拟环境: {venv_dir} ...")
            rc, out, err = run_cmd([sys.executable, "-m", "venv", str(venv_dir)], cwd=project_root)
            if rc != 0:
                print(f"[FAIL] 虚拟环境创建失败: {err}")
                return 1
            venv_python = get_venv_python(venv_dir)
            receipt["venv_created"] = True
            print(f"[OK] 局部虚拟环境创建成功: {venv_python}")
        else:
            print(f"[OK] 局部虚拟环境已存在: {venv_python}")

    receipt["venv_python"] = str(venv_python)

    # 3. 安装/核验核心依赖
    req_file = project_root / "requirements-core.txt"
    print(f"[STEP 2/5] 核验并安装核心依赖 ({req_file.name}) ...")
    if req_file.exists():
        rc, out, err = run_cmd([str(venv_python), "-m", "pip", "install", "-r", str(req_file)], cwd=project_root)
        if rc != 0:
            print(f"[WARN] pip install 返回异常，尝试直接验证已导入包...")
        else:
            receipt["dependencies_installed"] = True
            print("[OK] 核心依赖包安装/核验完成")
    else:
        print("[WARN] requirements-core.txt 未找到，跳过依赖安装")

    # 4. 生成本地配置文件（保留已有文件，不覆盖）
    print("[STEP 3/5] 检查本地环境配置文件...")
    # 4.1 PROJECT_ID.json
    local_pid = project_root / "PROJECT_ID.json"
    template_pid = project_root / "PROJECT_ID.example.json"
    if not local_pid.exists() and template_pid.exists():
        try:
            pid_data = json.loads(template_pid.read_text(encoding="utf-8"))
            pid_data["canonical_root"] = str(project_root)
            pid_data["canonical_path"] = str(project_root)
            pid_data["control_root"] = str(project_root)
            local_pid.write_text(json.dumps(pid_data, indent=2, ensure_ascii=False), encoding="utf-8")
            receipt["local_configs_generated"].append("PROJECT_ID.json")
            print(f"[OK] 生成本地身份配置: {local_pid.name} (指向当前根路径)")
        except Exception as e:
            print(f"[WARN] 生成 PROJECT_ID.json 异常: {e}")
    else:
        print(f"[INFO] 本地配置 {local_pid.name} 已存在，安全保留")

    # 4.2 code/pipeline/config/contest.yaml
    contest_yaml = project_root / "code" / "pipeline" / "config" / "contest.yaml"
    contest_tpl = project_root / "code" / "pipeline" / "config" / "contest.example.yaml"
    if not contest_yaml.exists() and contest_tpl.exists():
        try:
            shutil.copyfile(contest_tpl, contest_yaml)
            receipt["local_configs_generated"].append("code/pipeline/config/contest.yaml")
            print(f"[OK] 从模板生成本地比赛配置: {contest_yaml.relative_to(project_root)}")
        except Exception as e:
            print(f"[WARN] 生成 contest.yaml 异常: {e}")
    else:
        print(f"[INFO] 本地比赛配置 {contest_yaml.name} 已存在，安全保留")

    # 5. 探查可选能力
    print("[STEP 4/5] 探查系统可用能力...")
    has_xelatex = check_tool_available("xelatex")
    has_pdflatex = check_tool_available("pdflatex")
    if has_xelatex or has_pdflatex:
        receipt["capabilities"]["latex_typesetting"] = True
        tex_tool = "xelatex" if has_xelatex else "pdflatex"
        print(f"[OK] LaTeX 排版引擎可用 ({tex_tool})，支持直接编译论文模板")
    else:
        print("[INFO] 未检测到 xelatex/pdflatex。纯计算/建模队员可正常开展工作，排版交由负责队员统一编译")
        receipt["notes"].append("LaTeX typesetting tools not available on this host")

    # 6. 运行核心 smoke test
    smoke_script = project_root / "code" / "pipeline" / "tests" / "smoke_test.py"
    if args.skip_tests:
        print("[INFO] 依据参数跳过 smoke test")
    elif smoke_script.exists():
        print(f"[STEP 5/5] 执行流水线自检 ({smoke_script.name}) ...")
        rc, out, err = run_cmd([str(venv_python), str(smoke_script)], cwd=project_root)
        receipt["smoke_test"]["executed"] = True
        receipt["smoke_test"]["passed"] = (rc == 0)
        receipt["smoke_test"]["details"] = out.strip()
        if rc == 0:
            receipt["capabilities"]["core_computation"] = True
            print("[PASS] 核心流水线自检 100% 通过！")
        else:
            print(f"[FAIL] 流水线测试未通过 (rc={rc}):\n{out}\n{err}")
    else:
        print("[WARN] 未找到 smoke_test.py")

    # 7. 保存回执
    receipt_file = project_root / "bootstrap_receipt.json"
    receipt_file.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n" + "=" * 70)
    print("  部署完成！就绪摘要：")
    print(f"  - 核心计算能力: {'[READY] 可用' if receipt['capabilities']['core_computation'] else '[WARN] 需检查'}")
    print(f"  - LaTeX 排版能力: {'[READY] 可用' if receipt['capabilities']['latex_typesetting'] else '[OPTIONAL] 未安装 (可独立计算)'}")
    print(f"  - 部署回执已写入: {receipt_file.name}")
    print("=" * 70)
    print("下一步：阅读 START_HERE.md 开始任务或让您的 Agent 接管！\n")

    return 0 if (args.skip_tests or receipt["smoke_test"]["passed"]) else 1


if __name__ == "__main__":
    sys.exit(main())
