"""Source registry. 'status' tells the UI what each site can provide, 'domain' which side of the app it feeds."""
from dataclasses import dataclass
from typing import Callable

from . import culture, curated, dev, foundercal, luma, turkey


@dataclass
class Source:
    id: str
    label: str
    home: str
    fetch: Callable | None
    status: str          # events | news | blocked
    domain: str          # tech | culture | mixed
    note: str            # Turkish
    note_en: str


SOURCES = [
    Source("luma", "Luma", "https://lu.ma", luma.fetch, "events", "mixed",
           "Açık JSON API. Kategori ve şehir bazlı yüzlerce etkinlik.",
           "Open JSON API. Hundreds of events by category and city."),
    Source("foundercal", "Foundercal", "https://foundercal.com", foundercal.fetch, "events", "tech",
           "Şehir başına küratörlü kurucu etkinlikleri (JSON-LD).",
           "Curated founder events per city (JSON-LD)."),
    Source("techmeme", "Techmeme Events", "https://www.techmeme.com/events", curated.techmeme, "events", "tech",
           "Büyük teknoloji konferanslarının küratörlü listesi.",
           "Curated list of major tech conferences."),
    Source("dealroom", "Dealroom", "https://dealroom.co/events", curated.dealroom, "events", "tech",
           "Küratörlü startup ve VC etkinlikleri (JSON-LD).",
           "Curated startup and VC events (JSON-LD)."),
    Source("cerebral", "Cerebral Valley", "https://cerebralvalley.ai/events", curated.cerebral, "events", "tech",
           "Seçkin AI etkinlikleri ve hackathon'lar.",
           "Hand-picked AI events and hackathons."),
    Source("techcrunch", "TechCrunch", "https://techcrunch.com/events/", curated.techcrunch, "events", "tech",
           "Disrupt, StrictlyVC ve diğer TechCrunch etkinlikleri (WP REST). Haberleri de alınır.",
           "Disrupt, StrictlyVC and other TechCrunch events (WP REST). News included."),
    Source("slush", "Slush / Web Summit", "https://slush.org", curated.flagships, "events", "tech",
           "Amiral konferanslar: Slush ve Web Summit sürümleri.",
           "Flagship conferences: Slush and every Web Summit edition."),
    Source("devpost", "Devpost", "https://devpost.com/hackathons", dev.devpost, "events", "tech",
           "Açık ve yaklaşan hackathon'lar, ödül ve kayıt sayısıyla.",
           "Open and upcoming hackathons with prizes and sign-ups."),
    Source("devevents", "dev.events", "https://dev.events", dev.devevents, "events", "tech",
           "Geliştirici konferansları (RSS).",
           "Developer conferences (RSS)."),
    Source("aideadlines", "AI Deadlines", "https://aideadlin.es", dev.ai_deadlines, "events", "tech",
           "aideadlin.es 2025'te donduruldu; halefi huggingface/ai-deadlines kullanılıyor.",
           "aideadlin.es was frozen in 2025; its successor huggingface/ai-deadlines is used."),
    Source("webrazzi", "Webrazzi", "https://webrazzi.com/etkinlik/", turkey.webrazzi, "events", "tech",
           "Webrazzi konferansları. Haberleri de alınır.",
           "Webrazzi conferences. News included."),
    Source("itu", "İTÜ Çekirdek", "https://itucekirdek.com/etkinlikler/", turkey.itu, "events", "tech",
           "İTÜ Çekirdek etkinlikleri (WP REST).",
           "İTÜ Çekirdek events (WP REST)."),
    # ---- culture & arts ----
    Source("biletix", "Biletix", "https://www.biletix.com", culture.biletix, "events", "culture",
           "Türkiye'nin en büyük bilet sitesi: tiyatro, konser, stand-up, bale, sergi ve çocuk etkinlikleri "
           "(önümüzdeki 90 gün). Aynı oyunun temsilleri tek kartta birleşir.",
           "Türkiye's largest ticketing site: theatre, concerts, stand-up, ballet, exhibitions and family "
           "events (next 90 days). Performances of the same show are merged into one card."),
    Source("etkinlikio", "etkinlik.io", "https://etkinlik.io", culture.etkinlikio, "events", "culture",
           "Türkiye geneli etkinlik rehberi (resmî RSS servisi): 24 şehirde tiyatro, konser, sergi, festival, "
           "söyleşi ve çocuk etkinlikleri.",
           "Nationwide Turkish events guide (official RSS service): theatre, concerts, exhibitions, festivals, "
           "talks and family events in 24 cities."),
    Source("biletinial", "Biletinial", "https://biletinial.com", culture.biletinial, "events", "culture",
           "Tiyatro, müzik, opera ve bale; Anadolu şehirleri dahil (JSON-LD).",
           "Theatre, music, opera and ballet across Türkiye, including smaller cities (JSON-LD)."),
    Source("eventbrite", "Eventbrite", "https://www.eventbrite.com", culture.eventbrite, "events", "culture",
           "Dünya şehirlerinde sahne sanatları, müzik ve sanat etkinlikleri (şehirler Profilim'den seçilir).",
           "Performing arts, music and art events in world cities (cities are set in My profile)."),
    Source("izmir", "İzmir Kültür Sanat", "https://kultursanat.izmir.bel.tr", culture.izmir, "events", "culture",
           "İzmir Büyükşehir Belediyesi açık veri API'si: sergi, konser ve gösteriler.",
           "İzmir Metropolitan Municipality open data API: exhibitions, concerts and shows."),
    # ---- news only ----
    Source("swipeline", "Swipeline", "https://swipeline.co", None, "news", "tech",
           "Etkinlik takvimi yok; girişim ve yatırım haberleri Haberler sekmesinde.",
           "No event calendar; startup and investment news appear under News."),
    Source("endeavor", "Endeavor Türkiye", "https://endeavor.org.tr", None, "news", "tech",
           "Etkinlik bölümü yok; yazıları Haberler sekmesinde.",
           "No events section; its articles appear under News."),
    Source("crunchbase", "Crunchbase", "https://www.crunchbase.com", None, "blocked", "tech",
           "Cloudflare koruması (403). Sadece Crunchbase News RSS Haberler sekmesinde.",
           "Behind Cloudflare (403). Only the Crunchbase News RSS feed is used, under News."),
]

BY_ID = {s.id: s for s in SOURCES}
# websummit events are produced by the 'slush' fetcher
LABELS = {s.id: s.label for s in SOURCES} | {"websummit": "Web Summit", "slush": "Slush"}
