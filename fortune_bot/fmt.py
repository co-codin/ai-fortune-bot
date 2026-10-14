"""Safe Telegram HTML rendering: escape everything, then turn Markdown emphasis
(**bold**, __bold__, *italic*) into <b>/<i>. Headings lose their '#'.
Because escaping happens first, user or LLM text can never inject tags."""
import html
import re

_BOLD = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*|__(?=\S)(.+?)(?<=\S)__", re.S)
_ITAL = re.compile(r"(?<![\w*])\*(?=\S)([^*\n]+?)(?<=\S)\*(?![\w*])")
_CODE = re.compile(r"`([^`\n]+)`")
_HEAD = re.compile(r"^\s{0,3}#{1,6}\s+(.+)$", re.M)


def to_html(text: str) -> str:
    s = html.escape(text.replace("\x00", ""), quote=False)
    codes = []

    def keep(m):
        codes.append(m.group(1))
        return f"\x00{len(codes) - 1}\x00"
    s = _CODE.sub(keep, s)
    s = _HEAD.sub(r"**\1**", s)
    s = _BOLD.sub(lambda m: f"<b>{m.group(1) or m.group(2)}</b>", s)
    s = _ITAL.sub(r"<i>\1</i>", s)
    return re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", s)
