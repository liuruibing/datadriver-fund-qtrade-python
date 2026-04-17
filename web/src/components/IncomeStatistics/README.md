# 收益统计组件 (Vue 3)

## 概述

这是从 Vue 2 重构为 Vue 3 的收益统计组件，采用了模块化架构，将原来的单一组件拆分为三个独立的组件：

- `IncomeStatisticsContainer.vue` - 主容器组件，负责数据管理和状态控制
- `CalendarChart.vue` - 日历图表组件，展示日度热力图和月/季度卡片
- `TrendChart.vue` - 趋势图表组件，展示收益率的柱状图和基准折线图

## 特性

- ✅ Vue 3 Composition API
- ✅ TypeScript 支持
- ✅ 模块化架构
- ✅ 模拟数据支持
- ✅ 响应式设计
- ✅ 类型安全

## 使用方法

### 基础用法

```vue
<template>
  <IncomeStatisticsContainer
    :config="config"
    :use-mock="true"
    :meta-data-desc="metaDataDesc"
  />
</template>

<script setup lang="ts">
import { IncomeStatisticsContainer } from '@/components/IncomeStatistics'

const config = {
  startDate: '2024-10-01',
  endDate: '2024-12-31',
  portfolioInfo: {
    VC_PORT_CD: 'PORT001',
    VC_PORT_NM: '测试组合'
  },
  CASH_TYPE: 'CASH', // 或 'NON_CASH'
  RISK_FREE_RATE: '0.03'
}

const metaDataDesc = {
  IncomeStatistics: '这里是收益统计的说明文字'
}
</script>
```

### Props

#### IncomeStatisticsContainer

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| config | `Config` | `{}` | 配置对象，包含日期范围、组合信息等 |
| previewMode | `boolean` | `false` | 是否为预览模式 |
| metaDataDesc | `Record<string, string>` | `{}` | 元数据说明，用于显示帮助信息 |
| useMock | `boolean` | `false` | 是否使用模拟数据 |

#### CalendarChart

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| timeDimension | `'d' \| 'm' \| 'q'` | `'d'` | 时间维度：日/月/季 |
| calendarData | `DailyData[]` | `[]` | 日度数据 |
| monthData | `Record<string, MonthData>` | `{}` | 月度数据 |
| quarterData | `Record<string, QuarterData>` | `{}` | 季度数据 |
| cashType | `string` | `''` | 现金类型：CASH/NON_CASH |
| monthList | `string[]` | `[]` | 可选月份列表 |
| yearList | `string[]` | `[]` | 可选年份列表 |
| currentMonthIndex | `number` | `0` | 当前月份索引 |
| currentYearIndex | `number` | `0` | 当前年份索引 |

#### TrendChart

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| timeDimension | `'d' \| 'm' \| 'q'` | `'d'` | 时间维度：日/月/季 |
| dailyData | `DailyData[]` | `[]` | 日度数据 |
| monthlyData | `MonthData[]` | `[]` | 月度数据 |
| quarterlyData | `QuarterData[]` | `[]` | 季度数据 |
| cashType | `string` | `''` | 现金类型 |
| benchmarkName | `string` | `''` | 基准名称 |

### 事件

#### IncomeStatisticsContainer

| 事件名 | 参数 | 说明 |
|--------|------|------|
| refresh | - | 刷新数据 |

### 方法

通过 ref 可以调用以下方法：

```vue
<template>
  <IncomeStatisticsContainer ref="incomeStatsRef" />
</template>

<script setup>
const incomeStatsRef = ref()

// 刷新数据
incomeStatsRef.value.handleRefresh()

// 重新加载数据
incomeStatsRef.value.loadData()
</script>
```

## 数据结构

### 原始数据接口

```typescript
interface IncomeStatisticsData {
  VC_DATE_TYPE: 'D' | 'M' | 'Q' // 日期类型
  D_DATE_VALUE: string // 业务日期
  F_YIELD: number // 收益率
  F_BENCH_YIELD: number // 基准收益率
  F_MARKET_VALUE: number // 资产总值
  F_YIELD_HTD?: number // 累计收益率（仅日度）
  VC_BENCH_NM?: string // 基准名称
}
```

### 处理后数据接口

```typescript
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
```

## 模拟数据

组件支持使用模拟数据进行开发和测试。模拟数据生成器位于 `@/mock/incomeStatistics`：

```typescript
import { generateMockData } from '@/mock/incomeStatistics'

// 生成指定日期范围的模拟数据
const mockData = generateMockData('2024-01-01', '2024-12-31')
```

## 样式说明

组件沿用了原有的样式设计，包括：

- 日历热力图的配色方案（正值红色，负值绿色）
- 卡片布局的响应式设计
- 图表的交互效果

## 注意事项

1. 确保项目中已安装 ECharts 依赖
2. 需要配置 `@/components/Echarts` 组件路径
3. CSS 样式文件需要根据实际项目路径调整
4. 真实数据接口需要根据实际 API 调整 `loadRealData` 方法

## 迁移指南

从 Vue 2 版本迁移时：

1. 使用 `IncomeStatisticsContainer` 替代原来的 `IncomeStatistics`
2. Props 接口保持兼容，但建议使用新的类型定义
3. 事件和方法保持一致
4. 样式类名保持不变，确保样式兼容
