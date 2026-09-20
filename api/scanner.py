import random
from pathlib import Path
from .config import CFG
from .auth import register_file

_source_index = {}      # name -> [file_path, ...]  本地按路径存,抽片时 register_file 换活牌
_name_index = {}        # file_path -> display_name
_remote_sources = {}    # name -> {"url": "..."}
_local_sources = {}     # name -> path
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mkv", ".mov", ".webm", ".flv"}


def scan_all():
    sources = CFG.get("sources", [])
    _source_index.clear()
    _name_index.clear()
    _remote_sources.clear()
    _local_sources.clear()

    if not sources:
        print("[btv] WARNING: No sources configured. Edit /data/config.yaml and restart.")
        return

    for src in sources:
        name = src.get("name", "未命名")
        stype = src.get("type", "local")

        if stype == "remote":
            url = src.get("url", "")
            if url:
                _remote_sources[name] = {"url": url}
                _source_index[name] = []  # remote源的token列表为空，server层动态fetch
                print(f"[btv] REMOTE {name}: {url}")
            continue

        # type=local
        path = src.get("path", "")
        p = Path(path)
        _local_sources[name] = path
        if not p.exists():
            print(f"[btv] WARNING: {path} not found ({name})")
            _source_index[name] = []
            continue
        paths = []
        for f in p.rglob("*"):
            if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS:
                fp = str(f)
                register_file(fp)
                paths.append(fp)
                _name_index[fp] = f.stem
        _source_index[name] = paths
        print(f"[btv] LOCAL {name}: {len(paths)} videos from {path}")


def is_remote_source(name):
    return name in _remote_sources


def is_local_source(name):
    return name in _local_sources


def get_remote_url(name):
    return _remote_sources.get(name, {}).get("url")


def get_source_list():
    return list(_source_index.keys())


def _live_token(file_path):
    """抽片时按路径换活牌:过期自动续,不用重启。"""
    if not file_path:
        return None
    return register_file(file_path)


def get_random(name):
    if is_remote_source(name):
        return None  # server层fetch
    paths = _source_index.get(name, [])
    return _live_token(random.choice(paths)) if paths else None


def get_random_any():
    """从所有源随机选一个视频（优先本地，可混合远程）"""
    all_sources = list(_source_index.keys())
    if not all_sources:
        return None

    local_paths = []
    for name in all_sources:
        if not is_remote_source(name):
            local_paths.extend(_source_index.get(name, []))

    if local_paths:
        return _live_token(random.choice(local_paths))
    return None


def get_name(token):
    from .auth import resolve_token, is_remote_token, get_remote_info
    if is_remote_token(token):
        info = get_remote_info(token) or {}
        return info.get("name") or "未知"
    fp = resolve_token(token)
    if fp:
        return _name_index.get(fp, Path(fp).stem)
    return _name_index.get(token, "未知")


def get_stats():
    sources = {}
    for n in sorted(_source_index.keys()):
        if is_remote_source(n):
            sources[n] = {"type": "remote", "count": -1, "url": _remote_sources[n]["url"]}
        else:
            sources[n] = {"type": "local", "count": len(_source_index.get(n, [])), "path": _local_sources.get(n, "")}
    return {
        "sources": sources,
        "local_total": sum(s["count"] for s in sources.values() if s["type"] == "local"),
        "remote_count": len(_remote_sources),
    }
