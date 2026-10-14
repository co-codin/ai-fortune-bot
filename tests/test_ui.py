import asyncio
import os
import random
import re
from unittest.mock import AsyncMock, MagicMock

import pytest
from PIL import Image

from fortune_bot import app, tarot
from fortune_bot.engine import Engine, Reply
from fortune_bot.fmt import to_html
from fortune_bot.i18n import BOT_META, LANGS, SHICHEN, T, TOP_CITIES
from fortune_bot.storage import Store


@pytest.fixture
def eng(tmp_path, monkeypatch):
    for k in ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL"):
        monkeypatch.delenv(k, raising=False)
    return Engine(Store(str(tmp_path / "t.db")), bot_username="B", admin_ids=[], payments_enabled=False,
                  rate_per_min=100, rng=random.Random(5))


def cbs(r):
    return [c for row in r.buttons for _, c in row]


async def ready(eng, uid, L="en"):
    await eng.start(uid, L)
    await eng.callback(uid, f"onb:{L}")


async def test_onboarding_only_first_time(eng):
    rs = await eng.start(1, "ru-RU")
    assert "Добро пожаловать" in rs[0].text and "✅ Русский" in [b for b, _ in rs[0].buttons[0]]
    rs = await eng.callback(1, "onb:zh")
    assert rs[0].edit and "主菜单" not in rs[0].text and "AI 算命" in rs[0].text and "m:tarot" in cbs(rs[0])
    rs = await eng.start(1, "ru")                       # second /start: straight to menu, language kept
    assert "AI 算命" in rs[0].text and "m:bazi" in cbs(rs[0])


async def test_date_picker_shichen_and_city_buttons(eng):
    await ready(eng, 2)
    r = (await eng.callback(2, "m:bazi"))[0]
    assert r.edit and "dy:1990" in cbs(r) and "menu" in cbs(r)
    r = (await eng.callback(2, "dy:1990"))[0]
    assert cbs(r)[:10] == [f"yy:{y}" for y in range(1990, 2000)] and "back:date" in cbs(r)
    r = (await eng.callback(2, "back:date"))[0]
    assert "dy:1940" in cbs(r)
    await eng.callback(2, "dy:1990")
    r = (await eng.callback(2, "yy:2000"))[0]
    assert cbs(r)[:12] == [f"mm:{m}" for m in range(1, 13)]
    r = (await eng.callback(2, "mm:2"))[0]
    assert [c for c in cbs(r) if c.startswith("dd:")][-1] == "dd:29"   # leap year
    r = (await eng.callback(2, "dd:4"))[0]
    assert "2000-02-04" in r.text and len([c for c in cbs(r) if c.startswith("sc:")]) == 13 and "sc:-" in cbs(r)
    labels = [b for row in r.buttons for b, _ in row]
    assert "Rat 23–01" in labels and "Pig 21–23" in labels
    r = (await eng.callback(2, "sc:4"))[0]                            # 辰 -> 08:00
    assert [c for c in cbs(r)] == [f"city:{i}" for i in range(len(TOP_CITIES))] + ["city:?"]
    rs = await eng.callback(2, "city:0")                              # Beijing
    out = rs[0].text
    assert "2000-02-04 08:00" in out and "Beijing" in out
    assert eng.s.profile(2)["place"] == "Beijing" and eng.s.profile(2)["tz"] == "Asia/Shanghai"


async def test_other_city_prompt_then_typed(eng):
    await ready(eng, 3)
    await eng.callback(3, "m:astro")
    await eng.text(3, "1985-07-10"); await eng.text(3, "14:30")
    r = (await eng.callback(3, "city:?"))[0]
    assert "Berlin" in r.text and r.edit
    out = (await eng.text(3, "Europe/Berlin"))[0].text
    assert "Sun" in out and "♋" in out


async def test_unknown_time_bazi_three_pillars(eng):
    await ready(eng, 4)
    await eng.callback(4, "m:bazi")
    await eng.text(4, "2000-01-01")
    await eng.callback(4, "sc:-")
    out = (await eng.text(4, "+8"))[0].text
    assert "己卯" in out and "❔" in out and "three pillars" in out
    assert sum(int(n) for n in re.findall(r" (\d)$", out, re.M)) == 6   # 3 pillars x 2


async def test_saved_data_reuse(eng):
    await ready(eng, 5)
    await eng.callback(5, "m:bazi")
    await eng.text(5, "2000-01-01"); await eng.text(5, "00:00"); await eng.text(5, "Beijing")
    r = (await eng.callback(5, "m:astro"))[0]
    assert "1999" not in r.text and "2000-01-01" in r.text and "00:00" in r.text and "Beijing" in r.text
    assert cbs(r)[:2] == ["use:astro", "new:astro"]
    out = (await eng.callback(5, "use:astro"))[0].text
    assert "Capricorn" in out and "Ascendant" in out
    r = (await eng.callback(5, "m:bazi"))[0]
    out = (await eng.callback(5, "use:bazi"))[0].text
    assert "己卯" in out and "壬子" in out
    r = (await eng.callback(5, "new:bazi"))[0]
    assert "dy:1990" in cbs(r) and eng.s.get(5)["state"] == "c_date"


