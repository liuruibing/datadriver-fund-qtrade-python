<!--
 * @Description: 
 * @Author: 
 * @Date: 2026-01-08 15:52:12
 * @LastEditors: Please set LastEditors
 * @LastEditTime: 2026-01-13 10:50:11
-->
<template>
	<div style="height: 100%">
		<div class="title">
			<div>
				<div class="symbol-name" style="font-size: 16px">{{ symbolInfo.symbolName }}</div>
				<div class="symbol-code">{{ symbolInfo.symbolId }}</div>
			</div>
			<div class="flex items-center">
				<div class="attention-action refresh-action" @click="handleManualRefresh" title="刷新实时行情">
					<el-icon class="attention-icon" :size="20">
						<Refresh />
					</el-icon>
				</div>
				<div class="attention-action" @click="handleAttentionChange(!isAttention)" title="关注/取消关注">
					<el-icon :class="['attention-icon', { 'is-active': isAttention }]" :size="20">
						<StarFilled v-if="isAttention" />
						<Star v-else />
					</el-icon>
				</div>
			</div>
		</div>
		<div style="height: calc(100% - 90px)">
			<vxe-table
				ref="tableRef"
				:data="pagedTableData"
				border="inner"
				height="100%"
				:loading="tableLoading"
				:loading-config="{
					text: '关注列表加载中，请稍后...',
				}"
				:row-config="{ isCurrent: true, isHover: true }"
				:row-class-name="highlightRowClassName"
				@current-row-change="currentRowChangeEvent"
			>
				<vxe-column field="symbolName" title="股票名称" sortable>
					<template #default="{ row }">
						<div class="symbol-name">{{ row.symbolName }}</div>
						<div class="symbol-code">{{ row.symbolId || row.symbolCode || row.symbol }}</div>
					</template>
				</vxe-column>
				<vxe-column field="latestPrice" title="最新价" align="right" header-align="left" sortable>
					<template #default="{ row }">
						<div :class="['latestPrice-value', { positive: row.change > 0, negative: row.change < 0 }]">
							{{ !isNaN(Number(row.latestPrice)) ? Number(row.latestPrice).toFixed(2) : row.latestPrice }}
						</div>
						<div :class="['change-value', { positive: row.change > 0, negative: row.change < 0 }]">
							{{ row.change > 0 ? '+' : '' }}{{ row.change }}%
						</div>
					</template>
				</vxe-column>
			</vxe-table>
		</div>
		<!-- <div class="flex justify-end" style="padding: 10px">
			<el-pagination
				v-model:current-page="pageNum"
				v-model:page-size="pageSize"
				:page-sizes="[20, 50, 100]"
				size="small"
				background
				layout="prev, pager, next, sizes"
				:total="total"
				@size-change="handleSizeChange"
				@current-change="handleCurrentChange"
			/>
		</div> -->
	</div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue';
import { switchAttention, AttentionType, attentionList, getStockQuote } from '../scripts/api';
import { isTradingTime } from '/@/utils/formatTime';
import { useUserInfo } from '/@/stores/userInfo';
import { storeToRefs } from 'pinia';
import { ElMessage } from 'element-plus';
import { Star, StarFilled, Refresh } from '@element-plus/icons-vue';

const props = defineProps<{
	symbolInfo?: any;
}>();

// 定义变量内容
const stores = useUserInfo();
const { userInfos } = storeToRefs(stores);

const tableRef = ref();
const tableData = ref<any[]>([]);
const tableLoading = ref(false);
const total = ref(0);

const pageNum = ref(1);
const pageSize = ref(20);
// 是否开启切回页面即时唤醒（常量控制：true 开启 | false 关闭）
const IS_WAKEUP_ENABLED = false;
/**
 * 当前页展示的数据切片
 * NOTE: 基于全量数据 tableData 进行前端分页
 */
const pagedTableData = computed(() => {
	const start = (pageNum.value - 1) * pageSize.value;
	return tableData.value.slice(start, start + pageSize.value);
});
/**
 * 检查当前 symbolInfo 是否存在于关注列表中，同步更新 checkbox 状态
 * NOTE: 通过 symbolId 进行匹配判断，确保 props 与列表数据一致
 */
