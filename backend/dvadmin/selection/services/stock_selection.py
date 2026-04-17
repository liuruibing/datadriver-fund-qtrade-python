import logging

from django.db.models import Q, Avg, Value, Max, Subquery, OuterRef
from django.db.models.functions import Coalesce
from dvadmin.selection.models import StockBasic, DailyMarket, DailyBasic, StockIndustry, IdxShares, IdxTa, StockAnalysis

from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def get_avg_n_day_amount_codes_and_map(date, amount_avg_min, amount_avg_max, n_days=5):
    """
    计算截止日期前 N 个交易日的平均成交额，并返回符合范围条件的 ts_code 集合和所有计算出的平均值映射。
    
    参数说明：
    - amount_avg_min/max: 前端传入的单位是亿元，需要转换为千元进行筛选（1亿元 = 100000千元）
    
    返回: (符合条件的ts_code集合, 所有计算出的平均值映射(单位：亿元))
    数据库中的amount是千元，转换为亿元需要除以100000
    """
    # 找出在截止日期前，所有股票的 N 个交易日列表
    latest_n_dates_qs = DailyMarket.objects.filter(
        trade_date__lte=date
    ).order_by('-trade_date').values_list('trade_date', flat=True).distinct()[:n_days]

    latest_n_dates = list(latest_n_dates_qs)

    if not latest_n_dates:
        return set(), {}  # 如果没有找到日期，则返回空集和空映射

    # 只保留这 N 个日期内的数据
    daily_market_n_days_qs = DailyMarket.objects.filter(
        trade_date__in=latest_n_dates
    )

    # 按 ts_code 分组，计算平均成交额（单位：千元）
    avg_amount_qs = daily_market_n_days_qs.values('ts_code').annotate(
        avg_amount_n_days=Avg(Coalesce('amount', Value(0.0)))
    )

    # 构建所有股票的平均值映射（单位：亿元），并筛选符合条件的代码
    amount_map = {}
    filtered_codes = set()
    
    # 前端传入的是亿元，需要转换为千元进行筛选
    amount_avg_min_qian = amount_avg_min * 100000 if amount_avg_min is not None else None
    amount_avg_max_qian = amount_avg_max * 100000 if amount_avg_max is not None else None
    
    for item in avg_amount_qs:
        ts_code = item['ts_code']
        avg_amount_qian = item['avg_amount_n_days']
        # 转换为亿元（除以100000）
        avg_amount_yi = avg_amount_qian / 100000 if avg_amount_qian else None
        amount_map[ts_code] = avg_amount_yi
        
        # 检查是否符合筛选条件（使用千元进行比较）
        if amount_avg_min_qian is not None and avg_amount_qian is not None and avg_amount_qian < amount_avg_min_qian:
            continue
        if amount_avg_max_qian is not None and avg_amount_qian is not None and avg_amount_qian > amount_avg_max_qian:
            continue
        filtered_codes.add(ts_code)

    return filtered_codes, amount_map


