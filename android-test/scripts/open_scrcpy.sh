#!/bin/bash
# open_scrcpy.sh - 启动 scrcpy 屏幕镜像
# 用法: ./open_scrcpy.sh

SCRCPY="F:\Tools\scrcpy-win64-v3.3.4\scrplay.exe"
# 兼容 Windows 路径
SCRCPY_WIN="F:/Tools/scrcpy-win64-v3.3.4/scrplay.exe"

if [ -f "$SCRCPY_WIN" ]; then
    echo "✓ 启动 scrcpy..."
    "$SCRCPY_WIN" &
    echo "✓ scrcpy 已启动（PID: $!）"
else
    echo "❌ scrcpy 未找到: $SCRCPY_WIN"
    exit 1
fi
