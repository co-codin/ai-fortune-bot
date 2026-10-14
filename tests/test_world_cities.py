import pytest
from fortune_bot.bazi import parse_tz, parse_place, ParseError

@pytest.mark.parametrize("q,tz", [
    ("Melitopol", "Europe/Zaporozhye"), ("Мелитополь", "Europe/Zaporozhye"),
    ("мелитополь", "Europe/Zaporozhye"), ("Мелітополь", "Europe/Zaporozhye"),
    ("Melitopol, Ukraine", "Europe/Zaporozhye"), ("г. Мелитополь", "Europe/Zaporozhye"),
    ("Kyiv", "Europe/Kyiv"), ("Киев", "Europe/Kyiv"), ("Новосибирск", "Asia/Novosibirsk"),
    ("Владивосток", "Asia/Vladivostok"), ("Екатеринбург", "Asia/Yekaterinburg"),
    ("Paris", "Europe/Paris"), ("Sydney", "Australia/Sydney"), ("Mumbai", "Asia/Kolkata"),
    ("São Paulo", "America/Sao_Paulo"), ("Sao Paulo", "America/Sao_Paulo"),
    ("Chicago", "America/Chicago"), ("Cairo", "Africa/Cairo"), ("Almaty", "Asia/Almaty"),
    ("Tbilisi", "Asia/Tbilisi"), ("Ташкент", "Asia/Tashkent"), ("广州", "Asia/Shanghai"),
    ("成都市", "Asia/Shanghai"), ("Batumi", "Asia/Tbilisi"), ("Минск", "Europe/Minsk"),
    ("Москва", "Europe/Moscow"), ("Berlin", "Europe/Berlin"),
])
def test_world_city(q, tz):
    got = parse_tz(q)[1]
    # tzdata may alias Zaporozhye -> Kyiv
    assert got == tz or (tz == "Europe/Zaporozhye" and got in ("Europe/Kyiv", "Europe/Kiev", "Europe/Simferopol"))

def test_melitopol_coords():
    _, _, ll = parse_place("Мелитополь")
    assert ll and abs(ll[0] - 46.85) < 0.2 and abs(ll[1] - 35.37) < 0.2

@pytest.mark.parametrize("q,label", [("+3", "UTC+03:00"), ("UTC+5:30", "UTC+05:30"), ("-8", "UTC-08:00"), ("GMT+2", "UTC+02:00")])
def test_offsets(q, label):
    assert parse_tz(q)[1] == label

@pytest.mark.parametrize("q", ["Europe/Berlin", "America/Argentina/Buenos_Aires", "Asia/Kolkata", "Europe/Kyiv"])
def test_iana(q):
    assert parse_tz(q)[1] == q

def test_unknown():
    with pytest.raises(ParseError):
        parse_tz("Atlantisqwerty")
