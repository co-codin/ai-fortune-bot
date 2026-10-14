import re
import string

from fortune_bot.i18n import ELEMENT_NAMES, FALLBACK, HOROSCOPE_TIPS, LANGS, T, DM_TRAITS, detect_lang, t


def fields(s):
    return {f for _, f, _, _ in string.Formatter().parse(s) if f}


def test_every_key_in_every_language_with_same_placeholders():
    for key, tr in T.items():
        assert set(tr) == set(LANGS), key
        assert all(tr[L].strip() for L in LANGS), key
        assert fields(tr["zh"]) == fields(tr["ru"]) == fields(tr["en"]), key
    assert fields(FALLBACK["zh"]) == fields(FALLBACK["ru"]) == fields(FALLBACK["en"])
    for d in (DM_TRAITS, ):
        for v in d.values():
            assert set(v) == set(LANGS)
    assert all(len(HOROSCOPE_TIPS[L]) == 7 for L in LANGS)
    assert all(len(ELEMENT_NAMES[L]) == 5 for L in LANGS)


def test_disclaimer_present():
    for L in LANGS:
        assert "⚠️" in t("start", L) and "⚠️" in t("disclaimer", L)


def test_scripts_match_language():
    cyr, han = re.compile("[а-яА-Я]"), re.compile("[\u4e00-\u9fff]")
    for key, tr in T.items():
        if key in ("lang_set",):
            continue
        assert han.search(tr["zh"]) or key in ("compat_fallback", "iching_key", "today_tz"), key
        assert cyr.search(tr["ru"]) or key in ("compat_fallback", "iching_key", "today_tz"), key


def test_detect_lang_and_unknown_falls_back():
    assert detect_lang("zh-hans") == "zh" and detect_lang("ru") == "ru" and detect_lang("uk") == "ru"
    assert detect_lang("de") == "en" and detect_lang(None) == "en"
    assert t("cancelled", "xx") == "Cancelled."
