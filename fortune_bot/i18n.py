LANGS = ("zh", "ru", "en")

T = {
 "start": {
  "zh": "🔮 欢迎来到 AI 八字算命！\n发送 /bazi 开始排盘，/lang 切换语言，/help 查看帮助。\n\n⚠️ 仅供娱乐，不构成任何建议。",
  "ru": "🔮 Добро пожаловать в AI-гадание Бацзы!\n/bazi — начать, /lang — язык, /help — помощь.\n\n⚠️ Только для развлечения, не является советом.",
  "en": "🔮 Welcome to AI BaZi fortune telling!\n/bazi to start, /lang to change language, /help for help.\n\n⚠️ For entertainment only, not advice of any kind.",
 },
 "help": {
  "zh": "用法：\n/bazi — 输入出生日期、时间和地点/时区，排出四柱八字并给出解读\n/lang — 切换语言（中文/Русский/English）\n/cancel — 取消当前流程\n\n⚠️ 仅供娱乐。",
  "ru": "Как пользоваться:\n/bazi — дата, время и место/часовой пояс рождения → четыре столпа и толкование\n/lang — сменить язык\n/cancel — отменить\n\n⚠️ Только для развлечения.",
  "en": "How to use:\n/bazi — enter birth date, time and place/timezone to get your Four Pillars and a reading\n/lang — change language\n/cancel — cancel the current step\n\n⚠️ For entertainment only.",
 },
 "ask_date": {"zh": "请输入出生日期，例如 1990-05-15", "ru": "Введите дату рождения, например 1990-05-15", "en": "Enter your birth date, e.g. 1990-05-15"},
 "ask_time": {"zh": "请输入出生时间（24 小时制），例如 14:30", "ru": "Введите время рождения (24 ч), например 14:30", "en": "Enter your birth time (24h), e.g. 14:30"},
 "ask_tz": {
  "zh": "请输入出生城市或时区，例如：北京、Moscow、Asia/Shanghai、+8",
  "ru": "Введите город или часовой пояс рождения, например: Москва, Asia/Shanghai, +3",
  "en": "Enter birth city or timezone, e.g. Beijing, Europe/Moscow, +8",
 },
 "bad_date": {"zh": "日期格式不对（1900–2100 年，格式 YYYY-MM-DD），请重新输入。", "ru": "Неверная дата (1900–2100, формат ГГГГ-ММ-ДД). Попробуйте ещё раз.", "en": "Invalid date (1900–2100, format YYYY-MM-DD). Please try again."},
 "bad_time": {"zh": "时间格式不对，例如 08:05 或 23:30，请重新输入。", "ru": "Неверное время, например 08:05 или 23:30.", "en": "Invalid time, e.g. 08:05 or 23:30. Please try again."},
 "bad_tz": {"zh": "无法识别这个城市/时区，请用 IANA 名称（Asia/Shanghai）或偏移（+8）。", "ru": "Не удалось распознать город/пояс. Используйте IANA (Europe/Moscow) или смещение (+3).", "en": "Unknown city/timezone. Use an IANA name (Europe/Moscow) or an offset (+8)."},
 "cancelled": {"zh": "已取消。", "ru": "Отменено.", "en": "Cancelled."},
 "choose_lang": {"zh": "请选择语言：", "ru": "Выберите язык:", "en": "Choose a language:"},
 "lang_set": {"zh": "语言已切换为中文。", "ru": "Язык: русский.", "en": "Language set to English."},
 "thinking": {"zh": "🔮 正在排盘解读…", "ru": "🔮 Составляю карту…", "en": "🔮 Reading your chart…"},
 "chart": {
  "zh": "🀄 你的四柱八字\n出生：{dt}（{tz}）\n\n年柱 {y}　月柱 {m}　日柱 {d}　时柱 {h}\n日主：{dm}（{dme}）\n\n五行分布：\n{bars}",
  "ru": "🀄 Ваши четыре столпа\nРождение: {dt} ({tz})\n\nГод {y}  Месяц {m}  День {d}  Час {h}\nХозяин дня: {dm} ({dme})\n\nПять стихий:\n{bars}",
  "en": "🀄 Your Four Pillars\nBorn: {dt} ({tz})\n\nYear {y}  Month {m}  Day {d}  Hour {h}\nDay Master: {dm} ({dme})\n\nFive elements:\n{bars}",
 },
 "yearly_btn": {"zh": "📅 详细流年运势（付费）", "ru": "📅 Подробный прогноз на год (платно)", "en": "📅 Detailed yearly forecast (premium)"},
 "coming_soon": {"zh": "详细流年运势即将上线，敬请期待！", "ru": "Подробный годовой прогноз скоро появится!", "en": "The detailed yearly forecast is coming soon!"},
 "disclaimer": {"zh": "⚠️ 仅供娱乐，不构成任何人生、医疗、财务或法律建议。", "ru": "⚠️ Только для развлечения; не является жизненным, медицинским, финансовым или юридическим советом.", "en": "⚠️ For entertainment only; not life, medical, financial or legal advice."},
}

ELEMENT_NAMES = {
 "zh": dict(zip("木火土金水", "木火土金水")),
 "ru": dict(zip("木火土金水", ["Дерево", "Огонь", "Земля", "Металл", "Вода"])),
 "en": dict(zip("木火土金水", ["Wood", "Fire", "Earth", "Metal", "Water"])),
}

