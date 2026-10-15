#!/usr/bin/env python3
"""最小示例（无需照片）：用 japanese 风格做 3 页 deck → out/sample.pptx
Run from repo root:  python3 examples/sample_deck.py && scripts/make_final.sh out/sample.pptx out/final"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts", "styles"))
import styles_registry as R

S = R.get_style("japanese")
prs = S.new()

s = S.page(prs)
S.vtext(s, 9.6, 1.0, 1.4, 5.4, "一期一会")
S.htext(s, 1.2, 5.6, 6.5, 0.8, "A tiny sample deck · 小样例", size=20)
S.seal_mark(s, 11.6, 6.3)

s = S.page(prs)
S.latin(s, 1.2, 1.0, 6, "Chapter one")
S.htext(s, 1.2, 1.6, 8.0, 1.2, "留白，是给观众思考的空间。", size=36, font=S.F_TITLE)
S.hair(s, 1.2, 3.1, 4.2, 3.1)
S.htext(s, 1.2, 3.4, 8.0, 1.6, "每页只放一个主角。\nOne idea per slide.", size=20)
S.red_dot(s, 11.8, 1.2)

s = S.page(prs)
S.htext(s, 1.2, 2.8, 10.9, 1.2, "Thank you", size=48, font=S.F_TITLE, align="c")

os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
out = os.path.join(ROOT, "out", "sample.pptx")
from common import fit_boxes
fit_boxes(prs)   # 自动扩框留余量
prs.save(out); print(out)
