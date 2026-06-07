---
name: optimize-2.1.1-sample
description: Optimized 2.1.1 — CMake revert on fix, encoding fix on both branches
metadata:
  type: project
---

## Issues found

1. **CMake hack (fix only):** `microwakeword/build.gradle.kts` had `externalNativeBuild` blocks commented out. Reverted to master. Vuln branch was clean.

2. **Encoding corruption (both):** 3 `—` characters garbled to `�?` in `WebViewActivity.kt` comments on both branches.

## Fix quality

2.1.1's fix is **proper**: it removes `allowFileAccess`/`allowContentAccess`/`allowUniversalAccessFromFileURLs` from the deeplink flow and the HAWebViewClient config, and only enables them conditionally for trusted `home-assistant.io` domains via `isTrustedHomeAssistantDomain()`.

## Onboarding

2.1.1 has `isDeeplinkFlow` infrastructure — deeplink bypasses LaunchActivity/onboarding.

## Verification

Build passes. Deeplink smoke test: app opens, page loads, no crash.

