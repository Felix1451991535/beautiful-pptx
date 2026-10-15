# 手账拼贴 / Scrapbook

## 风格ID
`scrapbook` · 代码 `scripts/styles/scrapbook.py` · 示例 `styles/scrapbook/20261004-风格-手账拼贴.pptx`（7 页）· 总览 `styles/scrapbook/总览.png`

## 风格描述
- 一张摊平的旧皱纸上，随手贴着几张拍立得真实照片，用半透明纸胶带固定，旁边是手写的砖红大字和几行小字批注。
- 每页都"歪一点"：照片、纸片、标题各有 −8°～+8° 的小角度，彼此可以压叠；没有任何对齐网格感。
- 参考：`refs/canva-scrapbook-portfolio-01.png`（米色皱纸、巨大砖红手写词、倾斜拍立得、牛皮胶带、横格纸片、红色小号大写署名）。

## 适用主题
生活方式、旅行/活动回顾、个人作品集、读书分享、英语演讲、班会、社团招新、轻松的情绪/成长话题、毕业纪念。
**不适用**：严肃的财务/学术答辩、数据密集型汇报（超过 1 张图表就换 Editorial 或 Glass）。

## 设计令牌（配色）
| 角色 | HEX | 用在哪 |
|---|---|---|
| 纸底 | `#EBE0CA` | 皱纸纹理的基色（`paper_crumpled(base=...)`） |
| 砖红（唯一强调色） | `#B3261E` | 手写大标题、手绘下划线、角落小号大写署名、票根虚线框 |
| 墨色 | `#2E2622` | 手写副标题、拍立得题字、手绘箭头 |
| 正文 | `#3B302A` | Georgia 正文 |
| 弱化 | `#5F5346` | 次要说明（米色上 ≥4.5:1） |
| 拍立得白 | `#FBFAF5` | 拍立得相框（不是纯白） |
| 胶带 | `#D9C393` @74% | 半透明牛皮胶带；条纹款 `#E9C7B5`/`#D99A8A` |
| 牛皮纸 | `#C8A57A` | 日期标签、便签纸片 |
| 蓝墨水 | `#5B7BA6` | 只用于横格纸上的一行"钢笔字"批注，全 deck ≤ 2 处 |

**强调色规则**：砖红只给"手写的字"和极少量小号署名；照片之外，一页上砖红面积 ≤ 15%。不要把砖红做成色块底。

## 字体（全部 Windows 自带）
| 用途 | 西文 | 中文 | 说明 |
|---|---|---|---|
| 手写标题/题字 | **Ink Free**（Win10 1803+ 自带） | **楷体**（KaiTi，中文版 Windows 自带；英文版需装"简体中文补充字体"） | 有 Office 可把中文换成 华文行楷（Office 自带，Windows 本身不带） |
| 正文 | **Georgia** | 楷体 | 正文必须读得清，不要用手写体写大段文字 |
| 署名/角标 | **Franklin Gothic Medium** | 微软雅黑 | 全大写 + 字距 120 |
| 票根/打字机 | **Courier New** | 仿宋 | 只用于票根、日期标签 |

预览替代（仅本机 LibreOffice 渲染用，见 `scripts/styles/fonts.conf`）：Ink Free→Kalam（加粗）、Franklin Gothic→Libre Franklin、Courier New→Courier Prime、楷体→Ma Shan Zheng。Ink Free 没有粗体，PowerPoint 会做"仿粗"，实际笔画比预览略细、字面略宽，标题框已按保守估算留余量。

## 字号阶梯（pt）
mega 140（封面单词）｜title 54–60（页标题）｜h2 40–44｜hand 24–34（手写批注）｜caption 20（拍立得题字）｜body 16–18（Georgia）｜tag 11（署名）

## 照片调色参数
`grade(name, w, h, sat=0.86, contrast=0.96, lift=16, warm=7, grain=4.0)` —— 胶片感：降饱和 14%、抬黑位 16、偏暖、细颗粒。
选图：生活抓拍（人、野餐、街道、咖啡、旧物）；自然光；避免棚拍、强商业感、带 logo 的照片。照片一律裁成方形放进拍立得。

