<template>
  <fs-page>
    <div class="stock-pool-container">
      <!-- 主要内容区域 -->
      <div class="main-content">
        <!-- 左侧股票池列表 -->
        <el-card
          class="left-panel custom-card"
          shadow="never"
        >
          <template #header>
            <div class="panel-header">
              <span>股票池列表</span>
              <div class="panel-actions">
                <el-button
                  type="text"
                  @click="handleRefreshPools"
                  size="small"
                  icon="Refresh"
                > 刷新 </el-button>
                <el-button
                  type="primary"
                  @click="handleAddPool"
                  size="small"
                  icon="Plus"
                > 新增 </el-button>
              </div>
            </div>
          </template>

          <div class="pool-list">
            <div
              v-for="pool in poolList"
              :key="pool.id"
              :class="['pool-item', { active: selectedPool?.id === pool.id }]"
              @click="handleSelectPool(pool)"
            >
              <div class="pool-info">
                <div class="pool-name">{{ pool.name }}</div>
                <div class="pool-count">共 {{ pool.stockCount || 0 }} 只股票</div>
                <div
                  class="pool-remark"
                  v-if="pool.remark"
                >{{ pool.remark }}</div>
              </div>
              <div class="pool-actions">
                <el-button
                  type="text"
                  size="small"
                  @click.stop="handleEditPool(pool)"
                  icon="Edit"
                > 编辑 </el-button>
                <el-button
                  type="text"
                  size="small"
                  @click.stop="handleDeletePool(pool)"
                  style="color: #f56c6c"
                  icon="Delete"
                > 删除 </el-button>
              </div>
            </div>

            <div
              v-if="poolList.length === 0"
              class="empty-state"
            >
              <el-empty
                description="暂无股票池"
                :image-size="80"
              >
                <el-button
                  type="primary"
                  @click="handleAddPool"
                >创建第一个股票池</el-button>
              </el-empty>
            </div>
          </div>
        </el-card>

        <!-- 中间股票数据 -->
        <el-card
          class="middle-panel custom-card"
          shadow="never"
        >
          <template #header>
            <div class="panel-header">
              <span>{{ selectedPool ? `${selectedPool.name} - 股票列表` : '请选择股票池' }}</span>
              <div
                class="panel-actions"
                v-if="selectedPool"
              >
                <el-button
                  type="primary"
                  @click="handleAddStock"
                  size="small"
                  icon="Plus"
                > 添加股票 </el-button>
              </div>
            </div>
          </template>

          <div
            v-if="!selectedPool"
            class="empty-state"
          >
            <el-empty
              description="请先选择左侧的股票池"
              :image-size="80"
            ></el-empty>
          </div>

          <div
            v-else
            class="stock-table"
          >
            <el-table
              ref="stockTableRef"
              :data="stockList"
              style="width: 100%"
              height="calc(100% - 60px)"
              v-loading="stockLoading"
              size="small"
              stripe
            >
              <el-table-column
                type="index"
                label="序号"
                width="60"
              />
              <el-table-column
                prop="stockCode"
                label="股票代码|名称"
                min-width="180"
              >
                <template #default="{ row }">
                  <div style="display: flex; align-items: center; gap: 5px;">
                    <span :title="row.stockCode + ' | ' + row.stockName" style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ row.stockCode }} | {{ row.stockName }}</span>
                    <el-tag v-if="row.riskLevel === '低风险'" style="width: 60px;" type="warning" effect="plain" round size="small">{{ row.riskLevel }}</el-tag>
                    <el-tag v-if="row.riskLevel === '中风险'" style="width: 60px;" type="danger" effect="light" round size="small">{{ row.riskLevel }}</el-tag>
                    <el-tag v-if="row.riskLevel === '高风险'" style="width: 60px;" type="danger" effect="dark" round size="small">{{ row.riskLevel }}</el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column
                prop="score"
                label="评分"
                min-width="150"
              >
                <template #default="{ row }">
                  <span><el-rate v-model="row.score" disabled show-score text-color="#ff9900" score-template="{value}" :colors="['#99A9BF', '#F7BA2A', '#FF9900']" size="small" /></span>
                </template>
              </el-table-column>
              <el-table-column
                prop="remark"
                label="备注"
                min-width="150"
                show-overflow-tooltip
              />
              <el-table-column
                label="操作"
                width="170"
                fixed="right"
              >
                <template #default="scope">
                  <el-button
                    type="text"
                    size="small"
                    style="color: #f56c6c"
                    @click="handleRemoveStock(scope.row)"
                  > 移除 </el-button>
                  <el-button type="text" size="small" @click="handleAIAnalysis(scope.row)" style="color: #409eff;"> AI分析 </el-button>
                </template>
              </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination-container">
              <el-pagination
                :current-page="stockCurrentPage"
                :page-size="stockPageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="stockTotal"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleStockSizeChange"
                @current-change="handleStockCurrentChange"
              />
            </div>

            <div
              v-if="stockList.length === 0 && !stockLoading"
              class="empty-state"
            >
              <el-empty
                description="该股票池暂无股票"
                :image-size="60"
              >
                <el-button
                  type="primary"
                  @click="handleAddStock"
                >添加股票</el-button>
              </el-empty>
            </div>
          </div>
        </el-card>

        <!-- 右侧AI分析 -->
        <el-card
          class="right-panel custom-card"
          shadow="never"
        >
          <template #header>
            <div class="panel-header">
              <span>AI股票分析</span>
              <!-- <div class="panel-actions">
                <el-select
                  v-model="selectedAIModel"
                  placeholder="选择AI模型"
                  size="small"
                  style="width: 120px"
                  @change="handleAIModelChange"
                >
                  <el-option label="GPT-4" value="gpt4" />
                  <el-option label="GPT-3.5" value="gpt35" />
                  <el-option label="Claude" value="claude" />
                  <el-option label="通义千问" value="qwen" />
                  <el-option label="文心一言" value="ernie" />
                </el-select>
                <el-button
                  type="primary"
                  @click="startAIAnalysis"
                  size="small"
                  :loading="analyzing"
                  :disabled="!selectedStock"
                >
                  {{ analyzing ? '分析中...' : '开始分析' }}
                </el-button>
              </div> -->
            </div>
          </template>

          <!-- <AIAnalysisPanel
            ref="aiAnalysisPanelRef"
            :selected-stock="selectedStock"
            :selectedAIModel="selectedAIModel"
            :pool-name="selectedPool?.name"
            @analysis-start="handleAnalysisStart"
            @analysis-complete="handleAnalysisComplete"
            @analysis-error="handleAnalysisError"
          /> -->
          <stockAnalysisAI ref="stockAnalysisAiRef" />
        </el-card>
      </div>
    </div>

    <!-- 股票池编辑弹窗 -->
    <PoolEditDialog
      ref="poolEditDialogRef"
      @confirm="handlePoolEditConfirm"
    />

    <!-- 添加股票弹窗 -->
    <AddStockDialog
      v-if="addStockDialogVisible"
      ref="addStockDialogRef"
      :poolId="selectedPool?.id"
      @close="addStockDialogVisible = false"
      @confirm="handleAddStockConfirm"
    />

    <!-- 创建模拟组合弹窗 -->
    <CreateMnzhDialoge
      ref="createMnzhDialogRef"
      v-if="createMnzhDialogVisible"
      @close="createMnzhDialogVisible = false"
      @confirm="handleCreateConfirm"
    />
  </fs-page>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { GetPoolTypes, addPoolType, updatePoolType, deletePoolType, getPoolStocks, addStockToPool, removeStockFromPool, aiStockAnalysis } from './api';
