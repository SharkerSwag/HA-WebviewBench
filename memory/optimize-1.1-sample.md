---
name: optimize-1.1-sample
description: Optimized 1.1 vuln and fix branches — removed IDE artifacts, reverted unnecessary source mods, fixed encoding
metadata:
  type: project
---

Both vuln and fix branches of 1.1_Improper_Exposure_of_JavaScript_Bridge were cleaned up to follow the minimum-change principle.

**Changes applied (both branches):**

1. **Deleted `.vscode/tasks.json`** — VS Code workspace file accidentally committed. Not related to the vulnerability sample.

2. **Reverted `microwakeword/build.gradle.kts`** — The CMake `externalNativeBuild` blocks were previously commented out to work around Windows path-length build failures. This was wrong — source code should not be modified for build environment issues. The proper fix:
   - CMake 4.1.2 IS available in Android SDK
   - Windows long paths enabled in registry (`LongPathsEnabled=1`)
   - Build-time exclusions via `-x` Gradle flags handle the issue without source modification

3. **Fixed UTF-8 encoding corruption** — 5 occurrences of `—` (em dash, U+2014) were garbled to `�?` in WebViewActivity.kt comments. Restored to proper em dashes.

**What was NOT changed:**
- Deeplink infrastructure (Manifest, isDeeplinkFlow, handleDeeplinkIntent)
- HomeAppBridge registration and AccountSessionStore
- benchmark_mock_data.json
- HAWebView.kt visibility change
- DefaultFailFastHandler and gradle.properties (necessary build config)
- Onboarding/LaunchActivity — untouched, not needed for benchmark testing

**Commits:** `66d05ba` (vuln), `c81b010` (fix)

**Why:** The minimum-change principle requires that only vulnerability-related code is modified. IDE artifacts, commented-out native build config, and encoding corruption are all unnecessary deviations from the clean base.

**How to apply:** When reviewing other samples, apply the same checks: no IDE artifacts, no source-level build workarounds (use Gradle `-x` flags instead), and no encoding corruption in comments. See [[fix-2.1.2-content-access]] and [[fix-4.1-tls-certificate]] for similar fix-branch cleanups.
