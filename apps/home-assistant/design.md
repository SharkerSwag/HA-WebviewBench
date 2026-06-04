# home-assistant-2026.5.2

## 组件原业务功能介绍

Home Assistant Android 是 Home Assistant 智能家居平台官方伴侣 App。其 WebView 组件（`WebViewActivity`）用于加载 Home Assistant 服务端前端面板（Lovelace Dashboard），用户通过该面板控制全屋智能设备、查看安防摄像头、管理自动化场景。

---

## 已验证通用修复（验证阶段发现的共性坑）

以下问题影响所有含 Deeplink 的 vuln 样本（1.1-5.2 除 4.2），已在各样本 vuln 分支中统一修复：

| # | 问题 | 根因 | 修复 |
|---|------|------|------|
| 1 | **页面加载但 JS 不执行** | Deeplink 路径跳过 Compose UI → `defaultSettings()` 未调用 → `javaScriptEnabled=false` | `isDeeplinkFlow` 分支中调用 `webView.defaultSettings()`；`HAWebView.kt` 中 `private`→`internal` |
| 2 | **Deeplink 后 App 闪退** | Deeplink 加载完 URL 后继续执行 Compose UI 初始化代码 → 空指针崩溃 | Deeplink 分支在 `setContentView(webView)` 后调用 `handleDeeplinkIntent(intent)` 并立即 `return` |
| 3 | **EXP 数据回传失败** | `{{LOCAL_IP}}` 在模拟器中指向 LAN IP 而非 `10.0.2.2` | EXP HTML 改用 `location.origin + '/collect'` |
| 4 | **`/exp/<id>` 返回 404** | 样本 ID 含点号（如 `1.1`），server.py 误判已有扩展名 | `if not fn.endswith(".html")` 替代 `if "." not in fn` |
| 5 | **server.py 启动报错** | 中文注释编码损坏（Non-UTF-8） | 统一切换为纯英文通用模板 |
| 6 | **force-stop 无效** | debug 构建包名为 `io.homeassistant.companion.android.debug` | 使用 `.debug` 后缀 |
| 7 | **FailFast 崩溃** | StrictMode 违规触发 `CrashFailFastHandler` | 全部替换为 `LogOnlyFailFastHandler` |
| 8 | **CMake 构建失败** | `microwakeword` 模块需要 CMake 4.1.2 | `-x :microwakeword:*` 排除任务 |

---

组件核心能力：
- 通过 `HAWebViewClient` 加载 HA 服务端 URL，处理 SSL 错误、HTTP 错误、TLS 双向认证
- 通过 `FrontendJsBridge`（V1: `externalApp` / V2: `externalAppV2`）与前端面板交换认证 Token
- 通过 `HAWebChromeClient` 处理权限请求（摄像头/麦克风/位置）、文件选择上传、JS 弹窗及全屏视频
- 通过 `FrontendDownloadManager` 处理 WebView 内文件下载（HTTP/HTTPS/Data URI），附带 Cookie 和 Authorization Header
- 通过 `shouldOverrideUrlLoading` 拦截 `app://`、`intent:` 及 Play Store 链接

WebView 默认配置：JavaScript 启用、DOM Storage 启用、Cookie（含第三方）启用、文件访问默认关闭。当前没有直接暴露给外部的 deeplink 可传入任意 URL，WebView 由内部逻辑启动并加载已配置的 HA 服务器地址。

---

## 新增功能设计

### 新增功能1：添加智能设备快捷控制 Bridge

**可使用的样本：**

- 1.1_Improper_Exposure_of_JavaScript_Bridge

**功能描述：**

为 HA 前端面板提供直接调用 Native 设备控制能力的接口，使网页可以查询设备状态和发送控制指令（如开关灯、调节温度），提升前端交互响应速度。

**代码约束：**

- 改动位置：在 `WebViewActivity` 中 WebView 初始化完成后，于现有 `externalApp` bridge 注册逻辑旁新增。
- 接口名称：bridge 名固定为 `HomeAppBridge`，API 包括 `getDeviceState(deviceId: String): String` 和 `sendCommand(deviceId: String, command: String): String`。
- 入参约束：`deviceId` 和 `command` 均为字符串。
- 返回约束：返回 JSON 字符串表示操作结果。
- 行为约束：只新增一个 `addJavascriptInterface` 绑定，不修改现有 bridge 行为，不新增 deeplink，不修改 Activity 导出状态。

**统一命名约束：**

所有样本统一使用 `window.HomeAppBridge.getDeviceState(deviceId)` 和 `window.HomeAppBridge.sendCommand(deviceId, command)` 调用，不得改用其他 bridge 名称。

**非目标行为：**

- 不新增额外 bridge API（如文件读写、Token 获取）。
- 不修改现有 `externalApp` bridge。
- 不修改 WebViewClient 或 WebChromeClient 回调。
- 不新增 deeplink 入口。

---

### 新增功能2：添加安防媒体文件读取 Bridge API

**可使用的样本：**

- 1.2_Insecure_JavaScript_Bridge_Implementation

**功能描述：**

