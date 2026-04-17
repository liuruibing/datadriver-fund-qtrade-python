import logging
from datetime import datetime, timedelta
from django.db import transaction, models

from application.celery import app
from dvadmin.selection.models import StockBasic, StockAnalysis

# 调用的任务服务
from dvadmin.selection.task_services.calculate_stock_analysis import calculate_stock_analysis
from dvadmin.selection.task_services.sync_daily_cron import main as run_sync_daily

logger = logging.getLogger(__name__)


@app.task
def task__daily_stock_selection(*args, **kwargs):
    """
    每日股票筛选定时任务
    可以在这里执行每日的股票筛选逻辑
    """
    try:
        logger.info("开始执行每日股票筛选任务")
        
        # 获取今天的日期
        today = datetime.now().strftime("%Y-%m-%d")

        
        logger.info("每日股票筛选任务执行完成")
        return {"status": "success", "message": "任务执行成功"}
        
    except Exception as e:
        logger.error(f"每日股票筛选任务执行失败: {str(e)}", exc_info=True)
        raise


@app.task
def task__stock_data_sync(*args, **kwargs):
    """
    股票数据同步定时任务
    可以在这里执行数据同步、更新等操作
    """
    try:
        logger.info("开始执行股票数据同步任务")
        
        logger.info("股票数据同步任务执行完成")
        return {"status": "success", "message": "数据同步成功"}
        
    except Exception as e:
        logger.error(f"股票数据同步任务执行失败: {str(e)}", exc_info=True)
        raise


@app.task
def task__daily_stock_analysis(*args, **kwargs):
    """
    每日股票分析指标计算任务
    计算所有股票的MACD、筹码集中度、前十大流通股东占比等指标
    """
    try:
        logger.info("开始执行每日股票分析计算任务")

        # 获取传入的日期，如果没有就用今天
        trade_date = kwargs.get("date")
        if not trade_date:
            trade_date = datetime.now().strftime("%Y%m%d")

        # 获取所有股票代码
        all_stocks = StockBasic.objects.values_list('ts_code', flat=True)

        if not all_stocks:
            logger.warning("未找到任何股票数据")
            return {"status": "success", "message": "无股票数据可处理"}

        # 批量计算所有股票的指标
        analysis_data = []

        for ts_code in all_stocks:
            try:
                stock_analysis = calculate_stock_analysis(ts_code, trade_date)
                if stock_analysis:
                    analysis_data.append(stock_analysis)
            except Exception as e:
                logger.error(f"计算股票 {ts_code} 分析指标失败: {str(e)}")
                continue

        # 批量插入或更新数据，支持联合主键
        if analysis_data:
            with transaction.atomic():
                for data in analysis_data:
                    updated = StockAnalysis.objects.filter(
                        ts_code=data['ts_code'],
                        data_date=data['data_date']
                    ).update(
                        macd=data['macd'],
                        macd_zero_break=data['macd_zero_break'],
                        chip_concentration_90=data['chip_concentration_90'],
                        top10_share_ratio=data['top10_share_ratio']
                    )

                    if not updated:
                        # 如果没有更新成功，说明记录不存在，创建新记录
                        StockAnalysis.objects.create(**data)

        logger.info(f"每日股票分析计算任务执行完成，处理了 {len(analysis_data)} 只股票")
        return {"status": "success", "message": f"成功处理 {len(analysis_data)} 只股票"}

    except Exception as e:
        logger.error(f"每日股票分析计算任务执行失败: {str(e)}", exc_info=True)
        raise


# 如果需要使用重试机制，可以使用 retry_base_task_error 装饰器
# from application.celery import retry_base_task_error
#
# @retry_base_task_error()
# def your_task_with_retry():
#     # 你的任务逻辑
#     pass

@app.task
def task__sync_daily_cron(*args, **kwargs):
    """
    按天跑的同步脚本
    """
    try:
        logger.info("开始执行日常同步任务")
        # 跑数脚本的核心逻辑
        run_sync_daily()
        
        logger.info("日常同步任务执行完成")
        return {"status": "success", "message": "日常同步任务执行成功"}
    except Exception as e:
        logger.error(f"日常同步任务执行失败: {str(e)}", exc_info=True)
        raise
