---
name: android-ui-test-worker
description: Android 设备自动化测试，基于 JSON 用例 + uiautomator2 执行器。支持自然语言驱动的测试场景，自动生成 HTML 报告与截图证据。已验证兼容 MIUI 13 (Android 13, SDK 33)。
read_when:
  - Android 自动化测试
  - 跑回归用例
  - 模拟点击/输入/滑动
  - 截图 + UI 断言
  - "跑一下测试"/"测试这个功能"
---

# Android UI Test Worker

通过 **JSON 用例 + uiautomator2 执行器** 实现 Android 设备自动化测试。

## 触发词

- 「跑测试」「跑一下测试」「测试这个功能」
- 「Android 测试」「点击 XX」「截图」

## 适用设备

- ✅ 已验证：MIUI 13 (Android 13, SDK 33, 设备 cmi)
- 通用 Android 5.0+（uiautomator2 支持范围）

## 配置文件位置

- SKILL: `android-ui-test-worker/`
- 测试用例: `tests/*.json`
- 执行器: `runner.py`
- 输出: `test_output/YYYYMMDD_HHMMSS/`
- 备份 v1: `android-ui-test-worker.v1.bak/`（单用例硬编码版）

> 以上路径均相对于 skill 根目录（`android-ui-test-worker/`）。

## 权限前置条件

设备必须放开权限，否则所有点击/输入都会被 `INJECT_EVENTS` 拒绝：

- 开发者选项 → **USB 调试（安全设置）打开**
- MIUI 设备需要登录小米账号

## 快速开始

```bash
# 跑现成用例（在 skill 根目录下执行）
cd android-ui-test-worker
python -u runner.py --test tests/test_add_image.json

# 指定设备（多设备时）
python -u runner.py --test tests/xxx.json --device 192.168.3.4:42883
```

## JSON 用例格式

```json
{
  "name": "测试名称",
  "package": "com.wy.todaythings",
  "auto_launch": true,
  "continue_on_fail": false,
  "steps": [
    {"action": "screenshot", "name": "01_home"},
    {"action": "tap", "selector": "添加任务", "by": "description"},
    {"action": "wait", "ms": 2000},
    {"action": "screenshot", "name": "02_after_tap"},
    {"action": "input", "text": "买菜", "index": 0},
    {"action": "assert_exists", "selector": "买菜", "by": "text"}
  ]
}
```

## 支持的 Action

| Action | 必填参数 | 可选参数 | 说明 |
|--------|----------|----------|------|
| `launch` | `package` | `stop`, `wait` | 启动 App |
| `tap` | `selector`, `by` | `wait` | 点击元素 |
| `long_press` | `selector`, `by` | `wait` | 长按 |
| `input` | `text` | `index` | 输入文本（index 指定第几个 EditText） |
| `clear` | - | `index` | 清空输入框 |
| `swipe` | `x1`,`y1`,`x2`,`y2` | `duration` | 滑动 |
| `back` | - | - | 返回键 |
| `press` | `key` | - | 按键（home/back/menu 等） |
| `wait` | `ms` | - | 等待（毫秒） |
| `screenshot` | `name` | - | 截图 |
| `assert_exists` | `selector`, `by` | - | 断言元素存在 |
| `assert_not_exists` | `selector`, `by` | - | 断言元素不存在 |
| `assert_text_contains` | `text` | - | 断言 UI 树包含文本 |
| `log` | `message` | - | 输出日志 |

## 元素定位方式（by 参数）

| by 值 | 用途 | 示例 |
|-------|------|------|
| `text` | 完全匹配文字 | "确定" |
| `textContains` | 包含文字（推荐） | "添加" |
| `description` | content-desc 属性 | "添加任务" |
| `className` | 控件类型 | "android.widget.EditText" |
| `resourceId` | 资源 ID | "com.wy.todaythings:id/btn_save" |

## 模板脚本 / 编写新用例

最快方式：复制 `tests/test_add_image.json` → 改 steps。

**关键原则**：
1. 关键步骤前后都加 `screenshot`（排查用）
2. `tap` 后用 `wait` 等待动画/页面加载
3. 元素定位优先用 `textContains`（稳定，不受前后空格影响）
4. 用 `assert_exists` 做正向断言（如检查"拍照"按钮出现）
5. `continue_on_fail: true` 可以不中断跑完全部步骤（适合探查）

## 输出结构

```
test_output/YYYYMMDD_HHMMSS/
├── report.html            # HTML 报告（可浏览器打开）
├── 01_home.png            # 命名截图
├── 02_add_task_page.png
├── 03_image_picker.png
└── step_XX_*.png          # 自动步骤截图
```

## 现有用例

| 文件 | 场景 |
|------|------|
| `tests/add_task.json` | 基础：点击+号→新建页（3步） |
| `tests/add_task_complete.json` | 完整：输入→保存→断言（10步） |
| `tests/test_add_image.json` | 弹底部栏：添加图片（9步） ✅ 已跑通 |

## 进阶路线（未实现）

- [ ] LLM 解析自然语言 → JSON（用 Ollama qwen2.5:9b）
- [ ] 元素定位智能回退（text → description → className）
- [ ] 数据驱动（参数化用例）
- [ ] 并行执行多设备
- [ ] Allure 报告集成

## 常见问题

| 问题 | 解决 |
|------|------|
| `SecurityException: INJECT_EVENTS` | 开发者选项 → USB 调试安全设置 |
| `uiautomator dump` MIUI 崩溃 | `--compressed` + `2>/dev/null` |
| `init` 时 IME 安装失败 | 忽略，不影响点击 |
| Python 输出乱码 | `python -u runner.py ...` 加 `-u` 参数 |
| stdout 编码错误 | runner.py 内已 try/except 保护 |
