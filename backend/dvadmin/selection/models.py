from django.db import models
from dvadmin.utils.models import CoreModel


class StockBasic(models.Model):
    ts_code = models.CharField(max_length=255, primary_key=True)
    symbol = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)
    area = models.CharField(max_length=255, null=True)
    industry = models.CharField(max_length=255, null=True)
    cnspell = models.CharField(max_length=255, null=True)
    market = models.CharField(max_length=255, null=True)
    list_date = models.CharField(max_length=255, null=True)
    act_name = models.CharField(max_length=255, null=True)
    act_ent_type = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'stock_basic'
        managed = False
        verbose_name = "股票基本信息"


class DailyMarket(models.Model):
    ts_code = models.CharField(max_length=255, primary_key=True)
    trade_date = models.CharField(max_length=255)
    open = models.FloatField(null=True)
    high = models.FloatField(null=True)
    low = models.FloatField(null=True)
    close = models.FloatField(null=True)
    pre_close = models.FloatField(null=True)
    change = models.FloatField(null=True)
    pct_chg = models.FloatField(null=True)
    vol = models.FloatField(null=True)
    amount = models.FloatField(null=True)

    class Meta:
        db_table = 'daily_market'
        managed = False
        unique_together = (('ts_code', 'trade_date'),)
        verbose_name = "每日行情"


class DailyBasic(models.Model):
    ts_code = models.CharField(max_length=10, primary_key=True, db_index=True)
    trade_date = models.CharField(max_length=8, db_index=True)

    close = models.FloatField(null=True)
    turnover_rate = models.FloatField(null=True)
    turnover_rate_f = models.FloatField(null=True)
    volume_ratio = models.FloatField(null=True)
    pe = models.FloatField(null=True)
    pe_ttm = models.FloatField(null=True)
    pb = models.FloatField(null=True)
    ps = models.FloatField(null=True)
    ps_ttm = models.FloatField(null=True)
    dv_ratio = models.FloatField(null=True)
    dv_ttm = models.FloatField(null=True)
    total_share = models.FloatField(null=True)
    float_share = models.FloatField(null=True)
    free_share = models.FloatField(null=True)
    total_mv = models.FloatField(null=True)
    circ_mv = models.FloatField(null=True)

    class Meta:
        db_table = 'daily_basic'
        managed = False
        unique_together = (('ts_code', 'trade_date'),)
        verbose_name = "每日指标"


class Top10Floatholders(models.Model):
    ts_code = models.CharField(max_length=10, primary_key=True, db_index=True)
    end_date = models.CharField(max_length=10, db_index=True)
    ann_date = models.CharField(max_length=10, null=True)
    holder_name = models.CharField(max_length=200, null=True)
    holder_type = models.CharField(max_length=50, null=True)
    hold_amount = models.FloatField(null=True)
    hold_ratio = models.FloatField(null=True)
    hold_float_ratio = models.FloatField(null=True)
    hold_change = models.FloatField(null=True)

    class Meta:
        db_table = 'top10_floatholders'
        managed = False
        unique_together = (('ts_code', 'end_date'),)
        verbose_name = "十大流通股东"


class SwIndustry(models.Model):
    index_code = models.CharField(max_length=20, primary_key=True)
    industry_code = models.CharField(max_length=20, null=True)
    industry_name = models.CharField(max_length=100, null=True)
    level = models.CharField(max_length=5, null=True)
    parent_code = models.CharField(max_length=20, null=True)
    src = models.CharField(max_length=20, null=True)

    class Meta:
        db_table = 'sw_industry'
        managed = False
        verbose_name = "申万行业"


class Industry(models.Model):
    # django 模型必须要有一个主键，否则会报错
    VC_INDUSTRY_CODE1 = models.CharField(max_length=255, primary_key=True)
    VC_INDUSTRY_NAME1 = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_CODE2 = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_NAME2 = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_CODE3 = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_NAME3 = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_CODE4 = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_NAME4 = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_CODE5 = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_NAME5 = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_CODE6 = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_NAME6 = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_TYPE = models.CharField(max_length=255, null=True)
    VC_SOURCE = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = "industry"
        managed = False
        verbose_name = "行业分类"


