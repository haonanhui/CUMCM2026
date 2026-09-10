# Stage 00 — 赛题入库（Ingest）

输入：官方赛题 PDF/DOCX/TXT + 附件（xlsx/csv/blocks/nets/...）。
目标：把赛题统一为结构化工作目录，供后续阶段只读引用。
出口条件（G1 前件）：manifest.json 生成；全文 md 无乱码；附件全部登记。

## 执行步骤

1. 建目录：`data/contest/<contest>/<题号>/` 下
   - `official/` — 官方文件副本（只读，保留原名）
   - `00_ingest/` — 本次入库产物
2. 提取文本：
   - PDF → `00_ingest/problem.md`（pypdf；中文排版乱码时退回 OCR，标 WARN）
   - DOCX → 追加进 problem.md（python-docx 段落+表格）
   - xlsx/csv → 转 `00_ingest/data/<原表名>.csv`（每个 sheet 独立 csv，写 `00_ingest/data/README.md` 说明列含义，禁止改原始数据）
   - 其他附件（blocks/nets/pl 等）→ 复制到 `00_ingest/data/` 保持原名
3. 跑盘点：
   ```bash
   python code/pipeline/lib/ingest.py --config code/pipeline/config/contest.yaml
   ```
   生成 `00_ingest/manifest.json`：文件清单 + sha256 + 尺寸 + 文本提取状态(PASS/WARN/FAIL)。
4. 自查：读一遍 problem.md，确认题目背景、三问（或 N 问）完整、每问的数据依赖能对上附件。
5. 记录：把题号、附件数、数据表清单写进 `data/contest/<contest>/<题号>/README.md`。

## 注意

- official/ 只读：任何解析/清洗都输出到 00_ingest/，绝不在 official/ 里改文件。
- 大文件（>50MB）先登记尺寸与 hash，不做内容解析（标 UNVERIFIED）。
- 华数杯实测：B 题含 .blocks/.nets/.pl（VLSI 标准格式），C 题含多 xlsx；A 题 xlsx 附件——解析时先人工读列名再定 dtype。