在智能设备控制 Bridge 基础上，为安防场景提供本地快照/录像回放功能，允许前端面板根据文件名读取设备保存的截图或录像文件内容。

**代码约束：**

- 改动位置：在 `HomeAppBridge` 中新增方法。
- 接口名称：API 名为 `readMediaFile(fileName: String): String`。
- 入参约束：`fileName` 为字符串，由前端传入。
- 返回约束：返回文件内容字符串；文件不存在时返回空字符串。
- 行为约束：只新增一个 Bridge API 方法，使用 `File(baseDir, fileName)` 拼接路径后读取文件内容，不新增其他文件操作 API。

**统一命名约束：**

所有样本统一使用 `window.HomeAppBridge.readMediaFile(fileName)`，baseDir 固定为 App 内部存储的 `snapshots` 目录。

**非目标行为：**

- 不新增文件写入、删除、列出目录等 API。
- 不修改文件访问权限配置（`allowFileAccess` 等）。
- 不在 Bridge 外新增其他文件操作入口。

---

### 新增功能3：Dashboard 通知动态脚本注入

**可使用的样本：**

- 1.3_Dynamic_Script_Injection_Risk

**功能描述：**

支持服务端推送重要告警到前端面板时，自动执行 Native 注入的 JavaScript 代码，在面板上显示 Toast 提示或触发刷新。常用于安防告警、设备离线通知等场景。

**代码约束：**

- 改动位置：在 `WebViewActivity` 中收到服务端推送通知的回调处新增。
- 接口名称：不涉及 Bridge，为 `webView.loadUrl("javascript:...")` 或 `evaluateJavascript` 调用。
- 入参约束：注入的 JS 字符串由服务端推送消息体中的 `message` 字段拼接生成。
- 返回约束：无。
- 行为约束：只拼接 `message` 字段到固定 JS 模板字符串后执行，不新增 Bridge API，不修改 Bridge 行为。

**统一命名约束：**

JS 模板固定为 `"javascript:showNotification('" + message + "')"`。

**非目标行为：**

- 不对 `message` 字段做任何过滤或转义。
- 不新增其他动态 JS 执行路径。
- 不修改服务端推送消息的其他处理逻辑。

---

### 新增功能4：本地文件访问配置放宽

**可使用的样本：**

- 2.1.1_File_Access_Misconfiguration
- 2.1.2_Content_Access_Misconfiguration

**功能描述：**

为支持前端面板加载本地缓存的静态资源（如离线 Dashboard 页面）以及访问通过 ContentProvider 共享的设备配置文件，放宽 WebView 的文件和内容访问限制。

**代码约束：**

- 改动位置：在 `HAWebView.kt` 的 `defaultSettings()` 方法中或 WebView 初始化完成后设置。
- 接口名称：`settings.allowFileAccess = true`，`settings.allowContentAccess = true`，`settings.allowUniversalAccessFromFileURLs = true`。
- 入参约束：无。
- 返回约束：无。
- 行为约束：只设置这三个 WebSettings 标志位，不新增其他资源访问配置。

**统一命名约束：**

所有样本使用相同的三个 WebSettings 配置。

**非目标行为：**

- 不新增文件读取 Bridge API。
- 不新增 ContentProvider。
- 不修改网络访问策略。

---

### 新增功能5：Dashboard Deeplink 外部 URL 入口

**可使用的样本：**

- 2.2.1_Insufficient_URL_Source_Validation
- 2.2.2_Insecure_Redirect_Handling
- 2.3.1_Insecure_External_Navigation_Scheme_Handling
- 2.3.2_Insecure_System_Scheme_Handling
- 4.1_TLS_Certificate_Validation_Error
- 5.1_Cookie_Leakage

**功能描述：**

为支持从外部应用或通知点击直接跳转到指定 HA 面板页面，新增一条 deeplink 路由，允许外部通过 `homeassistant://webview` scheme 传入目标 URL 并打开 WebView。

**代码约束：**

- 改动位置：在 `WebViewActivity` 的 `AndroidManifest.xml` 声明中新增 `intent-filter`，并在 `onCreate` / `onNewIntent` 中解析 `url` 参数后调用现有 `loadUrl` 逻辑。
- 接口名称：scheme 固定为 `homeassistant`，host 固定为 `webview`，参数名固定为 `url`。
- 入参约束：`url` 参数为字符串，表示要加载的目标 URL。
- 返回约束：无。
- 行为约束：只解析 `url` 参数并传给现有 `loadUrl`，不新增独立的 URL 加载逻辑，不修改 WebView 的配置。

**统一命名约束：**

所有样本使用 `homeassistant://webview?url=<url>` 触发，不得新增其他 scheme、host 或参数。

**非目标行为：**

- 不新增其他 deeplink path。
- 不修改现有 `app://`、`intent:` 处理逻辑。
- 不在 deeplink 解析中对 URL 做白名单校验（白名单校验由新增功能7 独立负责）。

---

### 新增功能6：URL 可信域名校验逻辑

**可使用的样本：**

- 2.2.1_Insufficient_URL_Source_Validation

**功能描述：**

为 Dashboard Deeplink 加载的 URL 添加域名白名单校验，确保只加载来自 `home-assistant.io` 或其子域名的可信页面，防止恶意 URL 注入。

