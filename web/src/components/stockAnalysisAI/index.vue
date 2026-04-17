<template>
  <div class="ai-analysis-container">
    <!-- 分析条件选择区域 -->
    <div class="analysis-params">
      <!-- 股票选择 -->
      <div class="param-item">
        <label class="param-label">
          <span class="icon">🔍</span> 股票选择
        </label>
        <el-select-v2
          v-model="selectedStock"
          :options="stockList"
          :props="{ label: 'label', value: 'symbol' }"
          placeholder="请搜索或选择股票"
          filterable
          class="modern-select"
        />
      </div>
      <!-- 分析频率 -->
      <div class="param-item">
        <label class="param-label">
          <span class="icon">⏱️</span> 分析频率
        </label>
        <el-select
          v-model="selectedPeriod"
          placeholder="请选择频率"
          class="modern-select"
        >
          <el-option
            v-for="item in periodOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </div>
      <!-- 分析按钮 -->
      <div class="param-item action-item">
        <el-button
          type="primary"
          class="modern-analysis-btn"
          @click="startAnalysis"
          :loading="isAnalyzing"
          :disabled="activeAnalysisCount >= 5 && !isAnalyzing"
        >
          <span v-if="!isAnalyzing">
            ✨ 开始 AI 分析 
            <span v-if="activeAnalysisCount > 0" class="count-badge">({{ activeAnalysisCount }}/5)</span>
          </span>
          <span v-else>正在深度分析中...</span>
        </el-button>
        <div v-if="activeAnalysisCount >= 5 && !isAnalyzing" class="limit-tip">并发分析已达上限 (5/5)</div>
      </div>
    </div>

    <!-- 无结果提示 -->
    <div
      class="no-result"
      v-if="analysisHistory.length === 0"
    >
      <el-empty description="请选择分析条件并点击开始分析"></el-empty>
    </div>

    <div
      class="history-cards"
      v-if="analysisHistory.length > 0"
      v-loading="isHistoryLoading"
    >
      <div
        v-for="(item, index) in analysisHistory"
        :key="item.id || index"
        :class="['history-card', item.status]"
        @click="showDetail(item)"
      >
        <div class="card-status-bar"></div>
        <div class="card-main">
          <div class="card-header-row">
            <span class="stock-name">{{ item.stockName }}</span>
            <el-tag type="info" size="small" effect="plain" class="period-badge">{{ getPeriodLabel(item.resolution) }}</el-tag>
            <!-- 删除按钮 -->
            <el-icon class="delete-icon" @click.stop="handleDeleteHistory(item)"><Close /></el-icon>
          </div>
          <div class="card-code-row">{{ item.stockCode }}</div>
          <div class="card-footer-row">
            <div class="status-indicator">
              <span :class="['dot', item.status]"></span>
              <span class="status-text">{{ item.status === 'success' ? '已完成' : item.status === 'analyzing' ? '分析中' : '失败' }}</span>
            </div>
            <span class="time-stamp">{{ item.time }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- AI分析抽屉 -->
    <el-drawer
      v-model="aiAnalysisDrawerVisible"
      title="AI股票分析"
      size="70%"
      destroy-on-close
      @closed="analysisStockData = null"
    >
      <template #header>
        <div class="drawer-header-info" v-if="analysisStockData">
          <div class="header-content-row">
            <span class="h-stock-name">{{ analysisStockData.stockName }}</span>
            <span class="h-stock-code">{{ analysisStockData.stockCode }}</span>
            <el-tag type="success" size="small" effect="plain" class="h-period-tag">{{ getPeriodLabel(analysisStockData.resolution) }}</el-tag>
            
            <span class="h-model-name">{{ analysisStockData.model }}</span>
            
            <div class="h-token-usage" v-if="analysisStockData.usage">
              <span class="token-label">Tokens:</span>
              <span class="token-value">{{ analysisStockData.usage.total_tokens }}</span>
              <span class="token-split">(P:{{ analysisStockData.usage.prompt_tokens }} C:{{ analysisStockData.usage.completion_tokens }})</span>
            </div>

            <el-tag type="success" size="small" effect="plain" class="h-status-tag">成功</el-tag>
            
            <span class="h-time">{{ analysisStockData.time }}</span>
          </div>
        </div>
      </template>
      <div class="drawer-content-body" v-if="analysisStockData">
        <!-- 保留原有抽屉组件先注释 -->
        <!-- <StockAnalysis
          v-if="aiAnalysisDrawerVisible"
          :selected-stock="analysisStockData"
        /> -->
        
        <el-collapse v-model="activeNames" class="modern-collapse">
          <el-collapse-item name="1">
            <template #title>
              <div class="collapse-title">
                <span class="icon">📝</span> 提示词 (Prompt) 数据来源
              </div>
            </template>
            <div class="markdown-content" v-html="formatMarkdown(analysisStockData.prompt)"></div>
          </el-collapse-item>
          <el-collapse-item name="2">
            <template #title>
              <div class="collapse-title">
                <span class="icon">🤖</span> AI 分析复盘结果
              </div>
            </template>
            <div class="markdown-content" v-html="formatMarkdown(analysisStockData.report)"></div>
          </el-collapse-item>
        </el-collapse>
      </div>
      <template #footer>
        <div class="drawer-footer">
          <el-button @click="copyAllContent" plain icon="DocumentCopy">复制全部 (提示词+结果)</el-button>
          <el-button @click="downloadAllContent" plain icon="Download">下载全部 (提示词+结果)</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch, onMounted, onBeforeUnmount, computed } from 'vue';
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus';
import DOMPurify from 'dompurify';
import {
	GetAIAnalysis,
	GetAIHistory,
	DeleteAIHistory,
} from '/@/views/quantitative/chanlun/api';
import { useUserInfo } from '/@/stores/userInfo';
import { attentionList } from '/@/views/quantitative/chanlunyuan/scripts/api';
import { storeToRefs } from 'pinia';
import { Close, DocumentCopy, Download } from '@element-plus/icons-vue';

