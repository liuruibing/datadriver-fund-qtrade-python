// 收益统计组件模拟数据
export interface IncomeStatisticsData {
  VC_DATE_TYPE: 'D' | 'M' | 'Q' // 日期类型：日、月、季
  D_DATE_VALUE: string // 业务日期
  F_YIELD: number // 收益率（百分比格式）
  F_BENCH_YIELD: number // 基准收益率（百分比格式）
  F_MARKET_VALUE: number // 资产总值（万元格式）
  F_YIELD_HTD?: number // 组合累计日收益率（日度数据专用）
  VC_BENCH_NM?: string // 基准名称
}

// 生成指定范围的日期数据
function generateDateRange(startDate: Date, endDate: Date): string[] {
  const dates: string[] = []
  const currentDate = new Date(startDate)
  
  while (currentDate <= endDate) {
    dates.push(formatDate(currentDate))
    currentDate.setDate(currentDate.getDate() + 1)
  }
  
  return dates
}

// 格式化日期为 YYYY-MM-DD
function formatDate(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 格式化年月为 YYYY-MM
function formatYearMonth(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
}

// 生成季度标识
function formatQuarter(date: Date): string {
  const year = date.getFullYear()
  const month = date.getMonth()
  const quarter = Math.floor(month / 3) + 1
  return `${year}-Q${quarter}`
}

// 生成随机收益率（-5% 到 5%）
function randomYield(): number {
  return Number((Math.random() * 10 - 5).toFixed(2))
}

// 生成随机资产总值（1000-5000万元）
function randomMarketValue(): number {
  return Number((Math.random() * 4000 + 1000).toFixed(2))
}

// 生成模拟数据
export function generateMockData(startDate: string, endDate: string): IncomeStatisticsData[] {
  const start = new Date(startDate)
  const end = new Date(endDate)
  const mockData: IncomeStatisticsData[] = []
  
  // 生成日度数据
  const dailyDates = generateDateRange(start, end)
  dailyDates.forEach(date => {
    const dateObj = new Date(date)
    const yieldValue = randomYield()
    const benchYield = randomYield()
    const marketValue = randomMarketValue()
    
    mockData.push({
      VC_DATE_TYPE: 'D',
      D_DATE_VALUE: date,
      F_YIELD: yieldValue,
      F_BENCH_YIELD: benchYield,
      F_MARKET_VALUE: marketValue,
      F_YIELD_HTD: Number((yieldValue + Math.random() * 20 - 10).toFixed(2)),
      VC_BENCH_NM: '沪深300'
    })
  })
  
  // 生成月度数据
  const currentMonth = new Date(start)
  currentMonth.setDate(1)
  
  while (currentMonth <= end) {
    const yearMonth = formatYearMonth(currentMonth)
    const yieldValue = randomYield()
    const benchYield = randomYield()
    const marketValue = randomMarketValue()
    
    mockData.push({
      VC_DATE_TYPE: 'M',
      D_DATE_VALUE: yearMonth,
      F_YIELD: yieldValue,
      F_BENCH_YIELD: benchYield,
      F_MARKET_VALUE: marketValue,
      VC_BENCH_NM: '沪深300'
    })
    
    currentMonth.setMonth(currentMonth.getMonth() + 1)
  }
  
  // 生成季度数据
  const currentQuarter = new Date(start)
  currentQuarter.setMonth(currentQuarter.getMonth() - (currentQuarter.getMonth() % 3), 1)
  
  while (currentQuarter <= end) {
    const quarter = formatQuarter(currentQuarter)
    const yieldValue = randomYield()
    const benchYield = randomYield()
    const marketValue = randomMarketValue()
    
    mockData.push({
      VC_DATE_TYPE: 'Q',
      D_DATE_VALUE: quarter,
      F_YIELD: yieldValue,
      F_BENCH_YIELD: benchYield,
      F_MARKET_VALUE: marketValue,
      VC_BENCH_NM: '沪深300'
    })
    
    currentQuarter.setMonth(currentQuarter.getMonth() + 3)
  }
  
  return mockData
}

// 预设的模拟数据（最近3个月）
export const presetMockData = generateMockData(
  '2024-10-01',
  '2024-12-31'
)
