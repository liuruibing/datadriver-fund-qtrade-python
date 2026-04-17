<template>
	<fs-page>
		<div class="chanlunyuan-container" :class="{ 'small-screen': isSmallScreen }">
			<!-- 左侧分屏区域 -->
			<div class="chanlunyuan-left-container">
				<!-- 分屏控制按钮 -->
				<div class="split-screen-controls" v-if="showSplitControls">
					<el-tooltip v-for="mode in splitModes" :key="mode.value" :content="mode.label" effect="dark" placement="top">
						<el-button :class="{ active: splitMode === mode.value }" circle @click="splitMode = mode.value">
							<svg viewBox="64 64 896 896" focusable="false" data-icon="border" width="1em" height="1em" fill="currentColor" aria-hidden="true">
								<path :d="mode.svgPath"></path>
							</svg>
						</el-button>
					</el-tooltip>
				</div>

				<!-- 分屏图表容器 -->
				<div class="chart-grid" :class="`split-${splitMode}`">
					<TVChartContainer
						v-for="i in splitModes.find((mode) => mode.value === splitMode)?.num || 0"
						:key="i"
						:datafeedUrl="datafeedUrl"
            :chartsStorageUrl="chartsStorageUrl"
            clientId="qtrade"
            :userId="userId"
						:symbol="symbolInfo.symbolId"
						:interval="currentInterval"
						@symbolChange="(val) => handleSymbolChange(i, val)"
						@intervalChange="handleTVIntervalChange"
					/>
					<!-- :interval="intervals[i-1]" @symbolChange="(val) => handleSymbolChange(i, val)" @intervalChange="handleTVIntervalChange" -->
				</div>

				<!-- 移动端显示控制按钮 -->
				<el-button type="primary" circle class="mobile-control-btn" icon="Fold" @click="toggleDrawer"></el-button>

				<!-- 左侧蒙版，右侧抽屉打开时显示 -->
				<div class="left-mask" v-if="isSmallScreen && showDrawer" @click="toggleDrawer"></div>
			</div>

			<!-- 右侧区域，小屏幕以抽屉形式展示，大屏幕可收起 -->
			<div
				class="chanlunyuan-right-container"
				:class="{
					'drawer-open': isSmallScreen && showDrawer,
					'right-collapsed': !showDrawer && !isSmallScreen,
				}"
			>
				<div class="chanlunyuan-right-top">
					<div class="right-top-title">
						{{ rightMenuTitle }}
					</div>
					<!-- 移动端关闭按钮 -->
					<div class="drawer-close-btn" @click="toggleDrawer">
						<el-icon>
							<Expand />
						</el-icon>
					</div>
				</div>
				<div class="chanlunyuan-right-content">
					<div class="right-content">
						<rightContainer @rowChange="handleRowChange" v-show="rightMenuActive === '1'" :symbolInfo="symbolInfo" />
						<stockAnalysisAI 
							ref="stockAnalysisAiRef"
							v-show="rightMenuActive === '2'" 
							:symbol="symbolInfo.symbolId" 
							:period="currentInterval"
							@change="handleAIStockChange" 
							@periodChange="handleAIPeriodChange"
						/>
					</div>
					<ul class="right-menu">
						<li class="right-menu-item" v-for="item in rightMenuList" :key="item.value">
							<el-tooltip :content="item.label" effect="dark" placement="left">
								<el-button
									circle
									:icon="item.icon"
									:class="{ 'right-menu-active': rightMenuActive === item.value }"
									@click="handleRightMenuChange(item.value)"
								></el-button>
							</el-tooltip>
						</li>
					</ul>
				</div>
			</div>
		</div>
	</fs-page>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch, onBeforeUnmount, computed } from 'vue';