// 获取用户信息
const stores = useUserInfo();
const { userInfos } = storeToRefs(stores);

// 接收父组件传递的股票信息
const props = defineProps<{
	symbol?: string;
	period?: string;
}>();

const emit = defineEmits(['change', 'periodChange']);

// 监听父组件传递的股票变化 (已移动到下方定义之后)

// 股票列表数据（模拟）
const stockList = ref([] as any[]);

const getStockList = async () => {
	try {
		// 修改为获取用户关注列表
		const response = await attentionList({ userId: userInfos.value.id });
		const { code, data } = response;
		if (code === 2000 && data) {
			stockList.value = data.map((item: any) => {
				return {
					symbol: item.symbolId,
					name: item.symbolName,
					label: `${item.symbolId} | ${item.symbolName}`,
					value: item.symbolId, // el-select-v2 需要 value
				};
			});
			
			// 如果当前有 symbol，且在列表中，则选中
			if (props.symbol && stockList.value.some(s => s.symbol === props.symbol)) {
				selectedStock.value = props.symbol;
			}
		}
	} catch (error) {
		ElMessage.error('获取关注列表失败');
	}
};

// 选中的值
const selectedStock = ref('');
const isHistoryLoading = ref(false);
const activeNames = ref(['1', '2']);

// 正在分析的股票集合 (key: symbol + resolution)
const analyzingStocks = ref(new Set<string>());

// 计算属性：当前选中的股票是否正在分析
const isCurrentAnalyzing = computed(() => {
	return analyzingStocks.value.has(`${selectedStock.value}_${selectedPeriod.value}`);
});

// 计算属性：当前正在分析的任务总数
const activeAnalysisCount = computed(() => analyzingStocks.value.size);

// 分析按钮是否应该显示加载状态
const isAnalyzing = computed(() => isCurrentAnalyzing.value);

// 请求取消控制器，防止内存泄漏
let abortController: AbortController | null = null;

// 频率选项
const periodOptions = ref([
	{ label: '5分钟', value: '5m' },
	{ label: '30分钟', value: '30m' },
	{ label: '日线', value: '1D' },
]);
const selectedPeriod = ref('1D');

// 频率转换 (AI格式 -> TV格式)
const formatToTVInterval = (p: string) => {
	if (p === '5m') return '5';
	if (p === '30m') return '30';
	return p; // 1D stays 1D
};

// 频率转换 (TV格式 -> AI格式)
const formatFromTVInterval = (i: string) => {
	if (i === '5') return '5m';
	if (i === '30') return '30m';
	if (i === '1D') return '1D';
	return i;
};

// 分析历史记录
const analysisHistory = ref<any[]>([]);

// 详情弹窗
const aiAnalysisDrawerVisible = ref(false);
const analysisStockData = ref<any>(null);

