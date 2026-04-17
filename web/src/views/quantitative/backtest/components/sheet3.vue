<template>
	<div>
		<!-- 搜索条件 -->
		<div class="search-content">
			<el-form :model="searchForm" :inline="true" class="search-form">
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
				<el-form-item label="股票代码|名称" prop="stockCode">
					<el-input v-model="searchForm.stockCode" placeholder="请输入股票代码|名称" clearable style="width: 200px" />
				</el-form-item>
				<el-form-item label="交易方向">
					<el-select v-model="searchForm.direction" placeholder="请选择交易方向" clearable style="width: 200px">
						<el-option v-for="item in directionOptions" :key="item.value" :label="item.label" :value="item.value" />
					</el-select>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" @click="handleSearch" icon="Search"> 搜索 </el-button>
				</el-form-item>
			</el-form>
		</div>

		<!-- 数据表格 -->
		<el-card class="table-card custom-card" shadow="never">
			<template #header>
				<div class="card-header">
					<span>交易记录 ({{ total }})</span>
					<div class="table-actions"></div>
				</div>
			</template>

			<el-table :data="tableData" style="width: 100%" @selection-change="handleSelectionChange" height="400" v-loading="loading" size="small">
				<!-- <el-table-column type="selection" width="55" /> -->
				<el-table-column type="index" label="序号" width="60" />
				<el-table-column label="股票代码|名称" min-width="120" show-overflow-tooltip>
					<template #default="scope">
						{{ formatStockCodeName(scope.row) }}
					</template>
				</el-table-column>
				<el-table-column prop="date" label="交易日期" min-width="120" show-overflow-tooltip />
				<el-table-column label="交易方向" min-width="120" show-overflow-tooltip>
					<template #default="scope">
						<el-tag :type="scope.row.direction === 'BUY' ? 'success' : 'danger'">
							{{ formatDirection(scope.row.direction) }}
						</el-tag>
					</template>
				</el-table-column>
				<el-table-column label="交易数量" min-width="120" show-overflow-tooltip align="right">
					<template #default="scope">
						{{ formatQuantity(scope.row.quantity) }}
					</template>
				</el-table-column>
				<el-table-column label="单价（元）" min-width="120" show-overflow-tooltip align="right">
					<template #default="scope">
						{{ formatPrice(scope.row.price) }}
					</template>
				</el-table-column>
				<el-table-column label="交易金额" min-width="120" show-overflow-tooltip align="right">
					<template #default="scope">
						{{ formatAmount(scope.row.amount) }}
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

		<!-- echarts图表 -->
		<el-card shadow="never" class="custom-card">
			<ElChart :options="chartOption" width="100%" height="400px" />
		</el-card>
	</div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue';
import { getTradeRecords } from '../api';
import ElChart from '/@/components/elChart/index.vue';

// 类型定义
interface TradeRecord {
	id?: number;
	stockCode: string;
	stockName?: string;
	date: string;
	direction: string;
	quantity: number;
	price: number;
	amount: number;
}

// 交易方向选项
const directionOptions = [
	{ value: 'BUY', label: '买入' },
	{ value: 'SELL', label: '卖出' },
];

// 搜索表单
const searchForm = reactive({
	date: [],
	stockCode: '',
	direction: '',
});

