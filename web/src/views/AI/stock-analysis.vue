<template>
  <div class="min-h-screen bg-gradient-to-br from-green-50/50 via-white to-emerald-50/30">

    <div class="container mx-auto px-4 py-6">
      <!-- Main Content Grid -->
      <div class="mt-6 grid gap-6 lg:grid-cols-3">
        <!-- Score Card -->
        <div class="lg:col-span-1">
          <div class="h-full rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-3">
                <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50">
                  <svg class="h-5 w-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                  </svg>
                </div>
                <div>
                  <h2 class="text-2xl font-bold text-gray-800">{{ selectedStock.symbol }}</h2>
                  <p class="text-sm text-gray-500">{{ selectedStock.name }}</p>
                </div>
              </div>
              <div :class="[
                'flex items-center gap-1 rounded-full px-3 py-1.5 text-sm font-medium',
                selectedStock.change >= 0 ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'
              ]">
                {{ selectedStock.change >= 0 ? '+' : '' }}{{ selectedStock.changePercent.toFixed(2) }}%
              </div>
            </div>

            <!-- Score Circle -->
            <div class="flex items-center justify-center my-6">
              <div class="relative flex h-[180px] w-[180px] items-center justify-center">
                <svg class="h-[180px] w-[180px] -rotate-90 transform">
                  <circle cx="90" cy="90" r="76" stroke="#e5e7eb" stroke-width="10" fill="none" />
                  <circle
                    cx="90"
                    cy="90"
                    r="76"
                    :stroke="scoreLevel.ringColor"
                    stroke-width="10"
                    fill="none"
                    :stroke-dasharray="`${(selectedStock.score / 100) * 477.52} 477.52`"
                    stroke-linecap="round"
                  />
                </svg>
                <div class="absolute flex flex-col items-center">
                  <span :class="['text-5xl font-bold', scoreLevel.textColor]">{{ selectedStock.score }}</span>
                  <span class="text-sm text-gray-500">综合评分</span>
                </div>
              </div>
            </div>

            <!-- Recommendation Badge -->
            <div :class="['rounded-xl p-3 text-center mb-6', scoreLevel.bgLight]">
              <span :class="['text-lg font-semibold', scoreLevel.textColor]">{{ scoreLevel.label }}</span>
            </div>

            <!-- Signals & Risks -->
            <div class="space-y-4">
              <div>
                <div class="mb-2 flex items-center gap-2 text-sm font-medium text-gray-700">
                  <svg class="h-4 w-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  积极信号
                </div>
                <div class="flex flex-wrap gap-2">
                  <span v-for="signal in selectedStock.signals" :key="signal" class="rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 border border-emerald-200">
                    {{ signal }}
                  </span>
                </div>
              </div>
              <div>
                <div class="mb-2 flex items-center gap-2 text-sm font-medium text-gray-700">
                  <svg class="h-4 w-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  风险提示
                </div>
                <div class="flex flex-wrap gap-2">
                  <span v-for="risk in selectedStock.risks" :key="risk" class="rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700 border border-amber-200">
                    {{ risk }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Price Chart -->
        <div class="lg:col-span-2">
          <div class="h-full rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-2">
                <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-50">
                  <svg class="h-4 w-4 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                  </svg>
                </div>
                <h3 class="font-semibold text-gray-800">价格走势 - 近30日</h3>
              </div>
              <div class="text-right">
                <div class="text-2xl font-bold text-gray-800">{{ selectedStock.price.toFixed(2) }}</div>
                <div :class="['text-sm font-medium', selectedStock.change >= 0 ? 'text-emerald-600' : 'text-rose-600']">
                  {{ selectedStock.change >= 0 ? '+' : '' }}{{ selectedStock.change.toFixed(2) }}
                </div>
              </div>
            </div>
            <ElChart
              :options="priceLineChartOptions"
              height="300px"
            />
          </div>
        </div>
      </div>

      <!-- Analysis Grid -->
      <div class="mt-6 grid gap-6 lg:grid-cols-2">
        <!-- Dimension Analysis -->
        <div class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <div class="flex items-center gap-2 mb-6">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-teal-50">
              <svg class="h-4 w-4 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 class="font-semibold text-gray-800">多维度分析</h3>
          </div>
          
          <!-- 进度条和雷达图左右布局 -->
          <div class="flex items-center gap-6">
            <!-- 左侧：雷达图 -->
            <div class="flex-1 flex flex-col items-center justify-center">
              <ElChart
                :options="radarChartOptions"
                height="320px"
              />
            </div>

            <!-- 右侧：进度条 -->
            <div class="flex-1 flex flex-col items-center justify-center">
              <div class="w-full space-y-4">
                <div v-for="(value, key) in selectedStock.dimensions" :key="key" class="space-y-2">
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-500">{{ dimensionLabels[key] }}</span>
                    <span :class="['font-semibold', getScoreColor(value)]">{{ value }}</span>
                  </div>
                  <div class="h-2 rounded-full bg-gray-100 overflow-hidden">
                    <div
                      :style="{ width: `${value}%` }"
                      :class="['h-full rounded-full transition-all', getProgressColor(value)]"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Report -->
        <div class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <div class="flex items-center gap-2 mb-6">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-50">
              <svg class="h-4 w-4 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
            </div>
            <h3 class="font-semibold text-gray-800">AI 智能分析报告</h3>
          </div>

          <div class="rounded-xl bg-gradient-to-br from-slate-50 to-gray-50 p-4 border border-slate-100 mb-4">
            <div class="mb-3 flex items-center gap-2">
              <svg class="h-5 w-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <span class="font-medium text-gray-700">AI 投资观点</span>
            </div>
            <p class="text-sm leading-relaxed text-gray-600">{{ selectedStock.aiSummary }}</p>
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <div class="rounded-xl border border-emerald-200 bg-emerald-50/50 p-4">
              <div class="mb-2 flex items-center gap-2">
                <svg class="h-5 w-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <span class="font-medium text-emerald-700">操作建议</span>
              </div>
              <p class="text-lg font-bold text-gray-800">{{ recommendation.action }}</p>
              <p class="mt-1 text-xs text-gray-500">{{ recommendation.description }}</p>
            </div>

            <div class="rounded-xl border border-sky-200 bg-sky-50/50 p-4">
              <div class="mb-2 flex items-center gap-2">
                <svg class="h-5 w-5 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <span class="font-medium text-sky-700">风险等级</span>
              </div>
              <p class="text-lg font-bold text-gray-800">{{ riskLevel }}</p>
              <p class="mt-1 text-xs text-gray-500">基于 {{ selectedStock.risks.length }} 个风险因子综合评估</p>
            </div>
          </div>

          <div class="mt-4 rounded-xl border bg-slate-50/50 p-4">
            <p class="text-xs text-gray-500">
              <strong class="text-gray-700">免责声明：</strong>
              以上分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import ElChart from '/@/components/elChart/index.vue'

// Props定义
const props = defineProps({
  selectedStock: {
    type: Object,
    required: false
  }
});

// 如果没有传入股票数据，使用默认股票列表
const stocks = ref([
  {
    symbol: "AAPL",
    name: "苹果公司",
    price: 182.52,
    change: 2.34,
    changePercent: 1.3,
    score: 85,
    dimensions: {
      fundamental: 88,
      technical: 82,
      sentiment: 79,
      valuation: 75,
      momentum: 90,
    },
    aiSummary: "苹果公司在科技行业中保持领先地位，强劲的现金流和品牌忠诚度支撑估值。AI业务布局积极，iPhone销量稳定。建议长期持有，短期可关注季度财报表现。",
    signals: ["技术面突破", "机构增持", "盈利超预期"],
    risks: ["中国市场竞争加剧", "估值偏高"],
  },
  {
    symbol: "TSLA",
    name: "特斯拉",
    price: 248.88,
    change: -5.12,
    changePercent: -2.02,
    score: 68,
    dimensions: {
      fundamental: 72,
      technical: 65,
      sentiment: 58,
      valuation: 55,
      momentum: 70,
    },
    aiSummary: "特斯拉作为电动车龙头，面临激烈竞争压力。产能持续扩张但毛利率承压，FSD进展是关键催化剂。波动性较大，适合风险承受能力较高的投资者。",
    signals: ["产能提升", "FSD进展"],
    risks: ["竞争加剧", "毛利率下滑", "估值波动"],
  },
  {
    symbol: "NVDA",
    name: "英伟达",
    price: 875.35,
    change: 15.67,
    changePercent: 1.82,
    score: 92,
    dimensions: {
      fundamental: 95,
      technical: 90,
      sentiment: 94,
      valuation: 78,
      momentum: 96,
    },
    aiSummary: "英伟达凭借AI芯片需求爆发成为市场焦点，数据中心业务高速增长。技术壁垒深厚，客户锁定效应强。虽然估值较高，但业绩增长支撑，是AI投资核心标的。",
    signals: ["AI需求爆发", "业绩超预期", "技术领先"],
    risks: ["供应链约束", "竞争追赶"],
  },
])

// 如果有外部传入的股票数据，使用外部数据；否则使用默认的第一只股票
const selectedStock = ref(
  props.selectedStock || stocks.value[0]
)

// 监听外部传入的股票数据变化
watch(() => props.selectedStock, (newStock) => {
  if (newStock) {
    selectedStock.value = newStock
  } else if (stocks.value.length > 0) {
    selectedStock.value = stocks.value[0]
  }
}, { immediate: true })

const dimensionLabels = {
  fundamental: "基本面",
  technical: "技术面",
  sentiment: "市场情绪",
  valuation: "估值水平",
  momentum: "动量趋势",
}

const scoreLevel = computed(() => {
  const score = selectedStock.value.score
  if (score >= 80) return { label: "强烈推荐", textColor: "text-emerald-600", ringColor: "#10b981", bgLight: "bg-emerald-50" }
  if (score >= 60) return { label: "中性持有", textColor: "text-amber-600", ringColor: "#f59e0b", bgLight: "bg-amber-50" }
  return { label: "谨慎观望", textColor: "text-rose-600", ringColor: "#f43f5e", bgLight: "bg-rose-50" }
})

const recommendation = computed(() => {
  const score = selectedStock.value.score
  if (score >= 80) return { action: "建议买入", description: "该股票各项指标表现优异，具备较强的投资价值。" }
  if (score >= 60) return { action: "持有观望", description: "该股票表现中性，建议密切关注后续变化。" }
  return { action: "谨慎操作", description: "该股票存在一定风险，建议降低仓位或观望。" }
})

const riskLevel = computed(() => {
  const score = selectedStock.value.score
  if (score >= 80) return "低风险"
  if (score >= 60) return "中等风险"
  return "较高风险"
})

const priceData = computed(() => {
  const basePrice = selectedStock.value.price
  const isPositive = selectedStock.value.change >= 0
  const data = []
  let price = basePrice * (isPositive ? 0.95 : 1.05)
  
  for (let i = 0; i < 30; i++) {
    const change = (Math.random() - (isPositive ? 0.4 : 0.6)) * 3
    price = price + change
    data.push({
      date: `${i + 1}日`,
      price: Math.round(price * 100) / 100,
    })
  }
  data[data.length - 1].price = basePrice
  
  const prices = data.map(d => d.price)
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  const range = max - min || 1
  
  return data.map(d => ({
    ...d,
    height: 20 + ((d.price - min) / range) * 80
  }))
})

const getScoreColor = (score) => {
  if (score >= 80) return 'text-emerald-600'
  if (score >= 60) return 'text-amber-600'
  return 'text-rose-600'
}

const getProgressColor = (score) => {
  if (score >= 80) return 'bg-emerald-500'
  if (score >= 60) return 'bg-amber-500'
  return 'bg-rose-500'
}

// 雷达图配置
const radarChartOptions = computed(() => {
  const dimensions = selectedStock.value.dimensions
  return {
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        const indicators = ['基本面', '技术面', '市场情绪', '估值水平', '动量趋势']
        let result = params.name + '<br/>'
        params.value.forEach((val, index) => {
          result += indicators[index] + ': ' + val + '<br/>'
        })
        return result
      }
    },
    radar: {
      indicator: [
        { name: '基本面', max: 100 },
        { name: '技术面', max: 100 },
        { name: '市场情绪', max: 100 },
        { name: '估值水平', max: 100 },
        { name: '动量趋势', max: 100 }
      ],
      center: ['50%', '55%'],
      radius: '70%',
      splitNumber: 5,
      axisName: {
        color: '#666',
        fontSize: 12,
        fontWeight: 500
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(16, 185, 129, 0.05)', 'rgba(16, 185, 129, 0.1)', 'rgba(16, 185, 129, 0.15)', 'rgba(16, 185, 129, 0.2)', 'rgba(16, 185, 129, 0.25)']
        }
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(16, 185, 129, 0.2)'
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(16, 185, 129, 0.3)'
        }
      }
    },
    series: [
      {
        name: '股票评分',
        type: 'radar',
        data: [
          {
            value: [
              dimensions.fundamental,
              dimensions.technical,
              dimensions.sentiment,
              dimensions.valuation,
              dimensions.momentum
            ],
            name: selectedStock.value.symbol,
            areaStyle: {
              color: 'rgba(16, 185, 129, 0.3)'
            },
            lineStyle: {
              color: '#10b981',
              width: 2
            },
            itemStyle: {
              color: '#10b981'
            }
          }
        ]
      }
    ]
  }
})

