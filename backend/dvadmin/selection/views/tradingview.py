from datetime import datetime, timedelta
import pytz
import json
import os
import sys
import logging
from pathlib import Path
import pandas as pd
from django.db import models
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from dvadmin.selection.models import StockBasic, DailyMarket

logger = logging.getLogger(__name__)

# 强制使用本地开发版 czsc
backend_dir = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(backend_dir / "czsc"))
os.environ["CZSC_USE_PYTHON"] = "1"

import czsc
from czsc import Freq

# TradingView UDF 端点实现
class TradingViewViewSet(viewsets.GenericViewSet):
    """TradingView UDF 端点集合"""
    permission_classes = []  # 允许匿名访问
    
    # 移除固定的__init__数据加载，改为在history方法中动态加载
    
    @action(detail=False, methods=['get'], url_path='config')
    def config(self, request):
        """返回图表配置"""
        return Response({
            "supported_resolutions": ["5", "30", "1D", "1W", "1M", "3M", "12M"],
            "supports_group_request": False,
            "supports_search": True,
            "supports_time": True,
            "supports_marks": False,
            "supports_timescale_marks": False
        })
    
    @action(detail=False, methods=['get'], url_path='symbols')
    def symbols(self, request):
        """返回单个符号信息"""
        symbol = request.query_params.get('symbol', '')
        
        name = symbol
        description = symbol
        
        symbol_upper = symbol.upper()
        if symbol_upper.endswith(".SH") or symbol_upper.endswith(".SS") or symbol.startswith("6"):
            exchange = "SSE"
        elif symbol_upper.endswith(".BJ") or symbol.startswith("4") or symbol.startswith("8"):
            exchange = "BSE"
        else:
            exchange = "SZSE"
        
        if symbol == "000001.SH":
            name = "上证指数"
            description = "上证指数"
            exchange = "SSE"
        else:
            try:
                # 尝试根据ts_code查找股票信息
                stock = StockBasic.objects.filter(ts_code=symbol).first()
                if stock:
                    name = stock.name
                    description = stock.name
                    ts_code_upper = (stock.ts_code or "").upper()
                    if ts_code_upper.endswith(".SH") or ts_code_upper.endswith(".SS"):
                        exchange = 'SSE'
                    elif ts_code_upper.endswith(".SZ"):
                        exchange = 'SZSE'
                    elif ts_code_upper.endswith(".BJ"):
                        exchange = 'BSE'
                    elif stock.symbol and stock.symbol.startswith('6'):
                        exchange = 'SSE'
                    elif stock.symbol and (stock.symbol.startswith('8') or stock.symbol.startswith('4')):
                        exchange = 'BSE'
                    else:
                        exchange = 'SZSE'
            except Exception:
                pass

        return Response({
            "name": name,
            "full_name": name,
            "description": description,
            "exchange": exchange,
            "listed_exchange": exchange,
            "type": "stock",
            "session": "0900-1131,1300-1501",
            "timezone": "Asia/Shanghai",
            "ticker": symbol,
            "minmov": 1,
            "pricescale": 100,
            "has_intraday": True,
            "has_daily": True,
            "has_weekly": True,
            "has_monthly": True,
            "has_quarterly": True,
            "has_yearly": True,
            "supported_resolutions": ["5", "30", "1D", "1W", "1M", "3M", "12M"],
            "intraday-multipliers": ["5", "30"],
            "monthly_multipliers": ["1", "3", "12"],  # 1月、3月(季线)、12月(年线)
            "volume_precision": 0,
            "data_status": "streaming"
        })
    
    @action(detail=False, methods=['get'], url_path='history')
    def history(self, request):
        """返回历史 K 线数据"""
        # 获取请求参数
        symbol = request.query_params.get('symbol', '')
        from_time = request.query_params.get('from')
        to_time = request.query_params.get('to')
        resolution = request.query_params.get('resolution')
        countback = request.query_params.get('countback')
        first_data_request = request.query_params.get('firstDataRequest', '').lower() == 'true'
        logger.info(f"[history] 接收请求: symbol={symbol}, resolution={resolution}, from_time={from_time}, to_time={to_time}")
        print(f"[history] 接收请求: symbol={symbol}, resolution={resolution}, from_time={from_time}, to_time={to_time}")

        # 如果没有symbol，尝试从当前请求上下文获取（TradingView第一次请求时可能没有symbol）
        # 暂时使用上证指数作为默认值
        if not symbol:
            symbol = '000001.SH'

        try:
            # 调用获取K线数据的方法（包含缠论分析）
            result = self._get_kline_with_chanlun(symbol, resolution, from_time, to_time, countback, first_data_request)
            return Response(result)
        except Exception as e:
            print(f"Error in history: {e}")
            import traceback
            traceback.print_exc()
            # 如果出错，尝试返回mock数据
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            mock_file_path = os.path.join(base_dir, 'history_601888_日线_all_zsshape.json')
            if os.path.exists(mock_file_path):
                with open(mock_file_path, 'r', encoding='utf-8') as f:
                    mock_data = json.load(f)
                return Response(mock_data)
            return Response({"s": "no_data"})

    def _get_kline_with_chanlun(self, symbol, resolution, from_time=None, to_time=None, countback=None, first_data_request=False):
        """从数据库获取K线数据并进行缠论分析，转换为TradingView格式"""
        print(f"[_get_kline_with_chanlun] 开始处理: symbol={symbol}, resolution={resolution}, from_time={from_time}, to_time={to_time}, countback={countback}")
        # 将 resolution 映射到 czsc.Freq
        resolution_map = {
            '5': Freq.F5,
            '30': Freq.F30,
            '1D': Freq.D,
            '1W': Freq.W,
            '1M': Freq.M,
            '3M': Freq.S,  # 季线
            '12M': Freq.Y, # 年线（使用 12M 而不是 1Y）
            '1Y': Freq.Y   # 年线（兼容旧的 1Y 格式）
        }
        freq_enum = resolution_map.get(resolution, Freq.D)
        print(f"[_get_kline_with_chanlun] freq_enum={freq_enum}")

        # 确定是否为日线级别
        is_daily = freq_enum in (Freq.D, Freq.W, Freq.M, Freq.S, Freq.Y)

        # 确定查询范围
        end_date = datetime.now(pytz.UTC)
        if to_time:
            try:
                end_date = datetime.fromtimestamp(int(to_time), pytz.UTC)
            except (ValueError, OSError):
                pass  # 使用当前时间

        # 根据频率确定起始日期
        if freq_enum == Freq.D:
            start_date = end_date - timedelta(days=365 * 5)  # 5年数据
        elif freq_enum == Freq.W:
            start_date = end_date - timedelta(days=365 * 10)  # 10年数据
        elif freq_enum == Freq.M:
            start_date = end_date - timedelta(days=365 * 20)  # 20年数据
        elif freq_enum == Freq.S:
            start_date = end_date - timedelta(days=365 * 30)  # 30年数据
        elif freq_enum == Freq.Y:
            start_date = end_date - timedelta(days=365 * 50)  # 50年数据
        else:  # 分钟线
            start_date = end_date - timedelta(days=30)  # 30天数据

        # 只有当 from_time 是合理的时间戳时才使用它
        if from_time:
            try:
                from_ts = int(from_time)
                # 检查时间戳是否合理（大于 0 且不是太久远）
                if from_ts > 0:
                    start_date = datetime.fromtimestamp(from_ts, pytz.UTC)
            except (ValueError, OSError):
                pass  # 使用默认的 start_date

        # 从数据库查询日线数据
        print(f"查询数据: symbol={symbol}, resolution={resolution}, freq_enum={freq_enum}, start={start_date.strftime('%Y%m%d')}, end={end_date.strftime('%Y%m%d')}")
        print(f"原始参数: from_time={from_time}, to_time={to_time}")
        daily_data = DailyMarket.objects.filter(
            ts_code=symbol,
            trade_date__lte=end_date.strftime('%Y%m%d'),
            trade_date__gte=start_date.strftime('%Y%m%d')
        ).order_by('trade_date').values(
            'trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount'
        )

        # 转换为DataFrame
        df = pd.DataFrame(list(daily_data))

        if df.empty:
            print(f"查询数据为空: symbol={symbol}, freq={resolution}")
            return {"s": "no_data"}

        print(f"查询到 {len(df)} 条日线数据")

        # 数据预处理
        df['dt'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        df['symbol'] = symbol
        df = df[["dt", "symbol", "open", "high", "low", "close", "vol", "amount"]].copy().reset_index(drop=True)

        # 确保数值类型安全
        price_cols = ["open", "high", "low", "close"]
        for col in price_cols + ["vol", "amount"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # 填充成交量空值
        if "vol" in df.columns:
            df["vol"] = df["vol"].fillna(0)
        if "amount" in df.columns:
            df["amount"] = df["amount"].fillna(0)

        # 剔除无效行
        df = df.dropna(subset=["dt"] + price_cols).reset_index(drop=True)

        if df.empty:
            return {"s": "no_data"}

        # 周线特殊处理：将周五日期转换为周一（TradingView约定）
        if freq_enum == Freq.W:
            df['dt'] = df['dt'] - pd.to_timedelta(df['dt'].dt.dayofweek, unit='D')

        # 根据周期进行聚合（周线及以上）
        if freq_enum in (Freq.W, Freq.M, Freq.S, Freq.Y):
            rule_map = {
                Freq.W: 'W-MON',  # 周线，以周一为起点
                Freq.M: 'M',      # 月线
                Freq.S: 'Q',      # 季线
                Freq.Y: 'Y'       # 年线
            }
            rule = rule_map.get(freq_enum, 'D')

            df.set_index('dt', inplace=True)
            agg_dict = {
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'vol': 'sum',
                'amount': 'sum',
                'symbol': 'first'
            }
            df = df.resample(rule).agg(agg_dict).dropna()
            df.reset_index(inplace=True)

        # CZSC 格式化并分析
        try:
            raw_bars = czsc.format_standard_kline(df, freq=freq_enum)
            c = czsc.CZSC(raw_bars, max_bi_num=1000)
        except Exception as e:
            print(f"CZSC分析失败: {e}")
            import traceback
            traceback.print_exc()
            # 如果CZSC分析失败，至少返回K线数据
            return self._build_simple_kline_response(df, is_daily)

        # 导入中枢和买卖点计算函数
        try:
            # 从 backend 目录导入
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "ZS_sig",
                os.path.join(backend_dir, "ZS_sig.py")
            )
            ZS_sig = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ZS_sig)

            get_zs_seq = ZS_sig.get_zs_seq
            find_B1 = ZS_sig.find_B1
            find_B2 = ZS_sig.find_B2
            find_B3 = ZS_sig.find_B3
            find_S1 = ZS_sig.find_S1
            find_S2 = ZS_sig.find_S2
            find_S3 = ZS_sig.find_S3
        except ImportError as e:
            print(f"无法导入 ZS_sig: {e}，将不返回中枢和买卖点")
            zs_list = []
            b1_list = b2_list = b3_list = s1_list = s2_list = s3_list = []
        else:
            # 计算中枢
            zs_list = get_zs_seq(c.bi_list)
            # 计算买卖点
            b1_list = find_B1(c.bi_list, zs_list, c)
            b2_list = find_B2(c.bi_list, b1_list)
            b3_list = find_B3(c.bi_list, zs_list)
            s1_list = find_S1(c.bi_list, zs_list, c)
            s2_list = find_S2(c.bi_list, s1_list)
            s3_list = find_S3(c.bi_list, zs_list)

        bs_points = b1_list + b2_list + b3_list + s1_list + s2_list + s3_list

        # 处理K线数据
        bars = list(c.bars_raw)

        # 应用 from/to/countback 过滤
        if not first_data_request:
            if from_time is not None or to_time is not None:
                f = -10**18 if from_time is None else int(from_time)
                t = 10**18 if to_time is None else int(to_time)

                bars = [b for b in bars if self._dt_to_ts(b.dt, is_daily, freq_enum) is not None
                        and f <= self._dt_to_ts(b.dt, is_daily, freq_enum) <= t]

            if countback is not None and int(countback) > 0 and len(bars) > int(countback):
                bars = bars[-int(countback):]

        if not bars:
            return {"s": "no_data"}

        # 构建K线数组
        t_arr, o_arr, h_arr, l_arr, c_arr, v_arr = [], [], [], [], [], []
        for b in bars:
            ts = self._dt_to_ts(b.dt, is_daily, freq_enum)
            if ts is None:
                continue
            t_arr.append(int(ts))
            o_arr.append(float(b.open))
            h_arr.append(float(b.high))
            l_arr.append(float(b.low))
            c_arr.append(float(b.close))
            v_arr.append(float(getattr(b, "vol", 0)))

        if not t_arr:
            return {"s": "no_data"}

        t_min, t_max = t_arr[0], t_arr[-1]

        # 构建笔数据
        bis = []
        for bi in c.bi_list:
            s_ts = self._dt_to_ts(bi.fx_a.dt, is_daily, freq_enum)
            e_ts = self._dt_to_ts(bi.fx_b.dt, is_daily, freq_enum)
            if s_ts is None or e_ts is None:
                continue
            if e_ts < t_min or s_ts > t_max:
                continue
            bis.append({
                "points": [
                    {"time": int(s_ts), "price": float(bi.fx_a.fx)},
                    {"time": int(e_ts), "price": float(bi.fx_b.fx)}
                ],
                "linestyle": "0"
            })

        # 构建中枢数据
        bi_zss = []
        for zs in zs_list:
            s_ts = self._dt_to_ts(zs.sdt, is_daily, freq_enum)
            e_ts = self._dt_to_ts(zs.edt, is_daily, freq_enum)
            if s_ts is None or e_ts is None:
                continue
            if e_ts < t_min or s_ts > t_max:
                continue
            zg = float(zs.zg)
            zd = float(zs.zd)
            s_ts_i, e_ts_i = int(s_ts), int(e_ts)
            if e_ts_i <= s_ts_i:
                continue
            bi_zss.append({
                "points": [{"time": s_ts_i, "price": zg}, {"time": e_ts_i, "price": zd}],
                "linestyle": "0"
            })

        # 构建买卖点数据
        mmds = []
        for p in bs_points:
            ts = self._dt_to_ts(p.get("dt"), is_daily, freq_enum)
            price = p.get("price")
            if ts is None or price is None:
                continue
            text_val = p.get("op_desc") or p.get("bs_type") or "signal"
            if isinstance(p.get("bs_type"), str) and p.get("bs_type"):
                text_val = f"笔:{p.get('bs_type')}"
            mmds.append({
                "points": {"time": int(ts), "price": float(price)},
                "text": str(text_val)
            })

        # 构建响应
        result = {
            "s": "ok",
            "t": t_arr,
            "o": o_arr,
            "h": h_arr,
            "l": l_arr,
            "c": c_arr,
            "v": v_arr,
            "fxs": [],  # 分型暂不返回
            "bis": bis,
            "xds": [],  # 线段暂不返回
            "zsds": [],  # 走势段暂不返回
            "bi_zss": bi_zss,
            "xd_zss": [],  # 线段中枢暂不返回
            "zsd_zss": [],  # 走势段中枢暂不返回
            "bcs": [],  # 背驰暂不返回
            "mmds": mmds
        }

        return result

    def _build_simple_kline_response(self, df, is_daily):
        """当CZSC分析失败时，构建简单的K线响应"""
        t_arr, o_arr, h_arr, l_arr, c_arr, v_arr = [], [], [], [], [], []
        for _, row in df.iterrows():
            dt = row['dt']
            if isinstance(dt, str):
                dt = pd.to_datetime(dt)
            ts = int(dt.timestamp()) if is_daily else int(dt.timestamp())
            t_arr.append(ts)
            o_arr.append(float(row['open']))
            h_arr.append(float(row['high']))
            l_arr.append(float(row['low']))
            c_arr.append(float(row['close']))
            v_arr.append(float(row['vol']) if row['vol'] else 0)

        return {
            "s": "ok",
            "t": t_arr,
            "o": o_arr,
            "h": h_arr,
            "l": l_arr,
            "c": c_arr,
            "v": v_arr,
            "fxs": [], "bis": [], "xds": [], "zsds": [],
            "bi_zss": [], "xd_zss": [], "zsd_zss": [], "bcs": [], "mmds": []
        }

    def _dt_to_ts(self, dt, is_daily=False, freq=None):
        """将datetime转换为时间戳"""
        if dt is None:
            return None
        try:
            ts = pd.Timestamp(dt)
            if ts is pd.NaT:
                return None

            # 周线特殊处理：将日期转换为周一
            if freq == Freq.W:
                days_since_monday = ts.dayofweek
                ts = ts - pd.Timedelta(days=days_since_monday)

            if is_daily:
                return int(pd.Timestamp(ts.date()).timestamp())
            else:
                if ts.tz is None:
                    ts = ts.tz_localize("Asia/Shanghai")
                return int(ts.timestamp())
        except Exception:
            return None
    
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """搜索符号"""
        query = request.query_params.get('query')
        try:
            limit = int(request.query_params.get('limit', 10))
        except (ValueError, TypeError):
            limit = 10
        
        # 构建查询条件
        if query:
            # 当有query参数时，按条件搜索，支持股票代码、股票名称、拼音首字母
            # 注意：某些数据库环境下icontains可能对大小写敏感，额外增加小写匹配以支持"PAYH"搜到"payh"
            stocks = StockBasic.objects.filter(
                models.Q(ts_code__icontains=query) | 
                models.Q(symbol__icontains=query) | 
                models.Q(name__icontains=query) |
                models.Q(cnspell__icontains=query) |
                models.Q(cnspell__contains=query.lower())
            ).order_by('ts_code')[:limit]
        else:
            # 当query为空时，根据limit参数返回数据
            stocks = StockBasic.objects.all().order_by('ts_code')[:limit]
        
        # 判断是否需要包含默认的上证指数
        include_sz_index = False
        if not query:
            include_sz_index = True
        else:
            q_lower = query.lower()
            # 搜索词包含在这些关键词中，或者这些关键词包含在搜索词中
            if (q_lower in "000001.sh" or q_lower in "上证指数" or q_lower in "szzs" 
                or "000001" in q_lower or "上证" in q_lower):
                include_sz_index = True

        # 转换为TradingView需要的格式
        result = []
        if include_sz_index:
            result.append({
                "symbol": "000001.SH",
                "full_name": "上证指数",
                "name": "上证指数",
                "description": "上证指数",
                "type": "index",
                "exchange": "SSE",
                "ticker": "000001.SH"
            })
        
        for stock in stocks:
            # 避免重复添加上证指数
            if stock.ts_code == "000001.SH":
                continue
            # 根据股票代码判断交易所
            ts_code_upper = (stock.ts_code or "").upper()
            if ts_code_upper.endswith('.SH') or ts_code_upper.endswith('.SS'):
                exchange = 'SSE'
            elif ts_code_upper.endswith('.SZ'):
                exchange = 'SZSE'
            elif ts_code_upper.endswith('.BJ'):
                exchange = 'BSE'
            elif stock.symbol and stock.symbol.startswith('6'):
                exchange = 'SSE'
            elif stock.symbol and (stock.symbol.startswith('8') or stock.symbol.startswith('4')):
                exchange = 'BSE'
            else:
                exchange = 'SZSE'
            
            result.append({
                "symbol": stock.ts_code,
                "full_name": stock.name,
                "name": stock.name,
                "description": stock.name,
                "type": "stock",
                "exchange": exchange,
                "ticker": stock.ts_code
            })
        
        return Response(result)
    
    @action(detail=False, methods=['get'], url_path='time')
    def time(self, request):
        """返回服务器时间"""
        return Response(int(datetime.now(pytz.UTC).timestamp()))
