"""chanlun.py

TradingView 缠论 history 接口。

普通 history 接口统一使用 backend/ZS_sig.py 和 backend/BS_sig.py；
AI 分析接口单独使用 backend/ZS_sig_ai.py 的增强逻辑。
"""

from __future__ import annotations

import logging
from collections import Counter

from core.chanlun.data import aggregate_daily_kline, clean_kline_df, create_stock_kline_engine, read_stock_kline
from core.chanlun.history_response import build_history_payload
from core.chanlun.runtime import setup_local_czsc

setup_local_czsc()

import czsc
from czsc import Freq, Direction
from ..models import AIAnalysisHistory

from dvadmin.selection.services.ai_service import AIService
from rest_framework import viewsets
from rest_framework.decorators import action, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from core.chanlun.ai_algorithms import (
    calculate_xd_list as ai_calculate_xd_list,
    find_B1 as ai_find_B1,
    find_B2 as ai_find_B2,
    find_B3 as ai_find_B3,
    find_LB2 as ai_find_LB2,
    find_LS2 as ai_find_LS2,
    find_S1 as ai_find_S1,
    find_S2 as ai_find_S2,
    find_S3 as ai_find_S3,
    find_bi_bc_signals as ai_find_bi_bc_signals,
    get_zs_seq as ai_get_zs_seq,
)
from core.chanlun.algorithms import (
    calculate_main_bs_points,
    get_zs_seq,
)
from core.chanlun.utils import (
    dt_to_str as _dt_to_str,
    dt_to_ts as _dt_to_ts,
    get_ts_freq as _get_ts_freq,
    json_safe as _json_safe,
    normalize_ts_code as _normalize_ts_code,
    parse_bool as _parse_bool,
    resolution_to_freq as _resolution_to_freq,
)

logger = logging.getLogger(__name__)

AI_MARK_MAP = {
    "B1": "一买", "B2": "二买", "B3": "三买", "LB1": "类一买", "LB2": "类二买", "LB3": "类三买",
    "S1": "一卖", "S2": "二卖", "S3": "三卖", "LS1": "类一卖", "LS2": "类二卖", "LS3": "类三卖",
}

AI_MARK_PRIORITY = {
    "类一买": 1, "类二买": 2, "类三买": 3, "类一卖": 1, "类二卖": 2, "类三卖": 3,
    "一买": 4, "二买": 5, "三买": 6, "一卖": 4, "二卖": 5, "三卖": 6,
}


