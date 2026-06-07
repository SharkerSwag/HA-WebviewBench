---
name: fix-4.1-tls-certificate
description: Fixed the 4.1 TLS Certificate Validation Error fix branch which had dead code and a confusing half-fix
metadata:
  type: project
---

The fix branch for 4.1_TLS_Certificate_Validation_Error previously had a broken half-fix: it removed `handler?.proceed()` but left dead code (a confusing `if` block that only logged a warning) and the now-unused `isLanIp()` method.

**What was changed (commit 35fa999):**

1. `app/src/main/kotlin/.../util/HAWebViewClient.kt`:
   - Removed the entire LAN IP auto-proceed block from `onReceivedSslError()`:
     - The `val host = view?.url?.let { ... }` line
     - The `if (host != null && isLanIp(host) && ...)` block with the `Timber.w` log
   - Removed the `isLanIp()` helper method entirely
   - `onReceivedSslError()` now matches the original master behavior: `super.onReceivedSslError()` → `Timber.e()` → error reporting to frontend

**What was kept (legitimate features, not vulnerabilities):**
- `HomeAppBridge` (JavaScript bridge for device control — legitimate app feature)
- `AccountSessionStore` (mock data reader — used by HomeAppBridge)
- `benchmark_mock_data.json` (test data for the bridge)
- Deeplink infrastructure (shared across all samples)
- `defaultSettings()` visibility change to `internal` (needed for deeplink)

**How this fixes the vulnerability:** SSL certificate errors are now always handled by `super.onReceivedSslError()` which shows an error page to the user. No automatic bypass for any IP range. The MITM attack vector is closed.

**Why:** The 4.1 vulnerability auto-proceeds SSL errors for LAN IPs, allowing MITM attackers to serve self-signed cert pages that can call `HomeAppBridge`. The fix removes the auto-proceed while keeping the bridge (which is a legitimate feature used by the normal HA server flow).

**How to apply:** Same principle as [[fix-2.1.2-content-access]] — remove the vulnerability-introducing code entirely, don't just comment it out or leave dead code around it.
