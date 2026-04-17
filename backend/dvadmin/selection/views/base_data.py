from rest_framework.views import APIView
from rest_framework.response import Response

import traceback

from dvadmin.selection.services.base_data import get_base_selection_data


class BaseSelectionDataView(APIView):
    """
    返回基础数据:
    - 最新交易日
    - 行业列表
    - 股票代码列表
    """

    def get(self, request):
        try:
            params = request.query_params

            # 读取参数
            type = params.get("type")

            # 根据参数获取基础信息
            data = get_base_selection_data(type)

            return Response({"code": 2000, "msg": "查询成功", "data": data})

        except Exception as e:
            traceback.print_exc()
            return Response({"code": 4000, "msg": str(e), "data": None})