def get_analysis_data(code: str, freq_enum: Freq) -> dict:
    """输入 code(如 601888) + czsc.Freq，输出 README 定义的 JSON 结构 dict。"""

    ts_code = _normalize_ts_code(code)
    db_period = _get_ts_freq(freq_enum)
    engine = create_stock_kline_engine()
    df = read_stock_kline(engine, ts_code, db_period)

    if df.empty:
        return {"symbol": ts_code, "kline": [], "bi": [], "zs": [], "bs": []}

    df = clean_kline_df(df, ts_code)
    if df.empty:
        return {"symbol": ts_code, "kline": [], "bi": [], "zs": [], "bs": []}

    # czsc 计算
    raw_bars = czsc.format_standard_kline(df, freq=freq_enum)
    c = czsc.CZSC(raw_bars, max_bi_num=1000)

    zs_list = ai_get_zs_seq(c.bi_list)

    # 与原版 main.py 保持一致的买卖点计算顺序
    is_strict = freq_enum not in (Freq.S, Freq.Y)
    th_val = 120 if freq_enum in (Freq.S, Freq.Y) else 100
    
    b1_list = ai_find_B1(c.bi_list, zs_list, c, strict=is_strict, th=th_val)
    
    # 获取二类买卖点（季线/年线开启独立检测，不依赖一类买卖点列表）
    if freq_enum in (Freq.S, Freq.Y):
        b2_list = ai_find_B2(c.bi_list, b1_list, independent=True)
    else:
        b2_list = ai_find_B2(c.bi_list, b1_list, independent=False)
        
    lb2_list = ai_find_LB2(c.bi_list, b2_list)
    b3_list = ai_find_B3(c.bi_list, zs_list)
    s1_list = ai_find_S1(c.bi_list, zs_list, c, strict=is_strict, th=th_val)
    
    if freq_enum in (Freq.S, Freq.Y):
        s2_list = ai_find_S2(c.bi_list, s1_list, independent=True)
    else:
        s2_list = ai_find_S2(c.bi_list, s1_list, independent=False)
        
    ls2_list = ai_find_LS2(c.bi_list, s2_list)
    s3_list = ai_find_S3(c.bi_list, zs_list)
    
    # 高周期额外补充“笔背驰”信号
    bi_bc_points = []
    if freq_enum in (Freq.S, Freq.Y):
        bi_bc_points = ai_find_bi_bc_signals(c.bi_list)
    
    bs_points = b1_list + b2_list + lb2_list + b3_list + s1_list + s2_list + ls2_list + s3_list + bi_bc_points

    # A. 基础信息
    last_bar = raw_bars[-1]
    
    # B. 笔（同步提取买卖点标记及翻译）
    def _format_ai_dt(dt_val, f_enum):
        s_dt = _dt_to_str(dt_val)
        if f_enum == Freq.D and " 00:00:00" in s_dt:
            return s_dt.replace(" 00:00:00", " 15:00:00")
        return s_dt

    bi_data = []
    for bi in c.bi_list:
        actual_mark = ""
        actual_div = ""
        
        # 1. 扫描买卖点并翻译
        marks = []
        divs = []
        for p in bs_points:
            p_dt = _dt_to_str(p.get('dt'))
            if p_dt == _dt_to_str(bi.fx_b.dt):
                label_val = str(p.get('bs_type', ''))
                m_txt = AI_MARK_MAP.get(label_val, label_val)
                if m_txt and m_txt not in marks:
                    marks.append(m_txt)
                
                if label_val in ['B1', 'S1']:
                    if "趋势背驰" not in divs:
                        divs.append("趋势背驰")
        
        # 显示策略完全对齐官方：
        # mark列（买点列）：仅显示优先级最高的一个买卖点
        # div列（背驰列）：仅显示背驰相关信息，如"笔背驰"、"盘整背驰"，无则为空
        if marks:
            marks.sort(key=lambda x: AI_MARK_PRIORITY.get(x, 99))
            actual_mark = marks[0]  # 只取优先级最高的一个标记，和官方一致
            actual_div = "/".join(divs) if divs else ""  # 背驰列仅显示背驰信息
        else:
            actual_mark = ""
            actual_div = "/".join(divs) if divs else ""

        bi_data.append({
            "start_dt": _format_ai_dt(bi.fx_a.dt, freq_enum),
            "end_dt": _format_ai_dt(bi.fx_b.dt, freq_enum),
            "direction": "向上" if bi.direction == Direction.Up else "向下", # 显式转中文对齐
            "start_val": _json_safe(bi.fx_a.fx),
            "end_val": _json_safe(bi.fx_b.fx),
            "mark": actual_mark,
            "div": actual_div
        })

    # C. 线段数据 (Seg)
    seg_data = []
    try:
        # 基于 czsc 计算出的笔（bi_list）直接计算标准线段
        bi_count = len(c.bi_list)
        logger.debug("开始计算线段，当前笔总数：%s", bi_count)
        segment_data = ai_calculate_xd_list(c.bi_list)
        logger.debug("线段计算完成，共 %s 条", len(segment_data))

        # 极端保底：如果线段计算返回空，手动生成至少一条线段
        if not segment_data and bi_count >= 1:
            logger.debug("线段计算返回空，启动极端保底生成")
            # 把所有笔当成一个未完成线段
            if bi_count >= 2:
                dir_count = Counter([bi.direction for bi in c.bi_list])
                xd_dir = dir_count.most_common(1)[0][0]
                direction = "向上" if xd_dir == Direction.Up else "向下"
                start_val = min(bi.low for bi in c.bi_list) if xd_dir == Direction.Up else max(bi.high for bi in c.bi_list)
                end_val = max(bi.high for bi in c.bi_list) if xd_dir == Direction.Up else min(bi.low for bi in c.bi_list)
            else:
                # 只有1笔的情况
                bi = c.bi_list[0]
                direction = "向上" if bi.direction == Direction.Up else "向下"
                start_val = bi.fx_a.fx
                end_val = bi.fx_b.fx

            segment_data = [{
                "start_dt": c.bi_list[0].sdt,
                "end_dt": c.bi_list[-1].edt,
                "direction": direction,
                "start_val": round(start_val, 2),
                "end_val": round(end_val, 2),
                "completed": False,
                "beichi": ""
            }]
            logger.debug("极端保底生成线段成功：%s 条", len(segment_data))

        # 转换格式供 AI 和图表使用
        for seg in segment_data[-7:]: # 保留最新7条线段给AI分析
            seg_mark = ""
            # 优化买卖点匹配：不仅匹配结束时间，也匹配价格区间
            seg_end_dt = _dt_to_str(seg['end_dt'])
            seg_end_val = seg['end_val']
            for p in bs_points:
                p_dt = _dt_to_str(p.get('dt'))
                p_price = p.get('price', 0)
                # 时间匹配 + 价格误差在0.5%以内
                if p_dt == seg_end_dt and abs(p_price - seg_end_val) / seg_end_val < 0.005:
                    seg_mark = AI_MARK_MAP.get(str(p.get('bs_type', '')), str(p.get('bs_type', '')))
                    break

            seg_data.append({
                "start_dt": _dt_to_str(seg['start_dt']),
                "end_dt": _dt_to_str(seg['end_dt']),
                "direction": seg['direction'],
                "start_val": _json_safe(seg['start_val']),
                "end_val": _json_safe(seg['end_val']),
                "completed": seg.get('completed', True),
                "mark": seg_mark,
                "div": seg.get('beichi', "")
            })
        logger.debug("最终生成线段数据：%s 条", len(seg_data))
    except Exception as seg_err:
        logger.exception("线段计算异常: %s", seg_err)
        # 异常情况下也返回保底线段，不要返回空
        if len(c.bi_list) >= 1:
            bi = c.bi_list[-1]
            seg_data = [{
                "start_dt": _dt_to_str(c.bi_list[0].sdt),
                "end_dt": _dt_to_str(bi.edt),
                "direction": "向上" if bi.direction == Direction.Up else "向下",
                "start_val": _json_safe(min(b.low for b in c.bi_list)),
                "end_val": _json_safe(max(b.high for b in c.bi_list)),
                "completed": False,
                "mark": "",
                "div": ""
            }]
            logger.debug("异常兜底生成线段：%s 条", len(seg_data))
        else:
            seg_data = []

    # D. 中枢（完善 ZS 对象及 Level 计算）
    formatted_zs = []
    for zs in zs_list:
        # 中枢内包含的笔数量，用于计算中枢级别
        # 公式: round(max([1, line_num / 9]), 2)，line_num > 9 表示中枢级别升级
        line_num = len(zs.bis)
        level = round(max([1, line_num / 9]), 2)
        formatted_zs.append({
            "start_dt": _dt_to_str(zs.sdt),
            "end_dt": _dt_to_str(zs.edt),
            "zg": _json_safe(float(zs.zg)),
            "zd": _json_safe(float(zs.zd)),
            "gg": _json_safe(float(zs.gg)),
            "dd": _json_safe(float(zs.dd)),
            "level": level,
            "line_num": line_num
        })

    return {
        "symbol": code,
        "freq": freq_enum.value,
        "current_price": _json_safe(last_bar.close),
        "current_dt": _dt_to_str(last_bar.dt),
        "bi": bi_data,
        "seg": seg_data,
        "zs": formatted_zs,
    }

