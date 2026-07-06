#!/bin/bash
# screenshot.sh - 截图到指定路径
# 用法: ./screenshot.sh [输出路径]

OUT="${1:-./screenshot.png}"
adb exec-out screencap -p > "$OUT"
echo "✓ 截图保存到: $OUT"
