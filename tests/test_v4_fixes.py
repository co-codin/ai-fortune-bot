import asyncio
import random
import re
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from fortune_bot import app, bazi, dreams, i18n, iching, llm, lots, tarot
from fortune_bot.engine import Engine, Reply
from fortune_bot.storage import Store


@pytest.fixture
def eng(tmp_path, monkeypatch):
    for k in ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL"):
        monkeypatch.delenv(k, raising=False)
    return Engine(Store(str(tmp_path / "t.db")), bot_username="B", admin_ids=[], payments_enabled=False,
                  rate_per_min=1000, rng=random.Random(2))


async def ready(eng, uid, L="en"):
    await eng.start(uid, L)
    await eng.callback(uid, f"onb:{L}")


def cbs(r):
    return [c for row in r.buttons for _, c in row]


async def birth(eng, uid, d="1990-05-15", tm="08:00", place="Moscow"):
    await eng.callback(uid, "m:bazi")
    if eng.s.get(uid)["state"] is None:          # saved-data prompt
        await eng.callback(uid, "new:bazi")
    await eng.text(uid, d); await eng.text(uid, tm)
    return await eng.text(uid, place)


# ---- 1) results are never overwritten
def _two(first, second):
    async def go(e, u):
        await e.callback(u, first)
        return await e.callback(u, second)
    return go


RESULT_PATHS = [("tarot", lambda e, u: e.callback(u, "tarot:1")),
                ("lot", _two("m:lot", "lot:go")),
                ("iching", _two("m:iching", "ic:go")),
                ("lucky", lambda e, u: e.callback(u, "m:lucky")),
                ("huangli", lambda e, u: e.callback(u, "m:huangli"))]


@pytest.mark.parametrize("name,make", RESULT_PATHS)
async def test_result_buttons_never_edit(eng, name, make):
    await ready(eng, 1)
    res = (await make(eng, 1))[-1]
    assert not res.edit
    for data in cbs(res):
        if data in ("share", "buy:yearly"):
            continue
        assert data.startswith("r:"), (name, data)
        out = await eng.callback(1, data)
        assert out and out[0].clear_kb and out[0].text == ""
        assert all(not r.edit for r in out), (name, data)


async def test_bazi_and_other_results_use_r_prefix(eng):
    await ready(eng, 2)
    rs = await birth(eng, 2)
    assert all(c.startswith("r:") or c in ("share", "buy:yearly") for c in cbs(rs[-1]))
    for mode, inputs in (("dream", ["I was flying above a city"]), ("compat", ["1990-05-15", "1992-08-01"])):
        r = await eng.callback(2, f"m:{mode}")
        if mode == "compat":
            await eng.callback(2, "new:compat")
        for x in inputs:
            out = await eng.text(2, x)
        assert all(c.startswith("r:") or c == "share" for c in cbs(out[-1])), mode


async def test_navigation_still_edits(eng):
    await ready(eng, 3)
    assert (await eng.callback(3, "menu"))[0].edit
    assert (await eng.callback(3, "m:tarot"))[0].edit
    assert (await eng.callback(3, "m:bazi"))[0].edit
    assert (await eng.callback(3, "dy:1990"))[0].edit


async def test_adapter_clears_keyboard_and_sends_new():
    bot = AsyncMock()
    msg = MagicMock(message_id=42)
    await app.send(bot, 7, [Reply("", clear_kb=True), Reply("menu", [[("a", "b")]])], msg)
    bot.edit_message_reply_markup.assert_awaited_once()
    assert bot.edit_message_reply_markup.await_args.kwargs == {"chat_id": 7, "message_id": 42, "reply_markup": None}
    bot.edit_message_text.assert_not_awaited()
    assert bot.send_message.await_args.kwargs["text"] == "menu"


async def test_daily_push_buttons_r_prefixed(eng):
    await ready(eng, 4)
    await birth(eng, 4)
    r = (await eng.daily_message(4, datetime(2026, 10, 13, 9, tzinfo=timezone.utc)))[0]
    assert set(cbs(r)) == {"r:m:tarot", "r:menu"}


