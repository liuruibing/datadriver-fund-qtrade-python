"""Legacy Chanlun helper exports.

These helpers mirror the utility surface historically exposed by ``ZS_sig.py``
while relying on the existing ``czsc.utils.sig`` implementation.
"""

from __future__ import annotations

from .runtime import setup_local_czsc

setup_local_czsc()

from czsc.utils.sig import (
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

__all__ = [
    "cal_cross_num",
    "check_cross_info",
    "check_gap_info",
    "count_last_same",
    "create_single_signal",
    "cross_zero_axis",
    "down_cross_count",
    "fast_slow_cross",
    "get_sub_elements",
    "is_bis_down",
    "is_bis_up",
    "is_symmetry_zs",
    "same_dir_counts",
]
