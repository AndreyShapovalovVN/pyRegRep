"""Utility helpers for working with nested dictionaries."""

from typing import Any


def deep_get(data: dict, *keys: Any, default: Any = None) -> Any:
    """Safely read nested keys from a dictionary.

    Args:
        data: Source dictionary.
        *keys: Sequence of keys to traverse.
        default: Value returned when key path is missing or intermediate value is not a dict.

    Returns:
        Value by key path or ``default`` when the path cannot be resolved.
    """
    for key in keys:
        if not isinstance(data, dict):
            return default
        data = data.get(key)
    return data if data is not None else default

