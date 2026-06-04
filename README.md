# HA-WebviewBench

Home Assistant Android WebView 安全漏洞 Benchmark。

基于真实开源 App 构建的 WebView 漏洞样本集，每个漏洞同时提供**可攻击版本（vuln）**和**安全修复版本（fix）**，用于评估 SAST/DAST 工具和 AI 代码审计模型对 WebView 安全问题的检测能力。

## 覆盖 App

| App | 版本 | 漏洞样本数 | 状态 |
|-----|------|-----------|------|
| [Home Assistant Android](https://github.com/home-assistant/android) | 2026.5.2 | 18 vuln / 17 fix | ✅ 完成 |
| [Mihon App](https://github.com/mihonapp/mihon) | v0.19.9 | 13 vuln | 🚧 进行中 |

## 漏洞分类

涵盖 5 大类 WebView 安全风险：

| 类别 | 编号 | 说明 |
|------|------|------|
| **JS 交互** | 1.1–1.3 | Bridge 暴露、参数注入、动态脚本注入 |
| **资源访问控制** | 2.1–2.4 | 文件/Content 访问、URL 校验绕过、重定向、Scheme 注入、资源拦截 |
| **事件回调** | 3.1–3.4 | 文件选择、下载、权限请求、JS 对话框回调 |
| **网络信任** | 4.1–4.2 | TLS 证书绕过、混合内容 |
| **数据泄露** | 5.1–5.2 | Cookie/Token 泄露、日志泄露 |

完整分类说明见 [`apps/home-assistant/design.md`](apps/home-assistant/design.md)。

## 仓库结构

```
├── README.md                          # 本文件
├── applist.md                         # 候选 App 列表
├── samples/                           # Benchmark 元数据索引
│   ├── home-assistant/
│   │   └── benchmark_samples.json     # 18 个样本的分支/worktree/EXP 映射
│   └── mihon-0.19.9/
│       └── benchmark_samples.json
├── exp/                               # 漏洞利用脚本（Python 服务端 + HTML 攻击页面）
│   ├── template/server.py             # 通用 EXP 服务端模板
│   ├── home-assistant/                # 18 个 HA 样本 EXP
│   │   ├── 1.1_Improper_Exposure_of_JavaScript_Bridge/
│   │   ├── ...
│   │   └── 5.2_Debugging_and_Log_Information_Leakage/
│   └── mihon-0.19.9/                  # 13 个 Mihon 样本 EXP
│       └── ...
├── apps/                              # [gitignored] 本地 Android 源码 worktree
│   └── home-assistant/
│       ├── base/                      # Git 主仓库（master + vuln/* + fix/* 分支）
│       ├── design.md                  # 详细设计文档
│       └── samples/                   # 18 个 worktree（可切换 vuln/fix 分支）
│           ├── 1.1_Improper_Exposure_of_JavaScript_Bridge/
│           └── ...
└── apk/                               # [gitignored] 编译产物
    └── home-assistant/
        ├── vuln/                      # 17 个漏洞 APK
        └── fix/                       # 17 个修复 APK
```

## 分支说明

本仓库包含两类分支：

### 主分支
- **`main`** — 本仓库：EXP 脚本、设计文档、benchmark 索引

### 源码分支（Home Assistant Android base 仓库）
- **`master`** — 干净基础源码（未修改的原版 App）
- **`vuln/<id>`** — 18 个漏洞版本分支（如 `vuln/1.1_Improper_Exposure_of_JavaScript_Bridge`）
- **`fix/<id>`** — 17 个修复版本分支（如 `fix/2.2.1_Insufficient_URL_Source_Validation`）

检出对应分支即可获得该样本的完整 Android 项目源码。

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/SharkerSwag/HA-WebviewBench.git
cd HA-WebviewBench
```

### 2. 检出源码

切换到目标漏洞/修复版本的源码分支：

```bash
# 查看所有分支
git branch -a

# 检出漏洞版本
git checkout vuln/1.1_Improper_Exposure_of_JavaScript_Bridge

# 或检出修复版本
git checkout fix/1.1_Improper_Exposure_of_JavaScript_Bridge
```

### 3. 运行 EXP 服务端

```bash
cd exp/home-assistant/<sample_id>/
python server.py
# 默认监听 0.0.0.0:8000
```

### 4. 触发漏洞

通过 ADB 发送 Deeplink：

```bash
adb shell am start -a android.intent.action.VIEW \
  -d "homeassistant://webview?url=http://<HOST_IP>:8000/exp/<sample_id>"
```

## 本地开发

### Worktree 机制

本地 `apps/home-assistant/base/` 是源码 git 主仓库，`apps/home-assistant/samples/X/` 是其 git worktree。18 个样本共享同一份 `.git` 对象存储，切换分支即可在不同漏洞版本间切换：

```bash
cd apps/home-assistant/samples/1.1_Improper_Exposure_of_JavaScript_Bridge
git checkout vuln/1.1_Improper_Exposure_of_JavaScript_Bridge   # 漏洞版
git checkout fix/1.1_Improper_Exposure_of_JavaScript_Bridge    # 修复版
```

### 编译 APK

```bash
cd apps/home-assistant/samples/<sample_id>/
./gradlew assembleDebug
```

## License

本项目仅用于安全研究和教育目的。漏洞样本基于开源 App 构建，原始项目版权归各自作者所有。
