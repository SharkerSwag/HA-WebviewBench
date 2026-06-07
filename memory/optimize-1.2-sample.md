---
name: optimize-1.2-sample
description: Optimized 1.2 vuln/fix branches — encoding fix on fix branch, vuln was clean
metadata:
  type: project
---

The 1.2_Insecure_JavaScript_Bridge_Implementation sample was in better shape than 1.1. No `.vscode` artifacts, no CMake source hacks.

## Issues found

1. **Encoding corruption (fix branch only):** 6 `—` characters garbled to `�?` in `WebViewActivity.kt` comments. The vuln branch was clean — corruption was introduced during the fix commit editing. Fixed.

2. **Exp server encoding:** `server.py` had 3 corrupted Chinese characters causing `SystemError: Negative size passed to PyUnicode_New` on startup. Fixed.

## Fix quality assessment

The 1.2 fix is properly implemented (unlike 2.1.2 and 4.1 which were fixed in the previous round):

1. **`AccountSessionStore.readMediaFile()`:** Added path traversal validation:
   - Rejects `..` and absolute paths (`/`)
   - Canonical path check prevents symlink escapes
   - ✅ Proper fix

2. **`WebViewActivity.handleDeeplinkIntent()`:** Added `isTrustedHomeAssistantDomain()`:
   - Only registers `HomeAppBridge` for `home-assistant.io` or `*.home-assistant.io`
   - ✅ Defense in depth

## Verification results (2026-06-07)

| Metric | Vuln | Fix |
|---|---|---|
| Path traversal `../shared_prefs/` | ✅ Leaked | ❌ Blocked |
| Path traversal `../databases/` | ✅ Leaked | ❌ Blocked |
| Deep path traversal | ✅ Leaked | ❌ Blocked |
| Bridge accessible | ✅ | ❌ (domain check) |
| **Verdict** | Vulnerable | Fixed |

## How to apply

When reviewing other samples, check both branches for encoding corruption separately — the corruption may only exist in one branch. See [[optimize-1.1-sample]] for the first round and [[verification-workflow]] for the testing methodology.