# Template fallback interpretation (used when no LLM is configured or the LLM fails).
DM_TRAITS = {
 "木": {"zh": "如树木般向上生长，仁厚、有进取心，重成长与规划。", "ru": "Как дерево — растёт вверх: доброжелательность, стремление к развитию, планирование.", "en": "Like a tree growing upward: kind, ambitious, focused on growth and planning."},
 "火": {"zh": "如火焰般热情明亮，善表达、有感染力，行动迅速。", "ru": "Как огонь — тёплый и яркий: выразительность, харизма, быстрые действия.", "en": "Like fire: warm and bright, expressive, charismatic, quick to act."},
 "土": {"zh": "如大地般稳重可靠，守信、包容，善于协调。", "ru": "Как земля — устойчивость и надёжность: верность слову, терпимость, умение объединять.", "en": "Like earth: steady and reliable, trustworthy, tolerant, a natural mediator."},
 "金": {"zh": "如金属般果断坚毅，讲原则、重效率，执行力强。", "ru": "Как металл — решительность и твёрдость: принципы, эффективность, исполнительность.", "en": "Like metal: decisive and firm, principled, efficient, strong at execution."},
 "水": {"zh": "如流水般灵活聪慧，善思考、适应力强，洞察人心。", "ru": "Как вода — гибкость и ум: аналитичность, адаптивность, интуиция.", "en": "Like water: flexible and clever, thoughtful, adaptable, intuitive."},
}
FALLBACK = {
 "zh": "🔎 基础解读\n日主为{dm}（{dme}）：{trait}\n五行中{strong}最旺，{weak}最弱。传统上认为可多接触属{weak}的事物（颜色、方位、爱好）以求平衡，同时发挥{strong}带来的优势。",
 "ru": "🔎 Базовое толкование\nХозяин дня {dm} ({dme}): {trait}\nСильнее всего стихия «{strong}», слабее всего — «{weak}». Традиционно советуют добавить в жизнь больше «{weak}» (цвета, направления, увлечения) для баланса и опираться на сильные стороны «{strong}».",
 "en": "🔎 Basic reading\nDay Master {dm} ({dme}): {trait}\n{strong} is your strongest element and {weak} the weakest. Traditionally, adding more {weak} (colours, directions, hobbies) brings balance, while {strong} is the strength to build on.",
}


def t(key: str, lang: str, **kw) -> str:
    lang = lang if lang in LANGS else "en"
    s = T[key][lang]
    return s.format(**kw) if kw else s


def detect_lang(code: str | None) -> str:
    c = (code or "").lower()
    if c.startswith("zh"):
        return "zh"
    if c.startswith(("ru", "uk", "be", "kk")):
        return "ru"
    return "en"


def _add(key, zh, ru, en):
    T[key] = {"zh": zh, "ru": ru, "en": en}


_add("menu", "请选择：", "Выберите:", "Choose a mode:")
_add("btn_bazi", "🀄 八字", "🀄 Бацзы", "🀄 BaZi")
_add("btn_tarot", "🃏 塔罗", "🃏 Таро", "🃏 Tarot")
_add("btn_astro", "♈ 星座", "♈ Астрология", "♈ Astrology")
_add("btn_compat", "💞 合盘", "💞 Совместимость", "💞 Compatibility")
_add("btn_huangli", "📜 今日黄历", "📜 Календарь дня", "📜 Today's almanac")
_add("btn_share", "📤 分享", "📤 Поделиться", "📤 Share")
_add("btn_tarot1", "🌅 每日一张", "🌅 Карта дня", "🌅 Card of the day")
_add("btn_tarot3", "🔮 过去/现在/未来", "🔮 Прошлое/настоящее/будущее", "🔮 Past/Present/Future")
_add("tarot_choose", "选择牌阵：", "Выберите расклад:", "Choose a spread:")
_add("ask_question", "请写下你想问的问题（或发送「-」跳过）：", "Напишите свой вопрос (или «-», чтобы пропустить):", "Type your question (or '-' to skip):")
_add("tarot_pos", "过去|现在|未来", "Прошлое|Настоящее|Будущее", "Past|Present|Future")
_add("tarot_daily_title", "🌅 今日塔罗", "🌅 Карта дня", "🌅 Card of the day")
_add("tarot_fallback", "🔎 解读：结合牌面，{hint}。保持开放的心态，留意身边的小信号。", "🔎 Толкование: {hint}. Будьте открыты и замечайте маленькие знаки.", "🔎 Reading: {hint}. Stay open and watch for small signs around you.")
_add("ask_time_opt", "请输入出生时间（24 小时制，例如 14:30）；不知道就发「-」（只算太阳星座）：",
     "Время рождения (24 ч, например 14:30); если не знаете — «-» (только знак Солнца):",
     "Birth time (24h, e.g. 14:30); send '-' if unknown (sun sign only):")
_add("astro_chart", "♈ 你的星盘\n太阳：{sun}\n月亮：{moon}\n上升：{asc}", "♈ Ваша карта\nСолнце: {sun}\nЛуна: {moon}\nАсцендент: {asc}", "♈ Your chart\nSun: {sun}\nMoon: {moon}\nAscendant: {asc}")
_add("na_time", "未知（需要出生时间）", "неизвестно (нужно время)", "unknown (needs birth time)")
_add("na_place", "未知（城市坐标不在列表中，请输入如 Moscow、北京）", "неизвестно (нет координат города, введите, напр., Moscow)", "unknown (city coordinates not known; use e.g. London, Beijing)")
_add("moon_approx", "（无出生时间，按中午估算，可能不准）", "(без времени — оценка на полдень, может быть неточно)", "(no birth time — noon estimate, may be off)")
_add("horoscope_fallback", "✨ 今日运势（{sign}）：{tip}", "✨ Гороскоп на сегодня ({sign}): {tip}", "✨ Today ({sign}): {tip}")
_add("ask_date_a", "合盘：请输入第一个人的出生日期（YYYY-MM-DD）", "Совместимость: дата рождения первого человека (ГГГГ-ММ-ДД)", "Compatibility: first person's birth date (YYYY-MM-DD)")
_add("ask_date_b", "请输入第二个人的出生日期（YYYY-MM-DD）", "Дата рождения второго человека (ГГГГ-ММ-ДД)", "Second person's birth date (YYYY-MM-DD)")
_add("compat_result", "💞 合盘结果\nA：{pa}（{sa}）\nB：{pb}（{sb}）\n\n五行契合度：{s1}/100\n星座契合度：{s2}/100\n综合：{total}/100",
     "💞 Совместимость\nA: {pa} ({sa})\nB: {pb} ({sb})\n\nПять стихий: {s1}/100\nЗнаки зодиака: {s2}/100\nИтого: {total}/100",
     "💞 Compatibility\nA: {pa} ({sa})\nB: {pb} ({sb})\n\nFive elements: {s1}/100\nZodiac signs: {s2}/100\nOverall: {total}/100")