# ---- 2) 时辰 labels
async def test_shichen_labels_localized(eng):
    assert i18n.shichen_label(4, "en") == "Dragon 07–09"
    assert i18n.shichen_label(4, "ru") == "Дракон 07–09"
    assert i18n.shichen_label(0, "zh") == "子时 23–01"
    for L in ("en", "ru"):
        assert len(set(i18n.SHICHEN_ANIMALS[L])) == 12
        assert not any(re.search("[\u4e00-\u9fff]", i18n.shichen_label(i, L)) for i in range(12))
    await ready(eng, 5, "ru")
    await eng.callback(5, "m:bazi"); await eng.text(5, "1990-05-15")
    labels = [b for row in (await eng.callback(5, "m:bazi"))[0].buttons for b, _ in row]
    await eng.text(5, "1990-05-15")
    r = (await eng.text(5, "1990-05-15"))
    st = eng.s.get(5)["state"]
    assert st in ("c_date", "c_time")


async def test_shichen_buttons_in_flow(eng):
    await ready(eng, 6, "ru")
    await eng.callback(6, "m:bazi")
    r = (await eng.text(6, "1990-05-15"))[0]
    labels = [b for row in r.buttons for b, _ in row]
    assert "Крыса 23–01" in labels and "Свинья 21–23" in labels


# ---- 3) natal vs transit
async def test_horoscope_natal_and_transit(eng, monkeypatch):
    m = AsyncMock(return_value="ok")
    monkeypatch.setattr(llm, "complete", m)
    await eng.horoscope("cancer", "en", datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc), "aries", "libra")
    p = m.await_args.args[0]
    assert "NATAL Sun sign (at birth): cancer" in p and "NATAL Moon sign (at birth): aries" in p
    assert "NATAL Ascendant: libra" in p and "TRANSITING Moon is in capricorn" in p   # new moon in Capricorn
    assert "Never call a natal placement 'today's'" in p


# ---- 4) typing indicator never outlives the handler
async def test_typing_finishes_before_return():
    started, finished = [], []

    async def slow_action(**kw):
        started.append(1)
        await asyncio.sleep(0.3)
        finished.append(1)
    bot = MagicMock()
    bot.send_chat_action = slow_action

    async def work():
        await asyncio.sleep(0.5)       # returns while the chat action is still in flight
        return "x"
    assert await app.with_typing(bot, 1, work()) == "x"
    assert started and len(started) == len(finished)
    n = len(started)
    await asyncio.sleep(0.5)
    assert len(started) == n                 # loop really stopped


async def test_typing_stops_on_exception():
    bot = AsyncMock()

    async def boom():
        await asyncio.sleep(0.5)
        raise RuntimeError("x")
    with pytest.raises(RuntimeError):
        await app.with_typing(bot, 1, boom())
    n = bot.send_chat_action.await_count
    await asyncio.sleep(0.3)
    assert bot.send_chat_action.await_count == n


# ---- 5) timezone for "today"
async def test_today_timezone_resolution(eng):
    await ready(eng, 8, "ru")
    tz, label, src = eng.user_tz(8)
    assert (label, src) == ("Europe/Moscow", "default")
    out = (await eng.callback(8, "m:lucky"))[-1].text
    assert "(Europe/Moscow)" in out and "/tz" in out
    await birth(eng, 8, place="New York")
    assert eng.user_tz(8)[1:] == ("America/New_York", "birth")
    assert "Usage" not in (await eng.tz_cmd(8, ["Atlantis"]))[0].text
    assert "Europe/Berlin" in (await eng.tz_cmd(8, ["Europe/Berlin"]))[0].text
    assert eng.user_tz(8)[1:] == ("Europe/Berlin", "set")
    out = (await eng.callback(8, "m:lucky"))[-1].text
    assert "(Europe/Berlin)" in out and "/tz" not in out
    out = (await eng.callback(8, "m:huangli"))[-1].text
    assert "(Europe/Berlin)" in out
    assert "Europe/Berlin" in (await eng.tz_cmd(8, []))[0].text


