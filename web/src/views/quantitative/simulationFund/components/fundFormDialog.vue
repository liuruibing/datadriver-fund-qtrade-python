<template>
	<el-dialog
		v-model="dialogVisible"
		:title="isEdit ? '编辑模拟组合' : '新增模拟组合'"
		width="800px"
		:close-on-click-modal="false"
		@close="handleClose"
	>
		<el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
			<el-form-item label="模拟组合名称" prop="name">
				<el-input v-model="formData.name" placeholder="请输入模拟组合名称" clearable />
			</el-form-item>
			<el-row :gutter="20">
				<el-col :span="12">
					<el-form-item label="成立日期" prop="establishmentDate">
						<el-date-picker
							v-model="formData.establishmentDate"
							type="date"
							placeholder="选择成立日期"
							format="YYYY-MM-DD"
							value-format="YYYY-MM-DD"
							:disabled-date="disabledDate"
							style="width: 100%"
						/>
					</el-form-item>
				</el-col>
				<el-col :span="12">
					<el-form-item label="初始资金(万元)" prop="initialFund">
						<el-input-number v-model="formData.initialFund" :precision="2" :min="0" placeholder="请输入初始资金" style="width: 100%" />
					</el-form-item>
				</el-col>
				<el-col :span="12">
					<el-form-item label="业绩基准" prop="benchmark">
						<el-select v-model="formData.benchmark" placeholder="请选择业绩基准" style="width: 100%" clearable>
							<el-option v-for="item in benchmarkOptions" :key="item.value" :label="item.label" :value="item.value" />
						</el-select>
					</el-form-item>
				</el-col>
				<el-col :span="12">
					<el-form-item label="交易策略" prop="strategy">
						<el-select v-model="formData.strategy" placeholder="请选择交易策略" style="width: 100%" clearable>
							<el-option v-for="item in strategyOptions" :key="item.value" :label="item.label" :value="item.value" />
						</el-select>
					</el-form-item>
				</el-col>
			</el-row>
		</el-form>

		<!-- 股票列表 -->
		<el-card class="custom-card" shadow="never">
			<template #header>
				<div style="display: flex; justify-content: space-between; align-items: center">
					<span>股票列表 ({{ stockList.length }})</span>
					<el-button type="primary" @click="handleSelectStock" icon="Plus" size="small"> 选择股票 </el-button>
				</div>
			</template>
			<el-table :data="stockList" style="width: 100%" size="small" fit max-height="200px">
				<el-table-column type="index" label="序号" width="60" />
				<el-table-column prop="stockCode" label="股票代码|名称" min-width="120" show-overflow-tooltip>
					<template #default="scope">
						<span>{{ scope.row.stockCode }} | {{ scope.row.stockName }}</span>
					</template>
				</el-table-column>
				<el-table-column prop="poolName" label="股票池" min-width="120" show-overflow-tooltip />
				<el-table-column prop="allocation" label="资金分配(万元)" min-width="120">
					<template #default="scope">
						<el-input v-model="scope.row.allocation" placeholder="请输入" style="width: 100%" size="small" />
					</template>
				</el-table-column>
				<el-table-column label="操作" width="100" align="center">
					<template #default="scope">
						<el-button type="danger" size="small" @click="handleDelete(scope.row)" link> 移除 </el-button>
					</template>
				</el-table-column>
			</el-table>
			<div class="total-allocation">
				<div>
					总资金分配：<span :class="['total-allocation-value', totalAllocation > formData.initialFund && 'total-allocation-value-exceed']">{{
						totalAllocation
					}}</span>
					万元
					<span class="total-allocation-tip" v-if="totalAllocation > formData.initialFund"> 总资金分配不能超过初始资金 </span>
				</div>
				<el-button link type="primary" size="small" icon="Refresh" @click="handleReset"> 重置资金分配 </el-button>
			</div>
		</el-card>

		<!-- 股票选择弹窗 -->
		<StockSelectDialog ref="stockSelectDialogRef" @confirm="handleStockSelectConfirm" />

		<template #footer>
			<el-button @click="handleClose">取消</el-button>
			<el-button type="primary" @click="handleSubmit" :loading="submitLoading">
				{{ isEdit ? '保存' : '创建' }}
			</el-button>
		</template>
	</el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, watch, computed } from 'vue';
import { ElMessage, ElForm } from 'element-plus';
import { GetBenchmarkOptions, GetStrategyOptions } from '../api';
import StockSelectDialog from './stockSelectDialog.vue';

defineOptions({
	name: 'FundFormDialog',
});

