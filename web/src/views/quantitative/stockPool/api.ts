/*
 * @Description:
 * @Author:
 * @Date: 2025-12-01 10:00:00
 * @LastEditors: Please set LastEditors
 * @LastEditTime: 2025-12-01 10:00:00
 */
import { request } from '/@/utils/service';

export const baseUrl = 'http://202.46.226.13:47381';

// 股票池列表
export function GetList(query: any) {
	return request({
		url: baseUrl + '/api/selection/stock-pool/',
		method: 'get',
		params: query,
	});
}

// 股票池类型列表
export function GetPoolTypes(query: any) {
	return request({
		url: baseUrl + '/api/selection/stock-pool/types/',
		method: 'get',
		params: query,
	});
}

// 新增股票池类型
export function addPoolType(params: any) {
	return request({
		url: baseUrl + '/api/selection/stock-pool/types/',
		method: 'post',
		data: params,
	});
}

// 修改股票池类型
export function updatePoolType(id: string, params: any) {
	return request({
		url: baseUrl + '/api/selection/stock-pool/types/' + id + '/',
		method: 'put',
		data: params,
	});
}

// 删除股票池类型
export function deletePoolType(id: string) {
	return request({
		url: baseUrl + '/api/selection/stock-pool/types/' + id + '/',
		method: 'delete',
	});
}

// 添加股票到股票池
export function addStockToPool(params: any) {
	return request({
		url: baseUrl + '/api/selection/stock-pool/stocks/',
		method: 'post',
		data: params,
	});
}

// 从股票池删除股票
export function removeStockFromPool(poolId: string, stockId: string) {
	return request({
		url: baseUrl + '/api/selection/stock-pool/stocks/' + stockId + '/',
		method: 'delete',
	});
}

// 获取股票池中的股票列表
export function getPoolStocks(poolId: string, query: any = {}) {
	return request({
		url: baseUrl + '/api/selection/stock-pool/' + poolId + '/stocks/',
		method: 'get',
		params: query,
	});
}

// AI股票分析
export function aiStockAnalysis(params: any) {
	return request({
		url: baseUrl + '/api/selection/stock-pool/ai-analysis/',
		method: 'post',
		data: params,
	});
}
