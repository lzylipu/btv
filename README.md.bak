<div align="center">

# 📺 BTV

### ✨ 仿B站风格 · 全屏随机视频播放器 ✨

🚀 自托管 · 🐳 零配置部署 · 📱 移动端手势 · ⌨️ PC键盘操控 · 🔀 多源融合

[![Docker Pulls](https://img.shields.io/docker/pulls/lzylipu/btv?style=flat-square&logo=docker&color=blue)](https://hub.docker.com/r/lzylipu/btv)
[![License](https://img.shields.io/github/license/lzylipu/btv?style=flat-square&color=green)](./LICENSE)
[![Platform](https://img.shields.io/badge/platform-amd64%20%7C%20arm64-informational?style=flat-square&logo=linux)](https://github.com/lzylipu/btv)

**[English](./README_EN.md) | 中文**

</div>

---

## 🎯 项目简介

BTV 是一款**仿B站暗色风格**的全屏随机短视频播放器，让你像刷B站一样刷自己的视频库！🖥️

- 🏠 **本地挂载**：将 NAS / 硬盘中的视频目录挂载到容器，立刻拥有私人影院
- 🌐 **远程融合**：支持 302 跳转 / JSON API / 直播流 / HTML 页面等多种远程源自动识别
- 🔒 **安全播放**：HMAC 签名 token 机制，不暴露真实文件路径，安心分享
- 🔄 **智能转码**：非 H.264 视频自动 ffmpeg 实时转码，黑屏自动重试转码播放
- 📱 **移动端手势**：左滑调进度、右侧上下滑调音量、上下滑切视频、双击全屏
- ⌨️ **PC 键盘操控**：Space / 方向键 / F / V / 滚轮……全键盘操控无压力

---

## 🌟 功能特性

| 🎨 特性 | 📝 说明 |
|---------|--------|
| 🎭 仿B站暗色主题 | DS-DIGIT 字体 + 深色背景，沉浸式播放体验 |
| 📱 移动端手势 | 进度条拖动 / 左右滑进度 / 右侧上下滑音量 / 上下切视频 / 双击全屏 |
| ⌨️ PC 键盘操控 | Space 暂停 · ←→ 快进退 5s · ↑↓ 音量 · F 全屏 · V 静音 · 滚轮音量 |
| 🔀 多源融合 | 本地目录 + 远程 API 混合源，302 / JSON / MP4 / HTML 四种类型自动识别 |
| 🔄 智能转码 | ffmpeg 实时检测编码，非 H.264 自动转码；容器格式（AVI/MKV/MOV/FLV）自动转码 |
| 🔒 安全播放 | HMAC-SHA256 签名 token，真实路径永不暴露 |
| 🎯 一键部署 | Docker 镜像 `lzylipu/btv:latest`，30 秒上线 |
| 🐙 多架构支持 | `linux/amd64` + `linux/arm64`，NAS / 树莓派全兼容 |

---

## 🚀 快速开始

### 📦 Docker 一行命令启动

```bash
docker run -d --name btv \
  -p 8080:8080 \
  -v btv-data:/data \
  -v /你的视频目录:/videos:ro \
  -e API_SECRET=$(openssl rand -hex 16) \
  lzylipu/btv:latest
```

打开浏览器访问 `http://<IP>:8080` 🎉 手机电脑自动适配！

> 💡 配置文件 `/data/config.yaml` 首次启动自动生成，编辑后重启容器即可生效。

---

## 📋 部署详解

### 🐳 Docker Compose（推荐 👍）

```bash
# 1️⃣ 克隆仓库 & 复制环境变量
git clone https://github.com/lzylipu/btv.git
cd btv

# 2️⃣ 填写密钥
cp .env.example .env
# 编辑 .env，将 API_SECRET 替换为随机字符串
# 推荐生成方式: openssl rand -hex 16

# 3️⃣ 启动！
docker compose up -d
```

### 🐳 Docker Run

```bash
docker run -d \
  --name btv \
  --restart unless-stopped \
  --log-opt max-size=10m --log-opt max-file=3 \
  -e TZ=Asia/Shanghai \
  -e API_SECRET=your-random-secret-here \
  -p 8080:8080 \
  -v /path/to/btv/data:/data \
  -v /path/to/videos:/videos:ro \
  lzylipu/btv:latest
```

### 🔑 环境变量

| 📛 变量 | 🔧 默认值 | 📝 说明 |
|---------|----------|--------|
| `API_SECRET` | ⚠️ **必须修改** | HMAC 签名密钥，建议用 `openssl rand -hex 16` 生成 |
| `PORT` | `8080` | 服务监听端口 |
| `TZ` | — | 时区设置，如 `Asia/Shanghai` |
| `BTV_DATA` | `/data` | 数据目录（含自动生成的 `config.yaml`） |

### 📂 挂载说明

| 📁 挂载点 | 📝 说明 |
|----------|--------|
| `/data` | 配置持久化目录（`config.yaml` 自动生成于此） |
| `/videos` | 本地视频目录（建议 `:ro` 只读挂载） |

> 💡 **多目录挂载**：可挂载子目录实现分类，如 `-v /path/to/舞蹈:/videos/舞蹈:ro`

---

## 🎛️ 配置说明

编辑 `/data/config.yaml`，修改后重启容器生效：

```yaml
server:
  port: 8080
  secret: change-me-to-random-string

sources:
  # 📂 --- 本地目录（以 / 开头） ---
  默认: /videos
  # 舞蹈: /videos/舞蹈
  # 搞笑: /videos/搞笑

  # 🌐 --- 远程源（以 http 开头，无需 API Key，自动识别类型） ---
  小姐姐: https://tmini.net/api/meinv?mp4=json&r=
  随便看: https://api.yujn.cn/api/zzxjj.php
```

> 📖 更多示例参见 [`config.example.yaml`](./config.example.yaml)

### 🌐 远程源自动识别

BTV 会自动检测远程 API 的响应类型，无需手动配置：

| 🔖 类型 | 🔍 识别方式 | 🌍 示例站点 |
|---------|-----------|------------|
| 🔀 302 跳转 | `Location` 响应头指向 mp4 | `v.nrzj.vip` |
| 📄 JSON API | 返回 `{url:...}` / `{video_url:...}` / `{data:{link:...}}` | `tmini.net` |
| 🎬 直接 MP4 流 | 返回 `video/*` Content-Type | `api.yujn.cn` |
| 📝 HTML 页面 | 提取 `<video src="...">` 标签 | `tucdn.wpon.cn` |

---

## 🎮 操作指南

### 📱 移动端手势

| 👆 操作 | ⚡ 功能 |
|---------|--------|
| 进度条拖动 / 左右滑动视频区域 | 跳转播放进度 |
| 右侧上下滑动 | 调节音量 🔊 |
| 上滑 / 下滑 | 下一个 / 上一个视频 |
| 单击 | 暂停 / 播放 ⏯️ |
| 双击 | 全屏切换 🖥️ |
| 🎲 按钮 | 随机换视频 |

### 🖥️ PC 键盘快捷键

| ⌨️ 快捷键 | ⚡ 功能 |
|-----------|--------|
| `Space` | 暂停 / 播放 ⏯️ |
| `←` / `→` | 快退 / 快进 5s ⏪⏩ |
| `↑` / `↓` | 音量增大 / 减小 🔊🔉 |
| `F` | 全屏 🖥️ |
| `V` | 静音开关 🔇 |
| 滚轮 | 音量调节 🔊 |
| 点击进度条 | 跳转播放位置 |

---

## 🔌 API 接口

| 🛣️ 接口 | 📝 说明 | 📋 参数 |
|---------|--------|--------|
| `GET /api/random` | 获取随机视频 token | `source`（可选）：指定源名称 |
| `GET /api/play` | 播放视频 | `token`：视频 token；`transcode`（可选）：强制转码 |
| `GET /api/sources` | 列出所有源及统计信息 | — |

### 📖 API 使用流程

1. 调用 `/api/random` 获取带有 HMAC 签名的播放 token
2. 使用 `/api/play?token=xxx` 播放视频
3. 本地视频返回 `FileResponse` / 远程视频返回 `302` 重定向
4. 若播放黑屏，前端自动重试 `transcode=1` 参数进行 ffmpeg 转码播放

---

## 📁 项目结构

```
btv/
├── 📂 api/                        # 🔧 后端 Python 模块
│   ├── 📄 __init__.py             # 包初始化
│   ├── 📄 auth.py                 # 🔒 HMAC token 生成与验证
│   ├── 📄 config.py               # ⚙️ 配置加载（YAML + 环境变量）
│   ├── 📄 scanner.py              # 🔍 视频源扫描与索引
│   └── 📄 server.py               # 🚀 FastAPI 主服务（路由 + 转码逻辑）
├── 📂 web/                        # 🎨 前端静态资源
│   ├── 📄 index.html              # 📺 主页面（仿B站暗色主题 + 手势/键盘控制）
│   ├── 📂 css/
│   │   └── 📄 style.css           # 🎭 样式表
│   └── 📂 img/
│       ├── 🖼️ favicon.ico          # 网站图标
│       └── 🖼️ logo.png            # Logo 图片
├── 📂 .github/workflows/          # 🤖 CI/CD
│   └── 📄 docker.yml              # 🐳 Docker 多架构构建推送
├── 🐳 Dockerfile                  # 容器构建文件（Python 3.12 + ffmpeg）
├── 🐳 docker-compose.yml         # Docker Compose 编排
├── ⚙️ config.example.yaml         # 配置文件示例
├── 🔑 .env.example                # 环境变量示例
├── 📦 pyproject.toml              # Python 项目配置
├── 📄 .dockerignore               # Docker 构建排除规则
├── 📄 .gitignore                  # Git 忽略规则
├── 📄 LICENSE                     # MIT 许可证
├── 📄 README.md                   # 中文文档（本文件）
└── 📄 README_EN.md                # English Documentation
```

### 🔑 核心模块说明

| 📄 文件 | 📝 功能 |
|---------|--------|
| [`api/server.py`](./api/server.py) | FastAPI 主应用：定义路由 `/api/random`、`/api/play`、`/api/sources`，实现远程源获取、ffmpeg 转码、视频播放 |
| [`api/auth.py`](./api/auth.py) | Token 机制：HMAC-SHA256 签名生成与验证、本地/远程 token 注册与解析 |
| [`api/config.py`](./api/config.py) | 配置管理：加载 `config.yaml`，自动检测源类型（本地/远程），支持环境变量覆盖 |
| [`api/scanner.py`](./api/scanner.py) | 视频索引：递归扫描本地目录，识别视频文件（mp4/avi/mkv/mov/webm/flv），建立随机索引 |
| [`web/index.html`](./web/index.html) | 前端页面：仿B站暗色 UI、移动端手势识别、PC 键盘监听、视频播放器控制逻辑 |

---

## 🛠️ 技术栈

| 🖥️ 层级 | 🔧 技术 |
|---------|--------|
| 🐍 后端 | Python 3.12 · FastAPI · uvicorn · httpx · PyYAML |
| 🎬 转码 | ffmpeg（容器内置，非 H.264 自动转码） |
| 🎨 前端 | 原生 HTML / CSS / JS（零框架，仿B站暗色主题） |
| 🐳 部署 | Docker · Docker Compose · GitHub Actions CI/CD |
| 🏗️ 架构 | `linux/amd64` + `linux/arm64` 多平台支持 |

---

## 🤝 贡献与反馈

- 🐛 发现 Bug？[提交 Issue](https://github.com/lzylipu/btv/issues)
- 💡 有建议？[发起 Discussion](https://github.com/lzylipu/btv/discussions)
- 🛠️ 想贡献代码？欢迎提交 Pull Request！

---

## 📄 许可证

本项目基于 [MIT License](./LICENSE) 开源，自由使用、修改和分发 🎉

---

<div align="center">

**⭐ 如果 BTV 对你有帮助，给个 Star 吧！⭐**

Made with ❤️ by [lzylipu](https://github.com/lzylipu)

</div>