_add("compat_note", "（只用出生日期：八字取年/月/日三柱，按中午、东八区计算）", "(только даты: три столпа год/месяц/день, полдень UTC+8)", "(dates only: year/month/day pillars at noon UTC+8)")
_add("compat_fallback", "🔎 {verdict}", "🔎 {verdict}", "🔎 {verdict}")
_add("verdict_hi", "你们很合拍，互相补足，适合一起做事。", "Вы отлично дополняете друг друга.", "You complement each other very well.")
_add("verdict_mid", "整体不错，多沟通能更顺。", "В целом хорошо; больше общения — и всё сложится.", "A good match; more communication makes it smoother.")
_add("verdict_lo", "差异较大，但差异也是成长的机会。", "Различий много, но это шанс расти вместе.", "Quite different — which can also be a chance to grow.")
_add("huangli", "📜 今日黄历 {date}\n农历：{lunar}\n日柱：{day}\n宜：{yi}\n忌：{ji}", "📜 Китайский календарь {date}\nЛунная дата: {lunar}\nСтолп дня: {day}\nБлагоприятно: {yi}\nНеблагоприятно: {ji}", "📜 Chinese almanac {date}\nLunar date: {lunar}\nDay pillar: {day}\nGood for: {yi}\nAvoid: {ji}")
_add("daily_need_profile", "请先用 /bazi 或 /astro 保存你的出生信息（需要时区）。", "Сначала сохраните данные рождения через /bazi или /astro.", "Save your birth data first with /bazi or /astro (timezone needed).")
_add("daily_on", "✅ 每日运势已开启，每天 {hour}:00（{tz}）推送。用 /daily off 关闭。", "✅ Ежедневный прогноз включён: каждый день в {hour}:00 ({tz}). /daily off — выключить.", "✅ Daily fortune on: every day at {hour}:00 ({tz}). /daily off to stop.")
_add("daily_off", "已关闭每日运势。", "Ежедневный прогноз выключен.", "Daily fortune turned off.")
_add("daily_usage", "用法：/daily on [0-23] 或 /daily off", "Использование: /daily on [0-23] или /daily off", "Usage: /daily on [0-23] or /daily off")
_add("daily_msg", "☀️ 每日运势 {date}\n\n🀄 今日日柱：{day}（你的日主 {dm}）\n🃏 今日塔罗：{card}\n♈ {horo}", "☀️ Прогноз на {date}\n\n🀄 Столп дня: {day} (ваш хозяин дня {dm})\n🃏 Карта дня: {card}\n♈ {horo}", "☀️ Daily fortune {date}\n\n🀄 Day pillar: {day} (your Day Master {dm})\n🃏 Card of the day: {card}\n♈ {horo}")
_add("share", "🔮 我刚在 AI 算命机器人上算了一卦，你也来试试：\n{link}", "🔮 Я погадал(а) у AI-гадалки, попробуй и ты:\n{link}", "🔮 I just got a reading from an AI fortune bot — try it:\n{link}")
_add("rate_limited", "太快了，请稍等一分钟再试。", "Слишком часто, подождите минуту.", "Too many requests, please wait a minute.")
_add("stats", "📊 用户：{users}\n推荐来的用户：{refs}\n开启每日推送：{daily}\n各模式次数：\n{modes}", "📊 Пользователи: {users}\nПо рефералам: {refs}\nЕжедневный прогноз: {daily}\nПо режимам:\n{modes}", "📊 Users: {users}\nReferred: {refs}\nDaily on: {daily}\nReadings per mode:\n{modes}")
_add("invoice_title", "详细流年运势", "Подробный прогноз на год", "Detailed yearly forecast")
_add("invoice_desc", "基于你的八字的 12 个月详细运势报告（仅供娱乐）。", "Подробный отчёт на 12 месяцев по вашей карте Бацзы (для развлечения).", "A 12-month report based on your BaZi chart (entertainment only).")
_add("paid_thanks", "感谢支持！报告生成功能即将上线，我们会尽快发给你。", "Спасибо! Генерация отчёта скоро появится, мы пришлём его вам.", "Thank you! Report generation is coming soon; we'll send it to you.")

HOROSCOPE_TIPS = {
 "zh": ["适合整理计划，小步前进。", "沟通运佳，主动联系老朋友。", "注意休息，别把自己逼太紧。", "灵感充沛，适合创作和学习。", "财务上保持谨慎，避免冲动消费。", "适合与人合作，听听不同意见。", "专注一件事，会有意外收获。"],
 "ru": ["Хороший день, чтобы разложить планы и идти маленькими шагами.", "Удачный день для общения — напишите старым друзьям.", "Берегите силы и отдыхайте.", "Много вдохновения — творите и учитесь.", "Будьте осторожны с деньгами, без импульсивных покупок.", "Хорошо для командной работы — выслушайте других.", "Сосредоточьтесь на одном деле — будет приятный сюрприз."],
 "en": ["A good day to organise plans and take small steps.", "Communication is favoured — reach out to an old friend.", "Rest well; don't push yourself too hard.", "Inspiration is high — create and learn.", "Be careful with money; avoid impulse buys.", "Good for teamwork — listen to other views.", "Focus on one thing and expect a pleasant surprise."],
}
_add("tarot_fallback_neutral", "🔎 以上是每张牌的传统含义，请结合你自己的问题和处境来理解。", "🔎 Выше — традиционные значения карт; соотнесите их со своим вопросом и ситуацией.", "🔎 Above are the traditional card meanings; relate them to your own question and situation.")

# ---------------- UI/UX v2 (later _add calls override earlier texts) ----------------
_add("onboard", "🔮 **欢迎！**\n\n这里可以用八字、塔罗和星座给你算一卦。\n\n请先选择语言 👇",
     "🔮 **Добро пожаловать!**\n\nЗдесь можно узнать судьбу по Бацзы, Таро и астрологии.\n\nСначала выберите язык 👇",
     "🔮 **Welcome!**\n\nGet a reading from Chinese BaZi, Tarot or Western astrology.\n\nFirst, pick your language 👇")
