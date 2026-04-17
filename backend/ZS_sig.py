import numpy as np
from deprecated import deprecated
from collections import Counter, OrderedDict
from typing import List, Any, Dict, Union, Tuple, Optional
from czsc.core import Direction
from czsc.core import BI, RawBar, ZS, Signal, CZSC
from czsc.signals.tas import update_macd_cache
from czsc.core import Operate

def create_single_signal(**kwargs) -> OrderedDict:
    """创建单个信号"""
    from rs_czsc import Signal
    
    s = OrderedDict()
    k1, k2, k3 = kwargs.get("k1", "任意"), kwargs.get("k2", "任意"), kwargs.get("k3", "任意")
    v1, v2, v3 = kwargs.get("v1", "任意"), kwargs.get("v2", "任意"), kwargs.get("v3", "任意")
    score = kwargs.get("score", 0)
    v = Signal(key=f"{k1}_{k2}_{k3}", value=f"{v1}_{v2}_{v3}_{score}")
    # v = Signal(k1=k1, k2=k2, k3=k3, v1=v1, v2=v2, v3=v3, score=kwargs.get("score", 0))
    s[v.key] = v.value
    return s


def is_symmetry_zs(bis: List[BI], th: float = 0.3) -> bool:
    """对称中枢判断：中枢中所有笔的力度序列，标准差小于均值的一定比例

    https://pic2.zhimg.com/80/v2-2f55ef49eda01972462531ebb6de4f19_1440w.jpg

    :param bis: 构成中枢的笔序列
    :param th: 标准差小于均值的比例阈值
    :return:
    """
    if len(bis) % 2 == 0:
        return False

    zs = ZS(bis=bis)
    if zs.zd > zs.zg or max([x.low for x in bis]) > min([x.high for x in bis]):
        return False

    zns = [x.power_price for x in bis]
    if np.std(zns) / np.mean(zns) <= th:
        return True
    else:
        return False


def check_cross_info(fast: Union[List, np.ndarray], slow: Union[List, np.ndarray]):
    """计算 fast 和 slow 的交叉信息

    :param fast: 快线
    :param slow: 慢线
    :return:
    """
    assert len(fast) == len(slow), "快线和慢线的长度不一样"

    if isinstance(fast, list):
        fast = np.array(fast)
    if isinstance(slow, list):
        slow = np.array(slow)

    length = len(fast)
    delta = fast - slow
    cross_info = []
    last_i = -1
    last_v = 0
    temp_fast = []
    temp_slow = []
    for i, v in enumerate(delta):
        last_i += 1
        last_v += abs(v)
        temp_fast.append(fast[i])
        temp_slow.append(slow[i])

        if i >= 2 and delta[i - 1] <= 0 < delta[i]:
            kind = "金叉"
        elif i >= 2 and delta[i - 1] >= 0 > delta[i]:
            kind = "死叉"
        else:
            continue

        cross_info.append(
            {
                "位置": i,
                "类型": kind,
                "快线": fast[i],
                "慢线": slow[i],
                "距离": last_i,
                "距今": length - i,
                "面积": round(last_v, 4),
                "价差": round(v, 4),
                "快线高点": max(temp_fast),
                "快线低点": min(temp_fast),
                "慢线高点": max(temp_slow),
                "慢线低点": min(temp_slow),
            }
        )
        last_i = 0
        last_v = 0
        temp_fast = []
        temp_slow = []

    return cross_info


def check_gap_info(bars: List[RawBar]):
    """检查 bars 中的缺口信息

    :param bars: K线序列，按时间升序
    :return:
    """
    gap_info = []
    if len(bars) < 2:
        return gap_info

    for i in range(1, len(bars)):
        bar1, bar2 = bars[i - 1], bars[i]
        right = bars[i:]

        gap = None
        if bar1.high < bar2.low:
            delta = round(bar2.low / bar1.high - 1, 4)
            cover = "已补" if min(x.low for x in right) < bar1.high else "未补"
            gap = {
                "kind": "向上缺口",
                "cover": cover,
                "sdt": bar1.dt,
                "edt": bar2.dt,
                "high": bar2.low,
                "low": bar1.high,
                "delta": delta,
            }

        if bar1.low > bar2.high:
            delta = round(bar1.low / bar2.high - 1, 4)
            cover = "已补" if max(x.high for x in right) > bar1.low else "未补"
            gap = {
                "kind": "向下缺口",
                "cover": cover,
                "sdt": bar1.dt,
                "edt": bar2.dt,
                "high": bar1.low,
                "low": bar2.high,
                "delta": delta,
            }

        if gap:
            gap_info.append(gap)

    return gap_info


