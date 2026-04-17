<template>
  <div class="ai-analysis-container">
    <!-- 分析条件选择区域 -->
    <div class="analysis-params">
      <!-- 股票选择 -->
      <div class="param-item">
        <label class="param-label">股票选择</label>
        <el-select
          v-model="selectedStock"
          placeholder="请选择股票"
          class="param-select"
          filterable
          clearable
        >
          <el-option
            v-for="stock in stockList"
            :key="stock.code"
            :label="`${stock.name} (${stock.code})`"
            :value="stock.code"
          ></el-option>
        </el-select>
      </div>

      <!-- 时间周期选择 -->
      <div class="param-item">
        <label class="param-label">时间周期</label>
        <el-select
          v-model="selectedPeriod"
          placeholder="请选择时间周期"
          class="param-select"
        >
          <el-option
            v-for="period in periodOptions"
            :key="period.value"
            :label="period.label"
            :value="period.value"
          ></el-option>
        </el-select>
      </div>

      <!-- AI模型选择 -->
      <div class="param-item">
        <label class="param-label">AI模型</label>
        <el-select
          v-model="selectedModel"
          placeholder="请选择AI模型"
          class="param-select"
        >
          <el-option
            v-for="model in aiModels"
            :key="model.value"
            :label="model.label"
            :value="model.value"
          ></el-option>
        </el-select>
      </div>

      <!-- 分析按钮 -->
      <div class="param-item">
        <el-button
          type="primary"
          class="analysis-btn"
          @click="startAnalysis"
          :loading="isAnalyzing"
        >
          {{ isAnalyzing ? '分析中...' : '开始分析' }}
        </el-button>
      </div>
    </div>

    <!-- 无结果提示 -->
    <div
      class="no-result"
      v-if="analysisHistory.length === 0"
    >
      <el-empty description="请选择分析条件并点击开始分析"></el-empty>
    </div>

    <!-- 分析历史记录 -->
    <div
      class="history-cards"
      v-if="analysisHistory.length > 0"
    >
      <div
        v-for="(item, index) in analysisHistory"
        :key="index"
        class="history-card"
      >
        <div class="card-header">
          <div class="stock-info">
            <span class="stock-name">{{ item.stock.name }}</span>
            <span class="stock-code">{{ item.stock.code }}</span>
          </div>
          <div class="analysis-status success">成功</div>
        </div>
        <div class="card-content">
          <div class="content-item">
            <span class="item-label">模型</span>
            <span class="item-value">{{ getModelLabel(item.model) }}</span>
          </div>
          <div class="content-item">
            <span class="item-label">周期</span>
            <span class="item-value">{{ getPeriodLabel(item.period) }}</span>
          </div>
          <div class="content-item">
            <span class="item-label"></span>
            <span class="item-value">{{ item.time }}</span>
          </div>
        </div>
        <div class="card-footer">
          <el-button
            type="primary"
            size="small"
            @click="showDetail(item)"
            class="btn-detail"
          >
            详情
          </el-button>
          <el-button
            type="danger"
            size="small"
            text
            @click="deleteHistory(index)"
            class="btn-delete"
          >
            删除
          </el-button>
        </div>
      </div>
    </div>

    <!-- 分析详情弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      title="AI分析详情"
      width="700px"
      append-to-body
    >
      <div
        v-if="currentDetail"
        class="detail-dialog-content"
      >
        <div class="dialog-meta">
          <div class="meta-item">
            <span class="meta-label">股票:</span>
            <span class="meta-value">{{ currentDetail.stock.name }} ({{ currentDetail.stock.code }})</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">周期:</span>
            <span class="meta-value">{{ getPeriodLabel(currentDetail.period) }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">模型:</span>
            <span class="meta-value">{{ getModelLabel(currentDetail.model) }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">分析时间:</span>
            <span class="meta-value">{{ currentDetail.time }}</span>
          </div>
        </div>

        <div class="dialog-overview">
          <div class="overview-row">
            <div class="overview-item">
              <span class="overview-label">趋势预测</span>
              <span
                class="overview-value"
                :class="currentDetail.trend.toLowerCase()"
              >
                {{ currentDetail.trend }}
              </span>
            </div>
            <div class="overview-item">
              <span class="overview-label">置信度</span>
              <span class="overview-value">{{ currentDetail.confidence }}%</span>
            </div>
          </div>
          <div class="overview-row">
            <div class="overview-item">
              <span class="overview-label">支撑位</span>
              <span class="overview-value">{{ currentDetail.support }}</span>
            </div>
            <div class="overview-item">
              <span class="overview-label">阻力位</span>
              <span class="overview-value">{{ currentDetail.resistance }}</span>
            </div>
          </div>
        </div>

        <div class="dialog-section">
          <h4>详细分析</h4>
          <div
            class="detail-content"
            v-html="currentDetail.detail"
          ></div>
        </div>

        <div class="dialog-section">
          <h4>交易策略建议</h4>
          <ul class="strategy-list">
            <li
              v-for="(strategy, index) in currentDetail.strategy"
              :key="index"
            >
              {{ strategy }}
            </li>
          </ul>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch, defineProps } from 'vue';
import { ElMessage } from 'element-plus';

// 接收父组件传递的股票信息
const props = defineProps<{
	symbol?: string;
}>();

// 监听父组件传递的股票变化
watch(
	() => props.symbol,
	(newSymbol) => {
		if (newSymbol) {
			// 查找对应的股票对象
			const stock = stockList.value.find((s) => s.code === newSymbol);
			if (stock) {
				selectedStock.value = stock;
			}
		}
	}
);

// 股票列表数据（模拟）
const stockList = ref([
	{ code: 'SZ.000001', name: '平安银行' },
	{ code: 'SH.600000', name: '浦发银行' },
	{ code: 'SH.600036', name: '招商银行' },
	{ code: 'SH.601318', name: '中国平安' },
	{ code: 'SZ.000858', name: '五粮液' },
	{ code: 'SZ.002415', name: '海康威视' },
	{ code: 'SH.600519', name: '贵州茅台' },
	{ code: 'SH.601398', name: '工商银行' },
	{ code: 'SH.601288', name: '农业银行' },
	{ code: 'SZ.000725', name: '京东方A' },
]);

// 时间周期选项
const periodOptions = ref([
	{ label: '5分钟', value: '5' },
	{ label: '15分钟', value: '15' },
	{ label: '30分钟', value: '30' },
	{ label: '60分钟', value: '60' },
	{ label: '日线', value: 'D' },
]);

// AI模型选项
const aiModels = ref([
	{ label: '趋势预测模型', value: 'trend' },
	{ label: '波动分析模型', value: 'volatility' },
	{ label: '量价关系模型', value: 'volume_price' },
	{ label: '多因子预测模型', value: 'multi_factor' },
	{ label: '深度学习模型', value: 'deep_learning' },
]);

// 选中的值
const selectedStock = ref('');
const selectedPeriod = ref('D');
const selectedModel = ref('trend');
const isAnalyzing = ref(false);

// 分析历史记录
const analysisHistory = ref([]);

// 详情弹窗
const dialogVisible = ref(false);
const currentDetail = ref(null);

// 开始分析
const startAnalysis = () => {
	// 验证选择条件
	if (!selectedStock.value) {
		ElMessage.warning('请选择股票');
		return;
	}

	// 模拟分析过程
	isAnalyzing.value = true;

	// 模拟异步分析，2秒后返回结果
	setTimeout(() => {
		// 生成模拟分析结果
		const result = generateMockAnalysisResult();

		// 将结果添加到历史记录
		analysisHistory.value.unshift(result);

		isAnalyzing.value = false;

		// 分析完成后自动显示详情弹窗
		// showDetail(result);
	}, 2000);
};

// 显示详情弹窗
const showDetail = (item) => {
	currentDetail.value = item;
	dialogVisible.value = true;
};

// 删除历史记录
const deleteHistory = (index) => {
	analysisHistory.value.splice(index, 1);
	ElMessage.success('删除成功');
};

// 清空历史记录
const clearHistory = () => {
	analysisHistory.value = [];
	ElMessage.success('清空成功');
};

// 生成模拟分析结果
const generateMockAnalysisResult = () => {
	// 根据股票代码找到对应的股票对象
	const stock = stockList.value.find((s) => s.code === selectedStock.value);

	if (!stock) {
		return null;
	}

	const trends = ['上涨', '下跌', '震荡'];
	const randomTrend = trends[Math.floor(Math.random() * trends.length)];
	const confidence = Math.floor(Math.random() * 30) + 70; // 70-99%
	const support = (Math.random() * 100 + 10).toFixed(2);
	const resistance = (Math.random() * 100 + 110).toFixed(2);

	return {
		stock: stock,
		period: selectedPeriod.value,
		model: selectedModel.value,
		time: new Date().toLocaleString(),
		trend: randomTrend,
		confidence: confidence,
		support: support,
		resistance: resistance,
		detail: `<p>根据${getModelLabel(selectedModel.value)}分析，${stock.name}(${stock.code})在${getPeriodLabel(
			selectedPeriod.value
		)}周期下呈现<strong>${randomTrend}</strong>趋势，置信度为${confidence}%。</p>
            <p>从技术面来看，股价目前处于${randomTrend === '上涨' ? '上升通道' : randomTrend === '下跌' ? '下降通道' : '震荡区间'}，成交量${
			Math.random() > 0.5 ? '放大' : '萎缩'
		}，MACD指标${Math.random() > 0.5 ? '金叉' : '死叉'}，KDJ指标${Math.random() > 0.5 ? '处于超买区' : '处于超卖区'}。</p>
            <p>基本面方面，公司${Math.random() > 0.5 ? '业绩增长' : '业绩下滑'}，市盈率${(Math.random() * 50 + 10).toFixed(2)}，市净率${(
			Math.random() * 5 +
			1
		).toFixed(2)}，${Math.random() > 0.5 ? '估值合理' : '估值偏高'}。</p>`,
		strategy: [
			`建议${randomTrend === '上涨' ? '持有' : randomTrend === '下跌' ? '卖出' : '观望'}为主`,
			`支撑位${support}附近可考虑${randomTrend === '上涨' ? '加仓' : '建仓'}`,
			`阻力位${resistance}附近可考虑${randomTrend === '上涨' ? '减仓' : '止损'}`,
			`密切关注${getPeriodLabel(selectedPeriod.value)}周期的成交量变化`,
			`${getModelLabel(selectedModel.value)}提示${Math.random() > 0.5 ? '短期有反弹可能' : '短期仍有调整压力'}`,
		],
	};
};

// 获取周期标签
const getPeriodLabel = (value) => {
	const period = periodOptions.value.find((p) => p.value === value);
	return period ? period.label : value;
};

// 获取模型标签
const getModelLabel = (value) => {
	const model = aiModels.value.find((m) => m.value === value);
	return model ? model.label : value;
};
</script>

<style scoped>
.ai-analysis-container {
	/* padding: 16px; */
	height: 100%;
	overflow-y: auto;
}

/* 分析条件样式 */
.analysis-params {
	background-color: #f9f9f9;
	padding: 16px;
	border-radius: 8px;
	margin-bottom: 16px;
	border: 1px solid #e4e7ed;
}

.param-item {
	margin-bottom: 12px;
}

.param-item:last-child {
	margin-bottom: 0;
}

.param-label {
	display: block;
	font-size: 14px;
	font-weight: 500;
	margin-bottom: 6px;
	color: #303133;
}

.param-select {
	width: 100%;
}

.analysis-btn {
	width: 100%;
	margin-top: 4px;
}

/* 无结果样式 */
.no-result {
	/* padding: 40px 0; */
	text-align: center;
	background-color: #f9f9f9;
	border-radius: 8px;
	border: 1px solid #e4e7ed;
}

/* 分析中样式 */
.analyzing {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 40px 0;
	background-color: #f9f9f9;
	border-radius: 8px;
	border: 1px solid #e4e7ed;
}

.analyzing-text {
	margin-top: 16px;
	font-size: 14px;
	color: #606266;
}

/* 分析历史样式 */
.analysis-history {
	margin-top: 20px;
	background-color: #f9f9f9;
	padding: 16px;
	border-radius: 8px;
	border: 1px solid #e4e7ed;
}

.history-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 12px;
}

