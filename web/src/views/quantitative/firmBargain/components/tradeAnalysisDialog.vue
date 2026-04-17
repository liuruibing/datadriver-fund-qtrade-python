<!--
 * @Description: 交易分析弹窗
 * @Author: 
 * @Date: 2025-12-05 10:25:41
 * @LastEditors: Please set LastEditors
 * @LastEditTime: 2025-12-10 16:40:42
-->
<template>
  <el-dialog
    v-model="dialogVisible"
    title="交易分析"
    width="90%"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-row :gutter="10">
      <el-col :span="18">
        <div class="chart-box">
          <ElChart
            :options="chartOption"
            width="100%"
            height="600px"
          />
        </div>
      </el-col>
      <el-col :span="6">
        <div>交易明细</div>
        <el-table
          :data="tableData"
          style="width: 100%"
          size="small"
          height="600px"
        >
          <el-table-column
            prop="date"
            label="日期"
          />
          <el-table-column
            prop="direction"
            label="交易方向"
          />
          <el-table-column
            prop="price"
            label="成交价"
          />
          <el-table-column
            prop="quantity"
            label="成交量"
          />
          <el-table-column
            prop="amount"
            label="成交额"
          />
        </el-table>
      </el-col>
    </el-row>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import ElChart from '/@/components/elChart/index.vue';

interface Props {
	visible: boolean;
	rowData?: any;
}

const props = withDefaults(defineProps<Props>(), {
	visible: false,
	rowData: null,
});

const emit = defineEmits<{
	'update:visible': [value: boolean];
	close: [];
}>();

// 响应式数据
const dialogVisible = ref(false);

// 监听弹窗显示状态
watch(
	() => props.visible,
	(newVal) => {
		dialogVisible.value = newVal;
	}
);

watch(dialogVisible, (newVal) => {
	emit('update:visible', newVal);
	if (!newVal) {
		emit('close');
	}
});

// 关闭弹窗
const handleClose = () => {
	dialogVisible.value = false;
};

const tableData = ref<any[]>([]);
const tableLoading = ref(false);

// 生成近6个月的逼真交易数据
const generateTradeData = () => {
	const data = [];
	const now = new Date();
	const sixMonthsAgo = new Date(now.getTime() - 6 * 30 * 24 * 60 * 60 * 1000); // 近6个月

	// 基础股价，模拟从某个价格开始波动
	let basePrice = 85 + Math.random() * 30; // 85-115之间的随机起始价
	const trades = [];

	// 生成交易记录
	for (let i = 0; i < 45; i++) {
		// 大约45个交易日
		const tradeDate = new Date(sixMonthsAgo.getTime() + Math.random() * (now.getTime() - sixMonthsAgo.getTime()));
		const isBuy = Math.random() > 0.4; // 60%概率买入，40%卖出

		// 价格有小幅波动
		const priceChange = (Math.random() - 0.5) * 8; // -4到+4的波动
		basePrice = Math.max(50, Math.min(150, basePrice + priceChange)); // 限制在50-150区间
		const price = Math.round(basePrice * 100) / 100; // 保留两位小数

		const quantity = Math.floor(Math.random() * 500) + 100; // 100-600手
		const amount = Math.round(price * quantity * 100) / 100;

		trades.push({
			date: tradeDate.toISOString().split('T')[0],
			direction: isBuy ? '买入' : '卖出',
			price,
			quantity,
			amount,
			timestamp: tradeDate.getTime(),
		});
	}

	// 按日期排序
	return trades.sort((a, b) => a.timestamp - b.timestamp);
};

const getTableData = async () => {
	tableLoading.value = true;
	tableData.value = generateTradeData();
	tableLoading.value = false;
};

const chartOption = ref<any>({});

