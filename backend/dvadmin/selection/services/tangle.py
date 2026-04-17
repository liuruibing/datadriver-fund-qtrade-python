# utils.py
import pandas as pd
from typing import List, Dict

class TangleUtils:
    """股票技术分析工具类（缠论相关计算）"""

    @staticmethod
    def get_fractal_data(df: pd.DataFrame) -> List[Dict]:
        """
        计算分形（顶分形/底分形）
        顶分形：某K线最高价高于左右各2根K线的最高价
        底分形：某K线最低价低于左右各2根K线的最低价
        """
        df = df.sort_values('trade_date').reset_index(drop=True)
        fractal_list = []
        
        # 遍历K线（跳过前2根和后2根）
        for i in range(2, len(df)-2):
            current_high = df.iloc[i]['high']
            current_low = df.iloc[i]['low']
            # 顶分形判断
            if (current_high > df.iloc[i-1]['high'] and 
                current_high > df.iloc[i-2]['high'] and 
                current_high > df.iloc[i+1]['high'] and 
                current_high > df.iloc[i+2]['high']):
                fractal_list.append({
                    'trade_date': df.iloc[i]['trade_date'],
                    'type': 'top',
                    'price': current_high,
                    'ts_code': df.iloc[i]['ts_code']
                })
            # 底分形判断
            if (current_low < df.iloc[i-1]['low'] and 
                current_low < df.iloc[i-2]['low'] and 
                current_low < df.iloc[i+1]['low'] and 
                current_low < df.iloc[i+2]['low']):
                fractal_list.append({
                    'trade_date': df.iloc[i]['trade_date'],
                    'type': 'bottom',
                    'price': current_low,
                    'ts_code': df.iloc[i]['ts_code']
                })
        return fractal_list

    @staticmethod
    def get_stroke_data(df: pd.DataFrame, fractal_data: List[Dict]) -> List[Dict]:
        """
        计算笔（分形之间的有效连接，顶底交替）
        笔的成立条件：顶底分形之间至少有5根K线，且价格差满足最小波动
        """
        df = df.sort_values('trade_date').reset_index(drop=True)
        stroke_list = []
        # 按日期排序分形
        sorted_fractals = sorted(fractal_data, key=lambda x: x['trade_date'])
        
        # 遍历分形，寻找顶底交替的有效笔
        for i in range(len(sorted_fractals)-1):
            f1 = sorted_fractals[i]
            f2 = sorted_fractals[i+1]
            # 顶底交替
            if (f1['type'] == 'top' and f2['type'] == 'bottom') or (f1['type'] == 'bottom' and f2['type'] == 'top'):
                # 计算分形之间的K线数量
                f1_date_idx = df[df['trade_date'] == f1['trade_date']].index[0]
                f2_date_idx = df[df['trade_date'] == f2['trade_date']].index[0]
                k_count = abs(f2_date_idx - f1_date_idx)
                
                # 笔的成立条件：至少5根K线
                if k_count >= 5:
                    stroke_type = 'down' if f1['type'] == 'top' else 'up'
                    stroke_list.append({
                        'start_date': f1['trade_date'],
                        'end_date': f2['trade_date'],
                        'start_price': f1['price'],
                        'end_price': f2['price'],
                        'type': stroke_type,
                        'k_count': k_count,
                        'price_change': f2['price'] - f1['price'],
                        'ts_code': f1['ts_code']
                    })
        return stroke_list

    @staticmethod
    def get_segment_data(df: pd.DataFrame, stroke_data: List[Dict]) -> List[Dict]:
        """
        计算线段（由笔组成，至少3笔且方向一致）
        线段方向：向上线段（底-顶-底），向下线段（顶-底-顶）
        """
        segment_list = []
        # 按日期排序笔
        sorted_strokes = sorted(stroke_data, key=lambda x: x['start_date'])
        
        # 遍历笔，寻找3笔以上的有效线段
        for i in range(len(sorted_strokes)-2):
            p1 = sorted_strokes[i]
            p2 = sorted_strokes[i+1]
            p3 = sorted_strokes[i+2]
            
            # 向上线段：下-上-下 笔组合（底-顶-底）
            if p1['type'] == 'down' and p2['type'] == 'up' and p3['type'] == 'down':
                segment_list.append({
                    'start_date': p1['start_date'],
                    'end_date': p3['end_date'],
                    'type': 'up',
                    'start_price': p1['start_price'],
                    'end_price': p3['end_price'],
                    'stroke_count': 3,
                    'ts_code': p1['ts_code']
                })
            # 向下线段：上-下-上 笔组合（顶-底-顶）
            elif p1['type'] == 'up' and p2['type'] == 'down' and p3['type'] == 'up':
                segment_list.append({
                    'start_date': p1['start_date'],
                    'end_date': p3['end_date'],
                    'type': 'down',
                    'start_price': p1['start_price'],
                    'end_price': p3['end_price'],
                    'stroke_count': 3,
                    'ts_code': p1['ts_code']
                })
        return segment_list

    @staticmethod
    def get_central_point_data(df: pd.DataFrame, segment_data: List[Dict]) -> List[Dict]:
        """
        计算中枢（某价格区间内的多笔重叠，是买卖力量平衡的区域）
        中枢区间：重叠笔的最高价和最低价的交集
        """
        central_list = []
        # 按股票代码分组处理
        ts_codes = set([s['ts_code'] for s in segment_data])
        
        for ts_code in ts_codes:
            seg_list = [s for s in segment_data if s['ts_code'] == ts_code]
            if len(seg_list) < 3:
                continue
            
            # 计算重叠区间
            for i in range(len(seg_list)-2):
                s1, s2, s3 = seg_list[i], seg_list[i+1], seg_list[i+2]
                # 提取价格区间
                ranges = [
                    (min(s1['start_price'], s1['end_price']), max(s1['start_price'], s1['end_price'])),
                    (min(s2['start_price'], s2['end_price']), max(s2['start_price'], s2['end_price'])),
                    (min(s3['start_price'], s3['end_price']), max(s3['start_price'], s3['end_price']))
                ]
                # 计算交集
                overlap_low = max([r[0] for r in ranges])
                overlap_high = min([r[1] for r in ranges])
                
                if overlap_low < overlap_high:  # 存在有效中枢
                    central_list.append({
                        'ts_code': ts_code,
                        'start_date': min(s1['start_date'], s2['start_date'], s3['start_date']),
                        'end_date': max(s1['end_date'], s2['end_date'], s3['end_date']),
                        'central_low': overlap_low,
                        'central_high': overlap_high,
                        'central_mid': (overlap_low + overlap_high) / 2,
                        'segment_count': 3
                    })
        return central_list

    @staticmethod
    def get_trade_point_data(df: pd.DataFrame, central_data: List[Dict]) -> List[Dict]:
        """
        计算买卖点（基于中枢的突破/回踩，结合分形确认）
        买点：中枢下沿回踩不破 + 底分形；卖点：中枢上沿突破不站 + 顶分形
        """
        trade_points = []
        df = df.sort_values('trade_date').reset_index(drop=True)
        
        for central in central_data:
            ts_code = central['ts_code']
            central_low = central['central_low']
            central_high = central['central_high']
            central_dates = (central['start_date'], central['end_date'])
            
            # 筛选中枢之后的K线
            post_central_df = df[(df['ts_code'] == ts_code) & (df['trade_date'] > central_dates[1])]
            if len(post_central_df) < 3:
                continue
            
            # 遍历中枢后的K线，判断买卖点
            for idx, row in post_central_df.iterrows():
                current_price = row['close']
                # 买点判断：价格回踩中枢下沿附近（±1%）且收盘价站上，且出现底分形
                if abs(current_price - central_low) / central_low <= 0.01 and row['low'] <= central_low and row['close'] >= central_low:
                    # 检查附近是否有底分形
                    fractal_check = df[(df['ts_code'] == ts_code) & 
                                       (df['trade_date'] >= post_central_df.iloc[max(0, idx-2)]['trade_date']) &
                                       (df['trade_date'] <= post_central_df.iloc[min(len(post_central_df)-1, idx+2)]['trade_date'])]
                    if any(f['type'] == 'bottom' for f in TangleUtils.get_fractal_data(fractal_check)):
                        trade_points.append({
                            'ts_code': ts_code,
                            'trade_date': row['trade_date'],
                            'type': 'buy',
                            'price': current_price,
                            'reason': f'中枢下沿回踩确认，中枢区间[{central_low:.2f}, {central_high:.2f}]',
                            'confidence': 'high' if row['vol'] > df[df['ts_code'] == ts_code]['vol'].mean() else 'medium'
                        })
                # 卖点判断：价格突破中枢上沿附近（±1%）且收盘价回落，且出现顶分形
                elif abs(current_price - central_high) / central_high <= 0.01 and row['high'] >= central_high and row['close'] <= central_high:
                    # 检查附近是否有顶分形
                    fractal_check = df[(df['ts_code'] == ts_code) & 
                                       (df['trade_date'] >= post_central_df.iloc[max(0, idx-2)]['trade_date']) &
                                       (df['trade_date'] <= post_central_df.iloc[min(len(post_central_df)-1, idx+2)]['trade_date'])]
                    if any(f['type'] == 'top' for f in TangleUtils.get_fractal_data(fractal_check)):
                        trade_points.append({
                            'ts_code': ts_code,
                            'trade_date': row['trade_date'],
                            'type': 'sell',
                            'price': current_price,
                            'reason': f'中枢上沿突破回落，中枢区间[{central_low:.2f}, {central_high:.2f}]',
                            'confidence': 'high' if row['vol'] > df[df['ts_code'] == ts_code]['vol'].mean() else 'medium'
                        })
        return trade_points