def filter_stock_features(
        date: str = None,
        search_term: str = None,
        pe_min: float = None,
        pe_max: float = None,
        amount_avg_min: float = None,
        amount_avg_max: float = None,
        circ_mv_min: float = None,
        circ_mv_max: float = None,
        industry: str = None
):
    """
    联合筛选 StockBasic, DailyMarket, DailyBasic 模型数据。
    筛选逻辑基于一个单一的“数据截止日期”和前5个交易日平均值。
    """

    date = date.replace("-",'')

    stock_qs = StockBasic.objects.all()

    #  StockBasic 字段筛选
    if search_term:
        stock_qs = stock_qs.filter(
            Q(ts_code__icontains=search_term) | Q(name__icontains=search_term)
        )

    # 行业筛选 使用 StockIndustry
    if industry:
        # 行业用 , 分割成多个行业
        industry_names = [x.strip() for x in industry.split(",") if x.strip()]
        # 查 StockIndustry 表，获取对应的 symbol 列表
        stock_industry_qs = StockIndustry.objects.filter(
            VC_INDUSTRY_TYPE="SWSR",
            VC_INDUSTRY_NAME_3__in=industry_names
        ).values("VC_SYMBOL", "VC_INDUSTRY_NAME" , "VC_INDUSTRY_NAME_2", "VC_INDUSTRY_NAME_3").distinct()
    else:
        stock_industry_qs = StockIndustry.objects.filter(
            VC_INDUSTRY_TYPE="SWSR"
        ).values("VC_SYMBOL", "VC_INDUSTRY_NAME" , "VC_INDUSTRY_NAME_2", "VC_INDUSTRY_NAME_3").distinct()

    # 构建 VC_SYMBOL 到 三级级行业 的映射
    symbol_map = {
        row["VC_SYMBOL"]: {"industry": f'{row["VC_INDUSTRY_NAME"]}-{row["VC_INDUSTRY_NAME_2"]}-{row["VC_INDUSTRY_NAME_3"]}'}
        for row in stock_industry_qs
    }

    # StockBasic 字段筛选，只保留映射中的 symbol
    stock_qs = stock_qs.filter(symbol__in=symbol_map.keys())

    # 去重
    final_ts_codes = set(stock_qs.values_list('ts_code', flat=True))

    # 未指定日期
    if not date and (
            pe_min is not None or pe_max is not None or amount_avg_min is not None or amount_avg_max is not None or
            circ_mv_min is not None or circ_mv_max is not None):
        logger.error("缺少日期 (date)，无法执行 PE、5日成交额或流通市值筛选。")
        return []

    # DailyBasic 字段筛选
    if pe_min is not None or pe_max is not None:

        daily_basic_qs = DailyBasic.objects.filter(trade_date=date)

        # PE 范围筛选
        if pe_min is not None:
            daily_basic_qs = daily_basic_qs.filter(pe__gte=pe_min)
        if pe_max is not None:
            daily_basic_qs = daily_basic_qs.filter(pe__lte=pe_max)

        # 取交集
        pe_filter_codes = set(daily_basic_qs.values_list('ts_code', flat=True))
        final_ts_codes &= pe_filter_codes

    # IdxTa 字段筛选：从d5_vol_avg获取5日平均成交额（单位：千元）
    vol_avg5_map = {}
    if amount_avg_min is not None or amount_avg_max is not None:
        # 从IdxTa获取5日平均成交额，并筛选（直接使用传入日期）
        amount_avg_min_qian = amount_avg_min * 100000 if amount_avg_min is not None else None
        amount_avg_max_qian = amount_avg_max * 100000 if amount_avg_max is not None else None

        idx_ta_qs = IdxTa.objects.filter(
            ts_code__in=final_ts_codes,
            trade_date=date
        )
        if amount_avg_min_qian is not None:
            idx_ta_qs = idx_ta_qs.filter(d5_vol_avg__gte=amount_avg_min_qian)
        if amount_avg_max_qian is not None:
            idx_ta_qs = idx_ta_qs.filter(d5_vol_avg__lte=amount_avg_max_qian)

        amount_filter_codes = set()
        for idx_ta in idx_ta_qs.values('ts_code', 'd5_vol_avg'):
            d5_vol_avg_qian = idx_ta['d5_vol_avg']
            ts_code = idx_ta['ts_code']
            if d5_vol_avg_qian is None:
                continue
            vol_avg5_map[ts_code] = d5_vol_avg_qian / 100000  # 转换为亿元返回
            amount_filter_codes.add(ts_code)

        # 取交集
        final_ts_codes &= amount_filter_codes

    # DailyBasic 流通市值筛选
    if circ_mv_min is not None or circ_mv_max is not None:
        daily_basic_qs = DailyBasic.objects.filter(trade_date=date)
        
        # 前端传入的是亿元，数据库是万元，需要转换（1亿元 = 10000万元）
        if circ_mv_min is not None:
            daily_basic_qs = daily_basic_qs.filter(circ_mv__gte=circ_mv_min * 10000)
        if circ_mv_max is not None:
            daily_basic_qs = daily_basic_qs.filter(circ_mv__lte=circ_mv_max * 10000)
        
        # 取交集
        circ_mv_filter_codes = set(daily_basic_qs.values_list('ts_code', flat=True))
        final_ts_codes &= circ_mv_filter_codes

    final_qs = StockBasic.objects.filter(ts_code__in=final_ts_codes).values(
        "ts_code",
        "symbol",
        "name",
        "industry",
        "market",
    )

    if date:
        # 取每日流通市值和PE值
        daily_basic_data = DailyBasic.objects.filter(
            trade_date=date, ts_code__in=final_ts_codes
        ).values("ts_code", "circ_mv", "pe")
        
        circ_mv_map = {}
        pe_map = {}
        for item in daily_basic_data:
            ts_code = item["ts_code"]
            circ_mv_map[ts_code] = item["circ_mv"]
            pe_map[ts_code] = item["pe"]
        
        # 如果筛选时没有获取5日平均成交额，则现在从IdxTa获取（使用传入日期）
        if not vol_avg5_map:
            idx_ta_qs = IdxTa.objects.filter(
                ts_code__in=final_ts_codes,
                trade_date=date
            ).values('ts_code', 'd5_vol_avg')
            for item in idx_ta_qs:
                if item['d5_vol_avg'] is not None:
                    vol_avg5_map[item['ts_code']] = item['d5_vol_avg'] / 100000
    else:
        circ_mv_map = {}
        pe_map = {}
        vol_avg5_map = {}

    # 构建输出
    result = []
    for idx, row in enumerate(final_qs, start=1):
        ts = row["ts_code"]
        symbol = row["symbol"]
        industry_info = symbol_map.get(symbol, {})
        # 数据库中的流通市值是万元，转换为亿元返回给前端（除以10000）
        circ_mv_yi = None
        if circ_mv_map.get(ts) is not None:
            circ_mv_yi = circ_mv_map.get(ts) / 10000
        
        result.append({
            "index": idx,
            "ts_code": row["ts_code"],
            "symbol": row["symbol"],
            "name": row["name"],
            "industry": industry_info.get("industry", ""),
            "market": row["market"],
            "circ_mv": circ_mv_yi,
            "vol_avg5": vol_avg5_map.get(ts),
            "pe": pe_map.get(ts),
        })

    return result


