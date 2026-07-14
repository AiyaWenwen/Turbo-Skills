#!/bin/bash
# input_text.sh - 输入文字（不能含中文）
# 用法: ./input_text.sh "hello world"

TEXT="$1"
if [ -z "$TEXT" ]; then
    echo "用法: $0 <text>"
    exit 1
fi

# 空格用 %s 替换
ENCODED=$(echo "$TEXT" | sed 's/ /%s/g')
adb shell input text "$ENCODED"
echo "✓ 已输入: $TEXT"