**代码约束：**

- 改动位置：在 `WebViewActivity` 的 deeplink URL 加载前调用。
- 接口名称：校验方法名为 `isTrustedUrl(url: String): Boolean`。
- 入参约束：`url` 为待校验的完整 URL 字符串。
- 返回约束：返回布尔值，`true` 表示可信。
- 行为约束：只做字符串级别的域名检查，不涉及网络请求。

**统一命名约束：**

校验方法必须命名为 `isTrustedUrl`，且位于 `WebViewActivity` 中。

**非目标行为：**

- 不修改 WebViewClient 的 `shouldOverrideUrlLoading` 逻辑。
- 不在 `isTrustedUrl` 中做 URL 规范化或重定向追踪。

---

### 新增功能7：外部导航 Intent Scheme 处理

**可使用的样本：**

- 2.3.1_Insecure_External_Navigation_Scheme_Handling

**功能描述：**

在 WebView 中启用对 `intent://` scheme 的解析，使 HA 面板中的第三方集成链接（如打开银行 App 支付、跳转地图导航）能够正常启动外部 App。

**代码约束：**

- 改动位置：在 `WebViewActivity` 的 `shouldOverrideUrlLoading` 处理回调中新增 `intent:` scheme 分支。
- 接口名称：不新增命名接口，在现有 `onUrlIntercepted` 回调中增加 `Intent.parseIntUri` 处理。
- 入参约束：接收完整的 `intent://` URI 字符串。
- 返回约束：返回 `true` 表示已拦截处理。
- 行为约束：只解析 `intent://` URI 并调用 `startActivity`，不涉及其他 scheme。

**统一命名约束：**

`intent:` scheme 处理逻辑统一在 `onUrlIntercepted` 回调中实现。

**非目标行为：**

- 不新增 `intent:` 以外的自定义 scheme 处理。
- 不验证 intent URI 的来源或目标组件。

---

### 新增功能8：系统 Scheme 自动处理

**可使用的样本：**

- 2.3.2_Insecure_System_Scheme_Handling

**功能描述：**

为 HA 面板中的联系信息、地址等元素提供系统能力调用支持，例如点击电话号码自动拨号、点击地址自动打开地图、点击邮箱自动撰写邮件。

**代码约束：**

- 改动位置：在 `WebViewActivity` 的 URL 拦截回调中新增 `tel:`、`sms:`、`mailto:`、`geo:` scheme 分支。
- 接口名称：不新增命名接口，在各 scheme 分支中构造对应的 `Intent(Intent.ACTION_*)` 并启动。
- 入参约束：接收对应 scheme 的标准 URI 格式。
- 返回约束：返回 `true` 表示已拦截处理。
- 行为约束：只对 `tel:`、`sms:`、`mailto:`、`geo:` 四种系统 scheme 做处理。

**统一命名约束：**

处理逻辑统一在 `WebViewActivity` 的 URL 拦截回调中。

**非目标行为：**

- 不验证触发系统 scheme 的页面来源。
- 不弹出用户确认对话框。
- 不新增其他系统 scheme（如 `package:`）。
- 不修改 Manifest 权限声明。

---

### 新增功能9：本地资源拦截映射

**可使用的样本：**

- 2.4_Insecure_Request_Interception_and_Resource_Mapping

**功能描述：**

为提升离线或弱网环境下的面板加载速度，将 `app.local` host 下的 Web 请求映射到 App 内部存储的预缓存静态资源文件，使 HA 前端可以无网络访问本地资源。

**代码约束：**

- 改动位置：在 `HAWebViewClient` 中覆写 `shouldInterceptRequest`。
- 接口名称：拦截 host 固定为 `app.local`。
- 入参约束：映射 URL path 到 `context.filesDir` 下对应文件路径。
- 返回约束：返回 `WebResourceResponse`，MIME 根据文件扩展名推断。
- 行为约束：只拦截 `https://app.local/*` 的请求并映射到本地 `filesDir` 下对应文件。

**统一命名约束：**

host 固定为 `app.local`，路径映射规则为直接将 URL path 拼接到 `filesDir`。

**非目标行为：**

- 不拦截其他 host 的请求。
- 不修改请求或响应内容。
- 不新增文件写入逻辑。

---

### 新增功能10：安防截图文件选择回调

**可使用的样本：**

- 3.1.1_Insecure_File_Selection_Callback

**功能描述：**

为 HA 前端面板的安防配置页提供上传本地截图功能，允许用户通过 `<input type="file">` 选择保存在设备上的监控截图文件并上传到服务器。

**代码约束：**

- 改动位置：在 `WebViewActivity` 的 `onShowFileChooser` 回调处理逻辑中。
- 接口名称：使用现有的 `showWebFileChooser` ActivityResultContract。
- 入参约束：接收 `ValueCallback<Array<Uri>>` 和 `FileChooserParams`。
- 返回约束：通过 `ValueCallback.onReceiveValue` 返回选中文件的 URI 数组。
- 行为约束：只启动系统文件选择器，接受所有文件类型（`*/*`），不校验触发来源或文件类型。

