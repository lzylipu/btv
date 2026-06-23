# BTV - 轻量化短视频聚合播放器

[![Docker](https://img.shields.io/docker/pulls/lzylipu/btv)](https://hub.docker.com/r/lzylipu/btv)

自托管、零依赖、自适应 PC/手机的随机视频播放器。

## 特性

- 自适应 UI（手机/PC 自动适配）
- **移动端进度条支持触摸拖动**（竖屏/全屏均可）
- 手势控制（左滑进度，右滑音量）
- 一键 Docker 部署
- 多源融合（本地 + 远程 API）
- 智能转码（ffmpeg）

## 快速部署

### Docker Run（标准命令）

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

### Docker Compose

```yaml
version: "3.8"

services:
  btv:
    image: lzylipu/btv:latest
    container_name: btv
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    environment:
      - TZ=Asia/Shanghai
      - API_SECRET=your-secret-key
      - PORT=8080
    ports:
      - "8080:8080"
    volumes:
      - btv-data:/data
      - /srv/videos:/videos:ro

volumes:
  btv-data:
```

### 参数说明

| 参数 | 说明 | 为什么需要 |
|------|------|-----------|
| `--restart unless-stopped` | 容器异常自动重启 | 生产环境必选 |
| `--log-opt max-size=10m` | 单日志文件最大 10MB | 防止日志撑爆磁盘 |
| `--log-opt max-file=3` | 保留 3 个日志文件 | 总日志量 30MB |
| `-e TZ=Asia/Shanghai` | 时区设置 | 时间显示一致 |
| `-v btv-data:/data` | 持久化配置 | 数据不丢失 |
| `-v /videos:/videos:ro` | 视频源（只读） | 更安全 |
| `-e API_SECRET=...` | API 密钥 | 必须修改 |

## 配置

编辑 `/data/config.yaml`：

```yaml
server:
  port: 8080
  secret: change-me-to-random-string

sources:
  默认：/videos
  舞蹈：/videos/舞蹈
  小姐姐：https://tmini.net/api/meinv?mp4=json&r=
```

## 操作

### 移动端
- **进度条**：直接拖动进度条 thumb，或左右滑动视频区域
- **音量**：右侧区域上下滑动
- 单击：暂停/播放
- 双击：全屏

### PC 端
- `Space`：暂停
- `←`/`→`：快退/快进 5 秒
- `↑`/`↓`：音量 +/-
- `F`：全屏
- `V`：静音
- 滚轮：音量
- 点击进度条：跳转

## License

MIT
