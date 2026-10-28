# Etkinlik Radarı — Plan

## 1. Kaynak analizi (28 Ekim 2026'da test edildi)

| # | Site | Durum | Yöntem | Ne geliyor |
|---|------|-------|--------|-----------|
| 1 | lu.ma | ✅ Tam | Açık JSON API (`api.lu.ma/discover/get-paginated-events`) | Yüzlerce etkinlik; kategori (tech/ai/crypto) + şehir (istanbul, london…). Kapak görseli, katılımcı sayısı, ücretsiz mi, organizatör, tam adres |
| 2 | foundercal.com | ✅ Tam | Şehir sayfası JSON-LD listesi + etkinlik sayfası JSON-LD `Event` | Şehir başına ~25-60 küratörlü kurucu etkinliği (İstanbul dahil) |
| 3 | techmeme.com/events | ✅ Tam | HTML liste | ~100 büyük teknoloji konferansı (tarih, ad, şehir) |
| 4 | dealroom.co/events | ✅ Tam | JSON-LD `ItemList` | ~50 küratörlü startup/VC etkinliği |
| 5 | crunchbase.com | ❌ Engelli | Cloudflare 403 + captcha | Etkinlik yok. Sadece **Crunchbase News RSS** → Haberler sekmesi |
| 6 | slush.org | ✅ Tek etkinlik | Sayfa başlığı | Slush 2026, Helsinki |
| 7 | websummit.com | ✅ Tek etkinlik | JSON-LD `Event` | Web Summit Lisbon (+ diğer Web Summit şehirleri denenir) |
| 8 | cerebralvalley.ai | ✅ Tam | JSON-LD `ItemList` | ~20 seçkin AI etkinliği / hackathon |
| 9 | techcrunch.com | ✅ Tam | WordPress REST `tc_event` | Disrupt, StrictlyVC, Founder Summit… (+ haber RSS) |
| 10 | devpost.com | ✅ Tam | Açık JSON API | ~175 açık/yaklaşan hackathon, ödül miktarı, kayıt sayısı |
| 11 | dev.events | ✅ Tam | RSS (100 kayıt) | Geliştirici konferansları, teknoloji etiketleri |
| 12 | aideadlin.es | ⚠️ Eski | Site 2025'te güncellenmeyi bıraktı | Halefi **huggingface/ai-deadlines** (GitHub YAML) kullanılır: akademik AI konferansları + makale son tarihleri |
| 13 | swipeline.co | ➖ Etkinlik yok | Haber sitesi (WP REST/RSS) | Haberler sekmesi (girişim + yatırım haberleri) |
| 14 | webrazzi.com | ✅ Tam | `/etkinlik/` HTML kartları | Webrazzi Summit, Fintech, AI, Sessions… (+ haber RSS) |
| 15 | itucekirdek.com | ✅ Tam | WordPress REST `eventer` | İTÜ Çekirdek etkinlikleri (tarih metinden ayrıştırılır) |
| 16 | endeavor.org.tr | ➖ Etkinlik yok | Etkinlik bölümü yok | Haberler sekmesi (WP yazıları) |

**Özet:** 16 sitenin 12'sinden etkinlik çekilebiliyor (biri halef kaynakla), 3'ü sadece haber, 1'i (Crunchbase) tamamen engelli; ondan da haber RSS'i alınıyor.

## 2. Mimari

- **Python + pywebview** (Windows Edge WebView2): masaüstü penceresi, HTML/CSS/JS arayüzü.
- `backend/sources/*` — her site için bağımsız modül, hepsi ortak `Event` modeline dönüştürür.
- `backend/classify.py` — anahtar kelime ile kategori, tür, bölge tespiti (TR + EN).
- `backend/scoring.py` — önem puanı + kişisel uygunluk puanı + "neden önerildi" gerekçeleri.
- `backend/db.py` — SQLite (`data/radar.db`): etkinlikler, etkileşimler, ayarlar, kaynak durumu, haberler.
- Yenileme arka planda paralel (thread pool); bir kaynak bozulursa diğerleri çalışmaya devam eder.

## 3. Kategoriler

Yapay Zekâ · Girişimcilik · Yatırım & VC · Fintech · Kripto/Web3 · Yazılım & Geliştirici · Siber Güvenlik · Ürün & Tasarım · Büyüme & Pazarlama · Deep Tech · Sağlık/Biyotek · İklim/Enerji · Akademik/Araştırma

**Türler:** Konferans · Meetup/Networking · Hackathon · Workshop/Eğitim · Demo Day/Pitch · Webinar · Makale son tarihi
**Bölgeler:** Türkiye · Avrupa · Kuzey Amerika · Online · Diğer

## 4. Kişiselleştirme

1. **İlk açılış sihirbazı:** her kategori/tür/bölge için *İlgilenmiyorum / Nötr / İlgileniyorum / Çok ilgileniyorum*.
2. **Öğrenen profil:** 👍 Beğen, 👎 İlgilenmiyorum, 🔖 Kaydet, ✅ Katıldım → etkinliğin özellikleri (kategori, tür, bölge, kaynak, başlıktaki anahtar kelimeler) ağırlık kazanır/kaybeder. Geri alınabilir (etkileşimlerden her seferinde yeniden hesaplanır).
3. **Puan** = %60 kişisel uygunluk + %40 önem. Önem: kaynağın küratörlüğü, amiral etkinlik (Slush, Web Summit, Disrupt…), katılımcı sayısı, hackathon ödülü, akademik konferans derecesi.
4. Her kartta **uygunluk yüzdesi** ve **gerekçeler** ("Yapay Zekâ ilgini çekiyor", "Türkiye'de", "262 katılımcı").

## 5. Arayüz

- **Sol menü:** Keşfet · Takvim · Kaydedilenler · Haberler · Kaynaklar · Profilim · Yenile düğmesi + son güncelleme
- **Keşfet:** arama, zaman çipleri (Tümü / Bu hafta / Bu ay / 3 ay), sıralama (Önerilen / Tarih / Önem / Yeni eklenen), kategori çipleri, bölge, tür, kaynak, "Sadece ücretsiz", "Geçmişi göster". Üstte "Öne Çıkanlar" şeridi, altında kart ızgarası.
- **Kart:** kapak, tarih rozeti, başlık, yer, kaynak, kategori etiketleri, uygunluk halkası, gerekçeler, 👍 👎 🔖 ↗.
- **Detay paneli:** açıklama, tüm bilgiler, Google Takvim'e ekle, .ics indir, siteye git.
- **Takvim:** aylık ızgara, gün seçince o günün etkinlikleri.
- **Haberler:** Swipeline, Webrazzi, Techmeme, TechCrunch, Crunchbase News, Endeavor.
- **Kaynaklar:** her kaynağın durumu (etkinlik sayısı, süre, hata), aç/kapat, tek tek yenile.
- **Profilim:** ilgi ayarları, Luma/Foundercal şehirleri, öğrenilen tercihler, öğrenmeyi sıfırla.
- Koyu/açık tema.