_add("start", "🔮 **AI 算命**\n\n选一种方式开始吧 👇\n\n*⚠️ 仅供娱乐*",
     "🔮 **AI-гадание**\n\nВыберите способ 👇\n\n*⚠️ Только для развлечения*",
     "🔮 **AI Fortune**\n\nChoose a reading 👇\n\n*⚠️ For entertainment only*")
_add("menu", "🏠 **主菜单**\n选一种方式 👇", "🏠 **Главное меню**\nВыберите 👇", "🏠 **Main menu**\nChoose a reading 👇")
_add("help", "❓ **帮助**\n\n"
     "🀄 /bazi — 八字排盘\n🃏 /tarot — 塔罗\n♈ /astro — 星座\n💞 /compat — 合盘\n📜 /huangli — 今日黄历\n"
     "☀️ /daily on 9 — 每天 9 点推送运势（/daily off 关闭）\n🌐 /lang — 语言\n✖️ /cancel — 取消\n\n"
     "日期、时辰、城市都可以点按钮，也可以直接打字。\n\n*⚠️ 仅供娱乐*",
     "❓ **Помощь**\n\n🀄 /bazi — Бацзы\n🃏 /tarot — Таро\n♈ /astro — астрология\n💞 /compat — совместимость\n"
     "📜 /huangli — календарь дня\n☀️ /daily on 9 — прогноз каждый день в 9:00 (/daily off — выкл.)\n🌐 /lang — язык\n✖️ /cancel — отмена\n\n"
     "Дату, час и город можно выбрать кнопками или ввести текстом.\n\n*⚠️ Только для развлечения*",
     "❓ **Help**\n\n🀄 /bazi — BaZi chart\n🃏 /tarot — Tarot\n♈ /astro — astrology\n💞 /compat — compatibility\n"
     "📜 /huangli — today's almanac\n☀️ /daily on 9 — daily fortune at 9:00 (/daily off to stop)\n🌐 /lang — language\n✖️ /cancel — cancel\n\n"
     "Date, hour and city can be tapped or typed.\n\n*⚠️ For entertainment only*")
_add("btn_menu", "🏠 主菜单", "🏠 Меню", "🏠 Menu")
_add("btn_back", "⬅️ 返回", "⬅️ Назад", "⬅️ Back")
_add("btn_again", "🔄 再来一次", "🔄 Ещё раз", "🔄 Try again")
_add("btn_another_spread", "🔄 换个牌阵", "🔄 Другой расклад", "🔄 Another spread")
_add("btn_use_saved", "✅ 用保存的资料", "✅ Использовать сохранённые", "✅ Use saved data")
_add("btn_new_data", "✏️ 输入新的", "✏️ Ввести новые", "✏️ Enter new data")
_add("btn_unknown_time", "❔ 不知道时辰", "❔ Не знаю время", "❔ Time unknown")
_add("btn_other_city", "⌨️ 其他城市（打字）", "⌨️ Другой город (ввести)", "⌨️ Other city (type it)")
_add("use_saved", "💾 **用上次保存的出生资料吗？**\n\n{summary}", "💾 **Использовать сохранённые данные?**\n\n{summary}", "💾 **Use your saved birth data?**\n\n{summary}")
_add("ask_date", "📅 **出生日期**\n先选年代，或直接输入，例如 `1990-05-15`",
     "📅 **Дата рождения**\nВыберите десятилетие или введите, например `1990-05-15`",
     "📅 **Birth date**\nPick a decade, or type it, e.g. `1990-05-15`")
_add("ask_date_a", "💞 **合盘 · 第一个人**\n📅 选年代，或输入出生日期，例如 `1990-05-15`",
     "💞 **Совместимость · человек A**\n📅 Выберите десятилетие или введите дату, напр. `1990-05-15`",
     "💞 **Compatibility · person A**\n📅 Pick a decade or type the birth date, e.g. `1990-05-15`")
_add("ask_date_b", "💞 **第二个人**\n📅 选年代，或输入出生日期，例如 `1992-08-01`",
     "💞 **Человек B**\n📅 Выберите десятилетие или введите дату, напр. `1992-08-01`",
     "💞 **Person B**\n📅 Pick a decade or type the birth date, e.g. `1992-08-01`")
_add("pick_year", "📅 选年份：", "📅 Год:", "📅 Year:")
_add("pick_month", "📅 {y} 年 · 选月份：", "📅 {y} · месяц:", "📅 {y} · month:")
_add("pick_day", "📅 {y}-{m:02d} · 选日子：", "📅 {y}-{m:02d} · день:", "📅 {y}-{m:02d} · day:")
_add("ask_time", "🕰 **出生时辰**（{date}）\n点一个时辰，或输入准确时间，例如 `14:30`",
     "🕰 **Время рождения** ({date})\nВыберите двухчасовой период или введите точное время, напр. `14:30`",
     "🕰 **Birth time** ({date})\nTap a two-hour slot, or type the exact time, e.g. `14:30`")
_add("ask_tz", "📍 **出生城市**\n点一个城市，或输入城市 / 时区，例如 `Moscow`、`Asia/Shanghai`、`+8`",
     "📍 **Город рождения**\nВыберите город или введите город / пояс, напр. `Москва`, `Asia/Shanghai`, `+3`",
     "📍 **Birth city**\nTap a city, or type a city / timezone, e.g. `London`, `Asia/Shanghai`, `+8`")
_add("type_city", "⌨️ 请输入城市或时区，例如 `Berlin`、`Europe/Paris`、`UTC+5:30`",
     "⌨️ Введите город или часовой пояс, напр. `Berlin`, `Europe/Paris`, `UTC+5:30`",
     "⌨️ Type a city or timezone, e.g. `Berlin`, `Europe/Paris`, `UTC+5:30`")