import CreateMnzhDialoge from './components/createMnzhDialoge.vue';
import PoolEditDialog from './components/poolEditDialog.vue';
import AddStockDialog from './components/addStockDialog.vue';
import AIAnalysisPanel from './components/aiAnalysisPanel.vue';
import StockAnalysis from '/@/views/AI/stock-analysis.vue';
import stockAnalysisAI from '/@/components/stockAnalysisAI/index.vue';

defineOptions({
	name: 'stockPool',
});

// 类型定义
interface PoolType {
	id?: number;
	name: string;
	remark?: string;
	stockCount?: number;
}

interface StockItem {
	id?: number;
	stockCode: string;
	stockName: string;
	remark?: string;
	poolId?: number;
	score?: number;
  riskLevel?: string;
}

// 响应式数据
const poolList = ref<PoolType[]>([]);
const selectedPool = ref<PoolType | null>(null);
const stockList = ref<StockItem[]>([]);
const poolLoading = ref(false);
const stockLoading = ref(false);

// 分页数据
const stockCurrentPage = ref(1);
const stockPageSize = ref(10);
const stockTotal = ref(0);

// 弹窗控制
const createMnzhDialogVisible = ref(false);
const createMnzhDialogRef = ref();
const poolEditDialogRef = ref();
const addStockDialogRef = ref();

