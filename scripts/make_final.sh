#!/usr/bin/env bash
# 交付流水线 / delivery pipeline:
#   python-pptx 生成的 deck → LibreOffice 重存 → check.py → 渲染 PNG/PDF → oxv 严格校验
# 用法: scripts/make_final.sh in.pptx [out_dir]      (docx: 同时传入 .docx 也可)
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${2:-out/final}"; T="$(mktemp -d)"; mkdir -p "$OUT"
export FONTCONFIG_FILE="$DIR/scripts/fonts.conf"
IN="$1"; NAME="$(basename "$IN")"; EXT="${NAME##*.}"
PROF="-env:UserInstallation=file://$T/lo_profile"
if [ "$EXT" = "pptx" ]; then
  soffice "$PROF" --headless --convert-to pptx:"Impress MS PowerPoint 2007 XML" --outdir "$T/conv" "$IN" >/dev/null 2>&1
  cp "$T/conv/$NAME" "$OUT/$NAME"
  python3 "$DIR/scripts/check.py" "$OUT/$NAME"
  python3 "$DIR/scripts/render.py" "$OUT/$NAME" "$OUT/render" "$OUT/render/overview.png" | head -1
  cp "$OUT"/render/*.pdf "$OUT/" 2>/dev/null || true
else
  soffice "$PROF" --headless --convert-to docx:"MS Word 2007 XML" --outdir "$T/conv" "$IN" >/dev/null 2>&1
  cp "$T/conv/$NAME" "$OUT/$NAME"
  python3 "$DIR/scripts/fix_lo_docx.py" "$OUT/$NAME" "$IN"
  soffice "$PROF" --headless --convert-to pdf --outdir "$OUT" "$OUT/$NAME" >/dev/null 2>&1
fi
"$DIR/scripts/oxv.sh" "$OUT/$NAME"
rm -rf "$T"