const emit = defineEmits<{
	close: [];
	confirm: [data: FundFormData];
}>();

// 定义类型
type FundFormData = {
	id?: string;
	name: string;
	establishmentDate: string;
	initialFund: number;
	benchmark: string;
	strategy: string;
	stocks?: StockItem[];
};

type StockItem = {
	id?: number;
	stockCode: string;
	stockName: string;
	poolName: string;
	remark?: string;
	allocation?: number | string;
};

// 表单数据
const dialogVisible = ref(false);
const isEdit = ref(false);
const submitLoading = ref(false);
const formRef = ref<InstanceType<typeof ElForm>>();
const stockSelectDialogRef = ref();

// 选项数据
const benchmarkOptions = ref([]);
const strategyOptions = ref([]);

// 表单数据
const formData = reactive<FundFormData>({
	name: '',
	establishmentDate: '',
	initialFund: 0,
	benchmark: '',
	strategy: '',
});

// 股票列表
const stockList = ref<StockItem[]>([]);

// 表单验证规则
const formRules = {
	name: [{ required: true, message: '请输入模拟组合名称', trigger: 'change' }],
	establishmentDate: [{ required: true, message: '请选择成立日期', trigger: 'change' }],
	initialFund: [
		{ required: true, message: '请输入初始资金', trigger: 'change' },
		{ type: 'number', min: 0.01, message: '初始资金不能小于0', trigger: 'change' },
	],
	benchmark: [{ required: true, message: '请选择业绩基准', trigger: 'change' }],
	strategy: [{ required: true, message: '请选择交易策略', trigger: 'change' }],
};

// 获取选项数据
const fetchOptions = async () => {
	try {
		const [benchmarkRes, strategyRes] = await Promise.all([GetBenchmarkOptions(), GetStrategyOptions()]);

		if (benchmarkRes.code === 2000) {
			benchmarkOptions.value = benchmarkRes.data || [];
		}

		if (strategyRes.code === 2000) {
			strategyOptions.value = strategyRes.data || [];
		}
	} catch (error) {
		console.error('获取选项数据失败:', error);
	}
};

// 禁用日期选择（不能选择未来日期）
const disabledDate = (time: Date) => {
	return time.getTime() > Date.now();
};

// 打开弹窗
const open = (data?: FundFormData) => {
	dialogVisible.value = true;
	// fetchOptions()

	nextTick(() => {
		if (data) {
			// 编辑模式
			isEdit.value = true;
			Object.assign(formData, data);
			// 如果有股票数据，在这里设置（假设从data中获取）
			stockList.value = data.stocks || [];
		} else {
			// 新增模式
			isEdit.value = false;
			Object.assign(formData, {
				name: '',
				establishmentDate: '',
				initialFund: 0,
				benchmark: '',
				strategy: '',
			});
			stockList.value = [];
		}
	});
};

// 关闭弹窗
const handleClose = () => {
	dialogVisible.value = false;
	formRef.value?.clearValidate();
};

// 提交表单
const handleSubmit = async () => {
	if (!formRef.value) return;

	const valid = await formRef.value.validate().catch(() => false);
	if (!valid) return;

	submitLoading.value = true;
	try {
		emit('confirm', { ...formData });
		handleClose();
	} catch (error) {
		console.error('提交失败:', error);
	} finally {
		submitLoading.value = false;
	}
};

// 选择股票
const handleSelectStock = () => {
	stockSelectDialogRef.value?.open(stockList.value);
};

// 股票选择确认
const handleStockSelectConfirm = (selectedStocks: any[]) => {
	stockList.value = selectedStocks;
};

const handleDelete = (row: StockItem) => {
	stockList.value = stockList.value.filter((item) => item.id !== row.id);
};

// 计算总资金分配
const totalAllocation = computed(() => {
	return stockList.value.reduce((acc, item) => acc + Number(item.allocation || 0), 0);
});

// 重置资金分配
const handleReset = () => {
	stockList.value.forEach((item) => {
		item.allocation = '';
	});
};

// 暴露方法
defineExpose({
	open,
});
</script>

<style scoped>
.el-form-item {
	margin-bottom: 20px;
}
.total-allocation {
	margin-top: 10px;
	display: flex;
	justify-content: space-between;
	align-items: center;
}
.total-allocation-value {
	/* font-size: 16px; */
}
.total-allocation-value-exceed {
	color: #f56c6c;
}
.total-allocation-tip {
	color: #f56c6c;
	margin-left: 20px;
}
</style>
