---
name: build-environment
description: Build environment quirks discovered while compiling the HA Android samples
metadata:
  type: reference
---

**JAVA_HOME issue:** The system `JAVA_HOME` points to `D:\JEB\jadx-gui-1.5.5-with-jre-win\jre` (a stripped JRE from JADX). This JRE is missing `java.lang.management.ManagementFactory` which Gradle needs. Fix: override `JAVA_HOME` to a proper JDK:
```bash
JAVA_HOME="/c/Program Files/Java/jdk-21" ./gradlew.bat assembleDebug
```

**Gradle 9.5.0 wildcard exclusion changed:** The old build command `-x :microwakeword:*` no longer works in Gradle 9.5.0. The wildcard `*` task name matching was changed. To exclude native CMake tasks, use explicit task names:
```bash
-x :microwakeword:buildCMakeDebug -x :microwakeword:buildCMakeDebug[arm64-v8a] \
-x :microwakeword:buildCMakeDebug[armeabi-v7a] -x :microwakeword:buildCMakeDebug[x86] \
-x :microwakeword:buildCMakeDebug[x86_64]
```

**CMake path length issue:** The microwakeword module's CMake FetchContent creates paths exceeding Windows' 260-char limit. Two solutions:

1. **Enable Windows long paths** (permanent fix, needs admin + reboot):
   ```powershell
   Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name 'LongPathsEnabled' -Value 1
   ```
2. **Use `subst` to create a shorter path** (immediate, no reboot):
   ```bash
   subst W: "<worktree_path>"
   cd W:/
   JAVA_HOME="/c/Program Files/Java/jdk-21" ./gradlew.bat :app:assembleDebug
   subst W: /d  # cleanup
   ```

**CMake 4.1.2:** Verified installed at `C:\Users\16788\AppData\Local\Android\Sdk\cmake\4.1.2\`. The build failure is purely a path-length issue, not a missing dependency.

**Do NOT modify source code** (e.g., commenting out CMake in `microwakeword/build.gradle.kts`) to work around build issues. Use Gradle `-x` flags or environment fixes instead.

**Build command that works (from worktree root, with JDK 21):**
```bash
JAVA_HOME="/c/Program Files/Java/jdk-21" ./gradlew.bat :app:assembleDebug \
  -x :microwakeword:buildCMakeDebug \
  -x :microwakeword:buildCMakeDebug[arm64-v8a] \
  -x :microwakeword:buildCMakeDebug[armeabi-v7a] \
  -x :microwakeword:buildCMakeDebug[x86] \
  -x :microwakeword:buildCMakeDebug[x86_64]
```

**How to apply:** Use this build command for all HA sample worktrees. The `-x` flags are build-time configuration, not source modification — the source stays clean.
