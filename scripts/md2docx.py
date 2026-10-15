# -*- coding: utf-8 -*-
"""极简 Markdown -> docx（标题/段落/列表/表格/**粗体**/`代码`），中文字体正确设置
用法: python3 md2docx.py in.md out.docx"""
import re, sys
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT

EA, LAT = "微软雅黑", "Segoe UI"
INK, PRI = RGBColor(0x10, 0x2A, 0x43), RGBColor(0x0F, 0x4C, 0x81)


def set_font(run, size=None, bold=None, color=None, mono=False):
    run.font.name = "Consolas" if mono else LAT
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = rpr.makeelement(qn("w:rFonts"), {}); rpr.insert(0, rf)
    rf.set(qn("w:eastAsia"), EA); rf.set(qn("w:ascii"), "Consolas" if mono else LAT); rf.set(qn("w:hAnsi"), "Consolas" if mono else LAT)
    if size: run.font.size = Pt(size)
    if bold is not None: run.font.bold = bold
    if color is not None: run.font.color.rgb = color


def add_inline(p, text, size=10.5, color=None, bold=False):
    for part in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text):
        if not part: continue
        if part.startswith("**"):
            set_font(p.add_run(part[2:-2]), size, True, color)
        elif part.startswith("`"):
            set_font(p.add_run(part[1:-1]), size - 1, bold, RGBColor(0x00, 0x7A, 0x7A), mono=True)
        else:
            set_font(p.add_run(part), size, bold, color)


def shade(cell, hexcolor):
    tcPr = cell._element.get_or_add_tcPr()
    shd = tcPr.makeelement(qn("w:shd"), {qn("w:val"): "clear", qn("w:color"): "auto", qn("w:fill"): hexcolor})
    tcPr.append(shd)


def convert(src, out):
    doc = Document()
    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = Cm(2.2); sec.top_margin = sec.bottom_margin = Cm(2.0)
    st = doc.styles["Normal"]; st.font.name = LAT; st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), EA)
    lines = open(src, encoding="utf-8").read().splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip(): i += 1; continue
        m = re.match(r"^(#{1,3})\s+(.*)", ln)
        if m:
            lvl = len(m.group(1)); p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14 if lvl > 1 else 0); p.paragraph_format.space_after = Pt(6)
            add_inline(p, m.group(2), {1: 20, 2: 14, 3: 12}[lvl], INK if lvl == 1 else PRI, True)
            i += 1; continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.match(r"^:?-+:?$", c) for c in cells): rows.append(cells)
                i += 1
            t = doc.add_table(rows=len(rows), cols=len(rows[0])); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    cell = t.cell(r, c); cell.text = ""
                    p = cell.paragraphs[0]
                    hexm = re.match(r"^#([0-9A-Fa-f]{6})$", val)
                    add_inline(p, val, 9, RGBColor(0xFF, 0xFF, 0xFF) if r == 0 else None, r == 0)
                    if r == 0: shade(cell, "0F4C81")
                    elif hexm:
                        shade(cell, hexm.group(1))
                        h = hexm.group(1); lum = (int(h[0:2], 16) * 299 + int(h[2:4], 16) * 587 + int(h[4:6], 16) * 114) / 1000
                        for rr in p.runs: rr.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF) if lum < 140 else INK
            doc.add_paragraph()
            continue
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)", ln)
        if m:
            style = "List Number" if m.group(2)[0].isdigit() else "List Bullet"
            p = doc.add_paragraph(style=style); p.paragraph_format.space_after = Pt(3)
            add_inline(p, m.group(3)); i += 1; continue
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(6); p.paragraph_format.line_spacing = 1.3
        add_inline(p, ln); i += 1
    doc.save(out)
    return out


if __name__ == "__main__":
    print(convert(sys.argv[1], sys.argv[2]))
