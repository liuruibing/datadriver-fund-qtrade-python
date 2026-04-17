<template>
  <div class="h-full bg-gray-50 text-gray-800 dashboard-container overflow-hidden flex flex-col no-page-scroll">

    <main class="w-full px-6 py-6 flex flex-col gap-6 flex-1 min-h-0 overflow-hidden">
      <!-- 第一行：左侧收益统计，右侧上下两层 -->
      <div class="flex flex-col xl:flex-row gap-6 xl:h-[600px]">
        <!-- 收益统计日历图 - 左侧 -->
        <section class="bg-white rounded-xl border border-gray-200 shadow-sm w-full xl:w-[522px] h-[400px] xl:h-[600px] shrink-0 flex flex-col min-h-0">
          <div class="p-3 border-b border-gray-100 shrink-0">
            <h2 class="text-base font-semibold text-gray-900 flex items-center gap-2">
              <div class="w-6 h-6 bg-orange-50 rounded-lg flex items-center justify-center">
                <svg class="w-3 h-3 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
              </div>
              收益统计
            </h2>
          </div>
          <div class="flex-1 p-3 overflow-hidden">
            <CalendarChart
              :time-dimension="safeTimeDimension"
              :calendar-data="calendarData"
              :month-data="monthData"
              :quarter-data="quarterData"
              :cash-type="'CASH'"
              :month-list="monthList"
              :year-list="yearList"
              :current-month-index="currentMonthIndex"
              :current-year-index="currentYearIndex"
              @update:current-month-index="currentMonthIndex = $event"
              @update:current-year-index="currentYearIndex = $event"
              @update:time-dimension="timeDimension = $event"
            />
          </div>
        </section>

        <!-- 右侧：上下两层 -->
        <div class="flex-1 flex flex-col gap-6 min-w-0">
          <!-- 上层：账户信息 + 重大舆情监控 + 快捷导航 -->
          <div class="flex flex-col lg:flex-row gap-4 lg:gap-6 lg:h-[260px] min-w-0">
            <!-- 账户概览卡片 - 2x2网格布局 -->
            <section class="grid grid-cols-2 gap-2.5 w-full lg:w-auto lg:min-w-[280px] lg:max-w-[360px] lg:shrink">
              <!-- 总资产卡片 -->
              <div class="relative bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 border border-blue-200 shadow-sm overflow-hidden">
                <div class="absolute top-0 right-0 w-16 h-16 bg-blue-200 rounded-full -mr-8 -mt-8 opacity-30"></div>
                <div class="relative">
                  <div class="flex items-center gap-1.5 mb-1.5">
                    <div class="w-6 h-6 bg-blue-500 rounded-lg flex items-center justify-center shadow-sm">
                      <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                      </svg>
                    </div>
                    <span class="text-gray-600 text-xs font-medium">总资产</span>
                  </div>
                  <div class="text-lg font-bold text-gray-900 mb-1">¥1,256,890</div>
                  <div class="flex items-center gap-1">
                    <svg class="w-2.5 h-2.5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
                    </svg>
                    <span class="text-red-500 text-xs font-semibold">+2.35%</span>
                  </div>
                </div>
              </div>
              
              <!-- 今日盈亏卡片 -->
              <div class="relative bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-3 border border-red-200 shadow-sm overflow-hidden">
                <div class="absolute top-0 right-0 w-16 h-16 bg-red-200 rounded-full -mr-8 -mt-8 opacity-30"></div>
                <div class="relative">
                  <div class="flex items-center gap-1.5 mb-1.5">
                    <div class="w-6 h-6 bg-red-500 rounded-lg flex items-center justify-center shadow-sm">
                      <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
                      </svg>
                    </div>
                    <span class="text-gray-600 text-xs font-medium">今日盈亏</span>
                  </div>
                  <div class="text-lg font-bold text-red-600 mb-1">+¥28,756</div>
                  <div class="text-gray-500 text-xs">已实现 ¥12,500</div>
                </div>
              </div>
              
              <!-- 持仓市值卡片 -->
              <div class="relative bg-gradient-to-br from-amber-50 to-amber-100 rounded-lg p-3 border border-amber-200 shadow-sm overflow-hidden">
                <div class="absolute top-0 right-0 w-16 h-16 bg-amber-200 rounded-full -mr-8 -mt-8 opacity-30"></div>
                <div class="relative">
                  <div class="flex items-center gap-1.5 mb-1.5">
                    <div class="w-6 h-6 bg-amber-500 rounded-lg flex items-center justify-center shadow-sm">
                      <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                      </svg>
                    </div>
                    <span class="text-gray-600 text-xs font-medium">持仓市值</span>
                  </div>
                  <div class="text-lg font-bold text-gray-900 mb-1">¥856,320</div>
                  <div class="flex items-center gap-1.5">
                    <div class="w-12 h-1 bg-gray-200 rounded-full overflow-hidden flex-1">
                      <div class="w-[68.1%] h-full bg-amber-500 rounded-full"></div>
                    </div>
                    <span class="text-gray-600 text-xs font-semibold">68.1%</span>
                  </div>
                </div>
              </div>
              
              <!-- 可用资金卡片 -->
              <div class="relative bg-gradient-to-br from-cyan-50 to-cyan-100 rounded-lg p-3 border border-cyan-200 shadow-sm overflow-hidden">
                <div class="absolute top-0 right-0 w-16 h-16 bg-cyan-200 rounded-full -mr-8 -mt-8 opacity-30"></div>
                <div class="relative">
                  <div class="flex items-center gap-1.5 mb-1.5">
                    <div class="w-6 h-6 bg-cyan-500 rounded-lg flex items-center justify-center shadow-sm">
                      <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"/>
                      </svg>
                    </div>
                    <span class="text-gray-600 text-xs font-medium">可用资金</span>
                  </div>
                  <div class="text-lg font-bold text-gray-900 mb-1">¥400,570</div>
                  <div class="flex items-center gap-1.5">
                    <div class="w-12 h-1 bg-gray-200 rounded-full overflow-hidden flex-1">
                      <div class="w-[31.9%] h-full bg-cyan-500 rounded-full"></div>
                    </div>
                    <span class="text-gray-600 text-xs font-semibold">31.9%</span>
                  </div>
                </div>
              </div>
            </section>

            <!-- 重大舆情监控 -->
            <section 
              class="bg-white rounded-xl border border-gray-200 shadow-sm flex-1 lg:flex-[2] flex flex-col min-h-0 min-w-0 sentiment-section"
              @mouseenter="handleMouseEnter"
              @mouseleave="handleMouseLeave">
              <div class="p-3 border-b border-gray-100 flex items-center justify-between shrink-0">
                <h2 class="text-base font-semibold text-gray-900 flex items-center gap-2">
                  <div class="w-6 h-6 bg-cyan-50 rounded-lg flex items-center justify-center">
                    <svg class="w-3 h-3 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/>
                    </svg>
                  </div>
                  重大舆情监控
                </h2>
                <button class="text-xs text-blue-500 hover:text-blue-600 transition-colors">查看更多</button>
              </div>
              <div 
                ref="sentimentScrollRef"
                class="flex-1 overflow-y-auto sentiment-scroll-container">
                <div class="flex flex-col">
                  <div 
                    v-for="(news, index) in sentimentNews" 
                    :key="news.id" 
                    :class="[
                      'relative p-3 transition-all duration-200 cursor-pointer group overflow-hidden',
                      news.sentiment === 'positive' 
                        ? 'bg-gradient-to-r from-red-50/50 via-white to-white hover:from-red-50 hover:via-red-50/30 hover:to-white border-l-3 border-red-400' 
                        : news.sentiment === 'negative' 
                        ? 'bg-gradient-to-r from-emerald-50/50 via-white to-white hover:from-emerald-50 hover:via-emerald-50/30 hover:to-white border-l-3 border-emerald-400'
                        : 'bg-gradient-to-r from-gray-50/50 via-white to-white hover:from-gray-50 hover:via-gray-50/30 hover:to-white border-l-3 border-gray-400'
                    ]">
                    <!-- 装饰性背景元素 -->
                    <div 
                      :class="[
                        'absolute top-0 right-0 w-20 h-20 rounded-full opacity-5 transition-opacity duration-200 group-hover:opacity-10',
                        news.sentiment === 'positive' ? 'bg-red-400' 
                        : news.sentiment === 'negative' ? 'bg-emerald-400'
                        : 'bg-gray-400'
                      ]"
                      style="transform: translate(30%, -30%);">
                    </div>
                    <div class="flex items-center gap-2.5 relative z-10">
                      <div 
                        :class="[
                          'px-2 py-0.5 rounded text-xs font-bold shrink-0 shadow-sm',
                          news.sentiment === 'positive' ? 'bg-red-500 text-white' 
                          : news.sentiment === 'negative' ? 'bg-emerald-500 text-white' 
                          : 'bg-gray-500 text-white'
                        ]">
                        {{ news.sentiment === 'positive' ? '利好' : news.sentiment === 'negative' ? '利空' : '中性' }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="font-medium text-gray-900 mb-1 text-xs line-clamp-2 group-hover:text-gray-800 transition-colors">{{ news.title }}</div>
                        <div class="flex items-center gap-2 text-xs text-gray-500 flex-wrap">
                          <span 
                            :class="[
                              'px-1.5 py-0.5 rounded text-xs font-medium',
                              news.sentiment === 'positive' ? 'bg-red-100 text-red-700' 
                              : news.sentiment === 'negative' ? 'bg-emerald-100 text-emerald-700'
                              : 'bg-gray-100 text-gray-700'
                            ]">
                            {{ news.relatedStock }}
                          </span>
                          <span class="text-xs">{{ news.source }}</span>
                          <span class="text-xs">{{ news.time }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <!-- 快捷导航菜单 -->
            <section class="bg-white rounded-xl border border-gray-200 shadow-sm flex-1 lg:flex-[1] flex flex-col min-h-0 min-w-0">
              <div class="p-3 border-b border-gray-100 shrink-0">
                <h2 class="text-base font-semibold text-gray-900 flex items-center gap-2">
                  <div class="w-6 h-6 bg-indigo-50 rounded-lg flex items-center justify-center">
                    <svg class="w-3 h-3 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7"/>
                    </svg>
                  </div>
                  快捷导航
                </h2>
              </div>
              <div class="p-3 grid grid-cols-2 gap-2 overflow-y-auto flex-1 custom-scrollbar">
                <!-- 行情分析 -->
                <a href="#" class="flex flex-col items-center gap-1 p-2 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors group">
                  <div class="w-8 h-8 rounded-lg flex items-center justify-center bg-blue-100">
                    <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                    </svg>
                  </div>
                  <span class="text-xs text-gray-600 group-hover:text-gray-900">行情分析</span>
                </a>
                <!-- 策略管理 -->
                <a href="#" class="flex flex-col items-center gap-1 p-2 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors group">
                  <div class="w-8 h-8 rounded-lg flex items-center justify-center bg-emerald-100">
                    <svg class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                    </svg>
                  </div>
                  <span class="text-xs text-gray-600 group-hover:text-gray-900">策略管理</span>
                </a>
                <!-- 历史回测 -->
                <a href="#" class="flex flex-col items-center gap-1 p-2 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors group">
                  <div class="w-8 h-8 rounded-lg flex items-center justify-center bg-amber-100">
                    <svg class="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                  </div>
                  <span class="text-xs text-gray-600 group-hover:text-gray-900">历史回测</span>
                </a>
                <!-- 模拟交易 -->
                <a href="#" class="flex flex-col items-center gap-1 p-2 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors group">
                  <div class="w-8 h-8 rounded-lg flex items-center justify-center bg-rose-100">
                    <svg class="w-4 h-4 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/>
                    </svg>
                  </div>
                  <span class="text-xs text-gray-600 group-hover:text-gray-900">模拟交易</span>
                </a>
                <!-- 收益报表 -->
                <a href="#" class="flex flex-col items-center gap-1 p-2 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors group">
                  <div class="w-8 h-8 rounded-lg flex items-center justify-center bg-indigo-100">
                    <svg class="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                    </svg>
                  </div>
                  <span class="text-xs text-gray-600 group-hover:text-gray-900">收益报表</span>
                </a>
                <!-- 系统设置 -->
                <a href="#" class="flex flex-col items-center gap-1 p-2 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors group">
                  <div class="w-8 h-8 rounded-lg flex items-center justify-center bg-gray-200">
                    <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                    </svg>
                  </div>
                  <span class="text-xs text-gray-600 group-hover:text-gray-900">系统设置</span>
                </a>
              </div>
            </section>
          </div>

          <!-- 下层：买卖点信号 -->
          <section class="bg-white rounded-xl border border-gray-200 shadow-sm flex-1 flex flex-col min-h-0 min-w-0 overflow-hidden">
            <div class="p-5 border-b border-gray-100 flex items-center justify-between shrink-0">
              <h2 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <div class="w-8 h-8 bg-amber-50 rounded-lg flex items-center justify-center">
                  <svg class="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
                  </svg>
                </div>
                买卖点信号
              </h2>
              <div class="flex items-center gap-3">
                <span class="flex items-center gap-1 text-xs text-gray-500">
                  <span class="w-2 h-2 rounded-full bg-red-500"></span>买入
                </span>
                <span class="flex items-center gap-1 text-xs text-gray-500">
                  <span class="w-2 h-2 rounded-full bg-emerald-500"></span>卖出
                </span>
              </div>
            </div>
            <div class="flex-1 min-h-0 custom-scrollbar">
              <el-table 
                :data="tradingSignals" 
                class="trading-signals-table"
                :row-class-name="() => 'hover:bg-gray-50'"
                style="height: 100%;"
                fit>
                <el-table-column prop="stockName" label="股票" min-width="120">
                  <template #default="{ row }">
                    <div>
                      <div class="font-medium text-gray-900 text-sm">{{ row.stockName }}</div>
                      <div class="text-gray-400 text-xs">{{ row.code }}</div>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="日" min-width="100">
                  <template #default="{ row }">
                    <div v-if="row.daily" :class="getSignalClass(row.daily)" 
                         class="px-2 py-1 rounded text-xs font-bold text-center inline-block min-w-[70px]">
                      {{ formatSignal(row.daily) }}
                    </div>
                    <span v-else class="text-gray-300 text-xs">-</span>
                  </template>
                </el-table-column>
                <el-table-column label="周" min-width="100">
                  <template #default="{ row }">
                    <div v-if="row.weekly" :class="getSignalClass(row.weekly)" 
                         class="px-2 py-1 rounded text-xs font-bold text-center inline-block min-w-[70px]">
                      {{ formatSignal(row.weekly) }}
                    </div>
                    <span v-else class="text-gray-300 text-xs">-</span>
                  </template>
                </el-table-column>
                <el-table-column label="30分钟" min-width="100">
                  <template #default="{ row }">
                    <div v-if="row.minute30" :class="getSignalClass(row.minute30)" 
                         class="px-2 py-1 rounded text-xs font-bold text-center inline-block min-w-[70px]">
                      {{ formatSignal(row.minute30) }}
                    </div>
                    <span v-else class="text-gray-300 text-xs">-</span>
                  </template>
                </el-table-column>
                <el-table-column label="时间" min-width="100" align="right">
                  <template #default="{ row }">
                    <span class="text-xs text-gray-600 font-mono">{{ formatTime(row.time) }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="AI评价" min-width="120">
                  <template #default="{ row }">
                    <div class="flex items-center gap-0.5">
                      <svg v-for="i in 5" :key="i" 
                           :class="i <= row.aiStars ? 'text-amber-400' : 'text-gray-200'"
                           class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                      </svg>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="舆情" min-width="200">
                  <template #default="{ row }">
                    <div v-if="row.sentiment && (row.sentiment.positive > 0 || row.sentiment.negative > 0 || row.sentiment.neutral > 0)" class="flex flex-col gap-1.5">
                      <!-- 进度条 -->
                      <div class="w-full h-2.5 bg-gray-100 rounded-full overflow-hidden flex">
                        <div 
                          v-if="row.sentiment.positive > 0"
                          class="bg-red-500 h-full transition-all"
                          :style="{ width: `${getSentimentPercentage(row.sentiment, 'positive')}%` }">
                        </div>
                        <div 
                          v-if="row.sentiment.negative > 0"
                          class="bg-emerald-500 h-full transition-all"
                          :style="{ width: `${getSentimentPercentage(row.sentiment, 'negative')}%` }">
                        </div>
                        <div 
                          v-if="row.sentiment.neutral > 0"
                          class="bg-gray-400 h-full transition-all"
                          :style="{ width: `${getSentimentPercentage(row.sentiment, 'neutral')}%` }">
                        </div>
                      </div>
                      <!-- 数字标签 -->
                      <div class="flex items-center gap-3 text-xs flex-wrap">
                        <div v-if="row.sentiment.positive > 0" class="flex items-center gap-1">
                          <span class="w-2 h-2 rounded-full bg-red-500"></span>
                          <span class="text-red-600 font-medium">利好 {{ row.sentiment.positive }}</span>
                        </div>
                        <div v-if="row.sentiment.negative > 0" class="flex items-center gap-1">
                          <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                          <span class="text-emerald-600 font-medium">利空 {{ row.sentiment.negative }}</span>
                        </div>
                        <div v-if="row.sentiment.neutral > 0" class="flex items-center gap-1">
                          <span class="w-2 h-2 rounded-full bg-gray-400"></span>
                          <span class="text-gray-500 font-medium">中性 {{ row.sentiment.neutral }}</span>
                        </div>
                      </div>
                    </div>
                    <span v-else class="text-xs text-gray-300">-</span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </section>
        </div>
      </div>

      <!-- 第二行：我的持仓 + 走势图 -->
      <div class="flex flex-row gap-6 min-h-0" style="height: 660px;">
        <!-- 我的持仓 -->
        <section class="bg-white rounded-xl border border-gray-200 shadow-sm flex-1 flex flex-col overflow-hidden min-w-0">
          <div class="p-5 border-b border-gray-100 flex items-center justify-between shrink-0">
            <h2 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <div class="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
                </svg>
              </div>
              我的持仓
            </h2>
            <button class="text-sm text-blue-500 hover:text-blue-600 transition-colors">查看全部</button>
          </div>
          <div class="flex-1 min-h-0 custom-scrollbar">
            <el-table 
              :data="positions" 
              class="positions-table"
              :row-class-name="() => 'hover:bg-gray-50'"
              style="height: 100%;"
              fit>
              <el-table-column prop="name" label="股票" min-width="150">
                <template #default="{ row }">
                  <div>
                    <div class="font-medium text-gray-900 text-sm">{{ row.name }}</div>
                    <div class="text-gray-400 text-xs">{{ row.code }}</div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="现价" min-width="120" align="right">
                <template #default="{ row }">
                  <span class="text-sm text-gray-900">¥{{ row.currentPrice.toFixed(2) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="成本" min-width="120" align="right">
                <template #default="{ row }">
                  <span class="text-sm text-gray-900">¥{{ row.costPrice.toFixed(2) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="数量" min-width="100" align="right">
                <template #default="{ row }">
                  <span class="text-sm text-gray-900">{{ row.quantity.toLocaleString() }}</span>
                </template>
              </el-table-column>
              <el-table-column label="盈亏" min-width="120" align="right">
                <template #default="{ row }">
                  <span class="text-sm" :class="row.profit >= 0 ? 'text-red-500' : 'text-emerald-500'">
                    {{ row.profit >= 0 ? '+' : '' }}¥{{ row.profit.toLocaleString() }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="收益率" min-width="120" align="right">
                <template #default="{ row }">
                  <span :class="row.profitRate >= 0 ? 'bg-red-100 text-red-600' : 'bg-emerald-100 text-emerald-600'" 
                        class="px-2 py-0.5 rounded text-xs font-medium inline-block">
                    {{ row.profitRate >= 0 ? '+' : '' }}{{ row.profitRate.toFixed(2) }}%
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </section>

        <!-- 走势图 -->
        <section class="bg-white rounded-xl border border-gray-200 shadow-sm flex-1 flex flex-col overflow-hidden min-w-0">
          <div class="p-5 border-b border-gray-100 flex items-center justify-between shrink-0">
            <h2 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <div class="w-8 h-8 bg-purple-50 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"/>
                </svg>
              </div>
              收益走势
            </h2>
          </div>
          <div class="flex-1 min-h-0 p-3">
            <TrendChart
              :time-dimension="safeTimeDimension"
              :daily-data="trendDailyData"
              :monthly-data="trendMonthlyData"
              :quarterly-data="trendQuarterlyData"
              :cash-type="'CASH'"
              :benchmark-name="'沪深300'"
            />
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import CalendarChart from '../../components/IncomeStatistics/CalendarChart.vue'
import TrendChart from '../../components/IncomeStatistics/TrendChart.vue'

// 重大舆情监控滚动相关
const sentimentScrollRef = ref(null)
const isHovered = ref(false) // 鼠标是否悬停
const scrollTimer = ref(null) // 滚动定时器
const scrollSpeed = 30 // 滚动速度（毫秒）

// 自动滚动函数
const startAutoScroll = () => {
  if (scrollTimer.value) {
    clearInterval(scrollTimer.value)
  }
  
  scrollTimer.value = setInterval(() => {
    if (!isHovered.value && sentimentScrollRef.value) {
      const container = sentimentScrollRef.value
      const scrollHeight = container.scrollHeight
      const clientHeight = container.clientHeight
      const scrollTop = container.scrollTop
      
      // 如果已经滚动到底部，平滑重置到第一条数据的位置
      if (scrollTop + clientHeight >= scrollHeight - 1) {
        // 暂停当前滚动
        clearInterval(scrollTimer.value)
        scrollTimer.value = null
        
        // 平滑滚动到顶部
        container.scrollTo({ top: 0, behavior: 'smooth' })
        
        // 等待滚动完成后重新开始自动滚动
        setTimeout(() => {
          if (!isHovered.value) {
            startAutoScroll()
          }
        }, 500) // 等待平滑滚动完成
      } else {
        // 平滑向下滚动
        container.scrollTop += 0.5
      }
    }
  }, scrollSpeed)
}

// 鼠标进入 - 暂停滚动
const handleMouseEnter = () => {
  isHovered.value = true
  if (scrollTimer.value) {
    clearInterval(scrollTimer.value)
    scrollTimer.value = null
  }
}

// 鼠标离开 - 恢复滚动
const handleMouseLeave = () => {
  isHovered.value = false
  startAutoScroll()
}

// 隐藏父容器的滚动条并启动自动滚动
onMounted(() => {
  const scrollbarWrap = document.querySelector('.layout-main-scroll .el-scrollbar__wrap')
  const scrollbarBar = document.querySelector('.layout-main-scroll .el-scrollbar__bar')
  if (scrollbarWrap) {
    scrollbarWrap.style.overflow = 'hidden'
  }
  if (scrollbarBar) {
    scrollbarBar.style.display = 'none'
  }
  
  // 启动自动滚动
  nextTick(() => {
    startAutoScroll()
  })
})

onUnmounted(() => {
  const scrollbarWrap = document.querySelector('.layout-main-scroll .el-scrollbar__wrap')
  const scrollbarBar = document.querySelector('.layout-main-scroll .el-scrollbar__bar')
  if (scrollbarWrap) {
    scrollbarWrap.style.overflow = ''
  }
  if (scrollbarBar) {
    scrollbarBar.style.display = ''
  }
  
  // 清理滚动定时器
  if (scrollTimer.value) {
    clearInterval(scrollTimer.value)
    scrollTimer.value = null
  }
})

// CalendarChart 数据
const calendarData = ref([
  { D_DATE: '2024-01-01', F_YIELD_D: 0.0125, F_BENCH_YIELD_D: 0.0105, F_ICM_D: 1256.8, F_YIELD_HTD: 0.0125 },
  { D_DATE: '2024-01-02', F_YIELD_D: 0.0225, F_BENCH_YIELD_D: 0.0185, F_ICM_D: 1285.5, F_YIELD_HTD: 0.0175 },
  { D_DATE: '2024-01-03', F_YIELD_D: -0.0055, F_BENCH_YIELD_D: -0.0035, F_ICM_D: 1278.3, F_YIELD_HTD: 0.0120 },
  { D_DATE: '2024-01-04', F_YIELD_D: 0.0189, F_BENCH_YIELD_D: 0.0159, F_ICM_D: 1302.6, F_YIELD_HTD: 0.0309 },
  { D_DATE: '2024-01-05', F_YIELD_D: -0.0030, F_BENCH_YIELD_D: -0.0020, F_ICM_D: 1298.7, F_YIELD_HTD: 0.0279 },
  { D_DATE: '2024-01-06', F_YIELD_D: 0.0125, F_BENCH_YIELD_D: 0.0105, F_ICM_D: 1315.2, F_YIELD_HTD: 0.0404 },
  { D_DATE: '2024-01-07', F_YIELD_D: 0.0104, F_BENCH_YIELD_D: 0.0084, F_ICM_D: 1328.9, F_YIELD_HTD: 0.0508 },
  { D_DATE: '2024-01-08', F_YIELD_D: 0.0100, F_BENCH_YIELD_D: 0.0080, F_ICM_D: 1342.1, F_YIELD_HTD: 0.0608 },
  { D_DATE: '2024-01-09', F_YIELD_D: -0.0048, F_BENCH_YIELD_D: -0.0038, F_ICM_D: 1335.7, F_YIELD_HTD: 0.0560 },
  { D_DATE: '2024-01-10', F_YIELD_D: 0.0158, F_BENCH_YIELD_D: 0.0138, F_ICM_D: 1356.8, F_YIELD_HTD: 0.0718 },
  { D_DATE: '2024-01-11', F_YIELD_D: 0.0085, F_BENCH_YIELD_D: 0.0065, F_ICM_D: 1368.3, F_YIELD_HTD: 0.0803 },
  { D_DATE: '2024-01-12', F_YIELD_D: 0.0105, F_BENCH_YIELD_D: 0.0085, F_ICM_D: 1382.5, F_YIELD_HTD: 0.0908 },
  { D_DATE: '2024-01-13', F_YIELD_D: -0.0048, F_BENCH_YIELD_D: -0.0038, F_ICM_D: 1375.9, F_YIELD_HTD: 0.0860 },
  { D_DATE: '2024-01-14', F_YIELD_D: 0.0139, F_BENCH_YIELD_D: 0.0119, F_ICM_D: 1395.2, F_YIELD_HTD: 0.0999 },
  { D_DATE: '2024-01-15', F_YIELD_D: 0.0097, F_BENCH_YIELD_D: 0.0077, F_ICM_D: 1408.7, F_YIELD_HTD: 0.1096 },
  { D_DATE: '2024-01-16', F_YIELD_D: 0.0026, F_BENCH_YIELD_D: 0.0021, F_ICM_D: 1412.3, F_YIELD_HTD: 0.1122 },
  { D_DATE: '2024-01-17', F_YIELD_D: -0.0097, F_BENCH_YIELD_D: -0.0077, F_ICM_D: 1398.6, F_YIELD_HTD: 0.1025 },
  { D_DATE: '2024-01-18', F_YIELD_D: 0.0194, F_BENCH_YIELD_D: 0.0164, F_ICM_D: 1425.8, F_YIELD_HTD: 0.1219 },
  { D_DATE: '2024-01-19', F_YIELD_D: 0.0092, F_BENCH_YIELD_D: 0.0072, F_ICM_D: 1438.9, F_YIELD_HTD: 0.1311 },
  { D_DATE: '2024-01-20', F_YIELD_D: -0.0045, F_BENCH_YIELD_D: -0.0035, F_ICM_D: 1432.5, F_YIELD_HTD: 0.1266 },
  { D_DATE: '2024-01-21', F_YIELD_D: 0.0165, F_BENCH_YIELD_D: 0.0145, F_ICM_D: 1456.2, F_YIELD_HTD: 0.1431 },
  { D_DATE: '2024-01-22', F_YIELD_D: 0.0086, F_BENCH_YIELD_D: 0.0066, F_ICM_D: 1468.7, F_YIELD_HTD: 0.1517 },
  { D_DATE: '2024-01-23', F_YIELD_D: -0.0091, F_BENCH_YIELD_D: -0.0071, F_ICM_D: 1455.3, F_YIELD_HTD: 0.1426 },
  { D_DATE: '2024-01-24', F_YIELD_D: 0.0162, F_BENCH_YIELD_D: 0.0142, F_ICM_D: 1478.9, F_YIELD_HTD: 0.1588 },
  { D_DATE: '2024-01-25', F_YIELD_D: 0.0092, F_BENCH_YIELD_D: 0.0072, F_ICM_D: 1492.4, F_YIELD_HTD: 0.1680 },
  { D_DATE: '2024-01-26', F_YIELD_D: -0.0044, F_BENCH_YIELD_D: -0.0034, F_ICM_D: 1485.8, F_YIELD_HTD: 0.1636 },
  { D_DATE: '2024-01-27', F_YIELD_D: 0.0153, F_BENCH_YIELD_D: 0.0133, F_ICM_D: 1508.6, F_YIELD_HTD: 0.1789 },
  { D_DATE: '2024-01-28', F_YIELD_D: 0.0044, F_BENCH_YIELD_D: 0.0034, F_ICM_D: 1515.2, F_YIELD_HTD: 0.1833 },
  { D_DATE: '2024-01-29', F_YIELD_D: -0.0109, F_BENCH_YIELD_D: -0.0089, F_ICM_D: 1498.7, F_YIELD_HTD: 0.1724 },
  { D_DATE: '2024-01-30', F_YIELD_D: 0.0201, F_BENCH_YIELD_D: 0.0181, F_ICM_D: 1528.9, F_YIELD_HTD: 0.1925 },
  { D_DATE: '2024-01-31', F_YIELD_D: 0.0091, F_BENCH_YIELD_D: 0.0071, F_ICM_D: 1542.6, F_YIELD_HTD: 0.2016 }
])

const monthData = ref([
  { month: '2023-08', value: 1156.8 },
  { month: '2023-09', value: 1185.5 },
  { month: '2023-10', value: 1208.3 },
  { month: '2023-11', value: 1232.6 },
  { month: '2023-12', value: 1258.7 },
  { month: '2024-01', value: 1285.5 }
])

const quarterData = ref([
  { quarter: '2023-Q2', value: 1085.6 },
  { quarter: '2023-Q3', value: 1125.8 },
  { quarter: '2023-Q4', value: 1185.5 },
  { quarter: '2024-Q1', value: 1256.8 }
])

const monthList = ref(['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'])
const yearList = ref(['2023', '2024', '2025'])
const currentMonthIndex = ref(0)
const currentYearIndex = ref(1)
const timeDimension = ref('d')

// 确保 timeDimension 始终是有效字符串
const safeTimeDimension = computed(() => {
  const val = timeDimension.value
  if (!val || typeof val === 'undefined') return 'd'
  if (typeof val === 'number') {
    if (val === 1) return 'd'
    if (val === 2) return 'm'
    if (val === 3) return 'q'
    return 'd'
  }
  if (['d', 'm', 'q'].includes(val)) return val
  return 'd'
})

const marketIndices = ref([
  { name: '上证指数', value: '3,256.78', change: 1.25 },
  { name: '深证成指', value: '10,892.34', change: 1.58 },
  { name: '创业板指', value: '2,156.89', change: -0.32 },
  { name: '科创50', value: '986.45', change: 2.15 }
])

const positions = ref([
  { code: '600519', name: '贵州茅台', quantity: 100, costPrice: 1680.00, currentPrice: 1756.50, profit: 7650, profitRate: 4.55 },
  { code: '000858', name: '五粮液', quantity: 500, costPrice: 152.30, currentPrice: 168.90, profit: 8300, profitRate: 10.90 },
  { code: '300750', name: '宁德时代', quantity: 200, costPrice: 225.60, currentPrice: 198.30, profit: -5460, profitRate: -12.10 },
  { code: '601318', name: '中国平安', quantity: 1000, costPrice: 48.50, currentPrice: 52.80, profit: 4300, profitRate: 8.87 }
])

const trendDailyData = ref([
  { D_DATE: '01-02', F_YIELD_D: 0.5, F_BENCH_YIELD_D: 0.3, F_ICM_D: 100, F_YIELD_HTD: 0.5 },
  { D_DATE: '01-03', F_YIELD_D: -0.2, F_BENCH_YIELD_D: -0.1, F_ICM_D: 99.8, F_YIELD_HTD: 0.3 },
  { D_DATE: '01-06', F_YIELD_D: 0.8, F_BENCH_YIELD_D: 0.5, F_ICM_D: 100.6, F_YIELD_HTD: 1.1 },
  { D_DATE: '01-07', F_YIELD_D: 0.3, F_BENCH_YIELD_D: 0.2, F_ICM_D: 100.9, F_YIELD_HTD: 1.4 },
  { D_DATE: '01-08', F_YIELD_D: -0.5, F_BENCH_YIELD_D: -0.3, F_ICM_D: 100.4, F_YIELD_HTD: 0.9 },
  { D_DATE: '01-09', F_YIELD_D: 1.2, F_BENCH_YIELD_D: 0.8, F_ICM_D: 101.6, F_YIELD_HTD: 2.1 },
  { D_DATE: '01-10', F_YIELD_D: 0.1, F_BENCH_YIELD_D: 0.0, F_ICM_D: 101.7, F_YIELD_HTD: 2.2 },
  { D_DATE: '01-13', F_YIELD_D: -0.3, F_BENCH_YIELD_D: -0.2, F_ICM_D: 101.4, F_YIELD_HTD: 1.9 }
])

const trendMonthlyData = ref([
  { MDTE: '2023-07', F_YIELD_M: 2.5, F_BENCH_YIELD_M: 1.8, F_ICM_M: 102.5 },
  { MDTE: '2023-08', F_YIELD_M: -1.2, F_BENCH_YIELD_M: -0.8, F_ICM_M: 101.3 },
  { MDTE: '2023-09', F_YIELD_M: 1.8, F_BENCH_YIELD_M: 1.2, F_ICM_M: 103.1 },
  { MDTE: '2023-10', F_YIELD_M: 0.5, F_BENCH_YIELD_M: 0.3, F_ICM_M: 103.6 },
  { MDTE: '2023-11', F_YIELD_M: 3.2, F_BENCH_YIELD_M: 2.1, F_ICM_M: 106.8 },
  { MDTE: '2023-12', F_YIELD_M: -0.8, F_BENCH_YIELD_M: -0.5, F_ICM_M: 106.0 }
])

const trendQuarterlyData = ref([
  { QDTE: '2023-Q1', F_YIELD_Q: 5.2, F_BENCH_YIELD_Q: 3.8, F_ICM_Q: 105.2 },
  { QDTE: '2023-Q2', F_YIELD_Q: -2.1, F_BENCH_YIELD_Q: -1.5, F_ICM_Q: 103.1 },
  { QDTE: '2023-Q3', F_YIELD_Q: 3.5, F_BENCH_YIELD_Q: 2.4, F_ICM_Q: 106.6 },
  { QDTE: '2023-Q4', F_YIELD_Q: 1.8, F_BENCH_YIELD_Q: 1.2, F_ICM_Q: 108.4 }
])

const tradingSignals = ref([
  { 
    id: 1, 
    stockName: '比亚迪', 
    code: '002594', 
    daily: { type: 'buy', level: 1 },
    weekly: { type: 'buy', level: 2 },
    minute30: { type: 'buy', level: 1 },
    time: '2024-01-15 10:35:23', 
    aiStars: 4,
    sentiment: { positive: 8, negative: 2, neutral: 2 }
  },
  { 
    id: 2, 
    stockName: '宁德时代', 
    code: '300750', 
    daily: { type: 'sell', level: 2 },
    weekly: { type: 'sell', level: 1 },
    minute30: null,
    time: '2024-01-15 10:22:15', 
    aiStars: 3,
    sentiment: { positive: 2, negative: 5, neutral: 1 }
  },
  { 
    id: 3, 
    stockName: '隆基绿能', 
    code: '601012', 
    daily: { type: 'buy', level: 3 },
    weekly: { type: 'buy', level: 2 },
    minute30: { type: 'buy', level: 2 },
    time: '2024-01-15 09:58:42', 
    aiStars: 4,
    sentiment: { positive: 10, negative: 3, neutral: 2 }
  },
  { 
    id: 4, 
    stockName: '贵州茅台', 
    code: '600519', 
    daily: { type: 'sell', level: 1 },
    weekly: null,
    minute30: { type: 'sell', level: 1 },
    time: '2024-01-15 09:45:08', 
    aiStars: 5,
    sentiment: { positive: 15, negative: 6, neutral: 4 }
  },
  { 
    id: 5, 
    stockName: '中国中免', 
    code: '601888', 
    daily: { type: 'buy', level: 2 },
    weekly: { type: 'buy', level: 1 },
    minute30: { type: 'buy', level: 3 },
    time: '2024-01-15 09:32:56', 
    aiStars: 3,
    sentiment: { positive: 4, negative: 1, neutral: 1 }
  },
  { 
    id: 6, 
    stockName: '中国平安', 
    code: '601318', 
    daily: { type: 'buy', level: 1 },
    weekly: { type: 'buy', level: 1 },
    minute30: { type: 'buy', level: 2 },
    time: '2024-01-15 09:15:33', 
    aiStars: 5,
    sentiment: { positive: 12, negative: 4, neutral: 2 }
  },
  { 
    id: 7, 
    stockName: '五粮液', 
    code: '000858', 
    daily: { type: 'sell', level: 3 },
    weekly: { type: 'sell', level: 2 },
    minute30: { type: 'sell', level: 1 },
    time: '2024-01-15 09:08:17', 
    aiStars: 2,
    sentiment: { positive: 1, negative: 3, neutral: 1 }
  },
  { 
    id: 8, 
    stockName: '招商银行', 
    code: '600036', 
    daily: { type: 'buy', level: 2 },
    weekly: { type: 'buy', level: 1 },
    minute30: null,
    time: '2024-01-15 08:55:42', 
    aiStars: 4,
    sentiment: { positive: 14, negative: 5, neutral: 3 }
  },
  { 
    id: 9, 
    stockName: '美的集团', 
    code: '000333', 
    daily: { type: 'buy', level: 1 },
    weekly: { type: 'buy', level: 3 },
    minute30: { type: 'buy', level: 1 },
    time: '2024-01-15 08:42:28', 
    aiStars: 4,
    sentiment: { positive: 9, negative: 3, neutral: 2 }
  },
  { 
    id: 10, 
    stockName: '三一重工', 
    code: '600031', 
    daily: { type: 'sell', level: 1 },
    weekly: { type: 'sell', level: 1 },
    minute30: { type: 'sell', level: 2 },
    time: '2024-01-15 08:30:55', 
    aiStars: 3,
    sentiment: { positive: 3, negative: 5, neutral: 1 }
  },
  { 
    id: 11, 
    stockName: '海康威视', 
    code: '002415', 
    daily: { type: 'buy', level: 2 },
    weekly: { type: 'buy', level: 2 },
    minute30: { type: 'buy', level: 3 },
    time: '2024-01-15 08:18:12', 
    aiStars: 4,
    sentiment: { positive: 10, negative: 4, neutral: 2 }
  },
  { 
    id: 12, 
    stockName: '东方财富', 
    code: '300059', 
    daily: { type: 'buy', level: 3 },
    weekly: { type: 'buy', level: 1 },
    minute30: { type: 'buy', level: 1 },
    time: '2024-01-15 08:05:37', 
    aiStars: 5,
    sentiment: { positive: 18, negative: 6, neutral: 4 }
  },
  { 
    id: 13, 
    stockName: '药明康德', 
    code: '603259', 
    daily: { type: 'sell', level: 2 },
    weekly: null,
    minute30: { type: 'sell', level: 1 },
    time: '2024-01-15 07:52:44', 
    aiStars: 2,
    sentiment: { positive: 2, negative: 4, neutral: 1 }
  },
  { 
    id: 14, 
    stockName: '中芯国际', 
    code: '688981', 
    daily: { type: 'buy', level: 1 },
    weekly: { type: 'buy', level: 1 },
    minute30: { type: 'buy', level: 2 },
    time: '2024-01-15 07:40:19', 
    aiStars: 5,
    sentiment: { positive: 20, negative: 7, neutral: 4 }
  },
  { 
    id: 15, 
    stockName: '紫金矿业', 
    code: '601899', 
    daily: { type: 'buy', level: 2 },
    weekly: { type: 'buy', level: 3 },
    minute30: null,
    time: '2024-01-15 07:28:06', 
    aiStars: 3,
    sentiment: { positive: 7, negative: 2, neutral: 2 }
  }
])

// 格式化信号显示
const formatSignal = (signal) => {
  if (!signal) return ''
  const levelMap = {
    1: '一类',
    2: '二类',
    3: '三类'
  }
  const typeMap = {
    buy: '买入',
    sell: '卖出'
  }
  return `${levelMap[signal.level] || '三类'} ${typeMap[signal.type] || ''}`
}

// 获取信号样式类
const getSignalClass = (signal) => {
  if (!signal) return ''
  if (signal.type === 'buy') {
    // 买入信号（利好）：红色系
    const classMap = {
      1: 'bg-red-100 text-red-700',
      2: 'bg-red-50 text-red-600',
      3: 'bg-red-50/50 text-red-500'
    }
    return classMap[signal.level] || 'bg-red-50 text-red-600'
  } else {
    // 卖出信号（利空）：绿色系
    const classMap = {
      1: 'bg-emerald-100 text-emerald-700',
      2: 'bg-emerald-50 text-emerald-600',
      3: 'bg-emerald-50/50 text-emerald-500'
    }
    return classMap[signal.level] || 'bg-emerald-50 text-emerald-600'
  }
}

// 计算舆情占比
const getSentimentPercentage = (sentiment, type) => {
  if (!sentiment) return 0
  const total = sentiment.positive + sentiment.negative + sentiment.neutral
  if (total === 0) return 0
  return (sentiment[type] / total) * 100
}

// 格式化时间显示（显示年月日和时分秒）
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  // 如果已经是完整日期时间格式（YYYY-MM-DD HH:mm:ss），直接返回
  if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(timeStr)) {
    return timeStr
  }
  // 尝试解析为Date对象
  const date = new Date(timeStr)
  if (!isNaN(date.getTime())) {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  }
  // 如果包含日期和时间，尝试提取
  const match = timeStr.match(/(\d{4}-\d{2}-\d{2})[\sT](\d{2}):(\d{2}):(\d{2})/)
  if (match) {
    return `${match[1]} ${match[2]}:${match[3]}:${match[4]}`
  }
  // 如果只有时间，尝试补充当前日期
  const timeMatch = timeStr.match(/(\d{2}):(\d{2}):(\d{2})/)
  if (timeMatch) {
    const now = new Date()
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    const day = String(now.getDate()).padStart(2, '0')
    return `${year}-${month}-${day} ${timeMatch[1]}:${timeMatch[2]}:${timeMatch[3]}`
  }
  return timeStr
}

// 格式化标签文本（移除方向符号用于显示）
const formatTagText = (tag) => {
  return tag.replace(/[↑↓]/g, '')
}

// 获取标签样式类
const getTagClass = (tag) => {
  // 均线相关 - 根据方向设置颜色
  if (tag.includes('MA') || tag.includes('均线')) {
    if (tag.includes('↑')) {
      // 向上突破，看涨信号 - 绿色
      return 'bg-emerald-100 text-emerald-600'
    } else if (tag.includes('↓')) {
      // 向下跌破，看跌信号 - 红色
      return 'bg-red-100 text-red-600'
    } else {
      // 无方向信息 - 橙色
      return 'bg-orange-100 text-orange-600'
    }
  }
  // MACD相关
  if (tag.includes('MACD') || tag.includes('金叉') || tag.includes('死叉')) {
    return 'bg-blue-100 text-blue-600'
  }
  // KDJ相关
  if (tag.includes('KDJ') || tag.includes('超买') || tag.includes('超卖')) {
    return 'bg-purple-100 text-purple-600'
  }
  // RSI相关
  if (tag.includes('RSI')) {
    return 'bg-indigo-100 text-indigo-600'
  }
  // 成交量相关
  if (tag.includes('放量') || tag.includes('地量') || tag.includes('天量') || tag.includes('量')) {
    return 'bg-cyan-100 text-cyan-600'
  }
  // 突破/跌破相关
  if (tag.includes('突破') || tag.includes('跌破')) {
    return 'bg-emerald-100 text-emerald-600'
  }
  // 背弛相关
  if (tag.includes('背弛')) {
    return 'bg-pink-100 text-pink-600'
  }
  // 支撑/压力相关
  if (tag.includes('支撑') || tag.includes('压力')) {
    return 'bg-yellow-100 text-yellow-600'
  }
  // 目标位
  if (tag.includes('目标')) {
    return 'bg-green-100 text-green-600'
  }
  // 默认样式
  return 'bg-gray-100 text-gray-600'
}

const sentimentNews = ref([
  { id: 1, title: '央行宣布降准0.5个百分点，释放长期资金约1万亿元', sentiment: 'positive', relatedStock: '银行板块', source: '新华社', time: '10:30' },
  { id: 2, title: '某新能源龙头企业产品出现质量问题，股价承压', sentiment: 'negative', relatedStock: '宁德时代', source: '财联社', time: '10:15' },
  { id: 3, title: '国务院发布促进消费政策，零售业迎利好', sentiment: 'positive', relatedStock: '消费板块', source: '中国证券报', time: '09:45' },
  { id: 4, title: '海外市场波动加剧，A股短期或受影响', sentiment: 'neutral', relatedStock: '大盘', source: '证券时报', time: '09:20' },
  { id: 5, title: '芯片国产化进程加速，相关企业订单量大增', sentiment: 'positive', relatedStock: '半导体板块', source: '科技日报', time: '08:55' },
  { id: 6, title: '新能源汽车销量持续增长，产业链公司业绩亮眼', sentiment: 'positive', relatedStock: '新能源板块', source: '第一财经', time: '08:30' },
  { id: 7, title: '房地产政策调整，市场预期逐步改善', sentiment: 'positive', relatedStock: '房地产板块', source: '经济观察报', time: '08:15' },
  { id: 8, title: '人工智能概念股集体回调，短期调整压力较大', sentiment: 'negative', relatedStock: 'AI概念', source: '证券日报', time: '08:00' },
  { id: 9, title: '医药行业创新药获批数量创新高，行业景气度提升', sentiment: 'positive', relatedStock: '医药板块', source: '医药经济报', time: '07:45' },
  { id: 10, title: '国际油价大幅波动，能源股走势分化', sentiment: 'neutral', relatedStock: '能源板块', source: '能源网', time: '07:30' },
  { id: 11, title: '5G基础设施建设加速，通信设备公司订单饱满', sentiment: 'positive', relatedStock: '5G概念', source: '通信世界', time: '07:15' },
  { id: 12, title: '消费电子需求疲软，相关公司业绩承压', sentiment: 'negative', relatedStock: '消费电子', source: '电子时报', time: '07:00' },
  { id: 13, title: '光伏行业产能过剩担忧加剧，板块整体回调', sentiment: 'negative', relatedStock: '光伏板块', source: '光伏资讯', time: '06:45' },
  { id: 14, title: '金融科技监管政策落地，行业规范化发展加速', sentiment: 'positive', relatedStock: '金融科技', source: '金融时报', time: '06:30' },
  { id: 15, title: '物流行业数字化转型提速，智慧物流概念受关注', sentiment: 'positive', relatedStock: '物流板块', source: '物流时代', time: '06:15' },
  { id: 16, title: '钢铁行业去产能效果显现，行业盈利改善', sentiment: 'positive', relatedStock: '钢铁板块', source: '钢铁资讯', time: '06:00' },
  { id: 17, title: '教育行业政策调整，在线教育公司转型加速', sentiment: 'neutral', relatedStock: '教育板块', source: '教育观察', time: '05:45' },
  { id: 18, title: '农业现代化进程加快，农业科技公司迎来机遇', sentiment: 'positive', relatedStock: '农业板块', source: '农业日报', time: '05:30' },
  { id: 19, title: '环保政策趋严，环保设备需求持续增长', sentiment: 'positive', relatedStock: '环保板块', source: '环境报', time: '05:15' },
  { id: 20, title: '旅游行业复苏缓慢，相关公司业绩仍待改善', sentiment: 'negative', relatedStock: '旅游板块', source: '旅游时报', time: '05:00' }
])

</script>

<style scoped>
/* 设置基础字体大小为12px，确保所有文本最小为12px */
.dashboard-container {
  font-size: 12px;
  height: auto;
  min-height: calc(100vh - 84px);
  overflow: auto;
  display: flex;
  flex-direction: column;
}

/* main容器 */
.dashboard-container > main {
  flex: 1;
  min-height: 0;
  overflow: visible;
  display: flex;
  flex-direction: column;
}

/* 确保第二行容器 - 左右布局，固定高度 */
.dashboard-container > main > div:last-child {
  height: 660px;
  flex-shrink: 0;
  display: flex;
  flex-direction: row;
}

/* 确保第一行高度固定为520px */
.dashboard-container > main > div:first-child {
  height: 600px;
  flex-shrink: 0;
}

/* 确保两个模块平分剩余空间 */
.dashboard-container > main > div:last-child > section {
  flex: 1;
  min-height: 0;
}

/* 自定义滚动条样式 - 默认隐藏，hover时显示 */
.custom-scrollbar {
  scrollbar-width: none; /* Firefox - 默认隐藏 */
  -ms-overflow-style: none; /* IE and Edge */
  scroll-behavior: smooth;
  max-height: 100%; /* 确保表格容器正确限制高度 */
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
  display: none; /* Chrome, Safari, Opera - 默认隐藏 */
}

/* hover时显示滚动条 */
.custom-scrollbar:hover,
section:hover .custom-scrollbar {
  scrollbar-width: thin; /* Firefox - hover时显示 */
  scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
}

.custom-scrollbar:hover::-webkit-scrollbar,
section:hover .custom-scrollbar::-webkit-scrollbar {
  display: block; /* Chrome, Safari, Opera - hover时显示 */
}

.custom-scrollbar:hover::-webkit-scrollbar-track,
section:hover .custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar:hover::-webkit-scrollbar-thumb,
section:hover .custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}

.custom-scrollbar:hover::-webkit-scrollbar-thumb:hover,
section:hover .custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(156, 163, 175, 0.7);
}

/* Element Plus 表格样式 */
:deep(.trading-signals-table),
:deep(.positions-table) {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.trading-signals-table .el-table__body-wrapper),
:deep(.positions-table .el-table__body-wrapper) {
  flex: 1;
  overflow-y: auto;
}

:deep(.trading-signals-table .el-table__body-wrapper),
:deep(.positions-table .el-table__body-wrapper) {
  scrollbar-width: none; /* Firefox - 默认隐藏 */
  -ms-overflow-style: none; /* IE and Edge */
}

:deep(.trading-signals-table .el-table__body-wrapper::-webkit-scrollbar),
:deep(.positions-table .el-table__body-wrapper::-webkit-scrollbar) {
  display: none; /* Chrome, Safari, Opera - 默认隐藏 */
}

/* hover时显示滚动条 */
section:hover :deep(.trading-signals-table .el-table__body-wrapper),
section:hover :deep(.positions-table .el-table__body-wrapper) {
  scrollbar-width: thin; /* Firefox - hover时显示 */
  scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
}

section:hover :deep(.trading-signals-table .el-table__body-wrapper::-webkit-scrollbar),
section:hover :deep(.positions-table .el-table__body-wrapper::-webkit-scrollbar) {
  display: block; /* Chrome, Safari, Opera - hover时显示 */
  width: 6px;
  height: 6px;
}

section:hover :deep(.trading-signals-table .el-table__body-wrapper::-webkit-scrollbar-track),
section:hover :deep(.positions-table .el-table__body-wrapper::-webkit-scrollbar-track) {
  background: transparent;
}

section:hover :deep(.trading-signals-table .el-table__body-wrapper::-webkit-scrollbar-thumb),
section:hover :deep(.positions-table .el-table__body-wrapper::-webkit-scrollbar-thumb) {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}

section:hover :deep(.trading-signals-table .el-table__body-wrapper::-webkit-scrollbar-thumb:hover),
section:hover :deep(.positions-table .el-table__body-wrapper::-webkit-scrollbar-thumb:hover) {
  background-color: rgba(156, 163, 175, 0.7);
}

/* 表格头部样式 */
:deep(.trading-signals-table .el-table__header),
:deep(.positions-table .el-table__header) {
  background-color: #f9fafb;
}

:deep(.trading-signals-table .el-table__header th),
:deep(.positions-table .el-table__header th) {
  background-color: #f9fafb;
  color: #6b7280;
  font-size: 12px;
  font-weight: 500;
  padding: 12px 16px;
}

:deep(.trading-signals-table .el-table__body td),
:deep(.positions-table .el-table__body td) {
  padding: 12px 16px;
}

:deep(.trading-signals-table .el-table__row),
:deep(.positions-table .el-table__row) {
  transition: background-color 0.2s;
}

/* 重大舆情监控滚动容器样式 - 默认隐藏滚动条 */
.sentiment-scroll-container {
  scroll-behavior: smooth;
  scrollbar-width: none !important; /* Firefox - 默认隐藏 */
  -ms-overflow-style: none !important; /* IE and Edge */
}

.sentiment-scroll-container::-webkit-scrollbar {
  width: 6px;
  display: none !important; /* Chrome, Safari, Opera - 默认隐藏 */
}

/* 只有重大舆情监控模块hover时才显示滚动条 */
.sentiment-section:hover .sentiment-scroll-container {
  scrollbar-width: thin !important; /* Firefox - hover时显示 */
  scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
}

.sentiment-section:hover .sentiment-scroll-container::-webkit-scrollbar {
  display: block !important; /* Chrome, Safari, Opera - hover时显示 */
}

.sentiment-section:hover .sentiment-scroll-container::-webkit-scrollbar-track {
  background: transparent;
}

.sentiment-section:hover .sentiment-scroll-container::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}

.sentiment-section:hover .sentiment-scroll-container::-webkit-scrollbar-thumb:hover {
  background-color: rgba(156, 163, 175, 0.7);
}

/* 左侧边框样式 */
.border-l-3 {
  border-left-width: 3px !important;
  border-left-style: solid !important;
}
</style>



