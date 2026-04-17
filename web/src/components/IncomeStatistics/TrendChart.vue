<template>
  <div class="trend-chart-wrapper">
    <div ref="trendChartRef" style="width: 100%; height: 540px"></div>
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
  dailyData: DailyData[]
  monthlyData: MonthData[]
  quarterlyData: QuarterData[]
  cashType?: string
  benchmarkName?: string
}

const props = withDefaults(defineProps<Props>(), {
  cashType: '',
  benchmarkName: ''
})

// 响应式数据
const trendChartRef = ref()
let trendChartInstance: echarts.ECharts | null = null

// 方法
const getPercentageTooltip = (value: number): string => {
  if (value === null || value === undefined || isNaN(value)) {
    return '-'
  }
  return `${value}%`
}

// 更新折线图
const updateLineChart = () => {
  if (!trendChartRef.value) return
  
  // 初始化或获取实例
  if (!trendChartInstance) {
    trendChartInstance = echarts.init(trendChartRef.value)
  }
  
  // 检查空数据并处理
  const currentData = props.timeDimension === 'd' ? props.dailyData :
    (props.timeDimension === 'm' ? props.monthlyData : props.quarterlyData)

  if (!currentData || currentData.length === 0) {
    trendChartInstance.setOption({
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#999',
          fontSize: 16
        }
      },
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: []
    })
    return
  }

  const serData: any[] = []
  const xData: string[] = []

  // 根据时间维度动态生成标签名称
  const dimensionLabel = props.timeDimension === 'd' ? '日' : (props.timeDimension === 'm' ? '月' : '季')

  // 根据 CASH_TYPE 决定组合收益率的 label
  const isCashType = props.cashType === 'CASH'
  const portfolioYieldLabel = isCashType
    ? `组合${dimensionLabel}收益率(含现金)`
    : `组合${dimensionLabel}收益率(不含现金)`

  // 构建组合收益率柱状图的 series 对象
  const portfolioYield: any = {
    name: portfolioYieldLabel,
    type: 'bar',
    yAxisIndex: 0,
    data: [] as number[],
    itemStyle: {
      color: function (params: any) {
        const value = params.value
        if (value > 0) {
          return '#D73F1D' // 红色
        } else if (value < 0) {
          return '#12bb34' // 绿色
        } else {
          return '#999999' // 灰色
        }
      }
    }
  }

  // 构建基准收益率折线图的 series 对象
  const benchmarkYield: any = {
    name: props.benchmarkName || '基准',
    type: 'line',
    color: '#E7CD91',
    yAxisIndex: 0,
    data: [] as number[],
    symbol: 'circle',
    symbolSize: 4,
    lineStyle: {
      width: 2
    }
  }

  // 根据时间维度填充数据
  if (props.timeDimension === 'd') {
    props.dailyData.forEach((d) => {
      xData.push(d.D_DATE)
      portfolioYield.data.push(d.F_YIELD_D || 0)
      benchmarkYield.data.push(d.F_BENCH_YIELD_D || 0)
    })
  } else if (props.timeDimension === 'm') {
    props.monthlyData.forEach((d) => {
      xData.push(d.MDTE)
      portfolioYield.data.push(d.F_YIELD_M || 0)
      benchmarkYield.data.push(d.F_BENCH_YIELD_M || 0)
    })
  } else if (props.timeDimension === 'q') {
    props.quarterlyData.forEach((d) => {
      xData.push(d.QDTE)
      portfolioYield.data.push(d.F_YIELD_Q || 0)
      benchmarkYield.data.push(d.F_BENCH_YIELD_Q || 0)
    })
  }

  // 设置柱子宽度和间距
  portfolioYield.barMaxWidth = '30px'
  portfolioYield.barCategoryGap = '30%'
  benchmarkYield.barMaxWidth = '30px'
  benchmarkYield.barCategoryGap = '30%'

  // 推入组合收益率和基准收益率
  serData.push(portfolioYield, benchmarkYield)

  // 配置选项
  const options = {
    title: {
      show: false,
      text: '收益统计'
    },
    color: ECHARTS_THEME_CONFIG.seriesLineColor,
    grid: [
      {
        left: '10%',
        right: '3%',
        top: '100px',
        bottom: '80px',
        containLabel: true
      }
    ],
    axisPointer: {
      link: {
        xAxisIndex: 'all'
      }
    },
    xAxis: [
      {
        type: 'category',
        show: true,
        axisLine: {
          show: true,
          onZero: false,
          lineStyle: {
            color: ECHARTS_THEME_CONFIG.xAxisLabelLineColor
          }
        },
        boundaryGap: true,
        axisLabel: {
          margin: 15,
          color: ECHARTS_THEME_CONFIG.labelColor
        },
        axisTick: {
          show: false,
          alignWithLabel: true
        },
        splitLine: {
          interval: 1,
          show: false,
          lineStyle: {
            type: 'dashed',
            color: ECHARTS_THEME_CONFIG.yAxisSplitLineColor
          }
        },
        splitArea: {
          interval: 1,
          show: false,
          areaStyle: {
            color: ECHARTS_THEME_CONFIG.splitAreaColors
          }
        },
        data: xData
      }
    ],
    yAxis: [
      {
        name: '收益率(%)',
        type: 'value',
        position: 'left',
        scale: false,
        nameTextStyle: {
          color: ECHARTS_THEME_CONFIG.labelColor,
          fontWeight: 'normal'
        },
        axisLabel: {
          color: ECHARTS_THEME_CONFIG.labelColor,
          formatter: '{value}%'
        },
        axisLine: {
          show: false
        },
        axisTick: {
          show: false
        },
        splitLine: {
          show: true,
          interval: 0,
          lineStyle: {
            type: 'dashed',
            color: ECHARTS_THEME_CONFIG.yAxisSplitLineColor
          }
        }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        start: '0',
        end: '100',
        zoomOnMouseWheel: false,
        moveOnMouseMove: true,
        moveOnMouseWheel: false
      },
      {
        type: 'slider',
        start: '0',
        end: '100',
        bottom: 5,
        left: '10%',
        right: '10%',
        handleSize: 8,
        textStyle: {
          color: ECHARTS_THEME_CONFIG.zoomColor[2]
        },
        dataBackground: {
          lineStyle: {
            color: ECHARTS_THEME_CONFIG.zoomColor[4]
          },
          areaStyle: {
            color: ECHARTS_THEME_CONFIG.zoomColor[3]
          }
        },
        backgroundColor: ECHARTS_THEME_CONFIG.zoomColor[0],
        fillerColor: ECHARTS_THEME_CONFIG.zoomColor[1],
        borderColor: ECHARTS_THEME_CONFIG.zoomColor[0],
        handleStyle: {
          color: ECHARTS_THEME_CONFIG.zoomColor[2],
          borderColor: ECHARTS_THEME_CONFIG.zoomColor[2]
        },
        height: 20
      }
    ],
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        if (params instanceof Array && params.length > 0) {
          const time = params[0].axisValue
          let result = `<div><time>${time}</time><br />`

          params.forEach((param: any) => {
            const seriesName = param.seriesName || ''
            const value = param.value !== undefined ? param.value : param.data

            const isYieldData = seriesName.includes('收益率') || seriesName.includes('Local Listed Equity Sub-portfolio')
            const displayValue = isYieldData && typeof value === 'number' && !isNaN(value)
              ? getPercentageTooltip(value)
              : value

            const finalValue = typeof displayValue === 'string' && displayValue.includes('%') 
              ? displayValue 
              : displayValue + '%'
            
            result += `<p style="margin: 0;padding: 0;">${param.marker}${seriesName}: ${finalValue}</p>`
          })

          result += '</div>'
          return result
        }
        return ''
      },
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          borderWidth: '0',
          color: '#fff'
        },
        lineStyle: {
          color: ECHARTS_THEME_CONFIG.crossLineStyle,
          type: 'dotted'
        },
        crossStyle: {
          color: ECHARTS_THEME_CONFIG.crossLineStyle,
          type: 'dotted'
        }
      }
    },
    legend: [
      {
        type: 'scroll',
        icon: 'roundRect',
        top: '40px',
        textStyle: {
          color: ECHARTS_THEME_CONFIG.legendColor
        },
        itemWidth: 24,
        itemHeight: 4,
        itemGap: 24,
        borderRadius: 4,
        selected: (() => {
          const selected: Record<string, boolean> = {
            [portfolioYieldLabel]: true,
            [benchmarkYield.name]: true
          }
          return selected
        })()
      }
    ],
    series: serData
  }
  
  trendChartInstance.setOption(options)
}

// 监听数据变化
watch(
  [
    () => props.timeDimension,
    () => props.dailyData,
    () => props.monthlyData,
    () => props.quarterlyData,
    () => props.cashType,
    () => props.benchmarkName
  ],
  () => {
    nextTick(() => {
      updateLineChart()
    })
  },
  { immediate: true, deep: true }
)

// 初始化
onMounted(() => {
  nextTick(() => {
    updateLineChart()
  })
})

// 组件卸载时清理
onUnmounted(() => {
  if (trendChartInstance) {
    trendChartInstance.dispose()
    trendChartInstance = null
  }
})
</script>

<style scoped>
.trend-chart-wrapper {
  flex: 1;
  min-width: 0;
}
</style>
