import random, os, httpx, asyncio, json
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from api.auth import resolve_token, is_remote_token, get_remote_info, register_remote
from api.config import CFG
from api.scanner import get_random, get_random_any, get_source_list, get_name, get_stats, scan_all, is_remote_source, get_remote_url

app = FastAPI(title="BTV", docs_url=None, redoc_url=None)
WEB_DIR = Path(__file__).parent.parent / "web"
http_client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)


@app.on_event("startup")
async def startup():
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


def _parse_range(range_header, total_size):
    """解析 Range 头，返回 (start, end, content_length)"""
    if not range_header or not range_header.startswith("bytes="):
        return None
    range_spec = range_header[6:]
    parts = range_spec.split("-")
    try:
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if len(parts) > 1 and parts[1] else total_size - 1
        if end >= total_size:
            end = total_size - 1
        return (start, end, end - start + 1)
    except (ValueError, IndexError):
        return None


@app.get("/api/play")
async def api_play(token: str, request: Request):
    if is_remote_token(token):
        info = get_remote_info(token)
        if not info:
            return JSONResponse({"error": "invalid remote token"}, status_code=403)
        try:
            vid_url = info["url"]
            # 直接302重定向到视频URL，让浏览器自己处理Range
            # 比StreamingResponse更稳定，不会黑屏
            from starlette.responses import RedirectResponse
            return RedirectResponse(url=vid_url, status_code=302)
        except Exception:
            return JSONResponse({"error": "remote video redirect failed"}, status_code=502)

    file_path = resolve_token(token)
    if not file_path or not os.path.isfile(file_path):
        return JSONResponse({"error": "invalid token"}, status_code=403)

    path = Path(file_path)
    mime = {".mp4": "video/mp4", ".avi": "video/x-msvideo", ".mkv": "video/x-matroska",
            ".mov": "video/quicktime", ".webm": "video/webm", ".flv": "video/x-flv"}.get(path.suffix.lower(), "video/mp4")
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
