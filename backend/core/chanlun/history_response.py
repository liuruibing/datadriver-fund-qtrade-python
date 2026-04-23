"""Shared TradingView history payload builders for Chanlun APIs."""

from __future__ import annotations

import time
from typing import Any

import pandas as pd

from .utils import dt_to_ts, json_safe


def build_simple_kline_response(df: pd.DataFrame, is_daily: bool, freq=None) -> dict[str, Any]:
    """Build a minimal TradingView history payload when CZSC parsing fails."""

    t_arr, o_arr, h_arr, l_arr, c_arr, v_arr = [], [], [], [], [], []
    for _, row in df.iterrows():
        ts = dt_to_ts(row.get("dt"), is_daily, freq)
        if ts is None:
            continue
        t_arr.append(int(ts))
        o_arr.append(float(row["open"]))
        h_arr.append(float(row["high"]))
        l_arr.append(float(row["low"]))
        c_arr.append(float(row["close"]))
        v_arr.append(float(row["vol"]) if row.get("vol") is not None else 0.0)

    return {
        "s": "ok",
        "t": t_arr,
        "o": o_arr,
        "h": h_arr,
        "l": l_arr,
        "c": c_arr,
        "v": v_arr,
        "fxs": [],
        "bis": [],
        "xds": [],
        "zsds": [],
        "bi_zss": [],
        "xd_zss": [],
        "zsd_zss": [],
        "bcs": [],
        "mmds": [],
    }


def build_history_payload(
    *,
    bars_raw: list[Any],
    bi_list: list[Any],
    zs_list: list[Any],
    bs_points: list[dict[str, Any]],
    is_daily: bool,
    freq,
    from_ts: int | None = None,
    to_ts: int | None = None,
    countback: int | None = None,
    first_data_request: bool = False,
    include_tradingview_meta: bool = False,
    perf: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a TradingView-compatible history response from parsed Chanlun objects."""

    bars = list(bars_raw)
    if first_data_request:
        from_ts = None
        to_ts = None
        countback = None

    if from_ts is not None or to_ts is not None:
        start_ts = -10**18 if from_ts is None else int(from_ts)
        end_ts = 10**18 if to_ts is None else int(to_ts)
        filtered_bars = []
        for bar in bars:
            ts = dt_to_ts(bar.dt, is_daily, freq)
            if ts is not None and start_ts <= ts <= end_ts:
                filtered_bars.append(bar)
        bars = filtered_bars

    if countback is not None and int(countback) > 0 and len(bars) > int(countback):
        bars = bars[-int(countback):]

    if not bars:
        payload = {"s": "no_data"}
        if perf is not None:
            payload["_perf"] = perf
        return payload

    t_arr, o_arr, h_arr, l_arr, c_arr, v_arr = [], [], [], [], [], []
    for bar in bars:
        ts = dt_to_ts(bar.dt, is_daily, freq)
        if ts is None:
            continue
        t_arr.append(int(ts))
        o_arr.append(json_safe(bar.open))
        h_arr.append(json_safe(bar.high))
        l_arr.append(json_safe(bar.low))
        c_arr.append(json_safe(bar.close))
        v_arr.append(json_safe(getattr(bar, "vol", None)))

    if not t_arr:
        payload = {"s": "no_data"}
        if perf is not None:
            payload["_perf"] = perf
        return payload

    t_min, t_max = t_arr[0], t_arr[-1]

    bis = []
    for bi in bi_list:
        start_ts = dt_to_ts(bi.fx_a.dt, is_daily, freq)
        end_ts = dt_to_ts(bi.fx_b.dt, is_daily, freq)
        if start_ts is None or end_ts is None:
            continue
        if end_ts < t_min or start_ts > t_max:
            continue
        bis.append(
            {
                "points": [
                    {"time": int(start_ts), "price": json_safe(bi.fx_a.fx)},
                    {"time": int(end_ts), "price": json_safe(bi.fx_b.fx)},
                ],
                "linestyle": "0",
            }
        )

    bi_zss = []
    for zs in zs_list:
        start_ts = dt_to_ts(zs.sdt, is_daily, freq)
        end_ts = dt_to_ts(zs.edt, is_daily, freq)
        if start_ts is None or end_ts is None:
            continue
        if end_ts < t_min or start_ts > t_max:
            continue
        start_ts_i, end_ts_i = int(start_ts), int(end_ts)
        if end_ts_i <= start_ts_i:
            continue
        bi_zss.append(
            {
                "points": [
                    {"time": start_ts_i, "price": json_safe(float(zs.zg))},
                    {"time": end_ts_i, "price": json_safe(float(zs.zd))},
                ],
                "linestyle": "0",
            }
        )

    mmds = []
    for point in bs_points:
        ts = dt_to_ts(point.get("dt"), is_daily, freq)
        price = point.get("price")
        if ts is None or price is None:
            continue
        text_val = point.get("op_desc") or point.get("bs_type") or "signal"
        if isinstance(point.get("bs_type"), str) and point.get("bs_type"):
            text_val = f"笔:{point.get('bs_type')}"
        mmds.append({"points": {"time": int(ts), "price": json_safe(price)}, "text": str(text_val)})

    payload = {
        "s": "ok",
        "t": t_arr,
        "o": o_arr,
        "h": h_arr,
        "l": l_arr,
        "c": c_arr,
        "v": v_arr,
        "fxs": [],
        "bis": bis,
        "xds": [],
        "zsds": [],
        "bi_zss": bi_zss,
        "xd_zss": [],
        "zsd_zss": [],
        "bcs": [],
        "mmds": mmds,
    }

    if include_tradingview_meta:
        payload.update(
            {
                "update": True,
                "chart_color": {},
                "update_time": int(time.time()),
                "last_k_time": int(t_arr[-1]),
            }
        )

    if perf is not None:
        payload["_perf"] = perf

    return payload
