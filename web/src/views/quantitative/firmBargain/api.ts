import request from '/@/utils/request';

// 获取实盘交易列表
export const getFirmBargainList = (params: any) => {
	return request({
		url: '/firm-bargain/list',
		method: 'get',
		params,
	});
};

// 获取实盘交易详情
export const getFirmBargainDetail = (id: string) => {
	return request({
		url: `/firm-bargain/${id}`,
		method: 'get',
	});
};

// 创建实盘交易记录
export const createFirmBargain = (data: any) => {
	return request({
		url: '/firm-bargain',
		method: 'post',
		data,
	});
};

// 更新实盘交易记录
export const updateFirmBargain = (id: string, data: any) => {
	return request({
		url: `/firm-bargain/${id}`,
		method: 'put',
		data,
	});
};

// 删除实盘交易记录
export const deleteFirmBargain = (id: string) => {
	return request({
		url: `/firm-bargain/${id}`,
		method: 'delete',
	});
};
