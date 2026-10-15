#!/usr/bin/env python3
"""修复 LibreOffice 重存 docx 的已知缺陷：styles.xml 里带 themeShade/themeTint 的 <w:color> 丢了必填属性 w:val
（Open XML SDK 报 "The required attribute 'val' is missing"）。
用法：fix_lo_docx.py <LibreOffice 重存后的.docx> [原始 python-docx 生成的.docx]
有原始文件时按 (themeColor, shade, tint) 从原文件取回原来的 val；没有就补 w:val="auto"（schema 合法，Word 以 themeColor 为准）。
只改这一个属性，其他 zip 成员原样字节拷贝、顺序不变。"""
import re, sys, zipfile, shutil, os

def key(attrs):
    g = lambda n: (re.search(r'w:%s="([^"]*)"' % n, attrs) or [None, ""])[1].lower()
    return (g("themeColor"), g("themeShade"), g("themeTint"))

def main(dst, orig=None):
    table = {}
    if orig:
        with zipfile.ZipFile(orig) as z:
            for a in re.findall(r'<w:color ([^>]*?)/?>', z.read("word/styles.xml").decode("utf8")):
                v = re.search(r'w:val="([^"]*)"', a)
                if v: table.setdefault(key(a), v.group(1))
    tmp = dst + ".tmp"; n = 0
    with zipfile.ZipFile(dst) as zin, zipfile.ZipFile(tmp, "w") as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == "word/styles.xml":
                s = data.decode("utf8")
                def fix(m):
                    nonlocal n
                    a = m.group(1)
                    if 'w:val=' in a: return m.group(0)
                    n += 1
                    return '<w:color w:val="%s" %s/>' % (table.get(key(a), "auto"), a.rstrip("/ ").strip())
                s = re.sub(r'<w:color ([^>]*?)/>', fix, s)
                data = s.encode("utf8")
            zout.writestr(info, data, compress_type=info.compress_type)
    shutil.move(tmp, dst)
    print("%s: 补回 %d 个 w:color/@w:val" % (os.path.basename(dst), n))

if __name__ == "__main__":
    main(*sys.argv[1:3])