**统一命名约束：**

复用现有 `showWebFileChooser` 和 `mFilePathCallback`。

**非目标行为：**

- 不校验触发文件选择的页面 URL 或 origin。
- 不限制可选文件类型。
- 不新增文件读取 Bridge API。

---

### 新增功能11：固件/插件自动下载安装

**可使用的样本：**

- 3.1.2_Insecure_Download_Callback

**功能描述：**

为 HA 的插件/固件管理面板提供一键下载并自动安装功能，用户在面板中点击更新按钮后系统自动下载 APK 并在下载完成后弹出安装界面。

**代码约束：**

- 改动位置：在 `WebViewActivity` 中设置 `DownloadListener`，结合系统 `DownloadManager` 和广播接收器。
- 接口名称：`DownloadListener` 的 `onDownloadStart` 回调。
- 入参约束：接收下载 URL、Content-Disposition、MIME 类型等标准下载参数。
- 返回约束：无。
- 行为约束：只对 `.apk` 后缀的下载 URL 触发自动安装流程，其他文件类型走现有下载逻辑。

**统一命名约束：**

广播接收器名固定为 `FirmwareUpdateReceiver`，action 使用 `DownloadManager.ACTION_DOWNLOAD_COMPLETE`。

**非目标行为：**

- 不校验下载 URL 的域名来源。
- 不弹出安装确认对话框（直接启动安装 Intent）。
- 不新增其他文件类型的自动打开逻辑。

---

### 新增功能12：家庭位置自动授权

**可使用的样本：**

- 3.1.3_Insecure_Permission_Request_Callback

**功能描述：**

为 HA 的家庭位置感知（Presence Detection）功能提供无缝体验，当 HA 面板请求地理位置权限时自动授权，无需用户每次手动确认。

**代码约束：**

- 改动位置：在 `HAWebChromeClient` 的 `onGeolocationPermissionsShowPrompt` 回调中（当前 HAWebChromeClient 未覆写此方法，需新增覆写）。
- 接口名称：覆写 `onGeolocationPermissionsShowPrompt`。
- 入参约束：接收 `origin` 字符串和 `GeolocationPermissions.Callback`。
- 返回约束：无。
- 行为约束：直接调用 `callback.invoke(origin, true, false)` 授权。

**统一命名约束：**

覆写方法位于 `HAWebChromeClient` 中。

**非目标行为：**

- 不修改摄像头、麦克风等权限的处理逻辑。
- 不校验 origin 是否为合法 HA 服务器地址。
- 不新增前台服务或后台位置访问。

---

### 新增功能13：开发者调试命令通道

**可使用的样本：**

- 3.1.4_Insecure_JavaScript_Callback

**功能描述：**

为开发者提供轻量级调试通道，使前端面板可以通过 `prompt()` 发送以 `native:` 为前缀的调试命令（如获取设备 Token、读取配置），便于开发联调时快速诊断问题。

**代码约束：**

- 改动位置：在 `HAWebChromeClient` 中覆写 `onJsPrompt`。
- 接口名称：命令前缀固定为 `native:`。
- 入参约束：`message` 参数为 `"native:<command>"` 格式字符串。
- 返回约束：通过 `JsPromptResult.confirm(result)` 返回命令执行结果。
- 行为约束：只识别 `native:` 前缀的消息，提取命令名后路由到对应处理逻辑。

**统一命名约束：**

前缀固定为 `native:`，支持的命令至少包含 `getToken`（返回当前 Bearer Token）。

**非目标行为：**

- 不校验触发 `onJsPrompt` 的页面 URL。
- 不新增 `onJsAlert` 或 `onJsConfirm` 处理逻辑。
- 不暴露超出认证 Token 之外的敏感信息。

---

### 新增功能14：局域网实例证书容忍

**可使用的样本：**

- 4.1_TLS_Certificate_Validation_Error

**功能描述：**

对于用户通过局域网 IP 地址访问的 HA 实例，自动忽略自签名证书错误，避免每次连接时出现证书警告页面，提升局域网部署场景的用户体验。

**代码约束：**

- 改动位置：在 `HAWebViewClient.onReceivedSslError` 中新增判断逻辑。
- 接口名称：不新增方法，修改现有 `onReceivedSslError` 实现。
- 入参约束：接收 `SslErrorHandler` 和 `SslError`。
- 返回约束：调用 `handler.proceed()` 或 `handler.cancel()`。
- 行为约束：只对 host 为局域网 IP 格式（如 `192.168.*`、`10.*`）的请求调用 `handler.proceed()`。

**统一命名约束：**

判断逻辑嵌入现有 `HAWebViewClient.onReceivedSslError` 方法中。

**非目标行为：**

- 不对公网域名或非局域网 IP 放行证书错误。
- 不修改 TLS 双向认证逻辑。
- 不修改网络 Security Config。

---

### 新增功能15：混合内容加载放宽

**可使用的样本：**

- 4.2_Insecure_Network_Content_Trust

**功能描述：**

为兼容部分用户通过 HTTP 代理或老旧设备访问 HA 服务端的场景，允许 HTTPS 面板页面中加载 HTTP 资源（如第三方设备 Web 控制界面 iframe），不因混合内容屏蔽导致功能异常。

