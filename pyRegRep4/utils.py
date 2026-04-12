"""Utility helpers for working with nested dictionaries."""

from typing import Any


def deep_get(data: dict[Any, Any], *keys: str, default: Any = None) -> Any:
    """Safely read nested keys from a dictionary.

    Args:
        data: Source dictionary.
        *keys: Sequence of keys to traverse.
        default: Value returned when the key path is missing or the intermediate value is not a dict.

    Returns:
        Value by key path or "default" when the path cannot be resolved.
    """
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return current if current is not None else default

