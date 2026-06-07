---
name: optimize-pass2
description: Optimization pass for samples 2.1.2 and 4.1 (fix logic was already done in round 1)
metadata:
  type: project
---

These two samples had their fix logic corrected in the first round:
- [[fix-2.1.2-content-access]] — Removed insecure settings from deeplink flow
- [[fix-4.1-tls-certificate]] — Removed LAN IP auto-bypass

This optimization pass cleaned up encoding corruption only. Both branches were clean of .vscode artifacts and CMake source hacks.

## 2.1.2
- Vuln: 3 encoding corruptions fixed (`1850d8a` equivalent)
- Fix: 3 encoding corruptions fixed (`b682418`)

## 4.1
- Vuln: 5 encoding corruptions fixed (`53e7b4e`)
- Fix: 5 encoding corruptions fixed (`1795661`)
