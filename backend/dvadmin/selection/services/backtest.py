import datetime
from typing import List, Dict, Optional

from django.db.models import QuerySet

from dvadmin.selection.models import DailyMarket, IdxTa


def _normalize_date(date_str: Optional[str]) -> Optional[str]:
    """
    将 yyyy-mm-dd 转换为 yyyymmdd，若已是8位则原样返回。
    """
    if not date_str:
        return None
    return date_str.replace("-", "")


def _format_date(date_str: str) -> str:
    """
    将 yyyymmdd 转换为 yyyy-mm-dd。
    """
    return datetime.datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")


def _apply_date_filter(qs: QuerySet, start_date: Optional[str], end_date: Optional[str]) -> QuerySet:
    if start_date:
        qs = qs.filter(trade_date__gte=start_date)
    if end_date:
        qs = qs.filter(trade_date__lte=end_date)
    return qs


def get_kline_from_db(ts_code: str, start_date: Optional[str], end_date: Optional[str]) -> List[Dict]:
    """
    从 DailyMarket 获取K线数据。
    日期参数可为空；为空则返回该股票全部历史。
    """
    start = _normalize_date(start_date)
    end = _normalize_date(end_date)

    qs = DailyMarket.objects.filter(ts_code=ts_code)
    qs = _apply_date_filter(qs, start, end).order_by("trade_date").values(
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "pre_close",
        "change",
        "pct_chg",
        "vol",
        "amount",
    )

    return [
        {
            "trade_date": _format_date(item["trade_date"]),
            "open": item["open"],
            "high": item["high"],
            "low": item["low"],
            "close": item["close"],
            "pre_close": item["pre_close"],
            "change": item["change"],
            "pct_chg": item["pct_chg"],
            "vol": item["vol"],
            "amount": item["amount"],
        }
        for item in qs
    ]


def get_macd_backtest(ts_code: str, start_date: Optional[str], end_date: Optional[str]) -> Dict:
    """
    使用数据库中的指标与行情数据进行 MACD 回测。
    - MACD 线使用 IdxTa.dif
    - signal 线使用 IdxTa.dea
    - hist 使用 IdxTa.macd_val
    """
    start = _normalize_date(start_date)
    end = _normalize_date(end_date)

    # 行情数据
    kline_qs = DailyMarket.objects.filter(ts_code=ts_code)
    kline_qs = _apply_date_filter(kline_qs, start, end).order_by("trade_date").values(
        "trade_date", "close"
    )

    if not kline_qs.exists():
        return {"buy_dates": [], "sell_dates": [], "macd": []}

    # MACD 数据
    macd_qs = IdxTa.objects.filter(ts_code=ts_code)
    macd_qs = _apply_date_filter(macd_qs, start, end).order_by("trade_date").values(
        "trade_date", "dif", "dea", "macd_val"
    )

    macd_map = {item["trade_date"]: item for item in macd_qs}

    macd_records = []
    buy_dates: List[str] = []
    sell_dates: List[str] = []

    prev_diff = None  # 上一日 dif-dea

    for item in kline_qs:
        trade_date_raw = item["trade_date"]
        trade_date_fmt = _format_date(trade_date_raw)
        close = item["close"]

        macd_item = macd_map.get(trade_date_raw)
        dif = macd_item["dif"] if macd_item else None
        dea = macd_item["dea"] if macd_item else None
        hist = macd_item["macd_val"] if macd_item else None

        macd_records.append(
            {
                "date": trade_date_fmt,
                "close": close,
                "macd": dif,
                "signal": dea,
                "hist": hist,
            }
        )

        # 计算金叉 / 死叉
        if dif is not None and dea is not None:
            curr_diff = dif - dea
            if prev_diff is not None:
                if prev_diff <= 0 < curr_diff:
                    buy_dates.append(trade_date_fmt)
                elif prev_diff >= 0 > curr_diff:
                    sell_dates.append(trade_date_fmt)
            prev_diff = curr_diff

    return {"buy_dates": buy_dates, "sell_dates": sell_dates, "macd": macd_records}
