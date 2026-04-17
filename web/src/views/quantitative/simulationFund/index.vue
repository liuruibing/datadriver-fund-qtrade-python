<!--
 * @Description: 模拟基金管理页面
 * @Author:
 * @Date: 2025-12-01 16:14:59
 * @LastEditors: Please set LastEditors
 * @LastEditTime: 2025-12-08 09:21:04
-->
<template>
	<fs-page>
		<div class="simulation-fund-container">
			<!-- 搜索条件 -->
			<el-card class="search-card custom-card" shadow="never">
				<template #header>
					<div class="card-header">
						<span>模拟组合查询</span>
						<el-button type="text" @click="resetSearch" size="small">重置</el-button>
					</div>
				</template>

				<div class="search-content">
					<el-form :model="searchForm" :inline="true" class="search-form">
						<el-form-item label="模拟组合名称">
							<el-input v-model="searchForm.name" placeholder="请输入模拟组合名称" clearable style="width: 200px" />
						</el-form-item>
						<el-form-item label="业绩基准">
							<el-select v-model="searchForm.benchmark" placeholder="请选择业绩基准" clearable style="width: 200px">
								<el-option v-for="item in benchmarkOptions" :key="item.value" :label="item.label" :value="item.value" />
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
						<span>模拟组合列表 ({{ total }})</span>
						<div class="table-actions">
							<el-button type="primary" @click="handleAdd" icon="Plus" size="small"> 新增 </el-button>
						</div>
					</div>
				</template>

				<el-table ref="elTableRef" :data="tableData" style="width: 100%" height="calc(100vh - 420px)" v-loading="loading" size="small">
					<el-table-column type="index" label="序号" width="60" />
					<el-table-column prop="name" label="模拟组合名称" min-width="150" show-overflow-tooltip />
					<el-table-column prop="establishmentDate" label="成立日期" min-width="120" show-overflow-tooltip>
						<template #default="scope">
							{{ formatDate(scope.row.establishmentDate) }}
						</template>
					</el-table-column>
					<el-table-column prop="initialFund" label="初始资金（万元）" min-width="140" show-overflow-tooltip>
						<template #default="scope">
							{{ scope.row.initialFund ? scope.row.initialFund.toFixed(2) : '0.00' }}
						</template>
					</el-table-column>
					<el-table-column prop="benchmark" label="业绩基准" min-width="120" show-overflow-tooltip />
					<el-table-column prop="strategy" label="交易策略" min-width="120" show-overflow-tooltip />
					<el-table-column prop="stockCount" label="股票只数" min-width="100" show-overflow-tooltip />
					<!-- 操作列 -->
					<el-table-column label="操作" width="200" fixed="right">
						<template #default="scope">
							<el-button type="text" size="small" @click="handleEdit(scope.row)"> 编辑 </el-button>
							<el-button type="text" size="small" @click="handleBacktest(scope.row)"> 回测 </el-button>
							<el-button type="text" size="small" @click="handleDelete(scope.row)" style="color: #f56c6c"> 删除 </el-button>
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

		<!-- 表单弹窗 -->
		<FundFormDialog ref="fundFormDialogRef" v-if="formDialogVisible" @close="formDialogVisible = false" @confirm="handleFormConfirm" />
	</fs-page>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, Plus } from '@element-plus/icons-vue';
import { GetList, addFund, updateFund, deleteFund, GetBenchmarkOptions } from './api';
import FundFormDialog from './components/fundFormDialog.vue';

defineOptions({
	name: 'simulationFund',
});

// 类型定义
interface SimulationFundItem {
	id?: string;
	name: string;
	establishmentDate: string;
	initialFund: number;
	benchmark: string;
	stockCount: number;
	strategy: string;
}

interface SearchForm {
	name: string;
	benchmark: string;
}

const router = useRouter();

// 响应式数据
const loading = ref(false);
const elTableRef = ref();
const tableData = ref<SimulationFundItem[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);

// 弹窗控制
const formDialogVisible = ref(false);
const fundFormDialogRef = ref();

// 选项数据
const benchmarkOptions = ref([]);

// 搜索表单
const searchForm = reactive<SearchForm>({
	name: '',
	benchmark: '',
});

// 获取选项数据
const fetchBenchmarkOptions = async () => {
	try {
		const res = await GetBenchmarkOptions();
		if (res.code === 2000) {
			benchmarkOptions.value = res.data || [];
		}
	} catch (error) {
		console.error('获取业绩基准选项失败:', error);
	}
};