import { useUserInfo } from '/@/stores/userInfo';
import TVChartContainer from '/@/components/TVChartContainer/index.vue';
import rightContainer from './components/rightContainer.vue';
import stockAnalysisAI from '/@/components/stockAnalysisAI/index.vue';
const baseURL = import.meta.env.VITE_API_URL as string;
const datafeedUrl = ref(baseURL + '/api/selection/tradingview');
const chartsStorageUrl = ref(baseURL + '/api/selection/tradingview/storage');
// 获取用户信息
const userId = useUserInfo().userInfos?.id;
// const symbol = ref('000001.SH');
const symbolInfo = ref<any>({
	symbolId: '000001.SH',
	symbolName: '上证指数',
	symbolCode: '000001',
});
// 当前周期
const currentInterval = ref('1D');
// AI 组件引用
const stockAnalysisAiRef = ref<any>(null);
// 控制右侧抽屉显示状态
const showDrawer = ref(false);
// 是否显示切屏控件
const showSplitControls = ref(true);
// 是否为小屏幕
const isSmallScreen = ref(false);

// 分屏相关
const splitMode = ref('1'); // 当前分屏模式：1, 2, 3, 4
const splitModes = [
	{
		label: '单图',
		value: '1',
		svgPath:
			'M880 112H144c-17.7 0-32 14.3-32 32v736c0 17.7 14.3 32 32 32h736c17.7 0 32-14.3 32-32V144c0-17.7-14.3-32-32-32zm-40 728H184V184h656v656z',
		num: 1,
	},
	{
		label: '横双',
		value: '2a',
		svgPath:
			'M840 836H184c-4.4 0-8 3.6-8 8v60c0 4.4 3.6 8 8 8h656c4.4 0 8-3.6 8-8v-60c0-4.4-3.6-8-8-8zm0-724H184c-4.4 0-8 3.6-8 8v60c0 4.4 3.6 8 8 8h656c4.4 0 8-3.6 8-8v-60c0-4.4-3.6-8-8-8zM610.8 378c6 0 9.4-7 5.7-11.7L515.7 238.7a7.14 7.14 0 00-11.3 0L403.6 366.3a7.23 7.23 0 005.7 11.7H476v268h-62.8c-6 0-9.4 7-5.7 11.7l100.8 127.5c2.9 3.7 8.5 3.7 11.3 0l100.8-127.5c3.7-4.7.4-11.7-5.7-11.7H548V378h62.8z',
		num: 2,
	},
	{
		label: '纵双',
		value: '2b',
		svgPath:
			'M180 176h-60c-4.4 0-8 3.6-8 8v656c0 4.4 3.6 8 8 8h60c4.4 0 8-3.6 8-8V184c0-4.4-3.6-8-8-8zm724 0h-60c-4.4 0-8 3.6-8 8v656c0 4.4 3.6 8 8 8h60c4.4 0 8-3.6 8-8V184c0-4.4-3.6-8-8-8zM785.3 504.3L657.7 403.6a7.23 7.23 0 00-11.7 5.7V476H378v-62.8c0-6-7-9.4-11.7-5.7L238.7 508.3a7.14 7.14 0 000 11.3l127.5 100.8c4.7 3.7 11.7.4 11.7-5.7V548h268v62.8c0 6 7 9.4 11.7 5.7l127.5-100.8c3.8-2.9 3.8-8.5.2-11.4z',
		num: 2,
	},
	{
		label: '三图',
		value: '3',
		svgPath:
			'M872 476H152c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h720c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zm0-166h-56c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h56c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zm0 498h-56c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h56c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zm0-664h-56c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h56c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zm0 498h-56c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h56c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zM650 216h56c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8h-56c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8zm56 592h-56c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h56c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zm-332 0h-56c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h56c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zm-56-592h56c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8h-56c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8zm-166 0h56c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8h-56c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8zm332 0h56c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8h-56c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8zM208 808h-56c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h56c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zm332 0h-56c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h56c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zM152 382h56c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8h-56c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8zm332 0h56c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8h-56c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8zM208 642h-56c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h56c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zm332 0h-56c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h56c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8z',
		num: 3,
	},
	{
		label: '四图',
		value: '4',
		svgPath:
			'M464 144H160c-8.8 0-16 7.2-16 16v304c0 8.8 7.2 16 16 16h304c8.8 0 16-7.2 16-16V160c0-8.8-7.2-16-16-16zm-52 268H212V212h200v200zm452-268H560c-8.8 0-16 7.2-16 16v304c0 8.8 7.2 16 16 16h304c8.8 0 16-7.2 16-16V160c0-8.8-7.2-16-16-16zm-52 268H612V212h200v200zM464 544H160c-8.8 0-16 7.2-16 16v304c0 8.8 7.2 16 16 16h304c8.8 0 16-7.2 16-16V560c0-8.8-7.2-16-16-16zm-52 268H212V612h200v200zm452-268H560c-8.8 0-16 7.2-16 16v304c0 8.8 7.2 16 16 16h304c8.8 0 16-7.2 16-16V560c0-8.8-7.2-16-16-16zm-52 268H612V612h200v200z',
		num: 4,
	},
]; // 支持的分屏模式
// 不同分屏的默认时间周期
const intervals = ['1D', '1H', '30', '15'];

