import random
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from fortune_bot import astro, tarot


def test_deck_complete():
    assert len(tarot.DECK) == 78
    assert len({c.id for c in tarot.DECK}) == 78
    assert sum(c.id.startswith("major") for c in tarot.DECK) == 22
    for s in ("wands", "cups", "swords", "pentacles"):
        assert sum(c.id.startswith(s) for c in tarot.DECK) == 14
    for c in tarot.DECK:
        for L in ("zh", "ru", "en"):
            assert c.name(L) and c.meaning(L, False) and c.meaning(L, True)
            assert c.meaning(L, False) != c.meaning(L, True)
    assert len({c.name("zh") for c in tarot.DECK}) == len({c.name("ru") for c in tarot.DECK}) == 78


def test_draw_distinct_and_both_orientations():
    seen = set()
    for _ in range(200):
        cards = tarot.draw(3)
        assert len({c.id for c, _ in cards}) == 3
        seen |= {r for _, r in cards}
    assert seen == {True, False}
    assert isinstance(tarot._rng, random.SystemRandom)
    c = tarot.DECK[0]
    assert "逆位" in tarot.fmt(c, True, "zh") and "upright" in tarot.fmt(c, False, "en")


@pytest.mark.parametrize("m,d,sign", [
    (3, 20, "pisces"), (3, 21, "aries"), (4, 19, "aries"), (4, 20, "taurus"), (6, 20, "gemini"), (7, 23, "leo"),
    (12, 21, "sagittarius"), (12, 22, "capricorn"), (1, 19, "capricorn"), (1, 20, "aquarius"), (12, 31, "capricorn"),
])
def test_sun_sign_by_date_boundaries(m, d, sign):
    assert astro.sun_sign_by_date(m, d) == sign


def test_sun_sign_ephemeris_at_equinox():
    # 2024 March equinox: 2024-03-20 03:06 UTC
    assert astro.chart(datetime(2024, 3, 20, 2, 30, tzinfo=timezone.utc))["sun"] == "pisces"
    assert astro.chart(datetime(2024, 3, 20, 3, 40, tzinfo=timezone.utc))["sun"] == "aries"


def test_moon_and_ascendant_references():
    # New moon 2000-01-06 18:14 UTC at ~15°45' Capricorn: sun and moon both Capricorn
    c = astro.chart(datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc))
    assert c["sun"] == c["moon"] == "capricorn"
    # Full moon 2024-09-18 02:34 UTC: Moon in Pisces opposite Sun in Virgo
    c = astro.chart(datetime(2024, 9, 18, 2, 34, tzinfo=timezone.utc))
    assert (c["sun"], c["moon"]) == ("virgo", "pisces")
    # Ascendant at Greenwich, J2000 noon: ~24° Aries
    lon = astro.ascendant(datetime(2000, 1, 1, 12, tzinfo=timezone.utc), 51.48, 0.0)
    assert 23 < lon < 26
    # equator, RAMC 0 -> ascendant 0° Cancer (90°) sanity: asc always 90° ahead of MC near equator
    assert astro.chart(datetime(2000, 1, 1, 12, tzinfo=ZoneInfo("Europe/London")), (51.48, 0.0))["asc"] == "aries"


def test_sign_compat():
    assert astro.compat("aries", "leo") == 85 and astro.compat("aries", "gemini") == 75
    assert astro.compat("aries", "cancer") == 50 and astro.compat("taurus", "pisces") == 75
