import random, os, httpx, asyncio, json
from pathlib import Path
from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from api.auth import resolve_token, is_remote_token, get_remote_info, register_remote
from api.config import CFG
from api.scanner import get_random, get_random_any, get_source_list, get_name, get_stats, scan_all, is_remote_source, get_remote_url

app = FastAPI(title="BTV", docs_url=None, redoc_url=None)
WEB_DIR = Path(__file__).parent.parent / "web"
http_client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

FFMPEG_PATH = "/usr/bin/ffmpeg"
FFPROBE_PATH = "/usr/bin/ffprobe"


@app.on_event("startup")
async def startup():
    # Check ffmpeg availability
    has_ffmpeg = os.path.isfile(FFMPEG_PATH) and os.access(FFMPEG_PATH, os.X_OK)
    print(f"[btv] ffmpeg: {'available' if has_ffmpeg else 'NOT found (transcoding disabled)'}")
    scan_all()
    stats = get_stats()
    print(f"[btv] Ready: {stats['local_total']} local, {stats['remote_count']} remote sources")


@app.on_event("shutdown")
async def shutdown():
    await http_client.aclose()


def _parse_remote_response(data, resp):
    """从远程API响应中提取视频URL和名称，兼容多种格式"""
    if isinstance(data, dict):
        video_url = (data.get("video_url") or data.get("url")
                     or data.get("data", {}).get("url", "")
                     or data.get("data", {}).get("link", ""))
        video_name = (data.get("name") or data.get("title")
                      or data.get("data", {}).get("title", "unknown"))
        return video_url, video_name
    return "", "unknown"


async def _fetch_remote(remote_url):
    """请求远程视频源，兼容：302 Location跳转、JSON API、直接mp4流、HTML"""
    try:
        resp = await http_client.get(remote_url, timeout=15.0, follow_redirects=False)
        
        if resp.status_code in (301, 302, 303, 307, 308):
            location = resp.headers.get("location", "")
            if location:
                if location.startswith("//"):
                    location = "https:" + location
                token = register_remote(location, "远程视频")
                return {"token": token, "name": "远程视频", "remote": True}

        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "").lower()

        if "video" in content_type or "octet-stream" in content_type:
            video_url = str(resp.url)
            token = register_remote(video_url, "远程视频")
            return {"token": token, "name": "远程视频", "remote": True}

        for attempt in range(3):
            try:
                data = resp.json()
                video_url, video_name = _parse_remote_response(data, resp)
                if video_url:
                    token = register_remote(video_url, video_name)
                    return {"token": token, "name": video_name, "remote": True}
                import asyncio
                await asyncio.sleep(0.5)
                resp = await http_client.get(remote_url, timeout=15.0, follow_redirects=False)
                if resp.status_code in (301, 302, 303, 307, 308):
                    location = resp.headers.get("location", "")
                    if location:
                        if location.startswith("//"):
                            location = "https:" + location
                        token = register_remote(location, "远程视频")
                        return {"token": token, "name": "远程视频", "remote": True}
            except Exception:
                if attempt == 2:
                    pass

        html = resp.text
        for pat in [r'src="([^"]*\.mp4[^"]*)"', r"src='([^']*\.mp4[^']*)'"]:
            srcs = __import__("re").findall(pat, html)
            if srcs:
                video_url = srcs[0]
                if video_url.startswith("//"):
                    video_url = "https:" + video_url
                elif video_url.startswith("/"):
                    from urllib.parse import urlparse
                    parsed = urlparse(str(resp.url))
                    video_url = f"{parsed.scheme}://{parsed.netloc}{video_url}"
                token = register_remote(video_url, "热舞视频")
                return {"token": token, "name": "热舞视频", "remote": True}

        return None
    except httpx.HTTPError as e:
        print(f"[btv] Remote fetch failed: {e}")
        return None


@app.get("/api/random")
async def api_random(source: str | None = None):
    if source and is_remote_source(source):
        remote_url = get_remote_url(source)
        if remote_url:
            result = await _fetch_remote(remote_url)
            if result:
                return result
            return JSONResponse({"error": "remote fetch failed"}, status_code=502)

    all_sources = get_source_list()
    if source:
        token = get_random(source)
    else:
        remote_names = [s for s in all_sources if is_remote_source(s)]
        local_names = [s for s in all_sources if not is_remote_source(s)]
        if remote_names and (not local_names or random.random() < len(remote_names) / len(all_sources)):
            rs = random.choice(remote_names)
            remote_url = get_remote_url(rs)
            if remote_url:
                result = await _fetch_remote(remote_url)
                if result:
                    return result
        token = get_random_any()

    if not token:
        return JSONResponse({"error": "no videos"}, status_code=404)
    return {"token": token, "name": get_name(token)}


# ────────────── ffmpeg transcoding ──────────────

