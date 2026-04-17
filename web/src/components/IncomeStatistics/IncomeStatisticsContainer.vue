<template>
  <div class="income-statistics" v-loading="loading" element-loading-text="正在加载收益统计数据..."
    element-loading-background="rgba(255, 255, 255, 0.8)">
    <!-- 标题和操作栏 -->
    <div class="flexBetween mb12">
      <div class="item-boxtop-bet-row">
        <div class="dtlSecondTitle">收益统计</div>
        <div class="flexAlignCenter shaixuan-modal ml-2">
          <!-- 日期选择器（根据需要添加） -->
        </div>
      </div>
      <div class="item-boxtop-bet-row">
        <el-tooltip effect="light" placement="bottom" popper-class="custom-tooltip"
          v-if="metaDataDesc && metaDataDesc.IncomeStatistics">
          <div slot="content" style="max-width: 500px; line-height: 1.8;">
            <div v-html="metaDataDesc.IncomeStatistics"></div>
          </div>
          <i class="fa fa-question-circle infoIncoCss mr8" style="cursor: pointer"></i>
        </el-tooltip>
        <el-tooltip content="导出" placement="bottom">
          <i class="fa fa-download infoIncoCss mr8" style="cursor: pointer;" @click="handleExport" :class="{ 'loading': exportLoading }"></i>
        </el-tooltip>
      </div>
    </div>

    <!-- 时间维度切换 -->
    <div class="flexAlignCenter ml4 mb12">
      <el-radio-group v-model="timeDimension" size="small" @change="handleDimensionChange">
        <el-radio-button label="d">日</el-radio-button>
        <el-radio-button label="m">月</el-radio-button>
        <el-radio-button label="q">季</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 左侧：日历图组件 -->
      <CalendarChart
        :time-dimension="timeDimension"
        :calendar-data="calendarData"
        :month-data="monthData"
        :quarter-data="quarterData"
        :cash-type="formQuery.CASH_TYPE"
        :month-list="monthList"
        :year-list="yearList"
        :current-month-index="currentMonthIndex"
        :current-year-index="currentYearIndex"
        @update:current-month-index="currentMonthIndex = $event"
        @update:current-year-index="currentYearIndex = $event"
      />

      <!-- 右侧：趋势图组件 -->
      <TrendChart
        :time-dimension="timeDimension"
        :daily-data="rawDailyData"
        :monthly-data="rawMonthlyData"
        :quarterly-data="rawQuarterlyData"
        :cash-type="formQuery.CASH_TYPE"
        :benchmark-name="benchmarkName"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import CalendarChart from './CalendarChart.vue'
import TrendChart from './TrendChart.vue'
import { generateMockData, type IncomeStatisticsData } from '../../mock/incomeStatistics'

// 类型定义
interface FormQuery {
  beginDate: string
  endDate: string
  RISK_FREE_RATE: string
  CASH_TYPE: string
}

interface Config {
  startDate?: string
  endDate?: string
  RISK_FREE_RATE?: string
  CASH_TYPE?: string
  portfolioInfo?: {
    VC_PORT_CD: string
    VC_PORT_NM: string
  }
  benchmarkOptions?: Array<{ label: string; value: string }>
}

// Props
interface Props {
  config?: Config
  previewMode?: boolean
  metaDataDesc?: Record<string, string>
  useMock?: boolean // 是否使用模拟数据
}

const props = withDefaults(defineProps<Props>(), {
  config: () => ({}),
  previewMode: false,
  metaDataDesc: () => ({}),
  useMock: false // 默认使用真实接口
})

// 响应式数据
const loading = ref(false)
const exportLoading = ref(false)
const timeDimension = ref<'d' | 'm' | 'q'>('d')

// 查询参数
const formQuery = reactive<FormQuery>({
  beginDate: '',
  endDate: '',
  RISK_FREE_RATE: '',
  CASH_TYPE: ''
})

// 原始数据
const rawDailyData = ref<any[]>([])
const rawMonthlyData = ref<any[]>([])
const rawQuarterlyData = ref<any[]>([])

// 处理后的数据
const calendarData = ref<any[]>([])
const monthData = ref<Record<string, any>>({})
const quarterData = ref<Record<string, any>>({})

// 基准名称
const benchmarkName = ref('')

// 视图控制
const monthList = ref<string[]>([])
const yearList = ref<string[]>([])
const currentMonthIndex = ref(0)
const currentYearIndex = ref(0)

// SQL代码标识
const SQL_CODE = '2d296f87-626b-4cfc-958d-433c3d31e58f'