def get_analysis_json(code: str, freq_enum: Freq) -> str:
    import json
    data = get_analysis_data(code=code, freq_enum=freq_enum)
    return json.dumps(data, ensure_ascii=False, allow_nan=False)


def get_history_data(
    code: str,
    freq_enum: Freq,
    from_ts: int | None = None,
    to_ts: int | None = None,
    countback: int | None = None,
    first_data_request: bool = False,
) -> dict:
    """将缠论分析结果转换成 TradingView UDF /history 输出结构。

    说明：
    - 核心K线字段以数组形式输出：t/o/h/l/c/v（t 为秒级时间戳）
    - 叠加字段：bis（笔）、bi_zss（笔中枢）、mmds（买卖点）
    - 线段/中枢线段等（xds/zsds/xd_zss/zsd_zss/bcs）当前算法未提供，先返回空数组
    - 新增：_perf 字段包含各环节性能埋点数据
    - 对于季线和年线，如果数据库中没有，则从日线数据实时聚合
    """
    import time as _time
    
    # 性能埋点数据
    perf = {
        "total_start": _time.perf_counter(),
        "db_connect_ms": 0.0,
        "db_query_ms": 0.0,
        "data_preprocess_ms": 0.0,
        "czsc_format_ms": 0.0,
        "czsc_parse_ms": 0.0,
        "zs_calc_ms": 0.0,
        "bs_calc_ms": 0.0,
        "b1_calc_ms": 0.0,
        "b2_calc_ms": 0.0,
        "b3_calc_ms": 0.0,
        "s1_calc_ms": 0.0,
        "s2_calc_ms": 0.0,
        "s3_calc_ms": 0.0,
        "output_build_ms": 0.0,
        "total_ms": 0.0,
        "kline_count": 0,
        "bi_count": 0,
        "zs_count": 0,
        "bs_count": 0,
        "is_aggregated": False,  # 是否从日线聚合而来
    }
    
    # ========== 1. 数据库连接 ==========
    db_connect_start = _time.perf_counter()
    engine = create_stock_kline_engine()
    ts_code = _normalize_ts_code(code)
    db_period = _get_ts_freq(freq_enum)
    perf["db_connect_ms"] = (_time.perf_counter() - db_connect_start) * 1000

    # ========== 2. 数据库查询 ==========
    db_query_start = _time.perf_counter()
    df = read_stock_kline(engine, ts_code, db_period)
    perf["db_query_ms"] = (_time.perf_counter() - db_query_start) * 1000
    perf["kline_count"] = len(df)
    
    # 如果是季线或年线且没有数据，从日线数据聚合
    if df.empty and freq_enum in (Freq.S, Freq.Y):
        logger.debug("%s 没有%s数据，尝试从日线聚合", ts_code, freq_enum.value)
        daily_df = read_stock_kline(engine, ts_code, "daily")
        
        if not daily_df.empty:
            logger.debug("从 %s 条日线数据聚合 %s %s", len(daily_df), ts_code, freq_enum.value)
            df = aggregate_daily_kline(daily_df, freq_enum)
            perf["is_aggregated"] = True
            perf["kline_count"] = len(df)
            logger.debug("聚合后得到 %s 条%s数据", len(df), freq_enum.value)
        else:
            logger.debug("%s 也没有日线数据，无法聚合", ts_code)

    if df.empty:
        perf["total_ms"] = (_time.perf_counter() - perf["total_start"]) * 1000
        return {"s": "no_data", "_perf": perf}

    # ========== 3. 数据预处理 ==========
    preprocess_start = _time.perf_counter()
    df = clean_kline_df(df, ts_code)
    if df.empty:
        perf["total_ms"] = (_time.perf_counter() - perf["total_start"]) * 1000
        return {"s": "no_data", "_perf": perf}
    
    perf["data_preprocess_ms"] = (_time.perf_counter() - preprocess_start) * 1000

    # ========== 4. CZSC 格式化 ==========
    czsc_format_start = _time.perf_counter()
    raw_bars = czsc.format_standard_kline(df, freq=freq_enum)
    perf["czsc_format_ms"] = (_time.perf_counter() - czsc_format_start) * 1000
    
    # ========== 5. CZSC 解析（分型 + 笔） ==========
    czsc_parse_start = _time.perf_counter()
    c = czsc.CZSC(raw_bars, max_bi_num=1000)
    perf["czsc_parse_ms"] = (_time.perf_counter() - czsc_parse_start) * 1000
    perf["bi_count"] = len(c.bi_list)

    # 判断是否为日线级别（日线/周线/月线/季线/年线），用于时间戳转换
    is_daily = freq_enum in (Freq.D, Freq.W, Freq.M, Freq.S, Freq.Y)

    # ========== 6. 中枢计算 ==========
    zs_calc_start = _time.perf_counter()
    zs_list = get_zs_seq(c.bi_list)
    perf["zs_calc_ms"] = (_time.perf_counter() - zs_calc_start) * 1000
    perf["zs_count"] = len(zs_list)

    # ========== 7. 买卖点计算 ==========
    # 普通 history 接口统一使用 ZS_sig.py 的核心算法。
    bs_calc_start = _time.perf_counter()
    bs_result = calculate_main_bs_points(c, zs_list)
    b1_list = bs_result["B1"]
    b2_list = bs_result["B2"]
    b3_list = bs_result["B3"]
    s1_list = bs_result["S1"]
    s2_list = bs_result["S2"]
    s3_list = bs_result["S3"]
    bs_points = bs_result["points"]
    bs_calc_ms = (_time.perf_counter() - bs_calc_start) * 1000
    perf["bs_calc_ms"] = bs_calc_ms
    perf["b1_calc_ms"] = 0.0
    perf["b2_calc_ms"] = 0.0
    perf["b3_calc_ms"] = 0.0
    perf["s1_calc_ms"] = 0.0
    perf["s2_calc_ms"] = 0.0
    perf["s3_calc_ms"] = 0.0
    perf["bs_count"] = len(bs_points)

    logger.debug(
        "买卖点计算结果 %s %s: B1=%s B2=%s B3=%s S1=%s S2=%s S3=%s",
        ts_code,
        freq_enum.value,
        len(b1_list),
        len(b2_list),
        len(b3_list),
        len(s1_list),
        len(s2_list),
        len(s3_list),
    )

    # ========== 8. 构建输出 ==========
    output_start = _time.perf_counter()
    payload = build_history_payload(
        bars_raw=c.bars_raw,
        bi_list=c.bi_list,
        zs_list=zs_list,
        bs_points=bs_points,
        is_daily=is_daily,
        freq=freq_enum,
        from_ts=from_ts,
        to_ts=to_ts,
        countback=countback,
        first_data_request=first_data_request,
        include_tradingview_meta=True,
    )
    if payload.get("s") != "ok":
        perf["total_ms"] = (_time.perf_counter() - perf["total_start"]) * 1000
        del perf["total_start"]
        payload["_perf"] = perf
        return payload

    logger.debug("返回给前端的 mmds 数量: %s", len(payload["mmds"]))

    perf["output_build_ms"] = (_time.perf_counter() - output_start) * 1000
    perf["total_ms"] = (_time.perf_counter() - perf["total_start"]) * 1000
    
    # 移除 total_start（它是 float，不是最终输出）
    del perf["total_start"]
    payload["_perf"] = perf  # 性能埋点数据
    return payload


