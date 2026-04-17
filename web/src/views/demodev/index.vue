<!--
 * @Description: 
 * @Author: 
 * @Date: 2025-12-23 09:55:10
 * @LastEditors: Please set LastEditors
 * @LastEditTime: 2025-12-23 11:02:48
-->
<template>
  <fs-page>
    <div class="tradingview-demo">
      <h2>TradingView 图表 Demo</h2>

      <!-- 图表类型选择 -->
      <div class="chart-selector">
        <el-radio-group v-model="activeChart" @change="switchChart">
          <el-radio-button label="basic">基础K线图</el-radio-button>
          <el-radio-button label="advanced">高级图表</el-radio-button>
          <el-radio-button label="mini">迷你图表</el-radio-button>
          <el-radio-button label="forex">外汇图表</el-radio-button>
          <el-radio-button label="custom">自定义数据</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 自定义数据演示面板 -->
      <div v-if="activeChart === 'custom'" class="custom-data-panel">
        <h4>自定义数据演示</h4>
        <div class="data-generator">
          <div class="generator-controls">
            <el-input-number
              v-model="dataPoints"
              :min="5"
              :max="100"
              label="数据点数量"
              size="small"
              style="width: 120px"
            />
            <el-button @click="generateRandomData" type="primary" size="small">
              🔄 生成随机数据
            </el-button>
            <el-button @click="loadPresetData('bull')" type="success" size="small">
              📈 牛市数据
            </el-button>
            <el-button @click="loadPresetData('bear')" type="danger" size="small">
              📉 熊市数据
            </el-button>
          <el-button @click="loadPresetData('sideways')" type="info" size="small">
                ➡️ 横盘数据
              </el-button>
              <el-button @click="updateCustomChart" type="warning" size="small">
                🔄 刷新图表
              </el-button>
          </div>
          <div class="data-preview">
            <p><strong>当前数据预览 (最近5个数据点):</strong></p>
            <div class="data-table">
              <el-table :data="previewData" size="mini" max-height="150">
                <el-table-column prop="time" label="时间" width="100" align="center" />
                <el-table-column prop="open" label="开盘" width="80" align="center" />
                <el-table-column prop="high" label="最高" width="80" align="center" />
                <el-table-column prop="low" label="最低" width="80" align="center" />
                <el-table-column prop="close" label="收盘" width="80" align="center" />
                <el-table-column prop="volume" label="成交量" width="100" align="center" />
              </el-table>
            </div>
          </div>
        </div>
        <div class="demo-info">
          <p><strong>说明：</strong></p>
          <ul style="margin: 10px 0; padding-left: 20px;">
            <li><strong>数据生成：</strong>上方表格显示生成的假数据，可用于理解K线数据的结构</li>
            <li><strong>自定义图表：</strong>TradingView图表现在使用您生成的自定义数据作为数据源</li>
            <li><strong>Datafeed：</strong>通过TradingView的datafeed API提供历史K线数据</li>
            <li><strong>实时更新：</strong>修改数据后图表会自动更新显示</li>
            <li><strong>完整功能：</strong>支持所有TradingView的绘图工具和技术指标</li>
          </ul>
        </div>
      </div>

      <!-- 单个图表容器 -->
      <div class="chart-section">
        <h3>{{ chartTitles[activeChart] }}</h3>

        <!-- TradingView 图表 -->
        <tradingview-widget
          v-if="activeChart !== 'custom'"
          :key="activeChart"
          :options="currentChartOptions"
        />

        <!-- 自定义数据图表 -->
        <div v-else class="custom-chart-container">
          <div id="custom-tradingview-widget"></div>
        </div>
      </div>
    </div>
  </fs-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import {Chart as TradingviewWidget} from 'vue-tradingview-widgets'

