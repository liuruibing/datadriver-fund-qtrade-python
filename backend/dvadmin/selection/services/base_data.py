from datetime import datetime
from django.db.models import Max
from dvadmin.selection.models import DailyMarket, StockBasic, Industry


def convert_sw_industry():
    """
    查询 Industry 表中 的申万行业 SWSR
    并转换成 前端要求的 id,pid 树结构
    """
    qs = Industry.objects.filter(VC_INDUSTRY_TYPE="SWSR")

    nodes = {}

    for row in qs:
        # 一级行业
        if row.VC_INDUSTRY_CODE1 and row.VC_INDUSTRY_CODE1 not in nodes:
            nodes[row.VC_INDUSTRY_CODE1] = {
                "id": row.VC_INDUSTRY_CODE1,
                "name": row.VC_INDUSTRY_NAME1,
                "level": "L1",
                "pid": "0",
            }

        # 二级行业
        if row.VC_INDUSTRY_CODE2 and row.VC_INDUSTRY_CODE2 not in nodes:
            nodes[row.VC_INDUSTRY_CODE2] = {
                "id": row.VC_INDUSTRY_CODE2,
                "name": row.VC_INDUSTRY_NAME2,
                "level": "L2",
                "pid": row.VC_INDUSTRY_CODE1,
            }

        # 三级行业
        if row.VC_INDUSTRY_CODE3 and row.VC_INDUSTRY_CODE3 not in nodes:
            nodes[row.VC_INDUSTRY_CODE3] = {
                "id": row.VC_INDUSTRY_CODE3,
                "name": row.VC_INDUSTRY_NAME3,
                "level": "L3",
                "pid": row.VC_INDUSTRY_CODE2,
            }

    return nodes.values()

def get_base_selection_data(type):
    """
    根据类型获取基础信息:
    latest_trade_date 类型 获取DailyMarket 的最大 trade_date
    industry_list 类型 获取 SwIndustry 的行业列表（3级）
    ts_code_list 类型 获取 StockBasic 的 ts_code symbol name 列表
    """
    if type == "latest_trade_date":
        # 最大交易日
        latest_trade_date = DailyMarket.objects.aggregate(
            latest=Max("trade_date")
        )["latest"]

        return datetime.strptime(latest_trade_date, "%Y%m%d").strftime("%Y-%m-%d")

    elif type == "industry_list":
        # 申万行业列表
        industry_list = convert_sw_industry()

        return list(industry_list)

    elif type == "ts_code_list":
        # 股票代码列表 应前端要求获取代码、名称
        ts_code_qs = StockBasic.objects.all().order_by("ts_code")
        ts_code_list = [
            {"ts_code": s.ts_code, "symbol": s.symbol, "name": s.name, "industry": s.industry} for s in ts_code_qs
        ]

        return list(ts_code_list)
