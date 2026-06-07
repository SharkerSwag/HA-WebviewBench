---
name: sample-4.2-todo
description: 4.2 Insecure Network Content Trust — vuln/fix branches now complete, cleaned, and verified
metadata:
  type: project
---

4.2_Insecure_Network_Content_Trust has been verified and cleaned up (2026-06-07).

## Current state

- **vuln branch**: MIXED_CONTENT_ALWAYS_ALLOW + HomeAppBridge (getDeviceState, sendCommand). No deeplink.
- **fix branch**: MIXED_CONTENT_NEVER_ALLOW. HomeAppBridge removed. No deeplink.
- Both compile successfully (BUILD SUCCESSFUL).
- Exploit server exists at `exp/home-assistant/4.2_Insecure_Network_Content_Trust/` with widget.js + 4.2.html.

## Cleanup done

1. Resolved merge conflicts in fix branch (MIXED_CONTENT_NEVER_ALLOW was correct)
2. Removed incorrectly added deeplink code (isTrustedUrl, handleDeeplinkIntent) from fix branch
3. Fixed settings.gradle.kts to include microwakeword module
4. Updated benchmark_samples.json with corrected description and mock server info

## Attack chain (no deeplink)

1. User loads legitimate HA frontend over HTTPS (normal app flow)
2. Frontend includes `<script src="http://cdn.home-assistant.io/integrations/widget.js">`
3. MIXED_CONTENT_ALWAYS_ALLOW permits HTTP resource in HTTPS page
4. Attacker ARP-spoofs / MITMs the HTTP request to widget.js
5. Injected JS calls HomeAppBridge.sendCommand() / getDeviceState()
6. Data exfiltrated to attacker server

## How to apply

Verification requires HTTPS test page + MITM setup. For code-level verification:
- vuln has MIXED_CONTENT_ALWAYS_ALLOW + HomeAppBridge ✅
- fix has MIXED_CONTENT_NEVER_ALLOW, no HomeAppBridge ✅

**Why:** The branches existed but had merge conflicts, incorrectly added deeplink code, and a broken settings.gradle.kts. Now clean and buildable.

Related: [[deeplink-alignment-pass]]
