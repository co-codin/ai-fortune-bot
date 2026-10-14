"""Rider–Waite–Smith 78-card tarot deck with upright/reversed meanings in zh/ru/en.

Major Arcana have individual meanings. Minor Arcana meanings are composed from
the suit's domain plus the rank's traditional keyword (a standard teaching scheme).
Draws use secrets.SystemRandom (OS CSPRNG).
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass

_rng = secrets.SystemRandom()

# (en, zh, ru, upright en/zh/ru, reversed en/zh/ru)
MAJORS = [
 ("The Fool", "愚者", "Шут", ("new beginnings, spontaneity, a leap of faith", "新的开始、自由、勇于冒险", "новое начало, спонтанность, шаг веры"), ("recklessness, hesitation, naivety", "鲁莽、犹豫、天真", "безрассудство, колебания, наивность")),
 ("The Magician", "魔术师", "Маг", ("willpower, skill, manifestation", "意志力、技能、化想法为现实", "сила воли, мастерство, воплощение"), ("manipulation, untapped talent, poor planning", "操纵、才能未发挥、计划不周", "манипуляции, нераскрытый талант, плохое планирование")),
 ("The High Priestess", "女祭司", "Верховная Жрица", ("intuition, inner knowledge, mystery", "直觉、内在智慧、神秘", "интуиция, внутреннее знание, тайна"), ("secrets, ignored intuition, withdrawal", "秘密、忽视直觉、封闭", "секреты, игнорирование интуиции, замкнутость")),
 ("The Empress", "皇后", "Императрица", ("abundance, nurturing, creativity", "丰盛、滋养、创造力", "изобилие, забота, творчество"), ("dependence, creative block, smothering", "依赖、创造力受阻、过度保护", "зависимость, творческий блок, гиперопека")),
 ("The Emperor", "皇帝", "Император", ("structure, authority, stability", "秩序、权威、稳定", "структура, власть, стабильность"), ("rigidity, domination, lack of discipline", "僵化、专横、缺乏纪律", "жёсткость, деспотизм, недисциплинированность")),
 ("The Hierophant", "教皇", "Иерофант", ("tradition, guidance, institutions", "传统、指引、体制", "традиция, наставничество, институты"), ("rebellion, unconventional paths, dogma", "叛逆、非传统道路、教条", "бунт, нестандартный путь, догматизм")),
 ("The Lovers", "恋人", "Влюблённые", ("love, harmony, important choices", "爱情、和谐、重要抉择", "любовь, гармония, важный выбор"), ("disharmony, imbalance, misaligned values", "不和谐、失衡、价值观冲突", "разлад, дисбаланс, расхождение ценностей")),
 ("The Chariot", "战车", "Колесница", ("determination, control, victory", "决心、掌控、胜利", "решимость, контроль, победа"), ("lack of direction, aggression, obstacles", "迷失方向、冲动、受阻", "отсутствие направления, агрессия, препятствия")),
 ("Strength", "力量", "Сила", ("courage, patience, inner strength", "勇气、耐心、内在力量", "смелость, терпение, внутренняя сила"), ("self-doubt, weakness, insecurity", "自我怀疑、软弱、不安", "неуверенность, слабость, сомнения")),
 ("The Hermit", "隐士", "Отшельник", ("introspection, solitude, guidance", "内省、独处、寻求真理", "самоанализ, уединение, поиск истины"), ("isolation, loneliness, withdrawal", "孤立、寂寞、逃避", "изоляция, одиночество, уход в себя")),
 ("Wheel of Fortune", "命运之轮", "Колесо Фортуны", ("cycles, luck, turning point", "循环、好运、转折点", "циклы, удача, поворотный момент"), ("bad luck, resistance to change, setbacks", "厄运、抗拒变化、挫折", "неудача, сопротивление переменам, откат")),
 ("Justice", "正义", "Справедливость", ("fairness, truth, cause and effect", "公正、真相、因果", "справедливость, истина, причина и следствие"), ("unfairness, dishonesty, avoiding accountability", "不公、不诚实、逃避责任", "несправедливость, нечестность, уход от ответственности")),
 ("The Hanged Man", "倒吊人", "Повешенный", ("pause, surrender, new perspective", "暂停、放下、换个角度", "пауза, смирение, новый взгляд"), ("stalling, indecision, needless sacrifice", "拖延、犹豫不决、无谓牺牲", "застой, нерешительность, напрасная жертва")),
 ("Death", "死神", "Смерть", ("endings, transformation, transition", "结束、转化、过渡", "завершение, трансформация, переход"), ("resistance to change, stagnation", "抗拒改变、停滞", "сопротивление переменам, застой")),
 ("Temperance", "节制", "Умеренность", ("balance, moderation, patience", "平衡、适度、耐心", "баланс, умеренность, терпение"), ("excess, imbalance, impatience", "过度、失衡、急躁", "излишества, дисбаланс, нетерпение")),
 ("The Devil", "恶魔", "Дьявол", ("attachment, temptation, materialism", "执着、诱惑、物欲", "привязанность, искушение, материализм"), ("release, breaking free, reclaiming power", "解脱、挣脱束缚、重获掌控", "освобождение, разрыв оков, возвращение силы")),
 ("The Tower", "塔", "Башня", ("sudden upheaval, revelation, breakdown", "突变、真相揭露、崩塌", "внезапный переворот, откровение, крушение"), ("averted disaster, fear of change", "躲过灾难、害怕改变", "предотвращённая беда, страх перемен")),
 ("The Star", "星星", "Звезда", ("hope, renewal, inspiration", "希望、更新、灵感", "надежда, обновление, вдохновение"), ("despair, lack of faith, discouragement", "绝望、失去信心、气馁", "отчаяние, потеря веры, уныние")),
 ("The Moon", "月亮", "Луна", ("illusion, intuition, the subconscious", "幻象、直觉、潜意识", "иллюзия, интуиция, подсознание"), ("confusion lifting, released fear, truth", "迷雾散去、释放恐惧、真相", "рассеивание тумана, уход страха, правда")),
 ("The Sun", "太阳", "Солнце", ("joy, success, vitality", "喜悦、成功、活力", "радость, успех, жизненная сила"), ("temporary sadness, overconfidence", "暂时的低落、过度自信", "временная грусть, самонадеянность")),
 ("Judgement", "审判", "Суд", ("awakening, reckoning, renewal", "觉醒、反省、重生", "пробуждение, переоценка, возрождение"), ("self-doubt, refusing the call", "自我怀疑、拒绝召唤", "сомнение в себе, отказ от призыва")),
 ("The World", "世界", "Мир", ("completion, achievement, wholeness", "圆满、成就、完整", "завершение, достижение, целостность"), ("incompletion, delays, lack of closure", "未完成、延误、缺少收尾", "незавершённость, задержки, отсутствие финала")),
]

SUITS = [  # key, names en/zh/ru, domain en/zh/ru
 ("wands", ("Wands", "权杖", "Жезлов"), ("action and drive", "行动与动力", "действие и энергия")),
 ("cups", ("Cups", "圣杯", "Кубков"), ("feelings and relationships", "情感与人际", "чувства и отношения")),
 ("swords", ("Swords", "宝剑", "Мечей"), ("thoughts and decisions", "思考与决断", "мысли и решения")),
 ("pentacles", ("Pentacles", "星币", "Пентаклей"), ("resources and practical matters", "资源与现实事务", "ресурсы и практические дела")),
]
RANKS = [  # names en/zh/ru, upright en/zh/ru, reversed en/zh/ru
 (("Ace", "王牌", "Туз"), ("a new opportunity", "新的机会", "новая возможность"), ("a missed or delayed start", "错失或延迟的开始", "упущенный или отложенный старт")),
 (("Two", "二", "Двойка"), ("balance and choices", "平衡与选择", "баланс и выбор"), ("indecision and imbalance", "犹豫与失衡", "нерешительность и дисбаланс")),
 (("Three", "三", "Тройка"), ("growth and collaboration", "成长与合作", "рост и сотрудничество"), ("delays and poor teamwork", "延误与配合不佳", "задержки и плохая командная работа")),
 (("Four", "四", "Четвёрка"), ("stability and rest", "稳定与休整", "стабильность и отдых"), ("stagnation or restlessness", "停滞或不安", "застой или беспокойство")),
 (("Five", "五", "Пятёрка"), ("challenge and conflict", "挑战与冲突", "вызов и конфликт"), ("recovery after conflict", "冲突后的恢复", "восстановление после конфликта")),
 (("Six", "六", "Шестёрка"), ("harmony and progress", "和谐与进展", "гармония и прогресс"), ("lingering in the past", "沉溺过去", "застревание в прошлом")),
 (("Seven", "七", "Семёрка"), ("assessment and perseverance", "评估与坚持", "оценка и упорство"), ("doubt and scattered effort", "怀疑与精力分散", "сомнения и распыление сил")),
 (("Eight", "八", "Восьмёрка"), ("movement and mastery", "行动与精进", "движение и мастерство"), ("feeling stuck or rushed", "受困或操之过急", "ощущение тупика или спешки")),
 (("Nine", "九", "Девятка"), ("near fulfilment", "接近圆满", "почти исполнение"), ("anxiety or overindulgence", "焦虑或放纵", "тревога или излишества")),
 (("Ten", "十", "Десятка"), ("completion of a cycle", "一个循环的完成", "завершение цикла"), ("burden or an ending you resist", "重担或抗拒结束", "бремя или сопротивление концу")),
 (("Page", "侍从", "Паж"), ("curiosity and new messages", "好奇与新讯息", "любопытство и новые вести"), ("immaturity and bad news", "不成熟与坏消息", "незрелость и плохие вести")),
 (("Knight", "骑士", "Рыцарь"), ("bold pursuit", "大胆追求", "смелое стремление"), ("haste and impulsiveness", "急躁与冲动", "спешка и импульсивность")),
 (("Queen", "王后", "Королева"), ("mature care and intuition", "成熟的关怀与直觉", "зрелая забота и интуиция"), ("insecurity or coldness", "不安或冷漠", "неуверенность или холодность")),
 (("King", "国王", "Король"), ("leadership and mastery", "领导力与掌控", "лидерство и мастерство"), ("control issues or misuse of power", "控制欲或滥用权力", "проблемы контроля или злоупотребление властью")),
]
_L = {"en": 0, "zh": 1, "ru": 2}


@dataclass(frozen=True)
class Card:
    id: str
    names: tuple
    upright: tuple
    reversed: tuple

    def name(self, lang):
        return self.names[_L.get(lang, 0)]

    def meaning(self, lang, is_reversed):
        return (self.reversed if is_reversed else self.upright)[_L.get(lang, 0)]


_THEME = ("theme", "主题", "тема")


def _compose(meaning, domain, j):
    """Neutral template: the rank keyword plus the suit's theme (no life-area assumption)."""
    return f"{meaning}（{_THEME[j]}：{domain}）" if j == 1 else f"{meaning} ({_THEME[j]}: {domain})"


