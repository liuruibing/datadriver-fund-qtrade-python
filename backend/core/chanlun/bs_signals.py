"""Signal-style Chanlun helper functions migrated from ``BS_sig.py``."""

from __future__ import annotations

from collections import OrderedDict
from typing import List

import numpy as np
from czsc import CZSC
from czsc.core import BI, ZS, Direction
from czsc.signals.tas import update_ma_cache
from czsc.utils import create_single_signal, get_sub_elements

from .runtime import setup_local_czsc
from .zhongshu import get_zs_seq

setup_local_czsc()


def cxt_first_buy_V260101(c: CZSC, **kwargs) -> OrderedDict:
    di = int(kwargs.get("di", 1))

    def __check_first_buy(bis: List[BI]):
        res = {"match": False, "v1": "一买", "v2": f"{len(bis)}笔", "v3": "任意"}
        if len(bis) % 2 != 1 or bis[-1].direction == Direction.Up or bis[0].direction != bis[-1].direction:
            return res

        if max([x.high for x in bis]) != bis[0].high or min([x.low for x in bis]) != bis[-1].low:
            return res

        key_bis = []
        for i in range(0, len(bis) - 2, 2):
            if i == 0:
                key_bis.append(bis[i])
            else:
                b1, _, b3 = bis[i - 2: i + 1]
                if b3.low < b1.low:
                    key_bis.append(b3)

        bc_price = bis[-1].power_price < max(bis[-3].power_price, np.mean([x.power_price for x in key_bis]))
        bc_volume = bis[-1].power_volume < max(bis[-3].power_volume, np.mean([x.power_volume for x in key_bis]))
        bc_length = bis[-1].length < max(bis[-3].length, np.mean([x.length for x in key_bis]))

        if bc_price and (bc_volume or bc_length):
            res["match"] = True
        return res

    k1, k2, k3 = c.freq.value, f"D{di}B", "BUY1"
    v1, v2, v3 = "其他", "任意", "任意"

    for n in (21, 19, 17, 15, 13, 11, 9, 7, 5):
        _bis = get_sub_elements(c.bi_list, di=di, n=n)
        if len(_bis) != n:
            continue

        _res = __check_first_buy(_bis)
        if _res["match"]:
            v1, v2, v3 = _res["v1"], _res["v2"], _res["v3"]
            break

    return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1, v2=v2, v3=v3)


def cxt_first_sell_V260101(c: CZSC, **kwargs) -> OrderedDict:
    di = int(kwargs.get("di", 1))

    def __check_first_sell(bis: List[BI]):
        res = {"match": False, "v1": "一卖", "v2": f"{len(bis)}笔", "v3": "任意"}
        if len(bis) % 2 != 1 or bis[-1].direction == Direction.Down:
            return res
        if bis[0].direction != bis[-1].direction:
            return res

        max_high = max([x.high for x in bis])
        min_low = min([x.low for x in bis])
        if max_high != bis[-1].high or min_low != bis[0].low:
            return res

        key_bis = []
        for i in range(0, len(bis) - 2, 2):
            if i == 0:
                key_bis.append(bis[i])
            else:
                b1, _, b3 = bis[i - 2: i + 1]
                if b3.high > b1.high:
                    key_bis.append(b3)

        bc_price = bis[-1].power_price < max(bis[-3].power_price, np.mean([x.power_price for x in key_bis]))
        bc_volume = bis[-1].power_volume < max(bis[-3].power_volume, np.mean([x.power_volume for x in key_bis]))
        bc_length = bis[-1].length < max(bis[-3].length, np.mean([x.length for x in key_bis]))

        if bc_price and (bc_volume or bc_length):
            res["match"] = True
        return res

    k1, k2, k3 = c.freq.value, f"D{di}B", "SELL1"
    v1, v2, v3 = "其他", "任意", "任意"

    for n in (21, 19, 17, 15, 13, 11, 9, 7, 5):
        _bis = get_sub_elements(c.bi_list, di=di, n=n)
        if len(_bis) != n:
            continue

        _res = __check_first_sell(_bis)
        if _res["match"]:
            v1, v2, v3 = _res["v1"], _res["v2"], _res["v3"]
            break

    return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1, v2=v2, v3=v3)