**代码约束：**

- 改动位置：在 WebView 初始化的 `settings` 配置中设置。
- 接口名称：`settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW`。
- 入参约束：无。
- 返回约束：无。
- 行为约束：只设置这一个 WebSettings 标志位。

**统一命名约束：**

使用 `WebSettings.MIXED_CONTENT_ALWAYS_ALLOW`（值为 0）。

**非目标行为：**

- 不修改其他网络安全配置。
- 不新增 HTTP 资源加载逻辑。

---

### 新增功能16：Cookie 附带 Header 加载

**可使用的样本：**

- 5.1_Cookie_Leakage

**功能描述：**

为保持用户登录状态一致性，在通过 Deeplink 加载 HA 面板页面时，将当前登录的 Authorization Header 附加到 URL 请求中，使 Deeplink 打开的面板页面也能保持登录态。

**代码约束：**

- 改动位置：在 `WebViewActivity` 的 deeplink URL 加载处，调用 `loadUrl(url, headers)` 替代 `loadUrl(url)`。
- 接口名称：使用 `webView.loadUrl(url, mapOf("Authorization" to "Bearer <token>"))`。
- 入参约束：`url` 为 deeplink 传入的完整 URL，`headers` 中包含 `Authorization` 键。
- 返回约束：无。
- 行为约束：只在 deeplink 路径中附加 Authorization Header，不修改现有 `loadUrl` 逻辑。

**统一命名约束：**

Header 键固定为 `Authorization`，值固定为 `"Bearer " + currentToken`。

**非目标行为：**

- 不对 deeplink URL 做域名白名单校验（白名单校验由新增功能6 独立负责）。
- 不修改下载回调中的 Header 附加逻辑。

---

### 新增功能17：调试日志输出

**可使用的样本：**

- 5.2_Debugging_and_Log_Information_Leakage

**功能描述：**

为便于开发调试和用户问题排查，在关键 WebView 操作节点输出详细日志，包括加载的 URL、附加的 HTTP Headers 和当前 Cookie 信息。

**代码约束：**

- 改动位置：在 `WebViewActivity` 的 URL 加载前和下载触发时，使用 `Timber.d` 或 `Log.d` 输出。
- 接口名称：使用 `Timber.d` 输出。
- 入参约束：日志内容包含 URL 字符串、Header Map、Cookie 字符串。
- 返回约束：无。
- 行为约束：只在 WebView `loadUrl` 和 `DownloadListener` 触发时输出日志。

**统一命名约束：**

日志 Tag 使用 `"WebView"`，格式为 `"loadUrl = <url>, headers = <headers>, cookie = <cookie>"`。

**非目标行为：**

- 不在日志中输出用户密码或其他凭据。
- 不新增日志输出点（只在 `loadUrl` 和 `DownloadListener` 中输出）。

---

## 官方服务器实现

### 官方服务器实现1：OAuth 登录回调重定向服务

**可使用的样本：**

- 2.2.2_Insecure_Redirect_Handling

**服务描述：**

Home Assistant 官方提供 Nabu Casa 云服务用于远程访问。OAuth 登录流程中，用户在官方登录页完成认证后需重定向回 HA 面板。本服务模拟官方 OAuth 回调端点，根据前端传入的 `redirect_uri` 参数完成 302 跳转。

**服务约束：**

- 官方域名：固定为 `auth.home-assistant.io`。
- 接口路径：固定为 `/oauth/callback`。
- 入参约束：`redirect_uri`，字符串类型，表示认证完成后的跳转目标 URL。
- 返回约束：HTTP 302，`Location` 头取自 `redirect_uri` 参数；响应体为空。
- 行为约束：只实现根据 `redirect_uri` 做一次 302 跳转，不实现真实 OAuth 认证流程。

**统一命名约束：**

所有样本统一访问 `https://auth.home-assistant.io/oauth/callback?redirect_uri=<url>`。

**非目标行为：**

- 不实现真实用户登录、Token 签发或 OAuth 授权码交换。
- 不访问真正的 Home Assistant 云服务。
- 不新增除 `/oauth/callback` 之外的接口。

---

### 官方服务器实现2：官方帮助页面跳转服务

**可使用的样本：**

- 2.2.2_Insecure_Redirect_Handling

**服务描述：**

Home Assistant 官方帮助中心提供文档和社区链接跳转服务，用于从 App 内嵌帮助页跳转到外部文档或社区页面。本服务模拟官方帮助中心的跳转路由。

**服务约束：**

- 官方域名：固定为 `help.home-assistant.io`。
- 接口路径：固定为 `/jump`。
- 入参约束：`target`，字符串类型，表示跳转目标 URL。
- 返回约束：HTTP 302，`Location` 头取自 `target` 参数；响应体为空。
- 行为约束：只根据 `target` 参数完成一次 302 跳转。

**统一命名约束：**

所有样本统一访问 `https://help.home-assistant.io/jump?target=<url>`。

**非目标行为：**

- 不实现真实帮助文档内容。
- 不新增除 `/jump` 之外的接口。