## 纹理/装饰素材（程序生成，`scripts/styles/textures.py`）
| 素材 | 函数 | 关键参数 |
|---|---|---|
| 皱纸底 | `paper_crumpled(base="EBE0CA", crease=0.05, stains=0.55, seed=3)` | 脊状分形噪声 + 110 条随机短折痕 → 光照明暗；低频茶渍；边缘泛黄；每页换 seed 避免重复 |
| 纸胶带 | `tape(color="D9C393", alpha=0.74, seed=n)`；条纹款 `stripes=True` | 半透明、两端锯齿撕口、纵向纤维 |
| 横格纸 | `lined_paper()` | 蓝横线 `#9FB6D3` + 红页边线 + 撕口 |
| 牛皮纸/白卡纸片 | `kraft(base="C8A57A")` / `kraft(base="F7F3EA", seed=7)` | 撕边 + 纤维噪点 |
| 拍立得 | `polaroid(slide, photo, cx, cy, w, rot, caption, tape="top"/"corners")` | PPT 原生：白框矩形+外阴影+照片+题字，全部可编辑；按旋转角精确计算子元素位置 |
| 手绘箭头/下划线 | `arrow(slide, pts)` / `scribble_line(slide, x, y, w)` | 自由曲线 + 随机抖动 |

## 版式系统（函数 → 构图 → 字数上限）
| 函数 | 构图 | 字数上限 |
|---|---|---|
| `cover(prs, title, kicker, photos[2])` | 横跨全页的手写单词（−3°）+ 左上/右下两张拍立得 + 一张横格纸垫底 + 角落红色署名 | 标题 1 个英文词 ≤ 10 字母 / 中文 ≤ 4 字；kicker ≤ 4 词 |
| `story(prs, heading, paras, photo)` | 左大拍立得（四角胶带）+ 右手写标题 + 下划线 + Georgia 正文 + 手绘箭头 + 牛皮日期签 | 标题 ≤ 3 词；正文 ≤ 45 英文词 / 90 汉字 |
| `collage(prs, heading, items[3])` | 3 张拍立得错落压叠，各带手写题字 | 题字 ≤ 3 词 / 8 汉字 |
| `note_quote(prs, quote, who, photo)` | 倾斜横格纸 + 条纹胶带 + 手写引语 + 右侧小拍立得 | 引语 ≤ 18 英文词 / 36 汉字 |
| `big_number(prs, number, label, line, photo)` | 260pt 手写数字 + 手写标签 + 拍立得 + 虚线票根 | 数字 ≤ 3 字符 |
| `three_notes(prs, heading, notes[3])` | 牛皮/横格/白卡三张不同纸片，大小高低都不同，各带胶带 | 每张：小标题 ≤ 2 词，正文 ≤ 15 词 / 30 汉字 |
| `closing(prs, title, line, photo)` | 两行手写大字 + 下划线 + 大拍立得 | 标题 ≤ 3 词 |

## 禁止项
- 不要把三张纸片排成等宽等距一行（会变回"卡片阵"）；角度、尺寸、高度至少两项不同。
- 不要编号圆、图标阵、科技蓝、渐变按钮、圆角卡片阴影。
- 不要用手写体写正文段落；手写只给标题、题字、≤ 1 行批注。
- 不要一页超过 3 张照片；不要用 AI 生成的"手账素材图"。
- 胶带不要盖住人脸；拍立得旋转不超过 ±9°。

## 调用示例
```python
import sys; sys.path.insert(0, "scripts/styles")
import scrapbook as S
prs = S.new()
S.cover(prs, "adventures", "a year of small", ["scrap_picnic", "scrap_coffee"])   # 照片名=styles/assets/raw/<名>.jpg，也可传绝对路径
s = S.story(prs, "how it started", "One rainy Sunday…", "scrap_photos")
S.polaroid(s, "/path/my.jpg", 11.0, 2.0, 2.2, rot=6)        # 任意追加元素
from common import finish; finish(prs, "out.pptx", "标题", "副标题")   # 保存+渲染+总览
```

## 与参考图对比 / 已知局限
- 已对齐参考：米色皱纸、巨大砖红手写词压在照片和纸片上、倾斜拍立得 + 牛皮胶带、横格纸片、红色小号大写署名。
- 未做：参考图里"抠图人像"（需要抠图素材，本库不用 AI 抠图；可自行放透明 PNG 人像到横格纸上）。
- Ink Free 是"马克笔手写"而非参考图那种粗刷字；想要更粗可把标题字体换成 Segoe Print 加粗（同为 Windows 自带）。
- 皱纸/胶带是图片，颜色改动需重新调用生成函数（参数见上表）。
