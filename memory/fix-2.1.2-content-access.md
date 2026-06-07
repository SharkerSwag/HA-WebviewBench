---
name: fix-2.1.2-content-access
description: Fixed the 2.1.2 Content Access Misconfiguration fix branch which previously only changed comments
metadata:
  type: project
---

The fix branch for 2.1.2_Content_Access_Misconfiguration previously only changed a comment in `HAWebView.kt` without actually removing the insecure `allowContentAccess = true` setting. The "fix" was non-functional.

**What was changed (commit 73ce5cb):**

1. `app/src/main/kotlin/.../util/compose/webview/HAWebView.kt`:
   - Changed `allowContentAccess = true` to `allowContentAccess = false` in `defaultSettings()`
   - Updated the comment to indicate content access is disabled by default

2. `app/src/main/kotlin/.../webview/WebViewActivity.kt`:
   - Removed the three insecure WebSettings lines from the deeplink flow:
     - `allowFileAccess = true`
     - `allowContentAccess = true`
     - `allowUniversalAccessFromFileURLs = true`
   - Deeplink flow now only calls `webView.defaultSettings()` + `setContentView(webView)`

**How this fixes the vulnerability:** Deeplink-loaded pages no longer have `content://` cross-origin access. The deeplink infrastructure (isDeeplinkFlow, handleDeeplinkIntent, manifest intent-filter) remains intact as shared infrastructure for other samples.

**Why:** The 2.1.2 vulnerability allows `content://` URIs to be loaded via deeplink, giving attacker pages access to ContentProvider data. The proper fix removes the content access permissions from untrusted (deeplink-loaded) contexts.

**How to apply:** When reviewing other content/file access samples (2.1.1), ensure their fix branches similarly remove the insecure settings rather than just changing comments. [[fix-4.1-tls-certificate]] follows the same pattern of removing vulnerability code rather than commenting it out.