// 生成图表数据
const generateChartData = (): { dates: string[]; prices: number[]; buyPoints: any[]; sellPoints: any[] } => {
	if (tableData.value.length === 0) return { dates: [], prices: [], buyPoints: [], sellPoints: [] };

	const sortedData = [...tableData.value].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

	// 生成每日价格数据（基于交易数据插值）
	const dates: string[] = [];
	const prices: number[] = [];
	const buyPoints: any[] = [];
	const sellPoints: any[] = [];

	let currentPrice = sortedData[0].price;
	const startDate = new Date(sortedData[0].date);
	const endDate = new Date(sortedData[sortedData.length - 1].date);

	// 生成日期序列（工作日）
	for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
		const dayOfWeek = d.getDay();
		if (dayOfWeek !== 0 && dayOfWeek !== 6) {
			// 跳过周末
			dates.push(d.toISOString().split('T')[0]);

			// 检查当天是否有交易
			const tradesOnDay = sortedData.filter((trade) => trade.date === d.toISOString().split('T')[0]);

			if (tradesOnDay.length > 0) {
				// 当天有交易，使用交易价作为收盘价
				currentPrice = tradesOnDay[tradesOnDay.length - 1].price;

				// 记录买入卖出点
				tradesOnDay.forEach((trade) => {
					const point = {
						name: `${trade.direction} ${trade.price}`,
						value: [d.toISOString().split('T')[0], trade.price],
						itemStyle: {
							color: trade.direction === '买入' ? '#00C853' : '#D32F2F',
						},
						symbol: trade.direction === '买入' ? 'triangle' : 'diamond',
						symbolSize: 10,
					};

					if (trade.direction === '买入') {
						buyPoints.push(point);
					} else {
						sellPoints.push(point);
					}
				});
			} else {
				// 当天无交易，小幅随机波动
				const change = (Math.random() - 0.5) * 0.02; // ±1%的波动
				currentPrice = currentPrice * (1 + change);
				currentPrice = Math.round(currentPrice * 100) / 100;
			}

			prices.push(currentPrice);
		}
	}

	return { dates, prices, buyPoints, sellPoints };
};

const initChartOption = () => {
	const { dates, prices, buyPoints, sellPoints } = generateChartData();

	chartOption.value = {
		title: {
			text: '交易记录走势分析',
			left: 'center',
			textStyle: {
				fontSize: 16,
				fontWeight: 'bold',
			},
		},
		tooltip: {
			trigger: 'axis',
			axisPointer: {
				type: 'cross',
				lineStyle: {
					color: '#666',
					width: 1,
				},
			},
			formatter: function (params: any) {
				let result = `${params[0].name}<br/>`;
				params.forEach((param: any) => {
					if (param.seriesName === '股价走势') {
						result += `${param.seriesName}: ${param.value}元<br/>`;
					} else {
						result += `${param.seriesName}: ${param.value[1]}元<br/>`;
					}
				});
				return result;
			},
		},
		legend: {
			data: ['股价走势', '买入点', '卖出点'],
			top: 30,
		},
		grid: {
			left: '3%',
			right: '4%',
			bottom: '10%',
			containLabel: true,
		},
		xAxis: {
			type: 'category',
			boundaryGap: false,
			data: dates,
			axisLabel: {
				rotate: 45,
				formatter: function (value: string) {
					return value; // 直接显示 yyyy-mm-dd 格式
				},
			},
		},
		yAxis: {
			type: 'value',
			name: '价格(元)',
			axisLabel: {
				formatter: '{value}元',
			},
		},
		series: [
			{
				name: '股价走势',
				type: 'line',
				data: prices,
				smooth: true,
				lineStyle: {
					color: '#2196F3',
					width: 2,
				},
				// areaStyle: {
				//   color: {
				//     type: 'linear',
				//     x: 0,
				//     y: 0,
				//     x2: 0,
				//     y2: 1,
				//     colorStops: [{
				//       offset: 0, color: 'rgba(33, 150, 243, 0.3)'
				//     }, {
				//       offset: 1, color: 'rgba(33, 150, 243, 0.1)'
				//     }]
				//   }
				// },
				symbol: 'none',
			},
			{
				name: '买入点',
				type: 'scatter',
				data: buyPoints.map((point) => point.value),
				symbol: 'triangle',
				symbolSize: 12,
				itemStyle: {
					color: '#FF0000',
				},
				tooltip: {
					formatter: function (param: any) {
						return `买入: ${param.value[1]}元`;
					},
				},
			},
			{
				name: '卖出点',
				type: 'scatter',
				data: sellPoints.map((point) => point.value),
				symbol: 'triangle',
				symbolSize: 12,
        symbolRotate: 180,
				itemStyle: {
					color: '#008000',
				},
				tooltip: {
					formatter: function (param: any) {
						return `卖出: ${param.value[1]}元`;
					},
				},
			},
		],
	};
};

// 监听数据变化，更新图表
watch(tableData, () => {
	initChartOption();
});

onMounted(() => {
	getTableData();
});
</script>

<style scoped lang="scss">
.chart-box {
	width: 100%;
	height: 600px;
	border: 1px solid #e5e5e5;
	border-radius: 4px;
	padding: 10px;
	margin-top: 10px;
}
</style>
