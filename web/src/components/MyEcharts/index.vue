<template>
	<div class="chart-container">
		<div v-if="props.loading" class="chart-loading">数据加载中...</div>
		<div v-else-if="!hasData" class="chart-empty">暂无数据</div>
		<div ref="chartRef" :style="chartStyle"></div>
	</div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick, computed, markRaw } from 'vue';
import { useDebounceFn, useResizeObserver } from '@vueuse/core';
import * as echarts from 'echarts';

// 组件属性
const props = defineProps({
	options: {
		type: Object,
		required: true,
	},
	width: {
		type: String,
		default: '100%',
	},
	height: {
		type: String,
		default: '400px',
	},
	theme: {
		type: [String, Object],
		default: null,
	},
	loading: {
		type: Boolean,
		default: false,
	},
	autoresize: {
		type: Boolean,
		default: true,
	},
});

// 事件定义
const emit = defineEmits(['click', 'dblclick', 'mouseover', 'ready']);

// 响应式引用
const chartRef = ref(null);
let chartInstance = null;

// 计算属性
const chartStyle = computed(() => ({
	width: props.width,
	height: props.height,
}));

const hasData = computed(() => {
	const seriesData = props.options.series;
	if (!seriesData) return false;

	if (Array.isArray(seriesData)) {
		return seriesData.some((series) => series.data && series.data.length > 0);
	}

	return false;
});

// 图表方法
const initChart = () => {
	if (!chartRef.value) return;

	if (chartInstance) {
		chartInstance.dispose();
	}

	chartInstance = markRaw(echarts.init(chartRef.value, props.theme));

	chartInstance.setOption(props.options);
	setupEvents();

	emit('ready', chartInstance);
};

const setupEvents = () => {
	if (!chartInstance) return;

	const events = [
		{ eventName: 'click', emitName: 'click' },
		{ eventName: 'dblclick', emitName: 'dblclick' },
		{ eventName: 'mouseover', emitName: 'mouseover' },
	];

	events.forEach(({ eventName, emitName }) => {
		chartInstance.on(eventName, (params) => {
			emit(emitName, params);
		});
	});
};

const resizeChart = () => {
	if (chartInstance) {
		chartInstance.resize();
	}
};

const debouncedResize = useDebounceFn(resizeChart, 500);

// 生命周期
onMounted(() => {
	nextTick(() => {
		initChart();

		// 使用 useResizeObserver 监听容器尺寸变化
		if (props.autoresize) {
			useResizeObserver(chartRef, () => {
				debouncedResize();
			});
		}
	});
});

onBeforeUnmount(() => {
	if (chartInstance) {
		chartInstance.dispose();
	}
});

// 监听器
watch(
	() => props.options,
	(newOptions) => {
		if (chartInstance) {
			chartInstance.setOption(newOptions);
		}
	},
	{ deep: true }
);

watch(
	() => props.loading,
	(loading) => {
		if (!chartInstance) return;

		if (loading) {
			chartInstance.showLoading();
		} else {
			chartInstance.hideLoading();
		}
	}
);

watch(
	() => [props.width, props.height],
	() => {
		nextTick(() => {
			resizeChart();
		});
	}
);

// 暴露方法
defineExpose({
	getInstance: () => chartInstance,
	resize: resizeChart,
	setOption: (option) => {
		if (chartInstance) {
			chartInstance.setOption(option);
		}
	},
	dispose: () => {
		if (chartInstance) {
			chartInstance.dispose();
			chartInstance = null;
		}
	},
});
</script>

<style scoped>
.chart-container {
	position: relative;
}

.chart-loading,
.chart-empty {
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
	z-index: 10;
	padding: 8px 16px;
	border-radius: 4px;
	background: rgba(255, 255, 255, 0.9);
}
</style>
