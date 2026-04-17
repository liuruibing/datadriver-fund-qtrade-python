<!--
 * @Description: 
 * @Author: 
 * @Date: 2025-11-28 13:46:44
 * @LastEditors: Please set LastEditors
 * @LastEditTime: 2025-12-08 09:20:28
-->
<!--
 * @Description: 股票列表管理
 * @Author:
 * @Date: 2025-11-28 13:55:00
 * @LastEditors: Please set LastEditors
 * @LastEditTime: 2025-12-02 17:16:02
-->
<template>
	<fs-page>
		<div class="stock-list-container">
			<!-- 搜索条件 -->
			<el-card class="search-card custom-card" shadow="never">
				<template #header>
					<div class="card-header">
						<span>股票查询</span>
						<el-button type="text" @click="resetSearch" size="small">重置</el-button>
					</div>
				</template>

				<div class="search-content">
					<el-form :model="searchForm" :inline="true" class="search-form">
						<el-form-item label="股票代码">
							<el-input v-model="searchForm.symbol" placeholder="请输入股票代码" clearable style="width: 200px" />
						</el-form-item>
						<el-form-item label="股票名称">
							<el-input v-model="searchForm.name" placeholder="请输入股票名称" clearable style="width: 200px" />
						</el-form-item>
						<!-- <el-form-item label="行业">
              <el-select
                v-model="searchForm.industry"
                placeholder="请选择行业"
                clearable
                style="width: 200px"
              >
                <el-option
                  v-for="item in industryOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item> -->
						<el-form-item>
							<el-button type="primary" @click="handleSearch" icon="Search"> 搜索 </el-button>
						</el-form-item>
					</el-form>
				</div>
			</el-card>

			<!-- 数据表格 -->
			<el-card class="table-card custom-card" shadow="never">
				<template #header>
					<div class="card-header">
						<span>股票列表 ({{ total }})</span>
						<div class="table-actions">
							<el-button type="primary" @click="handleCreate" icon="Plus" size="small"> 新增股票 </el-button>
							<el-button type="success" @click="handleRandomCreate" icon="MagicStick" size="small"> 随机生成 </el-button>
						</div>
					</div>
				</template>

				<el-table
					:data="tableData"
					style="width: 100%"
					@selection-change="handleSelectionChange"
					height="calc(100vh - 420px)"
					v-loading="loading"
					size="small"
				>
					<!-- <el-table-column type="selection" width="55" /> -->
					<el-table-column type="index" label="序号" width="60" />
					<el-table-column prop="ts_code" label="tushare代码" width="120" show-overflow-tooltip />
					<el-table-column prop="symbol" label="股票代码" width="120" show-overflow-tooltip />
					<el-table-column prop="name" label="股票名称" width="150" show-overflow-tooltip />
					<el-table-column prop="area" label="地域" width="100" show-overflow-tooltip />
					<el-table-column prop="industry" label="所属行业" width="120" show-overflow-tooltip />
					<el-table-column prop="fullname" label="股票全称" width="180" show-overflow-tooltip />
					<el-table-column prop="enname" label="英文全称" width="150" show-overflow-tooltip />
					<el-table-column prop="cnspell" label="拼音缩写" width="120" show-overflow-tooltip />
					<el-table-column prop="market" label="市场类型" width="140" show-overflow-tooltip>
						<template #default="scope">
							<span>{{ getMarketLabel(scope.row.market) }}</span>
						</template>
					</el-table-column>
					<el-table-column prop="exchange" label="交易所代码" width="120" show-overflow-tooltip />
					<el-table-column prop="curr_type" label="交易货币" width="100" show-overflow-tooltip />
					<el-table-column prop="list_status" label="上市状态" width="120" show-overflow-tooltip>
						<template #default="scope">
							<span>{{ getListStatusLabel(scope.row.list_status) }}</span>
						</template>
					</el-table-column>
					<el-table-column prop="list_date" label="上市日期" width="120" show-overflow-tooltip />
					<el-table-column prop="delist_date" label="退市日期" width="120" show-overflow-tooltip />
					<el-table-column prop="is_hs" label="是否沪深港通标的" width="120" show-overflow-tooltip>
						<template #default="scope">
							<span>{{ getHsLabel(scope.row.is_hs) }}</span>
						</template>
					</el-table-column>
					<el-table-column prop="act_name" label="实控人名称" width="150" show-overflow-tooltip />
					<el-table-column prop="act_ent_type" label="实控人企业性质" width="150" show-overflow-tooltip />
					<el-table-column label="操作" width="150" fixed="right">
						<template #default="scope">
							<el-button type="text" size="small" @click="handleEdit(scope.row)"> 编辑 </el-button>
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

			<!-- 新增/编辑模态框 -->
			<el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px" :before-close="handleDialogClose">
				<el-form ref="formRef" :model="formData" :rules="formRules" label-width="140px">
					<el-row :gutter="20">
						<el-col :span="12">
							<el-form-item label="tushare代码" prop="ts_code">
								<el-input v-model="formData.ts_code" placeholder="请输入tushare代码" />
							</el-form-item>
						</el-col>
						<el-col :span="12">
							<el-form-item label="股票代码" prop="symbol">
								<el-input v-model="formData.symbol" placeholder="请输入股票代码" />
							</el-form-item>
						</el-col>
					</el-row>
					<el-row :gutter="20">
						<el-col :span="12">
							<el-form-item label="股票名称" prop="name">
								<el-input v-model="formData.name" placeholder="请输入股票名称" />
							</el-form-item>
						</el-col>
						<el-col :span="12">
							<el-form-item label="股票全称" prop="fullname">
								<el-input v-model="formData.fullname" placeholder="请输入股票全称" />
							</el-form-item>
						</el-col>
					</el-row>
					<el-row :gutter="20">
						<el-col :span="12">
							<el-form-item label="英文全称" prop="enname">
								<el-input v-model="formData.enname" placeholder="请输入英文全称" />
							</el-form-item>
						</el-col>
						<el-col :span="12">
							<el-form-item label="拼音缩写" prop="cnspell">
								<el-input v-model="formData.cnspell" placeholder="请输入拼音缩写" />
							</el-form-item>
						</el-col>
					</el-row>
					<el-row :gutter="20">
						<el-col :span="12">
							<el-form-item label="地域" prop="area">
								<el-input v-model="formData.area" placeholder="请输入地域" />
							</el-form-item>
						</el-col>
						<el-col :span="12">
							<el-form-item label="所属行业" prop="industry">
								<el-input v-model="formData.industry" placeholder="请输所属行业" />
								<!-- <el-select v-model="formData.industry" clearable placeholder="请选择行业" style="width: 100%">
                  <el-option
                    v-for="item in industryOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select> -->
							</el-form-item>
						</el-col>
					</el-row>
					<el-row :gutter="20">
						<el-col :span="12">
							<el-form-item label="市场类型" prop="market">
								<el-select v-model="formData.market" clearable placeholder="请选择市场类型" style="width: 100%">
									<el-option label="主板" value="主板" />
									<el-option label="创业板" value="创业板" />
									<el-option label="科创板" value="科创板" />
									<el-option label="CDR" value="CDR" />
								</el-select>
							</el-form-item>
						</el-col>
						<el-col :span="12">
							<el-form-item label="交易所代码" prop="exchange">
								<el-input v-model="formData.exchange" placeholder="请输入交易所代码" />
							</el-form-item>
						</el-col>
					</el-row>
					<el-row :gutter="20">
						<el-col :span="12">
							<el-form-item label="交易货币" prop="curr_type">
								<el-input v-model="formData.curr_type" placeholder="请输入交易货币" />
							</el-form-item>
						</el-col>
						<el-col :span="12">
							<el-form-item label="上市状态" prop="list_status">
								<el-select v-model="formData.list_status" placeholder="请选择上市状态" clearable style="width: 100%">
									<el-option label="上市" value="L" />
									<el-option label="退市" value="D" />
									<el-option label="暂停上市" value="P" />
								</el-select>
							</el-form-item>
						</el-col>
					</el-row>
					<el-row :gutter="20">
						<el-col :span="12">
							<el-form-item label="上市日期" prop="list_date">
								<el-date-picker
									v-model="formData.list_date"
									type="date"
									placeholder="请选择上市日期"
									style="width: 100%"
									format="YYYY-MM-DD"
									value-format="YYYY-MM-DD"
								/>
							</el-form-item>
						</el-col>
						<el-col :span="12">
							<el-form-item label="退市日期" prop="delist_date">
								<el-date-picker
									v-model="formData.delist_date"
									type="date"
									placeholder="请选择退市日期"
									style="width: 100%"
									format="YYYY-MM-DD"
									value-format="YYYY-MM-DD"
								/>
							</el-form-item>
						</el-col>
					</el-row>
					<el-row :gutter="20">
						<el-col :span="12">
							<el-form-item label="是否沪深港通标的" prop="is_hs">
								<el-select v-model="formData.is_hs" placeholder="请选择沪深港通" clearable style="width: 100%">
									<el-option label="否" value="N" />
									<el-option label="沪股通" value="H" />
									<el-option label="深股通" value="S" />
								</el-select>
							</el-form-item>
						</el-col>
						<el-col :span="12">
							<el-form-item label="实控人名称" prop="act_name">
								<el-input v-model="formData.act_name" placeholder="请输入实控人名称" />
							</el-form-item>
						</el-col>
					</el-row>
					<el-row :gutter="20">
						<el-col :span="12">
							<el-form-item label="实控人企业性质" prop="act_ent_type">
								<el-input v-model="formData.act_ent_type" placeholder="请输入实控人企业性质" />
							</el-form-item>
						</el-col>
					</el-row>
				</el-form>

				<template #footer>
					<span class="dialog-footer">
						<el-button @click="handleDialogClose">取消</el-button>
						<el-button type="primary" @click="handleSubmit" :loading="submitLoading"> 确定 </el-button>
					</span>
				</template>
			</el-dialog>
		</div>
	</fs-page>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Refresh, Search, MagicStick } from '@element-plus/icons-vue';
