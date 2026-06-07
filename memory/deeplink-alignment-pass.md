---
name: deeplink-alignment-pass
description: Aligned deeplink (feature 5) presence to match design.md spec across 4 samples
metadata:
  type: project
---

Aligned deeplink (isDeeplinkFlow pattern) across all 17 samples to strictly follow design.md specifications.

## Changes Made

| Sample | Action | Details |
|--------|--------|---------|
| 1.2 | Added isDeeplinkFlow | Was missing Compose UI bypass; deeplink worked but risked crash. Now has full pattern matching 1.1. |
| 2.2.2 | Added isDeeplinkFlow | Same fix as 1.2. Also fixed exp server /oauth/callback to read redirect_uri param per design. |
| 1.3 | Removed deeplink | Design only specifies feature 3 (JS injection) + feature 1 (HomeAppBridge). Removed intent-filter + handleDeeplinkIntent. Kept startNotificationPolling + registerHomeAppBridge. |
| 2.1.2 | Removed deeplink | Design says "仅使用新增功能4". Removed intent-filter + isDeeplinkFlow pattern + handleDeeplinkIntent. Moved content access settings to normal onCreate path. |

## Final State

- **15 samples with complete deeplink**: 1.1, 1.2, 2.1.1, 2.2.1, 2.2.2, 2.3.1, 2.3.2, 2.4, 3.1.1, 3.1.2, 3.1.3, 3.1.4, 4.1, 5.1, 5.2
- **2 samples without deeplink**: 1.3, 2.1.2
- **1 sample not yet created**: 4.2 (see [[sample-4.2-todo]])

## Key Insight

`isDeeplinkFlow` is NOT a vulnerability — it's shared infrastructure (通用修复 #1 and #2 from design.md). It skips Compose UI initialization when a deeplink is detected, preventing crashes from null server config. Samples that use deeplink (feature 5) MUST have it; samples that don't MUST NOT.

LaunchActivity was never modified in any sample — deeplink bypasses it entirely via AndroidManifest intent-filter routing directly to WebViewActivity.

**Why:** Design.md defines which features each sample uses. Extra features contaminate the benchmark. Missing infrastructure breaks exploits. Both directions needed fixing.

**How to apply:** When creating new samples, check design.md for feature 5 presence. If present, include full isDeeplinkFlow pattern (see 1.1 as reference). If absent, don't add deeplink at all.