async def test_daily_push_uses_same_timezone(eng):
    await ready(eng, 9)
    await birth(eng, 9, place="Beijing")
    await eng.tz_cmd(9, ["Europe/Moscow"])
    await eng.daily_cmd(9, ["on", "9"])
    assert eng.due_daily(datetime(2026, 10 , 13, 1, 0, tzinfo=timezone.utc)) == []   # 09:00 Beijing
    due = eng.due_daily(datetime(2026, 10, 13, 6, 0, tzinfo=timezone.utc))           # 09:00 Moscow
    assert [u for u, _ in due] == [9] and str(due[0][1].tzinfo) == "Europe/Moscow"


async def test_tz_column_migration(tmp_path):
    import sqlite3
    p = str(tmp_path / "old.db")
    db = sqlite3.connect(p)
    db.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, lang TEXT, state TEXT, data TEXT DEFAULT '{}', profile TEXT,"
               " daily_on INTEGER DEFAULT 0, daily_hour INTEGER DEFAULT 9, daily_last TEXT, referred_by INTEGER, created REAL)")
    db.execute("INSERT INTO users(id, lang) VALUES(1, 'en')"); db.commit(); db.close()
    s = Store(p)
    assert s.get(1)["tz"] is None
    s.set(1, tz="UTC")
    assert s.get(1)["tz"] == "UTC"


# ---- 6) compat with saved data for A
async def test_compat_offers_saved_a(eng):
    await ready(eng, 10)
    await birth(eng, 10, d="1990-05-15")
    r = (await eng.callback(10, "m:compat"))[0]
    assert cbs(r)[:2] == ["use:compat", "new:compat"] and "1990-05-15" in r.text
    r = (await eng.callback(10, "use:compat"))[0]
    assert "Person B" in r.text and r.edit
    out = (await eng.text(10, "1992-08-01"))[0].text
    assert "庚午 辛巳 庚辰" in out and "壬申" in out
    r = (await eng.callback(10, "r:m:compat"))
    assert (await eng.callback(10, "new:compat"))[0].text.startswith("💞 **Compatibility · person A**")


# ---- 7) exact element counts
def _manual(pillars):
    c = {e: 0 for e in "木火土金水"}
    for p in pillars:
        c[bazi.GAN_WX[p[0]]] += 1
        c[bazi.ZHI_WX[p[1]]] += 1
    return c


async def test_compat_counts_and_prompt(eng, monkeypatch):
    m = AsyncMock(return_value="ok")
    monkeypatch.setattr(llm, "complete", m)
    await ready(eng, 11)
    await eng.callback(11, "m:compat")
    await eng.text(11, "1990-05-15")
    await eng.text(11, "1992-08-01")
    p = m.await_args.args[0]
    b = bazi.compute(1992, 8, 1, 12, 0, bazi.CST)
    assert b.pillars[0] == "壬申"
    counts = _manual(b.pillars[:3])
    assert counts["水"] >= 1
    want = ", ".join(f"{bazi.ELEMENT_EN[e]} {n}" for e, n in counts.items())
    assert want in p and "never contradict them" in p
    a = bazi.compute(1990, 5, 15, 12, 0, bazi.CST)
    assert ", ".join(f"{bazi.ELEMENT_EN[e]} {n}" for e, n in _manual(a.pillars[:3]).items()) in p
    assert sum(counts.values()) == 6
    assert "Elements absent in BOTH: Wood." in p and "elements absent in A: Wood, Water." in p
    assert "Elements absent in B: Wood." in p


def test_count_elements_stems_and_branches():
    assert bazi.count_elements(["壬申"]) == {"木": 0, "火": 0, "土": 0, "金": 1, "水": 1}
    assert bazi.count_elements(["甲子", "丙午", "戊辰", "庚申"]) == {"木": 1, "火": 2, "土": 2, "金": 2, "水": 1}