_add("bad_date", "🙈 没看懂这个日期。\n请这样写：`1990-05-15` 或 `1990年5月15日`（1900–2100 年），或者点上面的按钮。",
     "🙈 Не понял дату.\nПример: `1990-05-15` (1900–2100) — или нажмите кнопку выше.",
     "🙈 I couldn't read that date.\nTry `1990-05-15` (years 1900–2100), or tap the buttons above.")
_add("bad_time", "🙈 没看懂这个时间。\n请这样写：`08:05`、`23:30` 或 `7`，或者点时辰按钮。",
     "🙈 Не понял время.\nПример: `08:05`, `23:30` или `7` — или нажмите кнопку.",
     "🙈 I couldn't read that time.\nTry `08:05`, `23:30` or `7`, or tap a slot button.")
_add("bad_tz", "🙈 找不到这个城市。\n试试：`Moscow`、`北京`、`Europe/Berlin`、`+8`。",
     "🙈 Не нашёл такой город.\nПопробуйте: `Москва`, `Europe/Berlin`, `+3`.",
     "🙈 I don't know that place.\nTry `London`, `Europe/Berlin`, `America/Chicago` or `+8`.")
_add("tarot_choose", "🃏 **塔罗**\n选一个牌阵 👇", "🃏 **Таро**\nВыберите расклад 👇", "🃏 **Tarot**\nChoose a spread 👇")
_add("ask_question", "❓ **你想问什么？**\n写下你的问题，例如：`我该换工作吗？`\n不想写就发 `-`",
     "❓ **Ваш вопрос?**\nНапример: `Стоит ли менять работу?`\nИли отправьте `-`",
     "❓ **What's your question?**\nE.g. `Should I change jobs?`\nOr send `-` to skip")
_add("chart", "🀄 **你的四柱八字**\n🗓 {dt}（{tz}）\n\n**年柱** {y}　**月柱** {m}　**日柱** {d}　**时柱** {h}\n☯️ 日主：**{dm}**（{dme}）\n\n🌈 **五行分布**\n{bars}",
     "🀄 **Ваши четыре столпа**\n🗓 {dt} ({tz})\n\n**Год** {y}  **Месяц** {m}  **День** {d}  **Час** {h}\n☯️ Хозяин дня: **{dm}** ({dme})\n\n🌈 **Пять стихий**\n{bars}",
     "🀄 **Your Four Pillars**\n🗓 {dt} ({tz})\n\n**Year** {y}  **Month** {m}  **Day** {d}  **Hour** {h}\n☯️ Day Master: **{dm}** ({dme})\n\n🌈 **Five elements**\n{bars}")
_add("hour_unknown_note", "（时辰未知：只排三柱）", "(время неизвестно: три столпа)", "(time unknown: three pillars only)")
_add("reading_head", "🔎 **解读**", "🔎 **Толкование**", "🔎 **Reading**")
_add("astro_chart", "♈ **你的星盘**\n\n☀️ 太阳：{sun}\n🌙 月亮：{moon}\n⬆️ 上升：{asc}",
     "♈ **Ваша карта**\n\n☀️ Солнце: {sun}\n🌙 Луна: {moon}\n⬆️ Асцендент: {asc}",
     "♈ **Your chart**\n\n☀️ Sun: {sun}\n🌙 Moon: {moon}\n⬆️ Ascendant: {asc}")
_add("horo_head", "✨ **今日运势**", "✨ **Гороскоп на сегодня**", "✨ **Today's horoscope**")
_add("tarot_daily_title", "🌅 今日之牌", "🌅 Карта дня", "🌅 Card of the day")
_add("lang_set", "✅ 语言：中文", "✅ Язык: русский", "✅ Language: English")
_add("choose_lang", "🌐 **选择语言**", "🌐 **Выберите язык**", "🌐 **Choose a language**")

SHICHEN = [  # (branch, start hour, representative time used for the calculation)
    ("子", "23–01", (0, 0)), ("丑", "01–03", (2, 0)), ("寅", "03–05", (4, 0)), ("卯", "05–07", (6, 0)),
    ("辰", "07–09", (8, 0)), ("巳", "09–11", (10, 0)), ("午", "11–13", (12, 0)), ("未", "13–15", (14, 0)),
    ("申", "15–17", (16, 0)), ("酉", "17–19", (18, 0)), ("戌", "19–21", (20, 0)), ("亥", "21–23", (22, 0)),
]

TOP_CITIES = [  # (key passed to parse_place, label zh, ru, en)
    ("beijing", "北京", "Пекин", "Beijing"), ("shanghai", "上海", "Шанхай", "Shanghai"),
    ("hong kong", "香港", "Гонконг", "Hong Kong"), ("singapore", "新加坡", "Сингапур", "Singapore"),
    ("moscow", "莫斯科", "Москва", "Moscow"), ("saint petersburg", "圣彼得堡", "Санкт-Петербург", "St Petersburg"),
    ("london", "伦敦", "Лондон", "London"), ("new york", "纽约", "Нью-Йорк", "New York"),
]

