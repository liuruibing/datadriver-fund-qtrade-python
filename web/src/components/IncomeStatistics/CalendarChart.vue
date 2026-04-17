<template>
  <div class="calendar-chart-wrapper">
    <!-- 日历图标题区 -->
    <div class="calendar-header">
      <span class="unit-label">{{ unitLabelText }}</span>
      <div class="date-navigation">
        <!-- 时间维度切换 -->
        <div class="dimension-tabs">
          <div 
            v-for="tab in timeTabs" 
            :key="tab.value"
            :class="['tab-item', { 'active': safeTimeDimension === tab.value }]"
            @click="handleTabChange(tab.value)"
          >
            {{ tab.label }}
          </div>
        </div>
        
        <!-- 月份切换器（日维度） -->
        <div v-show="safeTimeDimension === 'd'" class="month-nav">
          <i v-show="canGoPrevMonth" class="el-icon-arrow-left" @click="handlePrevMonth"></i>
          <span class="current-month">{{ currentViewMonth }}</span>
          <i v-show="canGoNextMonth" class="el-icon-arrow-right" @click="handleNextMonth"></i>
        </div>
        <!-- 年份切换器（月/季维度） -->
        <div v-show="safeTimeDimension !== 'd'" class="year-nav">
          <i v-show="canGoPrevYear" class="el-icon-arrow-left" @click="handlePrevYear"></i>
          <span class="current-year">{{ currentViewYear }}年</span>
          <i v-show="canGoNextYear" class="el-icon-arrow-right" @click="handleNextYear"></i>
        </div>
      </div>
    </div>

    <!-- 日历图/卡片容器 -->
    <div class="calendar-container">
      <!-- 日度日历图 -->
      <div v-show="safeTimeDimension === 'd'" class="calendar-chart">
        <div ref="calendarChartRef" style="width: 100%; height: 100%"></div>
      </div>

      <!-- 月度卡片 -->
      <div v-show="safeTimeDimension === 'm'" class="month-cards">
        <div v-for="month in 12" :key="month" class="month-card"
          :class="getCardClass(monthData[currentViewYear + '-' + padZero(month)])">
          <div class="card-title">{{ month }}月</div>
          <div class="card-content">
            <template v-if="monthData[currentViewYear + '-' + padZero(month)]">
              <div :class="getValueClass(monthData[currentViewYear + '-' + padZero(month)].F_YIELD_M)"
                :title="getPercentageTooltip(monthData[currentViewYear + '-' + padZero(month)].F_YIELD_M)">
                {{ formatPercentage(monthData[currentViewYear + '-' + padZero(month)].F_YIELD_M) }}
              </div>
              <div :class="getValueClass(monthData[currentViewYear + '-' + padZero(month)].F_ICM_M)"
                :title="String(monthData[currentViewYear + '-' + padZero(month)].F_ICM_M)"
                style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                {{ monthData[currentViewYear + '-' + padZero(month)].F_ICM_M }}
              </div>
            </template>
            <div v-else>-</div>
          </div>
        </div>
      </div>

      <!-- 季度卡片 -->
      <div v-show="safeTimeDimension === 'q'" class="quarter-cards">
        <div v-for="quarter in 4" :key="quarter" class="quarter-card"
          :class="getCardClass(quarterData[currentViewYear + '-Q' + quarter])">
          <div class="card-title">Q{{ quarter }}</div>
          <div class="card-content">
            <template v-if="quarterData[currentViewYear + '-Q' + quarter]">
              <div :class="getValueClass(quarterData[currentViewYear + '-Q' + quarter].F_YIELD_Q)"
                :title="getPercentageTooltip(quarterData[currentViewYear + '-Q' + quarter].F_YIELD_Q)">
                {{ formatPercentage(quarterData[currentViewYear + '-Q' + quarter].F_YIELD_Q) }}
              </div>
              <div :class="getValueClass(quarterData[currentViewYear + '-Q' + quarter].F_ICM_Q)"
                :title="String(quarterData[currentViewYear + '-Q' + quarter].F_ICM_Q)"
                style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                {{ quarterData[currentViewYear + '-Q' + quarter].F_ICM_Q }}
              </div>
            </template>
            <div v-else>-</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ECHARTS_THEME_CONFIG } from '../../enum/commonChartConfig'

