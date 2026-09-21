# 科研图技能验收（2026-09-21）

已完成 math-contest-native 原生技能；不依赖 app 投影或 Workbench。最终样例仅以 `yaxis-top-native/` 和 `yaxis-top-jfs/` 为准，其他目录保留迭代证据，不构成当前验收。

## 改动与架构

- `.agents/skills/cumcm-scientific-figure/SKILL.md`：原生使用入口；`references/profile.json` 集中定义字体、线宽、颜色、标记、尺寸和导出规则；`references/api.md` 记录公共接口。
- `scripts/scientific_figure/`：style 管理局部样式与字体，typography 处理中文/Times/数学混排，templates 只接收数据，qa 执行 artist 与文件检查，export 输出文件与证据。样式退出恢复，不污染全局 rcParams。
- `scripts/regression.py` 与 `tests/test_figures.py`：确定性合成回归与 18 项测试；requirements.txt 固定依赖版本。
- docs/SKILLS.md、docs/FIGURES_ZH.md、专项目标 spec、provenance/UPSTREAM.md：路由、原生适配和来源边界。
- 两个 probe 脚本：技能数由目录清单验证，支持新增技能，保留原生入口。
- task、handoff、AI_USAGE.md 和本目录：交付与证据。未改原论文、科学结果、既有技能或 Workbench 功能。

## 样式与图型

默认 native_zh_12pt_v1 保留原生工程成图 12 pt 要求；jfs_zh_reference_v1 提供专项参考字号。中文宋体（具备衬线回退），英文数字 Times New Roman，数学 STIX；真实论文数学字体一致性仍须论文侧确认。支持不同线型、空心/实心标记、红蓝绿主色、灰色参考线和浅蓝区间带。流场色标对称，正负等值线使用不同线型辅助灰度辨认。

子图字母统一位于 y 轴左侧顶部，顶端与上框齐平，不高出上框。禁止外部右上角说明；时间和统一说明写入独立 caption 段。支持 1×1、1×2、2×1、2×2、2×3 布局。

| 回归 | 图型 | 两套配置 |
|---|---|---|
| A | 参数扫描、对数轴、区间带和箭头 | PASS |
| B | 时序、相图、功率谱 2×3 面板 | PASS |
| C | 流场、流线、等值线及共享色标 | PASS |
| D | 模态/状态图 | PASS |
| E | 收敛与验证对比 | PASS |
| F | 双轴频率/幅值 | PASS |
| schematic | 几何、网格与尺寸示意图 | PASS |

全部为合成数据，只验证绘图能力，不构成科研结果。

## 实际验证

- 18 个单元测试通过，见 tests-delivered.txt。覆盖字体与真实字形、非法数据、PSD 奇偶采样能量、布局、标号、图例碰撞、样式恢复、覆盖保护与导出失败路径。
- 两套配置共 14 图自动 QA 全部 PASS。每图交付 PDF、SVG、600 dpi PNG、灰度 PNG、caption.txt 和 QA JSON；PDF/SVG/PNG 均重新打开，检查字体嵌入、中文文本、物理尺寸与跨格式渲染差异。
- 彩色及灰度最终总览经 agent 视觉检查；源清单哈希匹配当前实现，见 visual-review.json。人工审核保留 pending，未冒充人工签字。
- quick_validate：Skill is valid。Codex skills/list 和已安装 DSH filesystem provider list/get 均加载 10 个技能，包含新增技能，错误/警告列表为空；两项均 model turns = 0，不声称已经验证模型自主调用。
- Git diff --check 通过；既有上游技能、paper/results/code 跟踪文件与 HEAD 相同。没有提交或推送。

## 兼容性与限制

新技能为补充入口，未复制或改写第三方技能实现。依赖安装在项目虚拟环境，需可用的 Times New Roman 与中文衬线字体；缺字直接失败。SVG 使用字体轮廓以保持跨机显示，文字不是可编辑 text。PyMuPDF 1.26.4 已装入 native 本地环境。

字体子集工具的可选 MERG 表丢弃提示及依赖弃用提示记为 WARN；最终无缺字错误。最初混排缺字、图例与注释碰撞均已修复并回归。更早标号布局按用户意见淘汰，旧结果保留以追溯。

实际论文嵌入后的尺寸与数学字体匹配为 UNVERIFIED；真实数据的科学有效性、人工审查和正式提交不在本次通过范围。未重新通读参考 PDF。本轮未修改全局项目下一行动。
