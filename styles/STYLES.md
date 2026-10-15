# pptkit 风格库（7 套可编辑风格预设）

汇总对比图：`styles/20261004-风格库总览.png`。每套都有：风格说明书 `styles/<id>/STYLE.md`、示例 deck `styles/<id>/20261004-风格-*.pptx`、逐页渲染 `styles/<id>/render/`、总览 `styles/<id>/总览.png`。

> 说明：示例 deck、渲染图和总览图不随仓库分发；先 `python3 scripts/fetch_photos.py`，再 `python3 scripts/styles/build_all.py` 即可在本地重新生成。
代码：`scripts/styles/<id>.py`（主题 + 版式函数 + `build_demo`），公共工具 `scripts/styles/common.py`，程序纹理 `scripts/styles/textures.py`，注册表 `scripts/styles/__init__.py`（同内容副本 `styles_registry.py`），一键构建与校验 `scripts/styles/build_all.py`。

## 1. 按主题选风格

| 风格 | id | 一句话 | 最适合 | 别用在 |
|---|---|---|---|---|
| 手账拼贴 | `scrapbook` | 旧皱纸 + 拍立得 + 胶带 + 手写砖红大字 | 生活方式、旅行/活动回顾、作品集、读书分享、英语演讲、班会、情绪/成长话题 | 严肃答辩、数据密集汇报 |
| 杂志留白（Kami） | `editorial` | 暖纸白 + 单一墨蓝 + 大衬线 + 细线 | 品牌故事、文化讲座、叙事型研究报告、咨询提案、随笔分享 | 热闹活动、暗场发布 |
| 深色极光 | `aurora` | 近黑底 + 程序极光 + 发布会大字 | 产品发布、科技/AI 演讲、年度战略、活动开场 | 文字多的内容、亮会议室 |
| 通透玻璃 | `glass` | 柔彩渐变 + 球体 + 磨砂玻璃面板 | 年度回顾、互联网产品/运营汇报、App 介绍、轻商务数据 | 政务/学术答辩 |
| 复古孔版 | `riso` | 粉+蓝两专色 + 网点照片 + 错位套印 | 社区/公益、工作坊、艺术节、文创品牌、年轻向分享 | 正式商务、需真实照片颜色 |
| 日式留白 | `japanese` | 米白和纸 + 竖排宋体 + 印章红 | 茶/器物/美食、诗词文学、禅意品牌、高端简约提案、摄影 | 信息量大的汇报 |
| 国赛金奖风 | `guosai` | 满版照片统一深色调 + 金色书法标题 | 互联网+/挑战杯路演、乡村振兴/智慧农业（深绿）、科技（深蓝）、非遗文化（酒红） | 日常例会、英文场合 |

**快速决策**：先问"在哪讲、给谁看、情绪是什么"——
- 轻松、有人情味、学生/生活 → `scrapbook`（英文演讲、情绪话题首选）；年轻有态度、活动海报感 → `riso`
- 安静、文化、需要阅读 → `editorial`；更东方、更少字 → `japanese`
- 暗场大屏、产品/科技 → `aurora`；亮场、互联网/年度数据 → `glass`
- 比赛路演、领导评审、要"气势" → `guosai`
- 拿不准时：`editorial`（最稳、最不容易出 AI 味）。

## 2. 怎么调用

```python
import sys; sys.path.insert(0, "scripts/styles")
import styles_registry as R
S = R.get_style("scrapbook")          # 也接受中文别名：手账 / 杂志 / 极光 / 玻璃 / 孔版 / 日式 / 国赛
prs = S.new()                          # 主题色与字体写入母版（guosai: S.new("green"|"blue"|"wine")；editorial: S.new(accent="brick")）
S.cover(prs, "adventures", "a year of small", ["scrap_picnic", "scrap_coffee"])  # 照片：raw 目录里的名字或任意绝对路径
...
from common import finish
finish(prs, "out/xxx.pptx", "标题", "副标题")   # 自动扩框留余量 → 保存 → LibreOffice 渲染 → 总览图
from common import validate; print(validate("out/xxx.pptx"))   # check.py + OOXML 校验
```
- 每个版式函数返回 slide，可继续用该风格的原子函数加元素（如 `S.polaroid`、`G.glass_panel`、`Z.riso_text`、`J.vtext`、`A.grad_text`）。
- 公共原子：`common.grade()` 照片调色裁切、`pic()/pic_c()` 放图（出血自动裁切不越界）、`text()` 双字体文字（`font=("Georgia","宋体")`，`vert="eaVert"` 竖排）、`shadow()`、`place()` 旋转坐标换算、`fit_boxes()` 按 check.py 保守估算扩框。
- 重新生成全部示例与校验：`python3 scripts/styles/build_all.py [id ...]`。

## 3. 全库共同的关键规则（防 AI 味）
1. **不要**"每页小标签 + 大标题 + 卡片 + 编号圆"。序号用排版（衬线数字、动词大字、竖排列、手写词），不用圆圈。
2. 一套 deck 只有 **1 个强调色**（孔版是 2 个专色），强调色只给标题/关键数字/极少量线条。
3. **不对称 + 留白**：同一页的元素在大小、角度、高度上至少有两项不同；不要等宽等距三卡片。
4. **真实照片 + 统一调色**：每套风格有固定 `grade()` 参数，一个 deck 所有照片用同一组参数；照片来源记在 `styles/assets/SOURCES.md`。不用 AI 生成图；装饰一律程序生成。
5. **字体只用 Windows 自带**（国赛风的华文行楷为 Office 字体，已注明并提供楷体回退）。预览用开源近似字体，正式效果以 Windows 为准，文本框已按保守估算留余量。
6. 每页一个主信息；正文 ≥ 15pt（注释 ≥ 10pt）。

## 4. 字体可用性速查
| 字体 | 来源 |
|---|---|
| 微软雅黑、宋体、Segoe UI（含 Light/Semibold）、Georgia、Impact、Arial Black、Courier New、Franklin Gothic Medium、Ink Free（Win10 1803+）、Segoe Print/Script、Bahnschrift（Win10 1709+） | Windows 自带 |
| 等线、黑体、楷体、仿宋 | 中文版 Windows 自带；英文版 Windows 需在"设置 → 可选功能"装 Chinese (Simplified) Supplemental Fonts |
| 华文行楷、华文中宋、华文宋体、方正姚体、方正舒体、隶书、幼圆 | 随 Microsoft Office 安装，**Windows 本身不带** |
| Yu Mincho | Windows 日文补充字体（中文版默认没有）→ 本库不用 |

## 5. 已知局限（全库）
- 本机无 Windows 字体：渲染图用 Kalam/Selawik/Gelasio/Anton/Noto CJK/Ma Shan Zheng 等近似字体，字形与 Windows 实际显示不同（Gelasio 与 Georgia 度量兼容，最接近）。
- 纹理、光晕、网点照片、球体、印章是位图：改色/改位置需改参数重新生成（函数与参数写在各 STYLE.md）。
- 玻璃风的磨砂是"预模糊背景 + 精确裁切"模拟，拖动面板后不会实时更新。
- LibreOffice 预览不显示文字渐变（极光风日期页），PowerPoint 正常。
