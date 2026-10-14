"""python-telegram-bot adapter. Token comes ONLY from env FORTUNE_BOT_TOKEN."""
from __future__ import annotations

import asyncio
import io
import logging
import os
from datetime import datetime, timezone

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, LabeledPrice, Update)
from telegram.constants import ChatAction, ParseMode
from telegram.error import BadRequest
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler,
                          PreCheckoutQueryHandler, filters)

from . import llm
from .engine import Engine
from .fmt import to_html
from .i18n import BOT_META

log = logging.getLogger("fortune_bot")
TYPING_DELAY = 0.4   # only show "typing…" if the handler is not done quickly
CHUNK = 3500         # Telegram limit is 4096 chars after entity parsing; keep a margin


def split_text(text: str, limit: int = CHUNK) -> list[str]:
    """Split on paragraph, then line, then hard boundaries so each chunk renders on its own."""
    if len(text) <= limit:
        return [text]
    out, cur = [], ""
    for para in text.split("\n\n"):
        pieces = [para] if len(para) <= limit else [para[i:i + limit] for i in range(0, len(para), limit)]
        for piece in pieces:
            cand = f"{cur}\n\n{piece}" if cur else piece
            if len(cand) <= limit:
                cur = cand
            else:
                out.append(cur)
                cur = piece
    if cur:
        out.append(cur)
    return out


def _kb(r):
    if not r.buttons:
        return None
    return InlineKeyboardMarkup([[InlineKeyboardButton(l, callback_data=c) for l, c in row] for row in r.buttons])


def _photo(path, rev):
    if not rev:
        return open(path, "rb").read()
    from PIL import Image
    buf = io.BytesIO()
    Image.open(path).rotate(180).save(buf, "JPEG", quality=85)
    return buf.getvalue()


async def send(bot, chat_id, replies, message=None):
    """Render replies. `message` is the message whose button was pressed (for edit-in-place)."""
    for r in replies:
        if r.clear_kb:
            if message is not None:
                try:
                    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message.message_id, reply_markup=None)
                except Exception as e:  # noqa: BLE001 - already removed / too old
                    log.debug("clear keyboard failed: %s", e)
            continue
        if r.invoice:
            inv = r.invoice
            await bot.send_invoice(chat_id=chat_id, title=inv["title"], description=inv["description"],
                                   payload=inv["payload"], provider_token=inv["provider_token"],
                                   currency=inv["currency"], prices=[LabeledPrice(l, a) for l, a in inv["prices"]])
            continue
        if r.photos:
            try:
                if len(r.photos) == 1:
                    await bot.send_photo(chat_id=chat_id, photo=_photo(*r.photos[0]))
                else:
                    await bot.send_media_group(chat_id=chat_id, media=[InputMediaPhoto(_photo(*p)) for p in r.photos])
            except Exception as e:  # noqa: BLE001 - images are decoration only
                log.warning("card image send failed: %s", e)
        chunks = split_text(r.text)
        for extra in chunks[:-1]:
            await bot.send_message(chat_id=chat_id, text=to_html(extra), parse_mode=ParseMode.HTML,
                                   disable_web_page_preview=True)
        text, kb = to_html(chunks[-1]), _kb(r)
        if r.edit and message is not None and len(chunks) == 1:
            try:
                await bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=text,
                                            parse_mode=ParseMode.HTML, reply_markup=kb, disable_web_page_preview=True)
                continue
            except BadRequest as e:
                if "not modified" in str(e).lower():
                    continue
                log.info("edit failed (%s), sending new message", e)
        await bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML, reply_markup=kb,
                               disable_web_page_preview=True)
        if r.then is not None:
            await send(bot, chat_id, await with_typing(bot, chat_id, r.then()))


async def with_typing(bot, chat_id, coro):
    """Await coro; if it takes longer than TYPING_DELAY, show 'typing…' until it finishes."""
    done = asyncio.Event()

    async def typing():
        try:
            await asyncio.wait_for(done.wait(), TYPING_DELAY)
            return
        except asyncio.TimeoutError:
            pass
        while not done.is_set():
            try:
                await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            except Exception:  # noqa: BLE001
                pass
            try:
                await asyncio.wait_for(done.wait(), 4)
            except asyncio.TimeoutError:
                pass
    ticker = asyncio.ensure_future(typing())
    try:
        return await coro
    finally:
        # Let an in-flight sendChatAction finish BEFORE the reply is sent; otherwise the action can
        # reach Telegram after our message and "typing…" lingers for ~5 s.
        done.set()
        await ticker


