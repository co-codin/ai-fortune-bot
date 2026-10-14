"""Telegram-independent bot logic. Handlers return a list of Reply objects that the
adapter (app.py) renders. Text may use **bold**, *italic* and `code`; the adapter
escapes everything else (fmt.to_html), so user/LLM text can't inject HTML."""
from __future__ import annotations

import calendar
import hashlib
import json
import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from . import astro, bazi, dreams, iching, llm, lots, lucky, tarot
from .i18n import (DM_TRAITS, ELEMENT_NAMES, FALLBACK, HOROSCOPE_TIPS, LANGS, SHICHEN, TOP_CITIES, detect_lang, shichen_label, t)
from .storage import Store

LANG_BTNS = [("中文", "zh"), ("Русский", "ru"), ("English", "en")]
DECADES = list(range(1940, 2030, 10))


@dataclass
class Reply:
    text: str
    buttons: list = field(default_factory=list)   # rows of (label, callback_data)
    invoice: dict | None = None
    edit: bool = False                            # edit the message the button was on
    photos: list = field(default_factory=list)    # [(path, reversed)]
    clear_kb: bool = False                        # control reply: remove keyboard from the pressed message
    then: object = None                           # async callable -> list[Reply], sent after this one (with typing)


def _tz_from_label(label: str):
    if label.startswith("UTC") and len(label) > 3:
        return bazi.parse_tz(label[3:])[0]
    if label == "UTC":
        return timezone.utc
    return ZoneInfo(label)


class RateLimiter:
    def __init__(self, per_minute: int):
        self.n, self.hits = per_minute, defaultdict(deque)

    def allow(self, uid, now=None) -> bool:
        now = time.monotonic() if now is None else now
        q = self.hits[uid]
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= self.n:
            return False
        q.append(now)
        return True


