<template>
	<fs-page>
		<div class="firm-bargain-container">
			<!-- 搜索条件 -->
			<el-card class="search-card custom-card" shadow="never">
				<template #header>
					<div class="card-header">
						<span>实盘交易查询</span>
						<el-button type="text" @click="resetSearch" size="small">重置</el-button>
					</div>
				</template>

				<div class="search-content">
					<el-form :model="searchForm" :inline="true" class="search-form">
						<el-form-item label="股票代码|名称">
							<el-input v-model="searchForm.stockInfo" placeholder="请输入股票代码或名称" clearable style="width: 200px" />
						</el-form-item>
						<el-form-item label="状态">
							<el-select v-model="searchForm.status" placeholder="请选择状态" clearable style="width: 200px">
								<el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
							</el-select>
						</el-form-item>
						<el-form-item>
							<el-button type="primary" @click="handleSearch" icon="Search"> 查询 </el-button>
						</el-form-item>
					</el-form>
				</div>
			</el-card>

			<!-- 数据表格 -->
			<el-card class="table-card custom-card" shadow="never">
				<template #header>
					<div class="card-header">
						<span>实盘交易列表 ({{ total }})</span>
						<div class="table-actions">
							<!-- <el-button type="primary" @click="handleRefresh" icon="Refresh" size="small">
                刷新
              </el-button> -->
							<el-dropdown placement="bottom-end" @command="handleAddStockType">
								<el-button type="primary" icon="Plus" size="small"> 添加股票 </el-button>
								<template #dropdown>
									<el-dropdown-menu>
										<el-dropdown-item command="market">从股票市场选择</el-dropdown-item>
										<el-dropdown-item divided command="pool">从股票池选择</el-dropdown-item>
									</el-dropdown-menu>
								</template>
							</el-dropdown>
						</div>
					</div>
				</template>

				<el-table :data="tableData" style="width: 100%" height="calc(100vh - 420px)" v-loading="loading" size="small" fit>
					<el-table-column type="index" label="序号" width="60" />
					<el-table-column prop="stockInfo" label="股票代码|名称" min-width="150" show-overflow-tooltip>
						<template #default="scope">
							<span>{{ scope.row.stockCode }} | {{ scope.row.stockName }}</span>
						</template>
					</el-table-column>
					<el-table-column prop="time" label="时间(秒)" min-width="120" show-overflow-tooltip>
						<template #default="scope">
							<span>{{ scope.row.time }}</span>
						</template>
					</el-table-column>
					<el-table-column prop="currentPrice" label="实时行情(元)" min-width="140" show-overflow-tooltip>
						<template #default="scope">
							<span>{{ scope.row.currentPrice }}</span>
						</template>
					</el-table-column>
					<el-table-column prop="status" label="状态" min-width="100" show-overflow-tooltip>
						<template #default="scope">
							<el-tag :type="getStatusTagType(scope.row.status)" size="small">
								{{ getStatusLabel(scope.row.status) }}
							</el-tag>
						</template>
					</el-table-column>
					<el-table-column prop="method" label="方式" min-width="100" show-overflow-tooltip>
						<template #default="scope">
							<span>{{ scope.row.method }}</span>
						</template>
					</el-table-column>
					<el-table-column prop="holdShares" label="当前持股数量(股)" min-width="160" show-overflow-tooltip>
						<template #default="scope">
							<span>{{ scope.row.holdShares }}</span>
						</template>
					</el-table-column>
					<el-table-column prop="positionValue" label="当前持仓市值(元)" min-width="160" show-overflow-tooltip>
						<template #default="scope">
							<span>{{ scope.row.positionValue }}</span>
						</template>
					</el-table-column>
					<!-- 操作 -->
					<el-table-column label="操作" width="300" fixed="right">
						<template #default="scope">
							<el-button type="text" size="small" @click="handleEdit(scope.row)">编辑</el-button>
							<el-button type="text" size="small" @click="handleDelete(scope.row)">移除</el-button>
							<el-button type="text" size="small" @click="handleMarket(scope.row)">行情</el-button>
							<el-button type="text" size="small" @click="handleTradeDetail(scope.row)">交易详情</el-button>
						</template>
					</el-table-column>
				</el-table>

				<!-- 分页 -->
				<div class="pagination-container">
					<el-pagination
						:current-page="currentPage"
						:page-size="pageSize"
						:page-sizes="[10, 20, 50, 100]"
						:total="total"
						layout="total, sizes, prev, pager, next, jumper"
						@size-change="handleSizeChange"
						@current-change="handleCurrentChange"
					/>
				</div>
			</el-card>
		</div>
		<!-- 行情监控弹窗 -->
		<MarketMonitorDialog v-model:visible="marketDialogVisible" :row-data="currentMarketRow" @close="marketDialogVisible = false" />

		<!-- 交易分析弹窗 -->
		<TradeAnalysisDialog v-model:visible="tradeDialogVisible" :row-data="currentTradeRow" @close="tradeDialogVisible = false" />

		<!-- 添加股票弹窗 -->
		<AddStockDialog v-if="addStockDialogVisible" @close="addStockDialogVisible = false" />

		<!-- 股票池-股票选择弹窗 -->
		<StockSelectDialog v-if="stockSelectDialogVisible" ref="stockSelectDialogRef" @confirm="handleStockSelectConfirm" />
	</fs-page>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import { Refresh, Search } from '@element-plus/icons-vue';
import { getFirmBargainList } from './api';
import MarketMonitorDialog from './components/marketMonitorDialog.vue';
import TradeAnalysisDialog from './components/tradeAnalysisDialog.vue';
import AddStockDialog from './components/addStockDialog.vue';
import StockSelectDialog from '../simulationFund/components/stockSelectDialog.vue';

