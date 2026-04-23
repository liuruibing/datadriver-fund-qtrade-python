"""Main Chanlun buy/sell point helpers."""

from __future__ import annotations

from typing import Dict, List

from .runtime import setup_local_czsc

setup_local_czsc()

from czsc.core import BI, CZSC, ZS, Direction, Operate

from .beichi import check_beichi
from .zhongshu import check_down_trend, check_up_trend, get_relevant_zss


def find_B1(bi_list: List[BI], zs_list: List[ZS], czsc_obj: CZSC) -> List[Dict]:
    buy_points = []
    for current_bi in bi_list:
        if current_bi.direction != Direction.Down:
            continue

        valid_zs_list = get_relevant_zss(current_bi, zs_list)
        if len(valid_zs_list) < 2 or not check_down_trend(valid_zs_list):
            continue

        last_zs = valid_zs_list[-1]
        if current_bi.low > last_zs.dd:
            continue

        prev_zs = valid_zs_list[-2]
        try:
            b_sdt = prev_zs.bis[-1].sdt
            b_edt = last_zs.bis[0].sdt
        except (AttributeError, IndexError):
            continue

        c_candidates = [
            bi for bi in getattr(last_zs, "bis", []) or []
            if bi.sdt <= current_bi.sdt and bi.direction == current_bi.direction
        ]
        if not c_candidates:
            continue

        c_sdt = max(c_candidates, key=lambda x: x.sdt).sdt
        c_edt = current_bi.edt

        if check_beichi(c_sdt, c_edt, b_sdt, b_edt, current_bi.direction, czsc_obj):
            buy_points.append({
                "dt": current_bi.edt,
                "price": current_bi.low,
                "op": Operate.LO,
                "op_desc": "B1",
                "bs_type": "B1",
            })

    return buy_points


def find_S1(bi_list: List[BI], zs_list: List[ZS], czsc_obj: CZSC) -> List[Dict]:
    sell_points = []
    for current_bi in bi_list:
        if current_bi.direction != Direction.Up:
            continue

        valid_zs_list = get_relevant_zss(current_bi, zs_list)
        if len(valid_zs_list) < 2 or not check_up_trend(valid_zs_list):
            continue

        last_zs = valid_zs_list[-1]
        if current_bi.high < last_zs.gg:
            continue

        prev_zs = valid_zs_list[-2]
        try:
            b_sdt = prev_zs.bis[-1].sdt
            b_edt = last_zs.bis[0].sdt
        except (AttributeError, IndexError):
            continue

        c_candidates = [
            bi for bi in getattr(last_zs, "bis", []) or []
            if bi.sdt <= current_bi.sdt and bi.direction == current_bi.direction
        ]
        if not c_candidates:
            continue

        c_sdt = max(c_candidates, key=lambda x: x.sdt).sdt
        c_edt = current_bi.edt

        if check_beichi(c_sdt, c_edt, b_sdt, b_edt, current_bi.direction, czsc_obj):
            sell_points.append({
                "dt": current_bi.edt,
                "price": current_bi.high,
                "op": Operate.LE,
                "op_desc": "S1",
                "bs_type": "S1",
            })

    return sell_points


def find_B2(bi_list: List[BI], b1_list: List[Dict]) -> List[Dict]:
    buy_points = []
    for b1 in b1_list:
        b1_dt = b1["dt"]
        b1_price = b1["price"]

        b1_bi_index = None
        for i, bi in enumerate(bi_list):
            if bi.edt == b1_dt:
                b1_bi_index = i
                break

        if b1_bi_index is None:
            continue

        for j in range(b1_bi_index + 1, len(bi_list)):
            current_bi = bi_list[j]
            if current_bi.direction != Direction.Down:
                continue
            if current_bi.low < b1_price:
                break

            buy_points.append({
                "dt": current_bi.edt,
                "price": current_bi.low,
                "op": Operate.LO,
                "op_desc": "B2",
                "bs_type": "B2",
            })
            break

    return buy_points


def find_S2(bi_list: List[BI], s1_list: List[Dict]) -> List[Dict]:
    sell_points = []
    for s1 in s1_list:
        s1_dt = s1["dt"]
        s1_price = s1["price"]

        s1_bi_index = None
        for i, bi in enumerate(bi_list):
            if bi.edt == s1_dt:
                s1_bi_index = i
                break

        if s1_bi_index is None:
            continue

        for j in range(s1_bi_index + 1, len(bi_list)):
            current_bi = bi_list[j]
            if current_bi.direction != Direction.Up:
                continue
            if current_bi.high > s1_price:
                break

            sell_points.append({
                "dt": current_bi.edt,
                "price": current_bi.high,
                "op": Operate.LE,
                "op_desc": "S2",
                "bs_type": "S2",
            })
            break

    return sell_points


def find_B3(bi_list: List[BI], zs_list: List[ZS]) -> List[Dict]:
    buy_points = []
    for i, current_bi in enumerate(bi_list):
        if current_bi.direction != Direction.Down:
            continue

        valid_zs_list = get_relevant_zss(current_bi, zs_list)
        if len(valid_zs_list) < 1 or i < 1:
            continue

        last_zs = valid_zs_list[-1]
        prev_bi = bi_list[i - 1]
        if prev_bi.direction != Direction.Up or not last_zs.bis:
            continue

        last_bi_in_zs = last_zs.bis[-1]
        if prev_bi.sdt != last_bi_in_zs.sdt or prev_bi.edt != last_bi_in_zs.edt:
            continue

        if current_bi.low > last_zs.zg:
            buy_points.append({
                "dt": current_bi.edt,
                "price": current_bi.low,
                "op": Operate.LO,
                "op_desc": "B3",
                "bs_type": "B3",
            })

    return buy_points


def find_S3(bi_list: List[BI], zs_list: List[ZS]) -> List[Dict]:
    sell_points = []
    for i, current_bi in enumerate(bi_list):
        if current_bi.direction != Direction.Up:
            continue

        valid_zs_list = get_relevant_zss(current_bi, zs_list)
        if len(valid_zs_list) < 1 or i < 1:
            continue

        last_zs = valid_zs_list[-1]
        prev_bi = bi_list[i - 1]
        if prev_bi.direction != Direction.Down or not last_zs.bis:
            continue

        last_bi_in_zs = last_zs.bis[-1]
        if prev_bi.sdt != last_bi_in_zs.sdt or prev_bi.edt != last_bi_in_zs.edt:
            continue

        if current_bi.high < last_zs.zd:
            sell_points.append({
                "dt": current_bi.edt,
                "price": current_bi.high,
                "op": Operate.LE,
                "op_desc": "S3",
                "bs_type": "S3",
            })

    return sell_points

__all__ = [
    "find_B1",
    "find_B2",
    "find_B3",
    "find_S1",
    "find_S2",
    "find_S3",
]
