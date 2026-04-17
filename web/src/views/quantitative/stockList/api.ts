/*
 * @Description:
 * @Author:
 * @Date: 2025-11-28 10:40:50
 * @LastEditors: Please set LastEditors
 * @LastEditTime: 2025-11-28 16:10:40
 */
import { request } from '/@/utils/service';

export const baseUrl = 'http://202.46.226.13:47381';
// 股票列表
export function GetList(query: any) {
	return request({
		url: baseUrl + '/api/selection/stock-list/',
		method: 'get',
		params: query,
	});
}

// 股票列表随机生成100条
export function randomCreate() {
	return request({
		url: baseUrl + '/api/selection/stock-list/random/',
		method: 'post',
	});
}

// 股票详情
export function getStockDetail(id: string) {
	return request({
		url: baseUrl + '/api/selection/stock-list/' + id + '/',
		method: 'get',
	});
}

// 股票新增
export function addStock(params: any) {
	return request({
		url: baseUrl + '/api/selection/stock-list/',
		method: 'post',
		data: params,
	});
}

// 股票修改
export function updateStock(id: string, params: any) {
	return request({
		url: baseUrl + '/api/selection/stock-list/' + id + '/',
		method: 'put',
		data: params,
	});
}

// 股票删除
export function deleteStock(id: string) {
	return request({
		url: baseUrl + '/api/selection/stock-list/' + id + '/',
		method: 'delete',
	});
}
