import traceback

from rest_framework.decorators import action
from rest_framework.response import Response

from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.selection.services.backtest import get_kline_from_db, get_macd_backtest


class MACDBacktradeView(CustomModelViewSet):
    """
    MACD 回测接口（使用数据库数据）
    """

    queryset = []
    serializer_class = None

    @action(methods=["get"], detail=False, url_path="kline")
    def get_kline(self, request):
        try:
            ts_code = request.query_params.get("ts_code")
            start_date = request.query_params.get("start_date")
            end_date = request.query_params.get("end_date")

            if not ts_code:
                return Response({"code": 4000, "msg": "缺少 ts_code"})

            data = get_kline_from_db(ts_code, start_date, end_date)
            return Response({"code": 2000, "msg": "success", "data": data})
        except Exception as exc:  # pragma: no cover - 防御性返回错误信息
            traceback.print_exc()
            return Response({"code": 4000, "msg": str(exc)})

    @action(methods=["get"], detail=False, url_path="macd")
    def macd_backtest(self, request):
        try:
            ts_code = request.query_params.get("ts_code")
            start_date = request.query_params.get("start_date")
            end_date = request.query_params.get("end_date")

            if not ts_code:
                return Response({"code": 4000, "msg": "缺少 ts_code"})

            result = get_macd_backtest(ts_code, start_date, end_date)
            return Response({"code": 2000, "msg": "success", "data": result})
        except Exception as exc:  # pragma: no cover - 防御性返回错误信息
            traceback.print_exc()
            return Response({"code": 4000, "msg": str(exc)})