// AI分析相关
const selectedStock = ref<StockItem | null>(null);
const selectedAIModel = ref('gpt4');
const analyzing = ref(false);
const aiAnalysisPanelRef = ref();

// AI分析抽屉相关
const aiAnalysisDrawerVisible = ref(false);
const analysisStockData = ref<any>(null);

// 表格高度计算
const tableHeight = computed(() => {
	return 'calc(100% - 70px)';
});

// 获取股票池列表
const fetchPoolList = async () => {
	poolLoading.value = true;
	try {
		// 暂时使用假数据，后续替换为真实API
		poolList.value = [
			{ id: 1, name: '股票池1', remark: '默认股票池', stockCount: 10 },
			{ id: 2, name: '股票池2', remark: '测试股票池', stockCount: 2 },
			{ id: 3, name: '股票池3', remark: '量化选股池', stockCount: 0 },
		];
		if (poolList.value.length > 0) {
			handleSelectPool(poolList.value[0]);
		}
		// const res = await GetPoolTypes({})
		// const { code, data, msg } = res
		// if (code === 2000) {
		//   poolList.value = data || []
		// } else {
		//   ElMessage.error(msg)
		//   poolList.value = []
		// }
	} catch (error) {
		console.error('获取股票池列表失败:', error);
		poolList.value = [];
		ElMessage.error('获取股票池列表失败');
	} finally {
		poolLoading.value = false;
	}
};

// 获取选中股票池的股票列表
const fetchStockList = async (poolId?: number) => {
	if (!poolId) return;

	stockLoading.value = true;
	try {
		// 暂时使用假数据，后续替换为真实API
		const mockData = {
			1: [
				{ id: 1, stockCode: '000001', stockName: '平安银行', remark: '优质银行股', score: 4.5 },
				{ id: 2, stockCode: '000002', stockName: '万科A', remark: '房地产龙头', score: 4.0 },
        { id: 3, stockCode: '000003', stockName: '招商银行', remark: '零售银行', score: 4.0, riskLevel: '低风险' },
        { id: 4, stockCode: '000004', stockName: '兴业银行', remark: '股份制银行', score: 3.5 },
        { id: 5, stockCode: '000005', stockName: '工商银行', remark: '国有银行', score: 4.5 },
        { id: 6, stockCode: '000006', stockName: '农业银行', remark: '国有银行', score: 4.0, riskLevel: '低风险' },
        { id: 7, stockCode: '000007', stockName: '中国银行', remark: '国有银行', score: 3.5, riskLevel: '中风险' },
        { id: 8, stockCode: '000008', stockName: '建设银行', remark: '国有银行', score: 4.5 },
        { id: 9, stockCode: '000009', stockName: '交通银行', remark: '国有银行', score: 3.0, riskLevel: '高风险' },
        { id: 10, stockCode: '000010', stockName: '浦发银行', remark: '股份制银行', score: 3.5 },
			],
			2: [
				{ id: 3, stockCode: '000003', stockName: '招商银行', remark: '零售银行', score: 4.0 },
				{ id: 4, stockCode: '000004', stockName: '兴业银行', remark: '股份制银行', score: 3.5 },
			],
			3: [],
		};

		stockList.value = mockData[poolId as keyof typeof mockData] || [];
		stockTotal.value = stockList.value.length;

		// const res = await getPoolStocks(poolId.toString(), {
		//   page: stockCurrentPage.value,
		//   limit: stockPageSize.value
		// })
		// const { code, data, total: totalCount, msg } = res
		// if (code === 2000) {
		//   stockList.value = data || []
		//   stockTotal.value = totalCount || 0
		// } else {
		//   stockList.value = []
		//   stockTotal.value = 0
		//   ElMessage.error(msg)
		// }
	} catch (error) {
		console.error('获取股票列表失败:', error);
		stockList.value = [];
		stockTotal.value = 0;
		ElMessage.error('获取股票列表失败');
	} finally {
		stockLoading.value = false;
	}
};

