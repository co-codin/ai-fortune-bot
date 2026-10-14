"""I Ching (周易) — 64 King Wen hexagrams and the three-coin method.

Coins: each coin heads=3, tails=2; the sum of three coins gives a line:
  6 old yin (changing, ⚋→⚊)  7 young yang ⚊  8 young yin ⚋  9 old yang (changing, ⚊→⚋)
Probabilities 1/8, 3/8, 3/8, 1/8. Lines are cast bottom (line 1) to top (line 6).
Hexagram numbers come from the standard King Wen table (upper trigram × lower trigram).
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass

_rng = secrets.SystemRandom()

# trigram lines bottom->top, 1 = yang
TRIGRAMS = {
    (1, 1, 1): ("乾", "☰", "Heaven", "Небо"), (1, 1, 0): ("兑", "☱", "Lake", "Озеро"),
    (1, 0, 1): ("离", "☲", "Fire", "Огонь"), (1, 0, 0): ("震", "☳", "Thunder", "Гром"),
    (0, 1, 1): ("巽", "☴", "Wind", "Ветер"), (0, 1, 0): ("坎", "☵", "Water", "Вода"),
    (0, 0, 1): ("艮", "☶", "Mountain", "Гора"), (0, 0, 0): ("坤", "☷", "Earth", "Земля"),
}
_ORDER = ["乾", "震", "坎", "艮", "坤", "巽", "离", "兑"]
_KW = [  # rows: upper trigram, cols: lower trigram (order 乾 震 坎 艮 坤 巽 离 兑)
    [1, 25, 6, 33, 12, 44, 13, 10],
    [34, 51, 40, 62, 16, 32, 55, 54],
    [5, 3, 29, 39, 8, 48, 63, 60],
    [26, 27, 4, 52, 23, 18, 22, 41],
    [11, 24, 7, 15, 2, 46, 36, 19],
    [9, 42, 59, 53, 20, 57, 37, 61],
    [14, 21, 64, 56, 35, 50, 30, 38],
    [43, 17, 47, 31, 45, 28, 49, 58],
]

ZH = ("乾 坤 屯 蒙 需 讼 师 比 小畜 履 泰 否 同人 大有 谦 豫 随 蛊 临 观 噬嗑 贲 剥 复 无妄 大畜 颐 大过 坎 离 "
      "咸 恒 遯 大壮 晋 明夷 家人 睽 蹇 解 损 益 夬 姤 萃 升 困 井 革 鼎 震 艮 渐 归妹 丰 旅 巽 兑 涣 节 中孚 小过 既济 未济").split()
EN = ["The Creative", "The Receptive", "Difficulty at the Beginning", "Youthful Folly", "Waiting", "Conflict",
      "The Army", "Holding Together", "Small Taming", "Treading", "Peace", "Standstill", "Fellowship",
      "Great Possession", "Modesty", "Enthusiasm", "Following", "Work on the Decayed", "Approach", "Contemplation",
      "Biting Through", "Grace", "Splitting Apart", "Return", "Innocence", "Great Taming", "Nourishment",
      "Great Exceeding", "The Abysmal Water", "The Clinging Fire", "Influence", "Duration", "Retreat", "Great Power",
      "Progress", "Darkening of the Light", "The Family", "Opposition", "Obstruction", "Deliverance", "Decrease",
      "Increase", "Breakthrough", "Coming to Meet", "Gathering Together", "Pushing Upward", "Oppression", "The Well",
      "Revolution", "The Cauldron", "The Arousing Thunder", "Keeping Still", "Gradual Development",
      "The Marrying Maiden", "Abundance", "The Wanderer", "The Gentle Wind", "The Joyous Lake", "Dispersion",
      "Limitation", "Inner Truth", "Small Exceeding", "After Completion", "Before Completion"]
RU = ["Творчество", "Исполнение", "Начальная трудность", "Недоразвитость", "Необходимость ждать", "Тяжба",
      "Войско", "Приближение", "Воспитание малым", "Наступление", "Расцвет", "Упадок", "Единомышленники",
      "Обладание великим", "Смирение", "Вольность", "Последование", "Исправление порчи", "Посещение",
      "Созерцание", "Стиснутые зубы", "Убранство", "Разорение", "Возврат", "Беспорочность", "Воспитание великим",
      "Питание", "Переразвитие великого", "Повторная опасность", "Сияние", "Взаимодействие", "Постоянство",
      "Бегство", "Мощь великого", "Восход", "Поражение света", "Домашние", "Разлад", "Препятствие",
      "Разрешение", "Убыль", "Приумножение", "Выход", "Перечение", "Воссоединение", "Подъём", "Истощение",
      "Колодец", "Смена", "Жертвенник", "Возбуждение", "Сосредоточенность", "Постепенность", "Невеста",
      "Изобилие", "Странствие", "Проникновение", "Радость", "Раздробление", "Ограничение", "Внутренняя правда",
      "Переразвитие малого", "Уже конец", "Ещё не конец"]
# one-line modern keywords (fallback when no LLM): zh | en | ru
KEY = [
 ("刚健进取，自强不息", "strength, initiative, steady effort", "сила, инициатива, упорство"),
 ("柔顺包容，厚德载物", "receptivity, support, patience", "восприимчивость, поддержка, терпение"),
 ("万事开头难，稳住求援", "early chaos; get help and hold steady", "трудное начало; держитесь и ищите помощь"),
 ("虚心求教，启蒙学习", "learning, humility, asking good questions", "учёба, скромность, правильные вопросы"),
 ("耐心等待时机", "patience; wait for the right moment", "терпение; ждите подходящего момента"),
 ("争执宜和解，不宜硬拼", "dispute; seek settlement over victory", "спор; ищите согласие, а не победу"),
 ("组织纪律，团结力量", "discipline, organisation, leadership", "дисциплина, организация, лидерство"),
 ("亲近相辅，择善而从", "closeness, alliance, choosing well", "сближение, союз, верный выбор"),
 ("小有积蓄，蓄势待发", "small restraint; gather strength quietly", "малые накопления; копите силы"),
 ("谨慎行事，以礼待人", "careful conduct, tact, courtesy", "осторожность, такт, вежливость"),
 ("通泰顺利，上下相和", "harmony, flow, prosperity", "гармония, поток, процветание"),
 ("闭塞不通，守正待时", "stagnation; keep integrity and wait", "застой; сохраняйте честность и ждите"),
 ("志同道合，合作共赢", "fellowship, shared goals", "единомыслие, общие цели"),
 ("丰盛富足，宜分享", "abundance; share it generously", "изобилие; делитесь щедро"),
 ("谦虚有益，满招损", "modesty brings success", "скромность приносит успех"),
 ("愉悦振奋，顺势而动", "enthusiasm; move with momentum", "воодушевление; двигайтесь с потоком"),
 ("随机应变，择善而随", "adapting, following wisely", "гибкость, мудрое следование"),
 ("整治积弊，除旧布新", "repairing what was spoiled", "исправление застарелых проблем"),
 ("机会临近，积极把握", "opportunity approaching; engage", "возможность близко; действуйте"),
 ("观察反思，先看清再行动", "observe and reflect before acting", "наблюдайте и размышляйте перед действием"),
 ("果断处理障碍", "bite through obstacles decisively", "решительно устраняйте препятствия"),
 ("注重修饰，也勿忘本质", "beauty and form — keep the substance", "красота и форма — не забывайте суть"),
 ("剥落衰退，宜守不宜进", "decline; protect rather than push", "упадок; берегите, а не наступайте"),
 ("一阳来复，重新开始", "return, renewal, a fresh start", "возврат, обновление, новый старт"),
 ("真诚自然，勿存妄念", "sincerity, acting without guile", "искренность, действие без хитрости"),
 ("厚积薄发，蓄养大德", "great restraint; build deep reserves", "большие накопления; копите силы и знания"),
 ("颐养身心，慎言节食", "nourishment of body and mind", "питание тела и духа"),
 ("负荷过重，需调整", "overload; something must give", "перегрузка; нужно что-то изменить"),
 ("重重险阻，守信前行", "repeated danger; stay true and keep flowing", "повторная опасность; оставайтесь верны себе"),
 ("光明依附，明辨是非", "clarity, brightness, right attachment", "ясность, свет, верная опора"),
 ("感应相通，真情互动", "mutual attraction, influence", "взаимное притяжение, влияние"),
 ("持之以恒", "duration, commitment, consistency", "постоянство, верность, последовательность"),
 ("适时退避，保存实力", "strategic retreat", "стратегическое отступление"),
 ("强盛有力，勿恃强", "great power — use it rightly", "большая сила — используйте её верно"),
 ("晋升进步，前景光明", "progress, rising, recognition", "продвижение, рост, признание"),
 ("光明受损，韬光养晦", "dimmed light; protect your inner light", "свет приглушён; берегите внутренний свет"),
 ("家庭和睦，各司其职", "family, roles, home harmony", "семья, роли, домашний лад"),
 ("意见相左，求同存异", "opposition; find common ground in small things", "разлад; ищите согласие в малом"),
 ("前路艰难，反求诸己", "obstruction; look inward, seek allies", "препятствие; загляните в себя, ищите союзников"),
 ("困难化解，宽恕释怀", "release, relief, forgiveness", "освобождение, облегчение, прощение"),
 ("减损有益，简化欲望", "decrease; simplify to gain", "убыль; упрощайте, чтобы выиграть"),
 ("增益助人，乘势而为", "increase; benefit others and grow", "приумножение; помогайте и растите"),
 ("决断突破，公开坦荡", "breakthrough, resolute honesty", "прорыв, решительная честность"),
 ("不期而遇，慎重对待", "unexpected encounter; be discerning", "неожиданная встреча; будьте разборчивы"),
 ("聚集团结，共同目标", "gathering, community", "собрание, сообщество"),
 ("步步上升，稳健积累", "steady upward growth", "постепенный подъём"),
 ("困顿受限，守志不移", "exhaustion; keep your resolve", "истощение; сохраняйте решимость"),
 ("井养不穷，回归根本", "the well; inner resources, fundamentals", "колодец; внутренние ресурсы, основы"),
 ("变革更新，顺天应人", "revolution, timely change", "смена, своевременные перемены"),
 ("鼎新立制，滋养成就", "the cauldron; transformation, culture", "жертвенник; преобразование, культура"),
 ("震动惊醒，临危不乱", "shock that awakens; stay calm", "потрясение пробуждает; сохраняйте спокойствие"),
 ("知止而定，静心专注", "stillness, stopping at the right place", "сосредоточенность, умение остановиться"),
 ("循序渐进", "gradual progress, step by step", "постепенность, шаг за шагом"),
 ("名分未正，谨慎处世", "subordinate position; act with care", "зависимое положение; действуйте осторожно"),
 ("盛极之时，居安思危", "abundance at its peak; enjoy and prepare", "изобилие на пике; радуйтесь и готовьтесь"),
 ("旅途在外，谨慎谦和", "the traveller; be modest abroad", "странник; скромность в пути"),
 ("柔和渗透，持续影响", "gentle, persistent influence", "мягкое, настойчивое влияние"),
 ("喜悦交流，以诚相待", "joy, open exchange", "радость, открытое общение"),
 ("涣散化解，重新凝聚", "dispersion; dissolve rigidity, reunite", "раздробление; растопите лёд, объединитесь"),
 ("节制有度", "limitation, healthy boundaries", "ограничение, здоровые границы"),
 ("诚信感人", "inner truth, sincerity", "внутренняя правда, искренность"),
 ("小事可为，大事宜慎", "small steps fine, big leaps risky", "малое удаётся, в большом — осторожность"),
 ("功成之后，防微杜渐", "after completion; guard what you've built", "после завершения; берегите сделанное"),
 ("尚未完成，充满可能", "before completion; full of potential", "ещё не конец; много возможностей"),
]
LINE_NAMES = {"zh": ["初", "二", "三", "四", "五", "上"], "en": ["1", "2", "3", "4", "5", "6"],
              "ru": ["1", "2", "3", "4", "5", "6"]}


def number(lines6) -> int:
    """lines6: bottom->top yang(1)/yin(0)."""
    lower, upper = tuple(lines6[:3]), tuple(lines6[3:])
    return _KW[_ORDER.index(TRIGRAMS[upper][0])][_ORDER.index(TRIGRAMS[lower][0])]


@dataclass
class Cast:
    values: list            # six coin sums 6..9, bottom->top
    primary: int
    changed: int | None     # resulting hexagram if any line changes

    @property
    def moving(self):
        return [i + 1 for i, v in enumerate(self.values) if v in (6, 9)]


def toss_line(rng=_rng) -> int:
    return sum(rng.choice((2, 3)) for _ in range(3))


def from_values(values) -> Cast:
    yang = [1 if v in (7, 9) else 0 for v in values]
    after = [1 - y if v in (6, 9) else y for y, v in zip(yang, values)]
    p = number(yang)
    return Cast(list(values), p, number(after) if after != yang else None)


def cast(rng=_rng) -> Cast:
    return from_values([toss_line(rng) for _ in range(6)])


def name(n: int, lang: str) -> str:
    i = n - 1
    if lang == "zh":
        return f"第{n}卦 {ZH[i]}"
    if lang == "ru":
        return f"№{n} «{RU[i]}» ({ZH[i]})"
    return f"#{n} {EN[i]} ({ZH[i]})"


def keyword(n: int, lang: str) -> str:
    return KEY[n - 1][{"zh": 0, "en": 1, "ru": 2}.get(lang, 1)]


def drawing(values) -> str:
    """Top line first, as hexagrams are drawn; changing lines marked."""
    rows = []
    for v in reversed(values):
        bar = "`███████`" if v in (7, 9) else "`███ ███`"
        rows.append(bar + ("  ○" if v == 9 else "  ✕" if v == 6 else ""))
    return "\n".join(rows)


def trigram_desc(n_lines, lang):
    t = TRIGRAMS[tuple(n_lines)]
    return f"{t[1]} {t[0] if lang == 'zh' else t[2] if lang == 'en' else t[3]}"
