<div align="center">

# 📺 BTV

### ✨ Bilibili-Style · Fullscreen Random Video Player ✨

🚀 Self-Hosted · 🐳 Zero-Config Deploy · 📱 Mobile Gestures · ⌨️ PC Keyboard Controls · 🔀 Multi-Source Fusion

[![Docker Pulls](https://img.shields.io/docker/pulls/lzylipu/btv?style=flat-square&logo=docker&color=blue)](https://hub.docker.com/r/lzylipu/btv)
[![License](https://img.shields.io/github/license/lzylipu/btv?style=flat-square&color=green)](./LICENSE)
[![Platform](https://img.shields.io/badge/platform-amd64%20%7C%20arm64-informational?style=flat-square&logo=linux)](https://github.com/lzylipu/btv)

**English | [中文](./README.md)**

</div>

---

## 🎯 Overview

BTV is a **Bilibili-inspired dark-theme fullscreen random short video player** — browse your own video library just like scrolling Bilibili! 🖥️

- 🏠 **Local Mounts** — Mount NAS/hard drive video directories to the container, get your own private cinema instantly
- 🌐 **Remote Fusion** — Supports 302 redirect / JSON API / direct stream / HTML page auto-detection for remote sources
- 🔒 **Secure Playback** — HMAC-signed token mechanism, never exposes real file paths, safe to share
- 🔄 **Smart Transcoding** — Non-H.264 videos auto-transcoded via ffmpeg in real-time; black-screen auto-retry with transcoding
- 📱 **Mobile Gestures** — Left swipe to seek, right-side swipe for volume, swipe up/down for next/prev, double-tap for fullscreen
- ⌨️ **PC Keyboard** — Space / Arrow keys / F / V / Scroll wheel… full keyboard control

---

## 🌟 Features

| 🎨 Feature | 📝 Description |
|-----------|----------------|
| 🎭 Bilibili Dark Theme | DS-DIGIT font + dark background, immersive playback experience |
| 📱 Mobile Gestures | Progress bar drag / left-right swipe to seek / right-side swipe for volume / up-down swipe to switch / double-tap fullscreen |
| ⌨️ PC Keyboard Controls | Space pause · ←→ seek 5s · ↑↓ volume · F fullscreen · V mute · Scroll volume |
| 🔀 Multi-Source Fusion | Local directory + remote API hybrid sources, 302 / JSON / MP4 / HTML 4 types auto-detected |
| 🔄 Smart Transcoding | ffmpeg real-time codec detection, non-H.264 auto-transcode; container formats (AVI/MKV/MOV/FLV) auto-transcode |
| 🔒 Secure Playback | HMAC-SHA256 signed tokens, real paths never exposed |
| 🎯 One-Click Deploy | Docker image `lzylipu/btv:latest`, up in 30 seconds |
| 🐙 Multi-Arch Support | `linux/amd64` + `linux/arm64`, NAS / Raspberry Pi compatible |

---

## 🚀 Quick Start

### 📦 Docker One-Liner

```bash
docker run -d --name btv \
  -p 8080:8080 \
  -v btv-data:/data \
  -v /your/video/dir:/videos:ro \
  -e API_SECRET=$(openssl rand -hex 16) \
  lzylipu/btv:latest
```

Open `http://<IP>:8080` in your browser 🎉 Auto-adapts to mobile and desktop!

> 💡 Config file `/data/config.yaml` is auto-generated on first start. Edit and restart the container to apply.

---

## 📋 Deployment

### 🐳 Docker Compose (Recommended 👍)

```bash
# 1️⃣ Clone & copy environment file
git clone https://github.com/lzylipu/btv.git
cd btv

# 2️⃣ Fill in the secret
cp .env.example .env
# Edit .env, replace API_SECRET with a random string
# Recommended: openssl rand -hex 16

# 3️⃣ Start!
docker compose up -d
```

### 🐳 Docker Run

```bash
docker run -d \
  --name btv \
  --restart unless-stopped \
  --log-opt max-size=10m --log-opt max-file=3 \
  -e TZ=Asia/Shanghai \
  -e API_SECRET=your-secret-here \
  -p 8080:8080 \
  -v /path/to/btv/data:/data \
  -v /path/to/videos:/videos:ro \
  lzylipu/btv:latest
```

### 🔑 Environment Variables

| 📛 Variable | 🔧 Default | 📝 Description |
|-------------|-----------|----------------|
| `API_SECRET` | ⚠️ **Must change** | HMAC signing key. Generate with `openssl rand -hex 16` |
| `PORT` | `8080` | Server listen port |
| `TZ` | — | Timezone, e.g. `Asia/Shanghai` |
| `BTV_DATA` | `/data` | Data directory (contains auto-generated `config.yaml`) |

### 📂 Volume Mounts

| 📁 Mount | 📝 Description |
|----------|----------------|
| `/data` | Config persistence (`config.yaml` auto-generated here) |
| `/videos` | Local video directory (recommend `:ro` for read-only) |

> 💡 **Multi-directory Mount**: Mount sub-directories for categories, e.g. `-v /path/to/dance:/videos/dance:ro`

---

## 🎛️ Configuration

Edit `/data/config.yaml`, then restart the container to apply:

```yaml
server:
  port: 8080
  secret: change-me-to-random-string

sources:
  # 📂 --- Local directories (start with /) ---
  Default: /videos
  # Dance: /videos/dance
  # Funny: /videos/funny

  # 🌐 --- Remote sources (start with http, no API key needed, auto-detected) ---
  Girls: https://tmini.net/api/meinv?mp4=json&r=
  Random: https://api.yujn.cn/api/zzxjj.php
```

> 📖 See [`config.example.yaml`](./config.example.yaml) for more examples

### 🌐 Remote Source Auto-Detection

BTV automatically detects remote API response types — no manual configuration needed:

| 🔖 Type | 🔍 Detection Method | 🌍 Example Site |
|---------|---------------------|-----------------|
| 🔀 302 Redirect | `Location` header points to mp4 | `v.nrzj.vip` |
| 📄 JSON API | Returns `{url:...}` / `{video_url:...}` / `{data:{link:...}}` | `tmini.net` |
| 🎬 Direct MP4 Stream | Returns `video/*` Content-Type | `api.yujn.cn` |
| 📝 HTML Page | Extracts `<video src="...">` tag | `tucdn.wpon.cn` |

---

## 🎮 Controls

### 📱 Mobile Gestures

| 👆 Gesture | ⚡ Action |
|-----------|----------|
| Drag progress bar / swipe left-right on video | Seek playback position |
| Swipe up/down on right side | Volume adjustment 🔊 |
| Swipe up / down | Next / Previous video |
| Single tap | Pause / Play ⏯️ |
| Double tap | Toggle fullscreen 🖥️ |
| 🎲 Button | Random next video |

### 🖥️ Desktop Keyboard Shortcuts

| ⌨️ Shortcut | ⚡ Action |
|-------------|----------|
| `Space` | Pause / Play ⏯️ |
| `←` / `→` | Seek back / forward 5s ⏪⏩ |
| `↑` / `↓` | Volume up / down 🔊🔉 |
| `F` | Fullscreen 🖥️ |
| `V` | Mute toggle 🔇 |
| Scroll wheel | Volume adjustment 🔊 |
| Click progress bar | Jump to position |

---

## 🔌 API Endpoints

| 🛣️ Endpoint | 📝 Description | 📋 Parameters |
|-------------|----------------|---------------|
| `GET /api/random` | Get a random video token | `source` (optional): source name |
| `GET /api/play` | Play video | `token`: video token; `transcode` (optional): force transcoding |
| `GET /api/sources` | List all sources with stats | — |

### 📖 API Usage Flow

1. Call `/api/random` to get an HMAC-signed playback token
2. Use `/api/play?token=xxx` to play the video
3. Local videos return `FileResponse` / remote videos return `302` redirect
4. If playback shows a black screen, the frontend auto-retries with `transcode=1` for ffmpeg transcoding

---

## 📁 Project Structure

```
btv/
├── 📂 api/                        # 🔧 Backend Python modules
│   ├── 📄 __init__.py             # Package init
│   ├── 📄 auth.py                 # 🔒 HMAC token generation & validation
│   ├── 📄 config.py               # ⚙️ Config loading (YAML + env vars)
│   ├── 📄 scanner.py              # 🔍 Video source scanning & indexing
│   └── 📄 server.py               # 🚀 FastAPI main service (routes + transcoding)
├── 📂 web/                        # 🎨 Frontend static assets
│   ├── 📄 index.html              # 📺 Main page (Bilibili dark theme + gesture/keyboard)
│   ├── 📂 css/
│   │   └── 📄 style.css           # 🎭 Stylesheet
│   └── 📂 img/
│       ├── 🖼️ favicon.ico          # Favicon
│       └── 🖼️ logo.png            # Logo image
├── 📂 .github/workflows/          # 🤖 CI/CD
│   └── 📄 docker.yml              # 🐳 Docker multi-arch build & push
├── 🐳 Dockerfile                  # Container build (Python 3.12 + ffmpeg)
├── 🐳 docker-compose.yml         # Docker Compose orchestration
├── ⚙️ config.example.yaml         # Config example
├── 🔑 .env.example                # Environment variable example
├── 📦 pyproject.toml              # Python project config
├── 📄 .dockerignore               # Docker build exclusions
├── 📄 .gitignore                  # Git ignore rules
├── 📄 LICENSE                     # MIT License
├── 📄 README.md                   # Chinese Documentation
└── 📄 README_EN.md                # English Documentation (this file)
```

### 🔑 Core Modules

| 📄 File | 📝 Description |
|---------|----------------|
| [`api/server.py`](./api/server.py) | FastAPI main app: defines routes `/api/random`, `/api/play`, `/api/sources`; implements remote source fetching, ffmpeg transcoding, video playback |
| [`api/auth.py`](./api/auth.py) | Token mechanism: HMAC-SHA256 signing & validation, local/remote token registration and resolution |
| [`api/config.py`](./api/config.py) | Config management: loads `config.yaml`, auto-detects source type (local/remote), supports environment variable overrides |
| [`api/scanner.py`](./api/scanner.py) | Video indexing: recursively scans local directories, identifies video files (mp4/avi/mkv/mov/webm/flv), builds random index |
| [`web/index.html`](./web/index.html) | Frontend page: Bilibili dark UI, mobile gesture recognition, PC keyboard listener, video player control logic |

---

## 🛠️ Tech Stack

| 🖥️ Layer | 🔧 Technologies |
|----------|------------------|
| 🐍 Backend | Python 3.12 · FastAPI · uvicorn · httpx · PyYAML |
| 🎬 Transcoding | ffmpeg (built into container, auto-transcode non-H.264) |
| 🎨 Frontend | Vanilla HTML / CSS / JS (zero frameworks, Bilibili dark theme) |
| 🐳 Deployment | Docker · Docker Compose · GitHub Actions CI/CD |
| 🏗️ Architecture | `linux/amd64` + `linux/arm64` multi-platform support |

---

## 🤝 Contributing & Feedback

- 🐛 Found a bug? [Open an Issue](https://github.com/lzylipu/btv/issues)
- 💡 Have a suggestion? [Start a Discussion](https://github.com/lzylipu/btv/discussions)
- 🛠️ Want to contribute? Pull Requests are welcome!

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE) — free to use, modify, and distribute 🎉

---

<div align="center">

**⭐ If BTV helps you, give it a Star! ⭐**

Made with ❤️ by [lzylipu](https://github.com/lzylipu)

</div>