def fast_slow_cross(fast, slow):
    """计算 fast 和 slow 的交叉信息

    :param fast: 快线
    :param slow: 慢线
    :return:
    """
    assert len(fast) == len(slow), "快线和慢线的长度不一样"

    if isinstance(fast, list):
        fast = np.array(fast)
    if isinstance(slow, list):
        slow = np.array(slow)

    length = len(fast)
    delta = fast - slow
    cross_info = []
    last_i = -1
    last_v = 0
    temp_fast = []
    temp_slow = []
    for i, v in enumerate(delta):
        last_i += 1
        last_v += abs(v)
        temp_fast.append(fast[i])
        temp_slow.append(slow[i])

        if i >= 2 and delta[i - 1] <= 0 < delta[i]:
            kind = "金叉"
        elif i >= 2 and delta[i - 1] >= 0 > delta[i]:
            kind = "死叉"
        else:
            continue

        cross_info.append(
            {
                "位置": i,
                "类型": kind,
                "快线": fast[i],
                "慢线": slow[i],
                "距离": last_i,
                "距今": length - i,
                "面积": round(last_v, 4),
                "价差": round(v, 4),
                "快线高点": max(temp_fast),
                "快线低点": min(temp_fast),
                "慢线高点": max(temp_slow),
                "慢线低点": min(temp_slow),
            }
        )
        last_i = 0
        last_v = 0
        temp_fast = []
        temp_slow = []

    return cross_info


def same_dir_counts(seq: Union[List, np.ndarray]):
    """计算 seq 中与最后一个数字同向的数字数量

    :param seq: 数字序列
    :return:

    example
    ----------
    >>>print(same_dir_counts([-1, -1, -2, -3, 0, 1, 2, 3, -1, -2, 1, 1, 2, 3]))
    >>>print(same_dir_counts([-1, -1, -2, -3, 0, 1, 2, 3]))
    """
    s = seq[-1]
    c = 0
    for num in seq[::-1]:
        if (num > 0 and s > 0) or (num < 0 and s < 0):
            c += 1
        else:
            break
    return c


def count_last_same(seq: Union[List, np.ndarray, Tuple]):
    """统计与seq列表最后一个元素相似的连续元素数量

    :param seq: 数字序列
    :return:
    """
    s = seq[-1]
    c = 0
    for _s in seq[::-1]:
        if _s == s:
            c += 1
        else:
            break
    return c


def get_sub_elements(elements: List[Any], di: int = 1, n: int = 10) -> List[Any]:
    """获取截止到倒数第 di 个元素的前 n 个元素

    :param elements: 全部元素列表
    :param di: 指定结束元素为倒数第 di 个
    :param n: 指定需要的元素个数
    :return: 部分元素列表

    >>>x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>>y1 = get_sub_elements(x, di=1, n=3)
    >>>y2 = get_sub_elements(x, di=2, n=3)
    """
    assert di >= 1
    if di == 1:
        se = elements[-n:]
    else:
        se = elements[-n - di + 1 : -di + 1]
    return se


def is_bis_down(bis: List[BI]):
    """判断 bis 中的连续笔是否是向下的"""
    if not bis or len(bis) < 3 or len(bis) % 2 == 0:
        return False

    assert bis[1].fx_b.dt > bis[0].fx_b.dt, "时间由远到近"

    if (
        bis[-1].direction == Direction.Down
        and bis[0].high == max([x.high for x in bis])
        and bis[-1].low == min([x.low for x in bis])
    ):
        return True
    else:
        return False


def is_bis_up(bis: List[BI]):
    """判断 bis 中的连续笔是否是向上的"""
    if not bis or len(bis) < 3 and len(bis) % 2 == 0:
        return False

    assert bis[1].fx_b.dt > bis[0].fx_b.dt, "时间由远到近"

    if (
        bis[-1].direction == Direction.Up
        and bis[-1].high == max([x.high for x in bis])
        and bis[0].low == min([x.low for x in bis])
    ):
        return True
    else:
        return False


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

        new_bis = list(zs.bis) + [bi]  # merge bis list
        zs_list[-1] = ZS(bis=new_bis)
        i += 1

    return zs_list


