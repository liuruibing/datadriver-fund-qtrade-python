import { request } from '/@/utils/service';

export interface AttentionType {
	mode: string;
	userId: string | number;
	symbolId: string;
	symbolName: string;
	symbolCode: string;
}

export function switchAttention(data: AttentionType) {
	return request({
		url: '/api/selection/stock-selection/watch_stock/',
		method: 'post',
		params: data,
	});
}

export function attentionList(data: { userId: string | number }) {
	return request({
		url: '/api/selection/stock-selection/watch_stock_list/',
		method: 'post',
		params: data,
	});
}

/**
 * 获取股票实时行情
 * NOTE: 支持传入单个或多个 symbolId，批量查询时不能超过 50 个
 * @param data.symbolId 单个股票代码或股票代码数组
 */
export function getStockQuote(data: { symbolId: string | string[] }) {
	return request({
		url: '/api/selection/stock-selection/stock_quote/',
		method: 'post',
		params: data,
	});
}
