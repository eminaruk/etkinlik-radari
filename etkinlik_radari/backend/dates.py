"""Date normalisation and free-text date range parsing (English + Turkish)."""
import re
from datetime import date, datetime, timedelta, timezone

EN_MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
TR_MONTHS = {m: i + 1 for i, m in enumerate(
    ["ocak", "şubat", "mart", "nisan", "mayıs", "haziran", "temmuz", "ağustos",
     "eylül", "ekim", "kasım", "aralık"])}


def tr_lower(s: str) -> str:
    return s.replace("İ", "i").replace("I", "ı").lower()


def norm(value) -> str | None:
    """Normalise to 'YYYY-MM-DD' (all-day) or 'YYYY-MM-DDTHH:MM:SSZ' (UTC)."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, date):
        return value.isoformat()
    else:
        s = str(value).strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
            return s
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            return None
    if dt.tzinfo is None:
        if dt.hour == dt.minute == dt.second == 0:
            return dt.date().isoformat()
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _month(word: str, lang: str):
    w = tr_lower(word)
    if lang == "tr":
        return TR_MONTHS.get(w)
    return EN_MONTHS.get(w[:3]) if len(w) >= 3 else None


def parse_range(text: str, lang: str = "en", ref: date | None = None):
    """Parse things like 'Oct 25-28', 'Dec 30 - Jan 2, 2027', '09 Aralık 2026',
    '25 Kasım - 22 Aralık', '8-10 Ekim 2026'. Returns (start, end) ISO dates or (None, None)."""
    ref = ref or date.today()
    tokens = re.findall(r"[A-Za-zÇĞİÖŞÜçğıöşü]+|\d+", text or "")
    dates, pending, month = [], [], None  # dates: [y, m, d]
    for tok in tokens:
        if tok.isdigit():
            n = int(tok)
            if n >= 1900:
                for d in dates:
                    if d[0] is None:
                        d[0] = n
            elif 1 <= n <= 31:
                if lang == "tr":
                    pending.append(n)
                elif month:
                    dates.append([None, month, n])
        else:
            m = _month(tok, lang)
            if m:
                month = m
                if lang == "tr":
                    dates.extend([None, m, d] for d in pending)
                    pending = []
    if not dates:
        return None, None
    start, end = dates[0], dates[-1]
    if start[0] is not None and start[0] == end[0] and (start[1], start[2]) > (end[1], end[2]):
        start[0] -= 1  # "Dec 30 - Jan 2, 2027": the trailing year belongs to the end date
    if start[0] is None:
        start[0] = end[0]
    if start[0] is None:
        y = ref.year
        if date(y, start[1], min(start[2], 28)) < ref - timedelta(days=60):
            y += 1
        start[0] = y
    if end[0] is None:
        end[0] = start[0] + (1 if (end[1], end[2]) < (start[1], start[2]) else 0)
    try:
        s, e = date(*start), date(*end)
    except ValueError:
        return None, None
    if e < s:
        e = s
    return s.isoformat(), e.isoformat()
