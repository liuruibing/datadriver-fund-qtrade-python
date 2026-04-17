<template>
	<div ref="chartRef" class="el-chart" :style="{ width, height }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick, markRaw } from 'vue';
import * as echarts from 'echarts';

// 定义props
interface Props {
	options: any;
	width?: string;
	height?: string;
	autoResize?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
	width: '100%',
	height: '400px',
	autoResize: true,
});

// 定义emits
const emit = defineEmits<{
	click: [params: any];
}>();

// 暴露echarts实例
const chartRef = ref<HTMLElement>();
const chartInstance = ref<echarts.ECharts>();
let resizeObserver: ResizeObserver | null = null;
let intersectionObserver: IntersectionObserver | null = null;
let debounceTimeout: number | null = null;
let isComponentMounted = false;

// 获取echarts实例的方法
const getEchartsInstance = () => chartInstance.value;

// 防抖函数
const debounce = (func: Function, delay: number) => {
	return (...args: any[]) => {
		if (debounceTimeout) {
			clearTimeout(debounceTimeout);
		}
		debounceTimeout = window.setTimeout(() => {
			if (isComponentMounted) {
				func.apply(null, args);
			}
		}, delay);
	};
};

// 窗口大小改变处理（带防抖）
const handleResize = debounce(() => {
	if (isComponentMounted && chartInstance.value && props.autoResize) {
		chartInstance.value.resize();
	}
}, 100);

// 初始化ResizeObserver监听容器大小变化
const initResizeObserver = () => {
	if (!chartRef.value || !props.autoResize || !isComponentMounted) return;

	resizeObserver = new ResizeObserver(() => {
		if (isComponentMounted) {
			handleResize();
		}
	});
	resizeObserver.observe(chartRef.value);
};

// 初始化IntersectionObserver监听元素可见性变化
const initIntersectionObserver = () => {
	if (!chartRef.value || !isComponentMounted) return;

	intersectionObserver = new IntersectionObserver(
		(entries) => {
			entries.forEach((entry) => {
				// 当元素变为可见时，延迟一点时间再调整尺寸，确保DOM已经完全渲染
				if (entry.isIntersecting && isComponentMounted) {
					nextTick(() => {
						if (isComponentMounted && chartInstance.value) {
							chartInstance.value.resize();
						}
					});
				}
			});
		},
		{
			threshold: 0,
			rootMargin: '0px',
		}
	);
	intersectionObserver.observe(chartRef.value);
};

// 销毁IntersectionObserver
const destroyIntersectionObserver = () => {
	if (intersectionObserver) {
		intersectionObserver.disconnect();
		intersectionObserver = null;
	}
};

// 销毁ResizeObserver
const destroyResizeObserver = () => {
	if (resizeObserver) {
		resizeObserver.disconnect();
		resizeObserver = null;
	}
};

// 初始化图表
const initChart = () => {
	if (!chartRef.value) return;

	chartInstance.value = markRaw(echarts.init(chartRef.value));

	// 设置options
	if (props.options) {
		chartInstance.value.setOption(props.options);
	}

	// 监听点击事件
	chartInstance.value.on('click', (params: any) => {
		emit('click', params);
	});

	// 初始化ResizeObserver
	initResizeObserver();

	// 初始化IntersectionObserver
	initIntersectionObserver();
};

// 清理防抖定时器
const clearDebounceTimeout = () => {
	if (debounceTimeout) {
		clearTimeout(debounceTimeout);
		debounceTimeout = null;
	}
};

// 销毁图表
const disposeChart = () => {
	isComponentMounted = false;
	destroyResizeObserver();
	destroyIntersectionObserver();
	clearDebounceTimeout();
	if (chartInstance.value) {
		chartInstance.value.dispose();
		chartInstance.value = undefined;
	}
};

// 监听options变化
watch(
	() => props.options,
	(newOptions) => {
		if (isComponentMounted && chartInstance.value && newOptions) {
			chartInstance.value.setOption(newOptions);
		}
	},
	{ deep: true }
);

// 监听autoResize变化
watch(
	() => props.autoResize,
	(newValue) => {
		if (!isComponentMounted) return;
		if (newValue) {
			initResizeObserver();
			initIntersectionObserver();
		} else {
			destroyResizeObserver();
			destroyIntersectionObserver();
		}
	}
);

// 生命周期
onMounted(async () => {
	isComponentMounted = true;
	await nextTick();
	initChart();
});

onUnmounted(() => {
	disposeChart();
});

// 手动触发resize的方法
const resize = () => {
	if (chartInstance.value) {
		chartInstance.value.resize();
	}
};

// 暴露方法
defineExpose({
	getEchartsInstance,
	resize,
});
</script>

<style scoped>
.el-chart {
	width: 100%;
	height: 100%;
}
</style>