def check_down_trend(zs_list: List[ZS]) -> bool:
    """
    检查给定的中枢列表的最后两个中枢是否构成下跌趋势

    :param zs_list: 中枢列表
    :return: 如果最后两个中枢构成下跌趋势返回True，否则返回False
    """
    if len(zs_list) < 2:
        return False

    # 获取最后两个中枢
    zs_last = zs_list[-1]
    zs_prev = zs_list[-2]

    # 如果zs_last的上沿<zs_prev的下沿, 确认是下降趋势
    if zs_last.zg < zs_prev.zd:
        return True

    return False


def check_up_trend(zs_list: List[ZS]) -> bool:
    """
    检查给定的中枢列表的最后两个中枢是否构成上涨趋势

    :param zs_list: 中枢列表
    :return: 如果最后两个中枢构成上涨趋势返回True，否则返回False
    """
    if len(zs_list) < 2:
        return False

    # 获取最后两个中枢
    zs_last = zs_list[-1]
    zs_prev = zs_list[-2]

    # 如果zs_last的下沿 > zs_prev的上沿, 确认是上升趋势
    if zs_last.zd > zs_prev.zg:
        return True

    return False


def get_relevant_zss(current_bi: BI, zs_list: List[ZS]) -> List[ZS]:
    """
    获取在当前笔开始之前已“成立”的中枢

    注：为避免未来函数，不用中枢的结束时间去筛选；而是以“第二笔开始”作为中枢成立的最早时刻。

    :param current_bi: 当前笔
    :param zs_list: 中枢列表
    :return: 第二笔开始时间 <= 当前笔开始时间 的中枢列表
    """
    valid_zs_list = []
    for zs in zs_list:
        # 如果一个中枢的第二笔开始时间早于或等于当前笔的开始时间，就把这个中枢添加到valid_zs_list
        if not getattr(zs, "bis", None) or len(zs.bis) < 3:
            continue

        second_bi = zs.bis[1]
        if second_bi.sdt <= current_bi.sdt:
            valid_zs_list.append(zs)
    return valid_zs_list


def get_entry_BI(zs: ZS, bis: List[BI]) -> Optional[BI]:
    """
    获取中枢的进入段（中枢 lines 列表中的第一条笔之前的笔）

    :param zs: 中枢对象
    :param bis: 完整的笔列表
    :return: 进入段笔，如果不存在则返回None
    """
    # print("用于debug, 打印中枢信息", zs.sdt, zs.edt, zs.bis)
    if not zs.bis or len(zs.bis) == 0:
        return None

    # 获取中枢的第一笔
    first_bi_in_zs = zs.bis[0]

    # 在笔列表中找到中枢第一笔的位置
    for i, bi in enumerate(bis):
        if bi.sdt == first_bi_in_zs.sdt and bi.edt == first_bi_in_zs.edt:
            # 进入段是中枢第一笔之前的那一笔
            if i > 0:
                return bis[i - 1]
            break

    return None


def get_next_zs(current_zs: ZS, zss_list: List[ZS]) -> Optional[ZS]:
    """
    获取给定中枢在列表中的下一个中枢
    :param current_zs: 当前中枢对象
    :param zss_list: 中枢列表 (通常由 cd.get_bi_zss() 或 cd.get_xd_zss() 获取)
    :return: 下一个中枢对象 或 None
    """
    if not zss_list or current_zs is None:
        return None

    try:
        # 1. 找到当前中枢在列表中的位置下标
        for i, zs in enumerate(zss_list):
            if zs.sdt == current_zs.sdt and zs.edt == current_zs.edt:
                # 2. 检查是否还有下一个元素
                if i + 1 < len(zss_list):
                    return zss_list[i + 1]
                else:
                    return None
        return None
    except (AttributeError, IndexError):
        return None