# ---- 8) Chinese full-width brackets, draw-again
def test_zh_fullwidth_brackets():
    for k, v in i18n.T.items():
        assert "(" not in v["zh"] and ")" not in v["zh"], k
    for c in tarot.DECK:
        for rev in (False, True):
            s = tarot.fmt(c, rev, "zh")
            assert "(" not in s and ")" not in s, s
            assert tarot.label(c, rev, "zh").endswith(("（正位）", "（逆位）"))
    for g, verse, zh, en, ru in lots.LOTS:
        assert "(" not in zh and "(" not in verse
    for k in iching.KEY:
        assert "(" not in k[0]
    for s in dreams.SYMBOLS:
        assert "(" not in s[1]


async def test_tarot_again_buttons(eng):
    await ready(eng, 12, "zh")
    r = (await eng.callback(12, "tarot:1"))[0]
    assert ("🔄 再抽一张", "r:tarot:1") in r.buttons[0]
    assert "（" in r.text and "(正位)" not in r.text and "(逆位)" not in r.text
    await eng.callback(12, "m:tarot"); await eng.callback(12, "tarot:3")
    r = (await eng.text(12, "-"))[0]
    assert ("🔄 换个牌阵", "r:m:tarot") in r.buttons[0]


# ---- 9) Russian ё
YO = re.compile(r"\b(еще|Еще|черн\w*|Черн\w*|желт\w*|Желт\w*|зелен\w*|Зелен\w*|перевернут\w*|"
                r"(Пят|Шест|Сем|Восьм|Четв)ерк\w*|вперед|ребенок|ее|Ее|четк\w*|легк\w*|тяжел\w*|"
                r"\w+ьет|подъем|Подъем|объем|разъем|прием\w*|ряд|идет|придет|найдет|ждет|дает|растет|поймет)\b")


def _ru_strings():
    for k, v in i18n.T.items():
        yield k, v["ru"]
    for c in tarot.DECK:
        yield c.id, " ".join((c.names[2], c.upright[2], c.reversed[2]))
    for i, k in enumerate(iching.KEY):
        yield f"ic{i}", k[2] + " " + iching.RU[i]
    for n, l in enumerate(lots.LOTS):
        yield f"lot{n}", l[4]
    for s in dreams.SYMBOLS:
        yield "dream", s[3]
    yield "tips", " ".join(i18n.HOROSCOPE_TIPS["ru"])
    for v in i18n.DM_TRAITS.values():
        yield "dm", v["ru"]
    yield "fb", i18n.FALLBACK["ru"]
    for L in ("ru",):
        yield "meta", i18n.BOT_META[L]["desc"] + " " + i18n.BOT_META[L]["short"]
    yield "animals", " ".join(i18n.SHICHEN_ANIMALS["ru"])


def test_russian_uses_yo_consistently():
    bad = [(k, m.group(0)) for k, s in _ru_strings() for m in YO.finditer(s) if m.group(0) != "ряд"]
    assert bad == []
    from fortune_bot.prompts import system
    assert "ё" in system("tarot", "ru") and "«вы»" in system("tarot", "ru")


# ---- 10) bazi chart first, reading follows with typing
async def test_bazi_deferred_reading(eng, monkeypatch):
    eng.defer_followups = True

    async def slow(*a, **k):
        await asyncio.sleep(0.6)
        return "the reading"
    monkeypatch.setattr(llm, "complete", slow)
    await ready(eng, 13)
    rs = await birth(eng, 13)
    assert len(rs) == 1 and "Four Pillars" in rs[0].text and "the reading" not in rs[0].text
    assert rs[0].then is not None and not rs[0].buttons
    bot = AsyncMock()
    await app.send(bot, 13, rs)
    texts = [c.kwargs["text"] for c in bot.send_message.await_args_list]
    assert "Four Pillars" in texts[0] and "the reading" in texts[1]
    assert bot.send_chat_action.await_count >= 1
    assert bot.send_message.await_args_list[1].kwargs["reply_markup"] is not None


async def test_bazi_inline_when_not_deferred(eng):
    await ready(eng, 14)
    rs = await birth(eng, 14)
    assert len(rs) == 1 and rs[0].then is None and "Reading" in rs[0].text and rs[0].buttons