defineOptions({
	name: 'firmBargain',
});

// 类型定义
interface FirmBargainItem {
	id: string;
	stockCode: string;
	stockName: string;
	time: number;
	currentPrice: number;
	status: string;
	method: string;
	holdShares: number;
	positionValue: number;
}

interface SearchForm {
	stockInfo: string;
	status: string;
}

// 响应式数据
const loading = ref(false);
const tableData = ref<FirmBargainItem[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);

// 弹窗状态
const marketDialogVisible = ref(false);
const tradeDialogVisible = ref(false);
const currentMarketRow = ref<FirmBargainItem | null>(null);
const currentTradeRow = ref<FirmBargainItem | null>(null);

// 搜索表单
const searchForm = reactive<SearchForm>({
	stockInfo: '',
	status: '',
});

// 状态选项
const statusOptions = [
	{ label: '监控中', value: 'running' },
	{ label: '停止', value: 'stopped' },
	{ label: '收盘', value: 'error' },
];

// 方法
const handleRefresh = () => {
	fetchData();
};

const handleSearch = () => {
	currentPage.value = 1;
	fetchData();
};

const resetSearch = () => {
	Object.assign(searchForm, {
		stockInfo: '',
		status: '',
	});
	handleSearch();
};

// 获取实盘交易列表
const fetchData = async () => {
	loading.value = true;
	// mock演示数据
	tableData.value = [
		{
			id: '1',
			stockCode: '000001',
			stockName: '平安银行',
			time: 100,
			currentPrice: 100,
			status: 'running',
			method: '买入',
			holdShares: 100,
			positionValue: 10000,
		},
		{
			id: '2',
			stockCode: '000002',
			stockName: '万科A',
			time: 100,
			currentPrice: 100,
			status: 'stopped',
			method: '卖出',
			holdShares: 100,
			positionValue: 10000,
		},
		{
			id: '3',
			stockCode: '000003',
			stockName: '招商银行',
			time: 100,
			currentPrice: 100,
			status: 'error',
			method: '收盘',
			holdShares: 100,
			positionValue: 10000,
		},
	];
	total.value = tableData.value.length;
	loading.value = false;
	// try {
	//   const params = {
	//     page: currentPage.value,
	//     limit: pageSize.value,
	//     ...searchForm
	//   }
	//   const res = await getFirmBargainList(params)
	//   const { code, data, total: totalCount, msg } = res
	//   if (code === 2000) {
	//     tableData.value = data || []
	//     total.value = totalCount || 0
	//   } else {
	//     tableData.value = []
	//     total.value = 0
	//     ElMessage.error(msg)
	//   }
	// } catch (error) {
	//   console.error('获取数据失败:', error)
	//   tableData.value = []
	//   total.value = 0
	//   ElMessage.error('获取数据失败')
	// } finally {
	//   loading.value = false
	// }
};

const handleSizeChange = (size: number) => {
	pageSize.value = size;
	currentPage.value = 1;
	fetchData();
};

const handleCurrentChange = (page: number) => {
	currentPage.value = page;
	fetchData();
};

const getStatusLabel = (status: string) => {
	const statusMap: Record<string, string> = {
		running: '监控中',
		stopped: '停止',
		// 'paused': '暂停',
		error: '收盘',
	};
	return statusMap[status] || status;
};

const getStatusTagType = (status: string) => {
	const typeMap: Record<string, string> = {
		running: 'success',
		stopped: 'info',
		paused: 'warning',
		error: 'danger',
	};
	return typeMap[status] || 'info';
};

const addStockDialogVisible = ref(false);
const stockSelectDialogVisible = ref(false);
const stockSelectDialogRef = ref();
// 添加股票
const handleAddStockType = (type: string) => {
	if (type === 'market') {
		// 打开添加股票弹窗
		addStockDialogVisible.value = true;
	} else if (type === 'pool') {
		// 打开添加股票弹窗
		stockSelectDialogVisible.value = true;
		nextTick(() => {
			stockSelectDialogRef.value?.open([]);
		});
	}
};

// 股票选择确认
const handleStockSelectConfirm = (selectedStocks: any[]) => {
	console.log(selectedStocks);
	stockSelectDialogVisible.value = false;
};

// 编辑
const handleEdit = (row: FirmBargainItem) => {
	console.log(row);
};

// 移除
const handleDelete = (row: FirmBargainItem) => {
	console.log(row);
};

// 行情
const handleMarket = (row: FirmBargainItem) => {
	currentMarketRow.value = row;
	marketDialogVisible.value = true;
};

// 交易详情
const handleTradeDetail = (row: FirmBargainItem) => {
	currentTradeRow.value = row;
	tradeDialogVisible.value = true;
};

// 生命周期
onMounted(() => {
	fetchData();
});
</script>

<style scoped>
.firm-bargain-container {
	padding: 10px;
	background: #f5f5f5;
}

.search-card {
	margin-bottom: 10px;
}

.table-card {
	margin-bottom: 10px;
}

.card-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.search-content {
	margin-bottom: 10px;
}

.search-form {
	margin-top: 10px;
}

.search-form .el-form-item {
	margin-bottom: 15px;
	margin-right: 20px;
}

.table-actions {
	display: flex;
	gap: 10px;
}

.pagination-container {
	display: flex;
	justify-content: center;
	padding-top: 15px;
	border-top: 1px solid #f0f0f0;
}

.price-text {
	font-weight: bold;
	color: #409eff;
}

/* 响应式设计 */
@media (max-width: 768px) {
	.firm-bargain-container {
		padding: 10px;
	}

	.search-form .el-form-item {
		margin-right: 10px;
	}
}
</style>