BOT_META = {
    "zh": {"short": "🔮 AI 算命：八字、塔罗、星座、合盘、每日运势。仅供娱乐。",
           "desc": "🔮 AI 算命机器人\n\n🀄 八字四柱与五行\n🃏 78 张塔罗牌\n♈ 太阳 / 月亮 / 上升星座\n💞 合盘\n☀️ 每日运势推送\n\n⚠️ 仅供娱乐，不构成任何建议。点「开始」试试吧！",
           "cmds": [("start", "开始 / 主菜单"), ("bazi", "八字排盘"), ("tarot", "塔罗"), ("astro", "星座"),
                    ("compat", "合盘"), ("huangli", "今日黄历"), ("daily", "每日运势 on/off"), ("lang", "语言"), ("help", "帮助")]},
    "ru": {"short": "🔮 AI-гадание: Бацзы, Таро, астрология, совместимость, прогноз дня. Для развлечения.",
           "desc": "🔮 AI-гадалка\n\n🀄 Четыре столпа Бацзы\n🃏 78 карт Таро\n♈ Солнце / Луна / Асцендент\n💞 Совместимость\n☀️ Ежедневный прогноз\n\n⚠️ Только для развлечения. Нажмите «Старт»!",
           "cmds": [("start", "старт / меню"), ("bazi", "Бацзы"), ("tarot", "Таро"), ("astro", "астрология"),
                    ("compat", "совместимость"), ("huangli", "календарь дня"), ("daily", "прогноз on/off"), ("lang", "язык"), ("help", "помощь")]},
    "en": {"short": "🔮 AI fortune telling: BaZi, Tarot, astrology, compatibility, daily fortune. Entertainment only.",
           "desc": "🔮 AI fortune bot\n\n🀄 BaZi Four Pillars & five elements\n🃏 78-card Tarot\n♈ Sun / Moon / Ascendant\n💞 Compatibility\n☀️ Daily fortune push\n\n⚠️ For entertainment only. Tap Start!",
           "cmds": [("start", "start / menu"), ("bazi", "BaZi chart"), ("tarot", "Tarot"), ("astro", "astrology"),
                    ("compat", "compatibility"), ("huangli", "today's almanac"), ("daily", "daily fortune on/off"), ("lang", "language"), ("help", "help")]},
}
_add("daily_msg", "☀️ **每日运势 · {date}**\n\n🀄 今日日柱：**{day}**（你的日主 {dm}）\n\n🃏 今日之牌：{card}\n\n♈ {horo}",
     "☀️ **Прогноз · {date}**\n\n🀄 Столп дня: **{day}** (ваш хозяин дня {dm})\n\n🃏 Карта дня: {card}\n\n♈ {horo}",
     "☀️ **Daily fortune · {date}**\n\n🀄 Day pillar: **{day}** (your Day Master {dm})\n\n🃏 Card of the day: {card}\n\n♈ {horo}")
_add("huangli", "📜 **今日黄历 · {date}**\n\n🌙 农历：{lunar}\n🀄 日柱：**{day}**\n\n✅ 宜：{yi}\n⛔ 忌：{ji}",
     "📜 **Календарь дня · {date}**\n\n🌙 Лунная дата: {lunar}\n🀄 Столп дня: **{day}**\n\n✅ Благоприятно: {yi}\n⛔ Неблагоприятно: {ji}",
     "📜 **Chinese almanac · {date}**\n\n🌙 Lunar date: {lunar}\n🀄 Day pillar: **{day}**\n\n✅ Good for: {yi}\n⛔ Avoid: {ji}")
_add("compat_result", "💞 **合盘结果**\n\n👤 A：{pa}（{sa}）\n👤 B：{pb}（{sb}）\n\n🌈 五行契合：{s1}/100\n✨ 星座契合：{s2}/100\n❤️ 综合：{total}/100",
     "💞 **Совместимость**\n\n👤 A: {pa} ({sa})\n👤 B: {pb} ({sb})\n\n🌈 Пять стихий: {s1}/100\n✨ Знаки: {s2}/100\n❤️ Итого: {total}/100",
     "💞 **Compatibility**\n\n👤 A: {pa} ({sa})\n👤 B: {pb} ({sb})\n\n🌈 Five elements: {s1}/100\n✨ Zodiac: {s2}/100\n❤️ Overall: {total}/100")

# ---------------- v3: dream / lots / I Ching / lucky ----------------
_add("btn_dream", "🌙 解梦", "🌙 Сонник", "🌙 Dreams")
_add("btn_lot", "🎋 求签", "🎋 Жребий", "🎋 Fortune lot")
_add("btn_iching", "☯️ 易经", "☯️ И-цзин", "☯️ I Ching")
_add("btn_lucky", "🍀 今日幸运", "🍀 Удача дня", "🍀 Lucky today")
_add("btn_lang", "🌐 语言", "🌐 Язык", "🌐 Language")
_add("btn_help", "❓ 帮助", "❓ Помощь", "❓ Help")
_add("ask_dream", "🌙 **解梦**\n\n把你的梦讲给我听吧：梦里有谁、发生了什么、你有什么感觉。\n例如：`梦见自己在海边，牙齿掉了，但一点也不害怕`",
     "🌙 **Толкование снов**\n\nРасскажите свой сон: кто в нём был, что происходило и что вы чувствовали.\nНапример: `Мне снилось, что я на берегу моря и у меня выпал зуб, но страшно не было`",
     "🌙 **Dream reading**\n\nTell me your dream: who was there, what happened and how you felt.\nE.g. `I was on a beach, my tooth fell out, but I wasn't scared`")
_add("dream_too_short", "🙈 再多写一点吧（至少 10 个字），细节越多，解得越准。",
     "🙈 Напишите чуть подробнее (хотя бы 10 символов) — чем больше деталей, тем точнее толкование.",
     "🙈 Please add a bit more detail (at least 10 characters) — the more detail, the better the reading.")
_add("dream_head", "🌙 **你的梦**", "🌙 **Ваш сон**", "🌙 **Your dream**")
_add("dream_symbols", "🔎 **梦中意象**", "🔎 **Образы сна**", "🔎 **Dream symbols**")
_add("dream_generic", "这个梦没有出现常见的典型意象。梦往往是白天情绪的回声：留意梦里最强烈的那种感觉，它可能正对应你最近在意的事。",
     "В этом сне нет типичных символов из сонника. Сны часто — эхо дневных переживаний: прислушайтесь к самому сильному чувству из сна — возможно, оно связано с тем, что волнует вас сейчас.",
     "This dream has no classic dream-book symbols. Dreams often echo the day's feelings: notice the strongest emotion in it — it may point to what's on your mind lately.")
_add("dream_question", "💭 想一想：这个梦里的感觉，最近在生活中哪里也出现过？",
     "💭 Подумайте: где в жизни вы недавно испытывали то же чувство, что и во сне?",
     "💭 Reflect: where in your waking life have you felt the same way recently?")
_add("ask_lot", "🎋 **求签**\n\n先在心里默念你的问题，也可以写下来，例如：`今年适合换城市生活吗？`\n准备好了就点「直接抽签」。",
     "🎋 **Жребий**\n\nМысленно задайте вопрос — или напишите его, например: `Стоит ли мне в этом году переехать?`\nКогда будете готовы, нажмите «Тянуть жребий».",
     "🎋 **Fortune lot**\n\nHold your question in mind — or type it, e.g. `Is this a good year to move cities?`\nWhen you're ready, tap “Draw now”.")
