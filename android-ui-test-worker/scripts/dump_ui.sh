#!/bin/bash
# dump_ui.sh - 导出 UI 树（兼容 MIUI，忽略 stderr）
# 用法: ./dump_ui.sh [输出路径]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:-$SCRIPT_DIR/test_output/ui.xml}"
mkdir -p "$(dirname "$OUT")"
adb shell uiautomator dump --compressed /sdcard/ui.xml 2>/dev/null
adb pull /sdcard/ui.xml "$OUT" 2>/dev/null
echo "✓ UI 树导出到: $OUT"
