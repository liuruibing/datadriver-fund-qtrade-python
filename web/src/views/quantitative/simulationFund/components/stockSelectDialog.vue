<template>
	<el-dialog v-model="dialogVisible" title="选择股票" width="1000px" :close-on-click-modal="false" @close="handleClose">
		<!-- 搜索条件 -->
		<div class="search-section">
			<div class="selection-info">已选择 {{ selectedStocksMap.size }} 只股票</div>
			<el-form :model="searchForm" :inline="true">
				<!-- class="search-form" -->
				<el-form-item label="股票代码|名称">
					<el-input v-model="searchForm.stockCode" placeholder="请输入股票代码|名称" />
				</el-form-item>
				<!-- <el-form-item label="股票名称">
          <el-input
            v-model="searchForm.stockName"
            placeholder="请输入股票名称"
            clearable
            style="width: 150px"
          />
        </el-form-item> -->
				<el-form-item label="股票池名称">
					<el-input v-model="searchForm.poolName" placeholder="请输入股票池名称" />
				</el-form-item>
				<el-form-item>
					<el-button type="primary" icon="Search" size="small" @click="handleSearch">查询</el-button>
					<!-- <el-button
            size="small"
            @click="handleClearSelection"
            style="margin-left: 10px"
          >清空选择</el-button> -->
				</el-form-item>
			</el-form>
		</div>

		<!-- 股票列表表格 -->
		<vxe-table
			ref="tableRef"
			:data="filteredTableData"
			style="width: 100%"
			max-height="400px"
			:loading="loading"
			size="mini"
			border="inner"
			:checkbox-config="checkboxConfig"
			@checkbox-change="handleSelectionChange"
			@checkbox-all="handleSelectionAll"
		>
			<vxe-column type="checkbox" width="55" align="center" />
			<vxe-column field="stockCode" title="股票代码|名称" min-width="120" show-overflow>
				<template #default="{ row }">
					<span>{{ row.stockCode }} | {{ row.stockName }}</span>
				</template>
			</vxe-column>
			<vxe-column field="poolName" title="股票池" min-width="150" show-overflow />
		</vxe-table>

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

		<template #footer>
			<el-button @click="handleClose">取消</el-button>
			<el-button type="primary" @click="handleConfirm" :loading="confirmLoading"> 确定 </el-button>
		</template>
	</el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import { VXETable } from 'vxe-table';

defineOptions({
	name: 'StockSelectDialog',
});

const emit = defineEmits<{
	close: [];
	confirm: [data: StockItem[]];
}>();

// 定义类型
interface StockItem {
	id?: number;
	stockCode: string;
	stockName: string;
	poolName: string;
	remark?: string;
	checked?: boolean;
}

interface SearchForm {
	stockCode: string;
	stockName: string;
	poolName: string;
}

// 响应式数据
const dialogVisible = ref(false);
const loading = ref(false);
const confirmLoading = ref(false);
const tableRef = ref();
const isFirstOpen = ref(true);

// vxe-table复选框配置
const checkboxConfig = reactive({
	checkField: 'checked',
	checkAll: false,
	checkMethod: ({ row }: any) => {
		// 可以在这里添加行级别的复选框禁用逻辑
		return true;
	},
});

// 表格数据
const tableData = ref<StockItem[]>([]);
const filteredTableData = ref<StockItem[]>([]);
const selectedRows = ref<StockItem[]>([]);

// 分页数据
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);

// 搜索表单
const searchForm = reactive<SearchForm>({
	stockCode: '',
	stockName: '',
	poolName: '',
});

// 已选择的股票数据（用于编辑时的默认勾选）
const preSelectedStocks = ref<StockItem[]>([]);

// 全局选中状态：使用 Map 存储，key 为 stockCode，value 为完整的 StockItem
// 这样可以跨页面、跨查询条件保持选中状态
const selectedStocksMap = ref<Map<string, StockItem>>(new Map());

// 模拟数据（实际应该从API获取）
const mockData: StockItem[] = [
	{ id: 1, stockCode: '000001', stockName: '平安银行', poolName: '股票池1' },
	{ id: 2, stockCode: '000002', stockName: '万科A', poolName: '股票池1' },
	{ id: 3, stockCode: '000003', stockName: '招商银行', poolName: '股票池2' },
	{ id: 4, stockCode: '000004', stockName: '兴业银行', poolName: '股票池2' },
	{ id: 5, stockCode: '600000', stockName: '浦发银行', poolName: '股票池3' },
	{ id: 6, stockCode: '600036', stockName: '招商银行', poolName: '股票池3' },
	{ id: 7, stockCode: '000858', stockName: '五粮液', poolName: '股票池4' },
	{ id: 8, stockCode: '000568', stockName: '泸州老窖', poolName: '股票池4' },
	{ id: 9, stockCode: '000725', stockName: '京东方A', poolName: '股票池5' },
	{ id: 10, stockCode: '000002', stockName: '万科A', poolName: '股票池5' },
	{ id: 11, stockCode: '600519', stockName: '贵州茅台', poolName: '股票池6' },
	{ id: 12, stockCode: '000001', stockName: '平安银行', poolName: '股票池6' },
];

