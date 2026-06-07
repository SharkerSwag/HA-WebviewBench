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

**CMake path length issue:** The microwakeword module's CMake FetchContent creates paths exceeding Windows' 260-char limit (e.g., `tflite_micro-populate-done` under `.cxx/Debug/1g1b4cj2/x86/_deps/...`). The `android.overridePathCheck=true` in gradle.properties doesn't help with CMake/ninja path limits. Excluding the microwakeword native build tasks (see above) is the workaround.

**Build command that works (from worktree root, with JDK 21):**
```bash
JAVA_HOME="/c/Program Files/Java/jdk-21" ./gradlew.bat :app:assembleDebug \
  -x :microwakeword:buildCMakeDebug \
  -x :microwakeword:buildCMakeDebug[arm64-v8a] \
  -x :microwakeword:buildCMakeDebug[armeabi-v7a] \
  -x :microwakeword:buildCMakeDebug[x86] \
  -x :microwakeword:buildCMakeDebug[x86_64]
```

**How to apply:** Use this build command for all HA sample worktrees. The base repo (`apps/home-assistant/base/`) may also need JDK 21 override.