const checkAttentionStatus = () => {
	if (!props.symbolInfo?.symbolId) {
		isAttention.value = false;
		return;
	}
	const matchedRow = tableData.value.find((item: any) => item.symbolId === props.symbolInfo.symbolId);
	isAttention.value = !!matchedRow;
	// NOTE: 匹配到对应行时，自动设置为当前行实现高亮效果
	nextTick(() => {
		if (tableRef.value) {
			if (matchedRow) {
				tableRef.value.setCurrentRow(matchedRow);
			} else {
				tableRef.value.clearCurrentRow();
			}
		}
	});
};
/**
 * 根据 symbolInfo 动态设置行的 CSS 类名
 * NOTE: 匹配行添加高亮标识样式，与 setCurrentRow 形成双重视觉效果
 * @param row 行数据
 */
const highlightRowClassName = ({ row }: { row: any }) => {
	if (props.symbolInfo?.symbolId && row.symbolId === props.symbolInfo.symbolId) {
		return 'row--matched';
	}
	return '';
};
/**
 * 获取关注列表，获取成功后自动刷新 checkbox 状态
 */
const getAttentionList = async () => {
	tableLoading.value = true;
	try {
		const response = await attentionList({ userId: userInfos.value.id });
		const { code } = response;
		if (code === 2000) {
			tableData.value = response.data;
			total.value = response.data.length;
			checkAttentionStatus();
			// NOTE: 获取列表后立即拉取行情数据
			await fetchQuotesForList();
		} else {
			ElMessage.error('获取关注列表失败');
		}
	} catch (e) {
		console.log(e, e);
	} finally {
		tableLoading.value = false;
	}
};

/** 批量查询每批最大数量 */
const BATCH_SIZE = 50;

/**
 * 批量获取列表中所有股票的实时行情数据
 * NOTE: 将 close 映射为 latestPrice，pct_chg 映射为 change
 * NOTE: 接口限制单次最多查询 50 个，超过时自动分批请求
 * @param {boolean} isAutoRefresh 是否为自动轮询调用
 */
const fetchQuotesForList = async (isAutoRefresh = false) => {
	if (!tableData.value.length) return;
	// 非交易时间，跳过自动轮询接口调用
	if (isAutoRefresh && !isTradingTime()) {
		// console.log('非交易时间，跳过行情自动刷新');
		return;
	}
	try {
		const allSymbolIds = tableData.value.map((item: any) => item.symbolId);
		// NOTE: 按 BATCH_SIZE 将 symbolId 列表分批，避免超出接口限制
		const batches: string[][] = [];
		for (let i = 0; i < allSymbolIds.length; i += BATCH_SIZE) {
			batches.push(allSymbolIds.slice(i, i + BATCH_SIZE));
		}
		// 并发请求所有批次
		const batchPromises = batches.map((batch) =>
			getStockQuote({ symbolId: batch })
				.then((res: any) => (res.code === 2000 ? res.data : []))
				.catch(() => [])
		);
		const batchResults = await Promise.all(batchPromises);
		// NOTE: 将所有批次结果合并为一个 Map，使用 ts_code 作为 key（与后端返回格式一致）
		const quoteMap = new Map<string, any>();
		for (const batchData of batchResults) {
			if (Array.isArray(batchData)) {
				for (const quote of batchData) {
					if (quote?.ts_code) {
						quoteMap.set(quote.ts_code, quote);
					}
				}
			}
		}
		// NOTE: 将行情数据合并到列表中，保持响应式更新
		tableData.value = tableData.value.map((item: any) => {
			const quote = quoteMap.get(item.symbolId);
			if (quote) {
				return {
					...item,
					latestPrice: quote.close !== null ? Number(quote.close).toFixed(2) : '--',
					change: quote.pct_chg,
				};
			}
			return item;
		});
	} catch (e) {
		console.log('获取行情数据失败:', e);
	}
};

/**
 * 手动刷新行情数据
 */
const handleManualRefresh = async () => {
	tableLoading.value = true;
	try {
		await fetchQuotesForList();
		ElMessage.success('行情数据已刷新');
	} catch (e) {
		console.log('手动刷新失败:', e);
	} finally {
		tableLoading.value = false;
	}
};

