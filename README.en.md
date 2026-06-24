# BTV 🎬 Bilibili-Style Random Video Player

[![Docker](https://img.shields.io/docker/pulls/lzylipu/btv)](https://hub.docker.com/r/lzylipu/btv)
[![License](https://img.shields.io/github/license/lzylipu/btv)](./LICENSE)

Self-hosted, zero-config, Bilibili-inspired dark-theme short video player. Local mounts + remote API mix, mobile gestures & PC keyboard dual-mode controls.

**English | [中文](./README.md)**

---

## ✨ Features

- 🎨 **Bilibili-Inspired** — Dark theme + DS-DIGIT font, immersive playback
- 📱 **Mobile Gestures** — Left swipe to seek, right swipe for volume, draggable progress bar (portrait + fullscreen)
- ⌨️ **PC Keyboard** — Space/F/V/arrow keys, scroll wheel for volume
- 🔀 **Multi-Source** — Local directory mounts + remote APIs (302/JSON/MP4/HTML auto-detected)
- 🔄 **Smart Transcoding** — Non-H.264 videos auto-transcoded via ffmpeg; black-screen auto-retry with transcoding
- 🔒 **Secure Playback** — HMAC-signed tokens, real file paths never exposed
- 🎯 **One-Click Deploy** — Docker image `lzylipu/btv:latest`, up in 30 seconds
- 🐙 **Multi-Arch** — Supports `linux/amd64` + `linux/arm64`

---

## 🚀 Quick Start

```bash
docker run -d --name btv \
  -p 8080:8080 \
  -v btv-data:/data \
  -v /your/video/dir:/videos:ro \
  -e API_SECRET=replace-with-random-secret \
  lzylipu/btv:latest
```

Open `http://<IP>:8080` — auto-adapts to mobile and desktop.

> Config file `/data/config.yaml` is auto-generated on first start. Edit and restart to apply.

---

## 📋 Deployment

### Docker Compose (Recommended)

```bash
cp .env.example .env    # Fill in API_SECRET
docker compose up -d
```

### Docker Run

```bash
docker run -d \
  --name btv \
  --restart unless-stopped \
  --log-opt max-size=10m --log-opt max-file=3 \
  -e TZ=Asia/Shanghai \
  -e API_SECRET=replace-with-random-secret \
  -p 8080:8080 \
  -v /path/to/btv/data:/data \
  -v /path/to/videos:/videos:ro \
  lzylipu/btv:latest
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_SECRET` | ⚠️ Must change | HMAC signing key. Generate with `openssl rand -hex 16` |
| `PORT` | `8080` | Server port |
| `TZ` | — | Timezone, e.g. `Asia/Shanghai` |
| `BTV_DATA` | `/data` | Config directory (contains `config.yaml`) |

### Volume Mounts

| Mount | Description |
|-------|-------------|
| `/data` | Config persistence (`config.yaml` auto-generated here) |
| `/videos` | Local video directory (recommend `:ro` for read-only) |

> Mount sub-directories for multiple local sources: `-v /path/to/dance:/videos/dance:ro`

---

## 🎛 Configuration

Edit `/data/config.yaml`, then restart the container to apply:

```yaml
server:
  port: 8080
  secret: change-me-to-random-string

sources:
  # --- Local directories ---
  Default: /videos
  # Dance: /videos/dance
  # Funny: /videos/funny

  # --- Remote sources (no API key needed, auto-detected) ---
  Girls: https://tmini.net/api/meinv?mp4=json&r=
  Random: https://api.yujn.cn/api/zzxjj.php
```

### Remote Source Types (Auto-Detected)

| Type | Detection | Example |
|------|-----------|---------|
| 302 Redirect | `Location` header points to mp4 | `v.nrzj.vip` |
| JSON API | Returns `{url:...}` / `{video_url:...}` / `{data:{link:...}}` | `tmini.net` |
| Direct MP4 Stream | Returns `video/*` content | `api.yujn.cn` |
| HTML Page | Extracts `<video src="...">` | `tucdn.wpon.cn` |

---

## 🎮 Controls

### 📱 Mobile

| Gesture | Action |
|---------|--------|
| Drag progress bar | Seek to position (thumb drag or swipe left/right on video) |
| Swipe up/down on right | Volume adjustment |
| Swipe up / down | Next / Previous video |
| Single tap | Pause / Play |
| Double tap | Toggle fullscreen |
| 🎲 button | Random next video |

### 🖥 Desktop

| Shortcut | Action |
|----------|--------|
| `Space` | Pause / Play |
| `←` / `→` | Seek back / forward 5s |
| `↑` / `↓` | Volume + / - |
| `F` | Fullscreen |
| `V` | Mute toggle |
| Scroll wheel | Volume adjustment |
| Click progress bar | Jump to position |

---

## 🔌 API

| Endpoint | Description |
|----------|-------------|
| `GET /api/random?source=name` | Get a random video token |
| `GET /api/play?token=xxx` | Play video (local FileResponse / remote 302 redirect) |
| `GET /api/sources` | List all sources with stats |

---

## 🛠 Tech Stack

- **Backend** — Python / FastAPI / uvicorn / httpx / PyYAML
- **Frontend** — Vanilla HTML / CSS / JS (Bilibili-inspired dark theme), zero frameworks
- **CI/CD** — GitHub Actions → Docker Hub multi-arch push (amd64 + arm64)

---

## 📄 License

[MIT](./LICENSE)
