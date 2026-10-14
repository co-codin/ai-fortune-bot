import random
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from fortune_bot import app, llm
from fortune_bot.engine import Engine, RateLimiter
from fortune_bot.storage import Store


@pytest.fixture(autouse=True)
def no_llm(monkeypatch):
    for k in ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL"):
        monkeypatch.delenv(k, raising=False)


@pytest.fixture
def eng(tmp_path):
    return Engine(Store(str(tmp_path / "t.db")), bot_username="TestFortuneBot", admin_ids=[1],
                  payments_enabled=False, rate_per_min=100, rng=random.Random(1))


def texts(rs):
    return "\n".join(r.text for r in rs)


async def onboard(eng, uid, code="en", lang=None):
    rs = await eng.start(uid, code)
    from fortune_bot.i18n import detect_lang
    await eng.callback(uid, f"onb:{lang or detect_lang(code)}")


async def test_bazi_conversation_zh(eng):
    rs = await eng.start(42, "zh-hans")
    assert "欢迎" in rs[0].text and "✅ 中文" in [b for b, _ in rs[0].buttons[0]]
    rs = await eng.callback(42, "onb:zh")
    assert rs[0].edit and "m:bazi" in [c for row in rs[0].buttons for _, c in row]
    assert "日期" in texts(await eng.callback(42, "m:bazi"))
    assert "1990-05-15" in texts(await eng.text(42, "hello"))      # friendly error with example
    assert "时辰" in texts(await eng.text(42, "2000-01-01"))
    assert "城市" in texts(await eng.text(42, "00:00"))
    assert "Europe/Berlin" in texts(await eng.text(42, "Xqzzyplace"))
    rs = await eng.text(42, "北京")
    out = rs[0].text
    assert "己卯" in out and "壬子" in out and "五行" in out and "解读" in out and "仅供娱乐" in out
    cbs = [c for row in rs[0].buttons for _, c in row]
    assert {"buy:yearly", "share", "r:m:bazi", "r:menu"} <= set(cbs)
    assert "即将上线" in texts(await eng.callback(42, "buy:yearly"))
    assert eng.s.get(42)["state"] is None and eng.s.profile(42)["tz"] == "Asia/Shanghai"


async def test_lang_switch_and_cancel(eng):
    await onboard(eng, 5)
    rs = await eng.lang_cmd(5)
    assert [c for _, c in rs[0].buttons[0]] == ["lang:zh", "lang:ru", "lang:en"]
    assert "✅ English" in [b for b, _ in rs[0].buttons[0]]
    rs = await eng.callback(5, "lang:ru")
    assert "русский" in rs[0].text and rs[0].edit
    await eng.begin(5, "bazi")
    assert texts(await eng.cancel(5)) == "Отменено."
    assert "/bazi" in texts(await eng.help(5))


async def test_tarot_spreads(eng):
    await onboard(eng, 7)
    rs = await eng.callback(7, "m:tarot")
    assert rs[0].edit and rs[0].buttons[0][0][1] == "tarot:1"
    rs = await eng.callback(7, "tarot:1")
    one = texts(rs)
    assert "Card of the day" in one and "entertainment" in one
    cbs = [c for row in rs[0].buttons for _, c in row]
    assert "r:tarot:1" in cbs and "r:menu" in cbs
    assert "question" in texts(await eng.callback(7, "tarot:3"))
    three = texts(await eng.text(7, "Will my project succeed?"))
    assert "**Past**:" in three and "**Present**:" in three and "**Future**:" in three and "Will my project" in three


async def test_astro_with_and_without_time(eng):
    await onboard(eng, 8, "ru")
    await eng.callback(8, "m:astro")
    await eng.text(8, "2024-09-18")
    await eng.text(8, "05:34")
    out = texts(await eng.text(8, "Москва"))
    assert "Дева" in out and "Рыбы" in out and "Асцендент" in out and "неизвестно" not in out
    rs = await eng.callback(8, "m:astro")
    assert "Использовать" in rs[0].text
    await eng.callback(8, "new:astro")
    await eng.text(8, "1990-04-20")
    await eng.text(8, "-")
    out = texts(await eng.text(8, "+3"))
    assert "Телец" in out and "нужно время" in out