// 处理屏幕尺寸变化
const handleResize = () => {
	const width = window.innerWidth;
	// 屏幕宽度<=1000px时，判断为小屏幕
	isSmallScreen.value = width <= 1000;

	// 小屏幕时，自动切换为1屏，且不展示切屏控件
	if (isSmallScreen.value) {
		splitMode.value = '1';
		showSplitControls.value = false;
		// 小屏幕默认隐藏右侧区域
		showDrawer.value = false;
	} else {
		showSplitControls.value = true;
		// 大屏幕默认显示右侧区域
		showDrawer.value = true;
	}
};

onMounted(() => {
	// 初始化屏幕尺寸检测
	handleResize();
	// 添加窗口大小变化监听
	window.addEventListener('resize', handleResize);
});

// 组件卸载前移除事件监听
onBeforeUnmount(() => {
	window.removeEventListener('resize', handleResize);
});

// 切换抽屉显示状态
const toggleDrawer = () => {
	showDrawer.value = !showDrawer.value;
};

// 处理选中行变化
const handleRowChange = (row: any) => {
	// symbol.value = row.symbolId;
	symbolInfo.value.symbolId = row.symbolId;
	symbolInfo.value.symbolName = row.symbolName;
	symbolInfo.value.symbolCode = row.symbolId ? row.symbolId.match(/\d+/)?.[0] : '';
};

// 处理 AI 组件选择的股票同步到全局图表
const handleAIStockChange = (symbolId: string) => {
	if (symbolId === symbolInfo.value.symbolId) return;
	symbolInfo.value.symbolId = symbolId;
	symbolInfo.value.symbolCode = symbolId ? symbolId.match(/\d+/)?.[0] : '';
	// 如果需要同步名称，由于 AI 组件内部已有列表，这里可以静默等待图表加载或从关注列表同步
};

// 处理 AI 组件反馈的频率同步
const handleAIPeriodChange = (val: string) => {
	currentInterval.value = val;
};

// 处理 TV 图表反馈的频率同步
const handleTVIntervalChange = (val: string) => {
	currentInterval.value = val;
};

// 处理从TVChartContainer传来的symbolChange事件
const handleSymbolChange = (index: number, val: any) => {
	console.log('handleSymbolChange', index, val);
	// TradingView返回的往往是symbolInfo对象，提取其name或ticker
	// 如果 val.description 或 val.name 是空的，就不要覆盖现有正确的值
	symbolInfo.value.symbolId = val.ticker || val.symbol || symbolInfo.value.symbolId;
	symbolInfo.value.symbolName = val.description || val.name || symbolInfo.value.symbolName;
	symbolInfo.value.symbolCode = symbolInfo.value.symbolId ? symbolInfo.value.symbolId.match(/\d+/)?.[0] : '';
};

// 处理右侧区域菜单切换
const rightMenuList = ref([
	{ label: '股票', value: '1', icon: 'StarFilled' },
	{ label: 'AI市场分析', value: '2', icon: 'ChromeFilled' },
]);
const rightMenuActive = ref('1');
const handleRightMenuChange = (val: string) => {
	rightMenuActive.value = val;
	// 切换到 AI 分析菜单时，自动刷新股票列表
	if (val === '2' && stockAnalysisAiRef.value) {
		stockAnalysisAiRef.value.refreshStockList();
	}
};
// 计算当前选中的菜单标题
const rightMenuTitle = computed(() => {
	const selectedMenu = rightMenuList.value.find((item) => item.value === rightMenuActive.value);
	return selectedMenu ? selectedMenu.label : '';
});
</script>

