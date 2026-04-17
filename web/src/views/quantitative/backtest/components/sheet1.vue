<template>
	<div>
		<el-card shadow="never" class="custom-card" style="margin-bottom: 10px">
			<ElChart :options="chartOption" width="100%" height="400px" />
		</el-card>
		<!-- 设置每行4个卡片，用grid布局 -->
		<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px">
			<el-card shadow="hover" class="indicator-card custom-card">近一月收益：{{ recentMonthReturn }}%</el-card>
			<el-card shadow="hover" class="indicator-card custom-card">近三月收益：{{ recentThreeMonthsReturn }}%</el-card>
			<el-card shadow="hover" class="indicator-card custom-card">近半年收益：{{ recentSixMonthsReturn }}%</el-card>
			<el-card shadow="hover" class="indicator-card custom-card">近一年收益：{{ recentYearReturn }}%</el-card>
			<el-card shadow="hover" class="indicator-card custom-card">近一月基准收益：{{ recentMonthBenchmark }}%</el-card>
			<el-card shadow="hover" class="indicator-card custom-card">近三月基准收益：{{ recentThreeMonthsBenchmark }}%</el-card>
			<el-card shadow="hover" class="indicator-card custom-card">近半年基准收益：{{ recentSixMonthsBenchmark }}%</el-card>
			<el-card shadow="hover" class="indicator-card custom-card">近一年基准收益：{{ recentYearBenchmark }}%</el-card>
			<el-card shadow="hover" class="indicator-card custom-card">近一月超额收益：{{ recentMonthExcess }}%</el-card>
			<el-card shadow="hover" class="indicator-card custom-card">近三月超额收益：{{ recentThreeMonthsExcess }}%</el-card>
			<el-card shadow="hover" class="indicator-card custom-card">近半年超额收益：{{ recentSixMonthsExcess }}%</el-card>
			<el-card shadow="hover" class="indicator-card custom-card">近一年超额收益：{{ recentYearExcess }}%</el-card>
			<el-card shadow="hover" class="indicator-card custom-card">最大回撤：{{ maxDrawdown }}%</el-card>
			<el-card shadow="hover" class="indicator-card custom-card">最大回撤恢复期：{{ maxDrawdownRecovery }} 天</el-card>
			<el-card shadow="hover" class="indicator-card custom-card">夏普比率：{{ sharpeRatio }}</el-card>
		</div>
	</div>
</template>

<script setup>
import { onMounted, ref, nextTick, markRaw } from 'vue';
import ElChart from '/@/components/elChart/index.vue';

// 数据占位符，实际应从props或store获取
const recentMonthReturn = ref(5.2);
const recentThreeMonthsReturn = ref(15.1);
const recentSixMonthsReturn = ref(25.3);
const recentYearReturn = ref(45.7);

const recentMonthBenchmark = ref(4.8);
const recentThreeMonthsBenchmark = ref(14.2);
const recentSixMonthsBenchmark = ref(24.1);
const recentYearBenchmark = ref(42.5);

const recentMonthExcess = ref(0.4);
const recentThreeMonthsExcess = ref(0.9);
const recentSixMonthsExcess = ref(1.2);
const recentYearExcess = ref(3.2);

const maxDrawdown = ref(10.5);
const maxDrawdownRecovery = ref(45);
const sharpeRatio = ref(1.2);

// ECharts 配置
onMounted(() => {
	nextTick(() => {
		initChart();
	});
});

const chartOption = ref({});