class StockIndustry(models.Model):
    # django 模型必须要有一个主键，否则会报错
    VC_INDUSTRY_CODE = models.CharField(max_length=255, primary_key=True)
    VC_INDUSTRY_NAME = models.CharField(max_length=255, null=True)
    VC_SYMBOL_ID = models.CharField(max_length=255, null=True)
    VC_SYMBOL = models.CharField(max_length=255, null=True)
    VC_NAME = models.CharField(max_length=255, null=True)
    D_BEGIN_DATE = models.CharField(max_length=255, null=True)
    D_END_DATE = models.CharField(max_length=255, null=True)
    VC_COMPANY_CODE = models.CharField(max_length=255, null=True)
    VC_EXCHANGE = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_TYPE = models.CharField(max_length=255, null=True)
    VC_SOURCE = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_CODE_1 = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_NAME_1 = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_CODE_2 = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_NAME_2 = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_CODE_3 = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_NAME_3 = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_CODE_4 = models.CharField(max_length=255, null=True)
    VC_INDUSTRY_NAME_4 = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = "stock_industry"
        managed = False
        verbose_name = "股票行业"


class IdxShares(models.Model):
    ts_code = models.CharField(max_length=10, primary_key=True, db_index=True)
    end_date = models.CharField(max_length=10, db_index=True)
    top10holder_float_ratio = models.FloatField(null=True)

    class Meta:
        db_table = 'idx_shares'
        managed = False
        unique_together = (('ts_code', 'end_date'),)
        verbose_name = "指数持股占比"


class IdxTa(models.Model):
    ts_code = models.CharField(max_length=20, primary_key=True)
    trade_date = models.CharField(max_length=8)
    ema12 = models.FloatField(null=True)
    ema26 = models.FloatField(null=True)
    dif = models.FloatField(null=True)
    dea = models.FloatField(null=True)
    macd_val = models.FloatField(null=True)
    # 20251212发现数据库字段名称修改，同步修改，保持原变量名称
    d5_vol_avg = models.FloatField(null=True, db_column='5d_amount_avg') # 将 5d_vol_avg 转换为合法的 Python 变量名

    class Meta:
        db_table = 'idx_ta'
        managed = False
        unique_together = (('ts_code', 'trade_date'),)
        verbose_name = "指数技术指标"


class StockAnalysis(models.Model):
    ts_code = models.CharField(max_length=20)
    data_date = models.DateField()
    macd = models.BooleanField()
    macd_zero_break = models.BooleanField()
    chip_concentration_90 = models.FloatField(null=True)
    top10_share_ratio = models.FloatField(null=True)

    class Meta:
        db_table = 'stock_analysis'
        managed = False
        unique_together = (('ts_code', 'data_date'),)
        verbose_name = "股票分析"

    def __str__(self):
        return f"{self.ts_code} - {self.data_date}"


class UserStockWatch(models.Model):
    user_id = models.CharField(max_length=255, db_index=True, verbose_name="用户ID")
    ts_code = models.CharField(max_length=255, db_index=True, verbose_name="股票ID", db_column="ts_code")
    name = models.CharField(max_length=255, null=True, verbose_name="股票名称", db_column="name")
    symbol = models.CharField(max_length=255, null=True, verbose_name="股票代码", db_column="symbol")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'user_stock_watch'
        managed = False
        verbose_name = "用户关注股票"
        verbose_name_plural = verbose_name


class AIAnalysisHistory(CoreModel):
    symbol = models.CharField(max_length=255, verbose_name="标的代码")
    resolution = models.CharField(max_length=10, verbose_name="分析周期")
    prompt = models.TextField(verbose_name="提示词内容")
    report = models.TextField(verbose_name="分析报告内容")
    model = models.CharField(max_length=100, verbose_name="所用模型", null=True, blank=True)
    prompt_tokens = models.IntegerField(null=True, verbose_name="输入Token")
    completion_tokens = models.IntegerField(null=True, verbose_name="输出Token")
    total_tokens = models.IntegerField(null=True, verbose_name="总Token")

    class Meta:
        db_table = 'ai_analysis_history'
        verbose_name = "AI分析历史"
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']