import { GetList, randomCreate, getStockDetail, updateStock, deleteStock, addStock } from './api';

defineOptions({
	name: 'stockList',
});

// 类型定义
interface StockItem {
	id?: number;
	ts_code: string;
	symbol: string;
	name: string;
	area: string;
	industry: string;
	fullname: string;
	enname: string;
	cnspell: string;
	market: string;
	exchange: string;
	curr_type: string;
	list_status: string;
	list_date: string;
	delist_date: string;
	is_hs: string;
	act_name: string;
	act_ent_type: string;
}

interface SearchForm {
	symbol: string;
	name: string;
	industry: string;
}

interface StockForm {
	id?: number;
	ts_code: string;
	symbol: string;
	name: string;
	area: string;
	industry: string;
	fullname: string;
	enname: string;
	cnspell: string;
	market: string;
	exchange: string;
	curr_type: string;
	list_status: string;
	list_date: string;
	delist_date: string;
	is_hs: string;
	act_name: string;
	act_ent_type: string;
}

// 响应式数据
const loading = ref(false);
const submitLoading = ref(false);
const dialogVisible = ref(false);
const dialogTitle = ref('新增股票');
const selectedRows = ref<StockItem[]>([]);
const tableData = ref<StockItem[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);

// 搜索表单
const searchForm = reactive<SearchForm>({
	symbol: '',
	name: '',
	industry: '',
});

