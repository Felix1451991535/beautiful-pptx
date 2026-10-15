# 杂志留白 / Editorial（Kami）

## 风格ID
`editorial` · 代码 `scripts/styles/editorial.py` · 示例 `styles/editorial/20261004-风格-杂志留白.pptx`（8 页）· 总览 `styles/editorial/总览.png`

## 风格描述
- 像一本印在暖色纸上的文化杂志：大号衬线标题、细线分隔、宽页边、照片出血，只有一种彩色（墨蓝）。
- 层级只靠"字号 + 留白 + 墨蓝"，不靠加粗、色块、卡片阴影。来源规则：Kami `design.md`（parchment `#f5f4ed`、ink-blue `#1B365D`、serif carries hierarchy、no cool grays、no hard shadows）。

## 适用主题
品牌故事、读书/文化讲座、研究报告的叙事版、咨询提案、个人随笔式分享、展览导览、年度信（Founder letter）。
**不适用**：需要强烈情绪和热闹氛围的活动（换 Scrapbook / Riso）；暗场大屏发布（换 Aurora）。

## 设计令牌（配色）
| 角色 | HEX | 用在哪 |
|---|---|---|
| 羊皮纸底 | `#F5F4ED` | 所有页背景（禁止纯白） |
| 象牙 | `#FAF9F5` | 极少数需要"纸上再垫一层"的地方 |
| 墨黑 | `#141413` | 大标题 |
| 正文 | `#3D3D3A` | 正文 |
| 橄榄灰 | `#504E49` | 导语/副标题 |
| 石灰 | `#6B6A64` | 页眉、日期、图注、来源 |
| 细线 | `#D9D6CA` | 0.75pt 分隔线 |
| **墨蓝（唯一彩色）** | `#1B365D` | 目录页码数字、大数字、段首小型大写、1.2 英寸短强调线、图表最高项 |
| 可选替换：砖红 | `#A2412B` | `new(accent="brick")`，一个 deck 只能二选一 |

**强调色规则**：一页墨蓝出现 ≤ 2 处；不做墨蓝色块背景；图表只用墨蓝 100% / 35% 两档。

## 字体（Windows 自带）
| 用途 | 西文 | 中文 | 说明 |
|---|---|---|---|
| 标题 + 正文（同一衬线） | **Georgia** | **宋体**（SimSun） | 有 Office 可把中文换 华文中宋（Office 自带，Windows 不带）；宋体 < 14pt 投影会发虚，正文中文建议 ≥ 16pt |
| 页眉/栏目名 | **Segoe UI** | 微软雅黑 | 只用于 10pt 全大写 + 字距 200 的极小标签 |

Kami 规则：衬线不加粗；斜体只在引语里用。预览替代：Georgia→Gelasio（与 Georgia 等宽度度量，排版宽度可信）、宋体→Noto Serif CJK SC。

## 字号阶梯（pt）
display 88（封面）｜h1 40–44｜h2 26–28｜lead 18–22（导语）｜body 16｜caption 12｜meta 10（页眉，全大写）

## 照片调色参数
`grade(name, w, h, sat=0.82, contrast=0.97, lift=10, warm=5, grain=2.0)` —— 柔和、暖、微褪色。
选图：静物、窗光、人物侧影、书页、器物；画面干净、主体偏一侧（给标题留位）；照片要么出血（半页/满页），要么放在栏宽内，不加边框、不加圆角、不加阴影。

## 纹理/装饰
无纹理（Kami 要"纸感"靠颜色而非纹理）。装饰只有：0.75pt 细线 `rule()`、1.25pt 墨蓝短线（1.2 英寸）、页眉 `page(prs, running, num)`。

## 版式系统（函数 → 构图 → 字数上限）
| 函数 | 构图 | 字数上限 |
|---|---|---|
| `cover(prs, title, issue, deck_line, img)` | 左 62% 文字（期号/大标题/短线/导语），右 38% 竖照片出血 | 标题 ≤ 4 英文词 / 10 汉字，导语 ≤ 14 词 / 28 汉字 |
| `contents(prs, heading, items[3–4])` | 左大标题，右侧"墨蓝页码 + 标题 + 一句话"，细线分隔（不是编号圆） | 每项标题 ≤ 6 词 / 14 汉字，说明 ≤ 10 词 / 20 汉字 |
| `essay(prs, headline, dek, cols[2], img, caption)` | 标题 + 导语 + 细线 + 两栏正文（段首 4 词墨蓝小型大写）+ 侧栏竖图 | 正文合计 ≤ 110 英文词 / 220 汉字 |
| `full_photo(prs, img, caption, credit)` | 满版照片 + 左下纸色图注条 | 图注 ≤ 14 词 / 28 汉字 |
| `big_number(prs, number, unit_line, body, source)` | 210pt 墨蓝数字 + 细线 + 单位句；右侧解释；来源小字 | 数字 ≤ 5 字符 |
| `bars(prs, heading, rows[≤5], note)` | 极简横条（墨蓝 100%/35%），数值写在条尾 | 每行标签 ≤ 5 词 |
| `pull_quote(prs, quote, who)` | 居中大引语 + 墨蓝短线 + 署名 | ≤ 25 英文词 / 50 汉字 |
| `closing(prs, line, sub, credits, img)` | 左竖照片 + 右结语 + 版权信息 | — |

## 禁止项
- 纯白底、冷灰、科技蓝、渐变、阴影卡片、圆角卡片、图标阵、编号圆。
- 加粗衬线（层级靠字号）；同页两种彩色；一页超过 2 个字号以上的"抢眼元素"。
- 首字下沉（PPT 里无法随文字回绕，换字体后必错位 → 用段首小型大写代替）。

## 调用示例
```python
import sys; sys.path.insert(0, "scripts/styles")
import editorial as E
prs = E.new()                 # 或 E.new(accent="brick")
E.cover(prs, "The Quiet\nHours", "Vol. 03 — On slow mornings", "Notes on…", "edit_window")
E.big_number(prs, "7:40", "the average time…", "Earlier than…", "Reader survey (sample)", "The Quiet Hours", 5)
```

## 与参考对比 / 已知局限
- 对照 Kami 的 `design.md`/`anti-patterns.md` 与 `refs/skills/5-kami/` 示例：色板、单强调色、衬线层级、细线一致；Kami 的 TsangerJinKai 字体非 Windows 自带，已改为 Georgia + 宋体。
- 宋体在高分屏外观偏细；中文正文多的 deck 建议用 Office 的 华文中宋 或改正文为 等线。
