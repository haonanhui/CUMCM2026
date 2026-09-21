# 第二版研究阅读稿

成品：`../NPU_2025_A_revised.pdf`。源入口：`main.tex`；旧稿 `../main.tex` 与 `../NPU_2025_A.pdf` 保留。

从本目录运行两遍：

```powershell
& 'D:/texlive/2026/bin/windows/xelatex.exe' -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
```

图件位于项目根的 `figures/npu2025-r2/`，编译时需保留相对目录结构。已绑定求解基线005和派生分析001，见bindings.json；质量自审见 `reports/PAPER_QUALITY_REVIEW.md`。

本文采用阅读版行距、无参赛身份的研究封面，不能直接当作正式比赛提交稿。源码可以直接修改；不要在手工修改后执行稿件初始化脚本write_npu_revision2.py，否则该脚本会重新生成它负责的第二版源文件。