async def test_compat(eng):
    await onboard(eng, 9)
    await eng.callback(9, "m:compat")
    await eng.text(9, "1990-05-15")
    out = texts(await eng.text(9, "1992-08-01"))
    assert "Taurus" in out and "Leo" in out and "Overall:" in out and "/100" in out


async def test_referral_and_share(eng):
    await eng.start(100, "en")
    rs = await eng.callback(100, "share")
    assert "https://t.me/TestFortuneBot?start=ref_100" in rs[0].text
    await eng.start(200, "en", "ref_100")
    await eng.start(200, "en", "ref_999")          # existing user: not overwritten
    await eng.start(300, "en", "ref_300")          # self-referral ignored
    await eng.start(400, "en", "ref_abc")          # garbage ignored
    assert eng.s.get(200)["referred_by"] == 100
    assert eng.s.get(300)["referred_by"] is None and eng.s.get(400)["referred_by"] is None


async def test_payments_flag(tmp_path):
    e = Engine(Store(str(tmp_path / "p.db")), admin_ids=[], payments_enabled=True, rate_per_min=100)
    await e.start(1, "en")
    rs = await e.callback(1, "buy:yearly")
    inv = rs[0].invoice
    assert inv["currency"] == "XTR" and inv["provider_token"] == "" and inv["prices"][0][1] == e.stars
    assert e.precheckout_ok(inv["payload"], "XTR", e.stars)
    assert not e.precheckout_ok(inv["payload"], "USD", e.stars) and not e.precheckout_ok("x", "XTR", e.stars)
    off = Engine(e.s, payments_enabled=False)
    assert not off.precheckout_ok(inv["payload"], "XTR", off.stars)


async def test_stats_admin_only(eng):
    await eng.start(1, "en"); await eng.start(2, "en")
    await eng.callback(2, "tarot:1")
    assert await eng.stats(2) == []
    out = texts(await eng.stats(1))
    assert "Users: 2" in out and "tarot: 1" in out


async def test_rate_limit(tmp_path):
    e = Engine(Store(str(tmp_path / "r.db")), rate_per_min=2, rng=random.Random(0))
    await e.start(1, "en")
    await e.callback(1, "tarot:1"); await e.callback(1, "tarot:1")
    assert "Too many" in texts(await e.callback(1, "tarot:1"))
    rl = RateLimiter(1)
    assert rl.allow(1, 0) and not rl.allow(1, 30) and rl.allow(1, 61)


async def test_daily(eng):
    await eng.start(11, "en")
    assert "Save your birth" in texts(await eng.daily_cmd(11, ["on"]))
    await eng.begin(11, "bazi")
    await eng.text(11, "1990-05-15"); await eng.text(11, "08:00"); await eng.text(11, "Moscow")
    assert eng.s.profile(11)["tz"] == "Europe/Moscow"
    assert "Usage" in texts(await eng.daily_cmd(11, ["on", "25"]))
    assert "08:00" in texts(await eng.daily_cmd(11, ["on", "8"]))
    # 05:00 UTC = 08:00 Moscow -> due once
    now = datetime(2026, 10, 13, 5, 3, tzinfo=timezone.utc)
    assert eng.due_daily(datetime(2026, 10, 13, 4, 59, tzinfo=timezone.utc)) == []
    due = eng.due_daily(now)
    assert [u for u, _ in due] == [11]
    msg = texts(await eng.daily_message(*due[0]))
    assert "Day pillar: **庚申**" in msg and "Card of the day" in msg and "Taurus" in msg
    assert eng.due_daily(now) == []                    # not twice the same day
    await eng.daily_cmd(11, ["off"])
    assert eng.s.get(11)["daily_on"] == 0


