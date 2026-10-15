#!/usr/bin/env python3
"""Download the free Pexels photos listed in styles/assets/SOURCES.md into styles/assets/raw/.
按 SOURCES.md 下载风格库示例照片（Pexels License，免费可商用）。照片不随仓库分发。"""
import os, re, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "styles", "assets", "SOURCES.md")
RAW = os.path.join(ROOT, "styles", "assets", "raw")
os.makedirs(RAW, exist_ok=True)
URL = "https://images.pexels.com/photos/{0}/pexels-photo-{0}.jpeg?auto=compress&cs=tinysrgb&w=2400"
for name, pid in re.findall(r"^\|\s*([\w.-]+\.jpg)\s*\|\s*\[(\d+)\]", open(SRC, encoding="utf-8").read(), re.M):
    dst = os.path.join(RAW, name)
    if os.path.exists(dst):
        continue
    try:
        req = urllib.request.Request(URL.format(pid), headers={"User-Agent": "Mozilla/5.0"})
        open(dst, "wb").write(urllib.request.urlopen(req, timeout=60).read())
        print("ok  ", name)
    except Exception as e:
        print("FAIL", name, pid, e)
