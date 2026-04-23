"""Data access helpers for the Chanlun TradingView endpoint."""

from __future__ import annotations

import os

import pandas as pd
from sqlalchemy import create_engine, text


PRICE_COLS = ["open", "high", "low", "close"]
KLINE_COLS = ["dt", "symbol", "open", "high", "low", "close", "vol", "amount"]


def create_stock_kline_engine():
    db_host = os.getenv("DB_HOST", "192.168.1.207")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_user = os.getenv("DB_USER", "datadriver")
    db_password = os.getenv("DB_PASSWORD", "datadriver")
    db_name = os.getenv("DB_NAME", "datadriver")
    return create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")


def read_stock_kline(engine, ts_code: str, period: str) -> pd.DataFrame:
    query = text(
        """
        SELECT trade_time as dt, open, high, low, close, vol, amount
        FROM stock_kline
        WHERE ts_code = :code AND period = :period
        ORDER BY trade_time ASC
        """
    )
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params={"code": ts_code, "period": period})


def clean_kline_df(df: pd.DataFrame, ts_code: str) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    df["dt"] = pd.to_datetime(df["dt"])
    df = df.sort_values("dt")
    df["symbol"] = ts_code
    df = df[KLINE_COLS].copy().reset_index(drop=True)

    for col in PRICE_COLS + ["vol", "amount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "vol" in df.columns:
        df["vol"] = df["vol"].fillna(0)
    if "amount" in df.columns:
        df["amount"] = df["amount"].fillna(0)

    valid_mask = df[PRICE_COLS].notna().all(axis=1)
    if not valid_mask.any():
        return df.iloc[0:0].copy()

    first_valid_idx = df.index[valid_mask][0]
    if first_valid_idx != 0:
        df = df.loc[first_valid_idx:].copy().reset_index(drop=True)

    return df.dropna(subset=["dt"] + PRICE_COLS).reset_index(drop=True)


def aggregate_daily_kline(daily_df: pd.DataFrame, freq_enum) -> pd.DataFrame:
    if daily_df.empty:
        return daily_df

    df = daily_df.copy()
    df["dt"] = pd.to_datetime(df["dt"])
    df = df.sort_values("dt")
    df.set_index("dt", inplace=True)

    rule = "QS" if getattr(freq_enum, "value", None) == "季线" else "YS"
    agg_dict = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "vol": "sum",
        "amount": "sum",
    }

    df = df.resample(rule).agg(agg_dict).dropna()
    df.reset_index(inplace=True)
    return df


def aggregate_kline_by_rule(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Aggregate pre-cleaned kline data by a pandas resample rule."""

    if df.empty:
        return df

    data = df.copy()
    data["dt"] = pd.to_datetime(data["dt"])
    data = data.sort_values("dt")
    data.set_index("dt", inplace=True)

    agg_dict = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "vol": "sum",
        "amount": "sum",
    }
    if "symbol" in data.columns:
        agg_dict["symbol"] = "first"

    data = data.resample(rule).agg(agg_dict).dropna()
    data.reset_index(inplace=True)
    return data
