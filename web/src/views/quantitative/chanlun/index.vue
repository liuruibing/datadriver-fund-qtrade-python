<!--
 * @Description: 
 * @Author: 
 * @Date: 2025-12-05 11:37:26
 * @LastEditors: Please set LastEditors
 * @LastEditTime: 2025-12-19 15:55:36
-->
<template>
  <fs-page ref="fsPageRef" class="chanlun-page">
    <div
      class="chanlun-model-container"
      ref="chanlunModelContainerRef"
    >
      <!-- 筛选条件 -->
      <el-card
        class="filter-card custom-card"
        shadow="never"
      >
        <template #header>
          <div class="card-header">
            <span>缠论选股</span>
            <div class="filter-actions">
              <el-button
                type="text"
                size="small"
                @click="openTour"
                icon="Position"
              >指引</el-button>
              <!-- <el-button
                type="text"
                size="small"
                @click="refreshData"
                :loading="refreshLoading"
                style="color: #67c23a"
              >更新数据</el-button> -->
              <el-button
                type="text"
                size="small"
                @click="resetFilters"
              >重置</el-button>
            </div>
          </div>
        </template>

        <div class="filter-content">
          <!-- 基础筛选 -->
          <div class="filter-section">
            <div class="section-title">
              <div>
                <span>初筛查询条件</span>
                <el-button
                  type="text"
                  size="small"
                  @click="showBaseFilter = !showBaseFilter"
                >
                  {{ showBaseFilter ? '收起筛选' : '展开筛选' }}
                  <el-icon>
                    <ArrowUp v-if="showBaseFilter" />
                    <ArrowDown v-else />
                  </el-icon>
                </el-button>
              </div>
              <div>
                <!-- <span style="font-size: 14px; font-weight: bold;">筛选结果 ({{ tableData.length }})</span> -->
                <el-popover
                  title="筛选结果"
                  placement="bottom-end"
                  width="840"
                  :disabled="showBaseFilter"
                >
                  <template #reference>
                    <span v-if="showBaseFilter">
                      <span style="font-size: 14px; font-weight: bold">筛选结果 ({{ baseTableData.length }})</span>
                    </span>
                    <span v-else>
                      <span style="color: #409eff; font-size: 14px; font-weight: bold">筛选结果 ({{ baseTableData.length }})</span>
                    </span>
                  </template>
                  <vxe-table
                    border="inner"
                    height="400"
                    show-overflow
                    show-header-overflow="title"
                    :tooltip-config="{ enterable: false }"
                    :row-config="{ isHover: true }"
                    :column-config="{ resizable: true }"
                    :virtual-y-config="{ enabled: true, gt: 0 }"
                    :data="baseTableData"
                    v-loading="baseTableLoading"
                    size="mini"
                    :header-cell-style="{ backgroundColor: '#fff' }"
                  >
                    <vxe-column
                      type="seq"
                      width="50"
                    ></vxe-column>
                    <vxe-column
                      field="ts_code"
                      title="股票代码|名称"
                      sortable
                      min-width="120"
                    >
                      <template #default="scope">
                        <span>{{ scope.row.symbol }} | {{ scope.row.name }}</span>
                      </template>
                    </vxe-column>
                    <vxe-column
                      field="industry"
                      title="行业"
                      sortable
                      min-width="180"
                    ></vxe-column>
                    <vxe-column
                      field="market"
                      title="市场"
                      sortable
                      min-width="70"
                    ></vxe-column>
                    <vxe-column
                      field="circ_mv"
                      title="流通市值(亿元)"
                      sortable
                      min-width="110"
                      align="right"
                    >
                      <template #default="scope">
                        <span>{{ moneyFormat2Decimal(scope.row.circ_mv) }}</span>
                      </template>
                    </vxe-column>
                    <vxe-column
                      field="vol_avg5"
                      title="5日平均成交量(亿元)"
                      sortable
                      min-width="145"
                      align="right"
                    >
                      <template #default="scope">
                        <span>{{ moneyFormat2Decimal(scope.row.vol_avg5) }}</span>
                      </template>
                    </vxe-column>
                    <vxe-column
                      field="pe"
                      title="PE"
                      sortable
                      min-width="80"
                      align="right"
                    >
                      <template #default="scope">
                        <span>{{ moneyFormat2Decimal(scope.row.pe) }}</span>
                      </template>
                    </vxe-column>
                  </vxe-table>
                </el-popover>
                <el-button
                  ref="btn1Ref"
                  icon="Search"
                  type="primary"
                  size="small"
                  style="margin-left: 10px"
                  :loading="baseTableLoading"
                  @click="handleInitialScreening(true)"
                >初筛查询</el-button>
              </div>
            </div>
            <div
              v-show="showBaseFilter"
              style="display: flex; justify-content: space-between; padding-top: 10px"
            >
              <div style="width: 820px">
                <el-form
                  ref="filterFormRef"
                  :model="filterForm"
                  :rules="filterFormRules"
                  :inline="true"
                  class="filter-form"
                >
                  <el-form-item
                    label="数据日期"
                    prop="dataDate"
                  >
                    <el-date-picker
                      v-model="filterForm.dataDate"
                      type="date"
                      placeholder="选择数据日期"
                      format="YYYY-MM-DD"
                      value-format="YYYY-MM-DD"
                      style="width: 200px"
                    />
                  </el-form-item>
                  <el-form-item label="股票代码|名称">
                    <el-input
                      v-model="filterForm.stockCode"
                      placeholder="请输入股票代码|名称"
                      clearable
                      style="width: 200px"
                      @input="(value) => (filterForm.stockCode = value.trim())"
                    />
                  </el-form-item>
                  <!-- <el-form-item label="股票名称">
                    <el-input
                      v-model="filterForm.stockName"
                      placeholder="请输入股票名称"
                      clearable
                      style="width: 200px"
                    />
                  </el-form-item> -->
                </el-form>
                <el-form
                  :model="filterForm"
                  :inline="true"
                  class="filter-form"
                >
                  <el-form-item label="流通市值(亿元)">
                    <el-input
                      v-model="filterForm.marketCapMin"
                      placeholder="最小值"
                      clearable
                      style="width: 100px"
                      @input="(value) => handleInputNumber(value, 'marketCapMin')"
                    />
                    <span style="margin: 0 8px">-</span>
                    <el-input
                      v-model="filterForm.marketCapMax"
                      placeholder="最大值"
                      clearable
                      style="width: 100px"
                      @input="(value) => handleInputNumber(value, 'marketCapMax')"
                    />
                  </el-form-item>
                  <el-form-item label="5日平均成交量(亿元)">
                    <el-input
                      v-model="filterForm.volume5DayMin"
                      placeholder="最小值"
                      clearable
                      style="width: 100px"
                      @input="(value) => handleInputNumber(value, 'volume5DayMin')"
                    />
                    <span style="margin: 0 8px">-</span>
                    <el-input
                      v-model="filterForm.volume5DayMax"
                      placeholder="最大值"
                      clearable
                      style="width: 100px"
                      @input="(value) => handleInputNumber(value, 'volume5DayMax')"
                    />
                  </el-form-item>
                </el-form>
                <el-form
                  :model="filterForm"
                  :inline="true"
                  class="filter-form"
                >
                  <el-form-item label="PE">
                    <el-input
                      v-model="filterForm.peMin"
                      placeholder="最小值"
                      clearable
                      style="width: 100px"
                      @input="(value) => handleInputNumber(value, 'peMin')"
                    />
                    <span style="margin: 0 8px">-</span>
                    <el-input
                      v-model="filterForm.peMax"
                      placeholder="最大值"
                      clearable
                      style="width: 100px"
                      @input="(value) => handleInputNumber(value, 'peMax')"
                    />
                  </el-form-item>
                  <el-form-item label="行业">
                    <!-- <el-select
                      v-model="filterForm.industryLevel3"
                      placeholder="请选择行业"
                      clearable
                      multiple
                      collapse-tags
                      collapse-tags-tooltip
                      style="width: 350px"
                      filterable
                    >
                      <el-option
                        v-for="(item, index) in industryList"
                        :key="index"
                        :label="item"
                        :value="item"
                      ></el-option>
                    </el-select> -->
                    <el-cascader
                      v-model="filterForm.industryLevel3"
                      :options="industryOptions"
                      :props="cascaderProps"
                      placeholder="请选择行业"
                      clearable
                      filterable
                      multiple
                      collapse-tags
                      collapse-tags-tooltip
                      style="width: 350px"
                    />
                  </el-form-item>
                </el-form>
                <!-- 筹码特征 -->
                <!-- <div class="subsection-item-box">
                  <div class="subsection-title">筹码特征</div>
                  <div class="tag-group">
                    <el-tag
                      v-for="tag in tagOptions.chip"
                      :key="tag.key"
                      :type="tag.selected ? 'success' : 'info'"
                      class="filter-tag"
                      @click="handleTagClick('chip', tag.key)"
                    >
                      {{ tag.label }}
                    </el-tag>
                  </div>
                </div> -->
              </div>
              <div style="width: calc(100% - 820px)">
                <vxe-table
                  ref="baseTableRef"
                  border="inner"
                  show-overflow
                  show-header-overflow="title"
                  height="200"
                  :row-config="{ isHover: true }"
                  :column-config="{ resizable: true }"
                  :virtual-y-config="{ enabled: true, gt: 0 }"
                  :data="baseTableData"
                  v-loading="baseTableLoading"
                  size="mini"
                  :header-cell-style="{ backgroundColor: '#fff' }"
                >
                  <vxe-column
                    type="seq"
                    width="50"
                  ></vxe-column>
                  <vxe-column
                    field="ts_code"
                    title="股票代码|名称"
                    sortable
                    min-width="120"
                  >
                    <template #default="scope">
                      <span>{{ scope.row.symbol }} | {{ scope.row.name }}</span>
                    </template>
                  </vxe-column>
                  <vxe-column
                    field="industry"
                    title="行业"
                    sortable
                    min-width="180"
                  ></vxe-column>
                  <vxe-column
                    field="market"
                    title="市场"
                    sortable
                    min-width="70"
                  ></vxe-column>
                  <vxe-column
                    field="circ_mv"
                    title="流通市值(亿元)"
                    sortable
                    min-width="110"
                    align="right"
                  >
                    <template #default="scope">
                      <span>{{ moneyFormat2Decimal(scope.row.circ_mv) }}</span>
                    </template>
                  </vxe-column>
                  <vxe-column
                    field="vol_avg5"
                    title="5日平均成交量(亿元)"
                    sortable
                    min-width="145"
                    align="right"
                  >
                    <template #default="scope">
                      <span>{{ moneyFormat2Decimal(scope.row.vol_avg5) }}</span>
                    </template>
                  </vxe-column>
                  <vxe-column
                    field="pe"
                    title="PE"
                    sortable
                    min-width="80"
                    align="right"
                  >
                    <template #default="scope">
                      <span>{{ moneyFormat2Decimal(scope.row.pe) }}</span>
                    </template>
                  </vxe-column>
                </vxe-table>
              </div>
            </div>
            <!-- 已选条件标签 -->
            <div class="selected-conditions">
              <div class="conditions-content">
                <span class="conditions-label">已选条件：</span>
                <div class="conditions-tags">
                  <el-tag
                    v-for="condition in selectedBaseConditions"
                    :key="condition.key"
                    closable
                    @close="removeBaseCondition(condition.key)"
                    class="condition-tag"
                  >
                    {{ condition.label }}
                  </el-tag>
                </div>
              </div>
              <el-button
                type="text"
                @click="clearAllBaseConditions"
                class="clear-all"
              >清空</el-button>
            </div>
          </div>

          <!-- 精筛查询条件 -->
          <div class="filter-section">
            <div class="section-title">
              <div>
                <span>精筛查询条件</span>
                <el-button
                  type="text"
                  size="small"
                  @click="showAdvanced = !showAdvanced"
                >
                  {{ showAdvanced ? '收起筛选' : '展开筛选' }}
                  <el-icon>
                    <ArrowUp v-if="showAdvanced" />
                    <ArrowDown v-else />
                  </el-icon>
                </el-button>
              </div>
              <el-button
                ref="btn2Ref"
                icon="Search"
                type="primary"
                size="small"
                style="margin-left: 10px"
                @click="handleFineScreening(true)"
                :loading="tableLoading"
              >量化筛选</el-button>
            </div>
            <div v-show="showAdvanced">
              <!-- 技术指标 -->
              <div class="subsection-item-box">
                <div class="subsection-title">MACD特征</div>
                <div class="tag-group">
                  <el-tag
                    v-for="tag in tagOptions.macd"
                    :key="tag.key"
                    :type="tag.selected ? 'success' : 'info'"
                    class="filter-tag"
                    @click="handleTagClick('macd', tag.key)"
                  >
                    {{ tag.label }}
                  </el-tag>
                </div>
              </div>

              <!-- 筹码特征 -->
              <div class="subsection-item-box">
                <div class="subsection-title">筹码特征</div>
                <div class="tag-group">
                  <el-tag
                    v-for="tag in tagOptions.chip"
                    :key="tag.key"
                    :type="tag.selected ? 'success' : 'info'"
                    class="filter-tag"
                    @click="handleTagClick('chip', tag.key)"
                  >
                    {{ tag.label }}
                  </el-tag>
                </div>
              </div>

              <!-- 板块特征 -->
              <!-- <div class="subsection-item-box">
              <div class="subsection-title">板块特征</div>
              <div class="tag-group">
                <el-tag
                  v-for="tag in tagOptions.sector"
                  :key="tag.key"
                  :type="tag.selected ? 'success' : 'info'"
                  class="filter-tag"
                  @click="handleTagClick('sector', tag.key)"
                >
                  {{ tag.label }}
                </el-tag>
              </div>
            </div> -->

              <!-- 价格特征 -->
              <div class="subsection-item-box">
                <div class="subsection-title">价格特征</div>
                <div class="tag-group">
                  <el-tag
                    v-for="tag in tagOptions.volumePrice"
                    :key="tag.key"
                    :type="tag.selected ? 'success' : 'info'"
                    class="filter-tag"
                    @click="handleTagClick('volumePrice', tag.key)"
                  >
                    {{ tag.label }}
                  </el-tag>
                </div>
              </div>

              <!-- 成交量特征 -->
              <div class="subsection-item-box">
                <div class="subsection-title">成交量特征</div>
                <div class="tag-group">
                  <el-tag
                    v-for="tag in tagOptions.tradingVolume"
                    :key="tag.key"
                    :type="tag.selected ? 'success' : 'info'"
                    class="filter-tag"
                    @click="handleTagClick('tradingVolume', tag.key)"
                  >
                    {{ tag.label }}
                  </el-tag>
                </div>
              </div>

              <!-- 缠论特征 -->
              <div class="subsection-item-box">
                <div class="subsection-title">缠论特征</div>
                <div class="tag-group">
                  <el-tag
                    v-for="tag in tagOptions.chanlun"
                    :key="tag.key"
                    :type="tag.selected ? 'success' : 'info'"
                    class="filter-tag"
                    @click="handleTagClick('chanlun', tag.key)"
                  >
                    {{ tag.label }}
                  </el-tag>
                </div>
              </div>
            </div>

            <!-- 已选条件标签 -->
            <div class="selected-conditions">
              <div class="conditions-content">
                <span class="conditions-label">已选条件：</span>
                <div class="conditions-tags">
                  <el-tag
                    v-for="condition in selectedConditions"
                    :key="condition.key"
                    closable
                    @close="removeCondition(condition.key)"
                    class="condition-tag"
                  >
                    {{ condition.label }}
                  </el-tag>
                </div>
              </div>
              <el-button
                type="text"
                @click="clearConditions"
                class="clear-all"
              >清空</el-button>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 主要内容区域 -->
      <div class="main-content">
        <el-card
          class="result-table-card custom-card"
          shadow="never"
          ref="elTableCardRef"
        >
          <template #header>
            <div class="card-header">
              <span>筛选结果 ({{ tableData.length }})</span>
              <!-- <div class="table-actions"></div> -->
            </div>
          </template>

          <vxe-table
            ref="elTableRef"
            :data="tableData"
            v-loading="tableLoading"
            style="width: 100%"
            height="400"
            size="mini"
            border="inner"
            show-overflow
            show-header-overflow="title"
            :row-config="{ isHover: true }"
            :column-config="{ resizable: true }"
            :virtual-y-config="{ enabled: true, gt: 0 }"
            :header-cell-style="{ backgroundColor: '#fff' }"
          >
            <!-- 序号 -->
            <vxe-column
              type="seq"
              title="序号"
              width="50"
            />
            <vxe-column
              field="ts_code"
              title="股票代码|名称"
              min-width="130"
              sortable
            >
              <template #default="scope">
                <span>{{ scope.row.symbol }} | {{ scope.row.name }}</span>
              </template>
            </vxe-column>
            <vxe-column
              field="industry"
              title="行业"
              min-width="160"
              sortable
            />
            <vxe-column
              field="data_date"
              title="数据日期"
              min-width="100"
              sortable
            />
            <vxe-column
              field="current_price"
              title="收盘价格(元)"
              min-width="120"
              sortable
            >
              <template #default="scope">
                <span>{{ moneyFormat2Decimal(scope.row.current_price) }}</span>
              </template>
            </vxe-column>
            <vxe-column
              field="chip_concentration_90"
              title="90%筹码集中度(%)"
              min-width="140"
              sortable
            >
              <template #default="scope">
                <span>{{ formatNumber2Decimal(scope.row.chip_concentration_90) }}</span>
              </template>
            </vxe-column>
            <vxe-column
              field="top10_share_ratio"
              title="前十大流通股东占流通盘(%)"
              min-width="180"
              sortable
            >
              <template #default="scope">
                <span>{{ formatNumber2Decimal(scope.row.top10_share_ratio) }}</span>
              </template>
            </vxe-column>
            <vxe-column
              field="macdStr"
              title="MACD"
              min-width="100"
              sortable
            >
              <template #default="scope">
                <el-tag
                  :type="getMacdType(scope.row.macdStr)"
                  size="small"
                >
                  {{ scope.row.macdStr }}
                </el-tag>
              </template>
            </vxe-column>
            <!-- <el-table-column
              prop="sector_info"
              label="板块情况"
              min-width="120"
            /> -->
            <vxe-column
              title="操作"
              width="150"
              fixed="right"
            >
              <template #default="scope">
                <!-- <el-button
                  type="text"
                  size="small"
                  @click.stop="showStockChart(scope.row)"
                >
                  <el-icon>
                    <TrendCharts />
                  </el-icon>
                  图表
                </el-button> -->
                <el-button
                  type="text"
                  size="small"
                  @click.stop="handleClickRow(scope.row)"
                >回测</el-button>
                <el-button
                  type="text"
                  size="small"
                  @click.stop="addToPool(scope.row)"
                >入池</el-button>
              </template>
            </vxe-column>
          </vxe-table>

          <!-- 分页 -->
          <!-- <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div> -->
        </el-card>
      </div>

      <!-- 回测分析区域 -->
      <el-card
        class="backtest-card custom-card"
        shadow="never"
        id="backtest_container"
      >
        <template #header>
          <div class="card-header">
            <span>回测分析</span>
          </div>
        </template>

        <!-- 顶部控制区域 -->
        <el-affix
          target=".chanlun-model-container"
          :offset="85"
        >
          <div class="backtest-controls">
            <div class="date-range">
              <el-form
                ref="backtestFormRef"
                :inline="true"
                :model="backtestForm"
                :rules="backtestFormRules"
              >
                <el-form-item
                  label="日期"
                  prop="date"
                  style="margin-bottom: 0 !important"
                >
                  <el-date-picker
                    v-model="backtestForm.date"
                    type="daterange"
                    range-separator="至"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    value-format="YYYY-MM-DD"
                    format="YYYY-MM-DD"
                  />
                </el-form-item>
                <el-form-item
                  label="股票代码|名称"
                  prop="stockCode"
                  style="margin-bottom: 0 !important"
                >
                  <!-- <el-select
                    v-model="backtestForm.stockCode"
                    filterable
                    remote
                    reserve-keyword
                    placeholder="输入搜索"
                    :remote-method="handleStockCodeSearch"
                    :loading="loading"
                  >
                    <el-option
                      v-for="item in options"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                    />
                  </el-select> -->
                  <el-select-v2
                    v-model="backtestForm.stockCode"
                    :options="tsCodeList"
                    :props="{ label: 'label', value: 'ts_code' }"
                    placeholder="请选择"
                    style="width: 200px"
                    filterable
                  />
                </el-form-item>
              </el-form>
            </div>
            <div class="backtest-actions">
              <el-button
                type="primary"
                @click="runBacktestAnalysis"
                size="small"
              > 回测 </el-button>
            </div>
          </div>
        </el-affix>

        <!-- <div class="backtest-layout">
          <div class="backtest-left">
            <el-table
              :data="buySellSignals"
              v-loading="backtestLoading"
              height="450"
              style="width: 100%"
              size="small"
            >
              <el-table-column
                prop="date"
                label="日期"
                width="120"
              />
              <el-table-column
                prop="macd"
                label="MACD"
                width="100"
              >
                <template #default="scope">
                  {{ scope.row.macd?.toFixed(3) }}
                </template>
              </el-table-column>
              <el-table-column
                prop="signal"
                label="Signal"
                width="100"
              >
                <template #default="scope">
                  {{ scope.row.signal?.toFixed(3) }}
                </template>
              </el-table-column>
              <el-table-column
                prop="action"
                label="买卖点"
                width="120"
              >
                <template #default="scope">
                  <span v-if="!scope.row.action"></span>
                  <el-tag
                    v-else
                    :type="scope.row.action === '买入' ? 'success' : 'danger'"
                    size="small"
                  >
                    {{ scope.row.action }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div
            class="backtest-right"
            v-loading="backtestLoading"
          >
            <div
              class="backtest-chart-container"
              ref="backtestRef"
              style="height: 450px;"
            ></div>
          </div>
        </div> -->

        <div
          class="backtest-chart-section"
          v-loading="backtestLoading"
        >
          <ElChart
            :options="backtestChartOption"
            width="100%"
            height="400px"
          />
        </div>

        <!-- 底部：MACD曲线图 -->
        <div
          class="macd-chart-section"
          v-loading="backtestLoading"
        >
          <ElChart
            :options="macdChartOption"
            width="100%"
            height="400px"
          />
        </div>

        <!-- K线图区域 -->
        <div
          class="kline-chart-section"
          v-loading="kLineLoading"
        >
          <ElChart
            :options="klineChartOption"
            width="100%"
            height="400px"
          />
        </div>
      </el-card>
    </div>

    <!-- 图表模态框 -->
    <el-dialog
      v-model="showChartModal"
      :title="`${currentStock} - K线图`"
      width="80%"
      :before-close="closeChartModal"
    >
      <div
        class="chart-container"
        ref="chartRef"
        style="height: 500px"
      ></div>
    </el-dialog>

    <el-dialog
      v-model="poolManagerDialogVisible"
      :title="`${selectedStock?.symbol} | ${selectedStock?.name}`"
      width="500px"
      :close-on-click-modal="false"
    >
      <div style="display: flex; align-items: center; gap: 10px">
        <span style="width: 90px; text-align: right">选择股票池</span>
        <el-select
          style="flex: 1"
          v-model="selectedPoolId"
          placeholder="请选择股票池"
          filterable
        >
          <el-option
            v-for="item in poolList"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
      </div>
      <template #footer>
        <el-button @click="poolManagerDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleAddToPoolConfirm"
        >确定</el-button>
      </template>
    </el-dialog>

    <el-tour
      v-model="tourShow"
      type="primary"
      :append-to="fsPageRef?.$el"
    >
      <!-- :append-to="chanlunModelContainerRef?.$el" -->
      <el-tour-step
        :target="btn1Ref?.$el"
        title="初筛查询"
        description="初筛，根据初筛查询条件，筛选出符合条件的股票，数据展示在下方表格中"
      />
      <el-tour-step
        :target="baseTableRef?.$el"
        title="初筛结果"
        description="初筛结果"
      />
      <el-tour-step
        :target="btn2Ref?.$el"
        title="量化筛选"
        description="精筛，根据所有筛选条件，量化筛选出符合条件的股票，数据展示在下方表格中"
      />
      <el-tour-step
        :target="elTableRef?.$el"
        title="量化筛选结果"
        description="量化筛选结果"
      />
    </el-tour>
  </fs-page>
</template>

<script setup lang="ts">
import { GetBacktestKline, GetList, GetFineList, GetBacktestMacd, RefreshData, GetBaseInfo } from './api';
import { ref, reactive, computed, onMounted, nextTick, markRaw, watch } from 'vue';
import { ElMessage, ElMessageBox, FormRules } from 'element-plus';
import { Refresh, Download, Search, ArrowUp, ArrowDown, TrendCharts } from '@element-plus/icons-vue';
import * as echarts from 'echarts';
import ElChart from '/@/components/elChart/index.vue';
import _ from 'lodash';
import { dictionary } from '/@/utils/dictionary';

defineOptions({
	name: 'chanlunNew',
});

// 类型定义
interface Condition {
	key: string;
	label: string;
}

interface StockData {
	ts_code: string;
	code: string;
	name: string;
	industry: string;
	data_date: string;
	current_price: string;
	change: number;
	chip_concentration_90: number;
	top10_share_ratio: number;
	macd: string;
	sector_info: string;
}

interface FilterForm {
	dataDate: string;
	stockCode: string;
	stockName: string;
	marketCapMin: string;
	marketCapMax: string;
	volume5DayMin: string;
	volume5DayMax: string;
	peMin: string;
	peMax: string;
	industryLevel3: string[][];
	pattern: string;
	timeframe: string;
	centerLevel: string;
	macdFeature: string;
	rsiMin: number | undefined;
	rsiMax: number | undefined;
	volume: string;
	sector: string;
	industry: string;
}

interface TagOption {
	key: string;
	label: string;
	selected: boolean;
}

type TagCategory = 'macd' | 'chip' | 'sector' | 'industry' | 'volumePrice' | 'tradingVolume' | 'chanlun';

// MACD图表数据项接口
interface MacdDataItem {
	date: string;
	macd: number;
	signal: number;
	hist: number;
}

interface TagOptions {
	macd: TagOption[];
	chip: TagOption[];
	sector: TagOption[];
	industry: TagOption[];
	volumePrice: TagOption[];
	tradingVolume: TagOption[];
	chanlun: TagOption[];
}

interface ChartData {
	dates: string[];
	ohlc: number[][];
	buyPoints: Array<{ date: string; price: number }>;
	sellPoints: Array<{ date: string; price: number }>;
}

interface BuySellSignal {
	date: string;
	macd: number | any;
	signal: number | any;
	action: string;
}

interface KlineData {
	ts_code: string;
	trade_date: string;
	open: number;
	high: number;
	low: number;
	close: number;
	pre_close: number;
	change: number;
	pct_chg: number;
	vol: number;
	amount: number;
}

// 按钮ref
const btn1Ref = ref();
const btn2Ref = ref();

// 响应式数据
const filterFormRef = ref();
const filterForm = reactive<FilterForm>({
	dataDate: '',
	stockCode: '',
	stockName: '',
	marketCapMin: '',
	marketCapMax: '',
	volume5DayMin: '',
	volume5DayMax: '',
	peMin: '',
	peMax: '',
	industryLevel3: [],
	pattern: '',
	timeframe: 'daily',
	centerLevel: '',
	macdFeature: '',
	rsiMin: undefined,
	rsiMax: undefined,
	volume: '',
	sector: '',
	industry: '',
});

const filterFormRules = reactive<FormRules>({
	dataDate: [{ required: true, message: '请选择数据日期', trigger: 'change' }],
});

const showBaseFilter = ref(true);
const showAdvanced = ref(true);
const screeningMode = ref<'initial' | 'fine' | null>('fine');
const updateTime = ref('2024-11-27 15:00:00');
const tourShow = ref(false);
const chanlunModelContainerRef = ref();
const fsPageRef = ref();
// 图表相关状态
const showChartModal = ref(false);
const chartRef = ref();
const chartInstance = ref();
const currentStock = ref('');
const chartData = ref<ChartData>({
	dates: [],
	ohlc: [],
	buyPoints: [],
	sellPoints: [],
});

// 回测图表
const backtestChartOption = ref({});
const macdChartOption = ref({});
const klineChartOption = ref({});
const buySellSignals = ref<BuySellSignal[]>([]);

// 回测表单数据
const backtestForm = reactive({
	date: [],
	stockCode: '',
});

// 校验日期逻辑 开始日期不能大于结束日期
const backtestFormRules = reactive<FormRules>({
	date: [{ required: true, message: '请选择日期', trigger: 'change' }],
	stockCode: [{ required: true, message: '请选择股票代码', trigger: 'change' }],
});

const industryList = ref<string[]>([]);
const tsCodeList = ref<any[]>([]); // 股票代码列表

// 行业选项数据（证监会行业分类3级级联）
const industryOptions = ref<any[]>([]);

// 级联选择器配置
const cascaderProps = {
	expandTrigger: 'hover' as const,
	value: 'label',
	label: 'label',
	children: 'children',
	multiple: true,
};

// 标签选项数据
const tagOptions = reactive<TagOptions>({
	macd: [
		{ key: 'breakthrough', label: '突破过0轴以上反复纠缠', selected: false },
		{ key: 'golden_cross', label: 'MACD金叉', selected: false },
	],
	chip: [
		{ key: 'chip_concentration', label: '90%筹码集中度小于15%', selected: false },
		{ key: 'shareholder_ratio', label: '前十大流通股东上期公告持仓占流通盘>65%', selected: false },
	],
	sector: [
		{ key: 'tech', label: '科技板块', selected: false },
		{ key: 'finance', label: '金融板块', selected: false },
		{ key: 'medical', label: '医药板块', selected: false },
		{ key: 'consumer', label: '消费板块', selected: false },
	],
	industry: [
		{ key: 'software', label: '软件服务', selected: false },
		{ key: 'bank', label: '银行', selected: false },
		{ key: 'pharma', label: '医药制造', selected: false },
		{ key: 'liquor', label: '白酒', selected: false },
	],
	volumePrice: [
		{ key: 'price_above_ma60', label: '收盘价高于60日均线', selected: false },
		{ key: 'long_yang_24days', label: '24天内有9%以上的长阳', selected: false },
		{ key: 'relative_main_cost', label: '相对主力成本涨幅小于50%', selected: false },
		{ key: 'high_volume_not_bearish', label: '24日最高成交量日的K线不是阴线', selected: false },
	],
	// 成交量特征
	tradingVolume: [
		{ key: 'di_liang', label: '地量', selected: false },
		{ key: 'fang_liang', label: '放量', selected: false },
		{ key: 'tian_liang', label: '天量', selected: false },
	],
	// 缠论特征
	chanlun: [
		{ key: 'bottom_divergence', label: '日线底背弛', selected: false },
		{ key: 'top_divergence', label: '日线顶背弛', selected: false },
		{ key: 'first_buy_point', label: '出现第一类买点', selected: false },
		{ key: 'second_buy_point', label: '出现第二类买点', selected: false },
		{ key: 'constitute_center', label: '构筑中枢', selected: false },
		{ key: 'leave_center', label: '向上离开中枢', selected: false },
	],
});

// 已选条件
const selectedBaseConditions = ref<Condition[]>([]);
const selectedConditions = ref<Condition[]>([]);

// 监听 filterForm 变化，更新基础条件
watch(
	() => filterForm,
	() => {
		updateSelectedBaseConditions();
	},
	{ deep: true }
);

// 监听 tourShow 变化，控制页面滚动
watch(
	() => tourShow.value,
	(newVal) => {
    const chanlunPage = document.querySelector('.chanlun-page>.fs-page-content');
		if (newVal) {
      if (chanlunPage) {
        (chanlunPage as HTMLElement).style.overflow = 'hidden';
      }
		} else {
			(chanlunPage as HTMLElement).style.overflow = '';
		}
	}
);

// 更新已选基础条件
const updateSelectedBaseConditions = () => {
	const conditions: Condition[] = [];

	// 数据日期
	if (filterForm.dataDate) {
		conditions.push({
			key: 'dataDate',
			label: `数据日期：${filterForm.dataDate}`,
		});
	}

	// 股票代码
	if (filterForm.stockCode) {
		conditions.push({
			key: 'stockCode',
			label: `股票代码|名称：${filterForm.stockCode}`,
		});
	}

	// 股票名称
	if (filterForm.stockName) {
		conditions.push({
			key: 'stockName',
			label: `股票名称：${filterForm.stockName}`,
		});
	}

	// 流通市值(亿元)
	if (filterForm.marketCapMin || filterForm.marketCapMax) {
		const min = filterForm.marketCapMin;
		const max = filterForm.marketCapMax;
		let label = '流通市值(亿元)：';
		if (min && max) {
			label += `${min} ~ ${max}`;
		} else if (min) {
			label += `最小值 ${min}`;
		} else if (max) {
			label += `最大值 ${max}`;
		}
		conditions.push({
			key: 'marketCap',
			label: label,
		});
	}

	// 5日平均成交量(亿元)
	if (filterForm.volume5DayMin || filterForm.volume5DayMax) {
		const min = filterForm.volume5DayMin;
		const max = filterForm.volume5DayMax;
		let label = '5日平均成交量(亿元)：';
		if (min && max) {
			label += `${min} ~ ${max}`;
		} else if (min) {
			label += `最小值 ${min}`;
		} else if (max) {
			label += `最大值 ${max}`;
		}
		conditions.push({
			key: 'volume5Day',
			label: label,
		});
	}

	// PE
	if (filterForm.peMin || filterForm.peMax) {
		const min = filterForm.peMin;
		const max = filterForm.peMax;
		let label = 'PE：';
		if (min && max) {
			label += `${min} ~ ${max}`;
		} else if (min) {
			label += `最小值 ${min}`;
		} else if (max) {
			label += `最大值 ${max}`;
		}
		conditions.push({
			key: 'pe',
			label: label,
		});
	}

	// 行业
	if (filterForm.industryLevel3 && filterForm.industryLevel3.length > 0) {
		conditions.push({
			key: 'industry',
			label: `行业：已选择 ${filterForm.industryLevel3.length} 项`,
		});
	}

	// 筹码特征标签
	// tagOptions.chip.forEach((tag: TagOption) => {
	//   if (tag.selected) {
	//     conditions.push({ key: `chip_${tag.key}`, label: tag.label })
	//   }
	// })

	selectedBaseConditions.value = conditions;
};

const baseTableRef = ref();
const baseTableData = ref<StockData[]>([]);
const baseTableLoading = ref(false);
const baseTotal = ref(0);

const tableLoading = ref(false);
// 表格数据
const tableData = ref<StockData[]>([]);
const elTableRef = ref();
const elTableCardRef = ref();
// 分页数据
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

// 计算属性
// 保留2位小数
const formatNumber2Decimal = (value: number) => {
	if (value === 0) {
		return '0.00';
	} else if (value === null || value === undefined) {
		return '';
	} else {
		return value.toFixed(2);
	}
};

// 金额千分位+保留2位小数
const moneyFormat2Decimal = (value: number) => {
	if (value === 0) {
		return '0.00';
	} else if (value === null || value === undefined) {
		return '';
	} else {
		// 保留2位小数并添加千分位逗号
		const formatted = value.toFixed(2);
		const [integerPart, decimalPart] = formatted.split('.');
		const formattedInteger = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
		return `${formattedInteger}.${decimalPart}`;
	}
};

// 金额千分位+保留4位小数
const moneyFormat4Decimal = (value: number) => {
	if (value === 0) {
		return '0.0000';
	} else if (value === null || value === undefined) {
		return '';
	} else {
		// 保留2位小数并添加千分位逗号
		const formatted = value.toFixed(4);
		const [integerPart, decimalPart] = formatted.split('.');
		const formattedInteger = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
		return `${formattedInteger}.${decimalPart}`;
	}
};

// 只能输入数字，只能输入一个.
const handleInputNumber = (value: string, key: 'marketCapMin' | 'marketCapMax' | 'volume5DayMin' | 'volume5DayMax' | 'peMin' | 'peMax') => {
	let newVal = value.replace(/[^0-9.]/g, '');
	// 确保只能输入一个小数点
	const parts = newVal.split('.');
	if (parts.length > 2) {
		newVal = parts[0] + '.' + parts.slice(1).join('');
	}
	filterForm[key] = newVal;
};

const openTour = () => {
	tourShow.value = true;
	// 打开筛选区域
	showBaseFilter.value = true;
	showAdvanced.value = true;
};

// 校验流通市值、5日平均成交量、PE
// 校验是否为数字、校验最小值最大值逻辑
const customValidate = async () => {
	// 校验流通市值
	if (filterForm.marketCapMin && filterForm.marketCapMin.trim() !== '') {
		const minVal = Number(filterForm.marketCapMin);
		if (isNaN(minVal)) {
			ElMessage.warning('流通市值最小值必须为有效数字');
			return false;
		}
	}
	if (filterForm.marketCapMax && filterForm.marketCapMax.trim() !== '') {
		const maxVal = Number(filterForm.marketCapMax);
		if (isNaN(maxVal)) {
			ElMessage.warning('流通市值最大值必须为有效数字');
			return false;
		}
	}
	if (filterForm.marketCapMin && filterForm.marketCapMin.trim() !== '' && filterForm.marketCapMax && filterForm.marketCapMax.trim() !== '') {
		const minVal = Number(filterForm.marketCapMin);
		const maxVal = Number(filterForm.marketCapMax);
		if (minVal > maxVal) {
			ElMessage.warning('流通市值最小值不能大于最大值');
			return false;
		}
	}

	// 校验5日平均成交量
	if (filterForm.volume5DayMin && filterForm.volume5DayMin.trim() !== '') {
		const minVal = Number(filterForm.volume5DayMin);
		if (isNaN(minVal)) {
			ElMessage.warning('5日平均成交量最小值必须为有效数字');
			return false;
		}
	}
	if (filterForm.volume5DayMax && filterForm.volume5DayMax.trim() !== '') {
		const maxVal = Number(filterForm.volume5DayMax);
		if (isNaN(maxVal)) {
			ElMessage.warning('5日平均成交量最大值必须为有效数字');
			return false;
		}
	}
	if (filterForm.volume5DayMin && filterForm.volume5DayMin.trim() !== '' && filterForm.volume5DayMax && filterForm.volume5DayMax.trim() !== '') {
		const minVal = Number(filterForm.volume5DayMin);
		const maxVal = Number(filterForm.volume5DayMax);
		if (minVal > maxVal) {
			ElMessage.warning('5日平均成交量最小值不能大于最大值');
			return false;
		}
	}

	// 校验PE
	if (filterForm.peMin && filterForm.peMin.trim() !== '') {
		const minVal = Number(filterForm.peMin);
		if (isNaN(minVal)) {
			ElMessage.warning('PE最小值必须为有效数字');
			return false;
		}
	}
	if (filterForm.peMax && filterForm.peMax.trim() !== '') {
		const maxVal = Number(filterForm.peMax);
		if (isNaN(maxVal)) {
			ElMessage.warning('PE最大值必须为有效数字');
			return false;
		}
	}
	if (filterForm.peMin && filterForm.peMin.trim() !== '' && filterForm.peMax && filterForm.peMax.trim() !== '') {
		const minVal = Number(filterForm.peMin);
		const maxVal = Number(filterForm.peMax);
		if (minVal > maxVal) {
			ElMessage.warning('PE最小值不能大于最大值');
			return false;
		}
	}

	return true;
};

// 初筛查询
const handleInitialScreening = async (flag: boolean) => {
	// 表单校验
	if (!filterFormRef.value) return;
	const valid = await filterFormRef.value.validate().catch(() => false);
	if (!valid) return;
	// 校验流通市值、5日平均成交量、PE
	// 校验是否为数字、校验最小值最大值逻辑
	ElMessage.closeAll();
	const valid2 = await customValidate();
	if (!valid2) return;
	if (flag) {
		currentPage.value = 1;
	}
	try {
		let industry: string[] = [];
		filterForm.industryLevel3.forEach((item) => {
			industry.push(item[item.length - 1]);
		});
		let params = {
			date: filterForm.dataDate,
			search: filterForm.stockCode,
			industry: industry.join(','), // 行业
			pe_min: filterForm.peMin && Number(filterForm.peMin), // PE最小值
			pe_max: filterForm.peMax && Number(filterForm.peMax), // PE最大值
			vol_min: filterForm.volume5DayMin && Number(filterForm.volume5DayMin), // 5日平均成交量最小值
			vol_max: filterForm.volume5DayMax && Number(filterForm.volume5DayMax), // 5日平均成交量最大值
			circ_mv_min: filterForm.marketCapMin && Number(filterForm.marketCapMin), // 流通市值最小值
			circ_mv_max: filterForm.marketCapMax && Number(filterForm.marketCapMax), // 流通市值最大值
		};
		// const mapping = {
		//   chip1: 'chip_chip_concentration', // 90%筹码集中度小于15%
		//   chip2: 'chip_shareholder_ratio', // 前十大流通股东上期公告持仓占流通盘>65%
		// }
		// for (const key in mapping) {
		//   if (selectedBaseConditions.value.some(item => item.key === mapping[key as keyof typeof mapping])) {
		//     (params as any)[key as keyof typeof params] = '1'
		//   }
		// }
		// 剔除空值
		Object.keys(params).forEach((key) => {
			if (params[key as keyof typeof params] === '') {
				delete params[key as keyof typeof params];
			}
		});
		baseTableLoading.value = true;
		const res = await GetList(params);
		const { code, data, total: totalCount, msg } = res;
		if (code === 2000 && data) {
			baseTableData.value = data || [];
			baseTotal.value = totalCount || 0;
		} else {
			baseTableData.value = [];
			baseTotal.value = 0;
			ElMessage.error(msg);
		}
		baseTableLoading.value = false;
	} catch (error) {
		console.error('获取数据失败:', error);
		baseTableData.value = [];
		baseTotal.value = 0;
		baseTableLoading.value = false;
	}
};

// 点精筛前先调用初筛接口，获取初筛结果数量
const getBaseSize = async () => {
	try {
		let industry: string[] = [];
		filterForm.industryLevel3.forEach((item) => {
			industry.push(item[item.length - 1]);
		});
		let params = {
			date: filterForm.dataDate,
			search: filterForm.stockCode,
			industry: industry.join(','), // 行业
			pe_min: filterForm.peMin && Number(filterForm.peMin), // PE最小值
			pe_max: filterForm.peMax && Number(filterForm.peMax), // PE最大值
			vol_min: filterForm.volume5DayMin && Number(filterForm.volume5DayMin), // 5日平均成交量最小值
			vol_max: filterForm.volume5DayMax && Number(filterForm.volume5DayMax), // 5日平均成交量最大值
			circ_mv_min: filterForm.marketCapMin && Number(filterForm.marketCapMin), // 流通市值最小值
			circ_mv_max: filterForm.marketCapMax && Number(filterForm.marketCapMax), // 流通市值最大值
		};
		// 剔除空值
		Object.keys(params).forEach((key) => {
			if (params[key as keyof typeof params] === '') {
				delete params[key as keyof typeof params];
			}
		});
		const res = await GetList(params);
		const { code, data, total: totalCount, msg } = res;
		if (code === 2000 && data) {
			return data.length;
		}
		return 0;
	} catch (error) {
		return 0;
	}
};

// 精筛查询
const handleFineScreening = async (flag: boolean) => {
	// 表单校验
	if (!filterFormRef.value) return;
	const valid = await filterFormRef.value.validate().catch(() => false);
	if (!valid) return;
	// 校验流通市值、5日平均成交量、PE
	// 校验是否为数字、校验最小值最大值逻辑
	ElMessage.closeAll();
	const valid2 = await customValidate();
	if (!valid2) return;
	tableLoading.value = true;
	// 获取初筛结果数量
	const baseSize = await getBaseSize();
	// 获取精筛最大值限制字典配置
	const fineMaxNumData = dictionary('fine_max_num');
	let maxSize = 100;
	if (fineMaxNumData && fineMaxNumData.length) {
		maxSize = Number(fineMaxNumData[0].value) || 100;
	}
	if (baseSize > maxSize) {
		ElMessage.warning(`筛选结果数量超过${maxSize}条，请先初筛，把数量缩小到${maxSize}条以内，再进行精筛`);
		tableLoading.value = false;
		return;
	}
	if (flag) {
		currentPage.value = 1;
		// 关闭筛选区域
		// showBaseFilter.value = false
		// showAdvanced.value = false
	}
	try {
		let industry: string[] = [];
		filterForm.industryLevel3.forEach((item) => {
			industry.push(item[item.length - 1]);
		});
		let params = {
			// page: currentPage.value,
			// limit: pageSize.value,
			// sector: "", // 板块，预留，目前没用到
			date: filterForm.dataDate,
			search: filterForm.stockCode,
			industry: industry.join(','), // 行业
			circ_mv_min: filterForm.marketCapMin && Number(filterForm.marketCapMin), // 流通市值最小值
			circ_mv_max: filterForm.marketCapMax && Number(filterForm.marketCapMax), // 流通市值最大值
			vol_min: filterForm.volume5DayMin && Number(filterForm.volume5DayMin), // 5日平均成交量最小值
			vol_max: filterForm.volume5DayMax && Number(filterForm.volume5DayMax), // 5日平均成交量最大值
			pe_min: filterForm.peMin && Number(filterForm.peMin), // PE最小值
			pe_max: filterForm.peMax && Number(filterForm.peMax), // PE最大值
		};
		const mapping = {
			macd1: 'macd_breakthrough', // 突破过0轴以上反复纠缠
			macd2: 'macd_golden_cross', // MACD金叉
			chip1: 'chip_chip_concentration', // 90%筹码集中度小于15%
			chip2: 'chip_shareholder_ratio', // 前十大流通股东上期公告持仓占流通盘>65%
			price_above_ma60: 'volumePrice_price_above_ma60', // 收盘价高于60日均线
			long_yang_24days: 'volumePrice_long_yang_24days', // 24天内有9%以上的长阳
			relative_main_cost: 'volumePrice_relative_main_cost', // 相对主力成本涨幅小于50%
			high_volume_not_bearish: 'volumePrice_high_volume_not_bearish', // 24日最高成交量日的K线不是阴线
			di_liang: 'tradingVolume_di_liang', // 地量
			fang_liang: 'tradingVolume_fang_liang', // 放量
			tian_liang: 'tradingVolume_tian_liang', // 天量
			bottom_divergence: 'chanlun_bottom_divergence', // 日线底背弛
			top_divergence: 'chanlun_top_divergence', // 日线顶背弛
			first_buy_point: 'chanlun_first_buy_point', // 第一个买点
			second_buy_point: 'chanlun_second_buy_point', // 第二个买点
			constitute_center: 'chanlun_constitute_center', // 构筑中枢
			leave_center: 'chanlun_leave_center', // 向上离开中枢
		};
		for (const key in mapping) {
			if (selectedConditions.value.some((item) => item.key === mapping[key as keyof typeof mapping])) {
				(params as any)[key as keyof typeof params] = '1';
			}
		}
		// const mapping2 = {
		//   chip1: 'chip_chip_concentration', // 90%筹码集中度小于15%
		//   chip2: 'chip_shareholder_ratio', // 前十大流通股东上期公告持仓占流通盘>65%
		// }
		// for (const key in mapping2) {
		//   if (selectedBaseConditions.value.some(item => item.key === mapping2[key as keyof typeof mapping2])) {
		//     (params as any)[key as keyof typeof params] = '1'
		//   }
		// }
		// 剔除空值
		Object.keys(params).forEach((key) => {
			if (params[key as keyof typeof params] === '') {
				delete params[key as keyof typeof params];
			}
		});
		tableLoading.value = true;
		const res = await GetFineList(params);
		const { code, data, total: totalCount, msg } = res;
		if (code === 2000 && data) {
			const list = data || [];
			list.forEach((item: any) => {
				item.macdStr = item.macd ? '金叉' : '死叉';
			});
			tableData.value = list || [];
			total.value = totalCount || 0;
			// if (data.length > 0) {
			//   elTableRef.value!.setCurrentRow(data[0])
			// }
		} else {
			tableData.value = [];
			total.value = 0;
			ElMessage.error(msg);
		}
		tableLoading.value = false;
	} catch (error) {
		console.error('获取数据失败:', error);
		tableData.value = [];
		total.value = 0;
		tableLoading.value = false;
	}
};

const exportResults = () => {
	ElMessage.info('导出功能开发中...');
};

const resetFilters = () => {
	// 使用 Object.assign 进行类型安全的重置
	Object.assign(filterForm, {
		dataDate: '',
		stockCode: '',
		stockName: '',
		marketCapMin: '',
		marketCapMax: '',
		volume5DayMin: '',
		volume5DayMax: '',
		peMin: '',
		peMax: '',
		industryLevel3: [],
		pattern: '',
		centerLevel: '',
		macdFeature: '',
		rsiMin: undefined,
		rsiMax: undefined,
		volume: '',
		sector: '',
		industry: '',
		timeframe: 'daily',
	});

	// 重置所有标签选择状态
	(Object.keys(tagOptions) as TagCategory[]).forEach((category) => {
		tagOptions[category].forEach((tag: TagOption) => {
			tag.selected = false;
		});
	});

	selectedConditions.value = [];
};

const refreshLoading = ref(false);
const refreshData = async () => {
	refreshLoading.value = true;
	await RefreshData();
	ElMessage.success('数据更新成功');
	// resetFilters()
	// handleInitialScreening(true)
	refreshLoading.value = false;
};

const toggleAdvanced = () => {
	showAdvanced.value = !showAdvanced.value;
};

// 标签点击处理
const handleTagClick = (category: TagCategory, tagKey: string) => {
	const tag = tagOptions[category].find((item: TagOption) => item.key === tagKey);
	if (tag) {
		tag.selected = !tag.selected;
		updateSelectedConditions();
		// if (category === 'chip') {
		//   updateSelectedBaseConditions()
		// } else {
		//   updateSelectedConditions()
		// }
	}
};

// 更新已选条件
const updateSelectedConditions = () => {
	const conditions: Condition[] = [];

	// 遍历所有类别，收集选中的标签（排除筹码特征）
	(Object.keys(tagOptions) as TagCategory[]).forEach((category) => {
		// if (category !== 'chip') {  // 排除筹码特征
		tagOptions[category].forEach((tag: TagOption) => {
			if (tag.selected) {
				conditions.push({ key: `${category}_${tag.key}`, label: tag.label });
			}
		});
		// }
	});

	selectedConditions.value = conditions;
};

const handleSearch = () => {
	// 更新已选条件
	const conditions = [];
	if (filterForm.macdFeature) {
		const featureMap: Record<string, string> = {
			golden_cross: 'MACD金叉',
			death_cross: 'MACD死叉',
			breakthrough: '突破过0轴以上反复纠缠',
			bullish_divergence: '底背离',
			bearish_divergence: '顶背离',
		};
		conditions.push({ key: 'macd', label: featureMap[filterForm.macdFeature] });
	}
	if (filterForm.stockCode) {
		conditions.push({ key: 'code', label: `股票代码:${filterForm.stockCode}` });
	}
	selectedConditions.value = conditions;

	ElMessage.success('搜索完成');
	// 这里应该调用API获取数据
};

const handleSizeChange = (size: number) => {
	pageSize.value = size;
	currentPage.value = 1;
};

const handleCurrentChange = (page: number) => {
	currentPage.value = page;
};

const poolManagerDialogVisible = ref(false);
const selectedPoolId = ref(null);
const selectedStock = ref<any>(null);
const poolList = ref<any[]>([]);
const addToPool = (row: any) => {
	// 打开弹窗，选择股票池
	poolManagerDialogVisible.value = true;
	selectedStock.value = row;
	fetchPoolList();
};

const fetchPoolList = () => {
	poolList.value = [
		{ name: '基础池', id: '0' },
		{ name: '股票池1', id: '1' },
		{ name: '股票池2', id: '2' },
	];
	selectedPoolId.value = poolList.value[0].id;
};

const handleAddToPoolConfirm = (poolId: number) => {
	poolManagerDialogVisible.value = false;
	ElMessage.success('操作成功');
};

// 显示股票图表
const showStockChart = (row: any) => {
	currentStock.value = `${row.name}(${row.code})`;
	showChartModal.value = true;

	// 生成模拟数据
	generateMockChartData();

	// 延迟初始化图表，等待DOM渲染完成
	nextTick(() => {
		initChart();
	});
};

// 生成模拟图表数据
const generateMockChartData = () => {
	const dates = [];
	const ohlc = [];
	const buyPoints = [];
	const sellPoints = [];

	// 生成30天的模拟数据
	const basePrice = 100;
	for (let i = 0; i < 30; i++) {
		const date = new Date();
		date.setDate(date.getDate() - (30 - i));
		dates.push(date.toISOString().split('T')[0]);

		const open = basePrice + Math.random() * 10 - 5;
		const close = open + Math.random() * 8 - 4;
		const high = Math.max(open, close) + Math.random() * 5;
		const low = Math.min(open, close) - Math.random() * 5;

		ohlc.push([open, close, low, high]);

		// 随机生成买卖点
		if (i > 5 && Math.random() > 0.8) {
			buyPoints.push({
				date: dates[i],
				price: low,
			});
		}
		if (i > 10 && Math.random() > 0.8) {
			sellPoints.push({
				date: dates[i],
				price: high,
			});
		}
	}

	chartData.value = { dates, ohlc, buyPoints, sellPoints };
};

// 初始化图表
const initChart = () => {
	if (chartInstance.value) {
		chartInstance.value.dispose();
	}

	chartInstance.value = markRaw(echarts.init(chartRef.value));

	const buyData = chartData.value.buyPoints.map((point) => {
		const index = chartData.value.dates.indexOf(point.date);
		return [index, point.price];
	});

	const sellData = chartData.value.sellPoints.map((point) => {
		const index = chartData.value.dates.indexOf(point.date);
		return [index, point.price];
	});

	const option = {
		title: {
			text: `${currentStock.value} - 缠论买卖点`,
			left: 'center',
		},
		tooltip: {
			trigger: 'axis',
			axisPointer: {
				type: 'cross',
			},
		},
		legend: {
			data: ['K线', '买入点', '卖出点'],
			top: 30,
		},
		grid: {
			left: '8%',
			right: '6%',
			bottom: '20%',
		},
		toolbox: {
			feature: {
				dataZoom: {
					yAxisIndex: 'none',
				},
				restore: {},
				saveAsImage: {},
			},
			right: 20,
			top: 30,
		},
		dataZoom: [
			{
				type: 'inside',
				start: 50,
				end: 100,
			},
			{
				show: true,
				type: 'slider',
				top: '90%',
				start: 50,
				end: 100,
			},
		],
		xAxis: {
			type: 'category',
			data: chartData.value.dates,
			scale: true,
			axisLabel: {
				rotate: 45,
			},
		},
		yAxis: {
			type: 'value',
			scale: true,
		},
		series: [
			{
				name: 'K线',
				type: 'candlestick',
				data: chartData.value.ohlc,
				itemStyle: {
					color: '#ec0000',
					color0: '#00da3c',
					borderColor: '#8A0000',
					borderColor0: '#008F28',
				},
			},
			{
				name: '买入点',
				type: 'scatter',
				data: buyData,
				symbol: 'triangle',
				symbolSize: 15,
				itemStyle: {
					color: '#00da3c',
				},
			},
			{
				name: '卖出点',
				type: 'scatter',
				data: sellData,
				symbol: 'triangle',
				symbolRotate: 180,
				symbolSize: 15,
				itemStyle: {
					color: '#ec0000',
				},
			},
		],
	};

	chartInstance.value.setOption(option);
};

// 关闭图表模态框
const closeChartModal = () => {
	if (chartInstance.value) {
		chartInstance.value.dispose();
		chartInstance.value = null;
	}
	showChartModal.value = false;
};

const handleClickRow = (row: StockData) => {
	// 页面滚动到回测部分id=backtest_container
	const backtestContainer = document.getElementById('backtest_container');
	if (backtestContainer) {
		backtestContainer.scrollIntoView({ behavior: 'smooth' });
	}
	let tsCodeObj = tsCodeList.value.find((item) => item.ts_code == row.ts_code);
	if (tsCodeObj) {
		options.value = [{ value: tsCodeObj.ts_code, label: tsCodeObj.label }];
	}
	backtestForm.stockCode = row.ts_code;
	runBacktestAnalysis();
};

const handleStockCodeChange = (value: string) => {
	nextTick(() => {
		elTableRef.value!.setCurrentRow(tableData.value.find((item: StockData) => item.ts_code === value));
	});
};

const backtestFormRef = ref();
// 运行回测分析
const runBacktestAnalysis = async () => {
	// 校验
	const valid = await backtestFormRef.value.validate().catch(() => false);
	if (!valid) {
		return;
	}
	// 延迟初始化回测图表，等待DOM渲染完成
	nextTick(() => {
		// 获取MACD数据
		getBacktestMacdData();
		// 获取K线数据
		getBacktestKlineData();
	});
};
const kLineLoading = ref(false);
// 获取K线数据
const getBacktestKlineData = async () => {
	kLineLoading.value = true;
	try {
		const params = {
			ts_code: backtestForm.stockCode,
			start_date: backtestForm.date[0],
			end_date: backtestForm.date[1],
		};
		const res = await GetBacktestKline(params);
		const { code, data, msg } = res;
		if (code === 2000 && data) {
			// 组装K线图数据
			initKlineChart(data as KlineData[]);
		} else {
			initKlineChart([]);
			ElMessage.error(msg);
		}
		kLineLoading.value = false;
	} catch (error) {
		console.error('获取K线数据失败:', error);
		kLineLoading.value = false;
		initKlineChart([]);
	}
};

const initKlineChart = (data: KlineData[]) => {
	// K线颜色配置
	const upColor = '#ec0000';
	const downColor = '#00da3c';

	// 处理数据：转换为ECharts所需的格式
	const categoryData: string[] = [];
	const values: number[][] = [];
	const volumes: number[][] = [];

	// 对数据按交易日期排序
	const sortedData = data.sort((a, b) => new Date(a.trade_date).getTime() - new Date(b.trade_date).getTime());

	for (let i = 0; i < sortedData.length; i++) {
		const item = sortedData[i];
		categoryData.push(item.trade_date);
		// ECharts K线数据格式：[open, close, low, high]
		values.push([item.open, item.close, item.low, item.high]);
		// 成交量数据：[index, volume, direction]，direction: 1表示阳线，-1表示阴线
		volumes.push([i, item.vol, item.close > item.open ? 1 : -1]);
	}

	// 计算移动平均线
	function calculateMA(dayCount: number, data: number[][]) {
		const result: (string | number)[] = [];
		for (let i = 0; i < data.length; i++) {
			if (i < dayCount - 1) {
				result.push('-');
				continue;
			}
			let sum = 0;
			for (let j = 0; j < dayCount; j++) {
				// 使用收盘价计算MA
				sum += data[i - j][1];
			}
			result.push(+(sum / dayCount).toFixed(3));
		}
		return result;
	}

	const option = {
		animation: false,
		title: {
			text: 'K线图',
			left: 'center',
			top: 10,
		},
		legend: {
			top: 30,
			left: 'center',
			data: ['股价', 'MA5', 'MA10', 'MA20', 'MA30'],
		},
		tooltip: {
			trigger: 'axis',
			axisPointer: {
				type: 'cross',
			},
			borderWidth: 1,
			borderColor: '#ccc',
			padding: 10,
			textStyle: {
				color: '#000',
			},
			position: function (pos: number[], params: any, el: any, elRect: any, size: any) {
				const obj: { top: number; left?: number; right?: number } = {
					top: 10,
				};
				// 使用类型断言来解决这个问题，保持官方示例的逻辑
				(obj as any)[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30;
				return obj;
			},
			formatter: function (params: any) {
				if (!params || !params[0] || params[0].dataIndex === undefined) {
					return '';
				}
				const dataIndex = params[0].dataIndex;
				const klineData = sortedData[dataIndex];
				if (!klineData) {
					return '';
				}
				let html = `<div style="font-size:12px;">
          <div>日期: ${klineData.trade_date}</div>
          <div>开盘: ${klineData.open}</div>
          <div>最高: ${klineData.high}</div>
          <div>最低: ${klineData.low}</div>
          <div>收盘: ${klineData.close}</div>
          <div>涨跌幅: ${klineData.pct_chg}%</div>
          <div>成交量: ${klineData.vol}手</div>
          <div>成交额: ${klineData.amount}千元</div>
        </div>`;
				return html;
			},
		},
		visualMap: {
			show: false,
			seriesIndex: 5,
			dimension: 2,
			pieces: [
				{
					value: 1,
					color: downColor,
				},
				{
					value: -1,
					color: upColor,
				},
			],
		},
		grid: [
			{
				left: '8%',
				right: '6%',
				height: '50%',
			},
			{
				left: '8%',
				right: '6%',
				top: '63%',
				height: '16%',
			},
		],
		xAxis: [
			{
				type: 'category',
				data: categoryData,
				boundaryGap: false,
				axisLine: { onZero: false },
				splitLine: { show: false },
				min: 'dataMin',
				max: 'dataMax',
				axisPointer: {
					z: 100,
				},
				// axisLabel: {
				//   rotate: 45
				// }
			},
			{
				type: 'category',
				gridIndex: 1,
				data: categoryData,
				boundaryGap: false,
				axisLine: { onZero: false },
				axisTick: { show: false },
				splitLine: { show: false },
				axisLabel: { show: false },
				min: 'dataMin',
				max: 'dataMax',
			},
		],
		yAxis: [
			{
				scale: true,
				splitArea: {
					show: true,
				},
				axisLabel: {
					// 保留2位小数
					formatter: function (value: number) {
						return value.toFixed(2);
					},
				},
			},
			{
				scale: true,
				gridIndex: 1,
				splitNumber: 2,
				axisLabel: { show: false },
				axisLine: { show: false },
				axisTick: { show: false },
				splitLine: { show: false },
			},
		],
		dataZoom: [
			{
				type: 'inside',
				start: 0,
				end: 100,
			},
			{
				show: true,
				type: 'slider',
				top: '80%',
				start: 0,
				end: 100,
			},
		],
		series: [
			{
				name: '股价',
				type: 'candlestick',
				data: values,
				itemStyle: {
					color: upColor,
					color0: downColor,
					borderColor: undefined,
					borderColor0: undefined,
				},
			},
			{
				name: 'MA5',
				type: 'line',
				data: calculateMA(5, values),
				smooth: true,
				lineStyle: {
					opacity: 0.5,
					color: '#FF6B6B',
				},
			},
			{
				name: 'MA10',
				type: 'line',
				data: calculateMA(10, values),
				smooth: true,
				lineStyle: {
					opacity: 0.5,
					color: '#4ECDC4',
				},
			},
			{
				name: 'MA20',
				type: 'line',
				data: calculateMA(20, values),
				smooth: true,
				lineStyle: {
					opacity: 0.5,
					color: '#45B7D1',
				},
			},
			{
				name: 'MA30',
				type: 'line',
				data: calculateMA(30, values),
				smooth: true,
				lineStyle: {
					opacity: 0.5,
					color: '#96CEB4',
				},
			},
			{
				name: 'Volume',
				type: 'bar',
				xAxisIndex: 1,
				yAxisIndex: 1,
				data: volumes,
			},
		],
	};
	klineChartOption.value = option;
};
const backtestLoading = ref(false);
// 获取MACD数据
const getBacktestMacdData = async () => {
	backtestLoading.value = true;
	try {
		const params = {
			ts_code: backtestForm.stockCode,
			start_date: backtestForm.date[0],
			end_date: backtestForm.date[1],
		};
		const res = await GetBacktestMacd(params);
		const { code, data, msg } = res;
		if (code === 2000 && data) {
			// 组装买卖信号表格数据
			// buy_dates金叉买入信号日期，sell_dates死叉卖出信号日期
			const { buy_dates = [], sell_dates = [], macd = [] } = data;
			let tableData = macd.map((item: any, index: number) => {
				const obj = {
					date: item.date,
					macd: item.macd,
					signal: item.signal,
					action: '',
				};
				if (buy_dates.includes(item.date)) {
					obj.action = '买入';
				} else if (sell_dates.includes(item.date)) {
					obj.action = '卖出';
				} else {
					obj.action = '';
				}
				return obj;
			});
			buySellSignals.value = tableData;
			// MACD策略回测结果
			initBacktestChart(data as any);
			// MACD曲线
			initMacdChart(macd as any);
		} else {
			buySellSignals.value = [];
			ElMessage.error(msg);
		}
		backtestLoading.value = false;
	} catch (error) {
		console.error('获取MACD数据失败:', error);
		initBacktestChart({ buy_dates: [], sell_dates: [], macd: [] });
		initMacdChart([]);
		backtestLoading.value = false;
	}
};

// 初始化MACD曲线图
const initMacdChart = (data: MacdDataItem[]) => {
	try {
		// 生成MACD曲线数据
		const dates: string[] = [];
		const macdLine: number[] = [];
		const signalLine: number[] = [];
		const histogram: number[] = [];

		data.forEach((item: MacdDataItem) => {
			// 数据项验证
			if (!item || typeof item !== 'object') {
				console.warn('跳过无效的数据项:', item);
				return;
			}

			// 确保所有必需字段都存在且为有效数值
			const date = item.date;
			const macd = typeof item.macd === 'number' && !isNaN(item.macd) ? item.macd : 0;
			const signal = typeof item.signal === 'number' && !isNaN(item.signal) ? item.signal : 0;
			const hist = typeof item.hist === 'number' && !isNaN(item.hist) ? item.hist : 0;

			if (date && typeof date === 'string') {
				dates.push(date);
				macdLine.push(macd);
				signalLine.push(signal);
				histogram.push(hist);
			} else {
				console.warn('跳过日期无效的数据项:', item);
			}
		});

		const option = {
			title: {
				text: 'MACD曲线',
				left: 'center',
				top: 10,
			},
			tooltip: {
				trigger: 'axis',
				axisPointer: {
					type: 'cross',
				},
			},
			legend: {
				data: ['MACD', 'Signal', 'MACD柱图'],
				left: 'center',
				top: 35,
			},
			grid: {
				left: '8%',
				right: '6%',
				bottom: '15%',
				top: '20%',
			},
			dataZoom: [
				{
					type: 'inside',
					start: 0,
					end: 100,
				},
				{
					show: true,
					type: 'slider',
					top: '92%',
					start: 0,
					end: 100,
				},
			],
			xAxis: {
				type: 'category',
				data: dates,
				scale: true,
				axisLabel: {
					rotate: 45,
				},
			},
			yAxis: {
				type: 'value',
				scale: true,
				axisLabel: {
					// 保留2位小数
					formatter: function (value: number) {
						return value.toFixed(2);
					},
				},
			},
			series: [
				{
					name: 'MACD',
					type: 'line',
					data: macdLine,
					smooth: true,
					symbol: 'none',
					lineStyle: {
						color: '#FFA500',
						width: 2,
					},
				},
				{
					name: 'Signal',
					type: 'line',
					data: signalLine,
					smooth: true,
					symbol: 'none',
					lineStyle: {
						color: '#00FFFF',
						width: 2,
					},
				},
				{
					name: 'MACD柱图',
					type: 'bar',
					data: histogram.map((val: number) => ({
						value: val,
						itemStyle: {
							color: val >= 0 ? '#FF4444' : '#00C851',
						},
					})),
					barWidth: '60%',
				},
			],
		};
		macdChartOption.value = option;
	} catch (error) {
		console.error('初始化MACD图表时发生错误:', error);
		ElMessage.error('图表初始化失败');
	}
};

// 初始化回测图表
const initBacktestChart = (data: any) => {
	try {
		// buy_dates金叉买入信号日期，sell_dates死叉卖出信号日期
		const { buy_dates = [], sell_dates = [], macd = [] } = data;

		// 生成MACD策略回测数据
		const dates: string[] = [];
		const closingPrice: number[] = []; // 收盘价
		const macdLine: number[] = []; // MACD线
		const signalLine: number[] = []; // Signal线
		const buySignals: (number | null)[] = []; // 金叉买入信号
		const sellSignals: (number | null)[] = []; // 死叉卖出信号

		macd.forEach((item: any) => {
			dates.push(item.date);
			closingPrice.push(item.close);
			macdLine.push(item.macd);
			signalLine.push(item.signal);
			buySignals.push(null); // 初始化为null
			sellSignals.push(null); // 初始化为null
		});

		// 设置买入信号
		buy_dates.forEach((buyDate: string) => {
			const index = dates.indexOf(buyDate);
			if (index !== -1) {
				buySignals[index] = closingPrice[index];
			}
		});

		// 设置卖出信号
		sell_dates.forEach((sellDate: string) => {
			const index = dates.indexOf(sellDate);
			if (index !== -1) {
				sellSignals[index] = closingPrice[index];
			}
		});

		// 计算动态y轴范围
		const priceMin = Math.min(...closingPrice);
		const priceMax = Math.max(...closingPrice);
		const priceRange = priceMax - priceMin;
		const pricePadding = priceRange * 0.1; // 10% padding

		const macdMin = Math.min(...macdLine, ...signalLine);
		const macdMax = Math.max(...macdLine, ...signalLine);
		const macdRange = macdMax - macdMin;
		const macdPadding = macdRange * 0.1; // 10% padding

		const option = {
			title: {
				text: 'MACD策略回测结果',
				left: 'center',
				top: 10,
			},
			tooltip: {
				trigger: 'axis',
				axisPointer: {
					type: 'cross',
				},
			},
			legend: {
				data: ['收盘价', '金叉买入信号', '死叉卖出信号', 'MACD', 'Signal'],
				left: '13%', // 改为百分比定位
				top: '13%', // 改为百分比定位
				orient: 'vertical',
				backgroundColor: 'rgba(200, 200, 200, 0.3)', // 淡灰色半透明
				borderColor: 'transparent', // 边框也透明
				borderWidth: 0, // 无边框
				padding: 5, // 减小内边距
				itemGap: 8, // 减小间距
			},
			grid: {
				left: '8%',
				right: '6%',
				bottom: '15%',
				top: '20%',
			},
			dataZoom: [
				{
					type: 'inside',
					start: 0,
					end: 100,
				},
				{
					show: true,
					type: 'slider',
					top: '92%',
					start: 0,
					end: 100,
				},
			],
			xAxis: {
				type: 'category',
				data: dates,
				scale: true,
				axisLabel: {
					rotate: 45,
				},
				boundaryGap: false,
			},
			yAxis: [
				{
					type: 'value',
					name: '价格',
					position: 'left',
					scale: true,
					min: priceMin - pricePadding,
					max: priceMax + pricePadding,
					axisLabel: {
						// 保留2位小数
						formatter: function (value: number) {
							return value.toFixed(2);
						},
					},
					splitLine: {
						show: true,
						lineStyle: {
							type: 'dashed',
							color: '#eee',
						},
					},
				},
				{
					type: 'value',
					name: 'MACD',
					position: 'right',
					scale: true,
					min: macdMin - macdPadding,
					max: macdMax + macdPadding,
					axisLabel: {
						// 保留2位小数
						formatter: function (value: number) {
							return value.toFixed(2);
						},
					},
					splitLine: {
						show: false,
					},
				},
			],
			series: [
				{
					name: '收盘价',
					type: 'line',
					data: closingPrice,
					yAxisIndex: 0,
					smooth: true,
					symbol: 'none',
					lineStyle: {
						color: '#0000FF', // 蓝色实线
						width: 1.5,
					},
				},
				{
					name: '金叉买入信号',
					type: 'scatter',
					data: buySignals.map((val, idx) => (val !== null ? [idx, val] : null)).filter((item) => item !== null),
					yAxisIndex: 0,
					symbol: 'triangle',
					symbolSize: 12,
					itemStyle: {
						color: '#FF0000', // 红色三角形
					},
					z: 10,
				},
				{
					name: '死叉卖出信号',
					type: 'scatter',
					data: sellSignals.map((val, idx) => (val !== null ? [idx, val] : null)).filter((item) => item !== null),
					yAxisIndex: 0,
					symbol: 'triangle',
					symbolRotate: 180,
					symbolSize: 12,
					itemStyle: {
						color: '#008000', // 绿色倒三角形
					},
					z: 10,
				},
				{
					name: 'MACD',
					type: 'line',
					data: macdLine,
					yAxisIndex: 1,
					smooth: true,
					symbol: 'none',
					lineStyle: {
						color: '#FFA500', // 橙色实线
						width: 1.5,
					},
				},
				{
					name: 'Signal',
					type: 'line',
					data: signalLine,
					yAxisIndex: 1,
					smooth: true,
					symbol: 'none',
					lineStyle: {
						color: '#00FFFF', // 青色实线
						width: 1.5,
					},
				},
			],
		};

		backtestChartOption.value = option;
	} catch (error) {
		console.error('初始化回测图表时发生错误:', error);
		ElMessage.error('回测图表初始化失败');
	}
};

const removeBaseCondition = (key: string) => {
	selectedBaseConditions.value = selectedBaseConditions.value.filter((c) => c.key !== key);

	// 清空对应的 filterForm 值或取消标签选中状态
	if (key.startsWith('chip_')) {
		// 处理筹码特征标签
		const tagKey = key.replace('chip_', '');
		const tag = tagOptions.chip.find((item: TagOption) => item.key === tagKey);
		if (tag) {
			tag.selected = false;
		}
	} else {
		// 处理基础筛选条件
		switch (key) {
			case 'dataDate':
				filterForm.dataDate = '';
				break;
			case 'stockCode':
				filterForm.stockCode = '';
				break;
			case 'stockName':
				filterForm.stockName = '';
				break;
			case 'marketCap':
				filterForm.marketCapMin = '';
				filterForm.marketCapMax = '';
				break;
			case 'volume5Day':
				filterForm.volume5DayMin = '';
				filterForm.volume5DayMax = '';
				break;
			case 'pe':
				filterForm.peMin = '';
				filterForm.peMax = '';
				break;
			case 'industry':
				filterForm.industryLevel3 = [];
				break;
		}
	}
};

const clearAllBaseConditions = () => {
	selectedBaseConditions.value = [];

	// 清空所有基础筛选条件
	filterForm.dataDate = '';
	filterForm.stockCode = '';
	filterForm.stockName = '';
	filterForm.marketCapMin = '';
	filterForm.marketCapMax = '';
	filterForm.volume5DayMin = '';
	filterForm.volume5DayMax = '';
	filterForm.peMin = '';
	filterForm.peMax = '';
	filterForm.industryLevel3 = [];

	// 清空筹码特征标签选中状态
	// tagOptions.chip.forEach((tag: TagOption) => {
	//   tag.selected = false
	// })
};

const removeCondition = (key: string) => {
	selectedConditions.value = selectedConditions.value.filter((c) => c.key !== key);

	// 解析key格式: "category_tagKey" (如 "macd_golden_cross")
	const parts = key.split('_');
	if (parts.length >= 2) {
		const category = parts[0] as TagCategory;
		const tagKey = parts.slice(1).join('_'); // 处理可能包含下划线的tagKey

		// 更新对应标签的选中状态为false
		const tag = tagOptions[category].find((item: TagOption) => item.key === tagKey);
		if (tag) {
			tag.selected = false;
		}
	}
};

const clearConditions = () => {
	selectedConditions.value = [];
	// 取消所有精筛查询条件标签的选中状态（排除筹码特征）
	(Object.keys(tagOptions) as TagCategory[]).forEach((category) => {
		// if (category !== 'chip') {  // 排除筹码特征
		tagOptions[category].forEach((tag: TagOption) => {
			tag.selected = false;
		});
		// }
	});
};

const getPriceClass = (change: number) => {
	return change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral';
};

const getChipClass = (value: number) => {
	return value < 15 ? 'positive' : value < 25 ? 'warning' : 'negative';
};

const getMacdType = (val: string) => {
	const types: Record<string, string> = {
		金叉: 'success',
		死叉: 'danger',
		突破: 'primary',
		背离: 'warning',
	};
	return types[val as keyof typeof types] || 'info';
};

const loading = ref(false);
const options = ref<{ value: string; label: string }[]>([]);
const handleStockCodeSearch = (query: string) => {
	// 调用lodash的防抖函数
	loading.value = true;
	if (!query) {
		options.value = [];
		loading.value = false;
		return;
	}
	handleStockCodeSearchDebounce(query);
};

const handleStockCodeSearchDebounce = _.debounce((query: string) => {
	if (!query) {
		options.value = [];
		loading.value = false;
		return;
	}
	if (tsCodeList.value.length) {
		// 最多展示20条
		const filtered = tsCodeList.value.filter((item) => item?.label?.toLowerCase()?.includes(query.toLowerCase()));
		options.value = filtered.slice(0, 20).map((item) => ({ value: item?.ts_code, label: item.label }));
		loading.value = false;
	} else {
		setTimeout(() => {
			options.value = [{ value: query, label: query }];
			loading.value = false;
		}, 100);
	}
}, 500);

const getBaseInfo = async (type: string) => {
	const res = await GetBaseInfo({ type: type });
	const { code, data, msg } = res;
	if (code === 2000 && data) {
		if (type === 'latest_trade_date') {
			filterForm.dataDate = data || '';
			// 初筛查询
			handleInitialScreening(true);
		} else if (type === 'industry_list') {
			industryOptions.value = buildTree(data || [], '0');
		} else if (type === 'ts_code_list') {
			let list = data || [];
			tsCodeList.value = list.map((item: any) => {
				return {
          ...item,
					label: `${item.symbol} | ${item.name}`,
				};
			});
		}
	}
};

const buildTree = (data: any[], parentId: string | number = 0, processed = new Set()) => {
	const tree: any[] = [];

	data.forEach((item) => {
		if (item.pid === parentId && !processed.has(item.id)) {
			processed.add(item.id);
			const node = {
				value: item.id,
				label: item.name,
				children: buildTree(data, item.id, processed),
			};
			tree.push(node);
		}
	});

	return tree;
};

// 生命周期
onMounted(() => {
	nextTick(() => {
		// 初始化图表
		initBacktestChart({ buy_dates: [], sell_dates: [], macd: [] });
		initMacdChart([]);
		initKlineChart([]);
		// 初始化引导：从localstorage中获取是否引导过，如果引导过，则不引导，否则引导
		const isGuided = localStorage.getItem('isGuided');
		if (!isGuided) {
			setTimeout(() => {
				tourShow.value = true;
				localStorage.setItem('isGuided', 'true');
			}, 500);
		}
	});
	// 获取默认日期
	getBaseInfo('latest_trade_date');
	// 获取行业列表
	getBaseInfo('industry_list');
	// 获取股票代码列表
	getBaseInfo('ts_code_list');
	// 初始化数据
	// handleInitialScreening(true)
	// 回测日期默认近一年
	const now = new Date();
	const startDate = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());
	backtestForm.date = [startDate.toISOString().split('T')[0], now.toISOString().split('T')[0]] as any;
});
</script>

<style scoped>
.chanlun-model-container {
	padding: 10px;
	background: #f5f5f5;
	min-height: 100vh;
	display: flex;
	flex-direction: column;
}

.page-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20px;
	padding: 20px;
	background: white;
	border-radius: 8px;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-title {
	display: flex;
	align-items: center;
	font-size: 24px;
	font-weight: bold;
	color: #333;
}

.header-title i {
	margin-right: 10px;
	font-size: 28px;
	color: #409eff;
}

.update-time {
	margin-left: 20px;
	font-size: 12px;
	color: #999;
	font-weight: normal;
}

.header-actions {
	display: flex;
	gap: 10px;
	align-items: center;
}

.selected-conditions {
	padding-top: 10px;
	border-top: 1px solid #f0f0f0;
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	gap: 15px;
	/* margin-bottom: 15px; */
}

.conditions-content {
	display: flex;
	align-items: center;
	flex-wrap: wrap;
	gap: 10px;
	flex: 1;
	min-width: 0;
}

.conditions-label {
	font-size: 14px;
	color: #666;
	white-space: nowrap;
	margin-right: 5px;
}

.conditions-tags {
	display: flex;
	flex-wrap: wrap;
	gap: 8px;
	flex: 1;
	min-width: 0;
}

.condition-tag {
	margin: 0;
}

.clear-all {
	font-size: 12px;
	color: #409eff;
	white-space: nowrap;
	flex-shrink: 0;
}

.filter-card {
	margin-bottom: 10px;
}

.card-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.filter-actions {
	display: flex;
	gap: 10px;
	align-items: center;
}

.filter-section {
	margin-bottom: 10px;
	/* padding-bottom: 10px; */
	border-bottom: 1px solid #f0f0f0;
}

.filter-section:last-child {
	border-bottom: none;
	margin-bottom: 0;
}

/* .section-title {
  font-size: 16px;
  font-weight: bold;
  color: #606266;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
} */

.section-title {
	font-size: 16px;
	font-weight: 600;
	color: #303133;
	/* margin-bottom: 15px; */
	padding-bottom: 8px;
	border-bottom: 2px solid #e4e7ed;
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.section-title .el-button {
	font-size: 12px;
	padding: 2px 8px;
}

.subsection-item-box {
	display: flex;
	align-items: center;
}

.subsection-title {
	font-size: 13px;
	font-weight: 600;
	color: #606266;
	margin-bottom: 12px;
	margin-top: 16px;
	width: 90px;
}

.tag-group {
	display: flex;
	flex-wrap: wrap;
	gap: 10px;
	margin-top: 10px;
	width: calc(100% - 90px);
}

.filter-tag {
	cursor: pointer;
	transition: all 0.2s ease;
	user-select: none;
}

.filter-tag:hover {
	transform: translateY(-1px);
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.filter-tag.el-tag--info {
	background-color: #f4f4f5;
	border-color: #e9e9eb;
	color: #909399;
}

.filter-tag.el-tag--success {
	background-color: #f0f9ff;
	border-color: #67c23a;
	color: #67c23a;
}

.backtest-card {
	margin-bottom: 20px;
}

/* 回测模态框样式 */
.backtest-controls {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20px;
	padding: 15px;
	background-color: #f8f9fa;
	border-radius: 6px;
}

.date-range {
	display: flex;
	align-items: center;
}

.backtest-actions {
	display: flex;
	gap: 10px;
}

.backtest-layout {
	display: flex;
	gap: 20px;
	/* height: 500px; */
}

.backtest-left {
	flex: 0 0 400px; /* 固定宽度400px */
	display: flex;
	flex-direction: column;
}

.backtest-right {
	flex: 1; /* 占据剩余空间 */
	min-width: 0;
	display: flex;
	flex-direction: column;
}

.macd-chart-section {
	margin-top: 20px;
	width: 100%;
	border-top: 1px solid #e4e7ed;
	padding-top: 20px;
}

.kline-chart-section {
	margin-top: 20px;
	width: 100%;
	border-top: 1px solid #e4e7ed;
	padding-top: 20px;
}

.main-content {
	margin-bottom: 10px;
}

.result-table-card {
	/* margin-bottom: 20px; */
	width: 100%;
}

.result-table-card :deep(.el-card__body) {
	padding: 20px;
	width: 100%;
}

.result-table-card .el-table {
	width: 100% !important;
}

.table-actions {
	display: flex;
	gap: 10px;
}

.pagination-container {
	display: flex;
	justify-content: flex-end;
	/* margin-top: 20px; */
	padding-top: 15px;
	border-top: 1px solid #f0f0f0;
}

.list-view {
	margin-bottom: 20px;
}

/* 价格颜色样式 */
.positive {
	color: #f56c6c;
	font-weight: bold;
}

.negative {
	color: #67c23a;
	font-weight: bold;
}

.neutral {
	color: #909399;
}

/* 筹码集中度颜色 */
.positive {
	color: #67c23a;
}

.warning {
	color: #e6a23c;
}

/* 响应式设计 */
@media (max-width: 1200px) {
	/* 表格在小屏幕上的适配 */
}

@media (max-width: 768px) {
	.chanlun-model-container {
		padding: 10px;
	}

	.page-header {
		flex-direction: column;
		gap: 15px;
		align-items: flex-start;
	}

	.header-actions {
		width: 100%;
		justify-content: flex-end;
	}

	.selected-conditions {
		flex-wrap: wrap;
	}

	.filter-form .el-form-item {
		margin-right: 10px;
	}
}
</style>
