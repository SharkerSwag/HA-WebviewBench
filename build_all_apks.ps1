# build_all_apks.ps1 - 补全所有缺失的 vuln/fix APK
param(
    [switch]$VulnOnly,
    [switch]$FixOnly
)

$ErrorActionPreference = "Continue"
$base = "D:\Secsys\Webview Benchmark&自动化挖掘\Phrase 6\WebviewBench\apps\home-assistant\samples"
$apkRoot = "D:\Secsys\Webview Benchmark&自动化挖掘\Phrase 6\WebviewBench\apk\home-assistant"
$env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"

New-Item -ItemType Directory "$apkRoot\vuln" -Force | Out-Null
New-Item -ItemType Directory "$apkRoot\fix" -Force | Out-Null

$allSamples = Get-ChildItem $base -Directory | ForEach-Object { $_.Name } | Sort-Object

foreach ($sample in $allSamples) {
    $worktree = Join-Path $base $sample
    $vulnApk = Join-Path $apkRoot "vuln\$sample.apk"
    $fixApk = Join-Path $apkRoot "fix\$sample.apk"
    $buildApk = Join-Path $worktree "app\build\outputs\apk\full\debug\app-full-debug.apk"
    
    $needVuln = !(Test-Path $vulnApk) -and !$FixOnly
    $needFix = !(Test-Path $fixApk) -and !$VulnOnly
    
    if (!$needVuln -and !$needFix) {
        Write-Host "SKIP (both exist): $sample"
        continue
    }
    
    Push-Location $worktree
    
    if ($needVuln) {
        Write-Host "BUILD vuln: $sample"
        git switch "vuln/$sample" 2>$null
        $result = java -jar "gradle\wrapper\gradle-wrapper.jar" assembleDebug 2>&1
        if (Test-Path $buildApk) {
            Copy-Item $buildApk $vulnApk -Force
            Write-Host "  -> vuln OK: $($(Get-Item $vulnApk).Length) bytes"
        } else {
            Write-Host "  -> vuln FAILED"
        }
    }
    
    if ($needFix) {
        Write-Host "BUILD fix: $sample"
        git switch "fix/$sample" 2>$null
        $result = java -jar "gradle\wrapper\gradle-wrapper.jar" assembleDebug 2>&1
        if (Test-Path $buildApk) {
            Copy-Item $buildApk $fixApk -Force
            Write-Host "  -> fix OK: $($(Get-Item $fixApk).Length) bytes"
        } else {
            Write-Host "  -> fix FAILED"
        }
    }
    
    Pop-Location
    Write-Host "---"
}

# Final report
$vCount = (Get-ChildItem "$apkRoot\vuln" -Filter "*.apk" -ErrorAction SilentlyContinue).Count
$fCount = (Get-ChildItem "$apkRoot\fix" -Filter "*.apk" -ErrorAction SilentlyContinue).Count
Write-Host "`n=== FINAL: Vuln=$vCount/18, Fix=$fCount/18 ==="