// 表单数据
const formData = reactive<StockForm>({
	ts_code: '',
	symbol: '',
	name: '',
	area: '',
	industry: '',
	fullname: '',
	enname: '',
	cnspell: '',
	market: '',
	exchange: '',
	curr_type: '',
	list_status: '',
	list_date: '',
	delist_date: '',
	is_hs: '',
	act_name: '',
	act_ent_type: '',
});

// 表单验证规则
const formRules = {
	ts_code: [{ required: true, message: '请输入tushare代码', trigger: 'change' }],
	symbol: [{ required: true, message: '请输入股票代码', trigger: 'change' }],
	name: [{ required: true, message: '请输入股票名称', trigger: 'change' }],
};

// 行业选项
const industryOptions = [];

// 表单引用
const formRef = ref();

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
		symbol: '',
		name: '',
		industry: '',
	});
	handleSearch();
};
// 获取股票列表
const fetchData = async () => {
	loading.value = true;
	try {
		const params = {
			page: currentPage.value,
			limit: pageSize.value,
			...searchForm,
		};
		const res = await GetList(params);
		const { code, data, total: totalCount, msg } = res;
		if (code === 2000) {
			tableData.value = data || [];
			total.value = totalCount || 0;
		} else {
			tableData.value = [];
			total.value = 0;
			ElMessage.error(msg);
		}
		loading.value = false;
	} catch (error) {
		console.error('获取数据失败:', error);
	} finally {
		loading.value = false;
	}
};

const handleCreate = () => {
	dialogTitle.value = '新增股票';
	Object.assign(formData, {
		ts_code: '',
		symbol: '',
		name: '',
		area: '',
		industry: '',
		fullname: '',
		enname: '',
		cnspell: '',
		market: '',
		exchange: '',
		curr_type: '',
		list_status: '',
		list_date: '',
		delist_date: '',
		is_hs: '',
		act_name: '',
		act_ent_type: '',
	});
	delete formData.id;
	dialogVisible.value = true;
	nextTick(() => {
		formRef.value?.clearValidate();
	});
};

const handleEdit = async (row: StockItem) => {
	dialogTitle.value = '编辑股票';
	try {
		// const res = await getStockDetail((row.id || '').toString())
		Object.assign(formData, row);
		dialogVisible.value = true;
		nextTick(() => {
			formRef.value?.clearValidate();
		});
	} catch (error) {
		console.error('获取详情失败:', error);
		ElMessage.error('获取详情失败');
	}
};