def cxt_second_bs_V260101(c: CZSC, **kwargs) -> OrderedDict:
    di = int(kwargs.get("di", 1))
    timeperiod = int(kwargs.get("timeperiod", 21))
    ma_type = kwargs.get("ma_type", "SMA").upper()
    cache_key = update_ma_cache(c, ma_type=ma_type, timeperiod=timeperiod)
    k1, k2, k3 = f"{c.freq.value}_D{di}#{ma_type}#{timeperiod}_BS2辅助V230320".split("_")
    v1 = "其他"
    if len(c.bi_list) < di + 6:
        return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1)

    b1, b2, b3, b4, b5 = get_sub_elements(c.bi_list, di=di, n=5)
    b1_ma_b = b1.fx_b.raw_bars[-2].cache[cache_key]
    b3_ma_b = b3.fx_b.raw_bars[-2].cache[cache_key]
    b5_ma_a = b5.fx_a.raw_bars[-2].cache[cache_key]
    b5_ma_b = b5.fx_b.raw_bars[-2].cache[cache_key]

    lc1 = b1.low < b1_ma_b and b3.low < b3_ma_b
    if b5.direction == Direction.Down and lc1 and b5_ma_a < b5_ma_b:
        v1 = "二买"

    sc1 = b1.high > b1_ma_b and b3.high > b3_ma_b
    if b5.direction == Direction.Up and sc1 and b5_ma_a > b5_ma_b:
        v1 = "二卖"

    return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1)


def cxt_third_bs_V260101(c, **kwargs) -> OrderedDict:
    di = int(kwargs.get("di", 1))
    timeperiod = int(kwargs.get("timeperiod", 34))
    ma_type = kwargs.get("ma_type", "SMA").upper()
    cache_key = update_ma_cache(c, ma_type=ma_type, timeperiod=timeperiod)

    k1, k2, k3 = f"{c.freq.value}_D{di}#{ma_type}#{timeperiod}_BS3辅助V230319".split("_")
    v1 = "其他"

    if len(c.bi_list) < di + 7:
        return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1)

    b0, b1, b2, b3, b4, b5 = get_sub_elements(c.bi_list, di=di, n=6)
    bis_upto_b3 = c.bi_list[: -di - 1]
    zs_seq = get_zs_seq(bis_upto_b3)
    if not zs_seq:
        return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1)

    last_zs: ZS = zs_seq[-1]
    if last_zs.bis[-1].sdt != b3.sdt or len(last_zs.bis) < 3:
        return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1)

    zs_zg = last_zs.zg
    zs_zd = last_zs.zd

    if b3.direction == Direction.Up and b4.direction == Direction.Down and b4.low > zs_zg:
        v1 = "三买"
    if b3.direction == Direction.Down and b4.direction == Direction.Up and b4.high < zs_zd:
        v1 = "三卖"
    if v1 == "其他":
        return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1)

    ma_0 = b0.fx_b.raw_bars[-1].cache[cache_key]
    ma_2 = b2.fx_b.raw_bars[-1].cache[cache_key]
    ma_4 = b4.fx_b.raw_bars[-1].cache[cache_key]

    if ma_4 > ma_2 > ma_0:
        v2 = "均线新高"
    elif ma_4 < ma_2 < ma_0:
        v2 = "均线新低"
    elif ma_4 > ma_2 < ma_0:
        v2 = "均线底分"
    elif ma_4 < ma_2 > ma_0:
        v2 = "均线顶分"
    else:
        v2 = "均线否定"

    return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1, v2=v2)


__all__ = [
    "cxt_first_buy_V260101",
    "cxt_first_sell_V260101",
    "cxt_second_bs_V260101",
    "cxt_third_bs_V260101",
]