def filter_stock_features_refined(
        date: str = None,
        search_term: str = None,
        pe_min: float = None,
        pe_max: float = None,
        amount_avg_min: float = None,
        amount_avg_max: float = None,
        circ_mv_min: float = None,
        circ_mv_max: float = None,
        industry: str = None,
        chip1: int = None,
        chip2: int = None,
        macd1: int = None,
        macd2: int = None
):
    """
    二次筛选（精筛）服务：在初步筛选的基础上，增加以下筛选条件：
    - chip1: 90%筹码集中度<15%，为1则筛选，可选
    - chip2: 前十大流通股东上期公告持仓占流通盘>65%，为1则筛选，可选
    - macd1: MACD特征: 金叉，为1则筛选，可选
    - macd2: MACD特征: 突破过0轴以上反复纠缠，为1则筛选，可选

    返回字段：
    - id: 索引
    - ts_code: tushare代码
    - symbol: 股票代码
    - name: 股票名称
    - data_date: 数据日期
    - current_price: 收盘价格
    - macd: 是否MACD金叉
    - macd_zero_break: 是否突破过0轴以上反复纠缠
    - chip_concentration_90: 90%筹码集中度
    - top10_share_ratio: 前十大流通股东上期公告持仓占流通盘
    - industry: 行业
    """
    # 先进行初步筛选
    preliminary_results = filter_stock_features(
        date=date,
        search_term=search_term,
        pe_min=pe_min,
        pe_max=pe_max,
        amount_avg_min=amount_avg_min,
        amount_avg_max=amount_avg_max,
        circ_mv_min=circ_mv_min,
        circ_mv_max=circ_mv_max,
        industry=industry
    )
    
    if not preliminary_results:
        return []
    
    # 获取所有股票的ts_code
    ts_codes = [item["ts_code"] for item in preliminary_results]
    
    # 格式化日期
    date_str = date.replace("-", "") if date else None
    data_date_formatted = date if date else None
    
    # 获取收盘价格（从DailyBasic）
    current_price_map = {}
    if date_str:
        daily_basic_data = DailyBasic.objects.filter(
            trade_date=date_str,
            ts_code__in=ts_codes
        ).values("ts_code", "close")
        for item in daily_basic_data:
            current_price_map[item["ts_code"]] = item["close"]

    # 从StockAnalysis表获取分析数据
    stock_analysis_data = {}
    if date:
        analysis_qs = StockAnalysis.objects.filter(
            ts_code__in=ts_codes,
            data_date=date
        ).values('ts_code', 'macd', 'macd_zero_break', 'chip_concentration_90', 'top10_share_ratio')

        for item in analysis_qs:
            stock_analysis_data[item['ts_code']] = {
                'macd': item['macd'],
                'macd_zero_break': item['macd_zero_break'],
                'chip_concentration_90': item['chip_concentration_90'],
                'top10_share_ratio': item['top10_share_ratio']
            }
    
    # 筛选逻辑
    chip1_filtered_codes = set(ts_codes)
    chip2_filtered_codes = set(ts_codes)
    macd1_filtered_codes = set(ts_codes)
    macd2_filtered_codes = set(ts_codes)

    # chip1筛选：90%筹码集中度<15%
    if chip1 == 1:
        chip1_filtered_codes = set()
        for ts_code in ts_codes:
            analysis_data = stock_analysis_data.get(ts_code, {})
            chip_concentration = analysis_data.get('chip_concentration_90')
            if chip_concentration is not None and chip_concentration < 15:
                chip1_filtered_codes.add(ts_code)

    # chip2筛选：前十大流通股东上期公告持仓占流通盘>65%
    if chip2 == 1:
        chip2_filtered_codes = set()
        for ts_code in ts_codes:
            analysis_data = stock_analysis_data.get(ts_code, {})
            top10_ratio = analysis_data.get('top10_share_ratio')
            if top10_ratio is not None and top10_ratio > 65:
                chip2_filtered_codes.add(ts_code)

    # macd1筛选：MACD金叉
    if macd1 == 1:
        macd1_filtered_codes = set()
        for ts_code in ts_codes:
            analysis_data = stock_analysis_data.get(ts_code, {})
            if analysis_data.get('macd', False):
                macd1_filtered_codes.add(ts_code)

    # macd2筛选：突破过0轴以上反复纠缠
    if macd2 == 1:
        macd2_filtered_codes = set()
        for ts_code in ts_codes:
            analysis_data = stock_analysis_data.get(ts_code, {})
            if analysis_data.get('macd_zero_break', False):
                macd2_filtered_codes.add(ts_code)

    # 取交集：所有筛选条件的交集
    final_codes = set(ts_codes)
    if chip1 == 1:
        final_codes &= chip1_filtered_codes
    if chip2 == 1:
        final_codes &= chip2_filtered_codes
    if macd1 == 1:
        final_codes &= macd1_filtered_codes
    if macd2 == 1:
        final_codes &= macd2_filtered_codes
    
    # 构建最终结果，保持原有顺序
    result = []
    result_id = 1
    for item in preliminary_results:
        ts_code = item["ts_code"]
        if ts_code in final_codes:
            analysis_data = stock_analysis_data.get(ts_code, {})
            result.append({
                "id": result_id,
                "ts_code": ts_code,
                "symbol": item["symbol"],
                "name": item["name"],
                "data_date": data_date_formatted,
                "current_price": current_price_map.get(ts_code),
                "macd": analysis_data.get('macd', False),
                "macd_zero_break": analysis_data.get('macd_zero_break', False),
                "chip_concentration_90": analysis_data.get('chip_concentration_90'),
                "top10_share_ratio": analysis_data.get('top10_share_ratio'),
                "industry": item["industry"],
            })
            result_id += 1
    
    return result