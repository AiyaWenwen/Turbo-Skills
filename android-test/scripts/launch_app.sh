#!/bin/bash
# launch_app.sh - 启动 App
# 用法: ./launch_app.sh [package_name]

PKG="${1:-com.wy.todaythings}"
adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1 > /dev/null
echo "✓ 已启动: $PKG"