// 归一化股票代码 (处理 SSE/SZ/SH 等后缀差异)
const normalizeSymbol = (s: string) => {
	if (!s) return '';
	// 转大写并处理常见的后缀差异
	let normalized = s.toUpperCase();
	// SSE -> SH, SS -> SH
	normalized = normalized.replace(/\.SSE$/, '.SH').replace(/\.SS$/, '.SH');
	// SZSE -> SZ
	normalized = normalized.replace(/\.SZSE$/, '.SZ');
	return normalized;
};

// 刷新股票列表
const refreshStockList = async () => {
	const currentSelected = selectedStock.value;
	await getStockList();
	// 刷新后如果原来的还在，保持选中；如果不在了，可能需要重新同步 props.symbol
	if (currentSelected && stockList.value.some(s => s.symbol === currentSelected)) {
		selectedStock.value = currentSelected;
	} else if (props.symbol) {
		const normalizedProp = normalizeSymbol(props.symbol);
		const match = stockList.value.find(s => normalizeSymbol(s.symbol) === normalizedProp);
		if (match) selectedStock.value = match.symbol;
	}
};

// 设置选中的股票
const setSelectedStock = (stockCode: string, flag: boolean) => {
	const normalized = normalizeSymbol(stockCode);
	// 尝试在列表中找匹配（归一化对比）
	const match = stockList.value.find(s => normalizeSymbol(s.symbol) === normalized);
	if (match) {
		selectedStock.value = match.symbol;
	} else {
		selectedStock.value = stockCode; // 没找到也先赋值，触发后续加载
	}
	flag && startAnalysis();
};

// 获取历史记录
const fetchHistory = async (symbol?: string, resolution?: string) => {
	try {
		isHistoryLoading.value = true;
		const res = await GetAIHistory({
			symbol: symbol || undefined,
			resolution: resolution || undefined,
		});
		if (res.code === 2000 && res.data) {
			analysisHistory.value = res.data.map((item: any) => {
				// 获取股票名称
				const stock = stockList.value.find((s) => s.symbol === item.symbol);
				return {
					id: item.id,
					stockName: stock ? stock.name : item.symbol || '未知股票', // 兜底显示股票代码或未知
					stockCode: item.symbol,
					resolution: item.resolution,
					status: 'success',
					time: item.create_datetime,
					prompt: item.prompt,
					report: item.report,
					model: item.model || 'deepseek-chat',
					usage: item.usage,
				};
			});
		} else {
			// 即使 code 不是 2000，也要尝试抓取业务错误
			const errorMsg = res.error || res.msg || res.message || res.detail || '数据同步未就绪';
			ElMessage.error(`获取历史失败: ${errorMsg}`);
		}
	} catch (error: any) {
		console.error('获取历史记录失败:', error);
		// 优先从响应体中抓取 error 字段
		const detailMsg = error.response?.data?.error || error.response?.data?.message || error.message || '网络连接异常';
		ElMessage.error(`同步历史异常: ${detailMsg}`);
	} finally {
		isHistoryLoading.value = false;
	}
};

// 删除历史记录
const handleDeleteHistory = (item: any) => {
	if (!item.id) return;

	ElMessageBox.confirm('确定要删除这条分析报告吗?', '提示', {
		confirmButtonText: '确定',
		cancelButtonText: '取消',
		type: 'warning',
	})
		.then(async () => {
			try {
				const res = await DeleteAIHistory({ id: item.id });
				if (res.code === 2000) {
					ElMessage.success('删除成功');
					fetchHistory(selectedStock.value, selectedPeriod.value); // 重新加载过滤列表
				} else {
					const errorMsg = res.error || res.msg || res.message || res.detail || '服务器拒绝请求';
					ElMessage.error(`删除失败: ${errorMsg}`);
				}
			} catch (error: any) {
				console.error('删除分析历史失败:', error);
				const detailMsg = error.response?.data?.error || error.response?.data?.message || error.message || '操作未完成';
				ElMessage.error(`删除报错: ${detailMsg}`);
			}
		})
		.catch(() => {});
};

