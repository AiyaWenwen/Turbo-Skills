#!/bin/bash
# run_test.sh - 跑第一个测试用例
# 场景: 点击添加按钮能否跳转到新建任务页

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="$SCRIPT_DIR/test_output"
mkdir -p "$OUT_DIR"

echo "===== 测试 1: 点击添加按钮跳转新建任务页 ====="

# 1. 启动 App
echo "[1/5] 启动 App..."
adb shell monkey -p com.wy.todaythings -c android.intent.category.LAUNCHER 1 > /dev/null
sleep 2

# 2. 截图首页
echo "[2/5] 截图首页..."
adb exec-out screencap -p > "$OUT_DIR/01_home.png"
echo "  ✓ 01_home.png"

# 3. 点击"添加任务"按钮
echo "[3/5] 点击添加任务按钮..."
if ! "$SCRIPT_DIR/tap_by_text.sh" "添加任务"; then
    echo "❌ 找不到添加任务按钮"
    exit 1
fi
sleep 2

# 4. 截图新建页
echo "[4/5] 截图新建任务页..."
adb exec-out screencap -p > "$OUT_DIR/02_add_task.png"
echo "  ✓ 02_add_task.png"

# 5. 验证：检查 UI 中是否有标题输入框
echo "[5/5] 验证跳转..."
"$SCRIPT_DIR/dump_ui.sh" "$OUT_DIR/02_add_task.xml" > /dev/null
if grep -qE 'class="android.widget.EditText"' "$OUT_DIR/02_add_task.xml"; then
    echo ""
    echo "✅ 测试通过：成功跳转到新建任务页（检测到 EditText）"
    echo "   输出文件："
    echo "   - $OUT_DIR/01_home.png"
    echo "   - $OUT_DIR/02_add_task.png"
    echo "   - $OUT_DIR/02_add_task.xml"
    exit 0
else
    echo ""
    echo "❌ 测试失败：未检测到输入框"
    exit 1
fi
