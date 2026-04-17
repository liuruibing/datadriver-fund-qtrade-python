<template>
	<div>
		<el-card shadow="never" class="custom-card" style="margin-bottom: 10px">
			<ElChart :options="chartOption" width="100%" height="400px" @click="handleChartClick" />
		</el-card>
		<!-- 数据表格 -->
		<el-card class="table-card custom-card" shadow="never">
			<template #header>
				<div class="card-header">
					<span>
						<span>持仓股票列表 ({{ total }})</span>
						<span style="margin-left: 20px">日期：{{ dataDate }}</span>
					</span>
					<div class="table-actions"></div>
				</div>
			</template>

			<el-table :data="tableData" style="width: 100%" @selection-change="handleSelectionChange" height="400" v-loading="loading" size="small">
				<el-table-column type="index" label="序号" width="60" />
				<el-table-column prop="stockCode" label="股票代码" width="120" show-overflow-tooltip>
					<template #default="scope">
						<span class="stock-code">{{ scope.row.stockCode }}</span>
					</template>
				</el-table-column>
				<el-table-column prop="stockName" label="股票名称" min-width="120" show-overflow-tooltip />
				<el-table-column prop="position" label="持仓数量" min-width="120" show-overflow-tooltip> </el-table-column>
				<el-table-column prop="price" label="单价(元)" min-width="120" show-overflow-tooltip> </el-table-column>
				<el-table-column prop="marketValue" label="市值(元)" min-width="120" show-overflow-tooltip> </el-table-column>
				<el-table-column prop="positionRatio" label="仓位(%)" min-width="100" show-overflow-tooltip> </el-table-column>
			</el-table>
		</el-card>
	</div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, markRaw } from 'vue';
import { getPositionData, getPositionTimeline } from '../api';
import ElChart from '/@/components/elChart/index.vue';

// 类型定义
interface PositionItem {
	id?: number;
	stockCode: string;
	stockName: string;
	position: number;
	price: number;
	marketValue: number;
	positionRatio: number;
	date?: string;
}

// 响应式数据
const loading = ref(false);
const tableData = ref<PositionItem[]>([]);
const total = ref(0);
const selectedRows = ref<PositionItem[]>([]);
const dataDate = ref('');

// 图表相关
const chartOption = ref<any>({});

// 初始化持仓数据
const initPositionData = async () => {
	loadMockData();
	// loading.value = true
	// try {
	//   const res = await getPositionData()
	//   if (res.code === 2000) {
	//     tableData.value = res.data || []
	//     total.value = tableData.value.length
	//   } else {
	//     // 如果API调用失败，使用模拟数据
	//     console.warn('API调用失败，使用模拟数据')
	//     loadMockData()
	//   }
	// } catch (error) {
	//   console.error('获取持仓数据失败:', error)
	//   // 使用模拟数据作为fallback
	//   loadMockData()
	// } finally {
	//   loading.value = false
	// }
};

// 加载模拟数据（fallback）
const loadMockData = () => {
	tableData.value = [
		{
			stockCode: '000001',
			stockName: '平安银行',
			position: 1000,
			price: 12.34,
			marketValue: 12340,
			positionRatio: 15.2,
		},
		{
			stockCode: '000002',
			stockName: '万科A',
			position: 800,
			price: 18.56,
			marketValue: 14848,
			positionRatio: 12.1,
		},
		{
			stockCode: '600036',
			stockName: '招商银行',
			position: 600,
			price: 35.68,
			marketValue: 21408,
			positionRatio: 17.4,
		},
		{
			stockCode: '600519',
			stockName: '贵州茅台',
			position: 100,
			price: 1850.0,
			marketValue: 185000,
			positionRatio: 15.1,
		},
		{
			stockCode: '000858',
			stockName: '五粮液',
			position: 400,
			price: 128.9,
			marketValue: 51560,
			positionRatio: 4.2,
		},
	];
	total.value = tableData.value.length;
};

// 图表初始化
const initChart = async () => {
	renderChartWithMockData();
	// try {
	//   // 尝试获取时序数据
	//   const res = await getPositionTimeline()
	//   if (res.code === 2000 && res.data) {
	//     renderChartWithData(res.data)
	//   } else {
	//     // 使用模拟数据
	//     renderChartWithMockData()
	//   }
	// } catch (error) {
	//   console.error('获取时序数据失败:', error)
	//   // 使用模拟数据
	//   renderChartWithMockData()
	// }
};

// 使用API数据渲染图表
const renderChartWithData = (data: any) => {
	const option = {
		title: {
			text: '持仓时序',
			left: 'center',
		},
		tooltip: {
			trigger: 'axis',
			axisPointer: {
				type: 'cross',
			},
		},
		legend: {
			data: data.legend || [],
			top: 30,
		},
		grid: {
			left: '3%',
			right: '4%',
			bottom: '3%',
			containLabel: true,
		},
		xAxis: {
			type: 'category',
			boundaryGap: true,
			data: data.dates || [],
		},
		yAxis: {
			type: 'value',
			name: '持仓市值',
			axisLabel: {
				formatter: '{value}',
			},
		},
		series: data.series || [],
	};

};