// 开始分析
const startAnalysis = async () => {
	// 验证选择条件
	if (!selectedStock.value) {
		ElMessage.warning('请选择股票');
		return;
	}

	// 查找对应的股票对象
	const stock = stockList.value.find((s) => s.symbol === selectedStock.value);
	if (!stock) return;

	const analysisKey = `${stock.symbol}_${selectedPeriod.value}`;

	// 验证是否已经在分析中
	if (analyzingStocks.value.has(analysisKey)) {
		ElMessage.warning('该股票正在分析中，请勿重复操作');
		return;
	}

	// 验证并发数
	if (activeAnalysisCount.value >= 5) {
		ElMessage.warning('当前分析任务过多，请等待其他任务完成（最多支持5个并发）');
		return;
	}

	// 加入分析集合
	analyzingStocks.value.add(analysisKey);

	// 立即添加到历史记录，状态为分析中
	const newHistoryItem: Record<string, any> = {
		stockCode: stock.symbol,
		stockName: stock.name,
		resolution: selectedPeriod.value,
		time: new Date().toLocaleString(),
		status: 'analyzing',
		prompt: '',
		report: '',
	};

	analysisHistory.value.unshift(newHistoryItem);

	try {
		const response = await GetAIAnalysis({
			symbol: stock.symbol,
			resolution: selectedPeriod.value
		});

		const resData = response.data || response;

		if ((response.code === 2000 || resData.symbol) && resData.report) {
			newHistoryItem.status = 'success';
			newHistoryItem.prompt = resData.prompt || '';
			newHistoryItem.report = resData.report || '';
			ElMessage.success(`${stock.name} 分析完成`);
			// 更新该项的 ID 以便后续删除操作等
			if (resData.id) newHistoryItem.id = resData.id;
			
			// 如果是当前选中的股票，同步刷新历史记录以更新 ID 等元数据
			if (selectedStock.value === stock.symbol && selectedPeriod.value === newHistoryItem.resolution) {
				fetchHistory(selectedStock.value, selectedPeriod.value);
			}
		} else {
			newHistoryItem.status = 'failed';
			const errorMsg = response.error || response.msg || response.message || resData.detail || 'AI 服务响应为空';
			ElMessage.error(`分析失败: ${errorMsg}`);
		}
	} catch (error: any) {
		newHistoryItem.status = 'failed';
		console.error('AI分析请求失败:', error);
		const detailMsg = error.response?.data?.error || error.response?.data?.message || error.message || 'AI 分析任务由于环境或网络问题中断';
		ElMessage.error(`请求异常: ${detailMsg}`);
	} finally {
		// 从分析集合中移除
		analyzingStocks.value.delete(analysisKey);
	}
};

// 显示详情弹窗
const showDetail = (row: any) => {
	// 判断状态是否成功
	ElMessage.closeAll();
	if (row.status !== 'success') {
		ElMessage.warning('分析未完成，请等待分析完成后查看详情');
		return;
	}
	// 转换股票数据格式以适配抽屉头部和内容展示
	analysisStockData.value = {
		stockCode: row.stockCode,
		stockName: row.stockName,
		symbol: row.stockCode,
		name: row.stockName,
		resolution: row.resolution || '1D',
		time: row.time,
		prompt: row.prompt,
		report: row.report,
		model: row.model,
		usage: row.usage,
		// 以下为扩展模拟数据 (如果后续需要图表展示)
		price: 100 + Math.random() * 200,
		change: (Math.random() - 0.5) * 10,
		changePercent: (Math.random() - 0.5) * 5,
		score: row.score ? Math.round(row.score * 20) : Math.floor(Math.random() * 40) + 60,
		dimensions: {
			fundamental: Math.floor(Math.random() * 40) + 60,
			technical: Math.floor(Math.random() * 40) + 60,
			sentiment: Math.floor(Math.random() * 40) + 60,
			valuation: Math.floor(Math.random() * 40) + 60,
			momentum: Math.floor(Math.random() * 40) + 60,
		},
	};

	// 打开抽屉
	aiAnalysisDrawerVisible.value = true;
};

// 抽屉关闭处理 (改为使用 @closed 回调以提升稳定性)
const handleAnalysisDrawerClose = () => {
	aiAnalysisDrawerVisible.value = false;
};

// 删除历史记录 (本地内存同步，主要逻辑已由 handleDeleteHistory 处理)
const deleteHistory = (index: number) => {
	analysisHistory.value.splice(index, 1);
	ElMessage.success('删除成功');
};

// 复制全部内容
const copyAllContent = () => {
	if (!analysisStockData.value) return;
	const fullContent = `# 数据提示词 (Prompt)\n${analysisStockData.value.prompt}\n\n# 分析结果 (Report)\n${analysisStockData.value.report}`;
	
	copyToClipboard(fullContent);
};

