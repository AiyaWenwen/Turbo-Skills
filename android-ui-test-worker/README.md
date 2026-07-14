# Android UI Test Worker

通过 **JSON 用例 + uiautomator2 执行器** 实现 Android 设备自动化测试。使用说明见 [SKILL.md](./SKILL.md)。

## 整体架构

```mermaid
flowchart TD
    A[用户说「跑测试」「测试这个功能」] --> B[AI 读取 SKILL.md]
    B --> C{选择用例}
    C -->|现成用例| D[tests/*.json]
    C -->|新场景| E[复制模板 JSON 并修改 steps]
    D --> F[python runner.py --test xxx.json]
    E --> F
    F --> G[uiautomator2 连接 Android 设备]
    G --> H[按 steps 逐步执行]
    H --> I[截图 + 记录 PASS/FAIL]
    I --> J[生成 test_output/时间戳/report.html]
    J --> K[AI 解读结果 / 用户打开报告]
```

## 执行阶段（runner.py）

```mermaid
sequenceDiagram
    participant CLI as main()
    participant TR as TestRunner
    participant U2 as uiautomator2
    participant Dev as Android 设备

    CLI->>CLI: 解析 --test / --device / --out
    CLI->>CLI: 读取 JSON 用例
    CLI->>TR: 创建 TestRunner，连接设备
    TR->>U2: u2.connect(device)
    U2->>Dev: ADB 连接
    TR->>TR: run(test_case)
    alt auto_launch=true
        TR->>Dev: app_start(package)
    end
    loop 每个 step
        TR->>TR: _execute_one(step)
        TR->>Dev: tap/input/swipe/assert...
        TR->>Dev: screenshot（部分步骤）
        TR->>TR: 记录 PASS/FAIL + 耗时
        alt 失败且 continue_on_fail=false
            TR->>TR: break
        end
    end
    TR->>TR: save_report() → report.html
    CLI->>CLI: exit(0/1)
```

## 快速开始

```bash
cd android-ui-test-worker
python -u runner.py --test tests/test_add_image.json
```
