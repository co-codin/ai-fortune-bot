"""BaZi (四柱八字) calculation on top of lunar-python (6tail lunar).

Time handling:
* Year/month pillars depend on the *instant* of the solar terms (节气). lunar-python
  stores solar-term times in China Standard Time (UTC+8), so the birth instant is
  converted to UTC+8 before computing year and month pillars.
* Day/hour pillars follow the local wall-clock time at the birth place.
* 子时 handling uses lunar-python sect 2 (default): 23:00-23:59 keeps the same day
  pillar ("晚子时"), the hour stem is taken from the next day.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from lunar_python import Solar

CST = timezone(timedelta(hours=8))

GAN_WX = dict(zip("甲乙丙丁戊己庚辛壬癸", "木木火火土土金金水水"))
ZHI_WX = dict(zip("子丑寅卯辰巳午未申酉戌亥", "水土木木土火火土金金土水"))
ELEMENTS = "木火土金水"
ELEMENT_EN = dict(zip(ELEMENTS, ["Wood", "Fire", "Earth", "Metal", "Water"]))

# Common city -> IANA zone shortcuts (user can always type an IANA name or UTC offset).
CITY_TZ = {
    "beijing": "Asia/Shanghai", "北京": "Asia/Shanghai", "shanghai": "Asia/Shanghai",
    "上海": "Asia/Shanghai", "hong kong": "Asia/Hong_Kong", "香港": "Asia/Hong_Kong",
    "taipei": "Asia/Taipei", "台北": "Asia/Taipei", "singapore": "Asia/Singapore",
    "新加坡": "Asia/Singapore", "tokyo": "Asia/Tokyo", "东京": "Asia/Tokyo",
    "moscow": "Europe/Moscow", "москва": "Europe/Moscow", "莫斯科": "Europe/Moscow",
    "saint petersburg": "Europe/Moscow", "st petersburg": "Europe/Moscow",
    "санкт-петербург": "Europe/Moscow", "питер": "Europe/Moscow", "圣彼得堡": "Europe/Moscow",
    "london": "Europe/London", "伦敦": "Europe/London", "лондон": "Europe/London",
    "new york": "America/New_York", "纽约": "America/New_York", "нью-йорк": "America/New_York",
    "los angeles": "America/Los_Angeles", "洛杉矶": "America/Los_Angeles",
    "berlin": "Europe/Berlin", "dubai": "Asia/Dubai", "迪拜": "Asia/Dubai",
}


class ParseError(ValueError):
    pass


# city -> (lat, lon) for astrology ascendant
CITY_LL = {
    "beijing": (39.90, 116.41), "北京": (39.90, 116.41), "shanghai": (31.23, 121.47), "上海": (31.23, 121.47),
    "hong kong": (22.32, 114.17), "香港": (22.32, 114.17), "taipei": (25.03, 121.57), "台北": (25.03, 121.57),
    "singapore": (1.35, 103.82), "新加坡": (1.35, 103.82), "tokyo": (35.68, 139.69), "东京": (35.68, 139.69),
    "moscow": (55.76, 37.62), "москва": (55.76, 37.62), "莫斯科": (55.76, 37.62),
    "saint petersburg": (59.94, 30.31), "st petersburg": (59.94, 30.31), "санкт-петербург": (59.94, 30.31),
    "питер": (59.94, 30.31), "圣彼得堡": (59.94, 30.31), "london": (51.51, -0.13), "伦敦": (51.51, -0.13),
    "лондон": (51.51, -0.13), "new york": (40.71, -74.01), "纽约": (40.71, -74.01), "нью-йорк": (40.71, -74.01),
    "los angeles": (34.05, -118.24), "洛杉矶": (34.05, -118.24), "berlin": (52.52, 13.40),
    "dubai": (25.20, 55.27), "迪拜": (25.20, 55.27),
}


_GEO = None  # normalized name -> (tz, lat, lon, population, display, country)
_GEO_FILE = __import__("os").path.join(__import__("os").path.dirname(__file__), "data", "cities.tsv.gz")


def _norm(s: str) -> str:
    s = s.strip().lower().replace("ё", "е").replace("’", "'").replace("ʼ", "'")
    s = re.sub(r"^(г\.|город|city of)\s*", "", s)
    s = re.sub(r"[\s_\-]+", " ", s).strip(" .,")
    for suf in ("市",):
        if len(s) > 2 and s.endswith(suf):
            s = s[:-1]
    return s


def _geo():
    """Lazy-load the GeoNames world city index (~70k cities, pop >= 5000)."""
    global _GEO
    if _GEO is None:
        import gzip
        idx: dict = {}
        try:
            with gzip.open(_GEO_FILE, "rt", encoding="utf-8") as f:
                for line in f:
                    name, ascii_, cc, lat, lon, tz, pop, alts = line.rstrip("\n").split("\t")
                    rec = (tz, float(lat), float(lon), int(pop or 0), name, cc)
                    for n in {name, ascii_, *alts.split("|")}:
                        if not n:
                            continue
                        k = _norm(n)
                        old = idx.get(k)
                        if old is None or rec[3] > old[3]:
                            idx[k] = rec
        except FileNotFoundError:
            pass
        _GEO = idx
    return _GEO


def lookup_city(text: str):
    """Return (tz, lat, lon, population, display, country) or None. Accepts 'City' or 'City, Country'."""
    g = _geo()
    k = _norm(text)
    if k in g:
        return g[k]
    if "," in text:
        city, _, country = text.partition(",")
        r = g.get(_norm(city))
        if r:
            return r
    return None


def parse_place(text: str):
    """Returns (tzinfo, label, (lat, lon) or None)."""
    tz, label = parse_tz(text)
    ll = CITY_LL.get(text.strip().lower())
    if ll is None:
        r = lookup_city(text)
        if r:
            ll = (r[1], r[2])
    return tz, label, ll


def parse_tz(text: str):
    t = text.strip()
    key = t.lower()
    if key in CITY_TZ:
        return ZoneInfo(CITY_TZ[key]), CITY_TZ[key]
    m = re.fullmatch(r"(?:utc|gmt)?\s*([+-])(\d{1,2})(?::?(\d{2}))?", key)
    if m:
        h, mi = int(m.group(2)), int(m.group(3) or 0)
        if h > 14 or mi >= 60:
            raise ParseError("offset")
        sign = 1 if m.group(1) == "+" else -1
        off = timedelta(hours=h, minutes=mi) * sign
        return timezone(off), f"UTC{m.group(1)}{h:02d}:{mi:02d}"
    if key in ("utc", "gmt"):
        return timezone.utc, "UTC"
    if "/" in t:
        try:
            return ZoneInfo(t), t
        except (ZoneInfoNotFoundError, ValueError):
            pass
    r = lookup_city(t)
    if r and r[0]:
        try:
            return ZoneInfo(r[0]), r[0]
        except (ZoneInfoNotFoundError, ValueError):
            pass
    try:
        return ZoneInfo(t), t
    except (ZoneInfoNotFoundError, ValueError):
        raise ParseError("tz")


def parse_date(text: str) -> tuple[int, int, int]:
    m = re.fullmatch(r"\s*(\d{4})[-./年](\d{1,2})[-./月](\d{1,2})日?\s*", text)
    if not m:
        raise ParseError("date")
    y, mo, d = map(int, m.groups())
    try:
        datetime(y, mo, d)
    except ValueError:
        raise ParseError("date")
    if not 1900 <= y <= 2100:
        raise ParseError("date")
    return y, mo, d


def parse_time(text: str) -> tuple[int, int]:
    m = re.fullmatch(r"\s*(\d{1,2})[:：点时.](\d{2})?分?\s*", text) or re.fullmatch(r"\s*(\d{1,2})\s*", text)
    if not m:
        raise ParseError("time")
    h = int(m.group(1))
    mi = int(m.group(2) or 0) if m.lastindex and m.lastindex >= 2 else 0
    if h > 23 or mi > 59:
        raise ParseError("time")
    return h, mi


@dataclass
class BaZi:
    year: str
    month: str
    day: str
    hour: str
    local_dt: datetime
    tz_label: str
    elements: dict = field(default_factory=dict)

    @property
    def pillars(self):
        return [self.year, self.month, self.day, self.hour]

    @property
    def day_master(self) -> str:
        return self.day[0]

    @property
    def day_master_element(self) -> str:
        return GAN_WX[self.day[0]]


def count_elements(pillars) -> dict:
    c = {e: 0 for e in ELEMENTS}
    for p in pillars:
        c[GAN_WX[p[0]]] += 1
        c[ZHI_WX[p[1]]] += 1
    return c


def compute(y, mo, d, h, mi, tz, tz_label: str = "") -> BaZi:
    local = datetime(y, mo, d, h, mi, tzinfo=tz)
    cst = local.astimezone(CST)
    ec_cst = Solar.fromYmdHms(cst.year, cst.month, cst.day, cst.hour, cst.minute, 0).getLunar().getEightChar()
    ec_loc = Solar.fromYmdHms(y, mo, d, h, mi, 0).getLunar().getEightChar()
    pillars = [ec_cst.getYear(), ec_cst.getMonth(), ec_loc.getDay(), ec_loc.getTime()]
    return BaZi(*pillars, local_dt=local, tz_label=tz_label or str(tz), elements=count_elements(pillars))


def day_pillar(dt: datetime) -> str:
    """Day pillar for a local date (used by the daily push / 黄历)."""
    return Solar.fromYmd(dt.year, dt.month, dt.day).getLunar().getDayInGanZhi()


def huangli(dt: datetime) -> dict:
    lun = Solar.fromYmd(dt.year, dt.month, dt.day).getLunar()
    return {"lunar": f"{lun.getYearInGanZhi()}年 {lun.getMonthInChinese()}月{lun.getDayInChinese()}",
            "day": lun.getDayInGanZhi(), "yi": lun.getDayYi()[:6], "ji": lun.getDayJi()[:6]}


def compat(a: "BaZi", b: "BaZi") -> int:
    """Simple five-element compatibility score 0-100 (entertainment heuristic):
    rewards when one chart's strong elements fill the other's weak ones, and
    day masters in a generating (相生) relation."""
    gen = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    ctrl = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    score = 50
    wa = min(a.elements, key=a.elements.get); wb = min(b.elements, key=b.elements.get)
    if b.elements[wa] >= 2: score += 15
    if a.elements[wb] >= 2: score += 15
    x, y = a.day_master_element, b.day_master_element
    if gen[x] == y or gen[y] == x: score += 20
    elif x == y: score += 10
    elif ctrl[x] == y or ctrl[y] == x: score -= 15
    return max(0, min(100, score))