.history-header h3 {
	margin: 0;
	font-size: 16px;
	font-weight: 600;
	color: #303133;
}

.history-cards {
	display: flex;
	flex-direction: column;
	gap: 12px;
	overflow-y: auto;
	height: calc(100% - 350px);
}

.history-card {
	background-color: #fff;
	border: 1px solid #e4e7ed;
	border-radius: 8px;
	padding: 12px;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
	transition: all 0.3s ease;
}

.history-card:hover {
	box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	transform: translateY(-2px);
}

.card-header {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	margin-bottom: 12px;
	padding-bottom: 8px;
	border-bottom: 1px solid #f0f0f0;
}

.stock-info {
	flex: 1;
	overflow: hidden;
}

.stock-name {
	font-size: 14px;
	font-weight: 600;
	color: #303133;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
	margin-bottom: 2px;
}

.stock-code {
	margin-left: 10px;
	font-size: 12px;
	color: #606266;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.analysis-status {
	font-size: 12px;
	padding: 2px 8px;
	border-radius: 10px;
	font-weight: 500;
}

.analysis-status.success {
	background-color: #f0f9eb;
	color: #67c23a;
}

.analysis-status.failed {
	background-color: #fef0f0;
	color: #f56c6c;
}

.card-content {
	margin-bottom: 12px;
}