// 类型定义
interface DailyData {
  D_DATE: string
  F_YIELD_D: number
  F_BENCH_YIELD_D: number
  F_ICM_D: number
  F_YIELD_HTD: number
}

interface MonthData {
  MDTE: string
  F_YIELD_M: number
  F_BENCH_YIELD_M: number
  F_ICM_M: number
}

interface QuarterData {
  QDTE: string
  F_YIELD_Q: number
  F_BENCH_YIELD_Q: number
  F_ICM_Q: number
}

// Props
interface Props {
  timeDimension: 'd' | 'm' | 'q'
  calendarData: DailyData[]
  monthData: Record<string, MonthData>
  quarterData: Record<string, QuarterData>
  cashType?: string
  monthList: string[]
  yearList: string[]
  currentMonthIndex: number
  currentYearIndex: number
}

const props = withDefaults(defineProps<Props>(), {
  cashType: '',
  monthList: () => [],
  yearList: () => [],
  currentMonthIndex: 0,
  currentYearIndex: 0
})

// 确保 timeDimension 是有效的字符串值
const safeTimeDimension = computed(() => {
  if (typeof props.timeDimension === 'number') {
    // 如果是数字，转换为对应的字符串
    if (props.timeDimension === 1) return 'd'
    if (props.timeDimension === 2) return 'm'
    if (props.timeDimension === 3) return 'q'
    return 'd' // 默认值
  }
  if (typeof props.timeDimension === 'string' && ['d', 'm', 'q'].includes(props.timeDimension)) {
    return props.timeDimension
  }
  return 'd' // 默认值
})

// Emits
const emit = defineEmits<{
  'update:currentMonthIndex': [value: number]
  'update:currentYearIndex': [value: number]
  'update:timeDimension': [value: 'd' | 'm' | 'q']
}>()

// 响应式数据
const calendarChartRef = ref()
let calendarChartInstance: echarts.ECharts | null = null

// 时间维度选项
const timeTabs: Array<{ label: string; value: 'd' | 'm' | 'q' }> = [
  { label: '日', value: 'd' },
  { label: '月', value: 'm' },
  { label: '季', value: 'q' }
]

// 工具函数
const padZero = (num: number): string => {
  return String(num).padStart(2, '0')
}

// 计算属性
const currentViewMonth = computed(() => {
  return props.monthList[props.currentMonthIndex] || ''
})

const currentViewYear = computed(() => {
  return props.yearList[props.currentYearIndex] || ''
})

const calendarRange = computed(() => {
  const year = props.yearList[props.currentYearIndex] || ''
  const monthIndex = props.currentMonthIndex
  return `${year}-${padZero(monthIndex + 1)}`
})

const canGoPrevMonth = computed(() => {
  return props.currentMonthIndex > 0
})

const canGoNextMonth = computed(() => {
  return props.currentMonthIndex < props.monthList.length - 1
})

const canGoPrevYear = computed(() => {
  return props.currentYearIndex > 0
})

const canGoNextYear = computed(() => {
  return props.currentYearIndex < props.yearList.length - 1
})

const unitLabelText = computed(() => {
  const isCashType = props.cashType === 'CASH'
  return isCashType
    ? '资产总值: 万元，收益率(含现金)'
    : '资产总值: 万元，收益率(不含现金)'
})

// 方法
const formatPercentage = (value: number): string => {
  if (value === null || value === undefined || isNaN(value)) {
    return '-'
  }
  return `${value.toFixed(2)}%`
}

const getPercentageTooltip = (value: number): string => {
  if (value === null || value === undefined || isNaN(value)) {
    return '-'
  }
  return `${value}%`
}

