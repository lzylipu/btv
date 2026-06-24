# BTV - Lightweight Video Aggregator Player

[![Docker](https://img.shields.io/docker/pulls/lzylipu/btv)](https://hub.docker.com/r/lzylipu/btv)

Self-hosted, zero-dependency, adaptive random video player for PC/mobile.

## Features

- Adaptive UI (mobile/PC auto-detection)
- Mobile touch-drag progress bar (portrait + fullscreen)
- Gesture controls (left swipe seek, right swipe volume)
- One-click Docker deployment
- Multi-source fusion (local + remote API)
- Smart transcoding (ffmpeg)

## Quick Deploy

### Docker Run

```bash
docker run -d \
  --name btv \
  --restart unless-stopped \
  --log-opt max-size=10m --log-opt max-file=3 \
  -e TZ=Asia/Shanghai \
  -p 8080:8080 \
  -v btv-data:/data \
  -v /videos:/videos:ro \
  -e API_SECRET=$(openssl rand -hex 16) \
  lzylipu/btv:latest
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `--restart unless-stopped` | Auto-restart on crash |
| `--log-opt max-size=10m` | Max log file size |
| `-e TZ=Asia/Shanghai` | Timezone setting |
| `-v btv-data:/data` | Persistent data volume |
| `-v /videos:/videos:ro` | Video source (read-only) |
| `-e API_SECRET=...` | API secret (change it) |

## Configuration

Edit `/data/config.yaml`:

```yaml
server:
  port: 8080
  secret: change-me-to-random-string

sources:
  default: /videos
  dance: /videos/dance
  remote: https://example.com/api/videos
```

## Controls

### Mobile
- **Progress bar**: drag thumb or swipe left/right
- **Volume**: swipe up/down on right side
- Single tap: play/pause
- Double tap: fullscreen

### PC
- `Space`: play/pause
- `←`/`→`: seek ±5s
- `↑`/`↓`: volume +/-
- `F`: fullscreen
- `V`: mute
- Scroll: volume

## License

MIT
