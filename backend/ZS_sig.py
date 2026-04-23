"""Backward-compatible export surface for the main Chanlun algorithms.

The canonical implementations now live under ``core.chanlun``. This module is
kept so existing imports such as ``from ZS_sig import get_zs_seq`` continue to
work while the codebase is migrated in smaller steps.
"""

from __future__ import annotations

from core.chanlun.beichi import check_beichi
from core.chanlun.legacy_utils import (
    cal_cross_num,
    check_cross_info,
    check_gap_info,
    count_last_same,
    create_single_signal,
    cross_zero_axis,
    down_cross_count,
    fast_slow_cross,
    get_sub_elements,
    is_bis_down,
    is_bis_up,
    is_symmetry_zs,
    same_dir_counts,
)
from core.chanlun.signals import find_B1, find_B2, find_B3, find_S1, find_S2, find_S3
from core.chanlun.zhongshu import (
    check_down_trend,
    check_up_trend,
    get_entry_BI,
    get_next_zs,
    get_relevant_zss,
    get_zs_seq,
)

__all__ = [
    "cal_cross_num",
    "check_beichi",
    "check_cross_info",
    "check_down_trend",
    "check_gap_info",
    "check_up_trend",
    "count_last_same",
    "create_single_signal",
    "cross_zero_axis",
    "down_cross_count",
    "fast_slow_cross",
    "find_B1",
    "find_B2",
    "find_B3",
    "find_S1",
    "find_S2",
    "find_S3",
    "get_entry_BI",
    "get_next_zs",
    "get_relevant_zss",
    "get_sub_elements",
    "get_zs_seq",
    "is_bis_down",
    "is_bis_up",
    "is_symmetry_zs",
    "same_dir_counts",
]