_add("btn_draw_now", "🎋 直接抽签", "🎋 Тянуть жребий", "🎋 Draw now")
_add("lot_head", "🎋 **第 {n} 签 · {grade}**", "🎋 **Жребий № {n} · {grade}**", "🎋 **Lot No. {n} · {grade}**")
_add("lot_verse", "📜 **签诗**", "📜 **Стихи** (кит.)", "📜 **Verse** (Chinese)")
_add("lot_meaning", "🔎 **签解**", "🔎 **Смысл**", "🔎 **Meaning**")
_add("lot_note", "ℹ️ 本签诗为本机器人原创，并非出自任何寺庙签谱。",
     "ℹ️ Эти стихи написаны специально для этого бота и не взяты из храмовых сборников.",
     "ℹ️ These verses were written for this bot; they are not from any temple lot collection.")
_add("ask_iching", "☯️ **易经起卦**\n\n用三枚铜钱法起卦，共摇六次。\n可以先写下你的问题，例如：`这个合作值得推进吗？`，或者点「直接起卦」。",
     "☯️ **Гадание по И-цзин**\n\nМетод трёх монет: шесть бросков.\nМожно сначала написать вопрос, например: `Стоит ли развивать это сотрудничество?` — или нажать «Бросить монеты».",
     "☯️ **I Ching**\n\nThree-coin method, six tosses.\nYou can type your question first, e.g. `Should I push this partnership forward?` — or tap “Cast now”.")
_add("btn_cast_now", "🪙 直接起卦", "🪙 Бросить монеты", "🪙 Cast now")
_add("iching_primary", "**本卦**：{name}\n{upper} 上 · {lower} 下", "**Основная гексаграмма**: {name}\nверх {upper} · низ {lower}", "**Primary hexagram**: {name}\nupper {upper} · lower {lower}")
_add("iching_moving", "🔁 **变爻**：{lines}", "🔁 **Подвижные черты**: {lines}", "🔁 **Changing lines**: {lines}")
_add("iching_static", "🔒 没有变爻：以本卦为主。", "🔒 Подвижных черт нет — смотрим на основную гексаграмму.", "🔒 No changing lines — read the primary hexagram.")
_add("iching_changed", "➡️ **之卦**：{name}", "➡️ **Производная гексаграмма**: {name}", "➡️ **Resulting hexagram**: {name}")
_add("iching_coins", "🪙 六次投掷（自下而上）：{coins}", "🪙 Шесть бросков (снизу вверх): {coins}", "🪙 Six tosses (bottom to top): {coins}")
_add("iching_key", "🔑 {kw}", "🔑 {kw}", "🔑 {kw}")
_add("lucky", "🍀 **今日幸运 · {date}**\n\n🎨 幸运色：**{color}**\n🔢 幸运数字：**{nums}**\n🧭 吉利方位：**{dir}**\n☯️ 今日旺五行：{el}\n\n{why}",
     "🍀 **Удача дня · {date}**\n\n🎨 Цвет: **{color}**\n🔢 Числа: **{nums}**\n🧭 Направление: **{dir}**\n☯️ Стихия дня: {el}\n\n{why}",
     "🍀 **Lucky today · {date}**\n\n🎨 Colour: **{color}**\n🔢 Numbers: **{nums}**\n🧭 Direction: **{dir}**\n☯️ Element of the day: {el}\n\n{why}")
_add("lucky_why_dm", "根据你的日主 {dm} 和今日日柱 {day} 推算。", "Рассчитано по вашему хозяину дня {dm} и столпу дня {day}.", "Based on your Day Master {dm} and today's day pillar {day}.")
_add("lucky_why_none", "按今日日柱 {day} 推算。保存出生资料（/bazi）后会按你的八字个性化。",
     "Рассчитано по столпу дня {day}. Сохраните данные рождения (/bazi), и подсказка станет персональной.",
     "Based on today's day pillar {day}. Save your birth data (/bazi) to personalise it.")
_add("daily_lucky", "🍀 幸运色 {color} · 幸运数字 {nums}", "🍀 Цвет {color} · числа {nums}", "🍀 Colour {color} · numbers {nums}")
_add("help", "❓ **帮助**\n\n"
     "🀄 /bazi 八字排盘\n🃏 /tarot 塔罗\n♈ /astro 星座\n💞 /compat 合盘\n🌙 /dream 解梦\n🎋 /lot 求签\n☯️ /iching 易经起卦\n🍀 /lucky 今日幸运色与数字\n📜 /huangli 今日黄历\n\n"
     "☀️ /daily on 9：每天 9 点推送运势（/daily off 关闭）\n🌐 /lang 切换语言　✖️ /cancel 取消\n\n"
     "日期、时辰、城市都可以点按钮选，也可以直接输入。\n\n*⚠️ 仅供娱乐*",
     "❓ **Помощь**\n\n"
     "🀄 /bazi Бацзы\n🃏 /tarot Таро\n♈ /astro астрология\n💞 /compat совместимость\n🌙 /dream сонник\n🎋 /lot жребий\n☯️ /iching И-цзин\n🍀 /lucky цвет и числа дня\n📜 /huangli китайский календарь\n\n"
     "☀️ /daily on 9 — прогноз каждый день в 9:00 (/daily off — выключить)\n🌐 /lang язык   ✖️ /cancel отмена\n\n"
     "Дату, час и город можно выбрать кнопками или ввести вручную.\n\n*⚠️ Только для развлечения*",
     "❓ **Help**\n\n"
     "🀄 /bazi BaZi chart\n🃏 /tarot Tarot\n♈ /astro astrology\n💞 /compat compatibility\n🌙 /dream dream reading\n🎋 /lot fortune lot\n☯️ /iching I Ching\n🍀 /lucky lucky colour & numbers\n📜 /huangli Chinese almanac\n\n"
     "☀️ /daily on 9 — daily fortune at 9:00 (/daily off to stop)\n🌐 /lang language   ✖️ /cancel cancel\n\n"
     "Date, hour and city can be tapped or typed.\n\n*⚠️ For entertainment only*")
