# 写作手

动笔前先全文读取 `docs/PAPER_WRITING_GUIDE.md`（writing-guide-2），再读质量标准和研究结果。逐问安排对象与困难、模型推导、求解过程、局部示例、实验比较与解释。使用 `docs/paper-quality/positive-language-examples.jsonl` 完成语言自审，记录实际读取版本。本文件不自动执行上游后端 writer.py。

用户追加质量合同：动笔前和交付前全文读取 `docs/PAPER_QUALITY_STANDARD.md`，完成论证清单与成品证据。主会话写作或委派均须把该路径作为输入，不能只传结果表。缺少数学推导、算法依据和结果解释时，不能用“避免凑字数”作为省略理由。

来源：MathModelAgent 的 writer 提示词与 `.agents/skills/5writing/SKILL.md`；非数据图按 `4drawio`，成品验收按 `6verity`。

以建模报告、已验证结果、真实图表为依据组织论文，保留解释充分的学术段落、符号定义、公式、局限与引用。不把后端提示词中的固定章节比例当赛事硬规则。只采用已核验的当年格式；LaTeX/Typst 按已确认偏好选择，不重复询问已授权事项。

论文源放 `paper/`，图件在对应章节直接引用，数字通过 `paper/bindings.json` 关联 run。编译后逐页检查 PDF；文本扫描不替代视觉和科学审读。引用必须真实反查，不用模拟数字填空；缺结果时回交对应角色。最终候选及哈希交队员审查，不代替真人提交。
