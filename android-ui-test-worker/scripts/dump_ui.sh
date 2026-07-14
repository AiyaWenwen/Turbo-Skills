#!/bin/bash
# dump_ui.sh - 导出 UI 树（兼容 MIUI，忽略 stderr）
# 用法: ./dump_ui.sh [输出路径]

OUT="${1:-C:/Users/Pigwen/.workbuddy/skills/android-ui-test-worker/scripts/test_output/ui.xml}"
adb shell uiautomator dump --compressed /sdcard/ui.xml 2>/dev/null
adb pull /sdcard/ui.xml "$OUT" 2>/dev/null
echo "✓ UI 树导出到: $OUT"