let quoteTimer: ReturnType<typeof setTimeout> | null = null;
/**
 * 启动行情定时刷新
 * NOTE: 使用 setTimeout 递归调用并引入“智能动态区间”，根据页面可见性调整频率，规避反爬虫并节省资源
 */
const startQuoteRefresh = () => {
	stopQuoteRefresh();

	const scheduleNextRefresh = () => {
		let minBase: number, maxBase: number;
		// 感知刷新：判断用户是否在实时观察页面
		if (document.hidden) {
			// 用户没在看：设置极长区间（10 到 15 分钟），极度安全
			minBase = 10 * 60 * 1000;
			maxBase = 15 * 60 * 1000;
		} else {
			// 用户正在看：设置适中区间（3 到 6 分钟），平衡实时性与安全性
			minBase = 3 * 60 * 1000;
			maxBase = 6 * 60 * 1000;
		}
		// 全随机策略：在定义的区间内随机生成下一次刷新的延时
		const nextInterval = Math.floor(Math.random() * (maxBase - minBase + 1)) + minBase;
		quoteTimer = setTimeout(async () => {
			try {
				await fetchQuotesForList(true);
			} finally {
				// 无论请求成功与否，都基于当前页面状态调度下一次刷新
				scheduleNextRefresh();
			}
		}, nextInterval);
	};
	scheduleNextRefresh();
};
/**
 * 停止行情定时刷新
 */
const stopQuoteRefresh = () => {
	if (quoteTimer) {
		clearTimeout(quoteTimer);
		quoteTimer = null;
	}
};
/**
 * 每页条数变化时重置到第一页
 * @param val 新的每页条数
 */
const handleSizeChange = (val: number) => {
	pageSize.value = val;
	pageNum.value = 1;
	// NOTE: 翻页后需重新检查当前页是否包含匹配行
	nextTick(() => checkAttentionStatus());
};
/**
 * 页码变化时重新检查高亮状态
 * @param val 新的页码
 */
const handleCurrentChange = (val: number) => {
	pageNum.value = val;
	// NOTE: 翻页后需重新检查当前页是否包含匹配行
	nextTick(() => checkAttentionStatus());
};
/**
 * 处理页面可见性变化
 * NOTE: 当用户切回页面时，立即刷新行情并重置定时器，提升体验
 */
const handleVisibilityChange = () => {
	if (!document.hidden && IS_WAKEUP_ENABLED) {
		fetchQuotesForList(true);
		startQuoteRefresh();
	}
};
// 是否关注
const isAttention = ref(false);
/**
 * 处理关注状态变化
 * @param val 关注状态 true 关注 | false 取消关注
 */
const handleAttentionChange = (val: boolean) => {
	// 切换状态前如果还没有 symbolInfo 则不发请求
	if (!props.symbolInfo?.symbolId) return;
	isAttention.value = val;
	const requestData: AttentionType = {
		mode: val ? 'insert' : 'remove',
		userId: userInfos.value.id,
		symbolId: props.symbolInfo.symbolId,
		symbolName: props.symbolInfo.symbolName || '', // 兜底防止 undefined 被 axios 移除
		symbolCode: props.symbolInfo.symbolCode || '',
	};
	switchAttentionApi(requestData);
};
/**
 * 关注/取消关注API
 */