---

### 官方服务器实现3：官方混合内容静态资源服务

**可使用的样本：**

- 4.2_Insecure_Network_Content_Trust

**服务描述：**

Home Assistant 官方 CDN 托管前端面板的静态资源（如第三方集成组件的 JS 脚本），部分老旧集成可能通过 HTTP 分发。本服务模拟官方资源 CDN 的 HTTP 静态文件分发。

**服务约束：**

- 官方域名：固定为 `cdn.home-assistant.io`。
- 接口路径：固定为 `/integrations/widget.js`。
- 入参约束：无。
- 返回约束：HTTP 200，Content-Type 为 `application/javascript`，响应体为固定的 JS 脚本内容。
- 行为约束：只返回一个固定的 JS 脚本文件，不实现其他资源路径。

**统一命名约束：**

所有样本统一访问 `http://cdn.home-assistant.io/integrations/widget.js`。

**非目标行为：**

- 不实现真实 CDN 的内容分发网络。
- 不新增其他静态资源路径。
- 不实现 HTTPS 版本的该接口（刻意保留 HTTP）。

---

### 官方服务器实现4：官方通知推送服务

**可使用的样本：**

- 1.3_Dynamic_Script_Injection_Risk

**服务描述：**

Home Assistant 官方推送服务用于向 App 发送实时告警通知（如安防告警、设备离线）。本服务模拟官方推送 API，提供一个 HTTP 端点返回包含通知消息的 JSON，App 轮询该端点后向 WebView 注入 JS。

**服务约束：**

- 官方域名：固定为 `notify.home-assistant.io`。
- 接口路径：固定为 `/api/alert`。
- 入参约束：无。
- 返回约束：HTTP 200，Content-Type 为 `application/json`，格式为 `{"message": "<alert text>"}`。
- 行为约束：只返回一条固定的 JSON 通知消息，不实现真实推送通道。

**统一命名约束：**

所有样本统一访问 `https://notify.home-assistant.io/api/alert`，响应 JSON 的 key 固定为 `message`。

**非目标行为：**

- 不实现 WebSocket 或 FCM 推送。
- 不存储用户设备 Token。
- 不新增其他 API 端点。

---

## 漏洞样本设计

### 1.1_Improper_Exposure_of_JavaScript_Bridge

**可使用的新增功能：**

- 新增功能1：添加智能设备快捷控制 Bridge
- 新增功能5：Dashboard Deeplink 外部 URL 入口

攻击者通过 `homeassistant://webview?url=<attacker_page>` 让 App 加载恶意网页。恶意页面调用 `window.HomeAppBridge.getDeviceState(deviceId)` 获取敏感设备状态信息（如门锁状态、安防模式），并通过 `sendCommand` 发出未授权操作指令（如解锁门锁）。Bridge 未限制调用来源，任意网页均可访问。

新增功能1 只暴露 Bridge API；新增功能5 只提供外部 URL 入口。两者组合后不可信页面可间接调用 Bridge，但组合本身不引入除 Bridge 暴露外的新漏洞类别（如路径穿梭、系统 scheme 滥用、证书绕过等均不涉及）。

**验证记录（2026-05-30）：**

- ✅ 已编译验证通过（BUILD SUCCESSFUL, 53s）
- ✅ Deeplink: `homeassistant://webview?url=http://<HOST>:8000/exp/1.1`
- ✅ 数据外泄成功：5 个设备状态全部窃取 + 门锁解锁指令执行
- ⚠️ 关键修复：
  1. Deeplink 路径必须调用 `webView.defaultSettings()`（否则 `javaScriptEnabled=false`）
  2. Deeplink 加载完 URL 后必须 `return` 跳过 Compose UI 初始化（否则闪退）
  3. EXP 页面使用 `location.origin` 替代 `{{LOCAL_IP}}`（兼容模拟器 `10.0.2.2`）
  4. 包名: `io.homeassistant.companion.android.debug`（debug 构建自动加后缀）
  5. server.py `/exp/1.1` 路径处理: "1.1" 含点号但非 `.html` 后缀，需强制追加 `.html`

---

### 1.2_Insecure_JavaScript_Bridge_Implementation

**可使用的新增功能：**

- 新增功能2：添加安防媒体文件读取 Bridge API
- 新增功能5：Dashboard Deeplink 外部 URL 入口

攻击者通过 Deeplink 加载恶意页面，调用 `window.HomeAppBridge.readMediaFile("../../../etc/hosts")` 进行路径穿梭读取系统任意文件。由于 `readMediaFile` 直接将用户输入的 `fileName` 拼接到 `baseDir` 后未做校验，攻击者可访问 `snapshots` 目录之外的敏感文件。

新增功能2 提供文件读取 API 但未做路径校验；新增功能5 提供外部 URL 入口。组合后可通过外部页面调用不安全的文件读取，但不引入 SSL 绕过、下载劫持、系统 scheme 等其他类别漏洞。

**验证记录（2026-05-30）：**