def check_beichi(
        c_sdt,
        c_edt,
        b_sdt,
        b_edt,
        direction: Direction,
        czsc_obj: CZSC,
        th: int = 100
) -> bool:
    """
    检查离开段 c 是否相对于连接段 b 发生背驰（力度衰减）

    背景：
    - 在 A + b + B + c 的趋势结构中，b / c 可能包含不止 1 笔（或线段）
    - 因此背驰判定不应只依赖单一 BI 对象，而应允许用时间区间去聚合力度

    :param c_sdt: B 中枢离开段 c 的开始时间
    :param c_edt: B 中枢离开段 c 的结束时间
    :param b_sdt: A 与 B 中枢之间连接段 b 的开始时间
    :param b_edt: A 与 B 中枢之间连接段 b 的结束时间
    :param direction: 离开段 c 的方向；第一类买点为 Direction.Down，第一类卖点为 Direction.Up
    :param czsc_obj: 缠论计算数据对象（用于获取带 MACD cache 的 raw bars）
    :param th: 背驰阈值，c 段面积 <= b 段面积 * th / 100 时认为背驰
    :return: 如果发生背驰返回 True，否则返回 False
    """
    if not (c_sdt and c_edt and b_sdt and b_edt and czsc_obj):
        return False

    # 获取MACD缓存key
    cache_key = update_macd_cache(czsc_obj, fastperiod=26, slowperiod=12, signalperiod=9)

    def _bars_in_range(sdt, edt):
        bars = [x for x in czsc_obj.bars_raw if sdt <= x.dt <= edt]
        # 与 BI.raw_bars[1:-1] 类似，尽量剔除区间端点，减少端点重叠/毛刺影响
        if len(bars) > 2:
            return bars[1:-1]
        return bars

    def _macd_area(sdt, edt):
        try:
            macd = [x.cache[cache_key]["macd"] for x in _bars_in_range(sdt, edt)]
        except (KeyError, AttributeError, TypeError):
            return 0.0

        if direction == Direction.Down:
            # 下跌段取负柱面积（绝对值）
            return float(abs(sum([x for x in macd if x < 0])))
        else:
            # 上涨段取正柱面积
            return float(sum([x for x in macd if x > 0]))

    b_area = _macd_area(b_sdt, b_edt)
    c_area = _macd_area(c_sdt, c_edt)

    # 判断背驰：c 段面积 <= b 段面积 * th / 100
    if b_area > 0 and c_area <= b_area * th / 100:
        return True

    return False

def find_B1(bi_list: List[BI], zs_list: List[ZS], czsc_obj: CZSC) -> List[Dict]:
    """
    遍历检查第一类买点
    :param bi_list: 已完成的笔列表（按时间正序）
    :param zs_list: 已完成的中枢列表（按时间正序）
    :param czsc_obj: 缠论数据计算对象（用于计算MACD力度等）
    :return: 买点列表
    """
    buy_points = []

    # 遍历每一笔
    for i, current_bi in enumerate(bi_list):
        # 1. 筛选条件：必须是向下笔（Down Bi），因为向下笔结束通过底分型，才可能是买点
        if current_bi.direction != Direction.Down:
            continue

        # 2. 获取当前笔之前的相关中枢
        valid_zs_list = get_relevant_zss(current_bi, zs_list)

        # 至少需要两个中枢才能形成趋势
        if len(valid_zs_list) < 2:
            continue

        # 3. 核心规则 A：必须形成下跌趋势（至少包含两个同级别向下中枢，且互不重叠）
        if not check_down_trend(valid_zs_list):
            continue

        last_zs = valid_zs_list[-1]

        # 4. 核心规则 B：current_bi必须创新低（当前底分型价格 < 最后一个中枢的最低点 dd）
        if current_bi.low > last_zs.dd:
            continue

        # 6. 核心规则 C：力度背驰（A 与 B 的连接段 b vs B 的离开段 c）
        prev_zs = valid_zs_list[-2]
        try:
            # b 段：从 A 的最后一笔开始，到 B 的第一笔开始（允许 b 含多笔）
            b_sdt = prev_zs.bis[-1].sdt
            b_edt = last_zs.bis[0].sdt
        except (AttributeError, IndexError):
            continue

        # c 段：从 B 中枢内，距离 current_bi 最近且同向的笔开始，到 current_bi 结束（允许 c 含多笔）
        c_candidates = [
            bi for bi in getattr(last_zs, "bis", []) or []
            if bi.sdt <= current_bi.sdt and bi.direction == current_bi.direction
        ]
        if not c_candidates:
            continue

        c_sdt = max(c_candidates, key=lambda x: x.sdt).sdt
        c_edt = current_bi.edt

        if check_beichi(
                c_sdt=c_sdt,
                c_edt=c_edt,
                b_sdt=b_sdt,
                b_edt=b_edt,
                direction=current_bi.direction,
                czsc_obj=czsc_obj,
        ):
            # 记录结果：(底分型时间, 价格)
            buy_points.append({
                "dt": current_bi.edt,
                "price": current_bi.low,
                "op": Operate.LO,
                "op_desc": f"B1",
                "bs_type": "B1"
            })

    return buy_points


