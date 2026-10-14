"""求签 — 24 ORIGINAL fortune lots written for this bot (2026).

They follow the traditional form (grade + seven-character quatrain + explanation) but
are NOT taken from any temple set (观音灵签, 关帝灵签, etc.) and must never be presented
as such. Grades: 上上 / 上吉 / 中吉 / 中平 / 下 (no "大凶" — this is entertainment).
"""
from __future__ import annotations

import secrets

_rng = secrets.SystemRandom()

GRADES = {"上上": ("上上签", "Высший жребий", "Supreme"), "上吉": ("上吉签", "Очень благоприятный", "Very auspicious"),
          "中吉": ("中吉签", "Благоприятный", "Auspicious"), "中平": ("中平签", "Нейтральный", "Neutral"),
          "下": ("下签", "Предостерегающий", "Cautionary")}

# (grade, verse zh, meaning zh, meaning en, meaning ru)
LOTS = [
 ("上上", "春风十里百花开，久旱逢霖喜自来。\n莫道前程无觅处，青云有路步瑶台。",
  "久盼之事将有转机，贵人与机会同来，宜积极把握。",
  "What you have long waited for is turning in your favour; help and opportunity arrive together — step forward.",
  "То, чего вы давно ждали, поворачивается к лучшему: помощь и шанс приходят вместе — смело делайте шаг."),
 ("上吉", "一叶轻舟顺水行，两岸青山次第迎。\n不须摇橹争先后，自有清风送远程。",
  "顺势而为即可，不必强求速度，事情会自然推进。",
  "Go with the current; no need to force the pace — things will move forward on their own.",
  "Плывите по течению: не нужно торопить события, всё сдвинется само."),
 ("中吉", "山前云雾暂迷离，守得云开见月时。\n且把心灯常拨亮，前途自有好消息。",
  "眼下看不清方向，耐心守候，消息会在稍后到来。",
  "The path is foggy for now; keep your inner light on — good news comes a little later.",
  "Сейчас путь в тумане; храните внутренний свет — добрые вести придут чуть позже."),
 ("中平", "井中捞月费工夫，不若回头看自家。\n门前一树梅初放，何必天涯觅落花。",
  "答案可能就在身边，不必舍近求远。",
  "The answer may already be close at hand; no need to search far away.",
  "Ответ, возможно, уже рядом — не стоит искать его за тридевять земель."),
 ("上上", "金鳞岂是池中物，一遇风云便化龙。\n十年磨剑今朝试，万里鹏程此日中。",
  "长期积累迎来展示的时机，宜大胆表现自己。",
  "Long preparation meets its moment; it is a good time to show what you can do.",
  "Долгая подготовка встречает свой час — самое время показать, на что вы способны."),
 ("下", "急水滩头莫放舟，狂风未定且回头。\n待到潮平风静后，再扬帆去也无忧。",
  "时机未到，暂缓重大决定，等局势平稳再行动。",
  "The timing is off; postpone big decisions until the waters calm, then set sail without worry.",
  "Время ещё не пришло: отложите важные решения, пока вода не успокоится, — потом можно смело в путь."),
 ("中吉", "种豆南山待几时，晨兴理秽带月归。\n今朝汗水浇田地，秋后满仓不相欺。",
  "踏实付出必有回报，只是需要时间。",
  "Steady effort will pay off — it simply needs a season to ripen.",
  "Упорный труд окупится — просто ему нужно время созреть."),
 ("上吉", "桃李无言自成蹊，德行深处有人知。\n莫愁身畔无知己，自有良朋远道来。",
  "人缘渐旺，真诚待人会吸引志同道合的朋友。",
  "Your sincerity speaks for itself; kindred spirits and good friends are drawn to you.",
  "Ваша искренность говорит сама за себя — к вам тянутся близкие по духу люди."),
 ("中平", "半山亭里且停车，回望来时路几叉。\n不是前方无去处，须知歇脚也开花。",
  "适当休息与复盘，不是停滞，而是为下一段积蓄力量。",
  "Pausing to rest and look back is not standing still — it gathers strength for what comes next.",
  "Остановиться и оглянуться — не застой, а накопление сил для следующего отрезка пути."),
 ("下", "镜里看花花不真，水中捞月月无痕。\n劝君莫信甜言语，细辨方知假与真。",
  "注意辨别虚实，对过于美好的承诺保持清醒。",
  "Look closely at what is real; stay clear-headed about promises that sound too good.",
  "Отличайте настоящее от видимости и трезво смотрите на слишком сладкие обещания."),
 ("上上", "东方日出照乾坤，万象更新喜满门。\n旧事从今都放下，新程一路有贵人。",
  "放下过去，新阶段开启，处处有人相助。",
  "Let go of the past; a new chapter begins, with helpful people along the way.",
  "Отпустите прошлое: начинается новая глава, и на пути встретятся добрые помощники."),
 ("中吉", "细雨无声润物多，涓涓溪水汇成河。\n莫嫌今日收成少，积少成多奈若何。",
  "小步积累，量变终成质变。",
  "Small steps add up; quiet accumulation becomes real change.",
  "Маленькие шаги складываются: тихое накопление превращается в настоящие перемены."),
 ("中平", "两路分岔各有花，一边平坦一边沙。\n心中若有明灯在，何愁选错到天涯。",
  "面临选择，先问清自己真正想要什么。",
  "At a crossroads — first be clear about what you truly want.",
  "Вы на распутье — сначала честно ответьте себе, чего хотите на самом деле."),
 ("上吉", "梅花香自苦寒来，宝剑锋从磨砺开。\n莫怨此前多坎坷，春来正是好安排。",
  "过去的辛苦正在转化为能力与机会。",
  "Past hardship is turning into skill and opportunity.",
  "Прошлые трудности превращаются в умения и новые возможности."),
 ("下", "贪看路旁花满枝，误了归家日落时。\n收心莫向他处去，守住本分是良规。",
  "分心太多，宜收拢精力，专注主要目标。",
  "Too many distractions; gather your energy and focus on the main goal.",
  "Слишком много отвлечений: соберите силы и сосредоточьтесь на главном."),
 ("中吉", "月到中秋分外明，人逢喜事精神清。\n团圆自有团圆日，莫把相思付雁声。",
  "家人与亲密关系有好消息，团聚之时可期。",
  "Good news in family and close relationships; a reunion is within reach.",
  "Добрые вести в семье и близких отношениях — встреча уже не за горами."),
 ("上上", "龙门一跃上青天，多年心愿一朝圆。\n且将喜讯传亲友，更须谦逊保长年。",
  "重要心愿有望达成，成功后保持谦逊方能长久。",
  "An important wish may come true; stay humble and it will last.",
  "Заветное желание может исполниться; сохраните скромность — и удача будет долгой."),
 ("中平", "风吹杨柳自摇摆，不似青松立山崖。\n守得本心随境转，柔中带刚事自谐。",
  "灵活应变，但不要失去原则。",
  "Bend with circumstances, but keep your core principles.",
  "Будьте гибкими, но не изменяйте своим принципам."),
 ("下", "夜半行舟浪打头，前途未卜莫强求。\n且将灯火添油待，天明再作远方谋。",
  "当下信息不足，宜等待更清晰的时机再定。",
  "You don't have enough information yet; wait for a clearer moment before deciding.",
  "Сейчас слишком мало ясности — дождитесь более подходящего момента для решения."),
 ("中吉", "春蚕到老丝方尽，一缕一丝织锦成。\n莫问他人成功早，自家花开有时辰。",
  "不必与人比较，你的节奏自有其时。",
  "Don't compare yourself with others; your own timing will come.",
  "Не сравнивайте себя с другими — у вашего цветка своё время."),
 ("上吉", "清泉石上自流淌，明月松间照四方。\n心静自然天地阔，烦忧散尽好时光。",
  "放下焦虑，心境开阔，好运随之而来。",
  "Release your worries; a calm mind opens the way for good days.",
  "Отпустите тревоги — спокойный ум открывает дорогу хорошим дням."),
 ("中平", "旧屋梁间燕又来，去年巢在待重开。\n人间多少寻常事，循环往复莫疑猜。",
  "熟悉的事情再次出现，这次可以处理得更好。",
  "Something familiar returns; this time you can handle it better.",
  "Знакомая ситуация повторяется — на этот раз вы справитесь лучше."),
 ("上上", "百川东到海无涯，众志成城力可夸。\n独木难支千尺厦，同心协力满园花。",
  "合作带来成功，团队与伙伴是关键。",
  "Success comes through cooperation; partners and team are the key.",
  "Успех приходит через сотрудничество: ключ — в партнёрах и команде."),
 ("下", "满招损兮谦受益，登高莫忘脚下石。\n得意之时须回首，平安二字值千金。",
  "顺利时更要谨慎，避免骄傲与冒进。",
  "When things go well, be even more careful; avoid pride and rash moves.",
  "Когда всё идёт хорошо, будьте особенно внимательны: избегайте гордыни и поспешности."),
]


def draw(rng=_rng) -> int:
    """Returns a 1-based lot number."""
    return rng.randrange(len(LOTS)) + 1


def grade_name(n, lang):
    g = GRADES[LOTS[n - 1][0]]
    return g[{"zh": 0, "ru": 1, "en": 2}.get(lang, 2)]


def meaning(n, lang):
    return LOTS[n - 1][{"zh": 2, "en": 3, "ru": 4}.get(lang, 3)]