// 格式化日期
const formatDate = (dateStr: string) => {
	if (!dateStr) return '';
	return dateStr;
};

// 方法
const handleSearch = () => {
	currentPage.value = 1;
	fetchData();
};

const resetSearch = () => {
	Object.assign(searchForm, {
		name: '',
		benchmark: '',
	});
	handleSearch();
};

// 获取模拟基金列表
const fetchData = async () => {
	loading.value = true;
	// 假数据
	tableData.value = [
		{
			id: '1',
			name: '量化策略组合A',
			establishmentDate: '2024-01-01',
			initialFund: 100.0,
			benchmark: '沪深300',
			stockCount: 50,
			strategy: '均值回归策略',
		},
		{
			id: '2',
			name: '多因子模型组合B',
			establishmentDate: '2024-02-01',
			initialFund: 200.0,
			benchmark: '上证50',
			stockCount: 30,
			strategy: '多因子策略',
		},
		{
			id: '3',
			name: '趋势跟踪组合C',
			establishmentDate: '2024-03-01',
			initialFund: 150.0,
			benchmark: '创业板指数',
			stockCount: 40,
			strategy: '趋势跟踪策略',
		},
	];
	total.value = tableData.value.length;
	loading.value = false;

	// 真实API调用（暂时注释）
	// try {
	//   const params = {
	//     page: currentPage.value,
	//     limit: pageSize.value,
	//     ...searchForm
	//   }
	//   const res = await GetList(params)
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
	//   loading.value = false
	// }
};

// 分页
const handleSizeChange = (size: number) => {
	pageSize.value = size;
	currentPage.value = 1;
	fetchData();
};

const handleCurrentChange = (page: number) => {
	currentPage.value = page;
	fetchData();
};

// 新增
const handleAdd = () => {
	formDialogVisible.value = true;
	nextTick(() => {
		fundFormDialogRef.value?.open();
	});
};

// 编辑
const handleEdit = (row: SimulationFundItem) => {
	formDialogVisible.value = true;
	nextTick(() => {
		fundFormDialogRef.value?.open(row);
	});
};

// 删除
const handleDelete = async (row: SimulationFundItem) => {
	try {
		await ElMessageBox.confirm('确定删除该模拟组合吗？此操作不可恢复！', '提示', {
			type: 'warning',
			confirmButtonText: '确定',
			cancelButtonText: '取消',
		});

		// 真实删除API调用（暂时注释）
		// await deleteFund(row.id!)
		// ElMessage.success('删除成功')

		// 模拟删除
		const index = tableData.value.findIndex((item) => item.id === row.id);
		if (index > -1) {
			tableData.value.splice(index, 1);
			total.value = tableData.value.length;
		}
		ElMessage.success('删除成功');
	} catch (error) {
		if (error !== 'cancel') {
			console.error('删除失败:', error);
			ElMessage.error('删除失败');
		}
	}
};

// 回测
const handleBacktest = (row: SimulationFundItem) => {
	// 跳转到回测页面，对导航tag命名回测-${row.name}
	router.push({
		path: '/backtest',
		query: {
			id: row.id,
			name: row.name,
		},
	});
};

// 表单确认
const handleFormConfirm = async (formData: SimulationFundItem) => {
	try {
		if (formData.id) {
			// 编辑
			// 真实更新API调用（暂时注释）
			// await updateFund(formData.id, formData)
			// ElMessage.success('编辑成功')

			// 模拟更新
			const index = tableData.value.findIndex((item) => item.id === formData.id);
			if (index > -1) {
				tableData.value[index] = formData;
			}
			ElMessage.success('编辑成功');
		} else {
			// 新增
			// 真实新增API调用（暂时注释）
			// const res = await addFund(formData)
			// ElMessage.success('新增成功')

			// 模拟新增
			const newItem = {
				...formData,
				id: Date.now().toString(),
			};
			tableData.value.unshift(newItem);
			total.value = tableData.value.length;
			ElMessage.success('新增成功');
		}

		handleSearch();
	} catch (error) {
		console.error('操作失败:', error);
		ElMessage.error('操作失败');
	}
};

// 生命周期
onMounted(() => {
	// fetchBenchmarkOptions()
	handleSearch();
});
</script>

<style scoped>
.simulation-fund-container {
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

/* 响应式设计 */
@media (max-width: 768px) {
	.simulation-fund-container {
		padding: 10px;
	}

	.search-form .el-form-item {
		margin-right: 10px;
	}

	.table-actions {
		flex-direction: column;
		gap: 5px;
	}
}
</style>