// 兼容性复制函数 (解决非 HTTPS 环境下 navigator.clipboard 不可用的问题)
const copyToClipboard = (text: string) => {
	if (navigator.clipboard && window.isSecureContext) {
		// 优先使用 Clipboard API (需要 HTTPS 或 localhost)
		navigator.clipboard.writeText(text).then(() => {
			ElMessage.success('已复制到剪贴板');
		}).catch(() => {
			// 如果 API 失败，尝试降级
			copyToClipboardFallback(text);
		});
	} else {
		// 非安全上下文或不支持 Clipboard API，直接使用降级方案
		copyToClipboardFallback(text);
	}
};

// 降级复制方案：创建隐藏 textarea 并执行 execCommand('copy')
const copyToClipboardFallback = (text: string) => {
	const textArea = document.createElement("textarea");
	textArea.value = text;
	
	// 确保元素可见但不在视图内，防止页面闪烁或滚动
	textArea.style.position = "fixed";
	textArea.style.left = "-9999px";
	textArea.style.top = "-9999px";
	textArea.style.opacity = "0";
	
	document.body.appendChild(textArea);
	textArea.focus();
	textArea.select();
	
	try {
		const successful = document.execCommand('copy');
		if (successful) {
			ElMessage.success('已复制到剪贴板');
		} else {
			ElMessage.error('复制失败');
		}
	} catch (err) {
		console.error('Fallback copy failed:', err);
		ElMessage.error('复制失败，请手动选择复制');
	}
	
	document.body.removeChild(textArea);
};


// 下载全部内容
const downloadAllContent = () => {
	if (!analysisStockData.value) return;
	const fullContent = `# ${analysisStockData.value.stockName} (${analysisStockData.value.stockCode}) AI分析报告\n\n# 数据提示词 (Prompt)\n${analysisStockData.value.prompt}\n\n# 分析结果 (Report)\n${analysisStockData.value.report}`;
	
	const blob = new Blob([fullContent], { type: 'text/markdown' });
	const url = window.URL.createObjectURL(blob);
	const link = document.createElement('a');
	const dateStr = new Date().toISOString().split('T')[0];
	
	link.href = url;
	link.download = `${analysisStockData.value.stockName}_${analysisStockData.value.stockCode}_AI分析报告_${dateStr}.md`;
	document.body.appendChild(link);
	link.click();
	document.body.removeChild(link);
	window.URL.revokeObjectURL(url);
};


// 获取周期标签 (中文转换)
const getPeriodLabel = (value: string) => {
	const map: Record<string, string> = {
		'5m': '5分钟',
		'15m': '15分钟',
		'30m': '30分钟',
		'60m': '60分钟',
		'1D': '日线',
    '5': '5分钟',
    '15': '15分钟',
    '30': '30分钟',
    '60': '60分钟',
	};
	return map[value] || value;
};



