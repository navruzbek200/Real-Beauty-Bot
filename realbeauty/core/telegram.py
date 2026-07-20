"""
Blocking Telegram Bot API helpers for use from Django (admin, sync tasks).

The bot process itself uses aiogram; this module exists so synchronous code
can talk to Telegram without pulling in an event loop.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)

API_ROOT = "https://api.telegram.org"
TIMEOUT = 10


class TelegramError(RuntimeError):
    """Raised when the Bot API rejects a call or is unreachable."""


def call(method: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Call a Bot API method. Raises TelegramError on any failure."""
    token = settings.BOT_TOKEN
    if not token:
        raise TelegramError("BOT_TOKEN sozlanmagan.")
    request = urllib.request.Request(
        f"{API_ROOT}/bot{token}/{method}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            body = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        try:
            detail = json.loads(detail).get("description", detail)
        except json.JSONDecodeError:
            pass
        raise TelegramError(detail) from exc
    except Exception as exc:  # noqa: BLE001 — network/timeouts/JSON
        raise TelegramError(str(exc)) from exc
    if not body.get("ok"):
        raise TelegramError(body.get("description", "noma'lum xato"))
    return body.get("result", {})


def send_message(
    chat_id: int,
    text: str,
    parse_mode: str | None = None,
    reply_button: tuple[str, str] | None = None,
) -> None:
    """
    Send a message; `reply_button` is (label, callback_data) for a single
    inline button under it — enough for "reply to this" without pulling
    aiogram's keyboard types into synchronous Django code.
    """
    payload: dict[str, Any] = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_button:
        label, callback_data = reply_button
        payload["reply_markup"] = {
            "inline_keyboard": [[{"text": label, "callback_data": callback_data}]]
        }
    call("sendMessage", payload)


def file_url(file_id: str) -> str:
    """
    Resolve a file_id to a temporary download URL.

    Telegram keeps the file forever but the URL it hands back is short-lived
    (~1 hour), so callers must not persist the result.
    """
    path = call("getFile", {"file_id": file_id}).get("file_path")
    if not path:
        raise TelegramError("file_path qaytmadi.")
    return f"{API_ROOT}/file/bot{settings.BOT_TOKEN}/{path}"
