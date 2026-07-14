#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Android Test Runner v2
执行 JSON 描述的测试用例，支持自然语言驱动的 LLM 解析
"""
import uiautomator2 as u2
import json
import time
import os
import sys
import argparse
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass


class TestStep:
    def __init__(self, action, **kwargs):
        self.action = action
        self.params = kwargs

    def __repr__(self):
        return f"Step({self.action}, {self.params})"


class TestReport:
    def __init__(self, name):
        self.name = name
        self.steps = []
        self.start_time = datetime.now()
        self.end_time = None

    def add(self, step: TestStep, status: str, error: str = None, screenshot: str = None, duration_ms: int = 0):
        self.steps.append({
            "step": step,
            "status": status,  # PASS / FAIL / SKIP
            "error": error,
            "screenshot": screenshot,
            "duration_ms": duration_ms,
        })

    def finish(self):
        self.end_time = datetime.now()

    @property
    def passed(self):
        return sum(1 for s in self.steps if s["status"] == "PASS")

    @property
    def failed(self):
        return sum(1 for s in self.steps if s["status"] == "FAIL")

    @property
    def total(self):
        return len(self.steps)

    def to_html(self) -> str:
        rows = []
        for i, s in enumerate(self.steps, 1):
            status_color = {"PASS": "green", "FAIL": "red", "SKIP": "gray"}.get(s["status"], "black")
            img_html = f'<a href="{os.path.basename(s["screenshot"])}">截图</a>' if s["screenshot"] else ""
            err_html = f'<pre style="color:red">{s["error"]}</pre>' if s["error"] else ""
            rows.append(f"""
            <tr>
                <td>{i}</td>
                <td>{s["step"].action}</td>
                <td>{json.dumps(s["step"].params, ensure_ascii=False)}</td>
                <td style="color:{status_color};font-weight:bold">{s["status"]}</td>
                <td>{s["duration_ms"]}ms</td>
                <td>{img_html}{err_html}</td>
            </tr>
            """)

        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        return f"""
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{self.name}</title>
<style>
body{{font-family:Arial;margin:20px}}
.summary{{background:#f5f5f5;padding:15px;border-radius:8px;margin-bottom:20px}}
table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #ddd;padding:8px;text-align:left}}
th{{background:#4CAF50;color:white}}
</style></head>
<body>
<h1>测试报告: {self.name}</h1>
<div class="summary">
    <p>开始: {self.start_time.strftime("%Y-%m-%d %H:%M:%S")}</p>
    <p>结束: {self.end_time.strftime("%Y-%m-%d %H:%M:%S") if self.end_time else "-"}</p>
    <p>耗时: {duration:.1f}s</p>
    <p>通过: <b style="color:green">{self.passed}</b> / 失败: <b style="color:red">{self.failed}</b> / 总计: {self.total}</p>
</div>
<table>
<tr><th>#</th><th>动作</th><th>参数</th><th>状态</th><th>耗时</th><th>截图/错误</th></tr>
{''.join(rows)}
</table>
</body></html>
"""


class TestRunner:
    def __init__(self, device: str = None, out_dir: str = None):
        self.device = device
        self.d = u2.connect(device) if device else u2.connect()
        self.out_dir = out_dir or os.path.join(os.path.dirname(__file__), "test_output", datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(self.out_dir, exist_ok=True)

    def _screenshot(self, name: str) -> str:
        path = os.path.join(self.out_dir, f"{name}.png")
        self.d.screenshot(path)
        return path

    def _find(self, selector: str, by: str):
        """按指定方式查找元素"""
        by = by or "text"
        if by == "text":
            return self.d(text=selector)
        elif by == "textContains":
            return self.d(textContains=selector)
        elif by == "description":
            return self.d(description=selector)
        elif by == "className":
            return self.d(className=selector)
        elif by == "resourceId":
            return self.d(resourceId=selector)
        else:
            raise ValueError(f"Unknown selector by: {by}")

    def _execute_one(self, step: TestStep, report: TestReport) -> bool:
        """执行单步，返回是否成功"""
        start = time.time()
        action = step.action
        params = step.params
        screenshot = None
        try:
            if action == "launch":
                package = params.get("package")
                if not package:
                    raise ValueError("launch 需要 package 参数")
                self.d.app_start(package, stop=params.get("stop", True))
                time.sleep(params.get("wait", 2))
                screenshot = self._screenshot(f"step_{len(report.steps)+1:02d}_launch")

            elif action == "screenshot":
                screenshot = self._screenshot(params.get("name", f"step_{len(report.steps)+1:02d}"))

            elif action == "tap":
                # 支持坐标点击
                if "x" in params and "y" in params:
                    self.d.click(params["x"], params["y"])
                    time.sleep(params.get("wait", 1))
                    screenshot = self._screenshot(f"step_{len(report.steps)+1:02d}_after_tap")
                else:
                    selector = params.get("selector")
                    by = params.get("by", "text")
                    if not selector:
                        raise ValueError("tap 需要 selector 或 x/y 参数")
                    elem = self._find(selector, by)
                    if not elem.exists:
                        raise AssertionError(f"元素不存在: {selector} (by={by})")
                    elem.click()
                    time.sleep(params.get("wait", 1))
                    screenshot = self._screenshot(f"step_{len(report.steps)+1:02d}_after_tap")

            elif action == "long_press":
                selector = params.get("selector")
                by = params.get("by", "text")
                elem = self._find(selector, by)
                elem.long_click()
                time.sleep(params.get("wait", 1))

            elif action == "input":
                text = params.get("text", "")
                index = params.get("index", 0)  # 第几个 EditText
                edit = self.d(className="android.widget.EditText")
                if not edit.exists:
                    raise AssertionError("没有找到 EditText")
                # 多个 EditText 时按 index 选择
                if edit.count > 1:
                    edit[index].set_text(text)
                else:
                    edit.set_text(text)
                time.sleep(params.get("wait", 0.5))

            elif action == "clear":
                index = params.get("index", 0)
                edit = self.d(className="android.widget.EditText")
                if edit.count > 1:
                    edit[index].clear_text()
                else:
                    edit.clear_text()

            elif action == "swipe":
                x1, y1 = params["x1"], params["y1"]
                x2, y2 = params["x2"], params["y2"]
                duration = params.get("duration", 0.5)
                self.d.swipe(x1, y1, x2, y2, duration)

            elif action == "back":
                self.d.press("back")
                time.sleep(0.5)

            elif action == "press":
                self.d.press(params["key"])

            elif action == "wait":
                time.sleep(params.get("ms", 1000) / 1000)

            elif action == "assert_exists":
                selector = params.get("selector")
                by = params.get("by", "text")
                elem = self._find(selector, by)
                if not elem.exists:
                    raise AssertionError(f"断言失败：元素不存在 {selector}")
                screenshot = self._screenshot(f"step_{len(report.steps)+1:02d}_assert_ok")

            elif action == "assert_not_exists":
                selector = params.get("selector")
                by = params.get("by", "text")
                elem = self._find(selector, by)
                if elem.exists:
                    raise AssertionError(f"断言失败：元素不应存在 {selector}")

            elif action == "assert_text_contains":
                text = params.get("text", "")
                if text not in self.d.dump_hierarchy():
                    raise AssertionError(f"断言失败：UI 中不包含 {text}")

            elif action == "assert_not_clickable":
                selector = params.get("selector")
                by = params.get("by", "text")
                if not selector:
                    raise ValueError("assert_not_clickable 需要 selector 参数")
                elem = self._find(selector, by)
                if not elem.exists:
                    raise AssertionError(f"断言失败：元素不存在 {selector}")
                info = elem.info
                if info.get("clickable", False) and info.get("enabled", True):
                    raise AssertionError(f"断言失败：元素仍可点击 {selector}")
                attr = "text" if by in ("text", "textContains") else "content-desc"
                if by == "textContains":
                    xp = f'//*[contains(@{attr},"{selector}")]/ancestor::*[@clickable="true"][1]'
                else:
                    xp = f'//*[@{attr}="{selector}"]/ancestor::*[@clickable="true"][1]'
                clickable_parent = self.d.xpath(xp)
                if clickable_parent.exists:
                    parent_info = clickable_parent.info
                    if parent_info.get("enabled", True):
                        raise AssertionError(
                            f"断言失败：可点击父元素仍 enabled {selector} bounds={parent_info.get('bounds')}"
                        )
                screenshot = self._screenshot(f"step_{len(report.steps)+1:02d}_assert_not_clickable")

            elif action == "log":
                print(f"  [LOG] {params.get('message', '')}")

            else:
                raise ValueError(f"未知 action: {action}")

            duration = int((time.time() - start) * 1000)
            report.add(step, "PASS", screenshot=screenshot, duration_ms=duration)
            return True

        except Exception as e:
            duration = int((time.time() - start) * 1000)
            try:
                screenshot = screenshot or self._screenshot(f"step_{len(report.steps)+1:02d}_FAIL")
            except Exception:
                pass
            report.add(step, "FAIL", error=str(e), screenshot=screenshot, duration_ms=duration)
            return False

    def run(self, test_case: dict) -> TestReport:
        """执行一个测试用例"""
        name = test_case.get("name", "Unnamed Test")
        package = test_case.get("package")
        report = TestReport(name)
        print(f"\n===== {name} =====")

        # 可选：自动启动 App
        if package and test_case.get("auto_launch", True):
            launch_step = TestStep("launch", package=package, wait=2)
            if not self._execute_one(launch_step, report):
                report.finish()
                return report
            # 从报告中移除 launch 步骤（不计入测试步骤）
            report.steps.pop()

        steps_data = test_case.get("steps", [])
        for step_dict in steps_data:
            action = step_dict.pop("action")
            step = TestStep(action, **step_dict)
            print(f"  [{len(report.steps)+1}/{len(steps_data)}] {action} {step.params}")

            if not self._execute_one(step, report):
                print(f"  [FAIL] {step.action}: {report.steps[-1]['error']}")
                if not test_case.get("continue_on_fail", False):
                    break

        report.finish()
        return report

    def save_report(self, report: TestReport):
        """保存 HTML 报告"""
        html_path = os.path.join(self.out_dir, "report.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(report.to_html())
        return html_path


def main():
    parser = argparse.ArgumentParser(description="Android Test Runner v2")
    parser.add_argument("--test", "-t", required=True, help="测试用例 JSON 路径")
    parser.add_argument("--device", "-d", help="设备序列号或 IP")
    parser.add_argument("--out", "-o", help="输出目录")
    args = parser.parse_args()

    with open(args.test, "r", encoding="utf-8") as f:
        test_case = json.load(f)

    runner = TestRunner(device=args.device, out_dir=args.out)
    report = runner.run(test_case)

    # 输出结果
    print(f"\n===== 结果 =====")
    print(f"通过: {report.passed} / 失败: {report.failed} / 总计: {report.total}")
    html_path = runner.save_report(report)
    print(f"报告: {html_path}")
    print(f"截图: {runner.out_dir}")

    exit(0 if report.failed == 0 else 1)


if __name__ == "__main__":
    main()
