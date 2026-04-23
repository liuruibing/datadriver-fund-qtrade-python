"""Main Chanlun zhongshu helpers."""

from __future__ import annotations

from typing import List, Optional

from .runtime import setup_local_czsc

setup_local_czsc()

from czsc.core import BI, ZS, Direction


def get_zs_seq(bis: List[BI]) -> List[ZS]:
    """Get ZS sequence from consecutive bis."""

    def _has_overlap(bis3: List[BI]) -> bool:
        if len(bis3) != 3:
            return False
        return max(x.low for x in bis3) <= min(x.high for x in bis3)

    def _find_next_zs_start(start: int, pattern: List[Direction]) -> Optional[int]:
        idx = start
        while idx + 2 < len(bis):
            b0, b1, b2 = bis[idx], bis[idx + 1], bis[idx + 2]
            if (
                b0.direction == pattern[0]
                and b1.direction == pattern[1]
                and b2.direction == pattern[2]
                and _has_overlap([b0, b1, b2])
            ):
                return idx
            idx += 1
        return None

    zs_list = []
    if not bis:
        return []

    i = 0
    while i < len(bis):
        bi = bis[i]
        if not zs_list:
            zs_list.append(ZS(bis=[bi]))
            i += 1
            continue

        zs = zs_list[-1]
        if not zs.bis:
            zs.bis.append(bi)
            zs_list[-1] = zs
            i += 1
            continue

        is_break_down = bi.direction == Direction.Up and bi.high < zs.zd
        is_break_up = bi.direction == Direction.Down and bi.low > zs.zg
        if is_break_down or is_break_up:
            pattern = (
                [Direction.Up, Direction.Down, Direction.Up]
                if is_break_down
                else [Direction.Down, Direction.Up, Direction.Down]
            )
            start = _find_next_zs_start(i, pattern)
            if start is None:
                break
            zs_list.append(ZS(bis=bis[start : start + 3]))
            i = start + 3
            continue

        new_bis = list(zs.bis) + [bi]
        zs_list[-1] = ZS(bis=new_bis)
        i += 1

    return zs_list


def check_down_trend(zs_list: List[ZS]) -> bool:
    if len(zs_list) < 2:
        return False

    zs_last = zs_list[-1]
    zs_prev = zs_list[-2]
    return bool(zs_last.zg < zs_prev.zd)


def check_up_trend(zs_list: List[ZS]) -> bool:
    if len(zs_list) < 2:
        return False

    zs_last = zs_list[-1]
    zs_prev = zs_list[-2]
    return bool(zs_last.zd > zs_prev.zg)


def get_relevant_zss(current_bi: BI, zs_list: List[ZS]) -> List[ZS]:
    valid_zs_list = []
    for zs in zs_list:
        if not getattr(zs, "bis", None) or len(zs.bis) < 3:
            continue

        second_bi = zs.bis[1]
        if second_bi.sdt <= current_bi.sdt:
            valid_zs_list.append(zs)
    return valid_zs_list


def get_entry_BI(zs: ZS, bis: List[BI]) -> Optional[BI]:
    if not zs.bis:
        return None

    first_bi_in_zs = zs.bis[0]
    for i, bi in enumerate(bis):
        if bi.sdt == first_bi_in_zs.sdt and bi.edt == first_bi_in_zs.edt:
            if i > 0:
                return bis[i - 1]
            break

    return None


def get_next_zs(current_zs: ZS, zss_list: List[ZS]) -> Optional[ZS]:
    if not zss_list or current_zs is None:
        return None

    try:
        for i, zs in enumerate(zss_list):
            if zs.sdt == current_zs.sdt and zs.edt == current_zs.edt:
                if i + 1 < len(zss_list):
                    return zss_list[i + 1]
                return None
        return None
    except (AttributeError, IndexError):
        return None

__all__ = [
    "check_down_trend",
    "check_up_trend",
    "get_entry_BI",
    "get_next_zs",
    "get_relevant_zss",
    "get_zs_seq",
]
