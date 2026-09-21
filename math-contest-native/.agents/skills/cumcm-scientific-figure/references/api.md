# 可复用绘图 API

运行目录不限；把本项目 `.agents/skills/cumcm-scientific-figure/scripts` 加入当前绘图脚本的 `sys.path` 后使用。默认native_zh_12pt_v1；专项参考回归显式选jfs_zh_reference_v1。数学字体可选cm/stix，但论文中实际匹配验收独立进行：

```python
from scientific_figure import style_context, parametric_curve, export_bundle

with style_context():
    bundle = parametric_curve(
        x, [{"y": y, "label": r"响应 $A/D$", "role": "primary"}],
        xlabel=r"雷诺数 $Re$", ylabel=r"振幅 $A/D$", xscale="log")
    bundle.caption = "填写真实对象、结果与固定参数。"
    result = export_bundle(bundle, output_directory, "response",
                           provenance={"input_file": source_path, "input_sha256": source_hash})
    if result["status"] != "PASS":
        raise RuntimeError(result)
```

所有模板返回 `FigureBundle`；`figure`、`axes` 允许作者显式定制范围/图例，`data_lines` 用于主线样式和图例QA，`secondary_axes` 不计panel，`colorbars`不计panel。自定义主线用 `templates.draw_series` 加入QA；不要跳过数据归属。`style_context`退出恢复调用方rcParams，不在导入时改全局设置。各参数与数据结构见 templates.py 的公开函数签名及 regression.py 可运行调用。

`export_bundle` 在渲染前通过 typography.prepare_text 显式分配混排字形：含中文与公式的标签使用中文正文face，非中文普通片段进入Times正体run，变量进入STIX斜体run。只写字体fallback列表不足以解决Matplotlib mathtext内中文缺字。若在导出前直接显示图，也先在style_context内调用prepare_text(figure)。每个panel的标号在y轴左侧顶部，不高出上框；flow_field的snapshot label只形成独立caption映射，不在右上角渲染。

- time_phase_spectrum：两个等长信号、有限严格递增等间距时间。单边矩形窗周期图，去均值，积分与方差一致；奇偶样本正确处理Nyquist。PSD标签的量纲由调用方按真实输入填写。
- flow_field：四组 `{field,u,v,label}`，二维场形状 `(len(y),len(x))`；x/y均匀网格供streamplot，正负极值共用对称范围；场栅格化，流线/标签矢量。与真实速度场的一致性由数据拥有者核验。
- regime_map：各类 `{x,y,label,role}`；理论x/y及相对上下界band；类别由独立marker表示，不插值成连续概率。
- convergence_validation：共同x、coarse/baseline/refined/reference，label字典四键；可用于网格/时间步/域验证，但真正收敛结论需要独立数值误差证据。
- schematic：正域长宽、圆形物体 `(x,y,r)`、`inlet/length/x/y`标签。只是物理域模板；流程架构编辑仍使用原paper-diagram入口。
- `templates.layout`：1×1/1×2/2×1/2×2/2×3，sharex/sharey按需设置；2×1仍用单栏宽度。该辅助技能不包含自动运行钩子，不调用时不影响任何旧能力。

检查分界：字形路径/字体文件、物理尺寸、线宽、轴、曲线遮挡、panel与导出可自动验收；结论正确性、关键结构遮挡、公式量纲、视觉可读性仍要看最终图。SVG的字形轮廓不需要外部字体，PDF子集嵌入；没有声称SVG是可编辑文字。跨格式误差采用独立MuPDF渲染与PNG的全图平均绝对误差，需结合肉眼检查，不能单凭该数值证明局部无差异。

来源审查：figure-router适合分类但含个人绝对路径；paper-diagram适合可编辑draw.io流程，不提供科学数据模板；nature-figure偏另一套出版流程，未直接套用。实现由专项spec独立编写，不复制第三方正文/图标/字体，不改第三方原件。
