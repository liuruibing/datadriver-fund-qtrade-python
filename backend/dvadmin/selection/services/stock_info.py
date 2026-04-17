import logging
import os
from typing import Optional

import pandas as pd
import tushare as ts

logger = logging.getLogger(__name__)

# NOTE: 当前使用的 get_realtime_quotes 接口无需 Token
# TUSHARE_TOKEN = os.getenv(
#     'TUSHARE_TOKEN',
#     'ea8e4ada23d2aa40d031cbdbb6ce73d9877caeb409b0a82424ac3e66',
# )
# ts.set_token(TUSHARE_TOKEN)

def _normalize_ts_code(code: str) -> str:
    """
    将股票代码统一转为 ts_code 格式（如 000001.SZ）。
    支持纯数字输入（如 000001）和已带后缀的输入。
    """
    s = str(code).strip().upper()
    if "." in s and (s.endswith(".SH") or s.endswith(".SZ")):
        return s
    code_str = s.zfill(6)
    if code_str.startswith(("6", "688", "689")):
        return f"{code_str}.SH"
    return f"{code_str}.SZ"


def _ts_to_sina(ts_code: str) -> str:
    """
    将 ts_code (如 000001.SZ) 转换为新浪格式 (如 sz000001)。
    """
    if "." not in ts_code:
        # 尝试通过前缀猜测，如果是纯数字
        if ts_code.startswith(("6", "688", "689")):
            return f"sh{ts_code.zfill(6)}"
        return f"sz{ts_code.zfill(6)}"
        
    code, market = ts_code.split(".")
    return f"{market.lower()}{code}"


# NOTE: 新浪数据源单次最多查询 50 只股票，超出需分批
_BATCH_SIZE = 50


def get_stock_quote(ts_code: str) -> list[dict]:
    """
    通过 Tushare ts.get_realtime_quotes() 获取股票的盘中实时最新成交价和涨跌幅。
    此方式直接对接新浪数据源，无需消耗积分，且指数数据更稳定。

    Args:
        ts_code: 股票代码，支持以下格式：
            - 单只: "000001.SZ" 或 "000001"
            - 多只: "000001.SZ,600000.SH" 或 "000001,600000"

    Returns:
        包含 close 和 pct_chg 的字典列表，查不到则返回空列表 []
    """
    # 对每个代码做标准化
    raw_codes = [c.strip() for c in ts_code.split(",") if c.strip()]
    normalized_codes = [_normalize_ts_code(c) for c in raw_codes]

    # 按 _BATCH_SIZE 分批
    all_dfs: list[pd.DataFrame] = []
    for i in range(0, len(normalized_codes), _BATCH_SIZE):
        batch = normalized_codes[i : i + _BATCH_SIZE]
        sina_batch = [_ts_to_sina(c) for c in batch]
        try:
            # 使用经典版接口，直连新浪，更稳且免费
            df = ts.get_realtime_quotes(sina_batch)
        except Exception as e:
            logger.error("调用 Tushare get_realtime_quotes 接口失败 [%s]: %s", batch, e)
            continue

        if df is not None and not df.empty:
            all_dfs.append(df)

    if not all_dfs:
        logger.warning("未获取到股票 %s 的实时数据", ts_code)
        return []

    merged_df = pd.concat(all_dfs, ignore_index=True)

    result: list[dict] = []
    for _, row in merged_df.iterrows():
        try:
            current_price = float(row["price"])
            pre_close = float(row["pre_close"])
            name = str(row.get("name", ""))
            code = str(row.get("code", ""))

            # 映射回 ts_code，经典版接口返回的 code 不带后缀
            # 优先根据名称映射指数，确保 000001.SH 不会被错认位 000001.SZ (平安银行)
            if "上证指数" in name:
                final_code = "000001.SH"
            elif "深证成指" in name:
                final_code = "399001.SZ"
            elif "创业板指" in name:
                final_code = "399006.SZ"
            else:
                # 普通股票映射
                final_code = _normalize_ts_code(code)

            # 涨跌幅公式: pct_chg = (最新价 - 昨收价) / 昨收价 × 100%
            # 优化逻辑: 如果当前价为 0 (通常为未开盘或竞价阶段)，涨跌幅显示为 "-" 而不是 -100%
            if pre_close > 0 and current_price > 0:
                pct_chg = round((current_price - pre_close) / pre_close * 100, 2)
            else:
                pct_chg = "-"

            result.append(
                {
                    "ts_code": final_code,
                    "close": current_price,
                    "pct_chg": pct_chg,
                }
            )
        except Exception as e:
            logger.error("解析实时行情数据行失败: %s", e)
            continue

    return result