def build_handlers(engine: Engine):
    def u(update: Update):
        usr = update.effective_user
        return usr.id, usr.language_code

    async def run(update, ctx, coro, message=None):
        chat = update.effective_chat.id
        await send(ctx.bot, chat, await with_typing(ctx.bot, chat, coro), message)

    async def start(update, ctx: ContextTypes.DEFAULT_TYPE):
        uid, code = u(update)
        await run(update, ctx, engine.start(uid, code, (ctx.args or [""])[0]))

    def simple(fn):
        async def h(update, ctx):
            uid, code = u(update)
            await run(update, ctx, fn(uid, code))
        return h

    def mode(m):
        async def h(update, ctx):
            uid, code = u(update)
            await run(update, ctx, engine.begin(uid, m, code))
        return h

    async def daily(update, ctx):
        uid, code = u(update)
        engine.lang(uid, code)
        await run(update, ctx, engine.daily_cmd(uid, [a.lower() for a in ctx.args or []]))

    async def tz(update, ctx):
        uid, code = u(update)
        engine.lang(uid, code)
        await run(update, ctx, engine.tz_cmd(uid, ctx.args or []))

    async def stats(update, ctx):
        uid, _ = u(update)
        await run(update, ctx, engine.stats(uid))

    async def text(update, ctx):
        uid, code = u(update)
        await run(update, ctx, engine.text(uid, update.message.text, code))

    async def cb(update, ctx):
        q = update.callback_query
        await q.answer()
        uid, code = u(update)
        await run(update, ctx, engine.callback(uid, q.data, code), message=q.message)

    async def precheckout(update, ctx):
        q = update.pre_checkout_query
        ok = engine.precheckout_ok(q.invoice_payload, q.currency, q.total_amount)
        await q.answer(ok=ok, error_message=None if ok else "Unavailable")

    async def paid(update, ctx):
        uid, _ = u(update)
        sp = update.message.successful_payment
        await run(update, ctx, engine.paid(uid, sp.invoice_payload, sp.total_amount, sp.telegram_payment_charge_id))

    return [
        CommandHandler("start", start),
        CommandHandler("help", simple(engine.help)),
        CommandHandler("lang", simple(engine.lang_cmd)),
        CommandHandler("cancel", simple(engine.cancel)),
        CommandHandler("menu", mode("menu")),
        CommandHandler("bazi", mode("bazi")),
        CommandHandler("tarot", mode("tarot")),
        CommandHandler("astro", mode("astro")),
        CommandHandler("compat", mode("compat")),
        CommandHandler("huangli", mode("huangli")),
        CommandHandler("dream", mode("dream")),
        CommandHandler("lot", mode("lot")),
        CommandHandler("iching", mode("iching")),
        CommandHandler("lucky", mode("lucky")),
        CommandHandler("daily", daily),
        CommandHandler("tz", tz),
        CommandHandler("stats", stats),
        CallbackQueryHandler(cb),
        PreCheckoutQueryHandler(precheckout),
        MessageHandler(filters.SUCCESSFUL_PAYMENT, paid),
        MessageHandler(filters.TEXT & ~filters.COMMAND, text),
    ]


async def daily_job(ctx: ContextTypes.DEFAULT_TYPE):
    engine: Engine = ctx.job.data
    for uid, local in engine.due_daily(datetime.now(timezone.utc)):
        try:
            await send(ctx.bot, uid, await engine.daily_message(uid, local))
        except Exception as e:  # noqa: BLE001 - user may have blocked the bot
            log.warning("daily push to %s failed: %s", uid, e)


async def set_bot_profile(bot):
    """Per-language command menu, description and short description."""
    for L, meta in BOT_META.items():
        code = None if L == "en" else L          # English is also the default for other languages
        await bot.set_my_commands(meta["cmds"], language_code=code)
        await bot.set_my_description(meta["desc"], language_code=code)
        await bot.set_my_short_description(meta["short"], language_code=code)
        if L == "en":
            await bot.set_my_commands(meta["cmds"], language_code="en")


def make_error_handler(engine: Engine):
    async def on_error(update, ctx):
        log.error("handler error: %s", ctx.error, exc_info=ctx.error)
        try:
            if isinstance(update, Update) and update.effective_chat and update.effective_user:
                from .i18n import t
                L = engine.lang(update.effective_user.id)
                await ctx.bot.send_message(chat_id=update.effective_chat.id, text=to_html(t("error", L)),
                                           parse_mode=ParseMode.HTML)
        except Exception:  # noqa: BLE001
            pass
    return on_error


def build_app(token, engine, post_init=None):
    b = Application.builder().token(token).concurrent_updates(True)  # a slow LLM reply must not block others
    if post_init:
        b = b.post_init(post_init)
    app = b.build()
    for h in build_handlers(engine):
        app.add_handler(h)
    app.add_error_handler(make_error_handler(engine))
    app.job_queue.run_repeating(daily_job, interval=300, first=10, data=engine)
    return app


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)  # don't log URLs containing the token
    token = os.environ.get("FORTUNE_BOT_TOKEN")
    if not token:
        raise SystemExit("FORTUNE_BOT_TOKEN is not set")
    from .storage import Store
    engine = Engine(Store(os.getenv("FORTUNE_DB", "fortune.db")))
    engine.defer_followups = True

    async def post_init(app):
        if not engine.bot_username:
            engine.bot_username = (await app.bot.get_me()).username
        try:
            await set_bot_profile(app.bot)
        except Exception as e:  # noqa: BLE001 - cosmetic, don't fail startup
            log.warning("setting bot commands/description failed: %s", e)

    app = build_app(token, engine, post_init)
    log.info("starting; LLM configured=%s payments=%s", llm.configured(), engine.payments)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