async def test_compat_with_picker(eng):
    await ready(eng, 6)
    await eng.callback(6, "m:compat")
    await eng.callback(6, "dy:1990"); await eng.callback(6, "yy:1990"); await eng.callback(6, "mm:5")
    r = (await eng.callback(6, "dd:15"))[0]
    assert "Person B" in r.text and "dy:1990" in cbs(r)
    out = (await eng.text(6, "1992-08-01"))[0].text
    assert "Taurus" in out and "Leo" in out


async def test_result_buttons_and_menu_edit(eng):
    await ready(eng, 7)
    r = (await eng.callback(7, "tarot:1"))[0]
    assert {"r:tarot:1", "share", "r:menu"} <= set(cbs(r))
    assert "Draw again" in str(r.buttons)
    r = (await eng.callback(7, "menu"))[0]
    assert r.edit and "m:compat" in cbs(r)
    r = (await eng.callback(7, "m:huangli"))[0]
    assert "r:menu" in cbs(r)


async def test_stale_buttons_ignored(eng):
    await ready(eng, 8)
    assert await eng.callback(8, "dd:5") == [] and await eng.callback(8, "sc:3") == []
    assert await eng.callback(8, "city:1") == [] and await eng.callback(8, "lang:xx") == []


async def test_friendly_errors_have_examples(eng):
    await ready(eng, 9, "ru")
    await eng.callback(9, "m:bazi")
    assert "1990-05-15" in (await eng.text(9, "вчера"))[0].text
    await eng.text(9, "1990-05-15")
    assert "08:05" in (await eng.text(9, "утром"))[0].text


def test_suit_emoji_and_images():
    assert {tarot.emoji(c) for c in tarot.DECK} == {"🌟", "🪄", "🍷", "⚔️", "🪙"}
    d = os.path.join(os.path.dirname(__file__), "..", "assets", "cards")
    for c in tarot.DECK:
        p = os.path.join(d, f"{c.id}.jpg")
        assert os.path.exists(p), c.id
        assert Image.open(p).format == "JPEG"


async def test_tarot_photos_attached_and_reversed_rotated(eng):
    await ready(eng, 10)
    await eng.callback(10, "tarot:3")
    r = (await eng.text(10, "-"))[0]
    assert len(r.photos) == 3
    path = r.photos[0][0]
    import io
    up = Image.open(io.BytesIO(app._photo(path, False)))
    rv = Image.open(io.BytesIO(app._photo(path, True)))
    assert up.size == rv.size
    # top-left pixel of the reversed image ≈ bottom-right of the original
    a, b = up.convert("RGB").getpixel((up.width - 3, up.height - 3)), rv.convert("RGB").getpixel((2, 2))
    assert sum(abs(x - y) for x, y in zip(a, b)) < 60
    e2 = Engine(eng.s, card_dir="/nonexistent")
    assert e2._card_photos(tarot.draw(1)) == []


def test_all_templates_render_to_valid_html():
    for key, tr in T.items():
        for L in LANGS:
            h = to_html(tr[L])
            for tag in ("b", "i", "code"):
                assert h.count(f"<{tag}>") == h.count(f"</{tag}>"), (key, L)
            assert "**" not in h, (key, L)


async def test_typing_only_for_slow_handlers():
    bot = AsyncMock()

    async def fast():
        return 1

    async def slow():
        await asyncio.sleep(0.6)
        return 2
    assert await app.with_typing(bot, 1, fast()) == 1
    bot.send_chat_action.assert_not_awaited()
    assert await app.with_typing(bot, 1, slow()) == 2
    assert bot.send_chat_action.await_args.kwargs["action"] == "typing"


async def test_edit_fallback_and_not_modified():
    from telegram.error import BadRequest
    bot = AsyncMock()
    msg = MagicMock(message_id=99)
    bot.edit_message_text.side_effect = BadRequest("Message is not modified")
    await app.send(bot, 1, [Reply("x", edit=True)], msg)
    bot.send_message.assert_not_awaited()
    bot.edit_message_text.side_effect = BadRequest("Message to edit not found")
    await app.send(bot, 1, [Reply("x", edit=True)], msg)
    bot.send_message.assert_awaited_once()


async def test_set_bot_profile_per_language():
    bot = AsyncMock()
    await app.set_bot_profile(bot)
    langs = {c.kwargs["language_code"] for c in bot.set_my_commands.await_args_list}
    assert langs == {None, "zh", "ru", "en"}
    assert {c.kwargs["language_code"] for c in bot.set_my_description.await_args_list} == {None, "zh", "ru"}
    for L in LANGS:
        assert len(BOT_META[L]["short"]) <= 120 and len(BOT_META[L]["desc"]) <= 512
        assert all(re.fullmatch(r"[a-z0-9_]{1,32}", c) and 1 <= len(d) <= 256 for c, d in BOT_META[L]["cmds"])
