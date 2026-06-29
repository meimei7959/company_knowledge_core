from __future__ import annotations

from typing import TYPE_CHECKING

from .core import Bundle

if TYPE_CHECKING:
    from .feishu_executor import FeishuIntentDecision, FeishuSettings


def classify_message_intent(bundle: Bundle, incoming: dict[str, str], settings: "FeishuSettings") -> "FeishuIntentDecision":
    from . import feishu_executor as impl

    return impl.classify_feishu_intent(bundle, incoming, settings)