def get_history_json(
    code: str,
    freq_enum: Freq,
    from_ts: int | None = None,
    to_ts: int | None = None,
    countback: int | None = None,
    first_data_request: bool = False,
) -> str:
    import json

    data = get_history_data(
        code=code,
        freq_enum=freq_enum,
        from_ts=from_ts,
        to_ts=to_ts,
        countback=countback,
        first_data_request=first_data_request,
    )
    return json.dumps(data, ensure_ascii=False, allow_nan=False)


class ChanlunTradingViewViewSet(viewsets.GenericViewSet):
    """独立的缠论 history 接口（不修改原 TradingViewViewSet）。"""

    permission_classes = []  # 允许匿名访问

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        params = request.query_params

        symbol = (params.get("symbol") or "").strip().upper()
        resolution = params.get("resolution") or ""
        from_ts = params.get("from")
        to_ts = params.get("to")
        countback = params.get("countback")
        first_data_request = _parse_bool(params.get("firstDataRequest"))

        if not symbol or not resolution:
            return Response({"s": "no_data"})

        freq_enum = _resolution_to_freq(resolution)
        if not freq_enum:
            return Response({"s": "no_data"})

        try:
            from_ts_i = int(from_ts) if from_ts is not None else None
            to_ts_i = int(to_ts) if to_ts is not None else None
            countback_i = int(countback) if countback is not None else None
        except Exception:
            from_ts_i = None
            to_ts_i = None
            countback_i = None

        data = get_history_data(
            code=symbol,
            freq_enum=freq_enum,
            from_ts=from_ts_i,
            to_ts=to_ts_i,
            countback=countback_i,
            first_data_request=first_data_request,
        )
        return Response(data)

    @action(detail=False, methods=["post"], url_path="ai_analysis")
    @throttle_classes([UserRateThrottle])
    def ai_analysis(self, request):
        """
        AI 缠论分析接口 (POST)
        参数: symbol, resolution
        """
        # 强制登录校验
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "请先登录"}, status=401)

        # 从 request.data 读取 POST 参数
        params = request.data
        symbol = (params.get("symbol") or "").strip().upper()
        resolution = params.get("resolution") or "1D"

        if not symbol:
            return Response({"error": "缺少 symbol 参数"}, status=400)

        freq_enum = _resolution_to_freq(resolution)
        if not freq_enum:
            return Response({"error": f"不支持的周期: {resolution}"}, status=400)

        try:
            # 1. 获取基础缠论结构数据（笔、段、中枢、买卖点）
            chanlun_data = get_analysis_data(code=symbol, freq_enum=freq_enum)

            # 2. 调用 AI 服务进行推理复盘
            ai_data = AIService.analyze_chanlun(symbol, resolution, chanlun_data)

            # 如果服务返回的是错误，则直接给前端
            if "error" in ai_data:
                return Response(ai_data, status=500)

            # 3. 自动保存到历史记录表
            try:
                AIAnalysisHistory.objects.create(
                    symbol=symbol,
                    resolution=resolution,
                    prompt=ai_data.get("prompt"),
                    report=ai_data.get("report"),
                    model=ai_data.get("model"),
                    prompt_tokens=ai_data.get("usage", {}).get("prompt_tokens"),
                    completion_tokens=ai_data.get("usage", {}).get("completion_tokens"),
                    total_tokens=ai_data.get("usage", {}).get("total_tokens"),
                    creator=request.user if request.user.is_authenticated else None
                )
            except Exception as save_err:
                logger.warning("保存 AI 历史记录失败: %s", save_err)

            # 返回完整结构 (附上统一状态码)
            return Response({
                "code": 2000,
                "msg": "分析成功",
                "data": {
                    "symbol": symbol,
                    "resolution": resolution,
                    "prompt": ai_data.get("prompt"),
                    "report": ai_data.get("report"),
                    "usage": ai_data.get("usage"),
                    "model": ai_data.get("model")
                }
            })
        except Exception as e:
            logger.exception("AI 分析执行异常: %s", e)
            return Response({"code": 5000, "msg": f"AI 分析执行异常: {str(e)}", "error": str(e)}, status=500)

    @action(detail=False, methods=["post"], url_path="ai_history")
    @throttle_classes([UserRateThrottle])
    def ai_history(self, request):
        """
        获取历史分析记录 (POST)
        参数: symbol (可选)
        """
        # 强制登录校验
        user = request.user
        if not user.is_authenticated:
            return Response({"code": 401, "error": "请先登录"}, status=401)

        params = request.data
        symbol = params.get("symbol")
        resolution = params.get("resolution")
        # 仅查询自己的历史
        queryset = AIAnalysisHistory.objects.filter(creator=user)
            
        if symbol:
            queryset = queryset.filter(symbol__icontains=symbol.upper())
        if resolution:
            queryset = queryset.filter(resolution=resolution)
            
        # 结果列表
        data = []
        for item in queryset[:50]: # 最近50条
            data.append({
                "id": item.id,
                "symbol": item.symbol,
                "resolution": item.resolution,
                "report": item.report,
                "prompt": item.prompt,
                "model": item.model,
                "usage": {
                    "prompt_tokens": item.prompt_tokens,
                    "completion_tokens": item.completion_tokens,
                    "total_tokens": item.total_tokens
                },
                "create_datetime": item.create_datetime.strftime("%Y-%m-%d %H:%M:%S")
            })
            
        return Response({
            "code": 2000,
            "data": data
        })

    @action(detail=False, methods=["post"], url_path="ai_history_delete")
    @throttle_classes([UserRateThrottle])
    def ai_history_delete(self, request):
        """
        删除指定的历史记录 (POST)
        参数: id
        """
        # 强制登录校验
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "请先登录"}, status=401)

        params = request.data
        history_id = params.get("id")
        if not history_id:
            return Response({"error": "缺少 id 参数"}, status=400)

        try:
            instance = AIAnalysisHistory.objects.get(id=history_id)
            # 权限检查：仅允许删除自己的
            if instance.creator != user:
                return Response({"code": 4030, "msg": "无权删除他人的历史记录", "error": "Forbidden"})
            
            instance.delete()
            return Response({
                "code": 2000, 
                "msg": "删除成功"
            })
        except AIAnalysisHistory.DoesNotExist:
            return Response({"code": 4040, "msg": "记录不存在", "error": "Not Found"})
