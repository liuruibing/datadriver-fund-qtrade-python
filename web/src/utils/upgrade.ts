import axios from 'axios';
import { Local, Session } from '/@/utils/storage';
import { ElNotification } from 'element-plus';

// 是否显示升级提示信息框
const IS_SHOW_UPGRADE_SESSION_KEY = 'isShowUpgrade';
const VERSION_KEY = 'DVADMIN3_VERSION';
const VERSION_FILE_NAME = 'version-build';

// 修复import.meta.env在CJS模式下的问题
const META_ENV = {
	MODE: import.meta.env?.MODE || 'development',
	VITE_PUBLIC_PATH: import.meta.env?.VITE_PUBLIC_PATH || '/',
	npm_package_version: import.meta.env?.npm_package_version,
};

export function showUpgrade() {
	const isShowUpgrade = Session.get(IS_SHOW_UPGRADE_SESSION_KEY) ?? false;
	if (isShowUpgrade) {
		Session.remove(IS_SHOW_UPGRADE_SESSION_KEY);
		ElNotification({
			title: '新版本升级',
			message: '检测到系统新版本，正在更新中！不用担心，更新很快的哦！',
			type: 'success',
			duration: 5000,
		});
	}
}

// 生产环境前端版本校验，
export async function checkVersion() {
	if (META_ENV.MODE === 'development') {
		// 开发环境无需校验前端版本
		return;
	}
	// 获取线上版本号 t为时间戳，防止缓存
	await axios.get(`${META_ENV.VITE_PUBLIC_PATH}${VERSION_FILE_NAME}?t=${new Date().getTime()}`).then((res) => {
		const { status, data } = res || {};
		if (status === 200) {
			// 获取当前版本号
			const localVersion = Local.get(VERSION_KEY);
			// 将当前版本号持久缓存至本地
			Local.set(VERSION_KEY, data);
			// 当用户本地存在版本号并且和线上版本号不一致时，进行页面刷新操作
			if (localVersion && localVersion !== data) {
				// 本地缓存版本号和线上版本号不一致，弹出升级提示框
				// 此处无法直接使用消息框进行提醒，因为 window.location.reload()会导致消息框消失,将在loading页面判断是否需要显示升级提示框
				Session.set(IS_SHOW_UPGRADE_SESSION_KEY, true);
				window.location.reload();
			}
		}
	});
}

export function generateVersionFile() {
	// 生成版本文件到public目录下version文件中
	// 注意：这个函数只能在构建时运行，不能在浏览器环境中运行
	const package_version = META_ENV?.npm_package_version;
	const version = `${package_version}.${new Date().getTime()}`;

	// 在构建环境中，这个函数由Vite插件处理
	// 在浏览器环境中，我们只返回版本号
	console.log('Generated version:', version);
	return version;
}