def _build():
    deck = [Card(f"major_{i:02d}", (en, zh, ru), up, rv) for i, (en, zh, ru, up, rv) in enumerate(MAJORS)]
    for key, sn, dom in SUITS:
        for i, (rn, up, rv) in enumerate(RANKS, 1):
            names = (f"{rn[0]} of {sn[0]}", f"{sn[1]}{rn[1]}", f"{rn[2]} {sn[2]}")
            deck.append(Card(f"{key}_{i:02d}", names,
                             tuple(_compose(up[j], dom[j], j) for j in range(3)),
                             tuple(_compose(rv[j], dom[j], j) for j in range(3))))
    return deck


DECK = _build()


def draw(n: int, rng=_rng):
    """Draw n distinct cards; each independently upright/reversed (50/50)."""
    return [(c, rng.random() < 0.5) for c in rng.sample(DECK, n)]


def fmt(card, rev, lang):
    tag = {"zh": ("正位", "逆位"), "ru": ("прямая", "перевёрнутая"), "en": ("upright", "reversed")}[lang if lang in _L else "en"]
    return f"{label(card, rev, lang)} — {card.meaning(lang, rev)}"


def label(card, rev, lang):
    tag = {"zh": ("正位", "逆位"), "ru": ("прямая", "перевёрнутая"), "en": ("upright", "reversed")}[lang if lang in _L else "en"]
    return f"{card.name(lang)}（{tag[rev]}）" if lang == "zh" else f"{card.name(lang)} ({tag[rev]})"


SUIT_EMOJI = {"major": "🌟", "wands": "🪄", "cups": "🍷", "swords": "⚔️", "pentacles": "🪙"}


def emoji(card):
    return SUIT_EMOJI[card.id.split("_")[0]]