def find_S1(bi_list: List[BI], zs_list: List[ZS], czsc_obj: CZSC) -> List[Dict]:
    """
    遍历检查第一类卖点
    :param bi_list: 已完成的笔列表（按时间正序）
    :param zs_list: 已完成的中枢列表（按时间正序）
    :param czsc_obj: 缠论数据计算对象（用于计算MACD力度等）
    :return: 卖点列表
    """
    sell_points = []

    # 遍历每一笔
    for i, current_bi in enumerate(bi_list):
        # 1. 筛选条件：必须是向上笔（Up Bi），因为向上笔结束通过顶分型，才可能是卖点
        if current_bi.direction != Direction.Up:
            continue

        # 2. 获取当前笔之前的相关中枢
        valid_zs_list = get_relevant_zss(current_bi, zs_list)

        # 至少需要两个中枢才能形成趋势
        if len(valid_zs_list) < 2:
            continue

        # 3. 核心规则 A：必须形成上涨趋势（至少包含两个同级别向上中枢，且互不重叠）
        if not check_up_trend(valid_zs_list):
            continue

        last_zs = valid_zs_list[-1]

        # 4. 核心规则 B：current_bi必须创新高（当前顶分型价格 > 最后一个中枢的最高点 gg）
        if current_bi.high < last_zs.gg:
            continue

        # 5. 核心规则 C：力度背驰（A 与 B 的连接段 b vs B 的离开段 c）
        prev_zs = valid_zs_list[-2]
        try:
            # b 段：从 A 的最后一笔开始，到 B 的第一笔开始（允许 b 含多笔）
            b_sdt = prev_zs.bis[-1].sdt
            b_edt = last_zs.bis[0].sdt
        except (AttributeError, IndexError):
            continue

        # c 段：从 B 中枢内，距离 current_bi 最近且同向的笔开始，到 current_bi 结束（允许 c 含多笔）
        c_candidates = [
            bi for bi in getattr(last_zs, "bis", []) or []
            if bi.sdt <= current_bi.sdt and bi.direction == current_bi.direction
        ]
        if not c_candidates:
            continue

        c_sdt = max(c_candidates, key=lambda x: x.sdt).sdt
        c_edt = current_bi.edt

        if check_beichi(
                c_sdt=c_sdt,
                c_edt=c_edt,
                b_sdt=b_sdt,
                b_edt=b_edt,
                direction=current_bi.direction,
                czsc_obj=czsc_obj,
        ):
            # 记录结果：(顶分型时间, 价格)
            sell_points.append({
                "dt": current_bi.edt,
                "price": current_bi.high,
                "op": Operate.LE,
                "op_desc": "S1",
                "bs_type": "S1"
            })

    return sell_points


def find_B2(bi_list: List[BI], b1_list: List[Dict]) -> List[Dict]:
    """
    遍历检查第二类买点
    第一类买点之后的第一次向下回调笔，如果不跌破第一类买点的最低点，该回调笔的终点即为第二类买点

    :param bi_list: 已完成的笔列表（按时间正序）
    :param b1_list: 第一类买点列表
    :return: 第二类买点列表
    """
    buy_points = []

    for b1 in b1_list:
        b1_dt = b1["dt"]
        b1_price = b1["price"]

        # 找到B1对应的笔在bi_list中的位置
        b1_bi_index = None
        for i, bi in enumerate(bi_list):
            if bi.edt == b1_dt:
                b1_bi_index = i
                break

        if b1_bi_index is None:
            continue

        # 从B1之后寻找第一次向下回调笔
        for j in range(b1_bi_index + 1, len(bi_list)):
            current_bi = bi_list[j]

            # 必须是向下笔
            if current_bi.direction != Direction.Down:
                continue

            # 检查是否跌破B1的最低点
            if current_bi.low < b1_price:
                # 跌破了B1最低点，不构成B2
                break

            # 不跌破B1最低点，该回调笔的终点为第二类买点
            buy_points.append({
                "dt": current_bi.edt,
                "price": current_bi.low,
                "op": Operate.LO,
                "op_desc": f"B2",
                "bs_type": "B2"
            })
            break  # 只取第一次向下回调笔

    return buy_points


