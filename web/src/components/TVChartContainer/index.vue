<script setup>
import { onMounted, ref, onUnmounted, watch } from 'vue';
import { widget } from '../../../public/charting_library';
import { UDFCompatibleDatafeed } from '../../../public/datafeeds/udf/src/udf-compatible-datafeed';
const emit = defineEmits(['symbolChange', 'intervalChange']);
// 常量定义
const CHART_CONFIG = {
  COLORS: {
    DING: "#FA8072",
    DI: "#1E90FF",
    BI: "#708090", // #708090
    XD: "#00BFFF",
    ZSD: "#FFA710",
    BI_ZSS: "#708090", // #708090
    XD_ZSS: "#00BFFF",
    ZSD_ZSS: "#FFA710",
    BCS: "#D1D4DC",
    BC_TEXT: "#fccbcd",
    MMD_UP: "#FA8072",
    MMD_DOWN: "#1E90FF",
  },
  LINE_STYLES: {
    SOLID: 0,
    DOTTED: 1,
    DASHED: 2,
  },
  CHART_TYPES: [
    "fxs",
    "bis",
    "xds",
    "zsds",
    "bi_zss",
    "xd_zss",
    "zsd_zss",
    "bcs",
    "mmds",
  ],
};

// 防抖函数
function debounce(func, wait) {
  let timeout;
  return function (...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

// 图表工具类
const ChartUtils = {
  // 创建图表形状
  // 添加图表就绪检查，避免在图表未准备好时创建形状导致错误
  createShape(chart, points, options = {}) {
    const defaults = {
      lock: true,
      disableSelection: true,
      disableSave: true,
      disableUndo: true,
      showInObjectsTree: false,
      overrides: {},
    };

    const config = { ...defaults, ...options };

    // 检查图表是否存在且可用
    if (!chart) {
      console.warn("ChartUtils.createShape: chart is null or undefined");
      return Promise.reject(new Error("Chart not available"));
    }

    try {
      return config.shape === "trend_line" ||
        config.shape === "rectangle" ||
        config.shape === "circle"
        ? chart.createMultipointShape(points, config)
        : chart.createShape(points, config);
    } catch (error) {
      console.warn("ChartUtils.createShape failed:", error.message, "shape:", config.shape);
      return Promise.reject(error);
    }
  },

  // 创建分型点
  createFxShape(chart, fx, options = {}) {
    const color = fx.text === "ding" ? CHART_CONFIG.COLORS.DING : CHART_CONFIG.COLORS.DI;
    return this.createShape(chart, fx.points, {
      shape: "circle",
      overrides: {
        backgroundColor: color,
        color: color,
        linewidth: 4,
        ...options.overrides,
      },
      ...options,
    });
  },

  // 创建线段
  createLineShape(chart, line, options = {}) {
    return this.createShape(chart, line.points, {
      shape: "trend_line",
      overrides: {
        linestyle: parseInt(line.linestyle) || 0,
        linewidth: options.linewidth || 1,
        linecolor: options.color || CHART_CONFIG.COLORS.BI,
        ...options.overrides,
      },
      ...options,
    });
  },

  // 创建中枢
  createZhongshuShape(chart, zs, options = {}) {
    return this.createShape(chart, zs.points, {
      shape: "rectangle",
      overrides: {
        linestyle: parseInt(zs.linestyle) || 0,
        linewidth: options.linewidth || 1,
        linecolor: options.color || CHART_CONFIG.COLORS.BI,
        backgroundColor: options.color || CHART_CONFIG.COLORS.BI,
        transparency: 95,
        color: options.color,
        "trendline.linecolor": options.color,
        fillBackground: true,
        filled: true,
        ...options.overrides,
      },
      ...options,
    });
  },

  // 创建买卖点
  createMmdShape(chart, mmd, options = {}) {
    const isBuy = mmd.text.includes("B");
    const color = isBuy ? CHART_CONFIG.COLORS.MMD_UP : CHART_CONFIG.COLORS.MMD_DOWN;
    const shape = isBuy ? "arrow_up" : "arrow_down";

    return this.createShape(chart, mmd.points, {
      shape,
      text: mmd.text,
      overrides: {
        markerColor: color,
        backgroundColor: color,
        color: color,
        fontsize: 14, // 增加字号
        bold: true,   // 加粗提高辨识度
        transparency: 80,
        ...options.overrides,
      },
      ...options,
    });
  },

  // 创建背驰点
  createBcShape(chart, bc, options = {}) {
    return this.createShape(chart, bc.points, {
      shape: "balloon",
      text: bc.text,
      overrides: {
        markerColor: CHART_CONFIG.COLORS.BCS,
        backgroundColor: CHART_CONFIG.COLORS.BCS,
        textColor: CHART_CONFIG.COLORS.BC_TEXT,
        transparency: 70,
        backgroundTransparency: 70,
        fontsize: 12, // 增加字号
        bold: true,   // 加粗
        offset: 20,
        ...options.overrides,
      },
      ...options,
    });
  },
};

// 获取语言
function getLanguageFromURL() {
  const regex = new RegExp('[\\?&]lang=([^&#]*)');
  const results = regex.exec(window.location.search);
  return results === null
    ? null
    : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

// 定义props
const props = defineProps({
  symbol: {
    default: 'AAPL',
    type: String,
  },
  interval: {
    default: '1D',
    type: String,
  },
  datafeedUrl: {
    default: 'https://demo_feed.tradingview.com',
    type: String,
  },
  libraryPath: {
    // 线上环境需要添加/qtrade/前缀
    default: import.meta.env.DEV ? '/charting_library/' : '/qtrade/charting_library/',
    type: String,
  },
  chartsStorageUrl: {
    default: 'https://saveload.tradingview.com',
    type: String,
  },
  chartsStorageApiVersion: {
    default: '1.1',
    type: String,
  },
  clientId: {
    default: 'tradingview.com',
    type: String,
  },
  userId: {
    default: 'public_user_id',
    type: String,
  },
  fullscreen: {
    default: false,
    type: Boolean,
  },
  autosize: {
    default: true,
    type: Boolean,
  },
  studiesOverrides: {
    type: Object,
    default: () => ({
      // "volume.color based on previous close": true, // 基于前收盘价决定颜色
      "volume.volume.color.0": "#089981", // 成交量颜色
      "volume.volume.color.1": "#f23645", // 成交量颜色
      "volume.volume.transparency": 50, // 成交量不透明度
      // MACD 指标颜色设置 (中国股市风格：红涨绿跌)
      "macd.histogram.color.0": "#f23645", // MACD柱状图
      "macd.histogram.color.1": "rgba(242, 54, 69, .5)", // MACD柱状图
      "macd.histogram.color.2": "rgba(8, 153, 129, .5)", // MACD柱状图
      "macd.histogram.color.3": "#089981", // MACD柱状图
      "macd.macd.color": "#2962FF", // MACD线颜色（蓝色）
      "macd.signal.color": "#FF6D00", // 信号线颜色（橙色）
    })
  },
});

const chartContainer = ref();
let chartWidget;
let datafeed;
let activeChart = null;
let objCharts = {};

// 防抖绘制函数
const debouncedDrawChanlun = debounce(() => drawChanlun(), 1000);

// 获取图表数据
function getChartData() {
  // console.log("chartWidget:::::::::::::::", chartWidget);
  // console.log("activeChart:::::::::::::::", activeChart);
  if (!chartWidget || !activeChart) return null;

  const symbolInterval = chartWidget.symbolInterval();
  // console.log("symbolInterval:::::::::::::::::", symbolInterval);

  if (!symbolInterval) return null;

  const symbolResKey = `${symbolInterval.symbol.toString().toLowerCase()}${symbolInterval.interval.toString().toLowerCase()}`;
  // console.log("datafeed:::::::::::::::::", datafeed);
  // console.log("symbolResKey:::::::::::::::::", symbolResKey);

  const barsResult = datafeed?._historyProvider?.bars_result?.get(symbolResKey);
  // console.log("barsResult:::::::::::::::::", barsResult);
  if (!barsResult) return null;
  const visibleRange = activeChart.getVisibleRange();
  const from = visibleRange?.from || 0;
  const symbolKey = `${symbolInterval.symbol}_${symbolInterval.interval}`;

  return { symbolKey, barsResult, from };
}

// 初始化图表容器
function initChartContainer(symbolKey) {
  if (!objCharts[symbolKey]) {
    objCharts[symbolKey] = {};
    CHART_CONFIG.CHART_TYPES.forEach((type) => {
      objCharts[symbolKey][type] = [];
    });
  }
  return objCharts[symbolKey];
}

// 绘制图表元素
function drawChartElements(chartData) {
  const { symbolKey, barsResult, from } = chartData;
  // console.log("chartData:::::::::::::::::::", chartData);

  const chartContainer = initChartContainer(symbolKey);

  // 绘制分型
  if (barsResult.fxs) {
    barsResult.fxs.forEach((fx) => {
      if (fx.points?.[0]?.time >= from) {
        const key = JSON.stringify(fx);
        const existed = chartContainer.fxs.find((item) => item.key === key);
        if (existed) return;
        chartContainer.fxs.push({
          time: fx.points[0].time,
          key,
          id: ChartUtils.createFxShape(activeChart, fx),
        });
      }
    });
  }

  // 绘制笔
  if (barsResult.bis) {
    barsResult.bis.forEach((bi) => {
      if (bi.points?.[0]?.time >= from) {
        const key = JSON.stringify(bi);
        const existed = chartContainer.bis.find((item) => item.key === key);
        if (existed) return;
        chartContainer.bis.push({
          time: bi.points[0].time,
          key,
          id: ChartUtils.createLineShape(activeChart, bi, {
            color: CHART_CONFIG.COLORS.BI,
            linewidth: 1,
          }),
        });
      }
    });
  }

  // 绘制线段
  if (barsResult.xds) {
    barsResult.xds.forEach((xd) => {
      if (xd.points?.[0]?.time >= from) {
        const key = JSON.stringify(xd);
        const existed = chartContainer.xds.find((item) => item.key === key);
        if (existed) return;
        chartContainer.xds.push({
          time: xd.points[0].time,
          key,
          id: ChartUtils.createLineShape(activeChart, xd, {
            color: CHART_CONFIG.COLORS.XD,
            linewidth: 2,
          }),
        });
      }
    });
  }

  // 绘制走势段
  if (barsResult.zsds) {
    barsResult.zsds.forEach((zsd) => {
      if (zsd.points?.[0]?.time >= from) {
        const key = JSON.stringify(zsd);
        const existed = chartContainer.zsds.find((item) => item.key === key);
        if (existed) return;
        chartContainer.zsds.push({
          time: zsd.points[0].time,
          key,
          id: ChartUtils.createLineShape(activeChart, zsd, {
            color: CHART_CONFIG.COLORS.ZSD,
            linewidth: 3,
          }),
        });
      }
    });
  }

  // 绘制笔中枢
  if (barsResult.bi_zss) {
    barsResult.bi_zss.forEach((bi_zs) => {
      if (bi_zs.points?.[0]?.time >= from) {
        const key = JSON.stringify(bi_zs);
        const existed = chartContainer.bi_zss.find(
          (item) => item.key === key
        );
        if (existed) return;
        chartContainer.bi_zss.push({
          time: bi_zs.points[0].time,
          key,
          id: ChartUtils.createZhongshuShape(activeChart, bi_zs, {
            color: CHART_CONFIG.COLORS.BI_ZSS,
            linewidth: 1,
          }),
        });
      }
    });
  }

  // 绘制线段中枢
  if (barsResult.xd_zss) {
    barsResult.xd_zss.forEach((xd_zs) => {
      if (xd_zs.points?.[0]?.time >= from) {
        const key = JSON.stringify(xd_zs);
        const existed = chartContainer.xd_zss.find(
          (item) => item.key === key
        );
        if (existed) return;
        chartContainer.xd_zss.push({
          time: xd_zs.points[0].time,
          key,
          id: ChartUtils.createZhongshuShape(activeChart, xd_zs, {
            color: CHART_CONFIG.COLORS.XD_ZSS,
            linewidth: 2,
          }),
        });
      }
    });
  }

  // 绘制走势段中枢
  if (barsResult.zsd_zss) {
    barsResult.zsd_zss.forEach((zsd_zs) => {
      if (zsd_zs.points?.[0]?.time >= from) {
        const key = JSON.stringify(zsd_zs);
        const existed = chartContainer.zsd_zss.find(
          (item) => item.key === key
        );
        if (existed) return;
        chartContainer.zsd_zss.push({
          time: zsd_zs.points[0].time,
          key,
          id: ChartUtils.createZhongshuShape(activeChart, zsd_zs, {
            color: CHART_CONFIG.COLORS.ZSD_ZSS,
            linewidth: 2,
          }),
        });
      }
    });
  }

  // 绘制背驰
  if (barsResult.bcs) {
    // 按时间进行分组合并
    const bcGroups = new Map();
    barsResult.bcs.forEach((bc) => {
      const time = bc.points?.time || bc.time;
      if (time >= from) {
        if (!bcGroups.has(time)) bcGroups.set(time, []);
        bcGroups.get(time).push(bc);
      }
    });

    bcGroups.forEach((bcsAtTime, timeKey) => {
      const mergedText = [...new Set(bcsAtTime.map(b => b.text))].join('/');
      const mergedBc = { ...bcsAtTime[0], text: mergedText };
      const key = `bc_${timeKey}_${mergedText}`;
      
      // 检查并在必要时替换已有标签
      const existingIndex = chartContainer.bcs.findIndex(item => item.time === timeKey);
      if (existingIndex !== -1) {
        const existing = chartContainer.bcs[existingIndex];
        if (existing.key === key) return;
        try { existing.id.then(id => activeChart.removeEntity(id)); } catch(e) {}
        chartContainer.bcs.splice(existingIndex, 1);
      }

      chartContainer.bcs.push({
        time: timeKey,
        key,
        id: ChartUtils.createBcShape(activeChart, mergedBc),
      });
    });
  }

  // 绘制买卖点
  if (barsResult.mmds) {
    // 按时间进行分组，合并相同位置的买卖点，避免文字重叠
    const mmdGroups = new Map();
    barsResult.mmds.forEach((mmd) => {
      if (mmd.points?.time >= from) {
        const timeKey = mmd.points.time;
        if (!mmdGroups.has(timeKey)) mmdGroups.set(timeKey, []);
        mmdGroups.get(timeKey).push(mmd);
      }
    });

    mmdGroups.forEach((mmdsAtTime, timeKey) => {
      // 优化文字合并：按前缀分组（如：笔、线）
      const prefixGroups = {};
      mmdsAtTime.forEach(m => {
        const parts = m.text.split(':');
        const p = parts.length > 1 ? parts[0] + ':' : '';
        const c = parts.length > 1 ? parts[1] : parts[0];
        if (!prefixGroups[p]) prefixGroups[p] = new Set();
        prefixGroups[p].add(c);
      });
      
      const mergedStrings = Object.entries(prefixGroups).map(([p, contents]) => {
        return p + Array.from(contents).join('/');
      });
      const mergedText = mergedStrings.join(' ');

      const mergedMmd = {
        ...mmdsAtTime[0],
        text: mergedText,
      };

      const key = `mmd_${timeKey}_${mergedText}`;
      
      // 检查并在必要时替换已有标签
      const existingIndex = chartContainer.mmds.findIndex(item => item.time === timeKey);
      if (existingIndex !== -1) {
        const existing = chartContainer.mmds[existingIndex];
        if (existing.key === key) return;
        try { existing.id.then(id => activeChart.removeEntity(id)); } catch(e) {}
        chartContainer.mmds.splice(existingIndex, 1);
      }

      chartContainer.mmds.push({
        time: timeKey,
        key,
        id: ChartUtils.createMmdShape(activeChart, mergedMmd),
      });
    });
  }
}

// 绘制缠论图表
function drawChanlun() {
  console.log("drawChanlun:::::::::::::::::::::::::::::::::::::::::::::::::::::::::");

  // 确保 activeChart 存在
  if (!activeChart) {
    console.warn("drawChanlun: activeChart is not available");
    return;
  }

  // 使用 dataReady 确保数据已经准备好再绘制
  // 这样可以避免在数据加载过程中尝试创建形状导致的错误
  activeChart.dataReady(() => {
    const codeStart = performance.now();

    const chartData = getChartData();
    // console.log("chartData::::::::::", chartData);
    if (!chartData) {
      console.warn("drawChanlun: chartData is null");
      return;
    }

    console.log("Drawing chart for:", chartData.symbolKey);

    // 绘制所有图表元素
    drawChartElements(chartData);

    const codeEnd = performance.now();
    console.log(
      `${chartData.symbolKey} 运行时间: ${codeEnd - codeStart} 毫秒`
    );
  });
}

// 清除已绘制的图表
function clearDrawChanlun(clearType) {
  // 如果 clear_type == 'last' ，则按照 time 从低到高排序，删除 time 值最大的一个对象
  console.log("清除已绘制的图表 : " + clearType);
  if (clearType == "last") {
    for (const symbolKey in objCharts) {
      for (const chartType in objCharts[symbolKey]) {
        if (objCharts[symbolKey][chartType].length == 0) {
          continue;
        }
        const maxTime = Math.max(
          ...objCharts[symbolKey][chartType].map((item) => item.time)
        );
        for (const _i in objCharts[symbolKey][chartType]) {
          const item = objCharts[symbolKey][chartType][_i];
          if (item.time == maxTime) {
            item.id.then((_id) => activeChart.removeEntity(_id));
          }
        }
        objCharts[symbolKey][chartType] = objCharts[symbolKey][
          chartType
        ].filter((item) => item.time != maxTime);
      }
    }
  } else {
    Object.values(objCharts).forEach((symbolData) => {
      Object.values(symbolData).forEach((chartItems) => {
        chartItems.forEach((item) => {
          try {
            item.id.then((_id) => activeChart.removeEntity(_id));
          } catch (e) {
            console.warn("Failed to remove chart entity:", e);
          }
        });
      });
    });
    // 清空引用
    objCharts = {};
  }
}

// 处理数据加载
// 注意：这里不需要 clearDrawChanlun，因为 onIntervalChanged/onSymbolChanged 已经清除过了
function handleDataLoaded() {
  console.log("数据重新加载");
  // 数据加载完成，触发绘制
  debouncedDrawChanlun();
}

// 处理数据准备
// 这是绘制的主要触发点，数据已经完全准备好
function handleDataReady() {
  console.log("数据准备");
  // 数据准备完成，触发绘制
  debouncedDrawChanlun();
}

// 处理数据更新
function handleTick() {
  console.log("数据更新");
  clearDrawChanlun("last");
  debouncedDrawChanlun();
}

// 处理可视区域变化
function handleVisibleRangeChange() {
  debouncedDrawChanlun();
}

// 初始化图表
function initChart(forceBlankChart = false) {
  console.log('初始化图表', props.symbol);

  // 【彻底清理】防止重影和冲突
  if (window.tvObserver) {
     window.tvObserver.disconnect();
     window.tvObserver = null;
  }

  // 如果已有图表实例，先销毁
  if (chartWidget) {
    chartWidget.remove();
    chartWidget = null;
    activeChart = null;
    objCharts = {};
  }

  // 创建datafeed实例
  datafeed = new UDFCompatibleDatafeed(props.datafeedUrl);

  const widgetOptions = {
    symbol: props.symbol, // 商品
    interval: props.interval, // 周期
    datafeed: datafeed,
    container: chartContainer.value,
    library_path: props.libraryPath,
    time_frames: [],
    timezone: "Asia/Shanghai", // 时区
    locale: 'zh',
    disabled_features: ['use_localstorage_for_settings', 'go_to_date'],
    enabled_features: [
      'save_chart_properties_to_local_storage', // 允许保存到云端
      'use_localstorage_for_settings',
      'header_saveload',           // 基础保存/加载功能
      'header_layout_toggle',      // 启用布局切换菜单（通常包含新建）
      'show_object_tree',          // 可选：对象树
    ],
    charts_storage_url: props.chartsStorageUrl,
    charts_storage_api_version: props.chartsStorageApiVersion,
    client_id: props.clientId,
    user_id: props.userId,
    fullscreen: props.fullscreen,
    autosize: props.autosize,
    load_last_chart: forceBlankChart ? false : true, // 修改：正常情况刷新依然自动加载，只有点击新建按钮时才加载空白画板
    studies_overrides: props.studiesOverrides,
    // 延迟阈值（以毫秒为单位），用于在用户在搜索框中键入商品名称时减少商品搜索请求的数量。
    symbol_search_request_delay: 100,
    // theme: 'dark',
    // 设置K线和成交量颜色为中国习惯：上涨红色，下跌绿色
    overrides: {
      // K线颜色设置
      "mainSeriesProperties.candleStyle.upColor": "#f23645", // 上涨K线颜色
      "mainSeriesProperties.candleStyle.downColor": "#089981", // 下跌K线颜色
      "mainSeriesProperties.candleStyle.borderUpColor": "#f23645", // 上涨K线边框颜色
      "mainSeriesProperties.candleStyle.borderDownColor": "#089981", // 下跌K线边框颜色
      "mainSeriesProperties.candleStyle.wickUpColor": "#f23645", // 上涨K线影线颜色
      "mainSeriesProperties.candleStyle.wickDownColor": "#089981", // 下跌K线影线颜色
      "mainSeriesProperties.hollowCandleStyle.upColor": "#f23645", // 空心K线上涨颜色
      "mainSeriesProperties.hollowCandleStyle.downColor": "#089981", // 空心K线下跌颜色
      "mainSeriesProperties.hollowCandleStyle.borderUpColor": "#f23645", // 空心K线上涨边框颜色
      "mainSeriesProperties.hollowCandleStyle.borderDownColor": "#089981", // 空心K线下跌边框颜色
      "mainSeriesProperties.hollowCandleStyle.wickUpColor": "#f23645", // 空心K线上涨影线颜色
      "mainSeriesProperties.hollowCandleStyle.wickDownColor": "#089981", // 空心K线下跌影线颜色
      // 成交量柱状图颜色设置
      "mainSeriesProperties.volCandlesStyle.upColor": "#f23645", // 上涨时成交量颜色
      "mainSeriesProperties.volCandlesStyle.downColor": "#089981", // 下跌时成交量颜色
      "mainSeriesProperties.volCandlesStyle.borderUpColor": "#f23645", // 上涨时成交量边框颜色
      "mainSeriesProperties.volCandlesStyle.borderDownColor": "#089981", // 下跌时成交量边框颜色
      "mainSeriesProperties.volCandlesStyle.wickUpColor": "#f23645", // 
      "mainSeriesProperties.volCandlesStyle.wickDownColor": "#089981", // 
      // 买卖点箭头颜色
      "linetoolarrowmarkup.arrowColor": "#f23645",
      "linetoolarrowmarkdown.arrowColor": "#089981"
    },
  };

  chartWidget = new widget(widgetOptions);

  chartWidget.onChartReady(() => {
    // 自定义顶部工具栏按钮 - 退出/取消当前布局
    chartWidget.headerReady().then(() => {
      const button = chartWidget.createButton({ align: 'right' });

      button.setAttribute('title', '不再使用当前布局，重置为空白状态');
      button.classList.add('apply-common-tooltip');
      button.classList.add('tv-custom-cancel-layout-btn'); 
      
      button.style.color = '#333333';
      button.style.display = 'none'; 
      button.style.alignItems = 'center';
      button.style.justifyContent = 'center';
      button.style.cursor = 'pointer';
      button.style.fontWeight = 'bold';
      button.style.padding = '0 4px';
      // 注入 SVG 清除图标
      button.innerHTML = '<svg t="1776249299415" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1971" width="16" height="16"><path d="M405.312 736a32 32 0 0 1-32-32V448a32 32 0 0 1 64 0v256a32 32 0 0 1-32 32zM650.688 448a32 32 0 0 0-64 0v256a32 32 0 1 0 64 0V448z" fill="#333333" p-id="1972"></path><path d="M514.816 53.312h-2.752c-21.504 0-39.808 0-55.04 1.408a116.672 116.672 0 0 0-45.568 12.352c-5.76 3.008-11.2 6.528-16.32 10.496a116.608 116.608 0 0 0-30.144 36.352c-7.552 13.248-15.168 29.888-24.128 49.536l-17.856 39.232H128a32 32 0 0 0 0 64h32V832A160 160 0 0 0 320 992h384a160 160 0 0 0 160-160V266.688h32a32 32 0 0 0 0-64h-190.912l-20.992-43.264c-9.152-18.944-16.896-35.008-24.576-47.744a116.608 116.608 0 0 0-30.208-35.072 117.376 117.376 0 0 0-16.064-10.112 116.608 116.608 0 0 0-44.736-11.84c-14.784-1.28-32.64-1.28-53.696-1.28zM800 266.688V832a96 96 0 0 1-96 96H320A96 96 0 0 1 224 832V266.688h576z m-166.016-64h-240.64l5.184-11.456c9.664-21.184 16.064-35.2 22.016-45.568a54.144 54.144 0 0 1 13.568-17.28 53.312 53.312 0 0 1 7.424-4.8 54.144 54.144 0 0 1 21.312-5.12c11.968-1.088 27.328-1.152 50.624-1.152 22.72 0 37.76 0 49.344 1.088 11.072 0.96 16.704 2.752 20.928 4.928 2.56 1.28 4.992 2.88 7.36 4.608 3.776 2.816 7.808 7.168 13.504 16.64 6.016 10.048 12.608 23.488 22.528 43.968l6.848 14.08z" fill="#333333" p-id="1973"></path></svg>';

      button.addEventListener('click', () => {
        initChart(true);
      });

      // 核心优化：使用 MutationObserver 替代 setInterval 监听变化
      try {
        if (!chartWidget || typeof chartWidget._innerWindow !== 'function') return;
        const iframeDoc = chartWidget._innerWindow().document;
        if (iframeDoc) {
          const saveLoadBtn = iframeDoc.querySelector('#header-toolbar-save-load') 
                           || iframeDoc.querySelector('[data-name="save-load-menu"]')
                           || iframeDoc.querySelector('.layout-dropdown');
          
          if (saveLoadBtn && saveLoadBtn.parentNode) {
            
            const updateState = () => {
              // 1. 位置摆放
              if (saveLoadBtn.nextSibling !== button.parentNode) {
                saveLoadBtn.parentNode.insertBefore(button.parentNode, saveLoadBtn.nextSibling);
              }
              
              // 2. 清理可能残留的重复按钮
              const allMyBtns = iframeDoc.querySelectorAll('.tv-custom-cancel-layout-btn');
              allMyBtns.forEach(b => {
                if (b !== button) b.parentNode.remove();
              });

              // 3. 根据文本判断显示隐藏
              const text = saveLoadBtn.textContent.trim();
              const isNoLayout = !text 
                || text === '保存' 
                || text === '保存保存'
                || text === 'Save'

              button.style.display = isNoLayout ? 'none' : 'flex';
            };

            // 开启监听
            window.tvObserver = new MutationObserver(updateState);
            window.tvObserver.observe(saveLoadBtn.parentNode, { 
              childList: true, 
              characterData: true, 
              subtree: true 
            });

            // 初始执行一次
            updateState();
          }
        }
      } catch (e) {
        console.warn('TV Layout Observer Error:', e);
      }
    });

    // 获取活跃图表
    activeChart = chartWidget.activeChart();
    if (!activeChart) {
      console.error("Failed to get active chart");
      return;
    }

    // 数据加载事件
    activeChart
      .onDataLoaded()
      .subscribe(null, () => handleDataLoaded(), true);

    // 数据准备事件
    activeChart.dataReady(() => handleDataReady());

    // 数据更新事件
    chartWidget.subscribe("onTick", () => handleTick());

    // 交易品种变更事件
    activeChart.onSymbolChanged().subscribe(null, (symbolInfo) => {
      console.log("onSymbolChanged", symbolInfo);
      emit('symbolChange', symbolInfo);
      // 仅清除已绘制的图表元素
      // 不在这里调用 debouncedDrawChanlun()
      // 因为此时新数据还没加载，应该等 onDataLoaded/dataReady 触发后再绘制
      clearDrawChanlun();
    });

    // 周期变更事件
    activeChart.onIntervalChanged().subscribe(null, (interval) => {
      console.log('onIntervalChanged', interval);
      emit('intervalChange', interval);
      // 仅清除已绘制的图表元素
      // 不在这里调用 debouncedDrawChanlun()
      // 因为此时新数据还没加载，应该等 onDataLoaded/dataReady 触发后再绘制
      clearDrawChanlun();
    });

    // 可视区域变化事件
    activeChart
      .onVisibleRangeChanged()
      .subscribe(null, () => handleVisibleRangeChange());
  });
}

onMounted(() => {
  // 初始化图表
  initChart();
});

// 监听symbol变化，切换图表symbol
watch(
  () => props.symbol,
  (newSymbol, oldSymbol) => {
    if (newSymbol !== oldSymbol && chartWidget) {
      console.log(`切换股票从 ${oldSymbol} 到 ${newSymbol}`);

      // 获取当前图表的实际interval，而不是直接使用props.interval
      // 这样可以确保在用户通过UI切换周期后，切换股票时使用正确的周期
      const currentSymbolInterval = chartWidget.symbolInterval();
      const currentInterval = currentSymbolInterval ? currentSymbolInterval.interval : props.interval;

      // 使用setSymbol方法切换股票，不销毁图表实例
      chartWidget.setSymbol(newSymbol, currentInterval, () => {
        console.log(`股票切换完成：${newSymbol}`);
      });
    }
  }
);

// 监听interval变化，切换图表周期
watch(
  () => props.interval,
  (newInterval, oldInterval) => {
    if (newInterval !== oldInterval && chartWidget) {
      console.log(`切换周期从 ${oldInterval} 到 ${newInterval}`);

      // 获取当前图表的实际symbol，而不是直接使用props.symbol
      // 这样可以确保在用户通过UI切换股票后，切换周期时使用正确的股票
      const currentSymbolInterval = chartWidget.symbolInterval();
      const currentSymbol = currentSymbolInterval ? currentSymbolInterval.symbol : props.symbol;

      // 使用setSymbol方法切换周期，保持当前symbol不变
      chartWidget.setSymbol(currentSymbol, newInterval, () => {
        console.log(`周期切换完成：${newInterval}`);
      });
    }
  }
);

onUnmounted(() => {
  if (chartWidget) {
    chartWidget.remove();
    chartWidget = null;
  }
});
</script>

<template>
  <div class="TVChartContainer" ref="chartContainer" />
</template>

<style scoped>
.TVChartContainer {
  /* height: calc(100vh - 80px); */
  /* height: 100vh; */
  height: 100%;
}
</style>