// 使用模拟数据渲染图表
const renderChartWithMockData = () => {
	const dates = [
		'2024-01-01',
		'2024-01-15',
		'2024-02-01',
		'2024-02-15',
		'2024-03-01',
		'2024-03-15',
		'2024-04-01',
		'2024-04-15',
		'2024-05-01',
		'2024-05-15',
		'2024-06-01',
		'2024-06-15',
		'2024-07-01',
		'2024-07-15',
		'2024-08-01',
		'2024-08-15',
		'2024-09-01',
		'2024-09-15',
		'2024-10-01',
		'2024-10-15',
		'2024-11-01',
		'2024-11-15',
		'2024-12-01',
		'2024-12-15',
		'2025-01-01',
		'2025-01-15',
		'2025-02-01',
		'2025-02-15',
		'2025-03-01',
		'2025-03-15',
		'2025-04-01',
		'2025-04-15',
		'2025-05-01',
		'2025-05-15',
		'2025-06-01',
		'2025-06-15',
	];

	const option = {
		title: {
			text: '持仓时序',
			left: 'center',
		},
		tooltip: {
			trigger: 'axis',
			axisPointer: {
				type: 'cross',
			},
		},
		legend: {
			data: ['平安银行', '万科A', '招商银行', '贵州茅台', '五粮液'],
			top: 30,
		},
		grid: {
			left: '3%',
			right: '4%',
			bottom: '3%',
			containLabel: true,
		},
		xAxis: {
			type: 'category',
			boundaryGap: true,
			data: dates,
		},
		yAxis: {
			type: 'value',
			name: '持仓市值',
			axisLabel: {
				formatter: '{value}',
				// formatter: '{value} 股'
			},
		},
		series: [
			{
				name: '平安银行',
				type: 'bar',
				data: [
					800, 850, 900, 950, 1000, 1050, 950, 1000, 1050, 1100, 1000, 1050, 1100, 1150, 1000, 1050, 1100, 1150, 1000, 1050, 1100, 1150, 1000, 1050,
					1100, 1150, 1000, 1050, 1100, 1150, 1000, 1050, 1100, 1150, 1000, 1050,
				],
				stack: 'stack1',
			},
			{
				name: '万科A',
				type: 'bar',
				data: [
					600, 650, 700, 750, 800, 850, 750, 800, 850, 900, 800, 850, 900, 950, 800, 850, 900, 950, 800, 850, 900, 950, 800, 850, 900, 950, 800, 850,
					900, 950, 800, 850, 900, 950, 800, 850,
				],
				stack: 'stack1',
			},
			{
				name: '招商银行',
				type: 'bar',
				data: [
					500, 525, 550, 575, 600, 625, 580, 600, 625, 650, 600, 625, 650, 675, 600, 625, 650, 675, 600, 625, 650, 675, 600, 625, 650, 675, 600, 625,
					650, 675, 600, 625, 650, 675, 600, 625,
				],
				stack: 'stack1',
			},
			{
				name: '贵州茅台',
				type: 'bar',
				data: [
					80, 82, 85, 87, 90, 92, 95, 97, 100, 102, 95, 97, 100, 102, 95, 97, 100, 102, 95, 97, 100, 102, 95, 97, 100, 102, 95, 97, 100, 102, 95, 97,
					100, 102, 95, 97,
				],
				stack: 'stack1',
			},
			{
				name: '五粮液',
				type: 'bar',
				data: [
					300, 325, 350, 375, 400, 425, 380, 400, 425, 450, 400, 425, 450, 475, 400, 425, 450, 475, 400, 425, 450, 475, 400, 425, 450, 475, 400, 425,
					450, 475, 400, 425, 450, 475, 400, 425,
				],
				stack: 'stack1',
			},
		],
	};
	chartOption.value = option;
};

// 表格选择变化处理
const handleSelectionChange = (selection: PositionItem[]) => {
	selectedRows.value = selection;
};

// 图表点击事件处理
const handleChartClick = async (params: any) => {
	console.log('图表点击事件', params);

	// 只处理xAxis（日期轴）的点击
	if (params.componentType === 'series') {
		const clickedDate = params.name;
		console.log('点击的日期:', clickedDate);
		dataDate.value = clickedDate;
		// 根据日期获取对应持仓数据
		// await loadPositionDataByDate(clickedDate)
	}
};

// 根据日期加载持仓数据
const loadPositionDataByDate = async (date: string) => {
	loading.value = true;
	try {
		const res = await getPositionData({ date });
		if (res.code === 2000) {
			tableData.value = res.data || [];
			total.value = tableData.value.length;
		} else {
			console.warn('根据日期获取持仓数据失败');
			// 如果失败，保持当前数据或显示空数据
			tableData.value = [];
			total.value = 0;
		}
	} catch (error) {
		console.error('根据日期获取持仓数据失败:', error);
		// 失败时清空数据或保持当前数据
		tableData.value = [];
		total.value = 0;
	} finally {
		loading.value = false;
	}
};

// 格式化数字
const formatNumber = (num: number): string => {
	return new Intl.NumberFormat('zh-CN').format(num);
};

// 格式化货币
const formatCurrency = (amount: number): string => {
	return new Intl.NumberFormat('zh-CN', {
		style: 'currency',
		currency: 'CNY',
		minimumFractionDigits: 2,
		maximumFractionDigits: 2,
	}).format(amount);
};

// 格式化百分比
const formatPercent = (ratio: number): string => {
	return `${ratio.toFixed(2)}%`;
};

// 生命周期
onMounted(async () => {
	console.log('sheet2 生命周期');

	await initPositionData();
	nextTick(() => {
		initChart();
	});
});

// 暴露方法
defineExpose({});
</script>

<style scoped lang="scss">
.table-card {
	margin-bottom: 10px;
}

.card-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.table-actions {
	display: flex;
	gap: 10px;
}

/* 图表容器样式 */
#chart {
	margin-bottom: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
	.card-header {
		flex-direction: column;
		align-items: flex-start;
		gap: 10px;
	}

	.table-actions {
		width: 100%;
		justify-content: flex-start;
	}
}

/* 数字格式化样式 */
.position-value {
	font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
	font-weight: 500;
}

.positive {
	color: #67c23a;
}

.negative {
	color: #f56c6c;
}
</style>