async def test_huangli_menu(eng):
    await eng.start(12, "zh")
    out = texts(await eng.callback(12, "m:huangli"))
    assert "宜" in out and "忌" in out


async def test_llm_used_when_configured(eng, monkeypatch):
    monkeypatch.setattr(llm, "complete", AsyncMock(return_value="AI SAYS HI"))
    await eng.start(13, "en")
    assert "AI SAYS HI" in texts(await eng.callback(13, "tarot:1"))


async def test_llm_http_failure_falls_back(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "http://127.0.0.1:9"); monkeypatch.setenv("LLM_API_KEY", "x")
    monkeypatch.setenv("LLM_MODEL", "m"); monkeypatch.setenv("LLM_TIMEOUT", "2")
    assert llm.configured() and await llm.complete("hi", "en") is None


# ---------- Telegram adapter with a mocked Bot ----------
def _update(uid=77, text=None, data=None, lang="en"):
    u = MagicMock()
    u.effective_user.id, u.effective_user.language_code = uid, lang
    u.effective_chat.id = uid
    u.message.text = text
    if data:
        u.callback_query.data = data
        u.callback_query.answer = AsyncMock()
    return u


async def test_telegram_adapter(eng):
    handlers = {getattr(h, "commands", None) and next(iter(h.commands)) or type(h).__name__ + str(i): h
                for i, h in enumerate(app.build_handlers(eng))}
    ctx = MagicMock(); ctx.bot = AsyncMock(); ctx.args = []
    await handlers["start"].callback(_update(), ctx)
    kw = ctx.bot.send_message.await_args.kwargs
    assert "Welcome" in kw["text"] and kw["parse_mode"] == "HTML"
    assert [b.callback_data for b in kw["reply_markup"].inline_keyboard[0]] == ["onb:zh", "onb:ru", "onb:en"]
    ctx.bot.reset_mock()
    cbh = next(h for k, h in handlers.items() if k.startswith("CallbackQueryHandler"))
    upd = _update(data="onb:en")
    await cbh.callback(upd, ctx)
    upd.callback_query.answer.assert_awaited()
    kw = ctx.bot.edit_message_text.await_args.kwargs          # edited in place
    assert kw["message_id"] == upd.callback_query.message.message_id
    assert [b.callback_data for b in kw["reply_markup"].inline_keyboard[0]] == ["m:bazi", "m:tarot", "m:astro"]
    ctx.bot.reset_mock()
    await cbh.callback(_update(data="tarot:1"), ctx)
    assert "Card of the day" in ctx.bot.send_message.await_args.kwargs["text"]
    ctx.bot.send_photo.assert_awaited()                        # card image
    # text message handler drives the BaZi flow
    await handlers["bazi"].callback(_update(), ctx)
    txt = [h for k, h in handlers.items() if k.startswith("MessageHandler")][-1]
    for m in ("2000-01-01", "00:00", "+8"):
        await txt.callback(_update(text=m), ctx)
    assert "己卯" in ctx.bot.send_message.await_args.kwargs["text"]
    # invoice rendering
    eng.payments = True
    ctx.bot.reset_mock()
    await cbh.callback(_update(data="buy:yearly"), ctx)
    kw = ctx.bot.send_invoice.await_args.kwargs
    assert kw["currency"] == "XTR" and kw["prices"][0].amount == eng.stars and kw["provider_token"] == ""


async def test_daily_job(eng):
    await eng.start(11, "en")
    await eng.begin(11, "bazi")
    await eng.text(11, "1990-05-15"); await eng.text(11, "08:00"); await eng.text(11, "UTC")
    hour = datetime.now(timezone.utc).hour
    await eng.daily_cmd(11, ["on", str(hour)])
    ctx = MagicMock(); ctx.bot = AsyncMock(); ctx.job.data = eng
    await app.daily_job(ctx)
    assert ctx.bot.send_message.await_count == 1
    await app.daily_job(ctx)
    assert ctx.bot.send_message.await_count == 1
