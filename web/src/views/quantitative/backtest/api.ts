/*
 * @Description: 回测相关API
 * @Author:
 * @Date: 2025-12-02 15:00:00
 * @LastEditors: Please set LastEditors
 * @LastEditTime: 2025-12-02 15:00:00
 */
import { request } from '/@/utils/service';

export const baseUrl = 'http://202.46.226.13:47381';

// 获取持仓数据API
export function getPositionData(params?: any) {
	return request({
		url: baseUrl + '/api/backtest/positions/',
		method: 'get',
		params: params || {},
	});
}

// 获取持仓时序数据API
export function getPositionTimeline(params?: any) {
	return request({
		url: baseUrl + '/api/backtest/position-timeline/',
		method: 'get',
		params: params || {},
	});
}

// 获取交易记录数据API
export function getTradeRecords(params?: any) {
	return request({
		url: baseUrl + '/api/backtest/trade-records/',
		method: 'get',
		params: params || {},
	});
}