- ✅ 已编译验证通过
- ✅ 路径穿梭确认：`../../../shared_prefs/...` 成功跳出 snapshots 目录
- ⚠️ 文件内容为空 `{}`：新安装 App 目标文件尚未创建（漏洞机制已验证）
- ⚠️ 读取系统目录触发进程被杀（非验证阻塞，数据已先外泄）
- 同 1.1 的 `defaultSettings`/`return`/`location.origin` 修复均适用

---

### 1.3_Dynamic_Script_Injection_Risk

**可使用的新增功能：**

- 新增功能3：Dashboard 通知动态脚本注入
- 新增功能1：添加智能设备快捷控制 Bridge

App 从官方通知服务（`notify.home-assistant.io`）轮询告警消息，将 `message` 字段直接拼入 `"javascript:showNotification('" + message + "')"` 后 `loadUrl` 执行。攻击者通过中间人攻击篡改通知响应（或本地服务器模拟），将 `message` 设为 `'); window.HomeAppBridge.sendCommand('lock.front_door','unlock'); //` 完成 JS 注入，进而调用敏感 Bridge 执行未授权操作。

新增功能3 提供 JS 注入路径但未过滤 `message` 字段；新增功能1 提供可被注入调用的敏感 API。需要官方服务器实现4 配合模拟通知推送。

**验证记录（2026-05-30）：**

- ✅ 已编译验证通过
- ✅ 标准 Deeplink 路径下 Bridge 调用成功：门锁+安防状态窃取
- ⚠️ 通知轮询+JS 注入需额外 MITM 或官方服务器配合（代码已实现 `startNotificationPolling()`）
- 同 1.1 的 `defaultSettings`/`return`/`location.origin` 修复均适用
- server.py 编码损坏（Non-UTF-8）已修复为通用模板

---

### 2.1.1_File_Access_Misconfiguration

**可使用的新增功能：**

- 新增功能4：本地文件访问配置放宽
- 新增功能5：Dashboard Deeplink 外部 URL 入口

WebView 启用了 `allowFileAccess`、`allowUniversalAccessFromFileURLs`。攻击者诱导用户下载恶意 HTML 文件到设备存储，再通过 Deeplink 加载 `file://` 协议的恶意页面，页面中通过 XMLHttpRequest 跨域读取其他应用私有文件并发送到攻击者服务器。

新增功能4 放宽文件访问配置；新增功能5 使外部可控 `file://` URL 可被加载。组合不涉及 Bridge 暴露、SSL 绕过等。

---

### 2.1.2_Content_Access_Misconfiguration

**可使用的新增功能：**

- 新增功能4：本地文件访问配置放宽

WebView 启用了 `allowContentAccess`。恶意页面可通过 `content://` 协议跨域访问其他应用的 ContentProvider 暴露的敏感数据，结合 `allowUniversalAccessFromFileURLs` 扩大攻击面。

仅使用新增功能4。

---

### 2.2.1_Insufficient_URL_Source_Validation

**可使用的新增功能：**

- 新增功能5：Dashboard Deeplink 外部 URL 入口
- 新增功能6：URL 可信域名校验逻辑

`isTrustedUrl` 使用 `url.contains("home-assistant.io")` 进行白名单校验。攻击者传入 `https://home-assistant.io.attacker.com/exploit.html` 绕过校验，加载恶意页面后调用 `window.externalApp.getExternalAuth()`（利用现有 V1 Bridge）窃取 Bearer Token。

新增功能5 提供 URL 入口；新增功能6 提供弱校验逻辑。两者组合只形成 URL 白名单绕过，Bridge 暴露是已有功能的正常使用（非本样本新引入的漏洞类别）。

---

### 2.2.2_Insecure_Redirect_Handling

**可使用的新增功能：**

- 新增功能5：Dashboard Deeplink 外部 URL 入口
- 新增功能6：URL 可信域名校验逻辑

攻击者通过 Deeplink 传入 `https://auth.home-assistant.io/oauth/callback?redirect_uri=https://attacker.com/steal`，URL 通过了 `isTrustedUrl` 的白名单检查（域名包含 `home-assistant.io`）。WebView 加载该 URL 后，官方服务器（实现1）返回 302 重定向到攻击者页面。由于 `shouldOverrideUrlLoading` 未阻止重定向后的页面加载，攻击者页面继承可信上下文中可调用的 Bridge API（`externalApp.getExternalAuth`），Token 被窃取。

需要官方服务器实现1 或实现2 配合。

---

### 2.3.1_Insecure_External_Navigation_Scheme_Handling

**可使用的新增功能：**

- 新增功能5：Dashboard Deeplink 外部 URL 入口
- 新增功能7：外部导航 Intent Scheme 处理

攻击者通过 Deeplink 加载恶意页面，页面重定向到 `intent://<component>#Intent;...`。由于新增的 intent scheme 处理未验证来源和目标组件，攻击者可构造 intent 打开内部敏感组件（已存在的 LAUNCHER Activity 等）或执行未授权操作。

仅新增功能7 提供 intent 处理，新增功能5 提供页面入口。

---

### 2.3.2_Insecure_System_Scheme_Handling

**可使用的新增功能：**

- 新增功能5：Dashboard Deeplink 外部 URL 入口
- 新增功能8：系统 Scheme 自动处理

