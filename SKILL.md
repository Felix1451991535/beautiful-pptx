---
name: beautiful-pptx
description: >-
  use this when making any PPT/pptx deck (course presentation, speech slides,
  report, defense, roadshow) that must look template-site quality and open
  reliably in WPS/PowerPoint/phones: pick a style from the 7-style library, real
  photos, de-AI rules, compatibility pipeline, page-by-page render checks
---
# 做精美、能打开的 PPT（v3）

所有路径相对本仓库根目录（下文记作 `$SKILL_DIR`，即本 SKILL.md 所在目录）。在仓库根目录运行命令，或把相对路径前面加上 `$SKILL_DIR/`。

## 0. 兼容性铁律（最高优先级，先读）
很多人用 WPS（电脑和手机）打开。python-pptx 直出的文件即使严格校验 0 错误，WPS 也可能报“文档已被其它应用程序锁定/无法读取”；同一文件经 LibreOffice 重存后能打开。所以：
1. 只用 python-pptx / python-docx 标准 API。不手写注入 XML：不要 Morph、不要手写进入动画（p:timing）、不要 p:bg 背景填充（背景用最底层整页图片）、不要改主题/母版 XML、不要 docx 段落底纹/边框/表头重复。唯一允许的手写 XML 是基础 `<p:transition spd="med"><p:fade/></p:transition>`（放在 clrMapOvr 之后）。
2. 图片：照片 = baseline（非渐进式）RGB JPG；透明素材 = 8bit RGBA PNG（不用调色板 PNG）。pptx 控制在 10MB 内。
3. 最后一步 LibreOffice 重存：pptx 用 `soffice --headless --convert-to pptx:"Impress MS PowerPoint 2007 XML" --outdir conv in.pptx`；docx 用 `--convert-to docx:"MS Word 2007 XML"`，重存后跑 `python3 scripts/fix_lo_docx.py 重存.docx 原始.docx` 补回 styles.xml 里丢失的 w:val。
4. 渲染图、缩略图、PDF 一律用重存后的文件出。
5. `scripts/oxv.sh 文件…`（Open XML SDK 严格校验）全部 0 errors 才交付。一键流水线：`scripts/make_final.sh deck.pptx out/final`。
6. 同时附 PDF 版方便手机看。对方说打不开时，先发一个纯 python-pptx 的最小测试文件区分“文件问题”还是“传输问题”；WPS 报“锁定”也可能是残留的后台 WPS 进程。

## 1. 选风格（不要每次同一种）
风格库 7 套，说明书在 `styles/<id>/STYLE.md`，总表 `styles/STYLES.md`。先问：在哪讲、给谁看、什么情绪。
| 场景 | id |
|---|---|
| 轻松/生活/学生/英语演讲/情绪成长 | `scrapbook` 手账拼贴 |
| 文化/叙事/需要阅读/拿不准时 | `editorial` 杂志留白 |
| 暗场大屏/产品发布/科技 | `aurora` 深色极光 |
| 亮场/互联网/年度回顾/轻数据 | `glass` 通透玻璃 |
| 社区活动/工作坊/艺术节/年轻向 | `riso` 复古孔版 |
| 茶/器物/诗词/禅意/少字 | `japanese` 日式留白 |
| 互联网+/挑战杯路演/答辩要气势 | `guosai` 国赛金奖风 |
同一人连续几份 PPT 尽量换不同风格，除非用户指定。

调用：`sys.path.insert(0, "scripts/styles"); import styles_registry as R; S = R.get_style("<id>"); prs = S.new()`，按内容挑版式函数，最后 `common.finish(...)` 与 `common.validate(...)`。手账风更细的素材生成器见 `examples/scrapbook-assets/scrap_assets.py`（拍立得、胶带、撕纸、便利贴、圆贴纸、票根、手绘涂鸦）。

## 2. 去 AI 味
- 不要：每页“小标签 + 大标题 + 3 张卡片 + 编号圆”、科技蓝、心电线/几何装饰、卡片墙、渐变字、每页长得一样。
- 要：版式随内容换（满版照片/半版/拼贴/大字引语/排版对比/链条图），同一版式不连续出现；每页一个绝对主角，大小对比明显；大量留白；一套只一个强调色；元素不对称。
- 页上只放关键词（英文 ≤25 词），讲稿进备注；标题写成短句，只读标题能听懂结构。
- 封底：一句能带走的话 + Thank you。

## 3. 照片
- 只用真实照片（Pexels 免费可商用），不用 AI 生成图；装饰纹理一律程序生成。
- 先定槽位方向再找图；风格库示例照片用 `python3 scripts/fetch_photos.py` 按 `styles/assets/SOURCES.md` 下载：WebSearch `pexels photo <场景>` （或在 pexels.com 搜索）拿 ID → 下缩略图拼接触表看 → 下 w=2400 原图。来源记 `SOURCES.md`，作者名拿不到就署 `Photo · Pexels`。
- 同一 deck 统一调色（各风格 STYLE.md 有 grade 参数），渐变压暗直接画进图片，不依赖半透明形状。

## 4. 字体
只用 Windows 自带：Georgia、Segoe UI、Ink Free、Segoe Print、微软雅黑、宋体等；华文行楷等 Office 字体须注明并给楷体回退。本机预览用近似字体（映射在 `scripts/fonts.conf`、`scripts/styles/fonts.conf`），标题手动断行、文本框留 ≥10% 余量。

## 5. 演讲类 PPT
- 讲稿用 `▶N` 标记翻页，自动写进备注和演讲稿（“▶ 翻到第 N 页”）。换人时下一位开口就翻到自己的章节页。
- 时长：按每分钟 125–135 词估；3 分钟 ≈ 360–380 词，2 分半 ≈ 320–330 词。四级难度、具体生活例子。
- 交付：PPT + PPT 的 PDF + 总稿 + 每人 1 页个人稿 + 每人翻页指引（页码/缩略图/关键词/翻页句/要点）。

## 6. 交付前检查
1. `python3 scripts/check.py deck.pptx` 无问题（溢出/越界/<10pt）。
2. 重存后渲染逐页 Read PNG：文字截断、压脸、孤字换行、浅字压浅图、便签挡说明、拥挤。Read 会缓存同名图片，复查时换文件名。
3. oxv 0 errors；交付时说明预览字体与 Windows 的差异、照片来源、占位符（如讲者名字）。
4. 交付文件名用对方要的正式名称；同时给 PPTX 和 PDF。
