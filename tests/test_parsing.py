from datetime import date

from etkinlik_radari.backend import classify, dates, geo

REF = date(2026, 10, 1)


def test_parse_range_english():
    assert dates.parse_range("Oct 25-28, 2026", ref=REF) == ("2026-10-25", "2026-10-28")
    assert dates.parse_range("Dec 30 - Jan 2, 2027", ref=REF) == ("2026-12-30", "2027-01-02")


def test_parse_range_turkish():
    assert dates.parse_range("09 Aralık 2026", "tr", ref=REF) == ("2026-12-09", "2026-12-09")
    assert dates.parse_range("8-10 Ekim 2026", "tr", ref=REF) == ("2026-10-08", "2026-10-10")


def test_parse_range_empty():
    assert dates.parse_range("yakında", "tr", ref=REF) == (None, None)


def test_norm():
    assert dates.norm("2026-11-03") == "2026-11-03"
    assert dates.norm("2026-11-03T10:00:00+03:00") == "2026-11-03T07:00:00Z"
    assert dates.norm("") is None


def test_country_code():
    assert geo.country_code({"city": "Istanbul"}) == "tr"
    assert geo.country_code({"country": "DE"}) == "de"
    assert geo.country_code({"title": "StrictlyVC NYC 2026"}) == "us"
    assert geo.country_code({"online": True, "city": "London"}) == ""


def test_israel_excluded():
    assert geo.is_excluded({"title": "AI Week", "city": "Tel Aviv"})
    assert geo.is_excluded({"title": "Founders Night", "country": "IL"})
    assert not geo.is_excluded({"title": "Founders Night", "city": "Berlin"})


def test_region_and_kind():
    assert classify.region_of({"city": "İstanbul"}) == "turkey"
    assert classify.region_of({"city": "Berlin"}) == "europe"
    assert classify.region_of({"online": True}) == "online"
    assert classify.kind_of({"title": "Global AI Hackathon"}) == "hackathon"