.content-item {
	display: flex;
	justify-content: space-between;
	margin-bottom: 6px;
}

.content-item:last-child {
	margin-bottom: 0;
}

.item-label {
	font-size: 12px;
	color: #909399;
}

.item-value {
	font-size: 12px;
	color: #606266;
	font-weight: 500;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
	max-width: 180px;
	text-align: right;
}

.card-footer {
	display: flex;
	justify-content: flex-end;
	gap: 8px;
	padding-top: 8px;
	border-top: 1px solid #f0f0f0;
}

.btn-detail {
	padding: 4px 12px;
	font-size: 12px;
}

.btn-delete {
	padding: 4px 12px;
	font-size: 12px;
}

/* 滚动条样式 */
.history-cards::-webkit-scrollbar {
	width: 4px;
}

.history-cards::-webkit-scrollbar-track {
	background: #f1f1f1;
	border-radius: 2px;
}

.history-cards::-webkit-scrollbar-thumb {
	background: #c1c1c1;
	border-radius: 2px;
}

.history-cards::-webkit-scrollbar-thumb:hover {
	background: #a8a8a8;
}

/* 详情弹窗样式 */
.detail-dialog-content {
	max-height: 500px;
	overflow-y: auto;
}

.dialog-meta {
	background-color: #f9f9f9;
	padding: 12px;
	border-radius: 6px;
	margin-bottom: 16px;
}

