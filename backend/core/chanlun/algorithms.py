"""Stable imports for the main Chanlun algorithm modules.

The non-AI API path uses ``ZS_sig.py`` and ``BS_sig.py`` as the canonical
algorithm sources through structured ``core.chanlun`` import surfaces.
AI-only enhanced helpers live in ``ai_algorithms.py``.
"""

from __future__ import annotations

from typing import Any

from .runtime import setup_local_czsc

setup_local_czsc()

from .bs_signals import (
    cxt_first_buy_V260101,
    cxt_first_sell_V260101,
    cxt_second_bs_V260101,
    cxt_third_bs_V260101,
)
from .signals import find_B1, find_B2, find_B3, find_S1, find_S2, find_S3
from .zhongshu import get_zs_seq


def calculate_main_bs_points(c: Any, zs_list: list[Any]) -> dict[str, list[dict]]:
    """Calculate historical buy/sell points with the main ZS_sig.py logic."""

    b1_list = find_B1(c.bi_list, zs_list, c)
    b2_list = find_B2(c.bi_list, b1_list)
    b3_list = find_B3(c.bi_list, zs_list)
    s1_list = find_S1(c.bi_list, zs_list, c)
    s2_list = find_S2(c.bi_list, s1_list)
    s3_list = find_S3(c.bi_list, zs_list)

    return {
        "B1": b1_list,
        "B2": b2_list,
        "B3": b3_list,
        "S1": s1_list,
        "S2": s2_list,
        "S3": s3_list,
        "points": b1_list + b2_list + b3_list + s1_list + s2_list + s3_list,
    }


__all__ = [
    "calculate_main_bs_points",
    "cxt_first_buy_V260101",
    "cxt_first_sell_V260101",
    "cxt_second_bs_V260101",
    "cxt_third_bs_V260101",
    "find_B1",
    "find_B2",
    "find_B3",
    "find_S1",
    "find_S2",
    "find_S3",
    "get_zs_seq",
]
