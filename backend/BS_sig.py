import numpy as np
import pandas as pd
from typing import List
from czsc import CZSC
from czsc.traders.base import CzscSignals
from czsc.enum import Direction
from czsc.objects import FX, BI, ZS, Mark
from czsc.utils import get_sub_elements, create_single_signal
from ZS_sig import get_zs_seq
from czsc.signals.tas import update_ma_cache, update_macd_cache
from collections import OrderedDict
from deprecated import deprecated
from sklearn.linear_model import LinearRegression


def cxt_first_buy_V260101(c: CZSC, **kwargs) -> OrderedDict:
    """一买信号

    参数模板："{freq}_D{di}B_BUY1"

    **信号列表：**

    - Signal('15分钟_D1B_BUY1_一买_5笔_任意_0')
    - Signal('15分钟_D1B_BUY1_一买_11笔_任意_0')
    - Signal('15分钟_D1B_BUY1_一买_7笔_任意_0')
    - Signal('15分钟_D1B_BUY1_一买_21笔_任意_0')
    - Signal('15分钟_D1B_BUY1_一买_17笔_任意_0')
    - Signal('15分钟_D1B_BUY1_一买_19笔_任意_0')
    - Signal('15分钟_D1B_BUY1_一买_9笔_任意_0')
    - Signal('15分钟_D1B_BUY1_一买_15笔_任意_0')
    - Signal('15分钟_D1B_BUY1_一买_13笔_任意_0')

    :param c: CZSC 对象
    :param kwargs:
        - di: 倒数第di个笔
    :return: 信号字典
    """
    di = int(kwargs.get("di", 1))

    def __check_first_buy(bis: List[BI]):
        """检查 bis 是否是一买的结束

        :param bis: 笔序列，按时间升序
        """
        res = {"match": False, "v1": "一买", "v2": f"{len(bis)}笔", "v3": "任意"}
        if len(bis) % 2 != 1 or bis[-1].direction == Direction.Up or bis[0].direction != bis[-1].direction:
            return res

        if max([x.high for x in bis]) != bis[0].high or min([x.low for x in bis]) != bis[-1].low:
            return res

        # 检查背驰：获取向下突破的笔列表
        key_bis = []
        for i in range(0, len(bis) - 2, 2):
            if i == 0:
                key_bis.append(bis[i])
            else:
                b1, _, b3 = bis[i - 2 : i + 1]
                if b3.low < b1.low:
                    key_bis.append(b3)

        # 检查背驰：最后一笔的 power_price，power_volume，length 同时满足背驰条件才算背驰
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
    """一卖信号

    参数模板："{freq}_D{di}B_SELL1"

    **信号列表：**

    - Signal('15分钟_D1B_SELL1_一卖_17笔_任意_0')
    - Signal('15分钟_D1B_SELL1_一卖_15笔_任意_0')
    - Signal('15分钟_D1B_SELL1_一卖_5笔_任意_0')
    - Signal('15分钟_D1B_SELL1_一卖_7笔_任意_0')
    - Signal('15分钟_D1B_SELL1_一卖_9笔_任意_0')
    - Signal('15分钟_D1B_SELL1_一卖_19笔_任意_0')
    - Signal('15分钟_D1B_SELL1_一卖_21笔_任意_0')
    - Signal('15分钟_D1B_SELL1_一卖_13笔_任意_0')
    - Signal('15分钟_D1B_SELL1_一卖_11笔_任意_0')

    :param c: CZSC 对象
    :param di: CZSC 对象
    :return: 信号字典
    """
    di = int(kwargs.get("di", 1))

    def __check_first_sell(bis: List[BI]):
        """检查 bis 是否是一卖的结束

        :param bis: 笔序列，按时间升序
        """
        res = {"match": False, "v1": "一卖", "v2": f"{len(bis)}笔", "v3": "任意"}
        if len(bis) % 2 != 1 or bis[-1].direction == Direction.Down:
            return res

        if bis[0].direction != bis[-1].direction:
            return res

        max_high = max([x.high for x in bis])
        min_low = min([x.low for x in bis])

        if max_high != bis[-1].high or min_low != bis[0].low:
            return res

        # 检查背驰：获取向上突破的笔列表
        key_bis = []
        for i in range(0, len(bis) - 2, 2):
            if i == 0:
                key_bis.append(bis[i])
            else:
                b1, _, b3 = bis[i - 2 : i + 1]
                if b3.high > b1.high:
                    key_bis.append(b3)

        # 检查背驰：最后一笔的 power_price，power_volume，length 同时满足背驰条件才算背驰
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
    """均线辅助识别第二类买卖点

    参数模板："{freq}_D{di}#{ma_type}#{timeperiod}_BS2辅助V260101"

    **信号逻辑：**

    1. 二买：1）123笔序列向下，其中 1,3 笔的低点都在均线下方；2）5的fx_a的均线值小于fx_b均线值
    2. 二卖：1）123笔序列向上，其中 1,3 笔的高点都在均线上方；2）5的fx_a的均线值大于fx_b均线值

    **信号列表：**

    - Signal('15分钟_D1#SMA#21_BS2辅助V230320_二买_任意_任意_0')
    - Signal('15分钟_D1#SMA#21_BS2辅助V230320_二卖_任意_任意_0')

    :param c: CZSC对象
    :param di: 从最后一个笔的第几个开始识别
    :param kwargs: ma_type: 均线类型，timeperiod: 均线周期
    :return: 信号识别结果
    """
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
    """均线辅助识别第三类买卖点，结合严格中枢定义（稳定版）

    参数模板："{freq}_D{di}#{ma_type}#{timeperiod}_BS3辅助V260101"

    **信号逻辑：**
    1. 考虑到最后一笔 b5 不稳定，逻辑前移一笔。
    2. 获取截止到 b3 的中枢序列。
    3. 验证 b3 是中枢的离开笔。
    4. 验证 b4 是回拉笔且不回中枢（b4 已完成，信号稳定）。
    5. 叠加均线形态辅助判断。

    :param c: CZSC对象
    :param kwargs: di, ma_type, timeperiod
    :return: 信号识别结果
    """
    di = int(kwargs.get("di", 1))
    timeperiod = int(kwargs.get("timeperiod", 34))
    ma_type = kwargs.get("ma_type", "SMA").upper()
    cache_key = update_ma_cache(c, ma_type=ma_type, timeperiod=timeperiod)

    k1, k2, k3 = f"{c.freq.value}_D{di}#{ma_type}#{timeperiod}_BS3辅助V230319".split("_")
    v1 = "其他"

    # 需要至少 7 笔数据：b0, b1, b2, b3, b4, b5 以及之前的历史
    if len(c.bi_list) < di + 7:
        return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1)

    # 获取当前考察的最后6笔：b0, b1, b2, b3, b4, b5
    # b5 是当前未完成笔(不稳定)，b4 是回拉笔(稳定)，b3 是离开笔
    b0, b1, b2, b3, b4, b5 = get_sub_elements(c.bi_list, di=di, n=6)

    # 关键步骤：计算截止到 b3 的中枢序列
    # 我们需要排除 b4 和 b5，看 b3 结束时的中枢状态
    # 切片范围：从头开始，直到 b3 结束
    # 如果 di=1, b5 index=-1, b4 index=-2, b3 index=-3
    # 切片应该是 [:-2] 即 [: -di - 1]
    bis_upto_b3 = c.bi_list[: -di - 1]

    zs_seq = get_zs_seq(bis_upto_b3)

    if not zs_seq:
        return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1)

    last_zs: ZS = zs_seq[-1]

    # 校验1：b3 必须是该中枢序列的最后一笔 (确保 b3 是离开笔)
    if last_zs.bis[-1].sdt != b3.sdt:
        return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1)

    # 校验2：中枢笔数至少为3笔 (标准中枢)
    if len(last_zs.bis) < 3:
        return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1)

    zs_zg = last_zs.zg
    zs_zd = last_zs.zd

    # 判断三买：b3 向上离开(Up)，b4 向下回拉(Down)，b4 低点 > ZG
    # 隐含条件：b3 是 Up，则 b4 必然是 Down，这里显式判断增加健壮性
    if b3.direction == Direction.Up and b4.direction == Direction.Down:
        if b4.low > zs_zg:
            v1 = "三买"

    # 判断三卖：b3 向下离开(Down)，b4 向上回拉(Up)，b4 高点 < ZD
    if b3.direction == Direction.Down and b4.direction == Direction.Up:
        if b4.high < zs_zd:
            v1 = "三卖"

    if v1 == "其他":
        return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1)

    # 均线形态辅助判断
    # 信号笔是 b4，对比同向的 b2 和 b0
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


