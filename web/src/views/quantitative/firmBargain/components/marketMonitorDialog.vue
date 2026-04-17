<!--
 * @Description: 行情监控弹窗
 * @Author: 
 * @Date: 2025-12-05 10:25:41
 * @LastEditors: Please set LastEditors
 * @LastEditTime: 2026-01-05 18:45:28
-->
<template>
  <el-dialog
    v-model="dialogVisible"
    title="行情监控"
    top="2vh"
    width="95%"
    :close-on-click-modal="false"
    @close="handleClose"
    custom-class="market-monitor-dialog"
    destroy-on-close
  >
    <!-- <el-row :gutter="10">
      <el-col :span="18">
        <el-radio-group
          v-model="dateType"
          text-color="#626aef"
          fill="rgb(239, 240, 253)"
        >
          <el-radio-button
            label="实时"
            value="real"
          />
          <el-radio-button
            label="5分钟"
            value="5min"
          />
          <el-radio-button
            label="30分钟"
            value="30min"
          />
          <el-radio-button
            label="日K"
            value="day"
          />
        </el-radio-group>
        <div class="chart-box">
          <ElChart
            :options="chartOption"
            width="100%"
            height="400px"
          />
        </div>
      </el-col>
      <el-col :span="6"> </el-col>
    </el-row> -->
    <div style="height: calc(90vh - 160px);">
      <TVChartContainer :datafeedUrl="datafeedUrl" :symbol="rowData?.stockCode" />
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import ElChart from '/@/components/elChart/index.vue';
import TVChartContainer from '/@/components/TVChartContainer/index.vue';
let baseURL = import.meta.env.VITE_API_URL as any;
console.log("baseURL::::::::::::::::::::", baseURL);

const datafeedUrl = ref(baseURL+'/api/selection/tradingview');
console.log("datafeedUrl::::::::::::::::::::", datafeedUrl.value);


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
const dateType = ref('real');

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
    console.log("关闭弹窗");
    
		emit('close');
	}
});

const chartOption = ref({});
const initChart = () => {
	const option = {};
	chartOption.value = option;
};

// 关闭弹窗
const handleClose = () => {
	dialogVisible.value = false;
  
};

onMounted(() => {
	initChart();
});
</script>

<style lang="scss">
.market-monitor-dialog {
	.el-dialog__body {
		height: calc(90vh - 100px);
	}
}
</style>

<style scoped lang="scss">
.market-monitor-dialog {
	.chart-box {
		width: 100%;
		height: 400px;
		border: 1px solid #e5e5e5;
		border-radius: 4px;
		padding: 10px;
		margin-top: 10px;
	}
}
</style>