// 选择股票池
const handleSelectPool = (pool: PoolType) => {
	selectedPool.value = pool;
	stockCurrentPage.value = 1;
	fetchStockList(pool.id);
};

// 新增股票池
const handleAddPool = () => {
	poolEditDialogRef.value?.open();
};

// 编辑股票池
const handleEditPool = (pool: PoolType) => {
	poolEditDialogRef.value?.open(pool);
};

// 删除股票池
const handleDeletePool = async (pool: PoolType) => {
	try {
		await ElMessageBox.confirm(`确定删除股票池"${pool.name}"吗？删除后不可恢复！`, '提示', {
			confirmButtonText: '确定',
			cancelButtonText: '取消',
			type: 'warning',
		});

		// 暂时使用假删除逻辑
		poolList.value = poolList.value.filter((item) => item.id !== pool.id);
		if (selectedPool.value?.id === pool.id) {
			selectedPool.value = null;
			stockList.value = [];
		}
		ElMessage.success('删除成功');

		// const res = await deletePoolType(pool.id!.toString())
		// const { code, msg } = res
		// if (code === 2000) {
		//   ElMessage.success('删除成功')
		//   fetchPoolList()
		//   if (selectedPool.value?.id === pool.id) {
		//     selectedPool.value = null
		//     stockList.value = []
		//   }
		// } else {
		//   ElMessage.error(msg)
		// }
	} catch (error) {
		if (error !== 'cancel') {
			console.error('删除失败:', error);
			ElMessage.error('删除失败');
		}
	}
};

// 股票池编辑确认
const handlePoolEditConfirm = async (formData: { name: string; remark: string }, isEdit: boolean, editId?: number) => {
	try {
		if (isEdit && editId) {
			// 编辑
			const index = poolList.value.findIndex((item) => item.id === editId);
			if (index !== -1) {
				poolList.value[index] = { ...poolList.value[index], ...formData };
				ElMessage.success('修改成功');
			}
			// const res = await updatePoolType(editId.toString(), formData)
			// const { code, msg } = res
			// if (code === 2000) {
			//   ElMessage.success('修改成功')
			//   fetchPoolList()
			// } else {
			//   ElMessage.error(msg)
			// }
		} else {
			// 新增
			const newId = Math.max(...poolList.value.map((item) => item.id || 0)) + 1;
			poolList.value.push({
				id: newId,
				name: formData.name,
				remark: formData.remark,
				stockCount: 0,
			});
			ElMessage.success('新增成功');
			// const res = await addPoolType(formData)
			// const { code, msg } = res
			// if (code === 2000) {
			//   ElMessage.success('新增成功')
			//   fetchPoolList()
			// } else {
			//   ElMessage.error(msg)
			// }
		}
	} catch (error) {
		console.error('操作失败:', error);
		ElMessage.error(isEdit ? '修改失败' : '新增失败');
	}
};

const addStockDialogVisible = ref(false);
// 添加股票
const handleAddStock = () => {
	if (!selectedPool.value) {
		ElMessage.warning('请先选择股票池');
		return;
	}
	addStockDialogVisible.value = true;
};

