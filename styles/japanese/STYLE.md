# 日式留白 / Japanese Minimal

## 风格ID
`japanese` · 代码 `scripts/styles/japanese.py` · 示例 `styles/japanese/20261004-风格-日式留白.pptx`（7 页）· 总览 `styles/japanese/总览.png`

## 风格描述
- 米白和纸上，一列竖排宋体标题，旁边一行更小的竖排副题；画面 85% 是空的。一点印章红（朱印或一个小红点）是全页唯一的颜色。
- 照片低饱和、雾感、偏暖，要么只占一小块，要么占半页，字永远不压在照片上。参考：gpt-image2 `styles/initial/japanese-wabi.md`。

## 适用主题
茶/器物/美食/生活美学、诗词与文学、禅意或手作品牌、高端简约提案、摄影作品集、节气与传统文化（安静的那一类）。
**不适用**：信息量大的汇报（每页字太少）；热闹的活动（换 Scrapbook / Riso）。

## 设计令牌（配色）
| 角色 | HEX | 用在哪 |
|---|---|---|
| 米白和纸 | `#F6F2EA` | 背景（带纤维纹理） |
| 墨 | `#2B2926` | 标题 |
| 正文 | `#3E3A35` | 正文 |
| 灰 | `#6B655C` | 竖排副题、说明、西文小字 |
| 细线 | `#CFC7B8` | 0.6pt 发丝线 |
| **印章红（唯一彩色）** | `#B7282E` | 印章、0.13–0.16 英寸小红点；每页 ≤ 1 处 |

## 字体
| 用途 | 西文 | 中文 | 是否自带 |
|---|---|---|---|
| 标题（竖排/横排） | Georgia | **宋体** SimSun | Windows 自带；有 Office 可换 华文中宋 / 华文宋体（Office 自带，Windows 不带） |
| 正文 | Georgia | **等线** DengXian | 中文版 Windows 10/11 自带（英文版需"可选功能 → Chinese (Simplified) Supplemental Fonts"） |
| 西文小字 | Georgia 全大写 + 字距 400 | — | Windows 自带 |

不要用 Yu Mincho：它属于 Windows 的"日文补充字体"，中文版 Windows 默认没有，且缺简体字形。预览替代：宋体→Noto Serif CJK SC，等线→Noto Sans CJK SC。

## 字号阶梯（pt）
display 60–66（竖排标题）｜数字 150（Georgia）｜h1 36–40（竖排步骤名）｜h2 26–28（一句话）｜body 15–16｜small 12｜meta 10（西文）

## 照片调色参数
`grade(..., sat=0.62, contrast=0.92, bright=1.04, lift=22, warm=6, grain=2.0)` —— 低饱和、抬黑位起雾、偏暖。
选图：器物静物、手部动作、竹林/庭院、留白多的画面；避免高饱和、人物正脸大特写。

## 纹理/装饰素材
| 素材 | 函数 |
|---|---|
| 和纸 | `washi(base="F6F2EA", fibers=260, seed=31)`：极淡云纹 + 亮色纤维丝（5% 暗丝） |
| 印章 | `seal("茶", color="B7282E", style="white")` 白文方印；`seal("一期一会", style="red")` 朱文 4 字（右起竖读）；边缘与印面随机残缺 |
| 小红点 | `red_dot(slide, cx, cy, d=0.16)`（PPT 原生圆，可编辑） |
| 竖排 | `vtext(...)` = 文本框 `vert="eaVert"`，PowerPoint/LibreOffice/WPS 均支持 |

## 版式系统（函数 → 构图 → 字数上限）
| 函数 | 构图 | 字数上限 |
|---|---|---|
| `cover(prs, title, sub, en, img)` | 右侧竖排标题 + 更小竖排副题 + 印章；左下小照片 + 西文小字 | 标题 ≤ 7 汉字，副题 ≤ 10 汉字 |
| `intro(prs, heading, body, img)` | 左 38% 满高照片，右侧横排标题 + 短发丝线 + 正文（行距 1.8） | 正文 ≤ 3 行 × 20 汉字 |
| `one_line(prs, line, en)` | 只有一句话 + 一个红点 | ≤ 16 汉字 |
| `number(prs, num, vlabel, note)` | Georgia 大数字 + 发丝线 + 一句说明；右侧竖排标签 + 红点 | 数字 ≤ 5 字符 |
| `steps(prs, items[3])` | 三列竖排、自右向左阅读，列间竖发丝线（不用编号圆） | 步骤名 2 字，说明 ≤ 12 汉字 |
| `full_photo(prs, img, vline)` | 右 62% 照片，左侧和纸上一列竖排短句 + 红点 | ≤ 10 汉字 |
| `closing(prs, word, en)` | 居中竖排两字 + 朱文印 | — |

## 禁止项
- 一页两处红色；红色大面积色块；渐变、阴影、卡片、图标、编号圆。
- 文字压在照片上；正文超过 4 行；加粗。
- 居中对称的"标题 + 三栏"布局；页面四周塞满装饰（樱花、波浪纹、扇子等符号化元素）。

## 调用示例
```python
import japanese as J
prs = J.new(); J.cover(prs, "一杯茶的时间", "慢下来的二十分钟", "a cup of tea", "jp_cups")
s = J.page(prs); J.vtext(s, 10, 1, 1.2, 5, "竖排标题"); J.seal_mark(s, 10.6, 6.4, chars="静")
```

## 已知局限
- 竖排里的阿拉伯数字/英文会横躺（PowerPoint 的 eaVert 行为）；竖排里尽量用汉字数字。
- 宋体在投影上偏细，标题建议 ≥ 26pt；印章是位图（换字需重新生成）。
