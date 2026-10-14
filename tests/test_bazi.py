from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from fortune_bot import bazi
from fortune_bot.bazi import CST, compute, parse_date, parse_place, parse_time, parse_tz

GZ = [a + b for a, b in zip("甲乙丙丁戊己庚辛壬癸" * 6, "子丑寅卯辰巳午未申酉戌亥" * 5)]


def jdn_day_pillar(y, m, d):
    """Independent day-pillar formula: (JDN + 49) mod 60, 0 = 甲子."""
    return GZ[(date(y, m, d).toordinal() + 1721425 + 49) % 60]


@pytest.mark.parametrize("args,expected", [
    ((2000, 1, 1, 0, 0), "己卯 丙子 戊午 壬子"),          # widely published reference
    ((2024, 2, 4, 16, 0), "癸卯 乙丑 戊戌 庚申"),         # 27 min before 立春 (16:27 CST)
    ((2024, 2, 4, 17, 0), "甲辰 丙寅 戊戌 辛酉"),         # 33 min after 立春
    ((1984, 2, 4, 23, 30), "甲子 丙寅 戊辰 甲子"),        # 立春 1984-02-04 23:19, 子时
    ((1990, 5, 15, 22, 30), "庚午 辛巳 庚辰 丁亥"),       # 亥时
    ((1990, 5, 15, 23, 30), "庚午 辛巳 庚辰 戊子"),       # 晚子时: same day pillar, next-day hour stem
])
def test_reference_dates(args, expected):
    assert " ".join(compute(*args, CST).pillars) == expected


def test_day_pillar_matches_independent_formula():
    for y, m, d in [(1900, 1, 1), (1949, 10, 1), (1984, 2, 4), (2000, 1, 1), (2024, 2, 4), (2050, 12, 31)]:
        assert compute(y, m, d, 12, 0, CST).day == jdn_day_pillar(y, m, d)
    assert jdn_day_pillar(1900, 1, 1) == "甲戌"


def test_solar_term_uses_instant_not_wall_clock():
    # 2024-02-04 12:00 in Moscow = 17:00 CST, after 立春 -> 甲辰 year / 丙寅 month
    b = compute(2024, 2, 4, 12, 0, ZoneInfo("Europe/Moscow"))
    assert (b.year, b.month) == ("甲辰", "丙寅")
    # same wall clock in Beijing is before 立春
    b = compute(2024, 2, 4, 12, 0, ZoneInfo("Asia/Shanghai"))
    assert (b.year, b.month) == ("癸卯", "乙丑")


def test_zi_hour_boundary():
    assert compute(2000, 1, 1, 22, 59, CST).hour[1] == "亥"
    assert compute(2000, 1, 1, 23, 0, CST).hour[1] == "子"
    assert compute(2000, 1, 2, 0, 59, CST).hour[1] == "子"
    assert compute(2000, 1, 2, 1, 0, CST).hour[1] == "丑"


def test_elements_sum_to_eight():
    b = compute(2000, 1, 1, 0, 0, CST)
    assert sum(b.elements.values()) == 8
    assert b.elements == {"木": 1, "火": 2, "土": 2, "金": 0, "水": 3}


def test_parsers():
    assert parse_date("1990-05-15") == (1990, 5, 15)
    assert parse_date("1990年5月15日") == (1990, 5, 15)
    for bad in ("1990-02-30", "abc", "1800-01-01"):
        with pytest.raises(bazi.ParseError):
            parse_date(bad)
    assert parse_time("14:30") == (14, 30) and parse_time("7") == (7, 0) and parse_time("23点05") == (23, 5)
    with pytest.raises(bazi.ParseError):
        parse_time("24:00")
    assert parse_tz("+8")[1] == "UTC+08:00" and parse_tz("UTC-5:30")[1] == "UTC-05:30"
    assert parse_tz("北京")[1] == "Asia/Shanghai" and parse_tz("Europe/Berlin")[1] == "Europe/Berlin"
    with pytest.raises(bazi.ParseError):
        parse_tz("Atlantis")
    assert parse_place("Москва")[2] == (55.76, 37.62) and parse_place("+3")[2] is None


def test_huangli_and_compat():
    h = bazi.huangli(datetime(2026, 10, 13))
    assert h["day"] == jdn_day_pillar(2026, 10, 13) and h["yi"]
    a, b = compute(1990, 5, 15, 12, 0, CST), compute(1992, 8, 1, 12, 0, CST)
    assert 0 <= bazi.compat(a, b) <= 100 and bazi.compat(a, b) == bazi.compat(b, a)