class Engine:
    def __init__(self, store: Store, bot_username: str = "", admin_ids=None, payments_enabled=None,
                 rate_per_min=None, rng=None, card_dir=None):
        self.s = store
        self.bot_username = bot_username or os.getenv("BOT_USERNAME", "")
        self.admins = set(admin_ids if admin_ids is not None else
                          [int(x) for x in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",") if x])
        self.payments = (os.getenv("PAYMENTS_ENABLED", "false").lower() == "true"
                         if payments_enabled is None else payments_enabled)
        self.stars = int(os.getenv("PREMIUM_STARS", "100"))
        self.rl = RateLimiter(rate_per_min or int(os.getenv("RATE_LIMIT_PER_MIN", "6")))
        self.rng = rng or tarot._rng
        self.defer_followups = False   # app.py turns this on
        self.card_dir = card_dir if card_dir is not None else os.path.join(os.path.dirname(__file__), "..", "assets", "cards")

    # ---------- helpers ----------
    def lang(self, uid, code=None):
        self.s.ensure(uid, detect_lang(code))
        return self.s.get(uid)["lang"]

    def _menu_buttons(self, L):
        return [[(t("btn_bazi", L), "m:bazi"), (t("btn_tarot", L), "m:tarot"), (t("btn_astro", L), "m:astro")],
                [(t("btn_compat", L), "m:compat"), (t("btn_dream", L), "m:dream"), (t("btn_lot", L), "m:lot")],
                [(t("btn_iching", L), "m:iching"), (t("btn_lucky", L), "m:lucky"), (t("btn_huangli", L), "m:huangli")],
                [(t("btn_lang", L), "m:lang"), (t("btn_help", L), "m:help")]]

    def menu(self, L, edit=False, text_key="menu"):
        return Reply(t(text_key, L), self._menu_buttons(L), edit=edit)

    def _limited(self, uid, L):
        return None if self.rl.allow(uid) else [Reply(t("rate_limited", L), [[(t("btn_menu", L), "r:menu")]])]

    def _result_buttons(self, L, mode, yearly=False, again=None):
        """Buttons under a RESULT message. They carry the 'r:' prefix: pressing them never edits
        the result (the reading stays), the answer is sent as a new message."""
        label, target = again or (t("btn_another_spread" if mode == "tarot" else "btn_again", L), f"m:{mode}")
        rows = [[(t("yearly_btn", L), "buy:yearly")]] if yearly else []
        rows.append([(label, f"r:{target}"), (t("btn_share", L), "share")])
        rows.append([(t("btn_menu", L), "r:menu")])
        return rows

    def _reset(self, uid):
        self.s.set(uid, state=None, data={})

    # ---------- commands ----------
    async def start(self, uid, code=None, arg: str = ""):
        new = self.s.ensure(uid, detect_lang(code))
        if new and arg.startswith("ref_"):
            try:
                ref = int(arg[4:])
                if ref != uid and self.s.get(ref):
                    self.s.set(uid, referred_by=ref)
            except ValueError:
                pass
        self._reset(uid)
        L = self.s.get(uid)["lang"]
        if new:  # first-run onboarding: language picker, Telegram language preselected
            return [Reply(t("onboard", L), [[(("✅ " if c == L else "") + n, f"onb:{c}") for n, c in LANG_BTNS]])]
        return [self.menu(L, text_key="start")]

    async def help(self, uid, code=None):
        L = self.lang(uid, code)
        return [Reply(t("help", L), [[(t("btn_menu", L), "menu")]])]

    async def cancel(self, uid, code=None):
        L = self.lang(uid, code)
        self._reset(uid)
        return [Reply(t("cancelled", L), self._menu_buttons(L))]

    async def lang_cmd(self, uid, code=None, edit=False):
        L = self.lang(uid, code)
        return [Reply(t("choose_lang", L), [[(("✅ " if c == L else "") + n, f"lang:{c}") for n, c in LANG_BTNS],
                                            [(t("btn_menu", L), "menu")]], edit=edit)]

    async def begin(self, uid, mode, code=None, edit=False):
        L = self.lang(uid, code)
        self._reset(uid)
        if mode in ("bazi", "astro"):
            p = self.s.profile(uid)
            if p:
                return [Reply(t("use_saved", L, summary=self._summary(p, L)),
                              [[(t("btn_use_saved", L), f"use:{mode}")], [(t("btn_new_data", L), f"new:{mode}")],
                               [(t("btn_menu", L), "menu")]], edit=edit)]
            return [self._collect_start(uid, mode, L, edit)]
        if mode == "compat":
            p = self.s.profile(uid)
            if p:
                return [Reply(t("compat_saved", L, summary=self._summary(p, L)),
                              [[(t("btn_use_saved_a", L), "use:compat")], [(t("btn_new_data", L), "new:compat")],
                               [(t("btn_menu", L), "menu")]], edit=edit)]
            return [self._collect_start(uid, "compat", L, edit)]
        if mode == "tarot":
            return [Reply(t("tarot_choose", L), [[(t("btn_tarot1", L), "tarot:1")], [(t("btn_tarot3", L), "tarot:3")],
                                                  [(t("btn_menu", L), "menu")]], edit=edit)]
        if mode == "huangli":
            return await self.huangli(uid)
        if mode == "lucky":
            return await self.lucky_today(uid)
        if mode == "dream":
            self.s.set(uid, state="dream_q")
            return [Reply(t("ask_dream", L), [[(t("btn_menu", L), "menu")]], edit=edit)]
        if mode == "lot":
            self.s.set(uid, state="lot_q")
            return [Reply(t("ask_lot", L), [[(t("btn_draw_now", L), "lot:go")], [(t("btn_menu", L), "menu")]], edit=edit)]
        if mode == "iching":
            self.s.set(uid, state="iching_q")
            return [Reply(t("ask_iching", L), [[(t("btn_cast_now", L), "ic:go")], [(t("btn_menu", L), "menu")]], edit=edit)]
        if mode == "lang":
            return await self.lang_cmd(uid, edit=edit)
        if mode == "help":
            r = (await self.help(uid))[0]
            r.edit = edit
            return [r]
        return [self.menu(L, edit=edit)]

    def _summary(self, p, L):
        d = "-".join(f"{x:02d}" if i else str(x) for i, x in enumerate(p["date"]))
        tm = f"{p['time'][0]:02d}:{p['time'][1]:02d}" if p.get("time") else "?"
        return f"📅 {d}  🕰 {tm}  📍 {p.get('place') or p['tz']}"

    DEFAULT_TZ = {"zh": "Asia/Shanghai", "ru": "Europe/Moscow", "en": "UTC"}

    def user_tz(self, uid):
        """Current timezone for 'today': explicit /tz setting > saved birth place > language default."""
        row = self.s.get(uid)
        if row["tz"]:
            return _tz_from_label(row["tz"]), row["tz"], "set"
        p = self.s.profile(uid)
        if p:
            return _tz_from_label(p["tz"]), p["tz"], "birth"
        label = self.DEFAULT_TZ.get(row["lang"], "UTC")
        return _tz_from_label(label), label, "default"

    def _today_line(self, uid, L, now):
        _, label, src = self.user_tz(uid)
        return t("today_tz", L, date=now.strftime("%Y-%m-%d"), tz=label)

    def _tz_hint(self, uid, L):
        _, label, src = self.user_tz(uid)
        return "" if src == "set" else "\n\n" + t("tz_hint", L, tz=label)

    async def tz_cmd(self, uid, args):
        L = self.lang(uid)
        if not args:
            _, label, _ = self.user_tz(uid)
            return [Reply(t("tz_usage", L, tz=label))]
        try:
            _, label = bazi.parse_tz(" ".join(args)[:60])
        except bazi.ParseError:
            return [Reply(t("bad_tz", L))]
        self.s.set(uid, tz=label)
        return [Reply(t("tz_set", L, tz=label))]

    async def huangli(self, uid):
        L = self.lang(uid)
        now = datetime.now(self.user_tz(uid)[0])
        h = bazi.huangli(now)
        self.s.log_reading(uid, "huangli")
        return [Reply(t("huangli", L, date=self._today_line(uid, L, now), lunar=h["lunar"], day=h["day"],
                        yi="、".join(h["yi"]) or "-", ji="、".join(h["ji"]) or "-") + self._tz_hint(uid, L),
                      [[(t("btn_menu", L), "r:menu")]])]

    async def daily_cmd(self, uid, args: list[str]):
        L = self.lang(uid)
        if args[:1] == ["off"]:
            self.s.set(uid, daily_on=0)
            return [Reply(t("daily_off", L))]
        if args[:1] != ["on"]:
            return [Reply(t("daily_usage", L))]
        p = self.s.profile(uid)
        if not p:
            return [Reply(t("daily_need_profile", L), [[(t("btn_bazi", L), "m:bazi"), (t("btn_astro", L), "m:astro")]])]
        hour = 9
        if len(args) > 1:
            if not args[1].isdigit() or not 0 <= int(args[1]) <= 23:
                return [Reply(t("daily_usage", L))]
            hour = int(args[1])
        self.s.set(uid, daily_on=1, daily_hour=hour)
        return [Reply(t("daily_on", L, hour=f"{hour:02d}", tz=p["tz"]))]

    async def stats(self, uid):
        if uid not in self.admins:
            return []
        L = self.lang(uid)
        st = self.s.stats()
        modes = "\n".join(f"  {k}: {v}" for k, v in sorted(st["modes"].items())) or "  -"
        return [Reply(t("stats", L, users=st["users"], refs=st["refs"], daily=st["daily"], modes=modes))]

    # ---------- birth-data collection (pickers + typed input) ----------
    def _collect_start(self, uid, mode, L, edit=False):
        self.s.set(uid, state="c_date", data={"mode": mode})
        key = "ask_date_a" if mode == "compat" else "ask_date"
        return Reply(t(key, L), self._decade_buttons(L), edit=edit)

    def _decade_buttons(self, L):
        btns = [(f"{d}s", f"dy:{d}") for d in DECADES]
        return [btns[i:i + 3] for i in range(0, len(btns), 3)] + [[(t("btn_menu", L), "menu")]]

    async def _date_done(self, uid, L, date, edit=False):
        d = self.s.data(uid)
        mode = d.get("mode")
        if mode == "compat":
            if "a" not in d:
                d["a"] = date
                self.s.set(uid, state="c_date", data=d)
                return [Reply(t("ask_date_b", L), self._decade_buttons(L), edit=edit)]
            d["b"] = date
            return await self._finish_compat(uid, L, d)
        d["date"] = date
        self.s.set(uid, state="c_time", data=d)
        rows = [[(shichen_label(i, L), f"sc:{i}") for i in range(r, r + 3)] for r in range(0, 12, 3)]
        rows.append([(t("btn_unknown_time", L), "sc:-")])
        ds = f"{date[0]}-{date[1]:02d}-{date[2]:02d}"
        return [Reply(t("ask_time", L, date=ds), rows, edit=edit)]

    async def _time_done(self, uid, L, tm, edit=False):
        d = self.s.data(uid)
        d["time"] = tm
        self.s.set(uid, state="c_place", data=d)
        idx = {"zh": 1, "ru": 2, "en": 3}[L]
        cities = [(c[idx], f"city:{i}") for i, c in enumerate(TOP_CITIES)]
        rows = [cities[i:i + 2] for i in range(0, len(cities), 2)] + [[(t("btn_other_city", L), "city:?")]]
        return [Reply(t("ask_tz", L), rows, edit=edit)]

    async def _place_done(self, uid, L, text, display=None):
        tz, label, ll = bazi.parse_place(text)
        d = self.s.data(uid)
        d["place"] = (display or text.strip())[:40]
        if d.get("mode") == "bazi":
            return await self._finish_bazi(uid, L, d, tz, label, ll)
        return await self._finish_astro(uid, L, d, tz, label, ll)

    # ---------- callbacks ----------
    async def callback(self, uid, data: str, code=None):
        """Callback data can be forged by modified clients: anything malformed is ignored."""
        if not isinstance(data, str) or len(data) > 64:
            return []
        try:
            return await self._callback(uid, data, code)
        except (ValueError, IndexError, KeyError, TypeError):
            return []

    async def _callback(self, uid, data: str, code=None):
        if data.startswith("r:"):  # pressed under a result: keep the result, answer with new messages
            out = await self._callback(uid, data[2:], code)
            for r in out:
                r.edit = False
            return ([Reply("", clear_kb=True)] + out) if out else []
        L = self.lang(uid, code)
        st, d = self.s.get(uid)["state"], self.s.data(uid)
        if data.startswith(("lang:", "onb:")):
            new = data.split(":", 1)[1]
            if new not in LANGS:
                return []
            self.s.set(uid, lang=new)
            key = "start" if data.startswith("onb:") else "menu"
            return [Reply(t("lang_set", new) + "\n\n" + t(key, new), self._menu_buttons(new), edit=True)]
        if data == "menu":
            self._reset(uid)
            return [self.menu(L, edit=True)]
        if data.startswith("m:"):
            return await self.begin(uid, data[2:], edit=True)
        if data.startswith(("use:", "new:")):
            mode = data[4:]
            if mode not in ("bazi", "astro", "compat"):
                return []
            p = self.s.profile(uid)
            if data.startswith("new:") or not p:
                return [self._collect_start(uid, mode, L, edit=True)]
            if mode == "compat":
                self.s.set(uid, state="c_date", data={"mode": "compat", "a": p["date"]})
                return [Reply(t("ask_date_b", L), self._decade_buttons(L), edit=True)]
            dd = {"mode": mode, "date": p["date"], "time": p.get("time"), "place": p.get("place") or p["tz"]}
            tz = _tz_from_label(p["tz"])
            ll = tuple(p["ll"]) if p.get("ll") else None
            if mode == "bazi":
                return await self._finish_bazi(uid, L, dd, tz, p["tz"], ll)
            return await self._finish_astro(uid, L, dd, tz, p["tz"], ll)
        # date picker
        if st == "c_date" and data.startswith("dy:"):
            y0 = int(data[3:])
            if y0 not in DECADES:
                return []
            ys = [(str(y), f"yy:{y}") for y in range(y0, y0 + 10) if 1900 <= y <= datetime.now().year]
            rows = [ys[i:i + 5] for i in range(0, len(ys), 5)] + [[(t("btn_back", L), "back:date")]]
            return [Reply(t("pick_year", L), rows, edit=True)]
        if st == "c_date" and data == "back:date":
            return [Reply(t("ask_date_b" if "a" in d else ("ask_date_a" if d.get("mode") == "compat" else "ask_date"), L),
                          self._decade_buttons(L), edit=True)]
        if st == "c_date" and data.startswith("yy:"):
            d["y"] = int(data[3:])
            if not 1900 <= d["y"] <= datetime.now().year:
                return []
            self.s.set(uid, data=d)
            ms = [(f"{m:02d}", f"mm:{m}") for m in range(1, 13)]
            return [Reply(t("pick_month", L, y=d["y"]), [ms[i:i + 4] for i in range(0, 12, 4)] + [[(t("btn_back", L), f"dy:{d['y'] // 10 * 10}")]], edit=True)]
        if st == "c_date" and data.startswith("mm:") and "y" in d:
            d["m"] = int(data[3:])
            if not 1 <= d["m"] <= 12:
                return []
            self.s.set(uid, data=d)
            n = calendar.monthrange(d["y"], d["m"])[1]
            ds = [(str(x), f"dd:{x}") for x in range(1, n + 1)]
            return [Reply(t("pick_day", L, y=d["y"], m=d["m"]), [ds[i:i + 7] for i in range(0, n, 7)] + [[(t("btn_back", L), f"yy:{d['y']}")]], edit=True)]
        if st == "c_date" and data.startswith("dd:") and "m" in d:
            day = int(data[3:])
            if not 1 <= day <= calendar.monthrange(d["y"], d["m"])[1]:
                return []
            date = (d.pop("y"), d.pop("m"), day)
            self.s.set(uid, data=d)
            return await self._date_done(uid, L, date, edit=True)
        if st == "c_time" and data.startswith("sc:"):
            i = None if data == "sc:-" else int(data[3:])
            if i is not None and not 0 <= i < 12:
                return []
            tm = None if i is None else list(SHICHEN[i][2])
            return await self._time_done(uid, L, tm, edit=True)
        if st == "c_place" and data.startswith("city:"):
            if data == "city:?":
                return [Reply(t("type_city", L), edit=True)]
            i = int(data[5:])
            if not 0 <= i < len(TOP_CITIES):
                return []
            c = TOP_CITIES[i]
            return await self._place_done(uid, L, c[0], c[{"zh": 1, "ru": 2, "en": 3}[L]])
        if data == "lot:go" and st == "lot_q":
            return await self.lot(uid, "")
        if data == "ic:go" and st == "iching_q":
            return await self.iching_cast(uid, "")
        if data == "tarot:1":
            return await self.tarot(uid, 1, "")
        if data == "tarot:3":
            self.s.set(uid, state="tarot_q", data={})
            return [Reply(t("ask_question", L), [[(t("btn_back", L), "m:tarot")]], edit=True)]
        if data == "share":
            link = f"https://t.me/{self.bot_username}?start=ref_{uid}"
            return [Reply(t("share", L, link=link))]
        if data == "buy:yearly":
            if not self.payments:
                return [Reply(t("coming_soon", L), [[(t("btn_menu", L), "r:menu")]])]
            return [Reply(t("invoice_title", L), invoice={
                "title": t("invoice_title", L), "description": t("invoice_desc", L),
                "payload": f"yearly:{uid}", "currency": "XTR", "provider_token": "",
                "prices": [(t("invoice_title", L), self.stars)]})]
        return []  # stale button (e.g. picker from an old conversation): ignore

    def precheckout_ok(self, payload: str, currency: str, amount: int) -> bool:
        return self.payments and currency == "XTR" and amount == self.stars and payload.startswith("yearly:")

    async def paid(self, uid, payload, amount, charge_id):
        self.s.log_payment(uid, payload, amount, charge_id)
        return [Reply(t("paid_thanks", self.lang(uid)))]

    # ---------- free text ----------
    async def text(self, uid, text: str, code=None):
        L = self.lang(uid, code)
        st = self.s.get(uid)["state"]
        try:
            if st in ("c_date", "c_time", "c_place") and len(text) > 100:
                raise bazi.ParseError({"c_date": "date", "c_time": "time"}.get(st, "tz"))
            if st == "c_date":
                return await self._date_done(uid, L, bazi.parse_date(text))
            if st == "c_time":
                tm = None if text.strip() in ("-", "?") else list(bazi.parse_time(text))
                return await self._time_done(uid, L, tm)
            if st == "c_place":
                return await self._place_done(uid, L, text)
            if st in ("tarot_q", "lot_q", "iching_q"):
                q = "" if text.strip() == "-" else text.strip()
                if len(q) > 300:
                    return [Reply(t("too_long", L, n=300))]
                fn = {"tarot_q": lambda: self.tarot(uid, 3, q), "lot_q": lambda: self.lot(uid, q),
                      "iching_q": lambda: self.iching_cast(uid, q)}[st]
                return await fn()
            if st == "dream_q":
                dream = text.strip()
                if len(dream) < 10:
                    return [Reply(t("dream_too_short", L))]
                if len(dream) > 1500:
                    return [Reply(t("too_long", L, n=1500))]
                return await self.dream(uid, dream)
        except bazi.ParseError as e:
            return [Reply(t({"date": "bad_date", "time": "bad_time"}.get(str(e), "bad_tz"), L))]
        return [self.menu(L)]

    # ---------- readings ----------
    def _save_profile(self, uid, d, label, ll, **extra):
        p = self.s.profile(uid) or {}
        if (p.get("date"), p.get("time"), p.get("tz")) != (d["date"], d.get("time"), label):
            p = {}  # new person/birth data: drop derived fields
        p.update({"date": d["date"], "time": d.get("time"), "tz": label, "ll": ll, "place": d.get("place")})
        p.update({k: v for k, v in extra.items()})
        self.s.set(uid, profile=p)
        return p

    async def _finish_bazi(self, uid, L, d, tz, label, ll):
        if lim := self._limited(uid, L):
            return lim
        known = d.get("time") is not None
        hh, mm = d["time"] if known else (12, 0)
        b = bazi.compute(*d["date"], hh, mm, tz, label)
        if not known:
            b.elements = bazi.count_elements(b.pillars[:3])
        self._save_profile(uid, d, label, ll, dm=b.day_master)
        names = ELEMENT_NAMES[L]
        mx = max(max(b.elements.values()), 1)
        bars = "\n".join(f"{names[e]} {'🟩' * n}{'⬜' * (mx - n)} {n}" for e, n in b.elements.items())
        chart = t("chart", L, dt=b.local_dt.strftime("%Y-%m-%d %H:%M" if known else "%Y-%m-%d"),
                  tz=d.get("place") or label, y=b.year, m=b.month, d=b.day, h=b.hour if known else "❔",
                  dm=b.day_master, dme=names[b.day_master_element], bars=bars)
        if not known:
            chart += "\n" + t("hour_unknown_note", L)
        pillars = f"year {b.year}, month {b.month}, day {b.day}" + (f", hour {b.hour}" if known else " (hour unknown)")
        prompt = (f"BaZi pillars: {pillars}. Day master {b.day_master} ({b.day_master_element}). "
                  f"Five-element counts: {b.elements}. Give a basic personality reading and gentle advice for balance, "
                  "in 3 short paragraphs.")
        self._reset(uid)
        self.s.log_reading(uid, "bazi")

        async def reading():
            interp = await llm.complete(prompt, L, mode="bazi", words=200) or self._bazi_fallback(b, L)
            return [Reply(f"{t('reading_head', L)}\n{interp}\n\n*{t('disclaimer', L)}*",
                          self._result_buttons(L, "bazi", yearly=True))]
        if self.defer_followups:   # Telegram: show the chart now, the reading follows (with "typing…")
            return [Reply(chart, then=reading)]
        r = (await reading())[0]
        return [Reply(f"{chart}\n\n{r.text}", r.buttons)]

    def _bazi_fallback(self, b, L):
        names = ELEMENT_NAMES[L]
        strong = max(b.elements, key=b.elements.get)
        weak = min(b.elements, key=b.elements.get)
        return FALLBACK[L].format(dm=b.day_master, dme=names[b.day_master_element],
                                  trait=DM_TRAITS[b.day_master_element][L], strong=names[strong],
                                  weak=names[weak]).split("\n", 1)[-1]

    async def _finish_astro(self, uid, L, d, tz, label, ll):
        if lim := self._limited(uid, L):
            return lim
        known = d.get("time") is not None
        hh, mm = d["time"] if known else (12, 0)
        dt = datetime(*d["date"], hh, mm, tzinfo=tz)
        c = astro.chart(dt, ll if known else None)
        N = astro.SIGN_NAMES[L]
        moon = f"{astro.SIGN_EMOJI[c['moon']]} {N[c['moon']]}" + ("" if known else " " + t("moon_approx", L))
        asc = (f"{astro.SIGN_EMOJI[c['asc']]} {N[c['asc']]}" if c["asc"] else
               t("na_time", L) if not known else t("na_place", L))
        text = t("astro_chart", L, sun=f"{astro.SIGN_EMOJI[c['sun']]} **{N[c['sun']]}**", moon=moon, asc=asc)
        p = self._save_profile(uid, d, label, ll, sun=c["sun"], moon=c["moon"] if known else None, asc=c["asc"])
        horo = await self.horoscope(c["sun"], L, datetime.now(self.user_tz(uid)[0]), p["moon"], c["asc"])
        self._reset(uid)
        self.s.log_reading(uid, "astro")
        return [Reply(f"{text}\n\n{t('horo_head', L)}\n{horo}\n\n*{t('disclaimer', L)}*", self._result_buttons(L, "astro"))]

    async def horoscope(self, sign, L, now, moon=None, asc=None):
        """`now` is a datetime in the user's timezone (or a date)."""
        day = now.date() if isinstance(now, datetime) else now
        when = now if isinstance(now, datetime) else datetime(day.year, day.month, day.day, 12, tzinfo=timezone.utc)
        transit = astro.sign_of(astro.body_longitude(astro.ephem.Moon, when))
        extra = (f" NATAL Moon sign (at birth): {moon}." if moon else "") + (f" NATAL Ascendant: {asc}." if asc else "")
        ai = await llm.complete(f"Write a short daily horoscope for {day.isoformat()}. NATAL Sun sign (at birth): {sign}.{extra} "
                                f"TODAY'S TRANSITING Moon is in {transit}. Natal placements describe the person; the transiting "
                                "Moon describes today's mood. Never call a natal placement 'today's'. "
                                "Weave in the natal moon (emotional nature) and ascendant (outer approach) when given. "
                                "Cover mood, relationships and work in 3 short paragraphs.", L, 450, mode="astro", words=130)
        if ai:
            return ai
        idx = int(hashlib.sha256(f"{sign}{day}".encode()).hexdigest(), 16) % len(HOROSCOPE_TIPS[L])
        return t("horoscope_fallback", L, sign=astro.SIGN_NAMES[L][sign], tip=HOROSCOPE_TIPS[L][idx])

    def _card_photos(self, cards):
        out = []
        for c, r in cards:
            p = os.path.join(self.card_dir, f"{c.id}.jpg")
            if os.path.exists(p):
                out.append((p, r))
        return out if len(out) == len(cards) else []

    async def tarot(self, uid, n, question):
        L = self.lang(uid)
        if lim := self._limited(uid, L):
            return lim
        cards = tarot.draw(n, self.rng)
        pos = ["card of the day"] if n == 1 else ["past", "present", "future"]
        posL = [t("tarot_daily_title", L)] if n == 1 else t("tarot_pos", L).split("|")
        prompt = ("Tarot reading. " + (f"The user's question: \"{question}\". " if question else "No specific question; give general guidance. ") +
                  "Cards: " + "; ".join(f"{pos[i]}: {c.name('en')} ({'reversed' if r else 'upright'})" for i, (c, r) in enumerate(cards)) +
                  ". For EACH card write one line '<position>: <card> — <meaning>' interpreting that card for its position and for "
                  "the question's actual topic (do not assume love/career unless the question is about it). Then a 2-3 sentence overall summary.")
        ai = await llm.complete(prompt, L, mode="tarot", words=190 if n == 3 else 110)
        head = ["**" + (t("tarot_daily_title", L) if n == 1 else "🃏 " + t("btn_tarot3", L).split(" ", 1)[1]) + "**"]
        pre = (lambda i: "") if n == 1 else (lambda i: f"**{posL[i]}**: ")
        if question:
            head.append(f"❓ *{question}*")
        if ai:
            lines = [f"{tarot.emoji(c)} {pre(i)}{tarot.label(c, r, L)}" for i, (c, r) in enumerate(cards)]
            body = "\n".join(head) + "\n\n" + "\n".join(lines) + f"\n\n{t('reading_head', L)}\n{ai}"
        else:
            lines = [f"{tarot.emoji(c)} {pre(i)}{tarot.fmt(c, r, L)}" for i, (c, r) in enumerate(cards)]
            body = "\n".join(head) + "\n\n" + "\n".join(lines) + "\n\n" + t("tarot_fallback_neutral", L)
        self._reset(uid)
        self.s.log_reading(uid, "tarot")
        again = (t("btn_draw_again", L), "tarot:1") if n == 1 else None
        return [Reply(f"{body}\n\n*{t('disclaimer', L)}*", self._result_buttons(L, "tarot", again=again),
                      photos=self._card_photos(cards))]

    async def _finish_compat(self, uid, L, d):
        if lim := self._limited(uid, L):
            return lim
        cst = bazi.CST
        ba = bazi.compute(*d["a"], 12, 0, cst, "UTC+08:00")
        bb = bazi.compute(*d["b"], 12, 0, cst, "UTC+08:00")
        for b in (ba, bb):
            b.elements = bazi.count_elements(b.pillars[:3])
        sa, sb = astro.sun_sign_by_date(*d["a"][1:]), astro.sun_sign_by_date(*d["b"][1:])
        s1, s2 = bazi.compat(ba, bb), astro.compat(sa, sb)
        total = round((s1 + s2) / 2)
        N = astro.SIGN_NAMES[L]
        res = t("compat_result", L, pa=" ".join(ba.pillars[:3]), pb=" ".join(bb.pillars[:3]),
                sa=f"{astro.SIGN_EMOJI[sa]} {N[sa]}", sb=f"{astro.SIGN_EMOJI[sb]} {N[sb]}", s1=s1, s2=s2,
                total=f"**{total}**") + "\n" + t("compat_note", L)
        def absent(b):
            return ", ".join(bazi.ELEMENT_EN[e] for e, n in b.elements.items() if n == 0) or "none"
        absent_both = ", ".join(bazi.ELEMENT_EN[e] for e in bazi.ELEMENTS
                                if ba.elements[e] == 0 and bb.elements[e] == 0) or "none"

        def counts(b):
            return ", ".join(f"{bazi.ELEMENT_EN[e]} {n}" for e, n in b.elements.items())
        prompt = (f"Compatibility. Person A BaZi pillars (year, month, day): {' '.join(ba.pillars[:3])}; "
                  f"EXACT five-element counts over these 6 characters (stems + branches): {counts(ba)}; sun sign {sa}.\n"
                  f"Person B pillars: {' '.join(bb.pillars[:3])}; EXACT counts: {counts(bb)}; sun sign {sb}.\n"
                  f"Scores: elements {s1}/100, zodiac {s2}/100.\n"
                  f"FACTS: elements absent in A: {absent(ba)}. Elements absent in B: {absent(bb)}. "
                  f"Elements absent in BOTH: {absent_both}. Do not say any other element is missing.\n"
                  "These counts are computed and authoritative: never contradict them (an element with count 0 is "
                  "absent, any count >= 1 is present). Write a short, kind compatibility summary.")
        verdict = t("verdict_hi" if total >= 75 else "verdict_mid" if total >= 55 else "verdict_lo", L)
        ai = await llm.complete(prompt, L, mode="compat", words=160) or t("compat_fallback", L, verdict=verdict)
        self._reset(uid)
        self.s.log_reading(uid, "compat")
        return [Reply(f"{res}\n\n{ai}\n\n*{t('disclaimer', L)}*", self._result_buttons(L, "compat"))]

    # ---------- daily push ----------
    def due_daily(self, now_utc: datetime):
        out = []
        for r in self.s.daily_users():
            local = now_utc.astimezone(self.user_tz(r["id"])[0])
            if local.hour == r["daily_hour"] and r["daily_last"] != local.date().isoformat():
                out.append((r["id"], local))
        return out

    async def daily_message(self, uid, local: datetime):
        L = self.lang(uid)
        p = self.s.profile(uid)
        sun = p.get("sun") or astro.sun_sign_by_date(p["date"][1], p["date"][2])
        if "dm" not in p:
            hh, mm = p.get("time") or (12, 0)
            p["dm"] = bazi.compute(*p["date"], hh, mm, _tz_from_label(p["tz"]), p["tz"]).day_master
        c, r = tarot.draw(1, self.rng)[0]
        horo = await self.horoscope(sun, L, local, p.get("moon"), p.get("asc"))
        lk = lucky.lucky(uid, local.date(), bazi.day_pillar(local)[0], p["dm"])
        lucky_line = t("daily_lucky", L, color=lucky.color_name(lk["color"], L), nums=" · ".join(map(str, lk["numbers"])))
        self.s.set(uid, daily_last=local.date().isoformat())
        self.s.log_reading(uid, "daily")
        return [Reply(t("daily_msg", L, date=local.date().isoformat(), day=bazi.day_pillar(local), dm=p["dm"],
                        card=f"{tarot.emoji(c)} {tarot.fmt(c, r, L)}", horo=horo, lucky=lucky_line) + f"\n\n*{t('disclaimer', L)}*",
                      [[(t("btn_tarot", L), "r:m:tarot"), (t("btn_menu", L), "r:menu")]])]

    # ---------- new modes ----------
    async def dream(self, uid, dream):
        L = self.lang(uid)
        if lim := self._limited(uid, L):
            return lim
        ai = await llm.complete(f"The user's dream (verbatim, may be in any language):\n<<<\n{dream}\n>>>\n"
                                "Interpret it.", L, 800, mode="dream", words=180)
        if ai:
            body = ai
        else:
            notes = dreams.match(dream, L) or [t("dream_generic", L)]
            body = t("dream_symbols", L) + "\n" + "\n".join(f"• {n}" for n in notes) + "\n\n" + t("dream_question", L)
        quoted = dream if len(dream) <= 200 else dream[:200] + "…"
        self._reset(uid)
        self.s.log_reading(uid, "dream")
        return [Reply(f"{t('dream_head', L)}\n*{quoted}*\n\n{body}\n\n*{t('disclaimer', L)}*", self._result_buttons(L, "dream"))]

    async def lot(self, uid, question):
        L = self.lang(uid)
        if lim := self._limited(uid, L):
            return lim
        n = lots.draw(self.rng)
        grade, verse = lots.LOTS[n - 1][0], lots.LOTS[n - 1][1]
        head = t("lot_head", L, n=n, grade=lots.grade_name(n, L))
        q = f"\n❓ *{question}*" if question else ""
        ai = await llm.complete(
            f"Fortune lot No. {n}, grade {grade} ({lots.GRADES[grade][2]}). Verse (Chinese):\n{verse}\n"
            f"Plain meaning: {lots.meaning(n, 'en')}\n"
            + (f"User's question: \"{question}\"" if question else "No specific question; give general guidance.")
            + ("\nTranslate the verse's imagery briefly for a non-Chinese reader." if L != "zh" else ""),
            L, 700, mode="lot", words=160)
        meaning = ai or lots.meaning(n, L)
        body = (f"{head}{q}\n\n{t('lot_verse', L)}\n{verse}\n\n{t('lot_meaning', L)}\n{meaning}\n\n"
                f"{t('lot_note', L)}")
        self._reset(uid)
        self.s.log_reading(uid, "lot")
        return [Reply(body + f"\n\n*{t('disclaimer', L)}*",
                      self._result_buttons(L, "lot"))]

    async def iching_cast(self, uid, question):
        L = self.lang(uid)
        if lim := self._limited(uid, L):
            return lim
        c = iching.cast(self.rng)
        yang = [1 if v in (7, 9) else 0 for v in c.values]
        parts = [f"☯️ **{t('btn_iching', L).split(' ', 1)[1]}**"]
        if question:
            parts.append(f"❓ *{question}*")
        parts.append(iching.drawing(c.values))
        parts.append(t("iching_coins", L, coins=" ".join(str(v) for v in c.values)))
        parts.append(t("iching_primary", L, name=iching.name(c.primary, L),
                       upper=iching.trigram_desc(yang[3:], L), lower=iching.trigram_desc(yang[:3], L)))
        if c.moving:
            ln = iching.LINE_NAMES[L]
            parts.append(t("iching_moving", L, lines=", ".join(ln[i - 1] for i in c.moving)))
            parts.append(t("iching_changed", L, name=iching.name(c.changed, L)))
        else:
            parts.append(t("iching_static", L))
        prompt = (f"I Ching three-coin cast. Coin sums bottom-to-top: {c.values} (6/9 = changing). "
                  f"Primary hexagram {c.primary} {iching.EN[c.primary - 1]} ({iching.ZH[c.primary - 1]}). "
                  + (f"Changing lines: {c.moving}. Resulting hexagram {c.changed} {iching.EN[c.changed - 1]} "
                     f"({iching.ZH[c.changed - 1]}). " if c.moving else "No changing lines. ")
                  + (f"User's question: \"{question}\"" if question else "No specific question; give general guidance."))
        ai = await llm.complete(prompt, L, 800, mode="iching", words=200)
        if ai:
            parts.append(f"{t('reading_head', L)}\n{ai}")
        else:
            keys = [t("iching_key", L, kw=f"{iching.name(c.primary, L)}: {iching.keyword(c.primary, L)}")]
            if c.changed:
                keys.append(t("iching_key", L, kw=f"{iching.name(c.changed, L)}: {iching.keyword(c.changed, L)}"))
            parts.append("\n".join(keys))
        self._reset(uid)
        self.s.log_reading(uid, "iching")
        return [Reply("\n\n".join(parts) + f"\n\n*{t('disclaimer', L)}*", self._result_buttons(L, "iching"))]

    async def lucky_today(self, uid):
        L = self.lang(uid)
        p = self.s.profile(uid)
        now = datetime.now(self.user_tz(uid)[0])
        day = bazi.day_pillar(now)
        dm = p.get("dm") if p else None
        lk = lucky.lucky(uid, now.date(), day[0], dm)
        why = t("lucky_why_dm", L, dm=dm, day=day) if dm else t("lucky_why_none", L, day=day)
        self.s.log_reading(uid, "lucky")
        return [Reply(t("lucky", L, date=self._today_line(uid, L, now), color=lucky.color_name(lk["color"], L),
                        nums=" · ".join(map(str, lk["numbers"])), dir=lucky.direction_name(lk["direction"], L),
                        el=ELEMENT_NAMES[L][lk["element"]], why=why) + self._tz_hint(uid, L) + f"\n\n*{t('disclaimer', L)}*",
                      [[(t("btn_share", L), "share"), (t("btn_menu", L), "r:menu")]])]
