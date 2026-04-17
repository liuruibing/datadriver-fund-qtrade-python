/*
 * @Description:
 * @Author:
 * @Date: 2025-11-28 10:40:50
 * @LastEditors: Please set LastEditors
 * @LastEditTime: 2025-12-11 09:25:21
 */
import { request } from '/@/utils/service';

const baseUrl = import.meta.env.VITE_API_URL || '';
// const baseUrl = '';

// 通用查询参数类型
type QueryParams = Record<string, unknown>;

// 获取基础信息
export function GetBaseInfo(query: QueryParams) {
	return request({
		url: '/api/selection/stock-base/',
		method: 'get',
		params: query,
	});
}

// 刷新
export function RefreshData() {
	return request({
		url: '/api/selection/stock-analysis/refresh/',
		method: 'post',
	});
}

// 查询-初筛
export function GetList(query: QueryParams) {
	return request({
		url: '/api/selection/stock-selection/filter/',
		method: 'post',
		data: query,
	});
}

// 查询-精筛
export function GetFineList(query: QueryParams) {
	return request({
		// url: baseUrl + "/api/selection/stock-analysis/filter/",
		url: '/api/selection/stock-selection/refined_filter/',
		method: 'post',
		data: query,
	});
}

// 回测-K线
export function GetBacktestKline(query: QueryParams) {
	return request({
		url: '/api/selection/stock-back/kline/',
		method: 'get',
		params: query,
	});
}

// 回测-MACD
export function GetBacktestMacd(query: QueryParams) {
	return request({
		url: '/api/selection/stock-back/macd/',
		method: 'get',
		params: query,
	});
}

//
export function GetTangle(query: QueryParams) {
	return request({
		url: '/api/selection/stock-tangle/get/',
		method: 'get',
		params: query,
	});
}
// 缠论 AI 分析
export function GetAIAnalysis(data: { symbol: string; resolution?: string }) {
	return request({
		url: '/api/selection/tradingview/ai_analysis/',
		method: 'post',
		data: data,
	});
}

// 获取分析历史列表
export function GetAIHistory(data: { symbol?: string; resolution?: string }) {
	return request({
		url: '/api/selection/tradingview/ai_history/',
		method: 'post',
		data: data,
	});
}

// 删除指定历史记录
export function DeleteAIHistory(data: { id: number }) {
	return request({
		url: '/api/selection/tradingview/ai_history_delete/',
		method: 'post',
		data: data,
	});
}
