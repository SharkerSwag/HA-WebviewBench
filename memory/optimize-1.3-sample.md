---
name: optimize-1.3-sample
description: Optimized 1.3 — reverted CMake hack on both branches, fixed encoding on fix branch
metadata:
  type: project
---

## Issues found

1. **CMake hack on both branches:** `microwakeword/build.gradle.kts` had `externalNativeBuild`, `ndkVersion` commented out, plus an accidentally duplicated test block. Reverted to master on both branches.

2. **Encoding corruption (fix only):** 5 `—` characters garbled to `�?` in `WebViewActivity.kt` comments. Fixed. Vuln branch was clean.

## Fix quality assessment

1.3's fix is **proper**: it escapes special characters (`\`, `'`, `"`, `\n`, `\r`) in the notification message before injecting into `javascript:showNotification('...')`. This prevents breaking out of the string literal.

Unlike 1.1/1.2, 1.3's fix does NOT add domain restriction for `HomeAppBridge`. This is by design — 1.3's vulnerability is about dynamic script injection, not bridge exposure. The bridge remains accessible to all pages, which is the expected state for this sample.

## About onboarding bypass

1.3 does not have `isDeeplinkFlow` infrastructure. The deeplink loads the URL on top of the existing Compose UI WebView. Onboarding is bypassed naturally because the manifest intent-filter routes `homeassistant://webview` directly to `WebViewActivity`.

## Verification notes

1.3's exploit requires two attack vectors:
- **Deeplink**: Loads attack page → calls `HomeAppBridge` directly (works on both vuln and fix — bridge is not restricted for 1.3)
- **Notification injection**: Polls `notify.home-assistant.io` → MITM/spoof response → inject JS (works on vuln, blocked on fix by escaping)

The primary vulnerability is the JS injection, which is properly fixed. The bridge exposure is not 1.3's target vulnerability.

## How to apply

See [[optimize-1.1-sample]] and [[optimize-1.2-sample]] for previous rounds.