// 响应式数据
const loading = ref(false);
const tableData = ref<TradeRecord[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const selectedRows = ref<TradeRecord[]>([]);

// 图表相关
const chartRef = ref();
const chartOption = ref<any>({});

// 重置搜索
const resetSearch = () => {
	searchForm.date = [];
	searchForm.stockCode = '';
	searchForm.direction = '';
	handleSearch();
};

// 处理搜索
const handleSearch = async () => {
	currentPage.value = 1;
	await loadTradeRecords();
};

// 加载交易记录数据
const loadTradeRecords = async () => {
	loadMockData();
	// loading.value = true
	// try {
	//   const params: any = {
	//     page: currentPage.value,
	//     pageSize: pageSize.value,
	//     stockCode: searchForm.stockCode,
	//     direction: searchForm.direction
	//   }

	//   // 如果日期范围存在，转换为开始和结束日期
	//   if (searchForm.date && searchForm.date.length === 2) {
	//     params.startDate = searchForm.date[0]
	//     params.endDate = searchForm.date[1]
	//   }

	//   const res = await getTradeRecords(params)
	//   if (res.code === 2000) {
	//     tableData.value = res.data.records || []
	//     total.value = res.data.total || 0
	//   } else {
	//     // 如果API调用失败，使用模拟数据
	//     console.warn('API调用失败，使用模拟数据')
	//     loadMockData()
	//   }
	// } catch (error) {
	//   console.error('获取交易记录失败:', error)
	//   // 使用模拟数据作为fallback
	//   loadMockData()
	// } finally {
	//   loading.value = false
	//   // 数据加载完成后更新图表
	//   nextTick(() => {
	//     initChart()
	//   })
	// }
};

// 加载模拟数据（fallback）
const loadMockData = () => {
	const mockData: TradeRecord[] = [
		{
			stockCode: '000001',
			stockName: '平安银行',
			date: '2024-12-01',
			direction: 'BUY',
			quantity: 1000,
			price: 12.34,
			amount: 12340,
		},
		{
			stockCode: '000002',
			stockName: '万科A',
			date: '2024-12-02',
			direction: 'SELL',
			quantity: 500,
			price: 18.56,
			amount: 9280,
		},
		{
			stockCode: '600036',
			stockName: '招商银行',
			date: '2024-12-03',
			direction: 'BUY',
			quantity: 300,
			price: 35.68,
			amount: 10704,
		},
		{
			stockCode: '600519',
			stockName: '贵州茅台',
			date: '2024-12-04',
			direction: 'BUY',
			quantity: 50,
			price: 1850.0,
			amount: 92500,
		},
		{
			stockCode: '000858',
			stockName: '五粮液',
			date: '2024-12-05',
			direction: 'SELL',
			quantity: 200,
			price: 128.9,
			amount: 25780,
		},
		{
			stockCode: '000001',
			stockName: '平安银行',
			date: '2024-12-06',
			direction: 'BUY',
			quantity: 800,
			price: 12.5,
			amount: 10000,
		},
		{
			stockCode: '000002',
			stockName: '万科A',
			date: '2024-12-07',
			direction: 'BUY',
			quantity: 300,
			price: 18.8,
			amount: 5640,
		},
		{
			stockCode: '600036',
			stockName: '招商银行',
			date: '2024-12-08',
			direction: 'SELL',
			quantity: 100,
			price: 36.2,
			amount: 3620,
		},
	];

	// 根据搜索条件过滤数据
	let filteredData = mockData;

	if (searchForm.stockCode) {
		const searchTerm = searchForm.stockCode.toLowerCase();
		filteredData = filteredData.filter(
			(item) => item.stockCode.toLowerCase().includes(searchTerm) || (item.stockName && item.stockName.toLowerCase().includes(searchTerm))
		);
	}

	if (searchForm.direction) {
		filteredData = filteredData.filter((item) => item.direction === searchForm.direction);
	}

	if (searchForm.date && searchForm.date.length === 2) {
		const [startDate, endDate] = searchForm.date;
		filteredData = filteredData.filter((item) => {
			return item.date >= startDate && item.date <= endDate;
		});
	}

	// 分页
	const startIndex = (currentPage.value - 1) * pageSize.value;
	const endIndex = startIndex + pageSize.value;
	tableData.value = filteredData.slice(startIndex, endIndex);
	total.value = filteredData.length;
};

// 表格选择变化处理
const handleSelectionChange = (selection: TradeRecord[]) => {
	selectedRows.value = selection;
};

// 处理每页大小变化
const handleSizeChange = (size: number) => {
	pageSize.value = size;
	currentPage.value = 1;
	loadTradeRecords();
};

// 处理当前页变化
const handleCurrentChange = (page: number) => {
	currentPage.value = page;
	loadTradeRecords();
};

// 格式化股票代码和名称
const formatStockCodeName = (row: TradeRecord): string => {
	return `${row.stockCode}${row.stockName ? `(${row.stockName})` : ''}`;
};

// 格式化交易方向
const formatDirection = (direction: string): string => {
	const option = directionOptions.find((item) => item.value === direction);
	return option ? option.label : direction;
};

// 格式化数量
const formatQuantity = (quantity: number): string => {
	return new Intl.NumberFormat('zh-CN').format(quantity);
};

// 格式化价格
const formatPrice = (price: number): string => {
	return `${price.toFixed(2)}`;
};

// 格式化金额
const formatAmount = (amount: number): string => {
	return `${amount.toFixed(2)}`;
};

// 初始化图表
const initChart = () => {
	const chartData = generateChartData();
	chartOption.value = {
		title: {
			text: '股票价格走势与交易点位',
			left: 'center',
			top: 10,
		},
		tooltip: {
			trigger: 'axis',
			axisPointer: {
				type: 'cross',
			},
			formatter: function (params: any) {
				let result = params[0].name + '<br/>';
				params.forEach((item: any) => {
					if (item.seriesName === '收盘价') {
						result += item.marker + item.seriesName + ': ' + item?.value?.toFixed(2) + '<br/>';
					} else if (item.seriesName === '买入点' || item.seriesName === '卖出点') {
						result += item.marker + item.seriesName + ': ' + item + '<br/>';
					}
				});
				return result;
			},
		},
		legend: {
			data: ['收盘价', '买入点', '卖出点'],
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
			boundaryGap: false,
			data: chartData.dates,
			axisLabel: {
				formatter: function (value: string) {
					// 只显示月份标签，避免拥挤
					const date = new Date(value);
					return date.getMonth() + 1 + '月';
				},
				interval: 29, // 每30天显示一个标签
			},
		},
		yAxis: {
			type: 'value',
			axisLabel: {
				formatter: '{value}元',
			},
			scale: true,
		},
		series: [
			{
				name: '收盘价',
				type: 'line',
				data: chartData.prices,
				smooth: true,
				symbol: 'none',
				lineStyle: {
					color: '#5470c6',
					width: 2,
				},
				areaStyle: {
					color: {
						type: 'linear',
						x: 0,
						y: 0,
						x2: 0,
						y2: 1,
						colorStops: [
							{
								offset: 0,
								color: 'rgba(84, 112, 198, 0.3)',
							},
							{
								offset: 1,
								color: 'rgba(84, 112, 198, 0.1)',
							},
						],
					},
				},
			},
			{
				name: '买入点',
				type: 'scatter',
				data: chartData.buyPoints,
				symbol: 'triangle',
				symbolSize: 10,
				itemStyle: {
					color: '#67c23a',
				},
				tooltip: {
					formatter: function (params: any) {
						return `买入点<br/>日期: ${params.name}<br/>价格: ${params.value}元`;
					},
				},
			},
			{
				name: '卖出点',
				type: 'scatter',
				data: chartData.sellPoints,
				symbol: 'triangle',
				symbolRotate: 180,
				symbolSize: 10,
				itemStyle: {
					color: '#f56c6c',
				},
				tooltip: {
					formatter: function (params: any) {
						return `卖出点<br/>日期: ${params.name}<br/>价格: ${params.value}元`;
					},
				},
			},
		],
	};
};

// 生成图表数据
const generateChartData = () => {
	const endDate = new Date();
	const startDate = new Date();
	startDate.setFullYear(endDate.getFullYear() - 1);

	const dates: string[] = [];
	const prices: number[] = [];
	const buyPoints: Array<[string, number]> = [];
	const sellPoints: Array<[string, number]> = [];

	// 生成近一年的日期和价格数据
	let currentDate = new Date(startDate);
	let basePrice = 15.0; // 基准价格

	while (currentDate <= endDate) {
		const dateStr = currentDate.toISOString().split('T')[0];
		dates.push(dateStr);

		// 生成价格数据（加入随机波动）
		const randomChange = (Math.random() - 0.5) * 0.1; // -5% 到 +5% 的随机变化
		basePrice = basePrice * (1 + randomChange);

		// 确保价格在合理范围内
		basePrice = Math.max(8.0, Math.min(25.0, basePrice));
		prices.push(Number(basePrice.toFixed(2)));

		currentDate.setDate(currentDate.getDate() + 1);
	}

	// 从交易记录中提取交易点位
	tableData.value.forEach((record) => {
		const dateIndex = dates.indexOf(record.date);
		if (dateIndex !== -1) {
			const price = prices[dateIndex]; // 使用对应日期的收盘价
			if (record.direction === 'BUY') {
				buyPoints.push([record.date, price]);
			} else if (record.direction === 'SELL') {
				sellPoints.push([record.date, price]);
			}
		}
	});

	return {
		dates,
		prices,
		buyPoints,
		sellPoints,
	};
};

// 生命周期
onMounted(() => {
	loadTradeRecords();
	nextTick(() => {
		initChart();
	});
});

// 暴露方法
defineExpose({});
</script>

<style scoped lang="scss">
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
	background-color: #f8f9fa;
	border-radius: 6px;
	padding: 15px;
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
	padding-top: 15px;
	border-top: 1px solid #f0f0f0;
}

.custom-card {
	.el-card__header {
		background-color: #fafafa;
		border-bottom: 1px solid #e8e8e8;
		padding: 12px 20px;
	}

	.el-card__body {
		padding: 20px;
	}
}

// 表格样式
.el-table {
	.el-table__header th {
		background-color: #fafafa;
		color: #606266;
		font-weight: 500;
	}

	.el-table__row {
		&:hover {
			background-color: #f5f7fa;
		}
	}
}

// 响应式设计
@media (max-width: 768px) {
	.search-form {
		.el-form-item {
			display: block;
			margin-right: 0;
			margin-bottom: 10px;
		}
	}

	.card-header {
		flex-direction: column;
		align-items: flex-start;
		gap: 10px;
	}
}

// 标签样式
.el-tag {
	font-size: 12px;
}
</style>
