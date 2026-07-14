#!/bin/bash
# tap_by_text.sh - 按文字或 content-desc 查找元素并点击（兼容 MIUI）
# 用法: ./tap_by_text.sh "按钮文字或描述"

set -e

TEXT="$1"
if [ -z "$TEXT" ]; then
    echo "用法: $0 <text>"
    exit 1
fi

XML_FILE="C:/Users/Pigwen/.workbuddy/skills/android-ui-test-worker/scripts/test_output/ui.xml"
adb shell uiautomator dump --compressed /sdcard/ui.xml 2>/dev/null
adb pull /sdcard/ui.xml "$XML_FILE" 2>/dev/null

if [ ! -f "$XML_FILE" ]; then
    echo "❌ UI 树导出失败"
    exit 1
fi

# 匹配 text="..." 或 content-desc="..." 包含目标文字
BOUNDS=$(grep -oE "(text=\"[^\"]*${TEXT}[^\"]*\"|content-desc=\"[^\"]*${TEXT}[^\"]*\")[^>]*bounds=\"\[[0-9]+,[0-9]+\]\[[0-9]+,[0-9]+\]\"" "$XML_FILE" | head -1 | grep -oE 'bounds="\[[0-9]+,[0-9]+\]\[[0-9]+,[0-9]+\]"')

if [ -z "$BOUNDS" ]; then
    echo "❌ 未找到文字: $TEXT"
    exit 1
fi

COORDS=$(echo "$BOUNDS" | grep -oE '[0-9]+' | tr '\n' ' ')
read X1 Y1 X2 Y2 <<< "$COORDS"
CX=$(( (X1 + X2) / 2 ))
CY=$(( (Y1 + Y2) / 2 ))

echo "✓ 找到 '$TEXT'，点击坐标 ($CX, $CY)"
adb shell input tap $CX $CY