// 添加股票确认
const handleAddStockConfirm = async (stockData: { stockCode: string; stockName: string; remark?: string }) => {
	if (!selectedPool.value) return;

	try {
		// 暂时使用假数据新增
		const newId = Math.max(...stockList.value.map((item) => item.id || 0), 0) + 1;
		stockList.value.push({
			id: newId,
			stockCode: stockData.stockCode,
			stockName: stockData.stockName,
			remark: stockData.remark,
			poolId: selectedPool.value.id,
		});

		// 更新股票池的股票数量
		const poolIndex = poolList.value.findIndex((p) => p.id === selectedPool.value!.id);
		if (poolIndex !== -1) {
			poolList.value[poolIndex].stockCount = (poolList.value[poolIndex].stockCount || 0) + 1;
		}

		ElMessage.success('添加成功');

		// const res = await addStockToPool({
		//   poolId: selectedPool.value.id,
		//   ...stockData
		// })
		// const { code, msg } = res
		// if (code === 2000) {
		//   ElMessage.success('添加成功')
		//   fetchStockList(selectedPool.value.id)
		//   fetchPoolList() // 刷新股票池列表以更新数量
		// } else {
		//   ElMessage.error(msg)
		// }
	} catch (error) {
		console.error('添加股票失败:', error);
		ElMessage.error('添加股票失败');
	}
};

// 移除股票
const handleRemoveStock = async (stock: StockItem) => {
	try {
		await ElMessageBox.confirm(`确定从股票池移除"${stock.stockName}(${stock.stockCode})"吗？`, '提示', {
			confirmButtonText: '确定',
			cancelButtonText: '取消',
			type: 'warning',
		});

		// 暂时使用假删除逻辑
		stockList.value = stockList.value.filter((item) => item.id !== stock.id);

		// 更新股票池的股票数量
		if (selectedPool.value) {
			const poolIndex = poolList.value.findIndex((p) => p.id === selectedPool.value!.id);
			if (poolIndex !== -1) {
				poolList.value[poolIndex].stockCount = Math.max((poolList.value[poolIndex].stockCount || 0) - 1, 0);
			}
		}

		ElMessage.success('移除成功');

		// const res = await removeStockFromPool(selectedPool.value!.id!.toString(), stock.id!.toString())
		// const { code, msg } = res
		// if (code === 2000) {
		//   ElMessage.success('移除成功')
		//   fetchStockList(selectedPool.value!.id)
		//   fetchPoolList() // 刷新股票池列表以更新数量
		// } else {
		//   ElMessage.error(msg)
		// }
	} catch (error) {
		if (error !== 'cancel') {
			console.error('移除失败:', error);
			ElMessage.error('移除失败');
		}
	}
};

// 分页相关
const handleStockSizeChange = (size: number) => {
	stockPageSize.value = size;
	stockCurrentPage.value = 1;
	if (selectedPool.value) {
		fetchStockList(selectedPool.value.id);
	}
};

const handleStockCurrentChange = (page: number) => {
	stockCurrentPage.value = page;
	if (selectedPool.value) {
		fetchStockList(selectedPool.value.id);
	}
};

// 刷新股票池列表
const handleRefreshPools = () => {
	fetchPoolList();
};

// 创建模拟组合
const handleCreateSimulationFund = () => {
	if (stockList.value.length === 0) {
		ElMessage.warning('当前股票池没有股票，请先添加股票');
		return;
	}

	createMnzhDialogVisible.value = true;
	nextTick(() => {
		createMnzhDialogRef.value?.open();
	});
};

// 创建模拟组合确认
const handleCreateConfirm = (formData: any) => {
	console.log('创建模拟组合确认:', formData);
	console.log('选中的股票池:', selectedPool.value);
	console.log('股票列表:', stockList.value);

	// 这里可以调用创建模拟组合的API
	// 将选中的股票池和表单数据一起提交
};


// AI分析相关函数
const handleRowClick = (row: StockItem) => {
	selectedStock.value = row;
};

const stockAnalysisAiRef = ref<any>(null);
const handleAIAnalysis = (row: StockItem) => {
	selectedStock.value = row;
  stockAnalysisAiRef.value?.setSelectedStock(row.stockCode, true);
};