// 简单的 Markdown 格式化处理（持续增强版）
const formatMarkdown = (text: string) => {
	if (!text) return '';

	// 预先处理加粗
	let html = text
		.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/^# (.*?)$/gm, '<h1>$1</h1>')
    .replace(/^## (.*?)$/gm, '<h2>$1</h2>')
    .replace(/^### (.*?)$/gm, '<h3>$1</h3>')
    .replace(/^- (.*?)$/gm, '<li>$1</li>');

	// 处理表格
	if (html.includes('|')) {
		const lines = html.split('\n');
		let inTable = false;
		const processedLines = lines.map((line) => {
      const trimmed = line.trim();
			if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
				const cells = trimmed
					.split('|')
					.filter((c, i, a) => i > 0 && i < a.length - 1)
					.map((c) => {
						const val = c.trim();
						if (val === 'Down') return '<span class="trend-down">下</span>';
						if (val === 'Up') return '<span class="trend-up">上</span>';
						if (val === 'True') return '<span class="status-done">已完成</span>';
						if (val === 'False') return '<span class="status-pending">进行中</span>';
						return val;
					});
        
				// 忽略分隔行 (---)
				if (trimmed.includes('---') || trimmed.includes(':---')) {
					return '';
				}

				let rowHtml = '<tr>' + cells.map((c) => `<td>${c}</td>`).join('') + '</tr>';
				if (!inTable) {
					inTable = true;
					return '<div class="table-container"><table><thead>' + rowHtml.replace(/td>/g, 'th>') + '</thead><tbody>';
				}
				return rowHtml;
			} else {
				if (inTable) {
					inTable = false;
					return '</tbody></table></div>' + line;
				}
				return line;
			}
		});
		html = processedLines.join('\n');
    if (inTable) html += '</tbody></table></div>';
	}

  // 处理换行符：清理冗余空行，防止间距过大
  let unsafeHtml = html
    .replace(/\r/g, '')
    .replace(/\n\s*\n+/g, '\n') // 压缩多个连续换行（包括带空格的空行）
    .replace(/\n/g, '<br>')
    .replace(/([^0-9]):\s*/g, '$1:&nbsp;'); // 仅对非数字前的冒号增加微量间距，避开时间戳

  // 移除块级元素后的冗余换行
  unsafeHtml = unsafeHtml.replace(/(<\/h\d>|<\/div>|<\/tr>|<\/li>|<div.*?>)<br>/g, '$1');

	// 使用DOMPurify过滤，防止XSS攻击
	return DOMPurify.sanitize(unsafeHtml);
};

// 监听父组件传递的股票变化
watch(
	() => props.symbol,
	async (newSymbol) => {
		if (newSymbol) {
			const normalizedNew = normalizeSymbol(newSymbol);
			// 如果新 symbol（归一化后）不在当前列表中，尝试刷新列表
			const exists = stockList.value.some((s) => normalizeSymbol(s.symbol) === normalizedNew);
			if (!exists) {
				await getStockList();
			}
			
			// 再次查找匹配的实际代码
			const match = stockList.value.find((s) => normalizeSymbol(s.symbol) === normalizedNew);
			if (match) {
				selectedStock.value = match.symbol;
			} else {
				selectedStock.value = newSymbol;
			}
		}
	}
);

// 监听本地选择变化，上报给父组件以同步图表
watch(
	() => selectedStock.value,
	(newVal) => {
		if (newVal) {
			emit('change', newVal);
		}
	}
);



// 监听选中的股票及频率变化，联动查询精准历史
watch(
	[() => selectedStock.value, () => selectedPeriod.value],
	([newSymbol, newPeriod]) => {
		fetchHistory(newSymbol, newPeriod);
	}
);

onMounted(async () => {
	await getStockList();
  fetchHistory(selectedStock.value, selectedPeriod.value); // 加载后按当前条件初始化
});

// 组件销毁时取消未完成的请求
onBeforeUnmount(() => {
	if (abortController) {
		abortController.abort();
		abortController = null;
	}
});

defineExpose({
	setSelectedStock,
	refreshStockList,
});
</script>

<style scoped>
.ai-analysis-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #fcfcfd;
}

/* 参数面板美化 */
.analysis-params {
  padding: 10px;
  background: linear-gradient(135deg, #ffffff 0%, #f3f7ff 100%);
  border-radius: 16px;
  border: 1px solid rgba(64, 158, 255, 0.1);
  box-shadow: 0 8px 24px rgba(149, 157, 165, 0.1);
  margin-bottom: 24px;
}

.param-item {
  margin-bottom: 16px;
}

.param-item:last-child {
  margin-bottom: 0;
}

.param-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 8px;
}

.modern-select {
  width: 100%;
}

:deep(.el-select-v2__wrapper), :deep(.el-input__wrapper) {
  border-radius: 8px !important;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02) inset !important;
}

