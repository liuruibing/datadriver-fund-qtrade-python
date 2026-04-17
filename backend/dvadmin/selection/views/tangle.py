# views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from dvadmin.selection.models import DailyMarket
from dvadmin.selection.services.tangle import TangleUtils
import pandas as pd

class TangleView(viewsets.GenericViewSet):
    """
    缠分析接口
    analysis_type支持：
    - fractal: 分形
    - stroke: 笔
    - segment: 线段
    - central: 中枢
    - trade_point: 买卖点
    - all: 返回所有分析结果
    """
    @action(detail=False, methods=['get'])
    def get(self, request):
        # 1. 获取并校验请求参数
        params = {
            'ts_code': request.GET.get('ts_code'),
            'start_date': request.GET.get('start_date'),
            'end_date': request.GET.get('end_date'),
            'analysis_type': request.GET.get('analysis_type', 'all')
        }
        
        # 必选参数校验
        if not all([params['ts_code'], params['start_date'], params['end_date']]):
            return Response({
                'code': 400,
                'msg': '参数缺失（必填：ts_code/start_date/end_date）',
                'data': {}
            })
        
        # 分析类型校验
        valid_types = ['fractal', 'stroke', 'segment', 'central', 'trade_point', 'all']
        if params['analysis_type'] not in valid_types:
            return Response({
                'code': 400,
                'msg': f'analysis_type无效，支持：{valid_types}',
                'data': {}
            })
        
        try:
            # 2. 查询数据库数据并转换为DataFrame
            queryset = DailyMarket.objects.filter(
                ts_code=params['ts_code'],
                trade_date__gte=params['start_date'],
                trade_date__lte=params['end_date']
            )
            df = pd.DataFrame(list(queryset.values()))
            if df.empty:
                return Response({
                    'code': 200,
                    'msg': '暂无匹配的市场数据',
                    'data': {}
                })
            
            # 3. 逐步计算各类分析结果（依赖前置结果）
            analysis_result = {}
            
            # 3.1 计算分形（基础）
            fractal_data = TangleUtils.get_fractal_data(df)
            if params['analysis_type'] in ['fractal', 'all']:
                analysis_result['fractal'] = fractal_data
            
            # 3.2 计算笔（依赖分形）
            stroke_data = []
            if params['analysis_type'] in ['stroke', 'segment', 'central', 'trade_point', 'all']:
                stroke_data = TangleUtils.get_stroke_data(df, fractal_data)
                if params['analysis_type'] in ['stroke', 'all']:
                    analysis_result['stroke'] = stroke_data
            
            # 3.3 计算线段（依赖笔）
            segment_data = []
            if params['analysis_type'] in ['segment', 'central', 'trade_point', 'all']:
                segment_data = TangleUtils.get_segment_data(df, stroke_data)
                if params['analysis_type'] in ['segment', 'all']:
                    analysis_result['segment'] = segment_data
            
            # 3.4 计算中枢（依赖线段）
            central_data = []
            if params['analysis_type'] in ['central', 'trade_point', 'all']:
                central_data = TangleUtils.get_central_point_data(df, segment_data)
                if params['analysis_type'] in ['central', 'all']:
                    analysis_result['central'] = central_data
            
            # 3.5 计算买卖点（依赖中枢）
            trade_point_data = []
            if params['analysis_type'] in ['trade_point', 'all']:
                trade_point_data = TangleUtils.get_trade_point_data(df, central_data)
                analysis_result['trade_point'] = trade_point_data
            
            analysis_result['k'] = list(queryset.values())
            
            # 4. 返回结果
            return Response({
                'code': 200,
                'msg': '分析成功',
                'data': analysis_result,
                'request_params': params  # 返回请求参数，方便前端核对
            })
        
        except Exception as e:
            # 异常捕获与返回
            return Response({
                'code': 500,
                'msg': f'分析计算失败：{str(e)}',
                'data': {},
                'request_params': params
            })
