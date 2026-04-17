<template>
	<fs-page>
		<div class="backtest-container">
			<!-- 搜索条件 -->
			<el-card class="search-card custom-card" shadow="never">
				<template #header>
					<div class="card-header">
						<span>股票查询</span>
						<el-button type="text" @click="resetSearch" size="small">重置</el-button>
					</div>
				</template>

				<div class="search-content">
					<el-form :model="searchForm" :rules="searchFormRules" :inline="true" class="search-form">
						<el-form-item label="模拟组合" prop="name">
							<el-select v-model="searchForm.name" placeholder="请选择模拟组合" style="width: 200px" filterable @change="handleSimulationFundChange">
								<el-option v-for="item in simulationFundList" :key="item.value" :label="item.label" :value="item.value" />
							</el-select>
						</el-form-item>
						<el-form-item label="日期" prop="date">
							<el-date-picker
								v-model="searchForm.date"
								type="daterange"
								range-separator="至"
								start-placeholder="开始日期"
								end-placeholder="结束日期"
								value-format="YYYY-MM-DD"
								format="YYYY-MM-DD"
							/>
						</el-form-item>
						<el-form-item label="业绩基准" prop="benchmark">
							<el-select v-model="searchForm.benchmark" placeholder="请选择业绩基准" disabled style="width: 200px">
								<el-option v-for="item in benchmarkOptions" :key="item.value" :label="item.label" :value="item.value" />
							</el-select>
						</el-form-item>
						<el-form-item label="交易策略" prop="strategy">
							<el-select v-model="searchForm.strategy" placeholder="请选择交易策略" disabled style="width: 200px">
								<el-option v-for="item in strategyOptions" :key="item.value" :label="item.label" :value="item.value" />
							</el-select>
						</el-form-item>
						<el-form-item>
							<el-button type="primary" @click="handleSearch" :loading="searchLoading" icon="Cpu"> 回测计算 </el-button>
						</el-form-item>
					</el-form>
				</div>
			</el-card>

			<el-tabs type="border-card" class="backtest-tabs" @tab-click="handleTabClick" v-model="activeTab">
				<el-tab-pane label="净值走势" name="sheet1">
					<Sheet1 ref="sheet1Ref" />
				</el-tab-pane>
				<el-tab-pane label="持仓时序" name="sheet2">
					<Sheet2 ref="sheet2Ref" />
				</el-tab-pane>
				<el-tab-pane label="交易记录" name="sheet3">
					<Sheet3 ref="sheet3Ref" />
				</el-tab-pane>
			</el-tabs>
		</div>
	</fs-page>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import Sheet1 from './components/sheet1.vue';
import Sheet2 from './components/sheet2.vue';
import Sheet3 from './components/sheet3.vue';
import type { TabsPaneContext } from 'element-plus';

defineOptions({
	name: 'backtest',
});

const sheet1Ref = ref();
const sheet2Ref = ref();
const sheet3Ref = ref();

interface SimulationFundItem {
	value: string;
	label: string;
	benchmark: string;
	strategy: string;
}

// 搜索表单
const searchForm = ref({
	name: '',
	date: [],
	benchmark: '',
	strategy: '',
});

// 表单验证规则
const searchFormRules = {
	name: [{ required: true, message: '请输入模拟组合名称', trigger: 'blur' }],
	date: [{ required: true, message: '请选择日期范围', trigger: 'change' }],
};

// 模拟组合列表
const simulationFundList = ref<SimulationFundItem[]>([]);

// 获取模拟组合列表
const getSimulationFundList = async () => {
	simulationFundList.value = [
		{ value: '1', label: '量化策略组合A', benchmark: '沪深300', strategy: '均值回归策略' },
		{ value: '2', label: '多因子模型组合B', benchmark: '上证50', strategy: '多因子策略' },
		{ value: '3', label: '趋势跟踪组合C', benchmark: '创业板指数', strategy: '趋势跟踪策略' },
	];
	// const res = await GetSimulationFundList()
	// if (res.code === 2000) {
	//   simulationFundList.value = res.data || []
	// }
};

// 处理模拟组合变化
const handleSimulationFundChange = (value: string) => {
	const currentItem = simulationFundList.value.find((item) => item.value === value);
	if (currentItem) {
		searchForm.value.benchmark = currentItem.benchmark;
		searchForm.value.strategy = currentItem.strategy;
	}
};

// 业绩基准选项
const benchmarkOptions = [
	{ value: '沪深300', label: '沪深300' },
	{ value: '上证指数', label: '上证指数' },
	// 添加更多选项
];

// 交易策略选项
const strategyOptions = [
	{ value: '均线策略', label: '均线策略' },
	{ value: '动量策略', label: '动量策略' },
	// 添加更多选项
];

// 搜索加载状态
const searchLoading = ref(false);

// 重置搜索
const resetSearch = () => {
	searchForm.value = { name: '', date: [], benchmark: '', strategy: '' };
};

// 处理搜索（回测计算）
const handleSearch = () => {
	// 这里添加回测计算逻辑，例如调用API
	searchLoading.value = true;
	// 模拟异步操作
	setTimeout(() => {
		searchLoading.value = false;
		// 处理结果
	}, 2000);
};

const activeTab = ref('sheet1');
// 处理标签点击
const handleTabClick = (tab: TabsPaneContext) => {
	if (tab.paneName === 'sheet1') {
		nextTick(() => {
			
		});
	} else if (tab.paneName === 'sheet2') {
		nextTick(() => {
			
		});
	} else if (tab.paneName === 'sheet3') {
		nextTick(() => {
			
		});
	}
};

const route = useRoute();
onMounted(() => {
	// 获取模拟组合列表
	getSimulationFundList();
	nextTick(() => {
		if (route.query && route.query.id) {
			searchForm.value.name = route.query.id as string;
			// const id = route.query.id as string
			// const name = route.query.name as string
			// 把导航tag名称改为name
			// const element = document.querySelector('.layout-navbars-tagsview-ul-li.is-active span') as HTMLElement;
			// if (element) {
			//   element.textContent = name;
			// }
		}
	});
});
</script>

<style scoped lang="scss">
.backtest-container {
	padding: 10px;
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

.pagination-container {
	display: flex;
	justify-content: center;
	/* margin-top: 20px; */
	padding-top: 15px;
	border-top: 1px solid #f0f0f0;
}
</style>