_add("daily_msg", "☀️ **每日运势 · {date}**\n\n🀄 今日日柱：**{day}**（你的日主 {dm}）\n{lucky}\n\n🃏 今日之牌：{card}\n\n♈ {horo}",
     "☀️ **Прогноз · {date}**\n\n🀄 Столп дня: **{day}** (ваш хозяин дня {dm})\n{lucky}\n\n🃏 Карта дня: {card}\n\n♈ {horo}",
     "☀️ **Daily fortune · {date}**\n\n🀄 Day pillar: **{day}** (your Day Master {dm})\n{lucky}\n\n🃏 Card of the day: {card}\n\n♈ {horo}")
_add("error", "😵 出了点小问题，请再试一次。", "😵 Что-то пошло не так, попробуйте ещё раз.", "😵 Something went wrong, please try again.")
_add("too_long", "✂️ 内容太长了，请控制在 {n} 字以内。", "✂️ Слишком длинно — не больше {n} символов, пожалуйста.", "✂️ That's too long — please keep it under {n} characters.")

for _L, _cmds in (("zh", [("dream", "解梦"), ("lot", "求签"), ("iching", "易经起卦"), ("lucky", "今日幸运")]),
                  ("ru", [("dream", "сонник"), ("lot", "жребий"), ("iching", "И-цзин"), ("lucky", "удача дня")]),
                  ("en", [("dream", "dream reading"), ("lot", "fortune lot"), ("iching", "I Ching"), ("lucky", "lucky colour & numbers")])):
    BOT_META[_L]["cmds"][5:5] = _cmds
BOT_META["zh"]["desc"] = ("🔮 AI 算命机器人\n\n🀄 八字四柱与五行\n🃏 78 张塔罗牌\n♈ 太阳 / 月亮 / 上升星座\n💞 合盘\n🌙 AI 解梦\n🎋 求签\n☯️ 易经六爻\n🍀 每日幸运色与数字\n☀️ 每日运势推送\n\n⚠️ 仅供娱乐，不构成任何建议。")
BOT_META["ru"]["desc"] = ("🔮 AI-гадалка\n\n🀄 Бацзы: четыре столпа и пять стихий\n🃏 Таро (78 карт)\n♈ Солнце / Луна / Асцендент\n💞 Совместимость\n🌙 Толкование снов\n🎋 Жребий\n☯️ И-цзин\n🍀 Цвет и числа удачи\n☀️ Ежедневный прогноз\n\n⚠️ Только для развлечения.")
BOT_META["en"]["desc"] = ("🔮 AI fortune bot\n\n🀄 BaZi Four Pillars & five elements\n🃏 78-card Tarot\n♈ Sun / Moon / Ascendant\n💞 Compatibility\n🌙 Dream reading\n🎋 Fortune lots\n☯️ I Ching\n🍀 Lucky colour & numbers\n☀️ Daily fortune push\n\n⚠️ For entertainment only.")
BOT_META["zh"]["short"] = "🔮 AI 算命：八字、塔罗、星座、解梦、求签、易经。仅供娱乐。"
BOT_META["ru"]["short"] = "🔮 AI-гадание: Бацзы, Таро, астрология, сонник, жребий, И-цзин. Для развлечения."
BOT_META["en"]["short"] = "🔮 AI fortunes: BaZi, Tarot, astrology, dreams, lots, I Ching. Entertainment only."

# ---------------- v4 fixes ----------------
_add("btn_draw_again", "🔄 再抽一张", "🔄 Вытянуть ещё", "🔄 Draw again")
_add("btn_use_saved_a", "✅ 我的资料作为 A", "✅ Мои данные как A", "✅ Use my data as A")
_add("compat_saved", "💞 **合盘**\n\n用你保存的资料作为第一个人吗？\n{summary}",
     "💞 **Совместимость**\n\nИспользовать ваши сохранённые данные как человека A?\n{summary}",
     "💞 **Compatibility**\n\nUse your saved birth data as person A?\n{summary}")
_add("today_tz", "{date}（{tz}）", "{date} ({tz})", "{date} ({tz})")
_add("tz_hint", "🕐 日期按 {tz} 计算，可用 /tz 改成你现在所在的时区。", "🕐 Дата считается по поясу {tz}; свой текущий пояс можно задать командой /tz.", "🕐 Dates use {tz}; set your current timezone with /tz.")
_add("tz_usage", "🕐 当前时区：**{tz}**\n设置方法：`/tz Moscow`、`/tz Asia/Shanghai` 或 `/tz +8`",
     "🕐 Текущий часовой пояс: **{tz}**\nКак изменить: `/tz Москва`, `/tz Europe/Berlin` или `/tz +3`",
     "🕐 Current timezone: **{tz}**\nChange it with `/tz London`, `/tz America/New_York` or `/tz +8`")
_add("tz_set", "✅ 时区已设为 **{tz}**。黄历、今日幸运和每日推送都会按这个时区计算。",
     "✅ Часовой пояс: **{tz}**. По нему считаются календарь дня, удача дня и ежедневный прогноз.",
     "✅ Timezone set to **{tz}**. The almanac, lucky-today and the daily push now use it.")
SHICHEN_ANIMALS = {
    "en": ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"],
    "ru": ["Крыса", "Бык", "Тигр", "Кролик", "Дракон", "Змея", "Лошадь", "Коза", "Обезьяна", "Петух", "Собака", "Свинья"],
}
for _L, _c in (("zh", [("tz", "设置时区")]), ("ru", [("tz", "часовой пояс")]), ("en", [("tz", "set timezone")])):
    BOT_META[_L]["cmds"].insert(-2, _c[0])


def shichen_label(i: int, lang: str) -> str:
    b, span, _ = SHICHEN[i]
    if lang == "zh":
        return f"{b}时 {span}"
    return f"{SHICHEN_ANIMALS.get(lang, SHICHEN_ANIMALS['en'])[i]} {span}"