def find_S2(bi_list: List[BI], s1_list: List[Dict]) -> List[Dict]:
    """
    遍历检查第二类卖点
    第一类卖点之后的第一次向上回调笔，如果不突破第一类卖点的最高点，该回调笔的终点即为第二类卖点

    :param bi_list: 已完成的笔列表（按时间正序）
    :param s1_list: 第一类卖点列表
    :return: 第二类卖点列表
    """
    sell_points = []

    for s1 in s1_list:
        s1_dt = s1["dt"]
        s1_price = s1["price"]

        # 找到S1对应的笔在bi_list中的位置
        s1_bi_index = None
        for i, bi in enumerate(bi_list):
            if bi.edt == s1_dt:
                s1_bi_index = i
                break

        if s1_bi_index is None:
            continue

        # 从S1之后寻找第一次向上回调笔
        for j in range(s1_bi_index + 1, len(bi_list)):
            current_bi = bi_list[j]

            # 必须是向上笔
            if current_bi.direction != Direction.Up:
                continue

            # 检查是否突破S1的最高点
            if current_bi.high > s1_price:
                # 突破了S1最高点，不构成S2
                break

            # 不突破S1最高点，该回调笔的终点为第二类卖点
            sell_points.append({
                "dt": current_bi.edt,
                "price": current_bi.high,
                "op": Operate.LE,
                "op_desc": "S2",
                "bs_type": "S2"
            })
            break  # 只取第一次向上回调笔

    return sell_points


def find_B3(bi_list: List[BI], zs_list: List[ZS]) -> List[Dict]:
    """
    遍历检查第三类买点
    第三类买点：中枢形成后，向上突破中枢的笔之后，第一次向下回调笔不跌破中枢上沿(zg)，
    该回调笔的终点即为第三类买点

    :param bi_list: 已完成的笔列表（按时间正序）
    :param zs_list: 已完成的中枢列表（按时间正序）
    :param czsc_obj: 缠论数据计算对象（用于计算MACD力度等）
    :return: 买点列表
    """
    buy_points = []

    # 遍历每一笔
    for i, current_bi in enumerate(bi_list):
        # 1. 筛选条件：必须是向下笔（Down Bi），因为向下笔结束通过底分型，才可能是买点
        if current_bi.direction != Direction.Down:
            continue

        # 2. 获取当前笔之前的相关中枢
        valid_zs_list = get_relevant_zss(current_bi, zs_list)

        if len(valid_zs_list) < 1:
            continue

        last_zs = valid_zs_list[-1]

        # 3. current_bi的前一笔(向上)是last_zs的最后一笔
        if i < 1:
            continue

        prev_bi = bi_list[i - 1]

        # 前一笔必须是向上笔
        if prev_bi.direction != Direction.Up:
            continue

        # 检查前一笔是否是中枢的最后一笔
        if not last_zs.bis or len(last_zs.bis) == 0:
            continue

        last_bi_in_zs = last_zs.bis[-1]
        if prev_bi.sdt != last_bi_in_zs.sdt or prev_bi.edt != last_bi_in_zs.edt:
            continue

        # 4. current_bi的终点大于last_zs的上沿，current_bi的终点为第三类买点
        if current_bi.low > last_zs.zg:
            buy_points.append({
                "dt": current_bi.edt,
                "price": current_bi.low,
                "op": Operate.LO,
                "op_desc": "B3",
                "bs_type": "B3"
            })

    return buy_points