/* 渐变按钮 */
.modern-analysis-btn {
  width: 100%;
  height: 42px;
  border-radius: 12px;
  background: linear-gradient(90deg, #409eff 0%, #36d1dc 100%);
  border: none;
  font-weight: bold;
  letter-spacing: 1px;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.modern-analysis-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
  opacity: 0.9;
}

.count-badge {
  font-size: 12px;
  opacity: 0.8;
  margin-left: 4px;
}

.limit-tip {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 8px;
  text-align: center;
  font-weight: 500;
}

/* 历史卡片美化 */
.history-cards {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  padding-right: 4px;
}

.history-card {
  position: relative;
  display: flex;
  background: white;
  border-radius: 12px;
  border: 1px solid #f1f5f9;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.history-card:hover {
  transform: translateX(4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.card-status-bar {
  width: 4px;
  background: #cbd5e1;
}

.history-card.success .card-status-bar { background: #10b981; }
.history-card.analyzing .card-status-bar { background: #3b82f6; }
.history-card.failed .card-status-bar { background: #ef4444; }

.card-main {
  flex: 1;
  padding: 12px 16px;
}

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2px;
}

.stock-name {
  font-size: 15px;
  font-weight: 700;
  color: #1e293b;
  flex: 1;
}

.delete-icon {
  margin-left: 8px;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.3s;
  padding: 2px;
  border-radius: 4px;
}

.delete-icon:hover {
  color: #ef4444;
  background-color: #fee2e2;
}

.card-code-row {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
}

.card-footer-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #cbd5e1;
}

.dot.success { background: #10b981; box-shadow: 0 0 6px #10b981; }
.dot.analyzing { background: #3b82f6; animation: pulse 1.5s infinite; }
.dot.failed { background: #ef4444; }

.status-text {
  font-size: 11px;
  color: #475569;
}

.time-stamp {
  font-size: 11px;
  color: #94a3b8;
}

@keyframes pulse {
  0% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
  100% { opacity: 1; transform: scale(1); }
}

/* 抽屉头部展示样式 */
.drawer-header-info {
  width: 100%;
}

.header-content-row {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.h-stock-name {
  color: #409eff;
  font-size: 18px;
  font-weight: 700;
}

.h-stock-code {
  color: #1e293b;
  font-weight: 800;
  font-size: 16px;
}

.h-period-tag {
  font-family: monospace;
  padding: 0 6px;
  border-radius: 4px;
}

.h-model-name {
  color: #409eff;
  font-size: 13px;
  font-weight: 500;
  background: rgba(64, 158, 255, 0.05);
  padding: 2px 8px;
  border-radius: 4px;
}

.h-token-usage {
  font-size: 11px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 4px;
}

.token-value {
  color: #64748b;
  font-weight: 600;
}

.h-status-tag {
  border-radius: 4px;
}

.h-time {
  color: #94a3b8;
  font-size: 13px;
  margin-left: auto;
  font-family: tabular-nums;
  padding-right: 10px;
}

.drawer-content-body {
  padding: 0 20px 16px 20px;
}

.drawer-footer {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 16px 20px;
  border-top: 1px solid #f1f5f9;
  background-color: #ffffff;
}

.drawer-footer .el-button {
  padding: 8px 20px;
  font-size: 14px;
}

/* 折叠面板定制 */
.modern-collapse {
  border: none !important;
}

.collapse-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  font-weight: 700;
  color: #334155;
}

/* Markdown 详情区域 */
.markdown-content {
  background: #ffffff;
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  padding: 12px 16px;
  line-height: 1.5;
  color: #334155;
  font-size: 14px;
}

.markdown-content :deep(h1), .markdown-content :deep(h2), .markdown-content :deep(h3) {
  color: #0f172a;
  margin: 12px 0 8px 0;
  font-weight: 800;
  display: block;
}

.markdown-content :deep(h1) { font-size: 17px; border-bottom: 1px solid #f1f5f9; padding-bottom: 4px; margin-top: 12px; }
.markdown-content :deep(h2) { font-size: 15px; margin-top: 10px; }
.markdown-content :deep(h3) { font-size: 14px; margin-top: 8px; }

.markdown-content :deep(strong) {
  color: #1e293b;
  font-weight: 700;
  padding: 0 4px;
  margin: 0 2px;
  background: linear-gradient(transparent 75%, #e0f2fe 25%);
}

.table-container {
  margin: 10px 0;
  overflow-x: auto;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  min-width: 600px;
}

.markdown-content :deep(th) {
  background-color: #f8fafc;
  color: #475569;
  font-weight: 700;
  padding: 8px 12px;
  border-bottom: 2px solid #e2e8f0;
  text-align: left;
}

.markdown-content :deep(td) {
  padding: 6px 12px;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
}

.markdown-content :deep(tr:last-child td) {
  border-bottom: none;
}

.markdown-content :deep(tr:hover td) {
  background-color: #f8fafc;
}

.markdown-content :deep(li) {
  margin-bottom: 4px;
  list-style-type: disc;
  margin-left: 20px;
}

/* 表格内业务数据样式 */
:deep(.trend-down) { color: #ef4444; font-weight: bold; } /* 跌用红 */
:deep(.trend-up) { color: #10b981; font-weight: bold; }   /* 涨用绿 */
:deep(.status-done) { color: #10b981; }
:deep(.status-pending) { color: #f59e0b; }
</style>