// TradingView 类型定义
interface Bar {
  time: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface TradingViewDatafeed {
  onReady: (callback: (config: any) => void) => void
  searchSymbols: (userInput: string, exchange: string, symbolType: string, onResultReadyCallback: (symbols: any[]) => void) => void
  resolveSymbol: (symbolName: string, onSymbolResolvedCallback: (symbolInfo: any) => void, onResolveErrorCallback: (error: string) => void) => void
  getBars: (symbolInfo: any, resolution: string, from: number, to: number, onHistoryCallback: (bars: Bar[], meta: { noData: boolean }) => void, onErrorCallback: (error: string) => void, firstDataRequest: boolean) => void
  subscribeBars: (symbolInfo: any, resolution: string, onRealtimeCallback: (bar: Bar) => void, subscriberUID: string, onResetCacheNeededCallback: () => void) => void
  unsubscribeBars: (subscriberUID: string) => void
}

// 页面标题
defineOptions({
  name: 'TradingViewDemo'
})

// 响应式数据
const activeChart = ref('basic')
const dataPoints = ref(20)

// 自定义演示数据
const customDemoData = ref([
  { time: '2024-01-01', open: 100, high: 105, low: 95, close: 102, volume: 1000000 },
  { time: '2024-01-02', open: 102, high: 108, low: 100, close: 106, volume: 1200000 },
  { time: '2024-01-03', open: 106, high: 110, low: 103, close: 108, volume: 900000 },
  { time: '2024-01-04', open: 108, high: 112, low: 105, close: 111, volume: 1100000 },
  { time: '2024-01-05', open: 111, high: 115, low: 108, close: 114, volume: 1300000 }
])

// 计算预览数据 (最近5个)
const previewData = computed(() => customDemoData.value.slice(-5))

// 自定义 Datafeed 实现
const customDatafeed: TradingViewDatafeed = {
  onReady: (callback) => {
    setTimeout(() => {
      callback({
        exchanges: [],
        symbols_types: [],
        supported_resolutions: ['1', '5', '15', '30', '60', 'D', 'W', 'M'],
        supports_marks: false,
        supports_timescale_marks: false,
        supports_time: true,
      })
    }, 0)
  },

  searchSymbols: (userInput, exchange, symbolType, onResultReadyCallback) => {
    onResultReadyCallback([])
  },

  resolveSymbol: (symbolName, onSymbolResolvedCallback, onResolveErrorCallback) => {
    setTimeout(() => {
      onSymbolResolvedCallback({
        name: '自定义数据',
        description: 'Custom Demo Data',
        type: 'crypto',
        session: '24x7',
        timezone: 'Asia/Shanghai',
        ticker: symbolName,
        exchange: 'CUSTOM',
        minmov: 1,
        pricescale: 100,
        has_intraday: true,
        intraday_multipliers: ['1', '5', '15', '30', '60'],
        supported_resolutions: ['1', '5', '15', '30', '60', 'D', 'W', 'M'],
        volume_precision: 0,
        data_status: 'streaming',
      })
    }, 0)
  },

  getBars: (symbolInfo, resolution, from, to, onHistoryCallback, onErrorCallback, firstDataRequest) => {
    setTimeout(() => {
      try {
        // 将数据转换为TradingView期望的格式
        const bars: Bar[] = customDemoData.value
          .map(item => ({
            time: Math.floor(new Date(item.time).getTime() / 1000), // 转换为秒级时间戳
            open: item.open,
            high: item.high,
            low: item.low,
            close: item.close,
            volume: item.volume
          }))
          .filter(bar => bar.time >= from && bar.time <= to)
          .sort((a, b) => a.time - b.time) // 确保时间顺序

        onHistoryCallback(bars, { noData: bars.length === 0 })
      } catch (error) {
        console.error('Datafeed getBars error:', error)
        onErrorCallback('Failed to get bars')
      }
    }, 0)
  },

  subscribeBars: (symbolInfo, resolution, onRealtimeCallback, subscriberUID, onResetCacheNeededCallback) => {
    // 实时数据订阅（演示用，不实现）
  },

  unsubscribeBars: (subscriberUID) => {
    // 取消订阅
  }
}

// 图表标题映射
const chartTitles = {
  basic: '基础K线图',
  advanced: '高级图表配置',
  mini: '迷你图表',
  forex: '外汇图表',
  custom: '自定义数据演示'
}


// 图表配置选项 - 使用TradingView支持的演示数据
const chartOptions = {
  basic: {
    symbol: 'NASDAQ:AAPL', // 苹果股票 - 演示数据
    interval: 'D',
    timezone: 'Asia/Shanghai',
    theme: 'light',
    style: '1',
    locale: 'zh_CN',
    toolbar_bg: '#f1f3f6',
    enable_publishing: false,
    allow_symbol_change: true,
    container_id: 'tradingview-chart'
  },
  advanced: {
    symbol: 'BINANCE:BTCUSDT', // 比特币 - 演示数据
    interval: '1H',
    timezone: 'Asia/Shanghai',
    theme: 'dark',
    style: '1',
    locale: 'zh_CN',
    toolbar_bg: '#1e222d',
    enable_publishing: false,
    allow_symbol_change: true,
    hide_top_toolbar: false,
    hide_legend: false,
    save_image: false,
    studies: ['Volume@tv-basicstudies', 'MACD@tv-basicstudies'],
    container_id: 'tradingview-chart'
  },
  mini: {
    symbol: 'FX:EURUSD', // 欧元美元 - 演示数据
    interval: 'D',
    timezone: 'Asia/Shanghai',
    theme: 'light',
    style: '1',
    locale: 'zh_CN',
    toolbar_bg: '#f1f3f6',
    enable_publishing: false,
    hide_top_toolbar: true,
    hide_legend: true,
    save_image: false,
    allow_symbol_change: true,
    container_id: 'tradingview-chart'
  },
  forex: {
    symbol: 'FX_IDC:USDJPY', // 美元日元 - 演示数据
    interval: '1H',
    timezone: 'Asia/Shanghai',
    theme: 'light',
    style: '1',
    locale: 'zh_CN',
    toolbar_bg: '#f1f3f6',
    enable_publishing: false,
    allow_symbol_change: true,
    container_id: 'tradingview-chart'
  },
  custom: {
    symbol: 'CUSTOM:DEMO', // 自定义symbol
    interval: 'D',
    timezone: 'Asia/Shanghai',
    theme: 'light',
    style: '1',
    locale: 'zh_CN',
    toolbar_bg: '#f1f3f6',
    enable_publishing: false,
    allow_symbol_change: false,
    container_id: 'tradingview-chart',
    datafeed: customDatafeed,
    library_path: '/tradingview/',
    autosize: true
  }
}

// 当前图表选项
const currentChartOptions = computed(() => chartOptions[activeChart.value as keyof typeof chartOptions])

// 切换图表方法
const switchChart = () => {
  // 切换时会重新渲染图表组件（通过 key 属性）
  if (activeChart.value === 'custom') {
    nextTick(() => {
      initCustomTradingView()
    })
  }
}


// 切换演示数据symbol
const switchToDemoSymbol = (symbol: string) => {
  chartOptions.custom.symbol = symbol
  // 强制重新渲染图表
  activeChart.value = 'custom' + Date.now()
  setTimeout(() => {
    activeChart.value = 'custom'
  }, 100)
}

// 生成随机数据
const generateRandomData = () => {
  const data = []
  let currentPrice = 100 + Math.random() * 50 // 起始价格在100-150之间

  for (let i = 0; i < dataPoints.value; i++) {
    const date = new Date()
    date.setDate(date.getDate() - (dataPoints.value - i - 1))
    const timeStr = date.toISOString().split('T')[0]

    // 生成OHLC数据
    const volatility = 0.05 // 5%的波动率
    const open = currentPrice
    const change = (Math.random() - 0.5) * 2 * volatility * currentPrice
    const close = open + change
    const high = Math.max(open, close) + Math.random() * volatility * currentPrice * 0.5
    const low = Math.min(open, close) - Math.random() * volatility * currentPrice * 0.5
    const volume = Math.floor(500000 + Math.random() * 1000000)

    data.push({
      time: timeStr,
      open: Math.round(open * 100) / 100,
      high: Math.round(high * 100) / 100,
      low: Math.round(low * 100) / 100,
      close: Math.round(close * 100) / 100,
      volume: volume
    })

    currentPrice = close // 下一天的开盘价基于前一天的收盘价
  }

  customDemoData.value = data
}

// 加载预设数据模式
const loadPresetData = (type: 'bull' | 'bear' | 'sideways') => {
  const data = []
  let currentPrice = 100
  let trend = 0

  switch (type) {
    case 'bull':
      trend = 0.02 // 每天上涨2%
      break
    case 'bear':
      trend = -0.015 // 每天下跌1.5%
      break
    case 'sideways':
      trend = 0 // 横盘
      break
  }

  for (let i = 0; i < dataPoints.value; i++) {
    const date = new Date()
    date.setDate(date.getDate() - (dataPoints.value - i - 1))
    const timeStr = date.toISOString().split('T')[0]

    const baseChange = trend + (Math.random() - 0.5) * 0.04 // 添加随机波动
    const change = baseChange * currentPrice
    const open = currentPrice
    const close = open + change

    // 确保high和low在合理范围内
    const range = Math.abs(change) * 2 + Math.random() * currentPrice * 0.02
    const high = Math.max(open, close) + range
    const low = Math.min(open, close) - range

    const volume = Math.floor(800000 + Math.random() * 400000)

    data.push({
      time: timeStr,
      open: Math.round(open * 100) / 100,
      high: Math.round(high * 100) / 100,
      low: Math.round(low * 100) / 100,
      close: Math.round(close * 100) / 100,
      volume: volume
    })

    currentPrice = close
  }

  customDemoData.value = data
  console.log(data);
  
  updateCustomChart()
}

// 初始化自定义TradingView图表
const initCustomTradingView = () => {
  // 动态加载TradingView脚本
  if (!(window as any).TradingView) {
    const script = document.createElement('script')
    script.src = 'https://s3.tradingview.com/tv.js'
    script.async = true
    script.onload = () => {
      createCustomWidget()
    }
    document.head.appendChild(script)
  } else {
    createCustomWidget()
  }
}

// 创建自定义Widget
const createCustomWidget = () => {
  const TradingView = (window as any).TradingView

  if (!TradingView) return

  const widget = new TradingView.widget({
    symbol: '000001',
    interval: 'D',
    timezone: 'Asia/Shanghai',
    theme: 'light',
    style: '1',
    locale: 'zh_CN',
    toolbar_bg: '#f1f3f6',
    enable_publishing: false,
    allow_symbol_change: false,
    container_id: 'custom-tradingview-widget',
    datafeed: customDatafeed,
    library_path: '/tradingview/',
    width: '100%',
    height: 400,
    autosize: true
  })

  // 存储widget引用以便后续更新
  ;(window as any).customWidget = widget
}

// 更新自定义图表
const updateCustomChart = () => {
  // 当数据更新时，重新创建图表以显示新数据
  if ((window as any).customWidget) {
    // 清除现有图表
    const container = document.getElementById('custom-tradingview-widget')
    if (container) {
      container.innerHTML = ''
    }

    // 重新创建图表
    setTimeout(() => {
      createCustomWidget()
    }, 100)
  }
}
</script>

<style scoped>
.tradingview-demo {
  padding: 20px;
}

.chart-selector {
  margin-bottom: 20px;
  text-align: center;
}

.chart-selector .el-radio-group {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.chart-selector .el-radio-button {
  flex: 1;
  max-width: 150px;
}

/* 自定义数据演示面板样式 */
.custom-data-panel {
  margin-bottom: 20px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.custom-data-panel h4 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
}

.data-generator {
  background: rgba(255, 255, 255, 0.9);
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 15px;
}

.generator-controls {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.generator-controls .el-input-number {
  width: 150px;
}

.data-preview {
  background: rgba(255, 255, 255, 0.95);
  padding: 15px;
  border-radius: 6px;
}

.data-preview p {
  margin: 0 0 10px 0;
  font-weight: 600;
  color: #303133;
}

.data-table {
  border-radius: 4px;
  overflow: hidden;
}

.demo-info {
  margin-top: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #d1ecf1;
  border-radius: 4px;
}

.demo-info p {
  margin: 0;
  color: #31708f;
  font-size: 14px;
}

/* 自定义图表容器样式 */
.custom-chart-container {
  width: 100%;
  height: 400px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
  background: #fff;
}

#custom-tradingview-widget {
  width: 100%;
  height: 100%;
}

.chart-section {
  margin-bottom: 30px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  background: #fff;
}

.chart-section h3 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.chart-section:nth-child(even) {
  background: #f8f9fa;
}

/* TradingView 图表容器样式 */
:deep(.tradingview-widget-container) {
  height: 400px;
  width: 100%;
}

:deep(.tradingview-widget-container__widget) {
  height: 100% !important;
  width: 100% !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .tradingview-demo {
    padding: 10px;
  }

  .chart-section {
    padding: 15px;
  }

  :deep(.tradingview-widget-container) {
    height: 300px;
  }
}
</style>