// 获取表格数据
const fetchData = () => {
	loading.value = true;

	// 模拟API调用延迟
	setTimeout(() => {
		// 过滤数据
		let filteredData = mockData.filter((item) => {
			// 股票代码或名称匹配（合并搜索）
			const matchStockCodeOrName =
				!searchForm.stockCode ||
				item.stockCode.toLowerCase().includes(searchForm.stockCode.toLowerCase()) ||
				item.stockName.toLowerCase().includes(searchForm.stockCode.toLowerCase());
			// 股票池名称匹配
			const matchPoolName = !searchForm.poolName || item.poolName.toLowerCase().includes(searchForm.poolName.toLowerCase());
			return matchStockCodeOrName && matchPoolName;
		});

		total.value = filteredData.length;

		// 分页
		const startIndex = (currentPage.value - 1) * pageSize.value;
		const endIndex = startIndex + pageSize.value;
		const paginatedData = filteredData.slice(startIndex, endIndex);

		// 为每行数据添加checked字段，表示是否选中
		filteredTableData.value = paginatedData.map((item) => ({
			...item,
			checked: selectedStocksMap.value.has(item.id!.toString() || ''),
		}));

		loading.value = false;

		// 更新全选状态
		updateCheckAllStatus();
	}, 300);
};

// 搜索处理
const handleSearch = () => {
	currentPage.value = 1;
	fetchData();
};

// 清空选择
const handleClearSelection = () => {
	selectedStocksMap.value.clear();
	selectedRows.value = [];
	// 清除表格中的选中状态
	filteredTableData.value.forEach((item) => {
		item.checked = false;
	});
	checkboxConfig.checkAll = false;
};

// 分页
const handleSizeChange = (size: number) => {
	pageSize.value = size;
	currentPage.value = 1;
	fetchData();
};

// 分页
const handleCurrentChange = (page: number) => {
	currentPage.value = page;
	fetchData();
};

// 多选变化处理
const handleSelectionChange = ({ row, checked }: any) => {
	const item = row;
	const itemKey = item.id!.toString() || '';

	if (checked) {
		// 添加到全局选中状态
		selectedStocksMap.value.set(itemKey, item);
	} else {
		// 从全局选中状态移除
		selectedStocksMap.value.delete(itemKey);
	}

	// 更新当前行的checked状态
	item.checked = checked;

	// 更新全选状态
	updateCheckAllStatus();
};

// 全选变化处理
const handleSelectionAll = ({ checked }: any) => {
	filteredTableData.value.forEach((item) => {
		const itemKey = item.id!.toString() || '';
		if (checked) {
			selectedStocksMap.value.set(itemKey, item);
		} else {
			selectedStocksMap.value.delete(itemKey);
		}
		item.checked = checked;
	});

	// 更新全选状态
	updateCheckAllStatus();
};

// 更新全选状态
const updateCheckAllStatus = () => {
	const totalCount = filteredTableData.value.length;
	const checkedCount = filteredTableData.value.filter((item) => item.checked).length;
	checkboxConfig.checkAll = totalCount > 0 && checkedCount === totalCount;
};

// 打开弹窗
const open = (selectedStocks: StockItem[] = []) => {
	dialogVisible.value = true;
	preSelectedStocks.value = selectedStocks || [];

	// 初始化全局选中状态
	selectedStocksMap.value.clear();
	preSelectedStocks.value.forEach((stock) => {
		selectedStocksMap.value.set(stock.id!.toString() || '', stock);
	});
	selectedRows.value = [...preSelectedStocks.value];

	// 如果是首次打开，重置搜索条件和分页；如果是重新打开，保持搜索条件和分页状态
	if (isFirstOpen.value) {
		Object.assign(searchForm, {
			stockCode: '',
			stockName: '',
			poolName: '',
		});
		currentPage.value = 1;
		isFirstOpen.value = false;
	}

	fetchData();
};

// 关闭弹窗
const handleClose = () => {
	dialogVisible.value = false;
	selectedRows.value = [];
	// 不清空 selectedStocksMap，保持选中状态以便下次打开时恢复
};

// 确定按钮处理
const handleConfirm = () => {
	// 从全局选中状态获取所有选中的数据
	const allSelectedStocks = Array.from(selectedStocksMap.value.values());

	if (allSelectedStocks.length === 0) {
		ElMessage.warning('请至少选择一只股票');
		return;
	}

	confirmLoading.value = true;

	// 模拟提交延迟
	setTimeout(() => {
		emit('confirm', allSelectedStocks);
		handleClose();
		confirmLoading.value = false;
	}, 500);
};

// 暴露方法
defineExpose({
	open,
});
</script>

<style scoped>
.search-section {
	margin-bottom: 20px;
	padding: 15px 15px 0 15px;
	background-color: #f5f5f5;
	border-radius: 4px;
}

.selection-info {
	margin-bottom: 10px;
	color: #409eff;
	font-weight: 500;
	font-size: 14px;
}

.search-form {
	display: flex;
	flex-wrap: wrap;
	gap: 10px;
}

.search-form .el-form-item {
	margin-bottom: 0;
}

.pagination-container {
	padding-top: 15px;
	border-top: 1px solid #f0f0f0;
	display: flex;
	justify-content: center;
}
</style>
