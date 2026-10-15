# beautiful-pptx

> An agent skill for building template-quality PowerPoint decks with python-pptx that open reliably in WPS / PowerPoint / phones.

一个给 AI 编程助手（Claude Code / Cursor / Codex）用的 **PPT 制作技能**：用 python-pptx 标准 API 做出像模板站一样好看的 16:9 PPT，并通过 LibreOffice 重存 + Open XML SDK 严格校验，保证 WPS（电脑/手机）和 PowerPoint 都能打开。

## 包含什么

| 路径 | 说明 |
|---|---|
| `SKILL.md` | 技能主文件：兼容性铁律、选风格、去 AI 味、照片、字体、演讲类 PPT、交付检查 |
| `styles/` | 7 套风格说明书（`<id>/STYLE.md`）与总表 `STYLES.md`：scrapbook 手账拼贴、editorial 杂志留白、aurora 深色极光、glass 通透玻璃、riso 复古孔版、japanese 日式留白、guosai 路演金奖风 |
| `scripts/styles/` | 风格库代码（`styles_registry.get_style(id)`），纹理全部程序生成 |
| `scripts/pptkit.py` | python-pptx 基础封装 |
| `scripts/check.py` | 检查溢出 / 越界 / 小于 10pt 的字 |
| `scripts/render.py` | 用 LibreOffice 渲染 PDF、逐页 PNG 和总览图 |
| `scripts/make_final.sh` | 一键交付：LibreOffice 重存 → check → 渲染/PDF → 校验 |
| `scripts/oxv.sh` + `tools/oxv/` | Open XML SDK 严格校验器（C# 源码，首次运行自动编译） |
| `scripts/fix_lo_docx.py` | 修补 LibreOffice 重存 docx 后 styles.xml 丢失的 `w:val` |
| `scripts/fetch_photos.py` | 按 `styles/assets/SOURCES.md` 下载风格示例用的 Pexels 免费照片 |
| `examples/sample_deck.py` | 不需要照片的 3 页最小示例 |
| `examples/scrapbook-assets/` | 手账风素材生成器（拍立得、胶带、撕纸、贴纸等） |

照片不随仓库分发（Pexels License 允许免费商用，但不得原样再分发）；需要时运行 `python3 scripts/fetch_photos.py`。

## 依赖

- Python 3.10+：`pip install -r requirements.txt`（python-pptx、python-docx、Pillow、numpy、lxml）
- LibreOffice（`soffice` 命令）：重存、渲染、出 PDF
- poppler-utils（`pdftoppm`、`pdffonts`）：渲染 PNG 与字体检查
- 中文字体：Linux 装 `fonts-noto-cjk`；或设环境变量 `PPTKIT_SANS_FONT` / `PPTKIT_SERIF_FONT` 指向字体文件
- .NET 8 SDK（仅校验器需要）：<https://dotnet.microsoft.com/download>，首次运行 `scripts/oxv.sh` 会自动 `dotnet build`

```bash
# Ubuntu / Debian 示例
sudo apt install libreoffice poppler-utils fonts-noto-cjk
pip install -r requirements.txt
# .NET 8: https://learn.microsoft.com/dotnet/core/install/linux
```

## 安装到 AI 助手

先 `git clone` 本仓库（或下载解压），然后：

- **Claude Code**：把整个文件夹放到 `~/.claude/skills/beautiful-pptx/`（项目内用则放 `.claude/skills/beautiful-pptx/`）。
  ```bash
  git clone <repo-url> ~/.claude/skills/beautiful-pptx
  ```
- **Cursor**：放到项目的 `.cursor/skills/beautiful-pptx/`（或全局 `~/.cursor/skills/`）；旧版本可在 `.cursor/rules/` 新建规则，内容引用 `SKILL.md`。
- **Codex CLI**：放到 `~/.codex/skills/beautiful-pptx/`；或在项目 `AGENTS.md` 里写一句“做 PPT 时先读 `<路径>/beautiful-pptx/SKILL.md` 并照做”。

装好后直接说“帮我做一份 xx 主题的 PPT”，助手会按 `SKILL.md` 选风格、生成、校验。

## 手动使用

在仓库根目录：

```bash
python3 examples/sample_deck.py                    # 生成 out/sample.pptx
scripts/make_final.sh out/sample.pptx out/final    # 重存 + 检查 + PDF + 校验
```

在自己的脚本里：

```python
import sys; sys.path.insert(0, "scripts/styles")
import styles_registry as R
S = R.get_style("scrapbook")        # 7 选 1
prs = S.new()
# ……调用该风格的版式函数，见 styles/<id>/STYLE.md
prs.save("out/my.pptx")
```

需要照片的风格 demo（如 `python3 scripts/styles/build_all.py`）请先运行 `python3 scripts/fetch_photos.py`。

## 许可

代码与文档：MIT License，见 `LICENSE`。照片版权归各自的 Pexels 作者，见 `styles/assets/SOURCES.md`。
