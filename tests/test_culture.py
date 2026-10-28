from types import SimpleNamespace

from etkinlik_radari.backend.sources import culture

RSS = """<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>
<item><title>Martin Eden</title><description>Oyun</description><pubDate>Fri, 30 Oct 2026 20:30:00 +0300</pubDate>
<link>https://etkinlik.io/etkinlik/1/martin-eden</link><enclosure url="https://x/a.jpg" type="image/jpg"/>
<category>Sahne Sanatları</category><category>Tiyatro ve Gösteriler</category></item>
<item><title>Martin Eden</title><pubDate>Sat, 31 Oct 2026 20:30:00 +0300</pubDate>
<link>https://etkinlik.io/etkinlik/2/martin-eden</link><category>Tiyatro ve Gösteriler</category></item>
<item><title>Ekmek Atölyesi</title><pubDate>Sat, 31 Oct 2026 11:00:00 +0300</pubDate>
<link>https://etkinlik.io/etkinlik/3/ekmek</link><category>Aşçılık ve Mutfak</category></item>
<item><title>Caz Gecesi</title><pubDate>Sat, 31 Oct 2026 22:00:00 +0300</pubDate>
<link>https://etkinlik.io/etkinlik/4/caz</link><category>Caz Müzik</category></item>
</channel></rss>"""


def test_etkinlikio_feed(monkeypatch):
    monkeypatch.setattr(culture, "get", lambda url, **kw: SimpleNamespace(content=RSS.encode()))
    evs = culture._etkinlikio_feed("sehirIds=40&turIds=7", "İstanbul", 7)
    assert [e.title for e in evs] == ["Martin Eden", "Martin Eden", "Caz Gecesi"]  # cooking workshop skipped
    assert evs[0].start == "2026-10-30T17:30:00Z" and evs[0].city == "İstanbul" and evs[0].image == "https://x/a.jpg"
    assert evs[0].tags == ["cat:stage"] and evs[2].tags == ["cat:music"]
    folded = culture._fold(evs)
    assert len(folded) == 2 and folded[0].extra["performances"] == 2