async def _probe_codec(source: str, is_url: bool = False) -> str | None:
    """用ffprobe检测视频编码，返回codec名。失败返回None。"""
    if not os.path.isfile(FFPROBE_PATH):
        return None
    try:
        args = [FFPROBE_PATH, "-v", "quiet", "-print_format", "json",
                "-show_streams", "-select_streams", "v:0"]
        if is_url:
            args.append("-i")
            args.append(source)
        else:
            args.append(source)
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=15)
        info = json.loads(stdout)
        codec = info.get("streams", [{}])[0].get("codec_name", "")
        return codec if codec else None
    except Exception:
        return None


async def _ffmpeg_transcode(source: str, is_url: bool = False):
    """用ffmpeg将视频实时转码为H.264 MP4流（stdout pipe）"""
    input_args = ["-i", source]
    if is_url:
        # 远程URL需要更长的超时和重连
        input_args = ["-reconnect", "1", "-reconnect_streamed", "1",
                       "-reconnect_delay_max", "5", "-i", source]
    proc = await asyncio.create_subprocess_exec(
        FFMPEG_PATH,
        *input_args,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "frag_keyframe+empty_moov",
        "-f", "mp4",
        "-",  # stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    return proc


def _needs_transcode(codec: str | None) -> bool:
    """判断编码是否需要转码。h264/hevc/av1浏览器原生支持。"""
    if not codec:
        return False
    return codec not in ("h264", "hevc", "av1", "vp8", "vp9", "av1")


# ────────────── /api/play ──────────────

@app.get("/api/play")
async def api_play(token: str, request: Request, transcode: bool = False):
    """播放视频。transcode=1 强制转码（黑屏重试时用）。"""
    if is_remote_token(token):
        info = get_remote_info(token)
        if not info:
            return JSONResponse({"error": "invalid remote token"}, status_code=403)
        vid_url = info["url"]

        if transcode:
            # 黑屏重试：检测编码+转码流
            codec = await _probe_codec(vid_url, is_url=True)
            if codec and _needs_transcode(codec):
                print(f"[btv] Transcoding remote video ({codec} -> h264): {vid_url[:60]}...")
                proc = await _ffmpeg_transcode(vid_url, is_url=True)
                return StreamingResponse(
                    content=proc.stdout,
                    media_type="video/mp4",
                    headers={"X-Transcoded": codec, "Cache-Control": "no-cache"},
                )
            # 即使不需要转码也用ffmpeg重新封包（修复编码问题）
            print(f"[btv] Re-muxing remote video via ffmpeg: {vid_url[:60]}...")
            proc = await _ffmpeg_transcode(vid_url, is_url=True)
            return StreamingResponse(
                content=proc.stdout,
                media_type="video/mp4",
                headers={"X-Transcoded": "remux", "Cache-Control": "no-cache"},
            )

        # 默认：302重定向到视频URL
        try:
            return RedirectResponse(url=vid_url, status_code=302)
        except Exception:
            return JSONResponse({"error": "remote video redirect failed"}, status_code=502)

    file_path = resolve_token(token)
    if not file_path or not os.path.isfile(file_path):
        return JSONResponse({"error": "invalid token"}, status_code=403)

    # 本地文件：检测编码，非H.264自动转码
    codec = await _probe_codec(file_path)
    if codec and _needs_transcode(codec):
        print(f"[btv] Transcoding {Path(file_path).name} ({codec} -> h264)")
        proc = await _ffmpeg_transcode(file_path)
        return StreamingResponse(
            content=proc.stdout,
            media_type="video/mp4",
            headers={"X-Transcoded": codec},
        )

    path = Path(file_path)
    mime = {".mp4": "video/mp4", ".avi": "video/x-msvideo", ".mkv": "video/x-matroska",
            ".mov": "video/quicktime", ".webm": "video/webm", ".flv": "video/x-flv"}.get(path.suffix.lower(), "video/mp4")

    # 对于本地avi/mkv/mov/flv，即使ffprobe没检测到编码问题，也尝试转码
    # 因为浏览器可能不支持容器格式
    if path.suffix.lower() in (".avi", ".mkv", ".mov", ".flv") and os.path.isfile(FFMPEG_PATH):
        print(f"[btv] Container format {path.suffix} -> transcoding {path.name}")
        proc = await _ffmpeg_transcode(file_path)
        return StreamingResponse(
            content=proc.stdout,
            media_type="video/mp4",
            headers={"X-Transcoded": path.suffix.lstrip(".")},
        )

    return FileResponse(file_path, media_type=mime)


@app.get("/api/sources")
async def api_sources():
    return {"sources": get_source_list(), "stats": get_stats()}


@app.get("/", response_class=HTMLResponse)
async def index():
    return (WEB_DIR / "index.html").read_text(encoding="utf-8")

if (WEB_DIR / "css").exists():
    app.mount("/css", StaticFiles(directory=str(WEB_DIR / "css")), name="css")
if (WEB_DIR / "img").exists():
    app.mount("/img", StaticFiles(directory=str(WEB_DIR / "img")), name="img")
