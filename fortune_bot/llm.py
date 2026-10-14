"""Optional OpenAI-compatible LLM. Configure with LLM_BASE_URL, LLM_API_KEY, LLM_MODEL.
If any is missing, or the call fails, callers fall back to templates (returns None)."""
from __future__ import annotations

import logging
import os

import httpx

from .prompts import system

log = logging.getLogger(__name__)
_client: httpx.AsyncClient | None = None


def configured() -> bool:
    return all(os.getenv(k) for k in ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL"))


def _http():
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=float(os.getenv("LLM_TIMEOUT", "45")))
    return _client


async def complete(prompt: str, lang: str, max_tokens: int = 700, mode: str = "general",
                   words: int = 220) -> str | None:
    """Plain-text completion, or None (caller uses a template). Never raises."""
    if not configured():
        return None
    try:
        r = await _http().post(
            os.environ["LLM_BASE_URL"].rstrip("/") + "/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['LLM_API_KEY']}"},
            json={"model": os.environ["LLM_MODEL"], "max_tokens": max_tokens, "temperature": 0.7,
                  "messages": [{"role": "system", "content": system(mode, lang, words)},
                               {"role": "user", "content": prompt}]})
        r.raise_for_status()
        text = (r.json()["choices"][0]["message"]["content"] or "").strip()
        return text or None
    except Exception as e:  # noqa: BLE001 - any failure -> template fallback
        log.warning("LLM call failed (%s), using template", type(e).__name__)
        return None