const initChart = () => {
	const dates = [
		'2024-01-01',
		'2024-01-11',
		'2024-01-21',
		'2024-02-01',
		'2024-02-11',
		'2024-02-21',
		'2024-03-01',
		'2024-03-11',
		'2024-03-21',
		'2024-04-01',
		'2024-04-11',
		'2024-04-21',
		'2024-05-01',
		'2024-05-11',
		'2024-05-21',
		'2024-06-01',
		'2024-06-11',
		'2024-06-21',
		'2024-07-01',
		'2024-07-11',
		'2024-07-21',
		'2024-08-01',
		'2024-08-11',
		'2024-08-21',
		'2024-09-01',
		'2024-09-11',
		'2024-09-21',
		'2024-10-01',
		'2024-10-11',
		'2024-10-21',
		'2024-11-01',
		'2024-11-11',
		'2024-11-21',
		'2024-12-01',
		'2024-12-11',
		'2024-12-21',
		'2025-01-01',
		'2025-01-11',
		'2025-01-21',
		'2025-02-01',
		'2025-02-11',
		'2025-02-21',
		'2025-03-01',
		'2025-03-11',
		'2025-03-21',
		'2025-04-01',
		'2025-04-11',
		'2025-04-21',
		'2025-05-01',
		'2025-05-11',
		'2025-05-21',
		'2025-06-01',
		'2025-06-11',
		'2025-06-21',
		'2025-07-01',
		'2025-07-11',
		'2025-07-21',
		'2025-08-01',
		'2025-08-11',
		'2025-08-21',
		'2025-09-01',
		'2025-09-11',
		'2025-09-21',
		'2025-10-01',
		'2025-10-11',
		'2025-10-21',
		'2025-11-01',
		'2025-11-11',
		'2025-11-21',
		'2025-12-01',
		'2025-12-11',
		'2025-12-21',
		'2026-01-01',
		'2026-01-11',
		'2026-01-21',
		'2026-02-01',
		'2026-02-11',
		'2026-02-21',
		'2026-03-01',
		'2026-03-11',
		'2026-03-21',
		'2026-04-01',
		'2026-04-11',
		'2026-04-21',
		'2026-05-01',
		'2026-05-11',
		'2026-05-21',
		'2026-06-01',
		'2026-06-11',
		'2026-06-21',
		'2026-07-01',
		'2026-07-11',
		'2026-07-21',
		'2026-08-01',
		'2026-08-11',
		'2026-08-21',
		'2026-09-01',
		'2026-09-11',
		'2026-09-21',
		'2026-10-01',
		'2026-10-11',
		'2026-10-21',
		'2026-11-01',
		'2026-11-11',
		'2026-11-21',
		'2026-12-01',
		'2026-12-11',
		'2026-12-21',
	];

	const option = {
		grid: {
			left: '3%',
			right: '4%',
			bottom: '3%',
			containLabel: true,
		},
		title: { text: '净值走势', left: 'center' },
		tooltip: {
			trigger: 'axis',
			formatter: function (params) {
				let result = params[0].name + '<br/>';
				params.forEach(function (item) {
					result += item.marker + item.seriesName + ': ' + item.value.toFixed(2) + '<br/>';
				});
				return result;
			},
		},
		legend: { data: ['模拟组合', '基准'], top: 30 },
		xAxis: {
			type: 'category',
			data: dates,
			// axisLabel: {
			//   rotate: 45,
			//   interval: 8  // 每8个显示一个标签，避免拥挤
			// }
		},
		yAxis: {
			type: 'value',
			axisLabel: {
				formatter: '{value}%',
			},
		},
		series: [
			{
				name: '模拟组合',
				type: 'line',
				data: [
					// 2024年 - 震荡上涨
					100.0, 101.5, 103.2, 102.8, 104.5, 106.2, 105.8, 107.6, 109.4, 108.9, 110.8, 112.7, 112.2, 114.2, 116.3, 115.7, 117.9, 120.2, 119.5, 121.8,
					124.2, 123.4, 125.8, 128.3, 127.5, 130.0, 132.6, 131.7, 134.3, 137.0, 136.0, 138.7, 141.5, 140.4, 143.2, 146.1,
					// 2025年 - 回调后反弹
					145.0, 143.5, 141.8, 143.2, 141.6, 139.8, 141.3, 139.5, 137.6, 139.2, 137.3, 135.4, 137.1, 135.1, 133.0, 134.8, 136.7, 138.6, 140.5, 142.5,
					144.6, 142.8, 144.9, 147.1, 149.3, 151.6, 149.8, 152.1, 154.5, 156.9, 159.4, 161.9, 164.5, 162.7, 165.3, 168.0,
					// 2026年 - 持续震荡
					166.8, 169.6, 172.5, 175.5, 173.7, 176.6, 179.6, 177.8, 180.7, 183.7, 181.8, 184.8, 187.9, 190.1, 188.2, 191.3, 194.5, 192.6, 195.8, 199.1,
					201.4, 204.8, 207.2, 210.7, 213.2, 211.3, 214.7, 218.2, 221.8, 219.8, 223.3, 226.9, 230.6, 233.3, 236.1, 239.0,
				],
				smooth: true,
				itemStyle: { color: '#5470c6' },
				lineStyle: { width: 2 },
			},
			{
				name: '基准',
				type: 'line',
				data: [
					// 2024年 - 稳步上涨
					100.0, 101.2, 102.5, 103.8, 105.2, 106.6, 108.0, 109.5, 111.0, 112.6, 114.2, 115.8, 117.5, 119.2, 120.9, 122.7, 124.5, 126.4, 128.3, 130.2,
					132.2, 134.2, 136.2, 138.3, 140.4, 142.5, 144.7, 146.9, 149.1, 151.4, 153.7, 156.0, 158.4, 160.8, 163.2, 165.6,
					// 2025年 - 小幅回调
					164.2, 162.8, 161.4, 162.9, 161.5, 160.1, 161.6, 160.2, 158.8, 160.3, 158.9, 157.5, 159.0, 160.5, 162.1, 163.7, 165.3, 167.0, 168.7, 170.4,
					172.2, 173.9, 175.7, 177.5, 179.3, 181.2, 183.1, 184.9, 186.8, 188.7, 190.6, 192.5, 194.5, 196.4, 198.4, 200.4,
					// 2026年 - 稳定增长
					202.4, 204.4, 206.5, 208.6, 210.7, 212.8, 215.0, 217.2, 219.4, 221.6, 223.9, 226.2, 228.5, 230.8, 233.2, 235.6, 238.0, 240.4, 242.9, 245.4,
					247.9, 250.4, 252.9, 255.5, 258.1, 260.7, 263.3, 266.0, 268.7, 271.4, 274.1, 276.8, 279.6, 282.4, 285.2, 288.0,
				],
				smooth: true,
				itemStyle: { color: '#91cc75' },
				lineStyle: { width: 2 },
			},
		],
	};
	chartOption.value = option;
};

// 暴露方法
defineExpose({});
</script>

<style scoped lang="scss">
.indicator-card {
	background-color: #fafafa;
}

#chart {
	margin-bottom: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
	.row {
		flex-direction: column;
		align-items: flex-start;
	}

	.row span {
		text-align: left;
		margin-bottom: 5px;
	}
}
</style>