const switchAttentionApi = async (data: AttentionType) => {
	try {
		const response = await switchAttention(data);
		const { code, msg } = response;
		if (code === 2000) {
			ElMessage.success(msg || '操作成功');
			if (data.mode === 'remove') {
				tableData.value = tableData.value.filter((item) => item.symbolId !== data.symbolId);
				total.value = tableData.value.length;
				// 如果删除后当前页空了，且不是第一页，自动退回上一页
				const maxPage = Math.max(1, Math.ceil(total.value / pageSize.value));
				if (pageNum.value > maxPage) {
					pageNum.value = maxPage;
				}
				checkAttentionStatus();
			} else if (data.mode === 'insert') {
				const newItem: any = {
					symbolId: data.symbolId,
					symbolName: data.symbolName,
					symbol: data.symbolCode, // 列表模板绑定的是 row.symbol
					latestPrice: '--',
					change: 0,
				};
				tableData.value.unshift(newItem);
				total.value = tableData.value.length;
				checkAttentionStatus();

				// 单独获取新关注股票的行情（使用数组格式保持与批量接口一致）
				getStockQuote({ symbolId: [data.symbolId] }).then((res: any) => {
					if (res.code === 2000 && Array.isArray(res.data) && res.data.length > 0) {
						const quote = res.data[0];
						newItem.latestPrice = quote.close !== null ? Number(quote.close).toFixed(2) : '--';
						newItem.change = quote.pct_chg;
					}
				});
			}
		} else {
			ElMessage.error(msg || '操作失败');
			// 操作失败回滚关注按钮状态
			checkAttentionStatus();
		}
	} catch (e) {
		console.log(e, e);
		checkAttentionStatus();
	}
};
// NOTE: symbolInfo 变化时重新检查关注状态，确保 checkbox 与实际数据同步
watch(
	() => props.symbolInfo,
	() => {
		checkAttentionStatus();
	},
	{ deep: true }
);

onMounted(() => {
	getAttentionList();
	// NOTE: 组件挂载后启动行情定时刷新
	startQuoteRefresh();
	// 注册页面可见性变化监听
	document.addEventListener('visibilitychange', handleVisibilityChange);
});

onBeforeUnmount(() => {
	// NOTE: 组件销毁前清除定时器，防止内存泄漏
	stopQuoteRefresh();
	// 移除页面可见性变化监听，防止内存泄漏
	document.removeEventListener('visibilitychange', handleVisibilityChange);
});

const currentRowChangeEvent = ({ row }: { row: any }) => {
	console.log(row, '>>>>>>>>>>>>>>>>>>>>>>>');
	emit('rowChange', row);
};

const emit = defineEmits<{
	rowChange: [row: any];
}>();
</script>

<style scoped>
/* 股票名称加粗 */
.symbol-name {
	font-weight: bold;
	margin-bottom: 2px;
	color: #303133;
}

/* 股票代码浅色字体 */
.symbol-code {
	color: #909399;
	font-size: 12px;
}

/* 涨跌幅样式 */
.change-value {
	font-size: 12px;
}

/* 最新价样式 */
.latestPrice-value {
	font-size: 14px;
	font-weight: bold;
}

/* 上涨红色，添加+号 */
.change-value.positive,
.latestPrice-value.positive {
	color: #f56c6c;
}

/* 下跌绿色 */
.change-value.negative,
.latestPrice-value.negative {
	color: #67c23a;
}

/* 表格样式优化 */
:deep(.vxe-table) {
	font-size: 14px;
	border: 1px solid #ebeef5;
	border-radius: 4px;
}

:deep(.vxe-table-header-wrapper) {
	background-color: #fafafa;
}

:deep(.vxe-table-body-wrapper) {
	background-color: #fff;
}

:deep(.vxe-table--border-right) {
	border-right: 1px solid #ebeef5;
}

:deep(.vxe-table--border-bottom) {
	border-bottom: 1px solid #ebeef5;
}

.title {
	padding: 5px 0;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

/* 匹配当前 symbol 的高亮行样式 */
:deep(.row--matched) {
	background-color: #ecf5ff !important;
	transition: background-color 0.3s ease;
}

:deep(.row--matched:hover) {
	background-color: #d9ecff !important;
}

/* 高亮行左侧标识线 */
:deep(.row--matched td:first-child) {
	box-shadow: inset 3px 0 0 0 #409eff;
}

/* 关注操作按钮区域 */
.attention-action {
	display: flex;
	align-items: center;
	cursor: pointer;
	gap: 6px;
	padding: 4px 8px;
	border-radius: 4px;
	transition: background-color 0.2s, color 0.2s;
	user-select: none;
}

.attention-action:hover {
	background-color: #f5f7fa;
}

.attention-icon {
	color: #909399;
	transition: color 0.3s;
}

.attention-icon.is-active {
	color: #e6a23c; /* 星星填充为黄色 */
}

.attention-text {
	font-size: 14px;
	color: #606266;
}
</style>
