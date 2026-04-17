<template>
	<div class="layout-logo" v-if="setShowLogo" @click="onThemeConfigChange">
		<img :src="expandedLogo" class="layout-logo-medium-img" />
	</div>
	<div class="layout-logo-size" v-else @click="onThemeConfigChange">
		<img :src="collapsedLogo" class="layout-logo-size-img" />
	</div>
</template>

<script setup lang="ts" name="layoutLogo">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useThemeConfig } from '/@/stores/themeConfig';
import logoExpanded from '/@/assets/img/卓沃logo.png';
import logoCollapsed from '/@/assets/img/favicon.png';
import { SystemConfigStore } from '/@/stores/systemConfig';
import * as _ from 'lodash-es';
// 定义变量内容
const storesThemeConfig = useThemeConfig();
const { themeConfig } = storeToRefs(storesThemeConfig);

// 设置 logo 的显示。classic 经典布局默认显示 logo
const setShowLogo = computed(() => {
	let { isCollapse, layout } = themeConfig.value;
	return !isCollapse || layout === 'classic' || document.body.clientWidth < 1000;
});
// logo 点击实现菜单展开/收起
const onThemeConfigChange = () => {
	if (themeConfig.value.layout === 'transverse') return false;
	themeConfig.value.isCollapse = !themeConfig.value.isCollapse;
};

const systemConfigStore = SystemConfigStore();
const { systemConfig } = storeToRefs(systemConfigStore);
const getSystemConfig = computed(() => {
	return systemConfig.value;
});

const expandedLogo = computed(() => {
	if (!_.isEmpty(getSystemConfig.value['login.site_logo'])) {
		return getSystemConfig.value['login.site_logo'];
	}
	return logoExpanded;
});

const collapsedLogo = computed(() => {
	if (!_.isEmpty(getSystemConfig.value['login.site_logo_collapsed'])) {
		return getSystemConfig.value['login.site_logo_collapsed'];
	}
	return logoCollapsed;
});
</script>

<style scoped lang="scss">
.layout-logo {
	width: 220px;
	height: 50px;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: rgb(0 21 41 / 2%) 0px 1px 4px;
	color: var(--el-color-primary);
	font-size: 16px;
	cursor: pointer;
	animation: logoAnimation 0.3s ease-in-out;

	span {
		white-space: nowrap;
		display: inline-block;
	}

	&:hover {
		span {
			color: var(--color-primary-light-2);
		}
	}

	&-medium-img {
		height: 35px;
		width: auto;
		max-width: 160px;
		object-fit: contain;
	}
}

.layout-logo-size {
	width: 100%;
	height: 50px;
	display: flex;
	cursor: pointer;
	animation: logoAnimation 0.3s ease-in-out;

	&-img {
		height: 40px;
		width: auto;
		max-width: 40px;
		margin: auto;
		object-fit: contain;
	}

	&:hover {
		img {
			animation: logoAnimation 0.3s ease-in-out;
		}
	}
}
</style>