// 价格折线图配置
const priceLineChartOptions = computed(() => {
  const data = priceData.value
  const prices = data.map(d => d.price)
  const minPrice = Math.min(...prices)
  const maxPrice = Math.max(...prices)
  const priceRange = maxPrice - minPrice
  const padding = priceRange * 0.1 // 上下留10%的边距
  
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'line',
        lineStyle: {
          color: 'rgba(0, 0, 0, 0.1)',
          width: 1
        }
      },
      formatter: function(params) {
        const param = params[0]
        return `${param.axisValue}<br/>价格: <span style="color: #10b981; font-weight: bold;">${param.value.toFixed(2)}</span>`
      },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e5e7eb',
      borderWidth: 1,
      textStyle: {
        color: '#333'
      },
      padding: [8, 12]
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.map(d => d.date),
      axisLine: {
        show: true,
        lineStyle: {
          color: '#e5e7eb'
        }
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#9ca3af',
        fontSize: 11,
        interval: function(index) {
          // 只显示第1、15、30天的标签
          return index !== 0 && index !== 14 && index !== 29
        },
        formatter: function(value) {
          return value
        }
      },
      splitLine: {
        show: false
      }
    },
    yAxis: {
      type: 'value',
      min: Math.max(0, minPrice - padding),
      max: maxPrice + padding,
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#9ca3af',
        fontSize: 11,
        formatter: function(value) {
          return value.toFixed(0)
        }
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: '#f3f4f6',
          type: 'dashed',
          width: 1
        }
      }
    },
    series: [
      {
        name: '价格',
        type: 'line',
        smooth: true,
        data: data.map(d => d.price),
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          color: '#10b981',
          width: 2
        },
        itemStyle: {
          color: '#10b981',
          borderColor: '#fff',
          borderWidth: 2
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: 'rgba(16, 185, 129, 0.2)'
              },
              {
                offset: 1,
                color: 'rgba(16, 185, 129, 0.01)'
              }
            ]
          }
        },
        emphasis: {
          focus: 'series',
          itemStyle: {
            color: '#10b981',
            borderColor: '#fff',
            borderWidth: 2,
            shadowBlur: 10,
            shadowColor: 'rgba(16, 185, 129, 0.5)'
          }
        }
      }
    ]
  }
})
</script>