---
name: shared-deeplink-infra
description: The deeplink infrastructure is shared across all HA samples and should not be removed in fix branches
metadata:
  type: project
---

The deeplink infrastructure (`homeassistant://webview?url=<url>`) is shared across most HA vulnerability samples. It was introduced by `新增功能5：Dashboard Deeplink 外部 URL 入口` and consists of:

**Manifest changes** (in `AndroidManifest.xml`):
- `WebViewActivity` set to `android:exported="true"`
- Added `intent-filter` for scheme `homeassistant`, host `webview`

**Code changes** (in `WebViewActivity.kt`):
- `isDeeplinkFlow` flag set when intent matches the deeplink scheme
- Deeplink flow skips Compose UI, app lock, and `onResume` normal path
- `handleDeeplinkIntent()` parses the `url` parameter and calls `webView.loadUrl()`
- `defaultSettings()` visibility changed from `private` to `internal` in `HAWebView.kt`

**Other shared changes** (in all sample worktrees):
- `DefaultFailFastHandler` changed from `CrashFailFastHandler` to `LogOnlyFailFastHandler` (needed for emulator/debug builds)
- `gradle.properties`: `android.overridePathCheck=true` (needed for long paths on Windows)

**Important for fix branches:** When fixing a vulnerability that uses the deeplink, do NOT remove the deeplink infrastructure. The deeplink itself is not a vulnerability — it's a legitimate app feature. The fix should address the specific vulnerability code (e.g., remove insecure settings, fix SSL handling, add URL validation) while keeping the deeplink intact.

This applies to samples: 2.1.1, 2.1.2, 2.2.1, 2.2.2, 2.3.1, 2.3.2, 2.4, 3.1.1, 3.1.2, 3.1.3, 3.1.4, 4.1, 5.1, 5.2.

**How to apply:** When creating fix branches, first identify which "新增功能" are being fixed (the vulnerability-specific ones) vs which are shared infrastructure that should stay. See [[fix-2.1.2-content-access]] and [[fix-4.1-tls-certificate]] for examples.
