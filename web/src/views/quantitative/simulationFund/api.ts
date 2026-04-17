/*
 * @Description: 模拟基金API
 * @Author:
 * @Date: 2025-12-01 16:14:59
 * @LastEditors: Please set LastEditors
 * @LastEditTime: 2025-12-01 16:14:59
 */
import { request } from '/@/utils/service';

export const baseUrl = 'http://202.46.226.13:47381';

// 模拟基金列表
export function GetList(query: any) {
	return request({
		url: baseUrl + '/api/simulation/fund/',
		method: 'get',
		params: query,
	});
}

// 新增模拟基金
export function addFund(params: any) {
	return request({
		url: baseUrl + '/api/simulation/fund/',
		method: 'post',
		data: params,
	});
}

// 修改模拟基金
export function updateFund(id: string, params: any) {
	return request({
		url: baseUrl + '/api/simulation/fund/' + id + '/',
		method: 'put',
		data: params,
	});
}

// 删除模拟基金
export function deleteFund(id: string) {
	return request({
		url: baseUrl + '/api/simulation/fund/' + id + '/',
		method: 'delete',
	});
}

// 业绩基准选项
export function GetBenchmarkOptions() {
	return request({
		url: baseUrl + '/api/simulation/benchmark/options/',
		method: 'get',
	});
}

// 交易策略选项
export function GetStrategyOptions() {
	return request({
		url: baseUrl + '/api/simulation/strategy/options/',
		method: 'get',
	});
}