.meta-item {
	margin-bottom: 8px;
}

.meta-item:last-child {
	margin-bottom: 0;
}

.meta-label {
	font-weight: 500;
	color: #303133;
	margin-right: 8px;
}

.meta-value {
	color: #606266;
}

.dialog-overview {
	margin-bottom: 16px;
}

.overview-row {
	display: flex;
	gap: 16px;
	margin-bottom: 12px;
}

.overview-row:last-child {
	margin-bottom: 0;
}

.overview-item {
	flex: 1;
	background-color: #f9f9f9;
	padding: 12px;
	border-radius: 6px;
	display: flex;
	flex-direction: column;
	align-items: center;
}

.overview-item .overview-label {
	font-size: 14px;
	color: #606266;
	margin-bottom: 4px;
}

.overview-item .overview-value {
	font-size: 18px;
	font-weight: 600;
	color: #303133;
}

.dialog-section {
	margin-bottom: 20px;
}

.dialog-section:last-child {
	margin-bottom: 0;
}

.dialog-section h4 {
	margin: 0 0 12px 0;
	font-size: 16px;
	font-weight: 600;
	color: #303133;
}

.dialog-section .detail-content {
	background-color: #f9f9f9;
	padding: 12px;
	border-radius: 6px;
	font-size: 14px;
	color: #606266;
}

.dialog-section .strategy-list {
	background-color: #f9f9f9;
	padding: 12px;
	border-radius: 6px;
	margin: 0;
	padding-left: 20px;
	font-size: 14px;
	color: #606266;
}

.dialog-section .strategy-list li {
	margin-bottom: 8px;
}

.dialog-section .strategy-list li:last-child {
	margin-bottom: 0;
}
</style>