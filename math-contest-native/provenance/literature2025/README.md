# 原始方法文献核验（2026-09-21）

仅核验下列与正文实际论断有关的范围；不声称全文精读。来源为论文原文，转载站点不作为独立方法论证。

| 引文 | 原文来源与读取范围 | 支持内容与引用边界 |
|---|---|---|
| Wilson 等，1995，Dynamic Storage Allocation | https://users.cs.northwestern.edu/~pdinda/ics-s14/doc/dsa.pdf ，已保存 storage.pdf；原文第 1、8、30 页（电子 PDF） | 外部碎片与最佳适配是不同层次的存储分配问题；不支持最佳适配全局最优。下载版首页说明与会议出版版仅有排版、勘误等细微差别；参考文献列出版版。 |
| Bélády，1966，IBM Systems Journal 5(2):78–101 | https://www.yumpu.com/en/document/view/28104545/a-study-of-replacement-algorithms-for-a-virtual-storage-computer/8 ，读取原文扫描转写的 Optimal replacement algorithm 段，印刷 p.86；首页 p.78 核题名和刊卷 | 以完整未来引用序列作为离线替换研究基准；不转用等大小分页的最优性到本题。IBM DOI 页面未获取；bitsavers PDF 返回 403，未绕过或声称本地保存全文。 |
| Topcuoglu 等，2002，IEEE TPDS 13(3):260–274 | https://disco.ethz.ch/courses/fs14/seminar/paper/Jochen/4.pdf ，已保存 heft.pdf；首页摘要及调度模型说明 | 向上秩优先和最早完成时间分配思想。本文没有实现 HEFT 的处理器分配、插空与通信平均模型，正文明确区别。 |

HEFT 文件文字映射为 `/C数字` 字形名，读取时转换为相应字符，保留原始提取和 decoded 文本。Wilson 原文抽取存在断字，以网页原 PDF 行文辅助核对。没有照抄文献段落，没有依据这些论文编造本题实验。

题面及适用官方格式、AI 文件另存 `provenance/official2025/`。文内三项方法论断分别位于新版第 6.2、6.3、7.3 节。