const getValueClass = (value: number): string => {
  if (value === null || value === undefined) {
    return ''
  }
  return value > 0 ? 'value-positive' : value < 0 ? 'value-negative' : ''
}

const getCardClass = (data: MonthData | QuarterData | undefined): string => {
  if (!data) return ''
  const icm = 'F_ICM_M' in data ? data.F_ICM_M : data.F_ICM_Q
  return icm > 0 ? 'card-positive' : icm < 0 ? 'card-negative' : ''
}

// 更新日历图
const updateCalendarChart = () => {
  if (!calendarChartRef.value) return
  
  // 检查容器尺寸
  const container = calendarChartRef.value
  
  // 初始化或获取实例
  if (!calendarChartInstance) {
    // 确保容器有尺寸
    if (container.clientWidth === 0 || container.clientHeight === 0) {
      console.warn('Container has no dimensions, delaying initialization')
      setTimeout(() => {
        updateCalendarChart()
      }, 100)
      return
    }
    calendarChartInstance = echarts.init(calendarChartRef.value)
  }
  
  // 检查空数据并处理
  if (!props.calendarData || props.calendarData.length === 0) {
    calendarChartInstance.setOption({
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#999',
          fontSize: 16
        }
      },
      tooltip: { show: false },
      series: []
    })
    return
  }

  const heatmapData: any[] = []
  const scatterData: any[] = []

  props.calendarData.forEach(item => {
    heatmapData.push([item.D_DATE, item.F_YIELD_D])
    
    scatterData.push([
      item.D_DATE,
      1,
      item.F_YIELD_D,
      item.F_ICM_D
    ])
  })

  const options = {
    tooltip: {
      show: false
    },
    visualMap: {
      type: 'piecewise',
      show: false,
      seriesIndex: [1],
      pieces: [
        { lte: 0, color: ECHARTS_THEME_CONFIG.visualMapColor[0] },
        { gt: 0, color: ECHARTS_THEME_CONFIG.visualMapColor[1] }
      ]
    },
    calendar: {
      left: '0',
      right: '0',
      top: '40',
      cellSize: [70, 80],
      yearLabel: { show: false },
      orient: 'vertical',
      dayLabel: {
        margin: 15,
        fontSize: 12,
        firstDay: 1,
        color: ECHARTS_THEME_CONFIG.labelColor,
        nameMap: 'cn'
      },
      splitLine: {
        show: false
      },
      itemStyle: {
        color: ECHARTS_THEME_CONFIG.calendarBgColor,
        borderWidth: 2,
        borderColor: ECHARTS_THEME_CONFIG.calendarBorderColor
      },
      monthLabel: {
        show: false
      },
      range: calendarRange.value
    },
    series: [
      {
        type: 'scatter',
        coordinateSystem: 'calendar',
        symbolSize: 0.1,
        label: {
          show: true,
          align: 'center',
          verticalAlign: 'middle',
          color: ECHARTS_THEME_CONFIG.calendarLabelColor,
          formatter: (params: any) => {
            const d = new Date(params.value[0])
            const dayNum = d.getDate()

            if (params.value[3] === null || params.value[2] === null) {
              return `{cc|${dayNum}}\n{dd|-}`
            }

            const yieldValue = params.value[2]
            const richKey = yieldValue > 0 ? 'aa' : (yieldValue < 0 ? 'bb' : 'cc')

            const percentVal = formatPercentage(yieldValue)
            const moneyVal = params.value[3] !== null && params.value[3] !== undefined
              ? Number(params.value[3]).toFixed(2)
              : '-'

            return `{cc|${dayNum}}\n` +
              `{${richKey}|${percentVal}}\n` +
              `{${richKey}|${moneyVal}}\n`
          },
          rich: {
            aa: {
              lineHeight: 16,
              fontSize: 12,
              color: ECHARTS_THEME_CONFIG.upDownColor[0]
            },
            bb: {
              lineHeight: 16,
              fontSize: 12,
              color: ECHARTS_THEME_CONFIG.upDownColor[1]
            },
            cc: {
              lineHeight: 20,
              fontSize: 12,
              color: '#000'
            },
            dd: {
              lineHeight: 32,
              fontSize: 12,
              color: '#000'
            }
          }
        },
        data: scatterData
      },
      {
        name: '',
        type: 'heatmap',
        coordinateSystem: 'calendar',
        data: heatmapData
      }
    ]
  }
  
  calendarChartInstance.setOption(options)
}