<style scoped lang="scss">
.chanlunyuan-container {
	height: 100%;
	display: flex;
	position: relative;
	overflow: hidden;
}

.chanlunyuan-left-container {
	height: 100%;
	flex: 1;
	position: relative;
	background-color: #fff;
	display: flex;
	flex-direction: column;
}

.chanlunyuan-right-container {
	width: 350px;
	background-color: #fff;
	transition: transform 0.3s ease;
	/* PC端默认显示 */
	display: block;
	box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
	border-left: 1px solid #e4e7ed;
	.chanlunyuan-right-top {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 10px;
		border-bottom: 1px solid #e4e7ed;
		.right-top-title {
			font-size: 16px;
			font-weight: bold;
		}
	}
	.chanlunyuan-right-content {
		display: flex;
		height: 100%;
		.right-content {
			width: calc(100% - 40px);
			padding: 8px;
		}
		.right-menu {
			width: 40px;
			border-left: 1px solid #e4e7ed;
			.right-menu-item {
				text-align: center;
				margin: 20px 0;
				.right-menu-active {
					background-color: #e6f4ff;
					color: #409eff;
				}
			}
		}
	}
}

/* 分屏控制按钮 */
.split-screen-controls {
	// background-color: #fff;
	z-index: 100;
	position: absolute;
	bottom: 5px;
	left: 50%;
	transform: translateX(-50%);
	.active {
		background-color: #409eff;
		color: #fff;
	}
}

/* 分屏图表容器 */
.chart-grid {
	flex: 1;
	display: grid;
	gap: 8px;
	margin-bottom: 40px;
	border-bottom: 1px solid #e4e7ed;

	// padding: 8px;
	overflow: hidden;
	/* 单屏布局 */
	&.split-1 {
		padding: 0px !important;
	}

	/* 双屏布局 - 上下分屏 */
	&.split-2a {
		grid-template-columns: 1fr;
		grid-template-rows: repeat(2, 1fr);
	}

	/* 双屏布局 - 左右分屏 */
	&.split-2b {
		grid-template-columns: repeat(2, 1fr);
		grid-template-rows: 1fr;
	}

	/* 三屏布局 - 上1下2 */
	&.split-3 {
		grid-template-columns: 1fr 1fr;
		grid-template-rows: 1fr 1fr;
		grid-template-areas:
			'chart1 chart1'
			'chart2 chart3';

		& > *:nth-child(1) {
			grid-area: chart1;
		}

		& > *:nth-child(2) {
			grid-area: chart2;
		}

		& > *:nth-child(3) {
			grid-area: chart3;
		}
	}

	/* 四屏布局 - 2x2网格 */
	&.split-4 {
		grid-template-columns: 1fr 1fr;
		grid-template-rows: 1fr 1fr;
	}

	/* 每个图表容器 */
	& > * {
		background-color: #fff;
		border-radius: 4px;
		overflow: hidden;
		box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
	}
}

/* 移动端控制按钮 */
.mobile-control-btn {
	position: absolute;
	bottom: 10px;
	right: 10px;
	z-index: 999;
	font-size: 14px;
	/* 默认隐藏，通过JS控制显示 */
	display: none;
}

/* 移动端关闭按钮 */
.drawer-close-btn {
	border: none;
	border-radius: 4px;
	cursor: pointer;
	z-index: 1001;
	/* 默认隐藏，通过JS控制显示 */
	display: none;
}

.small-screen {
	.chanlunyuan-right-container {
		width: 300px;
	}
}
@media screen and (max-width: 1000px) {
	.small-screen {
		.chanlunyuan-right-container {
			position: absolute;
			right: 0;
			top: 0;
			height: 100%;
			transform: translateX(100%);
			z-index: 1000;
			box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
		}

		.chanlunyuan-right-container.drawer-open {
			transform: translateX(0);
		}

		.mobile-control-btn {
			display: block;
		}

		.drawer-close-btn {
			display: block;
		}

		.chart-grid {
			margin-bottom: 0px;
			border-bottom: none;
		}
	}

	/* 左侧蒙版样式 */
	.left-mask {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.3);
		z-index: 998;
		cursor: pointer;
		transition: opacity 0.3s ease;
	}
}
</style>
