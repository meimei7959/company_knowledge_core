from __future__ import annotations

# Compatibility facade only. Feishu implementation lives in layered modules:
# gateway -> router -> intent/command -> executor. Keep this file small so new
# business logic cannot accumulate here again.
import sys
import types

from . import feishu_executor as _executor
from .feishu_gateway import handle_feishu_event as _gateway_handle_feishu_event


class _FeishuFacade(types.ModuleType):
    def __getattr__(self, name: str):
        return getattr(_executor, name)

    def __setattr__(self, name: str, value):
        if not name.startswith("_") and hasattr(_executor, name):
            setattr(_executor, name, value)
        return super().__setattr__(name, value)


def __getattr__(name: str):
    return getattr(_executor, name)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(dir(_executor)))


_executor.handle_feishu_event = _gateway_handle_feishu_event
handle_feishu_event = _gateway_handle_feishu_event
sys.modules[__name__].__class__ = _FeishuFacade
__all__ = [name for name in dir(_executor) if not name.startswith("_")] + ["handle_feishu_event"]
