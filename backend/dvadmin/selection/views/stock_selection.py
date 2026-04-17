import re

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

import traceback

from dvadmin.selection.models import StockBasic
from dvadmin.selection.serializers.stock_basic import StockBasicSerializer
from dvadmin.selection.services.stock_selection import filter_stock_features, filter_stock_features_refined
from dvadmin.selection.services.stock_info import get_stock_quote


class StockSelectionViewSet(viewsets.GenericViewSet):
    """
    股票筛选接口

    - POST filter: 根据多条件筛选股票基础信息（初步筛选）
    - POST refined_filter: 二次筛选（精筛），包含初步筛选的所有参数，以及chip2、macd1、macd2参数
    """
    queryset = StockBasic.objects.all()
    serializer_class = StockBasicSerializer

    @staticmethod
    def _extract_symbol_ids(request) -> list[str]:
        """
        从请求中提取 symbolId 参数，兼容三种前端传参格式：

        1. axios 数组格式: symbolId[0]=xx&symbolId[1]=xx（URL 编码为 symbolId%5B0%5D=xx）
        2. 重复参数格式:   symbolId=xx&symbolId=yy
        3. 逗号分隔字符串: symbolId=xx,yy,zz（或 POST body 中的 JSON）

        Returns:
            去重后的股票代码列表
        """
        codes: list[str] = []

        # NOTE: 优先从 POST body（JSON）获取，可能是字符串或列表
        body_val = request.data.get("symbolId")
        if body_val:
            if isinstance(body_val, list):
                codes.extend(body_val)
            elif isinstance(body_val, str):
                codes.extend(body_val.split(","))

        if codes:
            return [c.strip() for c in codes if c.strip()]

        # 尝试 axios 数组格式: symbolId[0], symbolId[1], ...
        params = request.query_params
        indexed_items: list[tuple[int, str]] = []
        for key in params:
            match = re.match(r'^symbolId\[(\d+)]$', key)
            if match:
                indexed_items.append((int(match.group(1)), params[key]))

        if indexed_items:
            # 按索引排序以保持前端传入的顺序
            indexed_items.sort(key=lambda x: x[0])
            return [v.strip() for _, v in indexed_items if v.strip()]

        # 尝试重复参数格式: symbolId=xx&symbolId=yy
        multi = params.getlist("symbolId")
        if multi:
            return [c.strip() for c in multi if c.strip()]

        # 尝试逗号分隔字符串: symbolId=xx,yy,zz
        single = params.get("symbolId", "")
        if single:
            return [c.strip() for c in single.split(",") if c.strip()]

        return []


    @action(detail=False, methods=['post'])
    def filter(self, request):
        """
        筛选股票信息:
        - search      模糊搜索 ts_code / 名称
        - industry    行业
        - date        数据日期(必选，用于 PE、成交额和流通市值)
        - pe_min/max  PE区间
        - vol_min/max 5日平均成交额区间
        - circ_mv_min/max 流通市值区间(单位：亿元)
        """

        try:
            params = request.data

            # 读取参数
            date = params.get("date")           # yyyy-mm-dd
            search = params.get("search")
            industry = params.get("industry")

            pe_min = params.get("pe_min")
            pe_max = params.get("pe_max")
            vol_min = params.get("vol_min")
            vol_max = params.get("vol_max")
            circ_mv_min = params.get("circ_mv_min")
            circ_mv_max = params.get("circ_mv_max")

            # 转换参数类型
            pe_min = float(pe_min) if pe_min else None
            pe_max = float(pe_max) if pe_max else None
            vol_min = float(vol_min) if vol_min else None
            vol_max = float(vol_max) if vol_max else None
            circ_mv_min = float(circ_mv_min) if circ_mv_min else None
            circ_mv_max = float(circ_mv_max) if circ_mv_max else None

            # 直接调用 service 完成筛选
            data  = filter_stock_features(
                date=date,
                search_term=search,
                pe_min=pe_min,
                pe_max=pe_max,
                amount_avg_min=vol_min,
                amount_avg_max=vol_max,
                circ_mv_min=circ_mv_min,
                circ_mv_max=circ_mv_max,
                industry=industry
            )

            return Response({"code": 2000, "msg": "查询成功", "data": data})

        except Exception as e:
            traceback.print_exc()
            return Response({"code": 4000, "msg": str(e), "data": None})

    @action(detail=False, methods=['post'])
    def refined_filter(self, request):
        """
        二次筛选（精筛）股票信息:
        包含初步筛选的所有参数:
        - search      模糊搜索 ts_code / 名称
        - industry    行业
        - date        数据日期(必选，用于 PE、成交额和流通市值)
        - pe_min/max  PE区间
        - vol_min/max 5日平均成交额区间
        - circ_mv_min/max 流通市值区间(单位：亿元)
        
        新增二次筛选参数:
        - chip2       前十大流通股东上期公告持仓占流通盘>65%，为1则筛选，可选
        - macd1       MACD特征: 突破过0轴以上反复纠缠，为1则筛选，可选
        - macd2       MACD特征: MACD金叉，为1则筛选，可选
        - macd1_days  突破过0轴计算的天数范围，默认30天，可选
        """

        try:
            params = request.data

            # 读取初步筛选参数
            date = params.get("date")           # yyyy-mm-dd
            search = params.get("search")
            industry = params.get("industry")

            pe_min = params.get("pe_min")
            pe_max = params.get("pe_max")
            vol_min = params.get("vol_min")
            vol_max = params.get("vol_max")
            circ_mv_min = params.get("circ_mv_min")
            circ_mv_max = params.get("circ_mv_max")

            # 读取二次筛选参数
            chip1 = params.get("chip1")
            chip2 = params.get("chip2")
            macd1 = params.get("macd1")
            macd2 = params.get("macd2")

            # 转换参数类型
            pe_min = float(pe_min) if pe_min else None
            pe_max = float(pe_max) if pe_max else None
            vol_min = float(vol_min) if vol_min else None
            vol_max = float(vol_max) if vol_max else None
            circ_mv_min = float(circ_mv_min) if circ_mv_min else None
            circ_mv_max = float(circ_mv_max) if circ_mv_max else None
            chip1 = int(chip1) if chip1 else None
            chip2 = int(chip2) if chip2 else None
            macd1 = int(macd1) if macd1 else None
            macd2 = int(macd2) if macd2 else None

            # 调用二次筛选服务
            data = filter_stock_features_refined(
                date=date,
                search_term=search,
                pe_min=pe_min,
                pe_max=pe_max,
                amount_avg_min=vol_min,
                amount_avg_max=vol_max,
                circ_mv_min=circ_mv_min,
                circ_mv_max=circ_mv_max,
                industry=industry,
                chip1=chip1,
                chip2=chip2,
                macd1=macd1,
                macd2=macd2
            )

            return Response({"code": 2000, "msg": "查询成功", "data": data})

        except Exception as e:
            traceback.print_exc()
            return Response({"code": 4000, "msg": str(e), "data": None})

    @action(detail=False, methods=['post'])
    def watch_stock(self, request):
        """
        我的关注接口
        接受参数:
        - mode: 'insert' 或 'remove'
        - userId: 用户ID
        - symbolId: 股票ID
        - symbolName: 股票名称
        - symbolCode: 股票代码
        """
        try:
            # 兼容从 body(JSON) 以及 url(?a=1&b=2) 两种方式获取参数
            mode = request.data.get("mode") or request.query_params.get("mode")
            user_id = request.data.get("userId") or request.query_params.get("userId")
            symbol_id = request.data.get("symbolId") or request.query_params.get("symbolId")
            symbol_name = request.data.get("symbolName") or request.query_params.get("symbolName")
            symbol_code = request.data.get("symbolCode") or request.query_params.get("symbolCode")

            if not mode or not user_id or not symbol_id or not symbol_name or not symbol_code:
                return Response({"code": 4000, "msg": "缺少必要参数", "data": None})

            # 导入模型
            from dvadmin.selection.models import UserStockWatch

            if mode == 'insert':
                UserStockWatch.objects.using('pg_db').update_or_create(
                    user_id=user_id,
                    ts_code=symbol_id,
                    defaults={
                        'name': symbol_name,
                        'symbol': symbol_code
                    }
                )
                return Response({"code": 2000, "msg": "关注成功", "data": None})
            elif mode == 'remove':
                UserStockWatch.objects.using('pg_db').filter(user_id=user_id, ts_code=symbol_id).delete()
                return Response({"code": 2000, "msg": "取消关注成功", "data": None})
            else:
                return Response({"code": 4000, "msg": "未知的mode参数", "data": None})
        except Exception as e:
            traceback.print_exc()
            return Response({"code": 4000, "msg": str(e), "data": None})

    @action(detail=False, methods=['get', 'post'])
    def watch_stock_list(self, request) -> Response:
        """
        获取用户关注列表
        接受参数:
        - userId: 用户ID
        """
        try:
            # 兼容从 body(JSON) 以及 url(?userId=...) 两种方式获取参数
            user_id = request.data.get("userId") or request.query_params.get("userId")
            
            if not user_id:
                return Response({"code": 4000, "msg": "缺少必要参数 userId", "data": None})

            # NOTE: 为了保持和原有逻辑一致，这里从模型导入以防止循环依赖，并指定数据库 pg_db
            from dvadmin.selection.models import UserStockWatch

            # 获取当前用户的关注列表，按创建时间降序
            watch_queryset = UserStockWatch.objects.using('pg_db').filter(user_id=user_id).order_by('-created_at')
            
            data = []
            for item in watch_queryset:
                data.append({
                    "symbolId": item.ts_code,
                    "symbolName": item.name,
                    "symbolCode": item.symbol,
                    "createdAt": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else None
                })
                
            return Response({"code": 2000, "msg": "查询成功", "data": data})

        except Exception as e:
            traceback.print_exc()
            return Response({"code": 4000, "msg": str(e), "data": None})

    @action(detail=False, methods=['get', 'post'])
    def stock_quote(self, request) -> Response:
        """
        获取股票的盘中实时最新价和涨跌幅，支持单只或多只批量查询

        接受参数:
        - symbolId: 股票代码（必填），支持以下传参方式：
          1. 逗号分隔字符串: symbolId="000001.SZ,600000.SH"
          2. 数组重复参数:   symbolId=000001.SZ&symbolId=600000.SH
          3. axios 数组格式: symbolId[0]=000001.SZ&symbolId[1]=600000.SH

        返回字段（列表）:
        - ts_code: 股票代码
        - close: 实时最新价
        - pct_chg: 涨跌幅(%)
        """
        try:
            ts_codes = self._extract_symbol_ids(request)

            if not ts_codes:
                return Response({"code": 4000, "msg": "缺少必要参数 symbolId", "data": None})

            ts_code_str = ",".join(ts_codes)
            data = get_stock_quote(ts_code=ts_code_str)

            if not data:
                return Response({"code": 4004, "msg": f"未获取到股票 {ts_code_str} 的实时数据", "data": None})

            return Response({"code": 2000, "msg": "查询成功", "data": data})

        except Exception as e:
            traceback.print_exc()
            return Response({"code": 4000, "msg": str(e), "data": None})