// 事件处理
const handlePrevMonth = () => {
  if (canGoPrevMonth.value) {
    emit('update:currentMonthIndex', props.currentMonthIndex - 1)
  }
}

const handleNextMonth = () => {
  if (canGoNextMonth.value) {
    emit('update:currentMonthIndex', props.currentMonthIndex + 1)
  }
}

const handlePrevYear = () => {
  if (canGoPrevYear.value) {
    emit('update:currentYearIndex', props.currentYearIndex - 1)
  }
}

const handleNextYear = () => {
  if (canGoNextYear.value) {
    emit('update:currentYearIndex', props.currentYearIndex + 1)
  }
}

const handleTabChange = (val: 'd' | 'm' | 'q') => {
  emit('update:timeDimension', val)
}

// 监听数据变化
watch(
  [() => props.calendarData, () => props.currentMonthIndex],
  () => {
    nextTick(() => {
      updateCalendarChart()
    })
  },
  { immediate: true }
)

// 初始化
onMounted(() => {
  nextTick(() => {
    updateCalendarChart()
  })
})

// 组件卸载时清理
onUnmounted(() => {
  if (calendarChartInstance) {
    calendarChartInstance.dispose()
    calendarChartInstance = null
  }
})
</script>

<style scoped>
.calendar-chart-wrapper {
  width: 520px;
  flex-shrink: 0;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.date-navigation {
  display: flex;
  align-items: center;
  gap: 16px;
}

.dimension-tabs {
  display: flex;
  background: #f5f7fa;
  border-radius: 4px;
  padding: 2px;
}

.tab-item {
  padding: 4px 12px;
  font-size: 12px;
  color: #606266;
  cursor: pointer;
  border-radius: 2px;
  transition: all 0.3s;
}

.tab-item:hover {
  color: #409eff;
}

.tab-item.active {
  background: #fff;
  color: #409eff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.unit-label {
  font-size: 13px;
  color: #666;
}

.date-navigation {
  display: flex;
  align-items: center;
  gap: 12px;
}

.month-nav,
.year-nav {
  display: flex;
  align-items: center;
  gap: 8px;
}

.current-month,
.current-year {
  font-size: 15px;
  font-weight: 500;
  color: #333;
  min-width: 70px;
  text-align: center;
}

.el-icon-arrow-left,
.el-icon-arrow-right {
  font-size: 16px;
  color: #409eff;
  cursor: pointer;
  padding: 4px;
}

.el-icon-arrow-left:hover,
.el-icon-arrow-right:hover {
  color: #66b1ff;
}

.calendar-container {
  width: 500px;
  height: 540px;
  position: relative;
  overflow: hidden;
}

.calendar-chart {
  width: 100%;
  height: 100%;
}

.month-cards,
.quarter-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 0;
}

.month-card,
.quarter-card {
  width: calc(25% - 6px);
  height: 120px;
  border-radius: 6px;
  background: #f5f7fa;
  border: 2px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.quarter-card {
  width: calc(50% - 4px);
  height: 240px;
}

.month-card.card-positive,
.quarter-card.card-positive {
  background: rgba(211, 17, 69, 0.1);
  border-color: #d31145;
}

.month-card.card-negative,
.quarter-card.card-negative {
  background: rgba(103, 194, 58, 0.1);
  border-color: #67c23a;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.card-content {
  font-size: 13px;
  text-align: center;
}

.card-content div {
  margin: 4px 0;
}

.value-positive {
  color: #d31145;
  font-weight: 500;
}

.value-negative {
  color: #67c23a;
  font-weight: 500;
}
</style>