const handleAIModelChange = (value: string) => {
	console.log('选择的AI模型:', value);
};

const startAIAnalysis = () => {
	if (aiAnalysisPanelRef.value) {
		aiAnalysisPanelRef.value.startAIAnalysis();
	}
};

const handleAnalysisStart = () => {
	analyzing.value = true;
};

const handleAnalysisComplete = (result: any) => {
	analyzing.value = false;
	console.log('AI分析完成:', result);
};

const handleAnalysisError = (error: string) => {
	analyzing.value = false;
	console.error('AI分析错误:', error);
};



// 生命周期
onMounted(() => {
	fetchPoolList();
});
</script>

<style lang="scss">
.stock-pool-container {
	.left-panel {
		.el-card__body {
			height: calc(100% - 40px);
			.pool-list {
				height: 100%;
			}
		}
	}
	.middle-panel {
		.el-card__body {
			height: calc(100% - 40px);
			.stock-table {
				height: 100%;
			}
		}
	}
	.right-panel {
		.el-card__body {
			height: calc(100% - 40px);
		}
	}
}
</style>

<style scoped lang="scss">
.stock-pool-container {
	padding: 10px;
	background: #f5f5f5;
	height: calc(100vh - 100px);
}

.title-card {
	margin-bottom: 20px;
	background: white;
}

.page-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.page-header h2 {
	margin: 0;
	color: #333;
	font-size: 18px;
	font-weight: 500;
}

.main-content {
	display: flex;
	gap: 10px;
	height: 100%;
}

.left-panel {
	flex: 0 0 320px;
	background: white;
	display: flex;
	flex-direction: column;
}

.middle-panel {
	flex: 1;
	background: white;
	display: flex;
	flex-direction: column;
}

.right-panel {
	width: 300px;
	background: white;
	display: flex;
	flex-direction: column;
}

.panel-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.panel-actions {
	display: flex;
	gap: 8px;
}

.pool-list {
	flex: 1;
	overflow-y: auto;
}

.pool-item {
	padding: 12px 16px;
	margin-bottom: 8px;
	border: 1px solid #e4e7ed;
	border-radius: 6px;
	cursor: pointer;
	transition: all 0.3s ease;
	background: #fafafa;
}

.pool-item:hover {
	border-color: #c0c4cc;
	background: #f5f5f5;
}

.pool-item.active {
	border-color: #409eff;
	background: #ecf5ff;
	box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.pool-item.active:hover {
	background: #e6f7ff;
}

.pool-info {
	margin-bottom: 8px;
}

.pool-name {
	font-size: 14px;
	font-weight: 500;
	color: #303133;
	margin-bottom: 4px;
}

.pool-count {
	font-size: 12px;
	color: #909399;
	margin-bottom: 4px;
}

.pool-remark {
	font-size: 12px;
	color: #c0c4cc;
	line-height: 1.4;
	word-break: break-word;
}

.pool-actions {
	display: flex;
	justify-content: flex-end;
	gap: 8px;
}

.empty-state {
	padding: 40px 20px;
	text-align: center;
}

.pagination-container {
	display: flex;
	justify-content: center;
	padding: 15px;
	border-top: 1px solid #f0f0f0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
	.right-panel {
		flex: 0 0 350px;
	}
}

@media (max-width: 1024px) {
	.main-content {
		flex-direction: column;
		height: auto;
	}

	.left-panel {
		flex: none;
		height: 300px;
	}

	.middle-panel {
		flex: none;
		margin-top: 20px;
		height: 400px;
	}

	.right-panel {
		flex: none;
		margin-top: 20px;
		height: 500px;
	}
}

@media (max-width: 768px) {
	.stock-pool-container {
		padding: 10px;
	}

	.main-content {
		gap: 10px;
	}

	.pool-item {
		padding: 10px 12px;
		margin: 0 12px 6px 12px;
	}

	.panel-header {
		flex-direction: column;
		align-items: flex-start;
		gap: 10px;
	}

	.panel-actions {
		align-self: flex-end;
	}

.right-panel {
	height: 450px;
}
}
</style>
