import { request } from '/@/utils/service';

// 根据id获取字典，id需要从字典管理获取
export function GetDictionaryById(id: any) {
	return request({
		url: '/api/system/dictionary/?parent=' + id,
		method: 'get',
	});
}

// 根据字典type获取字典数据
export function GetDictionaryByType(type: any) {
	return request({
		url: '/api/current/dictionary/?dictionary_key=' + type,
		method: 'get',
	});
}