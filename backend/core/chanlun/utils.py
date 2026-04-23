"""Shared helpers for Chanlun API adapters."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

from tushare2postgresql import convert_stock_code


def dt_to_str(dt) -> str | None:
    if dt is None:
        return None
    if hasattr(dt, "strftime"):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)


def dt_to_ts(dt, is_daily: bool = False, freq=None) -> int | None:
    """Convert datetime-like values to TradingView-compatible second timestamps."""

    if dt is None:
        return None
    if isinstance(dt, (int, float)):
        return int(dt)
    try:
        ts = pd.Timestamp(dt)
        if ts is pd.NaT:
            return None

        freq_value = getattr(freq, "value", None)
        if freq_value == "周线":
            ts = ts - pd.Timedelta(days=ts.dayofweek)
        elif freq_value == "月线":
            ts = ts.replace(day=1)
        elif freq_value == "季线":
            new_month = ((ts.month - 1) // 3) * 3 + 1
            ts = ts.replace(month=new_month, day=1)
        elif freq_value == "年线":
            ts = ts.replace(month=1, day=1)

        if is_daily:
            return int(pd.Timestamp(ts.date()).timestamp())

        if ts.tz is None:
            ts = ts.tz_localize("Asia/Shanghai")
        return int(ts.timestamp())
    except Exception:
        return None


def normalize_ts_code(symbol: str) -> str:
    """Normalize user input to Tushare ``ts_code`` format."""

    s = str(symbol).strip().upper()
    if "." in s and (s.endswith(".SH") or s.endswith(".SZ")):
        return s
    return convert_stock_code(s)


def json_safe(v: Any):
    """Convert numpy, datetime and NaN/Inf values to JSON-safe Python values."""

    try:
        import numpy as np
    except Exception:
        np = None

    if v is None:
        return None

    if hasattr(v, "strftime") and not isinstance(v, (str, bytes)):
        return dt_to_str(v)

    if np is not None and isinstance(v, (getattr(np, "floating", ()), getattr(np, "integer", ()))):
        v = v.item()

    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None

    if isinstance(v, dict):
        return {str(k): json_safe(val) for k, val in v.items()}

    if isinstance(v, (list, tuple)):
        return [json_safe(x) for x in v]

    return v


def get_ts_freq(czsc_freq) -> str:
    """Map a czsc frequency to the ``stock_kline.period`` value."""

    freq_str = czsc_freq.value if hasattr(czsc_freq, "value") else str(czsc_freq)
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


def parse_bool(v: Any) -> bool:
    if v is None:
        return False
    return str(v).strip().lower() in {"1", "true", "yes", "y", "on"}


def resolution_to_freq(resolution: str):
    from czsc import Freq

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
        "1M_MONTH": Freq.M,
        "3M": Freq.S,
        "12M": Freq.Y,
        "1Y": Freq.Y,
    }
    if r == "1M":
        return Freq.M
    return mapping.get(r)