const handleDelete = async (row: StockItem) => {
	try {
		await ElMessageBox.confirm(`确定删除股票 "${row.name}" 吗？`, '提示', {
			confirmButtonText: '确定',
			cancelButtonText: '取消',
			type: 'warning',
		});

		await deleteStock((row.id || '').toString());
		ElMessage.success('删除成功');
		fetchData();
	} catch (error) {
		if (error !== 'cancel') {
			console.error('删除失败:', error);
			ElMessage.error('删除失败');
		}
	}
};

const handleBatchDelete = async () => {
	if (selectedRows.value.length === 0) return;

	try {
		await ElMessageBox.confirm(`确定删除选中的 ${selectedRows.value.length} 条数据吗？`, '提示', {
			confirmButtonText: '确定',
			cancelButtonText: '取消',
			type: 'warning',
		});

		// 批量删除逻辑
		for (const row of selectedRows.value) {
			await deleteStock((row.id || '').toString());
		}

		ElMessage.success('批量删除成功');
		selectedRows.value = [];
		fetchData();
	} catch (error) {
		if (error !== 'cancel') {
			console.error('批量删除失败:', error);
			ElMessage.error('批量删除失败');
		}
	}
};

const handleSubmit = async () => {
	if (!formRef.value) return;

	const valid = await formRef.value.validate().catch(() => false);
	if (!valid) return;

	submitLoading.value = true;
	try {
		if (formData.id) {
			// 编辑
			const res = await updateStock(formData.id.toString(), formData);
			const { code, msg } = res;
			if (code === 2000) {
				ElMessage.success('编辑成功');
			} else {
				ElMessage.error(msg);
			}
		} else {
			// 新增
			const res = await addStock(formData);
			const { code, msg } = res;
			if (code === 2000) {
				ElMessage.success('新增成功');
			} else {
				ElMessage.error(msg);
			}
		}
		submitLoading.value = false;
		dialogVisible.value = false;
		fetchData();
	} catch (error) {
		console.error('提交失败:', error);
		ElMessage.error('编辑失败');
	} finally {
		submitLoading.value = false;
	}
};

const handleDialogClose = () => {
	dialogVisible.value = false;
};

const handleSelectionChange = (selection: StockItem[]) => {
	selectedRows.value = selection;
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

const handleRandomCreate = async () => {
	await randomCreate();
	fetchData();
};

const getMarketLabel = (market: string) => {
	const marketMap: Record<string, string> = {
		主板: '主板',
		创业板: '创业板',
		科创板: '科创板',
		CDR: 'CDR',
	};
	return marketMap[market] || market;
};

const getListStatusLabel = (status: string) => {
	const statusMap: Record<string, string> = {
		L: '上市',
		D: '退市',
		P: '暂停上市',
	};
	return statusMap[status] || status;
};

const getHsLabel = (isHs: string) => {
	const hsMap: Record<string, string> = {
		N: '否',
		H: '沪股通',
		S: '深股通',
	};
	return hsMap[isHs] || isHs;
};

const getPriceClass = (change: number) => {
	return change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral';
};

const getChangeClass = (change: number) => {
	return change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral';
};

// 生命周期
onMounted(() => {
	fetchData();
});
</script>

<style scoped>
.stock-list-container {
	padding: 10px;
	background: #f5f5f5;
}

.page-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 10px;
	padding: 10px;
	background: white;
	border-radius: 8px;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-title {
	display: flex;
	align-items: center;
	font-size: 24px;
	font-weight: bold;
	color: #333;
}

.header-title i {
	margin-right: 10px;
	font-size: 28px;
	color: #409eff;
}

.header-actions {
	display: flex;
	gap: 10px;
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
	/* padding: 10px 0; */
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
	/* margin-top: 20px; */
	padding-top: 15px;
	border-top: 1px solid #f0f0f0;
}

/* 价格颜色样式 */
.positive {
	color: #f56c6c;
	font-weight: bold;
}

.negative {
	color: #67c23a;
	font-weight: bold;
}

.neutral {
	color: #909399;
}

.dialog-footer {
	display: flex;
	justify-content: flex-end;
	gap: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
	.stock-list-container {
		padding: 10px;
	}

	.page-header {
		flex-direction: column;
		gap: 15px;
		align-items: flex-start;
	}

	.header-actions {
		width: 100%;
		justify-content: flex-end;
	}

	.search-form .el-form-item {
		margin-right: 10px;
	}
}
</style>
