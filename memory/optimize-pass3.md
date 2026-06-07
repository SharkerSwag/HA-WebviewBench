---
name: optimize-pass3
description: Batch optimization pass for remaining 10 samples (2.2.2–5.2)
metadata:
  type: project
---

All remaining samples were checked and fixed. Only encoding corruption was found.

## Results

| Sample | Fix encoding | Vuln encoding | Other issues |
|---|---|---|---|
| 2.2.2 | 3 fixed | clean | — |
| 2.3.1 | 3 fixed | clean | — |
| 2.3.2 | 3 fixed | clean | — |
| 2.4 | clean | clean | — |
| 3.1.1 | 3 fixed | 3 fixed | — |
| 3.1.2 | 3 fixed | clean | — |
| 3.1.3 | clean | clean | — |
| 3.1.4 | clean | clean | — |
| 5.1 | 3 fixed | 3 fixed | — |
| 5.2 | 3 fixed | 3 fixed | — |

No `.vscode` artifacts, no CMake source hacks found in any of these samples.

## Key finding

The CMake hack (`externalNativeBuild` commented out in `microwakeword/build.gradle.kts`) only existed in early samples (1.1, 1.3, 2.1.1). Later samples were created without this hack, suggesting the build workaround was identified and avoided after the initial batch.

