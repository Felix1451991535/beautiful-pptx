# -*- coding: utf-8 -*-
"""pptkit 风格库注册表。
用法：
    import sys; sys.path.insert(0, "scripts/styles")
    import styles_registry as R      # 或：from styles import get_style（把 lib 加入 sys.path 后）
    S = R.get_style("scrapbook")     # 返回风格模块：S.T 主题、S.new() 新建演示文稿、S.cover()/... 版式函数、S.build_demo(out)
    prs = S.new(); S.cover(prs, ...); prs.save("out.pptx")
"""
import os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

STYLES = {
    "scrapbook": dict(cn="手账拼贴", module="scrapbook", fits="生活方式、旅行/活动回顾、个人作品集、读书分享、英语演讲、班会、轻松的情绪/成长话题"),
    "editorial": dict(cn="杂志留白", module="editorial", fits="品牌故事、读书/文化讲座、研究报告的叙事版、咨询提案、个人随笔式分享"),
    "aurora": dict(cn="深色极光", module="aurora", fits="产品发布、科技/AI 主题演讲、年度战略、活动开场、大屏幕暗场"),
    "glass": dict(cn="通透玻璃", module="glass", fits="年度回顾、互联网产品/运营汇报、App 介绍、轻商务数据页、校园社团招新"),
    "riso": dict(cn="复古孔版", module="riso", fits="社区/公益活动、创意工作坊、音乐/艺术节、文创与独立品牌、年轻向分享会"),
    "japanese": dict(cn="日式留白", module="japanese", fits="茶/器物/美食/生活美学、诗词与文学、禅意品牌、高端简约提案、摄影作品"),
    "guosai": dict(cn="国赛金奖风", module="guosai", fits="互联网+/挑战杯/创青春路演、乡村振兴/智慧农业/科技成果答辩、政务汇报"),
}
ALIASES = {"手账": "scrapbook", "手账拼贴": "scrapbook", "杂志": "editorial", "kami": "editorial", "极光": "aurora",
           "玻璃": "glass", "孔版": "riso", "risograph": "riso", "日式": "japanese", "国赛": "guosai"}


def get_style(name):
    key = ALIASES.get(name, name).lower()
    if key not in STYLES:
        raise KeyError("未知风格 %s，可选：%s" % (name, ", ".join(STYLES)))
    return importlib.import_module(STYLES[key]["module"])


def list_styles():
    return [(k, v["cn"], v["fits"]) for k, v in STYLES.items()]
