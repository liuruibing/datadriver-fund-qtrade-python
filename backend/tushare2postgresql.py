"""Minimal tushare2postgresql shim.

Only keep convert_stock_code for chanlun history endpoints.
"""


def convert_stock_code(code):
    code_str = str(code).zfill(6)
    # 上海证券交易所
    if code_str.startswith(('6', '688', '689')):  # 主板 + 科创板
        return f"{code_str}.SH"
    # 深圳证券交易所：主板、中小板、创业板
    if code_str.startswith(('000', '001', '002', '003', '300', '301')):
        return f"{code_str}.SZ"
    # 其他情况默认深圳
    return f"{code_str}.SZ"
