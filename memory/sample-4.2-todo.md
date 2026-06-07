---
name: sample-4.2-todo
description: 4.2 Insecure Network Content Trust vuln/fix branches not yet written — needs to be created from scratch
metadata:
  type: project
---

4.2_Insecure_Network_Content_Trust 的 vuln 和 fix 分支尚未创建。需要根据 design.md 自行编写。

## Design requirements (from design.md)

**Vulnerability:** 新增功能15（混合内容加载放宽）+ 新增功能1（HomeAppBridge）+ 官方服务器实现3

WebView 设置 `MIXED_CONTENT_ALWAYS_ALLOW`，HTTPS 面板页面中可加载 HTTP JS 资源。攻击者 MITM 篡改 HTTP 响应注入恶意 JS 调用 `HomeAppBridge.sendCommand` 执行未授权操作。

需要：
- 新增功能15: `settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW`
- 新增功能1: 添加 HomeAppBridge（getDeviceState + sendCommand）
- 官方服务器实现3: 混合内容 CDN 服务器

**Fix approach:** Remove `MIXED_CONTENT_ALWAYS_ALLOW` or restrict to trusted domains only.

## How to apply

When we reach 4.2 in the optimization queue, refer to:
- `apps/home-assistant/design.md` for full design specification
- [[WebviewBench_sample_skill]] for the build workflow
- Previous samples (1.1, 2.1.1) as templates for vuln/fix structure

**Why:** The user confirmed 4.2 was never implemented — needs full creation, not just optimization.
