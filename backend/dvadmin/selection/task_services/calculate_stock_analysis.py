import logging
from datetime import datetime, timedelta
from django.db import transaction, models
from dvadmin.selection.models import StockBasic, DailyMarket, Top10Floatholders, StockAnalysis, IdxTa

logger = logging.getLogger(__name__)

def calculate_stock_analysis(ts_code, trade_date):
    """
    计算单个股票的分析指标

    Args:
        ts_code: 股票代码
        trade_date: 交易日期 (YYYYMMDD格式)

    Returns:
        包含计算结果的字典，如果计算失败返回None
    """
    try:
        # 1. 计算筹码集中度90%
        chip_concentration_90 = calculate_chip_concentration_90(ts_code, trade_date)

        # 2. 计算前十大流通股东占比
        top10_share_ratio = calculate_top10_share_ratio(ts_code)

        # 3. 计算MACD指标
        macd, macd_zero_break = calculate_macd_indicators(ts_code, trade_date)

        return {
            'ts_code': ts_code,
            'data_date': datetime.strptime(trade_date, "%Y%m%d").date(),
            'macd': macd,
            'macd_zero_break': macd_zero_break,
            'chip_concentration_90': chip_concentration_90,
            'top10_share_ratio': top10_share_ratio,
        }

    except Exception as e:
        logger.error(f"计算股票 {ts_code} 指标失败: {str(e)}")
        return None


def calculate_chip_concentration_90(ts_code, trade_date):
    """
    计算90%筹码集中度

    Args:
        ts_code: 股票代码
        trade_date: 交易日期 (YYYYMMDD格式)

    Returns:
        筹码集中度百分比，如果计算失败返回None
    """
    try:
        # 获取近60日历史价格和成交量数据
        end_date = datetime.strptime(trade_date, "%Y%m%d")
        start_date = (end_date - timedelta(days=90)).strftime("%Y%m%d")  # 多取一些确保有60个交易日

        df = DailyMarket.objects.filter(
            ts_code=ts_code,
            trade_date__gte=start_date,
            trade_date__lte=trade_date
        ).order_by('trade_date').values('close', 'vol', 'amount')

        if not df:
            return None

        # 转换为DataFrame-like结构进行计算
        data = []
        for item in df:
            if item['close'] and item['vol'] and item['amount']:
                # 成交额近似权重 (amount已经是成交额，单位：千元)
                amount_ratio = item['amount']
                data.append({
                    'close': item['close'],
                    'amount_ratio': amount_ratio
                })

        if len(data) < 30:  # 至少需要30天的数据
            return None

        # 按收盘价分布计算累计占比
        price_groups = {}
        for item in data:
            price = item['close']
            amount = item['amount_ratio']
            if price not in price_groups:
                price_groups[price] = 0
            price_groups[price] += amount

        # 排序并计算累计占比
        sorted_prices = sorted(price_groups.items())  # 按价格升序
        total_amount = sum(amount for _, amount in sorted_prices)

        if total_amount == 0:
            return None

        cumulative = 0
        concentration_count = 0

        for price, amount in sorted_prices:
            cumulative += amount
            if cumulative <= total_amount * 0.9:  # 达到90%
                concentration_count += 1
            else:
                break

        # 计算集中度百分比
        concentration_90 = (concentration_count / len(sorted_prices)) * 100 if sorted_prices else None

        return concentration_90

    except Exception as e:
        logger.error(f"计算筹码集中度失败 {ts_code}: {str(e)}")
        return None


def calculate_top10_share_ratio(ts_code):
    """
    计算前十大流通股东合计占流通盘比例

    Args:
        ts_code: 股票代码

    Returns:
        前十大流通股东占比，如果计算失败返回None
    """
    try:
        # 获取最新报告期的数据
        latest_record = Top10Floatholders.objects.filter(
            ts_code=ts_code
        ).aggregate(latest_end_date=models.Max('end_date'))

        if not latest_record['latest_end_date']:
            return None

        latest_end_date = latest_record['latest_end_date']

        # 获取该报告期前十大流通股东数据
        top10_data = Top10Floatholders.objects.filter(
            ts_code=ts_code,
            end_date=latest_end_date
        ).order_by('-hold_float_ratio')[:10].values_list('hold_float_ratio', flat=True)

        if not top10_data:
            return None

        # 过滤掉None值并求和
        valid_ratios = [ratio for ratio in top10_data if ratio is not None]
        if not valid_ratios:
            return None

        total_ratio = sum(valid_ratios)

        return total_ratio

    except Exception as e:
        logger.error(f"计算前十大股东占比失败 {ts_code}: {str(e)}")
        return None


def calculate_macd_indicators(ts_code, trade_date):
    """
    计算MACD指标

    Args:
        ts_code: 股票代码
        trade_date: 交易日期 (YYYYMMDD格式)

    Returns:
        (macd, macd_zero_break) 元组
    """
    try:
        date_obj = datetime.strptime(trade_date, "%Y%m%d")

        # MACD金叉计算 - 需要最近2天的数据
        macd2_start_date = (date_obj - timedelta(days=10)).strftime("%Y%m%d")

        macd_data = IdxTa.objects.filter(
            ts_code=ts_code,
            trade_date__gte=macd2_start_date,
            trade_date__lte=trade_date
        ).order_by('-trade_date').values_list('macd_val', flat=True)[:2]

        # 计算MACD金叉 (macd)
        macd = False
        if len(macd_data) >= 2 and macd_data[0] is not None and macd_data[1] is not None:
            macd = (macd_data[0] > 0 and macd_data[1] <= 0)

        # 突破过0轴计算 - 需要近30天的数据
        macd1_start_date = (date_obj - timedelta(days=30)).strftime("%Y%m%d")

        macd_history = IdxTa.objects.filter(
            ts_code=ts_code,
            trade_date__gte=macd1_start_date,
            trade_date__lte=trade_date
        ).values_list('macd_val', flat=True)

        # 计算突破过0轴 (macd_zero_break)
        macd_zero_break = False
        valid_vals = [val for val in macd_history if val is not None]
        if len(valid_vals) >= 2:
            has_below_zero = any(val <= 0 for val in valid_vals)
            has_above_zero = any(val > 0 for val in valid_vals)
            macd_zero_break = has_below_zero and has_above_zero

        return macd, macd_zero_break

    except Exception as e:
        logger.error(f"计算MACD指标失败 {ts_code}: {str(e)}")
        return False, False