// 方法
const initFromConfig = () => {
  if (props.config) {
    if (props.config.startDate) {
      formQuery.beginDate = props.config.startDate
    }
    if (props.config.endDate) {
      formQuery.endDate = props.config.endDate
    }
    if (props.config.RISK_FREE_RATE) {
      formQuery.RISK_FREE_RATE = props.config.RISK_FREE_RATE
    }
    if (props.config.CASH_TYPE) {
      formQuery.CASH_TYPE = props.config.CASH_TYPE
    }
  }
}

const formatDate = (date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const formatYearMonth = (date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
}

const fillMissingDates = (data: any[]): any[] => {
  if (!data || data.length === 0) return []

  const result: any[] = []
  const startDate = new Date(formQuery.beginDate)
  const firstDataDate = new Date(data[0].D_DATE)

  // 补全开始日期到第一条数据之间的空白
  while (startDate < firstDataDate) {
    result.push({
      D_DATE: formatDate(startDate),
      F_ICM_D: null,
      F_YIELD_D: null,
      F_BENCH_YIELD_D: null,
      F_YIELD_HTD: null
    })
    startDate.setDate(startDate.getDate() + 1)
  }

  // 添加原始数据
  result.push(...data)

  // 补全最后一条数据到月末的空白
  const lastDate = new Date(data[data.length - 1].D_DATE)
  lastDate.setDate(lastDate.getDate() + 1)
  const lastMonth = new Date(data[data.length - 1].D_DATE).getMonth()

  while (lastDate.getMonth() === lastMonth) {
    result.push({
      D_DATE: formatDate(lastDate),
      F_ICM_D: null,
      F_YIELD_D: null,
      F_BENCH_YIELD_D: null,
      F_YIELD_HTD: null
    })
    lastDate.setDate(lastDate.getDate() + 1)
  }

  return result
}

const initMonthYearList = () => {
  const startDate = new Date(formQuery.beginDate)
  const endDate = new Date(formQuery.endDate)

  // 生成月份列表
  monthList.value = []
  const currentMonth = new Date(startDate)
  currentMonth.setDate(1)

  while (currentMonth <= endDate) {
    const yearMonth = formatYearMonth(currentMonth)
    monthList.value.push(yearMonth)
    currentMonth.setMonth(currentMonth.getMonth() + 1)
  }

  // 设置当前查看的月份为最后一个月
  currentMonthIndex.value = monthList.value.length - 1

  // 生成年份列表
  yearList.value = []
  const startYear = startDate.getFullYear()
  const endYear = endDate.getFullYear()

  for (let year = startYear; year <= endYear; year++) {
    yearList.value.push(String(year))
  }

  // 设置当前查看的年份为最后一个年份
  currentYearIndex.value = yearList.value.length - 1
}

// 加载模拟数据
const loadMockData = async () => {
  loading.value = true
  
  try {
    // 生成模拟数据
    const mockData = generateMockData(formQuery.beginDate, formQuery.endDate)
    
    // 按 VC_DATE_TYPE 分组
    const dailyDataArray: any[] = []
    const monthlyDataArray: any[] = []
    const quarterlyDataArray: any[] = []

    mockData.forEach((item: IncomeStatisticsData) => {
      if (item.VC_DATE_TYPE === 'D') {
        dailyDataArray.push({
          D_DATE: item.D_DATE_VALUE,
          F_YIELD_D: item.F_YIELD || 0,
          F_BENCH_YIELD_D: item.F_BENCH_YIELD || 0,
          F_ICM_D: item.F_MARKET_VALUE || 0,
          F_YIELD_HTD: item.F_YIELD_HTD || 0
        })
      } else if (item.VC_DATE_TYPE === 'M') {
        monthlyDataArray.push({
          MDTE: item.D_DATE_VALUE,
          F_YIELD_M: item.F_YIELD || 0,
          F_BENCH_YIELD_M: item.F_BENCH_YIELD || 0,
          F_ICM_M: item.F_MARKET_VALUE || 0
        })
      } else if (item.VC_DATE_TYPE === 'Q') {
        quarterlyDataArray.push({
          QDTE: item.D_DATE_VALUE,
          F_YIELD_Q: item.F_YIELD || 0,
          F_BENCH_YIELD_Q: item.F_BENCH_YIELD || 0,
          F_ICM_Q: item.F_MARKET_VALUE || 0
        })
      }
    })

    // 加载日度数据
    if (dailyDataArray.length > 0) {
      rawDailyData.value = dailyDataArray
      calendarData.value = fillMissingDates(rawDailyData.value)
    }

    // 加载月度数据
    if (monthlyDataArray.length > 0) {
      rawMonthlyData.value = monthlyDataArray
      monthData.value = {}
      rawMonthlyData.value.forEach(item => {
        monthData.value[item.MDTE] = item
      })
    }

    // 加载季度数据
    if (quarterlyDataArray.length > 0) {
      rawQuarterlyData.value = quarterlyDataArray
      quarterData.value = {}
      rawQuarterlyData.value.forEach(item => {
        quarterData.value[item.QDTE] = item
      })
    }

    // 设置基准名称
    benchmarkName.value = '沪深300'

    // 初始化月份年份列表
    initMonthYearList()
  } catch (error) {
    ElMessage.error('模拟数据加载失败')
  } finally {
    loading.value = false
  }
}

// 加载真实数据（需要根据实际接口调整）
const loadRealData = async () => {
  loading.value = true
  
  try {
    // TODO: 调用真实的API接口
    // const response = await commonApi.getDataBySqlCode({
    //   sqlCode: SQL_CODE,
    //   beginDate: formQuery.beginDate,
    //   endDate: formQuery.endDate,
    //   VC_PORT_CD: props.config?.portfolioInfo?.VC_PORT_CD || '',
    //   RISK_FREE_RATE: formQuery.RISK_FREE_RATE,
    //   CASH_TYPE: formQuery.CASH_TYPE
    // })
    
    // 暂时使用模拟数据
    await loadMockData()
  } catch (error) {
    ElMessage.error('数据加载失败')
  } finally {
    loading.value = false
  }
}

// 加载数据
const loadData = async () => {
  if (!formQuery.beginDate || !formQuery.endDate) {
    ElMessage.warning('请选择日期范围')
    return
  }

  if (props.useMock) {
    await loadMockData()
  } else {
    await loadRealData()
  }
}

// 维度切换
const handleDimensionChange = () => {
  // 切换时间维度时，只需要更新图表，不需要重新加载数据
}

// 刷新数据
const handleRefresh = () => {
  loadData()
}

// 导出数据
const handleExport = () => {
  const params = {
    sqlCode: SQL_CODE,
    beginDate: formQuery.beginDate || '',
    endDate: formQuery.endDate || '',
    VC_PORT_CD: props.config?.portfolioInfo?.VC_PORT_CD || '',
    VC_PORT_NM: props.config?.portfolioInfo?.VC_PORT_NM || '',
    RISK_FREE_RATE: formQuery.RISK_FREE_RATE || '',
    CASH_TYPE: formQuery.CASH_TYPE || ''
  }
  
  const fileName = `收益统计(${props.config?.portfolioInfo?.VC_PORT_NM} ${formQuery.beginDate} ${formQuery.endDate}).xlsx`
  const url = `/api/report/v1.0/data/sql/${SQL_CODE}?_file_template=port_detail_income_statistics.xlsx&_file_name=${encodeURIComponent(fileName)}`
  
  exportLoading.value = true
  
  // TODO: 实现导出功能
  // exportCommon.downLoadFileByUrlPost(url, params, fileName, () => {
  //   exportLoading.value = false
  // })
  
  // 模拟导出
  setTimeout(() => {
    exportLoading.value = false
    ElMessage.success('导出成功')
  }, 1000)
}

// 初始化
onMounted(async () => {
  initFromConfig()
  
  // 设置默认日期范围（如果config中没有提供）
  if (!formQuery.beginDate || !formQuery.endDate) {
    const endDate = new Date()
    const startDate = new Date()
    startDate.setMonth(startDate.getMonth() - 3) // 默认最近3个月
    
    formQuery.beginDate = formatDate(startDate)
    formQuery.endDate = formatDate(endDate)
  }
  
  await loadData()
})

// 暴露方法给父组件
defineExpose({
  loadData,
  handleRefresh
})
</script>

<style scoped>
/* 组件样式 */
.main-content {
  display: flex;
  gap: 20px;
}

.flexBetween {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.flexAlignCenter {
  display: flex;
  align-items: center;
}

.item-boxtop-bet-row {
  display: flex;
  align-items: center;
}

.dtlSecondTitle {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.shaixuan-modal {
  display: flex;
  align-items: center;
}

.ml-2 {
  margin-left: 8px;
}

.ml4 {
  margin-left: 16px;
}

.mb12 {
  margin-bottom: 12px;
}

.mr8 {
  margin-right: 8px;
}

.infoIncoCss {
  font-size: 16px;
  color: #666;
  cursor: pointer;
}

.infoIncoCss:hover {
  color: #409eff;
}

.infoIncoCss.loading {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Loading颜色覆盖 */
:deep(.el-loading-spinner .circular) {
  color: #d31145 !important;
}

:deep(.el-loading-text) {
  color: #d31145 !important;
}
</style>
