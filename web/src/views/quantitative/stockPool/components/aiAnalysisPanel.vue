<template>
  <div class="ai-analysis-content">
    <!-- 股票选择提示 -->
    <div v-if="!selectedStock" class="no-selection">
      <el-empty
        description="请先选择要分析的股票"
        :image-size="60"
      ></el-empty>
    </div>

    <!-- 股票信息展示 -->
    <div v-else class="analysis-result">
      <div class="stock-info-section">
        <!-- <h4>股票信息</h4> -->
        <div class="stock-info">
          <div class="info-item">
            <span class="label">股票代码：</span>
            <span class="value">{{ selectedStock.stockCode }}</span>
          </div>
          <div class="info-item">
            <span class="label">股票名称：</span>
            <span class="value">{{ selectedStock.stockName }}</span>
          </div>
          <!-- <div class="info-item">
            <span class="label">股票池：</span>
            <span class="value">{{ poolName }}</span>
          </div>
          <div class="info-item">
            <span class="label">备注：</span>
            <span class="value">{{ selectedStock.remark || '无' }}</span>
          </div> -->
        </div>
      </div>

      <!-- 分析结果 -->
      <div v-if="analysisResult" class="result-section">
        <!-- 评分部分 -->
        <div class="rating-section">
          <div class="rating-item">
            <span class="rating-label">综合评分：</span>
            <el-rate v-model="analysisResult.overallRating" disabled show-score text-color="#ff9900" score-template="{value}" />
          </div>
          <div class="rating-item">
            <span class="rating-label">技术评分：</span>
            <el-rate v-model="analysisResult.technicalRating" disabled show-score text-color="#ff9900" score-template="{value}" />
          </div>
          <div class="rating-item">
            <span class="rating-label">基本面评分：</span>
            <el-rate v-model="analysisResult.fundamentalRating" disabled show-score text-color="#ff9900" score-template="{value}" />
          </div>
          <div class="rating-item">
            <span class="rating-label">市场情绪评分：</span>
            <el-rate v-model="analysisResult.sentimentRating" disabled show-score text-color="#ff9900" score-template="{value}" />
          </div>
        </div>

        <!-- 分析报告 -->
        <div class="report-section">
          <h5>分析报告</h5>
          <div class="report-content">
            <div class="report-item">
              <h6>投资建议</h6>
              <p>{{ analysisResult.investmentAdvice }}</p>
            </div>
            <div class="report-item">
              <h6>技术分析</h6>
              <p>{{ analysisResult.technicalAnalysis }}</p>
            </div>
            <div class="report-item">
              <h6>基本面分析</h6>
              <p>{{ analysisResult.fundamentalAnalysis }}</p>
            </div>
            <div class="report-item">
              <h6>风险提示</h6>
              <p>{{ analysisResult.riskWarning }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 等待分析提示 -->
      <div v-else class="waiting-analysis">
        <el-empty
          description="点击开始分析按钮进行AI分析"
          :image-size="60"
        ></el-empty>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { aiStockAnalysis } from '/@/utils/aiService';

// 类型定义
interface StockItem {
  id?: number;
  stockCode: string;
  stockName: string;
  remark?: string;
  poolId?: number;
}

interface AIAnalysisResult {
  overallRating: number;
  technicalRating: number;
  fundamentalRating: number;
  sentimentRating: number;
  investmentAdvice: string;
  technicalAnalysis: string;
  fundamentalAnalysis: string;
  riskWarning: string;
}

defineOptions({
  name: 'AIAnalysisPanel',
});

// Props
const props = defineProps<{
  selectedStock: StockItem | null;
  selectedAIModel: string;
  poolName?: string;
}>();

// Emits
const emit = defineEmits<{
  analysisStart: [];
  analysisComplete: [result: AIAnalysisResult];
  analysisError: [error: string];
}>();

// 响应式数据
const analyzing = ref(false);
const analysisResult = ref<AIAnalysisResult | null>(null);

// 模拟AI分析数据
const getMockAnalysisData = (stockCode: string, stockName: string, aiModel: string) => {
  const mockData = {
    gpt4: {
      overallRating: 4.2,
      technicalRating: 4.5,
      fundamentalRating: 3.8,
      sentimentRating: 4.0,
      investmentAdvice: `基于GPT-4模型深度分析，${stockName}(${stockCode})展现出良好的投资潜力。建议中长期持有，关注公司业绩增长和行业发展趋势。`,
      technicalAnalysis: `${stockName}技术面表现稳健，股价运行在上升通道中。MACD指标显示多头动能充足，RSI指标处于合理区间。建议投资者关注60日均线支撑位，同时注意成交量放大情况。`,
      fundamentalAnalysis: `基本面分析显示，${stockName}公司业绩保持稳定增长，ROE水平在行业内处于领先地位。现金流状况良好，债务结构合理。行业地位稳固，具有较强的市场竞争力。`,
      riskWarning: `市场风险：宏观经济波动可能影响整体市场表现。个股风险：公司面临行业竞争加剧和成本上升压力。建议投资者根据自身风险承受能力谨慎投资，定期跟踪公司业绩和行业动态。`
    },
    gpt35: {
      overallRating: 3.9,
      technicalRating: 4.2,
      fundamentalRating: 3.6,
      sentimentRating: 4.1,
      investmentAdvice: `GPT-3.5模型分析结果显示，${stockName}具有一定的投资价值，但需谨慎对待。适合稳健型投资者中长期配置，建议分批建仓。`,
      technicalAnalysis: `技术指标显示${stockName}股价处于震荡整理阶段，布林带收缩表明市场波动性降低。建议关注突破信号，同时注意支撑和阻力位的表现。`,
      fundamentalAnalysis: `${stockName}基本面相对稳健，但增长动力有待观察。建议关注公司未来业绩指引和行业政策变化对公司业绩的影响。`,
      riskWarning: `需要关注宏观经济环境变化、行业政策调整以及公司内部经营风险。建议投资者做好风险控制，合理控制仓位，避免过度集中投资。`
    },
    claude: {
      overallRating: 4.1,
      technicalRating: 4.3,
      fundamentalRating: 4.0,
      sentimentRating: 3.9,
      investmentAdvice: `Claude模型综合评估后认为，${stockName}是一个值得关注的标的。建议投资者重点关注公司核心竞争力和市场份额变化。`,
      technicalAnalysis: `从技术角度看，${stockName}呈现出良好的上涨趋势，均线系统多头排列。建议投资者把握回调机会，分批买入。`,
      fundamentalAnalysis: `${stockName}公司治理结构完善，管理层执行力强。行业地位突出，具有较强的议价能力和市场影响力。`,
      riskWarning: `主要风险包括市场系统性风险、行业周期性波动以及公司经营不确定性。建议投资者理性投资，做好资产配置。`
    },
    qwen: {
      overallRating: 4.0,
      technicalRating: 4.1,
      fundamentalRating: 3.9,
      sentimentRating: 4.2,
      investmentAdvice: `通义千问模型分析表明，${stockName}整体表现良好，适合价值投资者关注。建议结合公司基本面情况和市场环境做出投资决策。`,
      technicalAnalysis: `${stockName}技术形态健康，成交量配合良好。建议投资者关注重要技术关口，同时结合基本面情况分析。`,
      fundamentalAnalysis: `公司基本面扎实，盈利能力稳定。行业景气度较高，公司具备较强的市场适应能力和创新能力。`,
      riskWarning: `投资风险主要来自于市场波动、行业竞争以及公司经营环境变化。建议投资者定期复盘，适时调整投资策略。`
    },
    ernie: {
      overallRating: 3.8,
      technicalRating: 4.0,
      fundamentalRating: 3.5,
      sentimentRating: 4.0,
      investmentAdvice: `文心一言模型评估显示，${stockName}投资价值一般偏上，适合有一定风险承受能力的投资者。建议关注公司长期发展前景。`,
      technicalAnalysis: `技术面分析显示${stockName}运行相对稳健，建议投资者把握低吸机会，同时设置合理的止损位。`,
      fundamentalAnalysis: `${stockName}公司基本面有待进一步观察，建议关注公司治理结构和内部控制体系建设情况。`,
      riskWarning: `存在一定的市场风险和个股风险，建议投资者做好风险评估，合理控制仓位，避免过度集中投资。`
    }
  };

  return mockData[aiModel as keyof typeof mockData] || mockData.gpt4;
};

// 开始AI分析
const startAIAnalysis = async () => {
  if (!props.selectedStock) {
    ElMessage.warning('请先选择要分析的股票');
    return;
  }

  analyzing.value = true;
  emit('analysisStart');

  try {
    const params = {
      stockCode: props.selectedStock.stockCode,
      stockName: props.selectedStock.stockName,
      aiModel: props.selectedAIModel,
      analysisType: 'comprehensive'
    };

    // 尝试调用第三方AI API，如果失败则使用模拟数据
    try {
      const result = await aiStockAnalysis(params);
      analysisResult.value = result;

      emit('analysisComplete', analysisResult.value);
      ElMessage.success('AI分析完成');
    } catch (apiError) {
      console.log('第三方AI API调用失败，使用模拟数据:', apiError);

      // 使用模拟数据作为fallback
      await new Promise(resolve => setTimeout(resolve, 2000)); // 模拟网络延迟

      analysisResult.value = getMockAnalysisData(
        props.selectedStock.stockCode,
        props.selectedStock.stockName,
        props.selectedAIModel
      );

      emit('analysisComplete', analysisResult.value);
      ElMessage.success('AI分析完成（使用模拟数据）');
    }

  } catch (error) {
    console.error('AI分析失败:', error);
    emit('analysisError', 'AI分析失败，请重试');
    ElMessage.error('AI分析失败，请重试');
  } finally {
    analyzing.value = false;
  }
};

// 监听股票变化时清除分析结果
watch(() => props.selectedStock, () => {
  analysisResult.value = null;
});

// 暴露方法给父组件
defineExpose({
  startAIAnalysis,
  getAnalyzing: () => analyzing.value,
  getAnalysisResult: () => analysisResult.value
});
</script>

<style scoped lang="scss">
.ai-analysis-content {
  height: 100%;
  overflow-y: auto;
  padding-right: 10px;
}

.no-selection,
.waiting-analysis {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stock-info-section {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stock-info-section h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 500;
}

.stock-info {
  // 两列分布
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.stock-info .info-item {
  display: flex;
  margin-bottom: 8px;
  align-items: center;
}

.stock-info .label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
  margin-right: 8px;
}

.stock-info .value {
  color: #303133;
}

.rating-section {
  margin-bottom: 20px;
  padding: 16px;
  background: #f0f9ff;
  border-radius: 8px;
}

.rating-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.rating-label {
  font-weight: 500;
  color: #606266;
  min-width: 120px;
  margin-right: 16px;
}

.report-section h5 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 500;
}

.report-content {
  line-height: 1.6;
}

.report-item {
  margin-bottom: 16px;
}

.report-item h6 {
  margin: 0 0 8px 0;
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.report-item p {
  margin: 0;
  color: #303133;
  text-align: justify;
  line-height: 1.6;
}
</style>
