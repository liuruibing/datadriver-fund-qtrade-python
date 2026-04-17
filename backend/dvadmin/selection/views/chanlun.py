"""chanlun.py

独立的缠论 history 接口：
- 不改动既有 TradingViewViewSet（保留原 mock 逻辑）
- 直接迁移 analysis_api.py 的完整逻辑（含 ZS_sig 的核心算法）
"""

from __future__ import annotations

import math
import os
import sys
import time
from pathlib import Path
from typing import Any

# 强制使用本地开发版 czsc
# 强制使用本地开发版 czsc (backend/czsc)
backend_dir = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(backend_dir / "czsc"))

os.environ["CZSC_USE_PYTHON"] = "1"
import czsc
import pandas as pd
from czsc import Freq, Direction
from ..models import AIAnalysisHistory
from dvadmin.selection.utils.json_utils import _json_safe, _dt_to_str
from sqlalchemy import create_engine, text

from dvadmin.selection.services.ai_service import AIService
from rest_framework import viewsets
from rest_framework.decorators import action, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from tushare2postgresql import convert_stock_code
from ZS_sig_ai import get_zs_seq, find_B1, find_B2, find_B3, find_S1, find_S2, find_S3, find_LB2, find_LS2





def _dt_to_ts(dt, is_daily: bool = False, freq: Freq | None = None) -> int | None:
    """将 datetime / 可解析字符串 转为秒级时间戳（int）。
    
    Args:
        dt: 日期时间对象或字符串
        is_daily: 是否为日线/周线/月线数据。日线数据不做时区转换，直接当作 UTC 0:00 处理，
                  避免前端显示时差一天的问题。
        freq: 频率枚举。如果是周线 (Freq.W)，会将周五的日期转换为周一，以匹配 TradingView 的周线约定。
    """
    if dt is None:
        return None
    if isinstance(dt, (int, float)):
        return int(dt)
    try:
        ts = pd.Timestamp(dt)
        if ts is pd.NaT:
            return None
        
        # 周线特殊处理：数据库存的是周五，TradingView 显示周一为周线起点
        # 将周五日期转换为同一周的周一
        if freq == Freq.W:
            # ts.dayofweek: 0=周一, 1=周二, ..., 4=周五, 5=周六, 6=周日
            # 如果是周五(4)，往前推4天到周一；如果是其他日期，也推到该周周一
            days_since_monday = ts.dayofweek
            ts = ts - pd.Timedelta(days=days_since_monday)
        elif freq == Freq.M:
            # 月线：对齐到月初
            ts = ts.replace(day=1)
        elif freq == Freq.S:
            # 季线：对齐到季初（1, 4, 7, 10月）
            month = ts.month
            new_month = ((month - 1) // 3) * 3 + 1
            ts = ts.replace(month=new_month, day=1)
        elif freq == Freq.Y:
            # 年线：对齐到年初
            ts = ts.replace(month=1, day=1)
        
        if is_daily:
            # 日线/周线/月线：直接取日期的 UTC 0:00 时间戳，不做时区转换
            # 这样前端按 UTC 解析时显示正确的日期
            return int(pd.Timestamp(ts.date()).timestamp())
        else:
            # 分钟线：假设为北京时间，转换为 UTC 时间戳
            if ts.tz is None:
                ts = ts.tz_localize("Asia/Shanghai")
            return int(ts.timestamp())
    except Exception:
        return None


def _normalize_ts_code(symbol: str) -> str:
    """将入参标准化为 ts_code（如 601888.SH / 000001.SZ）。

    约定：
    - 如果已经是 ts_code（包含 . 且以 .SH/.SZ 结尾），直接返回（会做 upper + 去空格）
    - 否则按 6 位股票代码走 convert_stock_code
    """
    s = str(symbol).strip().upper()
    if "." in s and (s.endswith(".SH") or s.endswith(".SZ")):
        return s
    return convert_stock_code(s)


def _json_safe(v: Any):
    """把 numpy 标量 / datetime / NaN/Inf 等转换成可 JSON 序列化的值（递归）。"""
    try:
        import numpy as np
    except Exception:
        np = None

    if v is None:
        return None

    # datetime/date
    if hasattr(v, "strftime") and not isinstance(v, (str, bytes)):
        return _dt_to_str(v)

    # numpy scalar -> python scalar
    if np is not None and isinstance(v, (getattr(np, "floating", ()), getattr(np, "integer", ()))):
        v = v.item()

    # float NaN/Inf -> None
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None

    if isinstance(v, dict):
        return {str(k): _json_safe(val) for k, val in v.items()}

    if isinstance(v, (list, tuple)):
        return [_json_safe(x) for x in v]

    return v


def _get_ts_freq(czsc_freq: Freq | str) -> str:
    """将 czsc 的频率映射到数据库 period 字段。"""
    freq_str = czsc_freq.value if isinstance(czsc_freq, Freq) else str(czsc_freq)
    freq_str = str(freq_str).strip()

    mapping = {
        "日线": "daily",
        "周线": "weekly",
        "月线": "monthly",
        "季线": "quarterly",
        "年线": "yearly",
        "5分钟": "5min",
        "30分钟": "30min",
    }
    if freq_str in mapping:
        return mapping[freq_str]
    if freq_str.endswith("分钟"):
        return freq_str.replace("分钟", "min")
    return freq_str


def _parse_bool(v: Any) -> bool:
    if v is None:
        return False
    s = str(v).strip().lower()
    return s in {"1", "true", "yes", "y", "on"}


def _resolution_to_freq(resolution: str) -> Freq | None:
    r = str(resolution).strip().upper()
    mapping = {
        "1": Freq.F1,
        "1M": Freq.F1,
        "5": Freq.F5,
        "5M": Freq.F5,
        "15": Freq.F15,
        "15M": Freq.F15,
        "30": Freq.F30,
        "30M": Freq.F30,
        "60": Freq.F60,
        "60M": Freq.F60,
        "1H": Freq.F60,
        "1D": Freq.D,
        "D": Freq.D,
        "1W": Freq.W,
        "W": Freq.W,
        "1M_MONTH": Freq.M,  # 区分 1m (分钟) 和 1M (月线)
        "3M": Freq.S,        # 季线
        "12M": Freq.Y,       # 年线
        "1Y": Freq.Y,        # 年线 (TradingView 有时使用 1Y)
    }
    # 针对月线进行特殊修正，因为 TradingView 的 1M 是月线
    if r == "1M":
        return Freq.M
    return mapping.get(r)


def get_analysis_data(code: str, freq_enum: Freq) -> dict:
    """输入 code(如 601888) + czsc.Freq，输出 README 定义的 JSON 结构 dict。"""

    db_host = os.getenv("DB_HOST", "192.168.1.207")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_user = os.getenv("DB_USER", "datadriver")
    db_password = os.getenv("DB_PASSWORD", "datadriver")
    db_name = os.getenv("DB_NAME", "datadriver")

    engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

    ts_code = _normalize_ts_code(code)
    db_period = _get_ts_freq(freq_enum)

    query = text(
        """
        SELECT trade_time as dt, open, high, low, close, vol, amount
        FROM stock_kline
        WHERE ts_code = :code AND period = :period
        ORDER BY trade_time ASC
        """
    )

    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"code": ts_code, "period": db_period})

    if df.empty:
        return {"symbol": ts_code, "kline": [], "bi": [], "zs": [], "bs": []}

    # 与原版 main.py 保持一致的预处理
    df["dt"] = pd.to_datetime(df["dt"])
    df = df.sort_values("dt")
    df["symbol"] = ts_code
    df = df[["dt", "symbol", "open", "high", "low", "close", "vol", "amount"]].copy().reset_index(drop=True)

    # --- 这里新增：复刻 main.py 的数据清洗逻辑 ---
    # 1. 确保数值类型安全 (防止数据库返回 Decimal 或字符串混杂)
    price_cols = ["open", "high", "low", "close"]
    for col in price_cols + ["vol", "amount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # 2. 填充成交量空值
    if "vol" in df.columns:
        df["vol"] = df["vol"].fillna(0)
    if "amount" in df.columns:
        df["amount"] = df["amount"].fillna(0)

    # 3. 裁剪由于复权可能导致的头部无效 NaN 数据 (参考 main.py)
    # 找到第一个“价格字段全不为NaN”的行索引
    valid_mask = df[price_cols].notna().all(axis=1)
    if not valid_mask.any():
        # 如果全部都是 NaN，直接返回空
        return {"symbol": ts_code, "kline": [], "bi": [], "zs": [], "bs": []}

    first_valid_idx = df.index[valid_mask][0]
    if first_valid_idx != 0:
        df = df.loc[first_valid_idx:].copy().reset_index(drop=True)
    
    # 4. 剔除剩余的无效行 (价格为 NaN 的行)
    df = df.dropna(subset=["dt"] + price_cols).reset_index(drop=True)

    if df.empty:
        return {"symbol": ts_code, "kline": [], "bi": [], "zs": [], "bs": []}
    # ---------------------------------------------

    # czsc 计算
    raw_bars = czsc.format_standard_kline(df, freq=freq_enum)
    c = czsc.CZSC(raw_bars, max_bi_num=1000)

    zs_list = get_zs_seq(c.bi_list)

    # 与原版 main.py 保持一致的买卖点计算顺序
    is_strict = freq_enum not in (Freq.S, Freq.Y)
    th_val = 120 if freq_enum in (Freq.S, Freq.Y) else 100
    
    b1_list = find_B1(c.bi_list, zs_list, c, strict=is_strict, th=th_val)
    
    # 获取二类买卖点（季线/年线开启独立检测，不依赖一类买卖点列表）
    if freq_enum in (Freq.S, Freq.Y):
        b2_list = find_B2(c.bi_list, b1_list, independent=True)
    else:
        b2_list = find_B2(c.bi_list, b1_list, independent=False)
        
    lb2_list = find_LB2(c.bi_list, b2_list)
    b3_list = find_B3(c.bi_list, zs_list)
    s1_list = find_S1(c.bi_list, zs_list, c, strict=is_strict, th=th_val)
    
    if freq_enum in (Freq.S, Freq.Y):
        s2_list = find_S2(c.bi_list, s1_list, independent=True)
    else:
        s2_list = find_S2(c.bi_list, s1_list, independent=False)
        
    ls2_list = find_LS2(c.bi_list, s2_list)
    s3_list = find_S3(c.bi_list, zs_list)
    
    # 高周期额外补充“笔背驰”信号
    bi_bc_points = []
    if freq_enum in (Freq.S, Freq.Y):
        from ZS_sig_ai import find_bi_bc_signals
        bi_bc_points = find_bi_bc_signals(c.bi_list)
    
    bs_points = b1_list + b2_list + lb2_list + b3_list + s1_list + s2_list + ls2_list + s3_list + bi_bc_points

    # A. K线（只输出前端常用字段，避免把 cache 等内部字段带出去）
    kline_data = []
    for x in c.bars_raw:
        kline_data.append(
            {
                "dt": _dt_to_str(x.dt),
                "open": _json_safe(x.open),
                "close": _json_safe(x.close),
                "high": _json_safe(x.high),
                "low": _json_safe(x.low),
                "vol": _json_safe(getattr(x, "vol", None)),
                "amount": _json_safe(getattr(x, "amount", None)),
            }
        )

    # A. 基础信息
    last_bar = raw_bars[-1]
    
    # B. 笔（同步提取买卖点标记及翻译）
    # 建立信号映射字典 (czsc 默认标签 -> 缠论中文术语)
    mark_map = {
        "B1": "一买", "B2": "二买", "B3": "三买", "LB1": "类一买", "LB2": "类二买", "LB3": "类三买",
        "S1": "一卖", "S2": "二卖", "S3": "三卖", "LS1": "类一卖", "LS2": "类二卖", "LS3": "类三卖"
    }

    def _format_ai_dt(dt_val, f_enum):
        s_dt = _dt_to_str(dt_val)
        if f_enum == Freq.D and " 00:00:00" in s_dt:
            return s_dt.replace(" 00:00:00", " 15:00:00")
        return s_dt

    bi_data = []
    for bi in c.bi_list:
        actual_mark = ""
        actual_div = ""
        
        # 1. 扫描买卖点并翻译
        marks = []
        divs = []
        for p in bs_points:
            p_dt = _dt_to_str(p.get('dt'))
            if p_dt == _dt_to_str(bi.fx_b.dt):
                label_val = str(p.get('bs_type', ''))
                m_txt = mark_map.get(label_val, label_val)
                if m_txt and m_txt not in marks:
                    marks.append(m_txt)
                
                if label_val in ['B1', 'S1']:
                    if "趋势背驰" not in divs:
                        divs.append("趋势背驰")
        
        # 显示策略完全对齐官方：
        # mark列（买点列）：仅显示优先级最高的一个买卖点
        # div列（背驰列）：仅显示背驰相关信息，如"笔背驰"、"盘整背驰"，无则为空
        mark_priority = {"类一买": 1, "类二买": 2, "类三买": 3, "类一卖": 1, "类二卖": 2, "类三卖": 3,
                         "一买": 4, "二买": 5, "三买": 6, "一卖": 4, "二卖": 5, "三卖": 6}
        if marks:
            marks.sort(key=lambda x: mark_priority.get(x, 99))
            actual_mark = marks[0]  # 只取优先级最高的一个标记，和官方一致
            actual_div = "/".join(divs) if divs else ""  # 背驰列仅显示背驰信息
        else:
            actual_mark = ""
            actual_div = "/".join(divs) if divs else ""

        bi_data.append({
            "start_dt": _format_ai_dt(bi.fx_a.dt, freq_enum),
            "end_dt": _format_ai_dt(bi.fx_b.dt, freq_enum),
            "direction": "向上" if bi.direction == Direction.Up else "向下", # 显式转中文对齐
            "start_val": _json_safe(bi.fx_a.fx),
            "end_val": _json_safe(bi.fx_b.fx),
            "mark": actual_mark,
            "div": actual_div
        })

    # C. 线段数据 (Seg)
    seg_data = []
    try:
        from ZS_sig_ai import calculate_xd_list
        # 基于 czsc 计算出的笔（bi_list）直接计算标准线段
        bi_count = len(c.bi_list)
        print(f"[DEBUG] 开始计算线段，当前笔总数：{bi_count}")
        segment_data = calculate_xd_list(c.bi_list)
        print(f"[DEBUG] 线段计算完成，共 {len(segment_data)} 条")

        # 极端保底：如果线段计算返回空，手动生成至少一条线段
        if not segment_data and bi_count >= 1:
            print(f"[DEBUG] 线段计算返回空，启动极端保底生成")
            # 把所有笔当成一个未完成线段
            if bi_count >= 2:
                dir_count = Counter([bi.direction for bi in c.bi_list])
                xd_dir = dir_count.most_common(1)[0][0]
                direction = "向上" if xd_dir == Direction.Up else "向下"
                start_val = min(bi.low for bi in c.bi_list) if xd_dir == Direction.Up else max(bi.high for bi in c.bi_list)
                end_val = max(bi.high for bi in c.bi_list) if xd_dir == Direction.Up else min(bi.low for bi in c.bi_list)
            else:
                # 只有1笔的情况
                bi = c.bi_list[0]
                direction = "向上" if bi.direction == Direction.Up else "向下"
                start_val = bi.fx_a.fx
                end_val = bi.fx_b.fx

            segment_data = [{
                "start_dt": c.bi_list[0].sdt,
                "end_dt": c.bi_list[-1].edt,
                "direction": direction,
                "start_val": round(start_val, 2),
                "end_val": round(end_val, 2),
                "completed": False,
                "beichi": ""
            }]
            print(f"[DEBUG] 极端保底生成线段成功：{len(segment_data)} 条")

        # 转换格式供 AI 和图表使用
        for seg in segment_data[-7:]: # 保留最新7条线段给AI分析
            seg_mark = ""
            # 优化买卖点匹配：不仅匹配结束时间，也匹配价格区间
            seg_end_dt = _dt_to_str(seg['end_dt'])
            seg_end_val = seg['end_val']
            for p in bs_points:
                p_dt = _dt_to_str(p.get('dt'))
                p_price = p.get('price', 0)
                # 时间匹配 + 价格误差在0.5%以内
                if p_dt == seg_end_dt and abs(p_price - seg_end_val) / seg_end_val < 0.005:
                    seg_mark = mark_map.get(str(p.get('bs_type', '')), str(p.get('bs_type', '')))
                    break

            seg_data.append({
                "start_dt": _dt_to_str(seg['start_dt']),
                "end_dt": _dt_to_str(seg['end_dt']),
                "direction": seg['direction'],
                "start_val": _json_safe(seg['start_val']),
                "end_val": _json_safe(seg['end_val']),
                "completed": seg.get('completed', True),
                "mark": seg_mark,
                "div": seg.get('beichi', "")
            })
        print(f"[DEBUG] 最终生成线段数据：{len(seg_data)} 条")
    except Exception as seg_err:
        print(f"线段计算异常: {seg_err}")
        import traceback
        traceback.print_exc()
        # 异常情况下也返回保底线段，不要返回空
        if len(c.bi_list) >= 1:
            bi = c.bi_list[-1]
            seg_data = [{
                "start_dt": _dt_to_str(c.bi_list[0].sdt),
                "end_dt": _dt_to_str(bi.edt),
                "direction": "向上" if bi.direction == Direction.Up else "向下",
                "start_val": _json_safe(min(b.low for b in c.bi_list)),
                "end_val": _json_safe(max(b.high for b in c.bi_list)),
                "completed": False,
                "mark": "",
                "div": ""
            }]
            print(f"[DEBUG] 异常兜底生成线段：{len(seg_data)} 条")
        else:
            seg_data = []

    # D. 中枢（完善 ZS 对象及 Level 计算）
    formatted_zs = []
    for zs in zs_list:
        # 中枢内包含的笔数量，用于计算中枢级别
        # 公式: round(max([1, line_num / 9]), 2)，line_num > 9 表示中枢级别升级
        line_num = len(zs.bis)
        level = round(max([1, line_num / 9]), 2)
        formatted_zs.append({
            "start_dt": _dt_to_str(zs.sdt),
            "end_dt": _dt_to_str(zs.edt),
            "zg": _json_safe(float(zs.zg)),
            "zd": _json_safe(float(zs.zd)),
            "gg": _json_safe(float(zs.gg)),
            "dd": _json_safe(float(zs.dd)),
            "level": level,
            "line_num": line_num
        })

    return {
        "symbol": code,
        "freq": freq_enum.value,
        "current_price": _json_safe(last_bar.close),
        "current_dt": _dt_to_str(last_bar.dt),
        "bi": bi_data,
        "seg": seg_data,
        "zs": formatted_zs,
    }

def get_analysis_json(code: str, freq_enum: Freq) -> str:
    import json
    data = get_analysis_data(code=code, freq_enum=freq_enum)
    return json.dumps(data, ensure_ascii=False, allow_nan=False)


def get_history_data(
    code: str,
    freq_enum: Freq,
    from_ts: int | None = None,
    to_ts: int | None = None,
    countback: int | None = None,
    first_data_request: bool = False,
) -> dict:
    """将缠论分析结果转换成 TradingView UDF /history 输出结构。

    说明：
    - 核心K线字段以数组形式输出：t/o/h/l/c/v（t 为秒级时间戳）
    - 叠加字段：bis（笔）、bi_zss（笔中枢）、mmds（买卖点）
    - 线段/中枢线段等（xds/zsds/xd_zss/zsd_zss/bcs）当前算法未提供，先返回空数组
    - 新增：_perf 字段包含各环节性能埋点数据
    - 对于季线和年线，如果数据库中没有，则从日线数据实时聚合
    """
    import time as _time
    
    # 性能埋点数据
    perf = {
        "total_start": _time.perf_counter(),
        "db_connect_ms": 0.0,
        "db_query_ms": 0.0,
        "data_preprocess_ms": 0.0,
        "czsc_format_ms": 0.0,
        "czsc_parse_ms": 0.0,
        "zs_calc_ms": 0.0,
        "b1_calc_ms": 0.0,
        "b2_calc_ms": 0.0,
        "b3_calc_ms": 0.0,
        "s1_calc_ms": 0.0,
        "s2_calc_ms": 0.0,
        "s3_calc_ms": 0.0,
        "output_build_ms": 0.0,
        "total_ms": 0.0,
        "kline_count": 0,
        "bi_count": 0,
        "zs_count": 0,
        "bs_count": 0,
        "is_aggregated": False,  # 是否从日线聚合而来
    }
    
    # ========== 1. 数据库连接 ==========
    db_connect_start = _time.perf_counter()
    
    db_host = os.getenv("DB_HOST", "192.168.1.207")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_user = os.getenv("DB_USER", "datadriver")
    db_password = os.getenv("DB_PASSWORD", "datadriver")
    db_name = os.getenv("DB_NAME", "datadriver")

    engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

    ts_code = _normalize_ts_code(code)
    db_period = _get_ts_freq(freq_enum)
    
    perf["db_connect_ms"] = (_time.perf_counter() - db_connect_start) * 1000

    # ========== 2. 数据库查询 ==========
    db_query_start = _time.perf_counter()
    
    query = text(
        """
        SELECT trade_time as dt, open, high, low, close, vol, amount
        FROM stock_kline
        WHERE ts_code = :code AND period = :period
        ORDER BY trade_time ASC
        """
    )
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"code": ts_code, "period": db_period})
    
    perf["db_query_ms"] = (_time.perf_counter() - db_query_start) * 1000
    perf["kline_count"] = len(df)
    
    # 如果是季线或年线且没有数据，从日线数据聚合
    if df.empty and freq_enum in (Freq.S, Freq.Y):
        print(f"[DEBUG] {ts_code} 没有{freq_enum.value}数据，尝试从日线聚合...")
        
        # 查询日线数据
        daily_query = text(
            """
            SELECT trade_time as dt, open, high, low, close, vol, amount
            FROM stock_kline
            WHERE ts_code = :code AND period = 'daily'
            ORDER BY trade_time ASC
            """
        )
        with engine.connect() as conn:
            daily_df = pd.read_sql(daily_query, conn, params={"code": ts_code})
        
        if not daily_df.empty:
            print(f"[DEBUG] 从 {len(daily_df)} 条日线数据聚合...")
            
            # 数据预处理
            daily_df["dt"] = pd.to_datetime(daily_df["dt"])
            daily_df = daily_df.sort_values("dt")
            
            # 设置索引并聚合
            daily_df.set_index("dt", inplace=True)
            
            # 确定聚合规则
            if freq_enum == Freq.S:
                rule = "QS"  # 季度开始
            else:  # Freq.Y
                rule = "YS"  # 年度开始
            
            agg_dict = {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "vol": "sum",
                "amount": "sum"
            }
            
            df = daily_df.resample(rule).agg(agg_dict).dropna()
            df.reset_index(inplace=True)
            
            perf["is_aggregated"] = True
            perf["kline_count"] = len(df)
            print(f"[DEBUG] 聚合后得到 {len(df)} 条{freq_enum.value}数据")
        else:
            print(f"[DEBUG] {ts_code} 也没有日线数据，无法聚合")

    if df.empty:
        perf["total_ms"] = (_time.perf_counter() - perf["total_start"]) * 1000
        return {"s": "no_data", "_perf": perf}

    # ========== 3. 数据预处理 ==========
    preprocess_start = _time.perf_counter()
    
    df["dt"] = pd.to_datetime(df["dt"])
    df = df.sort_values("dt")
    df["symbol"] = ts_code
    df = df[["dt", "symbol", "open", "high", "low", "close", "vol", "amount"]].copy().reset_index(drop=True)

    # --- 这里新增：复刻 main.py 的数据清洗逻辑 ---
    # 1. 确保数值类型安全 (防止数据库返回 Decimal 或字符串混杂)
    price_cols = ["open", "high", "low", "close"]
    for col in price_cols + ["vol", "amount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # 2. 填充成交量空值
    if "vol" in df.columns:
        df["vol"] = df["vol"].fillna(0)
    if "amount" in df.columns:
        df["amount"] = df["amount"].fillna(0)

    # 3. 裁剪由于复权可能导致的头部无效 NaN 数据 (参考 main.py)
    # 找到第一个“价格字段全不为NaN”的行索引
    valid_mask = df[price_cols].notna().all(axis=1)
    if not valid_mask.any():
        perf["total_ms"] = (_time.perf_counter() - perf["total_start"]) * 1000
        return {"s": "no_data", "_perf": perf}

    first_valid_idx = df.index[valid_mask][0]
    if first_valid_idx != 0:
        df = df.loc[first_valid_idx:].copy().reset_index(drop=True)
    
    # 4. 剔除剩余的无效行 (价格为 NaN 的行)
    df = df.dropna(subset=["dt"] + price_cols).reset_index(drop=True)

    if df.empty:
        perf["total_ms"] = (_time.perf_counter() - perf["total_start"]) * 1000
        return {"s": "no_data", "_perf": perf}
    # ---------------------------------------------
    
    perf["data_preprocess_ms"] = (_time.perf_counter() - preprocess_start) * 1000

    # ========== 4. CZSC 格式化 ==========
    czsc_format_start = _time.perf_counter()
    raw_bars = czsc.format_standard_kline(df, freq=freq_enum)
    perf["czsc_format_ms"] = (_time.perf_counter() - czsc_format_start) * 1000
    
    # ========== 5. CZSC 解析（分型 + 笔） ==========
    czsc_parse_start = _time.perf_counter()
    c = czsc.CZSC(raw_bars, max_bi_num=1000)
    perf["czsc_parse_ms"] = (_time.perf_counter() - czsc_parse_start) * 1000
    perf["bi_count"] = len(c.bi_list)

    # 判断是否为日线级别（日线/周线/月线/季线/年线），用于时间戳转换
    is_daily = freq_enum in (Freq.D, Freq.W, Freq.M, Freq.S, Freq.Y)

    # --- K线：对象列表 -> 等长数组（并支持 from/to/countback 裁剪） ---
    bars = list(c.bars_raw)
    # 约定：firstDataRequest=true 时"第一次返回全量"，忽略 from/to/countback
    if first_data_request:
        from_ts = None
        to_ts = None
        countback = None

    if (from_ts is not None or to_ts is not None):
        f = -10**18 if from_ts is None else int(from_ts)
        t = 10**18 if to_ts is None else int(to_ts)
        bars = [b for b in bars if (_dt_to_ts(b.dt, is_daily, freq_enum) is not None and f <= _dt_to_ts(b.dt, is_daily, freq_enum) <= t)]

    if countback is not None and countback > 0 and len(bars) > countback:
        bars = bars[-int(countback) :]

    if not bars:
        perf["total_ms"] = (_time.perf_counter() - perf["total_start"]) * 1000
        return {"s": "no_data", "_perf": perf}

    t_arr, o_arr, h_arr, l_arr, c_arr, v_arr = [], [], [], [], [], []
    for b in bars:
        ts = _dt_to_ts(b.dt, is_daily, freq_enum)
        if ts is None:
            continue
        t_arr.append(int(ts))
        o_arr.append(_json_safe(b.open))
        h_arr.append(_json_safe(b.high))
        l_arr.append(_json_safe(b.low))
        c_arr.append(_json_safe(b.close))
        v_arr.append(_json_safe(getattr(b, "vol", None)))

    if not t_arr:
        perf["total_ms"] = (_time.perf_counter() - perf["total_start"]) * 1000
        return {"s": "no_data", "_perf": perf}

    t_min, t_max = t_arr[0], t_arr[-1]

    # --- 笔（bis）：start/end 结构 -> points 结构 ---
    bis = []
    for bi in c.bi_list:
        s_ts = _dt_to_ts(bi.fx_a.dt, is_daily, freq_enum)
        e_ts = _dt_to_ts(bi.fx_b.dt, is_daily, freq_enum)
        if s_ts is None or e_ts is None:
            continue
        # 只保留与当前K线区间有交集的笔
        if e_ts < t_min or s_ts > t_max:
            continue
        bis.append(
            {
                "points": [
                    {"time": int(s_ts), "price": _json_safe(bi.fx_a.fx)},
                    {"time": int(e_ts), "price": _json_safe(bi.fx_b.fx)},
                ],
                "linestyle": "0",
            }
        )

    # ========== 6. 中枢计算 ==========
    zs_calc_start = _time.perf_counter()
    zs_list = get_zs_seq(c.bi_list)
    perf["zs_calc_ms"] = (_time.perf_counter() - zs_calc_start) * 1000
    perf["zs_count"] = len(zs_list)
    
    bi_zss = []
    for zs in zs_list:
        s_ts = _dt_to_ts(zs.sdt, is_daily, freq_enum)
        e_ts = _dt_to_ts(zs.edt, is_daily, freq_enum)
        if s_ts is None or e_ts is None:
            continue
        if e_ts < t_min or s_ts > t_max:
            continue
        zg = _json_safe(float(zs.zg))
        zd = _json_safe(float(zs.zd))
        s_ts_i, e_ts_i = int(s_ts), int(e_ts)
        if e_ts_i <= s_ts_i:
            continue

        # 用两个对角点表达矩形：左上(s_ts, zg) 与 右下(e_ts, zd)
        bi_zss.append(
            {
                "points": [{"time": s_ts_i, "price": zg}, {"time": e_ts_i, "price": zd}],
                "linestyle": "0",
            }
        )

    # ========== 7. 六类买卖点计算 ==========
    is_strict = freq_enum not in (Freq.S, Freq.Y)
    th_val = 120 if freq_enum in (Freq.S, Freq.Y) else 100
    
    # B1
    b1_start = _time.perf_counter()
    b1_list = find_B1(c.bi_list, zs_list, c, strict=is_strict, th=th_val)
    perf["b1_calc_ms"] = (_time.perf_counter() - b1_start) * 1000
    
    # B2
    b2_start = _time.perf_counter()
    if freq_enum in (Freq.S, Freq.Y):
        b2_list = find_B2(c.bi_list, b1_list, independent=True)
    else:
        b2_list = find_B2(c.bi_list, b1_list, independent=False)
    perf["b2_calc_ms"] = (_time.perf_counter() - b2_start) * 1000
    
    # B3
    b3_start = _time.perf_counter()
    b3_list = find_B3(c.bi_list, zs_list)
    perf["b3_calc_ms"] = (_time.perf_counter() - b3_start) * 1000
    
    # S1
    s1_start = _time.perf_counter()
    s1_list = find_S1(c.bi_list, zs_list, c, strict=is_strict, th=th_val)
    perf["s1_calc_ms"] = (_time.perf_counter() - s1_start) * 1000
    
    # S2
    s2_start = _time.perf_counter()
    if freq_enum in (Freq.S, Freq.Y):
        s2_list = find_S2(c.bi_list, s1_list, independent=True)
    else:
        s2_list = find_S2(c.bi_list, s1_list, independent=False)
    perf["s2_calc_ms"] = (_time.perf_counter() - s2_start) * 1000
    
    # S3
    s3_start = _time.perf_counter()
    s3_list = find_S3(c.bi_list, zs_list)
    perf["s3_calc_ms"] = (_time.perf_counter() - s3_start) * 1000
    
    # LB2 / LS2 (之前遗漏，与 get_analysis_data 对齐)
    lb2_list = find_LB2(c.bi_list, b2_list)
    ls2_list = find_LS2(c.bi_list, s2_list)
    
    # 高周期额外补充“笔背驰”信号
    bi_bc_points = []
    if freq_enum in (Freq.S, Freq.Y):
        from ZS_sig_ai import find_bi_bc_signals
        bi_bc_points = find_bi_bc_signals(c.bi_list)
    
    bs_points = b1_list + b2_list + lb2_list + b3_list + s1_list + s2_list + ls2_list + s3_list + bi_bc_points
    perf["bs_count"] = len(bs_points)

    # ========== 调试打印：所有买卖点 ==========
    print(f"\n{'='*80}")
    print(f"[DEBUG] 买卖点计算结果 ({ts_code}, {freq_enum.value}):")
    print(f"  - B1: {len(b1_list)} 个")
    for p in b1_list:
        print(f"      {p.get('dt')} @ {p.get('price'):.2f}")
    print(f"  - B2: {len(b2_list)} 个")
    for p in b2_list:
        print(f"      {p.get('dt')} @ {p.get('price'):.2f}")
    print(f"  - B3: {len(b3_list)} 个")
    for p in b3_list:
        print(f"      {p.get('dt')} @ {p.get('price'):.2f}")
    print(f"  - S1: {len(s1_list)} 个")
    for p in s1_list:
        print(f"      {p.get('dt')} @ {p.get('price'):.2f}")
    print(f"  - S2: {len(s2_list)} 个")
    for p in s2_list:
        print(f"      {p.get('dt')} @ {p.get('price'):.2f}")
    print(f"  - LB2: {len(lb2_list)} 个")
    for p in lb2_list:
        print(f"      {p.get('dt')} @ {p.get('price'):.2f}")
    print(f"  - LS2: {len(ls2_list)} 个")
    for p in ls2_list:
        print(f"      {p.get('dt')} @ {p.get('price'):.2f}")
    print(f"  - S3: {len(s3_list)} 个")
    for p in s3_list:
        print(f"      {p.get('dt')} @ {p.get('price'):.2f}")
    # 打印最近 20 笔详情
    print(f"\n  [最近20笔]:")
    for bi in c.bi_list[-20:]:
        d = "↑" if bi.direction == Direction.Up else "↓"
        print(f"    {bi.sdt} → {bi.edt} {d} high={bi.high:.2f} low={bi.low:.2f} pp={bi.power_price:.2f} pv={bi.power_volume:.0f} len={bi.length}")
    print(f"{'='*80}\n")

    # ========== 8. 构建输出 ==========
    output_start = _time.perf_counter()
    
    mmds = []
    for p in bs_points:
        ts = _dt_to_ts(p.get("dt"), is_daily, freq_enum)
        price = p.get("price")
        if ts is None or price is None:
            continue
        # 注意：不再按时间范围过滤买卖点，返回所有计算出的点，让前端决定显示
        # if ts < t_min or ts > t_max:
        #     continue
        text_val = p.get("op_desc") or p.get("bs_type") or "signal"
        # 与文档示例风格更接近（"笔:3S"）
        if isinstance(p.get("bs_type"), str) and p.get("bs_type"):
            text_val = f"笔:{p.get('bs_type')}"
        mmds.append({"points": {"time": int(ts), "price": _json_safe(price)}, "text": str(text_val)})

    # TradingView 不显示线段，xds 保持空
    xds = []
    
    # ========== 调试打印：输出的 mmds ==========
    print(f"\n{'='*80}")
    print(f"[DEBUG] 返回给前端的 mmds ({len(mmds)} 个):")
    for m in mmds:
        print(f"      time={m['points']['time']}, price={m['points']['price']}, text={m['text']}")
    print(f"{'='*80}\n")

    perf["output_build_ms"] = (_time.perf_counter() - output_start) * 1000
    perf["total_ms"] = (_time.perf_counter() - perf["total_start"]) * 1000
    
    # 移除 total_start（它是 float，不是最终输出）
    del perf["total_start"]

    return {
        "s": "ok",
        "t": t_arr,
        "o": o_arr,
        "h": h_arr,
        "l": l_arr,
        "c": c_arr,
        "v": v_arr,
        "fxs": [],
        "bis": bis,
        "xds": xds,
        "zsds": [],
        "bi_zss": bi_zss,
        "xd_zss": [],
        "zsd_zss": [],
        "bcs": [],
        "mmds": mmds,
        "update": True,
        "chart_color": {},
        "update_time": int(time.time()),
        "last_k_time": int(t_arr[-1]),
        "_perf": perf,  # 性能埋点数据
    }


def get_history_json(
    code: str,
    freq_enum: Freq,
    from_ts: int | None = None,
    to_ts: int | None = None,
    countback: int | None = None,
    first_data_request: bool = False,
) -> str:
    import json

    data = get_history_data(
        code=code,
        freq_enum=freq_enum,
        from_ts=from_ts,
        to_ts=to_ts,
        countback=countback,
        first_data_request=first_data_request,
    )
    return json.dumps(data, ensure_ascii=False, allow_nan=False)


class ChanlunTradingViewViewSet(viewsets.GenericViewSet):
    """独立的缠论 history 接口（不修改原 TradingViewViewSet）。"""

    permission_classes = []  # 允许匿名访问

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        params = request.query_params

        symbol = (params.get("symbol") or "").strip().upper()
        resolution = params.get("resolution") or ""
        from_ts = params.get("from")
        to_ts = params.get("to")
        countback = params.get("countback")
        first_data_request = _parse_bool(params.get("firstDataRequest"))

        if not symbol or not resolution:
            return Response({"s": "no_data"})

        freq_enum = _resolution_to_freq(resolution)
        if not freq_enum:
            return Response({"s": "no_data"})

        try:
            from_ts_i = int(from_ts) if from_ts is not None else None
            to_ts_i = int(to_ts) if to_ts is not None else None
            countback_i = int(countback) if countback is not None else None
        except Exception:
            from_ts_i = None
            to_ts_i = None
            countback_i = None

        data = get_history_data(
            code=symbol,
            freq_enum=freq_enum,
            from_ts=from_ts_i,
            to_ts=to_ts_i,
            countback=countback_i,
            first_data_request=first_data_request,
        )
        return Response(data)

    @action(detail=False, methods=["post"], url_path="ai_analysis")
    @throttle_classes([UserRateThrottle])
    def ai_analysis(self, request):
        """
        AI 缠论分析接口 (POST)
        参数: symbol, resolution
        """
        # 强制登录校验
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "请先登录"}, status=401)

        # 从 request.data 读取 POST 参数
        params = request.data
        symbol = (params.get("symbol") or "").strip().upper()
        resolution = params.get("resolution") or "1D"

        if not symbol:
            return Response({"error": "缺少 symbol 参数"}, status=400)

        freq_enum = _resolution_to_freq(resolution)
        if not freq_enum:
            return Response({"error": f"不支持的周期: {resolution}"}, status=400)

        try:
            # 1. 获取基础缠论结构数据（笔、段、中枢、买卖点）
            chanlun_data = get_analysis_data(code=symbol, freq_enum=freq_enum)

            # 2. 调用 AI 服务进行推理复盘
            ai_data = AIService.analyze_chanlun(symbol, resolution, chanlun_data)

            # 如果服务返回的是错误，则直接给前端
            if "error" in ai_data:
                return Response(ai_data, status=500)

            # 3. 自动保存到历史记录表
            try:
                AIAnalysisHistory.objects.create(
                    symbol=symbol,
                    resolution=resolution,
                    prompt=ai_data.get("prompt"),
                    report=ai_data.get("report"),
                    model=ai_data.get("model"),
                    prompt_tokens=ai_data.get("usage", {}).get("prompt_tokens"),
                    completion_tokens=ai_data.get("usage", {}).get("completion_tokens"),
                    total_tokens=ai_data.get("usage", {}).get("total_tokens"),
                    creator=request.user if request.user.is_authenticated else None
                )
            except Exception as save_err:
                print(f"保存历史记录失败: {save_err}")

            # 返回完整结构 (附上统一状态码)
            return Response({
                "code": 2000,
                "msg": "分析成功",
                "data": {
                    "symbol": symbol,
                    "resolution": resolution,
                    "prompt": ai_data.get("prompt"),
                    "report": ai_data.get("report"),
                    "usage": ai_data.get("usage"),
                    "model": ai_data.get("model")
                }
            })
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response({"code": 5000, "msg": f"AI 分析执行异常: {str(e)}", "error": str(e)}, status=500)

    @action(detail=False, methods=["post"], url_path="ai_history")
    @throttle_classes([UserRateThrottle])
    def ai_history(self, request):
        """
        获取历史分析记录 (POST)
        参数: symbol (可选)
        """
        # 强制登录校验
        user = request.user
        if not user.is_authenticated:
            return Response({"code": 401, "error": "请先登录"}, status=401)

        params = request.data
        symbol = params.get("symbol")
        resolution = params.get("resolution")
        # 仅查询自己的历史
        queryset = AIAnalysisHistory.objects.filter(creator=user)
            
        if symbol:
            queryset = queryset.filter(symbol__icontains=symbol.upper())
        if resolution:
            queryset = queryset.filter(resolution=resolution)
            
        # 结果列表
        data = []
        for item in queryset[:50]: # 最近50条
            data.append({
                "id": item.id,
                "symbol": item.symbol,
                "resolution": item.resolution,
                "report": item.report,
                "prompt": item.prompt,
                "model": item.model,
                "usage": {
                    "prompt_tokens": item.prompt_tokens,
                    "completion_tokens": item.completion_tokens,
                    "total_tokens": item.total_tokens
                },
                "create_datetime": item.create_datetime.strftime("%Y-%m-%d %H:%M:%S")
            })
            
        return Response({
            "code": 2000,
            "data": data
        })

    @action(detail=False, methods=["post"], url_path="ai_history_delete")
    @throttle_classes([UserRateThrottle])
    def ai_history_delete(self, request):
        """
        删除指定的历史记录 (POST)
        参数: id
        """
        # 强制登录校验
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "请先登录"}, status=401)

        params = request.data
        history_id = params.get("id")
        if not history_id:
            return Response({"error": "缺少 id 参数"}, status=400)

        try:
            instance = AIAnalysisHistory.objects.get(id=history_id)
            # 权限检查：仅允许删除自己的
            if instance.creator != user:
                return Response({"code": 4030, "msg": "无权删除他人的历史记录", "error": "Forbidden"})
            
            instance.delete()
            return Response({
                "code": 2000, 
                "msg": "删除成功"
            })
        except AIAnalysisHistory.DoesNotExist:
            return Response({"code": 4040, "msg": "记录不存在", "error": "Not Found"})
