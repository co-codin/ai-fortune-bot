"""Western (tropical) astrology using PyEphem (VSOP87/ELP-based, arc-minute accuracy).

* Sun and Moon signs: true ecliptic longitude of date at the birth instant.
* Ascendant: computed from local sidereal time, obliquity and latitude; needs
  birth time and coordinates (only known cities have coordinates). Without
  coordinates the ascendant is omitted.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

import ephem

SIGNS = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra",
         "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
SIGN_ELEMENT = {s: e for s, e in zip(SIGNS, ["fire", "earth", "air", "water"] * 3)}
SIGN_NAMES = {
    "zh": dict(zip(SIGNS, "白羊座 金牛座 双子座 巨蟹座 狮子座 处女座 天秤座 天蝎座 射手座 摩羯座 水瓶座 双鱼座".split())),
    "ru": dict(zip(SIGNS, "Овен Телец Близнецы Рак Лев Дева Весы Скорпион Стрелец Козерог Водолей Рыбы".split())),
    "en": dict(zip(SIGNS, [s.capitalize() for s in SIGNS])),
}
SIGN_EMOJI = dict(zip(SIGNS, "♈♉♊♋♌♍♎♏♐♑♒♓"))

# Approximate date table: used when only a date is known (compat mode). Boundary
# days can differ by one day from year to year; the time-aware path uses ephem.
_DATE_TABLE = [(1, 20, "capricorn"), (2, 19, "aquarius"), (3, 21, "pisces"), (4, 20, "aries"),
               (5, 21, "taurus"), (6, 21, "gemini"), (7, 23, "cancer"), (8, 23, "leo"),
               (9, 23, "virgo"), (10, 23, "libra"), (11, 22, "scorpio"), (12, 22, "sagittarius"),
               (12, 32, "capricorn")]


def sign_of(lon_deg: float) -> str:
    return SIGNS[int((lon_deg % 360) // 30)]


def sun_sign_by_date(month: int, day: int) -> str:
    for m, d, sign in _DATE_TABLE:
        if (month, day) < (m, d):
            return sign
    return "capricorn"


def _edate(dt: datetime) -> ephem.Date:
    u = dt.astimezone(timezone.utc)
    return ephem.Date(u.replace(tzinfo=None))


def body_longitude(body, dt: datetime) -> float:
    d = _edate(dt)
    b = body(d)
    return math.degrees(ephem.Ecliptic(b, epoch=d).lon)


def ascendant(dt: datetime, lat: float, lon: float) -> float:
    d = _edate(dt)
    obs = ephem.Observer()
    obs.date, obs.lat, obs.lon = d, str(lat), str(lon)
    ramc = float(obs.sidereal_time())  # local apparent sidereal time, radians
    eps = math.radians(23.4392911 - 0.0130042 * ((float(d) + 2415020 - 2451545.0) / 36525))
    phi = math.radians(lat)
    asc = math.atan2(math.cos(ramc), -(math.sin(ramc) * math.cos(eps) + math.tan(phi) * math.sin(eps)))
    return math.degrees(asc) % 360


def chart(dt: datetime, coords=None) -> dict:
    res = {"sun": sign_of(body_longitude(ephem.Sun, dt)), "moon": sign_of(body_longitude(ephem.Moon, dt)),
           "asc": None}
    if coords:
        res["asc"] = sign_of(ascendant(dt, *coords))
    return res


def compat(a: str, b: str) -> int:
    ea, eb = SIGN_ELEMENT[a], SIGN_ELEMENT[b]
    if ea == eb:
        return 85
    good = {frozenset(("fire", "air")), frozenset(("earth", "water"))}
    return 75 if frozenset((ea, eb)) in good else 50