def find_S3(bi_list: List[BI], zs_list: List[ZS]) -> List[Dict]:
    """
    遍历检查第三类卖点
    第三类卖点：中枢形成后，向下突破中枢的笔之后，第一次向上回调笔不突破中枢下沿(zd)，
    该回调笔的终点即为第三类卖点

    :param bi_list: 已完成的笔列表（按时间正序）
    :param zs_list: 已完成的中枢列表（按时间正序）
    :return: 卖点列表
    """
    sell_points = []

    # 遍历每一笔
    for i, current_bi in enumerate(bi_list):
        # 1. 筛选条件：必须是向上笔（Up Bi），因为向上笔结束通过顶分型，才可能是卖点
        if current_bi.direction != Direction.Up:
            continue

        # 2. 获取当前笔之前的相关中枢
        valid_zs_list = get_relevant_zss(current_bi, zs_list)

        if len(valid_zs_list) < 1:
            continue

        last_zs = valid_zs_list[-1]

        # 3. current_bi的前一笔(向下)是last_zs的最后一笔
        if i < 1:
            continue

        prev_bi = bi_list[i - 1]

        # 前一笔必须是向下笔
        if prev_bi.direction != Direction.Down:
            continue

        # 检查前一笔是否是中枢的最后一笔
        if not last_zs.bis or len(last_zs.bis) == 0:
            continue

        last_bi_in_zs = last_zs.bis[-1]
        if prev_bi.sdt != last_bi_in_zs.sdt or prev_bi.edt != last_bi_in_zs.edt:
            continue

        # 4. current_bi的终点小于last_zs的下沿，current_bi的终点为第三类卖点
        if current_bi.high < last_zs.zd:
            sell_points.append({
                "dt": current_bi.edt,
                "price": current_bi.high,
                "op": Operate.LE,
                "op_desc": "S3",
                "bs_type": "S3"
            })

    return sell_points


def cross_zero_axis(n1: Union[List, np.ndarray], n2: Union[List, np.ndarray]) -> int:
    """判断两个数列的零轴交叉点

    :param n1: 数列1
    :param n2: 数列2
    :return: 交叉点所在的索引位置
    """
    assert len(n1) == len(n2), "输入两个数列长度不等"
    axis_0 = np.zeros(len(n1))

    n1 = np.flip(n1)
    n2 = np.flip(n2)

    x1 = np.where(n1[0] * n1 < axis_0, True, False)
    x2 = np.where(n2[0] * n2 < axis_0, True, False)

    num1 = np.argmax(x1[:-1] != x1[1:]) + 2 if np.any(x1) else 0
    num2 = np.argmax(x2[:-1] != x2[1:]) + 2 if np.any(x2) else 0
    return int(max(num1, num2))


def cal_cross_num(cross: List, distance: int = 1) -> tuple:
    """使用 distance 过滤掉fast_slow_cross函数返回值cross列表中
    不符合要求的交叉点，返回处理后的金叉和死叉数值

    :param cross: fast_slow_cross函数返回值
    :param distance: 金叉和死叉之间的最小距离
    :return: jc金叉值 ，SC死叉值
    """
    if len(cross) == 0:
        return 0, 0
    elif len(cross) == 1:
        cross_ = cross
    elif len(cross) == 2:
        if cross[-1]["距离"] < distance:
            cross_ = []
        else:
            cross_ = cross
    else:
        if cross[-1]["距离"] < distance:
            last_cross = cross[-1]
            del cross[-2]
            re_cross = [i for i in cross if i["距离"] >= distance]
            re_cross.append(last_cross)
        else:
            re_cross = [i for i in cross if i["距离"] >= distance]
        cross_ = []
        for i in range(0, len(re_cross)):
            if len(cross_) >= 1 and re_cross[i]["类型"] == re_cross[i - 1]["类型"]:
                # 不将上一个元素加入cross_
                del cross_[-1]
                cross_.append(re_cross[i])
            else:
                cross_.append(re_cross[i])

    jc = len([x for x in cross_ if x["类型"] == "金叉"])
    sc = len([x for x in cross_ if x["类型"] == "死叉"])

    return jc, sc


def down_cross_count(x1: Union[List, np.ndarray], x2: Union[List, np.ndarray]) -> int:
    """输入两个序列，计算 x1 下穿 x2 的次数

    :param x1: list
    :param x2: list
    :return: int
    """
    x = np.array(x1) < np.array(x2)
    num = 0
    for i in range(len(x) - 1):
        b1, b2 = x[i], x[i + 1]
        if b2 and b1 != b2:
            num += 1
    return num
