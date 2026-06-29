from __future__ import annotations

from typing import TYPE_CHECKING

from .core import Bundle

if TYPE_CHECKING:
    from .feishu import FeishuIntentDecision, FeishuSettings


def classify_message_intent(bundle: Bundle, incoming: dict[str, str], settings: "FeishuSettings") -> "FeishuIntentDecision":
    from . import feishu as legacy

    return legacy.classify_feishu_intent(bundle, incoming, settings)
