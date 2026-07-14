#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
uiautomator2 测试脚本
场景: 点击添加按钮能否跳转到新建任务页
"""
import uiautomator2 as u2
import time
import os
import sys

# 解决 Windows GBK 编码问题
sys.stdout.reconfigure(encoding='utf-8')

OUT_DIR = os.path.join(os.path.dirname(__file__), "test_output")
os.makedirs(OUT_DIR, exist_ok=True)

OK = "[OK]"
FAIL = "[FAIL]"

def main():
    print("===== 测试 1: 点击添加按钮跳转新建任务页 =====")

    # 连接设备
    print("[1/5] 连接设备...")
    d = u2.connect()
    print(f"  设备信息: {d.info.get('productName')} / SDK {d.info.get('sdkInt')}")

    # 启动 App
    print("[2/5] 启动 App...")
    d.app_start("com.wy.todaythings", stop=True)
    time.sleep(2)

    # 截图首页
    print("[3/5] 截图首页...")
    d.screenshot(os.path.join(OUT_DIR, "01_home.png"))
    print(f"  {OK} 01_home.png")

    # 点击"添加任务"按钮
    print("[4/5] 点击添加任务按钮...")
    btn = d(description="添加任务")
    if not btn.exists:
        print(f"{FAIL} 找不到'添加任务'按钮")
        return False
    print(f"  找到按钮，位置: {btn.info.get('bounds')}")
    btn.click()
    time.sleep(2)

    # 截图新建页 + 验证
    print("[5/5] 截图新建任务页...")
    d.screenshot(os.path.join(OUT_DIR, "02_add_task.png"))
    print(f"  {OK} 02_add_task.png")

    # 验证：检查是否有 EditText
    if d(className="android.widget.EditText").exists:
        print("")
        print(f"{OK} 测试通过：成功跳转到新建任务页（检测到 EditText）")
        print(f"   输出目录: {OUT_DIR}")
        return True
    else:
        print("")
        print(f"{FAIL} 测试失败：未检测到输入框")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
