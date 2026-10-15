# 复古孔版 / Risograph

## 风格ID
`riso` · 代码 `scripts/styles/riso.py` · 示例 `styles/riso/20261004-风格-复古孔版.pptx`（7 页）· 总览 `styles/riso/总览.png`

## 风格描述
- 像社区小报（zine）：米色纸上只有两种专色油墨——荧光粉和孔版蓝；照片被分色成两版网点，粉版故意没对准；粗体大字也是"粉色底版 + 蓝色半透明压印"的错位套印，叠色处发紫。
- 最上层盖一层油墨颗粒/灰尘，纸面有纤维。参考：gpt-image2 `styles/initial/risograph.md`。

## 适用主题
社区/公益活动、创意工作坊、音乐/艺术节、文创与独立品牌、读书会、年轻向分享会、校园活动海报式 PPT。
**不适用**：正式商务/学术汇报、需要准确还原照片颜色的内容（照片会被双色化）。

## 设计令牌（配色）
| 角色 | HEX | 用在哪 |
|---|---|---|
| 纸色 | `#F2EDE1` | 背景（带极淡纤维） |
| **孔版蓝** `Riso Blue` | `#0078BF` | 主文字色（代替黑色）、照片暗部网点、压印层 |
| **荧光粉** `Fluorescent Pink` | `#FF48B0` | 套印底版、照片中间调网点、错位色块、强调 |
| 深蓝（小字） | `#1D3F6E` | 打字机正文（可读性） |
| 可选第三色：黄 | `#FFE800` | 全 deck ≤ 2 处小色块 |

**强调色规则**：全页只有纸色 + 两专色（+可选黄）；不出现黑、灰、其他颜色。叠色靠半透明（蓝 88% 压在粉上）。

## 字体（Windows 自带）
| 用途 | 西文 | 中文 |
|---|---|---|
| 大标题 | **Impact**（备选 Arial Black） | **黑体**（加粗） |
| 正文 | **Courier New**（打字机） | **仿宋**（或 等线） |

预览替代：Impact→Anton、Arial Black→Archivo Black、Courier New→Courier Prime、黑体→Noto Sans CJK。Impact 是窄体，换成中文黑体时字面会变宽，中文标题字号需降 25%。

## 字号阶梯（pt）
mega 128–150（封面）｜数字 230｜display 110–130（动词/口号）｜h1 54–64｜lead 22–24｜body 16–18｜meta 12–14

## 照片调色（双色网点）
`riso_duotone(src, w, h, c1="FF48B0", c2="0078BF", paper="F2EDE1", cell=9, offset=(7,-5), k1=0.85, gamma2=1.3)`
- 粉版管中间调（15° 网角），蓝版管暗部（75° 网角），粉版错位 offset 像素，正片叠底到纸色；油墨浓度加低频噪声模拟不匀。
- `halftone()` 可在照片下垫一块错位的粉色实地。选图：高反差、主体清楚、背景简单的照片（人物动作、蔬果、工具）。

## 纹理/装饰素材
| 素材 | 函数 |
|---|---|
| 纸 | `washi(base="F2EDE1", fibers=45)` |
| 颗粒/灰尘层 | `grain_overlay(dark="1D3F6E", density=0.006, alpha=0.35)`（每页最后调用 `grain_on`） |
| 网点色块 | `halftone_blob(color, size, cell)` |
| 套印字 | `riso_text(slide, x, y, w, h, text, under=粉, over=蓝, mis=(0.06, 0.035))` |

## 版式系统（函数 → 构图 → 字数上限）
| 函数 | 构图 | 字数上限 |
|---|---|---|
| `cover(prs, title, img, meta)` | 左两行套印大字 + 粉色粗线 + 打字机 meta；右网点照片带错位粉块 | 标题 2 行 × ≤ 8 字母 / 4 汉字 |
| `intro(prs, heading, body, img)` | 左半满高网点照片，右套印标题 + 打字机正文 | 正文 ≤ 40 英文词 / 80 汉字 |
| `big_number(prs, number, line, note)` | 超大套印数字（蓝底粉压）+ 粉色网点圆 | 数字 ≤ 6 字符 |
| `verbs(prs, items[3])` | 三个动词大字竖向堆叠、颜色交替，右侧一句说明，点线分隔（不用编号） | 动词 ≤ 6 字母 / 3 汉字；说明 ≤ 12 词 |
| `full_halftone(prs, img, word)` | 满版网点照片 + 纸色底条上的套印口号 | ≤ 10 字母 |
| `quote(prs, q, who)` | 粉色大引号 + 打字机粗体引语 + 蓝色网点圆 | ≤ 22 英文词 / 44 汉字 |
| `closing(prs, title, info, img)` | 套印口号 + 黄色小方块 + 时间地点；右侧网点照片条 | info ≤ 3 行 |

## 禁止项
- 彩色原片（必须双色网点化）；渐变、阴影、圆角卡片、玻璃效果、图标阵、编号圆。
- 第三种以上颜色；黑色文字；细体字做标题。
- 套印偏移 > 0.1 英寸（会像重影 bug）；颗粒层 alpha > 0.5（脏）。

## 调用示例
```python
import riso as Z
prs = Z.new(); Z.cover(prs, "GROW\nTOGETHER", "riso_harvest", "ROOFTOP GARDEN CLUB")
s = Z.page(prs); Z.riso_text(s, 1, 1, 8, 2, "HELLO", size=120); Z.grain_on(s)
```

## 已知局限
- 套印字是两个文本框叠在一起：改文字要两个都改（或删掉 under 层再复制 over 层）。
- 半透明文字在 PowerPoint、LibreOffice 都能显示；WPS 旧版可能不显示透明度（叠色变为纯蓝）。
- 网点照片是位图，换照片需重新调用 `riso_duotone`。