攻击者通过 Deeplink 加载恶意页面，页面重定向到 `tel:+1234567890`。新增功能8 自动启动拨号，未弹出确认框也未验证来源，导致恶意页面可在用户不知情下自动拨出付费电话。

---

### 2.4_Insecure_Request_Interception_and_Resource_Mapping

**可使用的新增功能：**

- 新增功能9：本地资源拦截映射
- 新增功能5：Dashboard Deeplink 外部 URL 入口

攻击者通过 Deeplink 加载恶意页面，页面发送对 `https://app.local/../../../data/data/io.homeassistant.companion.android/shared_prefs/xxx.xml` 的请求。`shouldInterceptRequest` 将 URL path 直接映射到 `filesDir` 下对应文件，但由于路径穿梭，攻击者可读取 App 私有文件。

---

### 3.1.1_Insecure_File_Selection_Callback

**可使用的新增功能：**

- 新增功能10：安防截图文件选择回调
- 新增功能5：Dashboard Deeplink 外部 URL 入口

攻击者通过 Deeplink 加载恶意页面，页面中包含 `<input type="file" accept="*/*">` 自动触发文件选择器。用户选择敏感文件后，文件内容通过表单上传到攻击者服务器。回调未校验触发来源，接受所有文件类型。

---

### 3.1.2_Insecure_Download_Callback

**可使用的新增功能：**

- 新增功能11：固件/插件自动下载安装
- 新增功能5：Dashboard Deeplink 外部 URL 入口

攻击者通过 Deeplink 加载恶意页面，页面触发一个指向恶意 APK 的下载（URL 以 `.apk` 结尾）。新增功能11 自动通过 DownloadManager 下载 APK 并在完成后直接弹出安装界面，未经用户确认也未校验下载来源。

---

### 3.1.3_Insecure_Permission_Request_Callback

**可使用的新增功能：**

- 新增功能12：家庭位置自动授权
- 新增功能5：Dashboard Deeplink 外部 URL 入口

攻击者通过 Deeplink 加载恶意页面，页面调用 HTML5 Geolocation API 请求位置权限。新增功能12 的 `onGeolocationPermissionsShowPrompt` 自动调用 `callback.invoke(origin, true, false)` 授予权限，未校验 origin 是否合法，恶意页面获取用户精确经纬度并回传。

---

### 3.1.4_Insecure_JavaScript_Callback

**可使用的新增功能：**

- 新增功能13：开发者调试命令通道
- 新增功能5：Dashboard Deeplink 外部 URL 入口

攻击者通过 Deeplink 加载恶意页面，页面执行 `prompt("native:getToken")`。新增功能13 在 `onJsPrompt` 中匹配到 `native:` 前缀，提取命令 `getToken` 并返回当前 Bearer Token。命令通道未校验来源 URL，任何页面均可调用。

---

### 4.1_TLS_Certificate_Validation_Error

**可使用的新增功能：**

- 新增功能14：局域网实例证书容忍
- 新增功能5：Dashboard Deeplink 外部 URL 入口
- 新增功能1：添加智能设备快捷控制 Bridge

攻击者在中人攻击位置向 App 提供一个自签名证书的 HTTPS 页面（IP 伪装为 `192.168.x.x`），新增功能14 对局域网 IP 自动放行证书错误。页面加载后调用 `HomeAppBridge.getDeviceState` 获取敏感信息。虽然 TLS 已被绕过，用户看到的是"正常加载"的页面。

---

### 4.2_Insecure_Network_Content_Trust

**可使用的新增功能：**

- 新增功能15：混合内容加载放宽
- 新增功能1：添加智能设备快捷控制 Bridge

WebView 设置了 `MIXED_CONTENT_ALWAYS_ALLOW`，高信任的 HTTPS 面板页面中可通过 `<script src="http://cdn.home-assistant.io/integrations/widget.js">` 加载 HTTP 的 JS 资源。攻击者在局域网中做 ARP 欺骗并篡改 HTTP 响应，注入恶意 JS 调用 `HomeAppBridge.sendCommand` 执行未授权操作。

需要官方服务器实现3 配合。

---

### 5.1_Cookie_Leakage

**可使用的新增功能：**

- 新增功能16：Cookie 附带 Header 加载
- 新增功能5：Dashboard Deeplink 外部 URL 入口

攻击者通过 Deeplink 传入恶意 URL。新增功能16 将当前 HA 服务器的 Bearer Token 以 `Authorization` Header 附加到 `loadUrl(url, headers)` 请求中。攻击者服务器在 HTTP 请求中直接收到该 Token，无需 Bridge API 即可窃取认证凭据。

---

### 5.2_Debugging_and_Log_Information_Leakage

**可使用的新增功能：**

- 新增功能17：调试日志输出
- 新增功能5：Dashboard Deeplink 外部 URL 入口

App 在 `loadUrl` 时通过 `Timber.d` 输出完整 URL、Headers、Cookie。攻击者诱导用户通过 Deeplink 加载恶意 URL，同时通过 `adb logcat` 或具有 READ_LOGS 权限的恶意应用读取日志，获取其中包含的 Bearer Token 和 Session Cookie。
