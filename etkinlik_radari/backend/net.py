"""Shared HTTP helpers: per-thread sessions, JSON-LD extraction, HTML cleanup."""
import html as _html
import json
import re
import threading

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")

_local = threading.local()


def session() -> requests.Session:
    s = getattr(_local, "s", None)
    if s is None:
        s = requests.Session()
        s.headers.update({"User-Agent": UA, "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8"})
        _local.s = s
    return s


def get(url, timeout=30, **kw) -> requests.Response:
    r = session().get(url, timeout=timeout, **kw)
    r.raise_for_status()
    return r


def get_json(url, **kw):
    return get(url, **kw).json()


def json_ld(page: str) -> list:
    out = []
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', page, re.S):
        try:
            data = json.loads(m.group(1))
        except ValueError:
            continue
        out.extend(data if isinstance(data, list) else [data])
    return out


def has_type(obj, name) -> bool:
    t = obj.get("@type") if isinstance(obj, dict) else None
    return t == name or (isinstance(t, list) and name in t)


def strip_html(s: str, limit: int = 0) -> str:
    if not s:
        return ""
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>|</p>|</h\d>|</li>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = _html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s*\n\s*", "\n", s).strip()
    if limit and len(s) > limit:
        s = s[:limit].rsplit(" ", 1)[0] + "…"
    return s
