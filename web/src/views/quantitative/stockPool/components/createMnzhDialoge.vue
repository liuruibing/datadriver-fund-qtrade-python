<template>
	<el-dialog v-model="dialogVisible" title="创建模拟组合" width="600px" :close-on-click-modal="false" @close="handleClose">
		<el-form ref="formRef" :model="formData" :rules="formRules" label-width="130px">
			<el-form-item label="组合名称" prop="name">
				<el-input v-model="formData.name" placeholder="请输入模拟组合名称" clearable />
			</el-form-item>

			<el-form-item label="初始资金(万元)" prop="initialFund">
				<el-input-number v-model="formData.initialFund" :precision="2" :min="0" placeholder="请输入初始资金" style="width: 100%" />
			</el-form-item>

			<el-form-item label="开始日期" prop="startDate">
				<el-date-picker
					v-model="formData.startDate"
					type="date"
					placeholder="选择开始日期"
					format="YYYY-MM-DD"
					value-format="YYYY-MM-DD"
					:disabled-date="disabledDate"
					style="width: 100%"
				/>
			</el-form-item>

			<el-form-item label="业绩基准" prop="benchmark">
				<el-select v-model="formData.benchmark" placeholder="请选择业绩基准" style="width: 100%">
					<el-option v-for="item in benchmarkOptions" :key="item.value" :label="item.label" :value="item.value" />
				</el-select>
			</el-form-item>

			<el-form-item label="交易策略" prop="strategy">
				<el-select v-model="formData.strategy" placeholder="请选择交易策略" style="width: 100%">
					<el-option v-for="item in strategyOptions" :key="item.value" :label="item.label" :value="item.value" />
				</el-select>
			</el-form-item>
		</el-form>

		<template #footer>
			<el-button @click="handleClose">取消</el-button>
			<el-button type="primary" @click="handleSubmit" :loading="submitLoading"> 创建 </el-button>
		</template>
	</el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick } from 'vue';
import { ElMessage, ElForm } from 'element-plus';

defineOptions({
	name: 'CreateMnzhDialoge',
});

const emit = defineEmits<{
	close: [];
	confirm: [data: SimulationFundFormData];
}>();

// 定义类型
type SimulationFundFormData = {
	name: string;
	initialFund: number;
	startDate: string;
	benchmark: string;
	strategy: string;
};

// 响应式数据
const dialogVisible = ref(false);
const submitLoading = ref(false);

// 表单数据
const formData = reactive<SimulationFundFormData>({
	name: '',
	initialFund: 0,
	startDate: '',
	benchmark: '',
	strategy: '',
});

// 表单验证规则
const formRules = {
	name: [
		{ required: true, message: '请输入模拟组合名称', trigger: 'change' },
		{ min: 1, max: 50, message: '名称长度在 1 到 50 个字符', trigger: 'change' },
	],
	initialFund: [
		{ required: true, message: '请输入初始资金', trigger: 'change' },
		{ type: 'number', min: 0.01, message: '初始资金不能小于0', trigger: 'change' },
	],
	startDate: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
	benchmark: [{ required: true, message: '请选择业绩基准', trigger: 'change' }],
	strategy: [{ required: true, message: '请选择交易策略', trigger: 'change' }],
};

// 表单引用
const formRef = ref<InstanceType<typeof ElForm>>();

// 业绩基准选项
const benchmarkOptions = [
	{ label: '沪深300', value: 'hs300' },
	{ label: '上证50', value: 'sz50' },
	{ label: '中证500', value: 'zz500' },
	{ label: '创业板指数', value: 'cyb' },
	{ label: '无基准', value: 'none' },
];

// 交易策略选项
const strategyOptions = [
	{ label: '量化选股', value: 'quantitative' },
	{ label: '均线策略', value: 'ma' },
	{ label: '趋势策略', value: 'trend' },
	{ label: '均值回归', value: 'mean_reversion' },
	{ label: '多因子模型', value: 'multi_factor' },
];

// 禁用过去的日期
const disabledDate = (time: Date) => {
	return time.getTime() < Date.now() - 8.64e7; // 禁用今天之前的日期
};

// 打开弹窗
const open = () => {
	dialogVisible.value = true;
	// 重置表单
	formData.name = '';
	formData.initialFund = 0;
	formData.startDate = '';
	formData.benchmark = '';
	formData.strategy = '';
	nextTick(() => {
		formRef.value?.clearValidate();
	});
};

// 关闭弹窗
const handleClose = () => {
	dialogVisible.value = false;
	emit('close');
};

// 提交表单
const handleSubmit = async () => {
	if (!formRef.value) return;

	const valid = await formRef.value.validate().catch(() => false);
	if (!valid) return;

	submitLoading.value = true;
	try {
		// 这里可以调用创建模拟组合的API
		console.log('创建模拟组合:', formData);

		// 模拟API调用
		await new Promise((resolve) => setTimeout(resolve, 1000));

		ElMessage.success('模拟组合创建成功');
		emit('confirm', { ...formData });
		handleClose();
	} catch (error) {
		console.error('创建失败:', error);
		ElMessage.error('创建失败，请重试');
	} finally {
		submitLoading.value = false;
	}
};

// 暴露方法给父组件
defineExpose({
	open,
});
</script>

<style scoped>
.el-form-item {
	margin-bottom: 20px;
}
</style>
