<template>
  <el-select
    ref="selectRef"
    v-model="selectedLabels"
    :multiple="config.multiple"
    :clearable="config.clearable"
    :collapse-tags="config.collapseTags"
    :collapse-tags-tooltip="(config.collapseTags && selectedLabels.length <= 20)"
    :placeholder="config.placeholder || '请选择'"
    :disabled="config.disabled"
    :filterable="false"
    :remote="false"
    popper-class="my-table-selector-popper"
    @clear="handleClear"
    @visible-change="handleVisibleChange"
    class="my-table-selector"
  >
    <template #empty>
      <div class="selector-content">
        <!-- 搜索框 -->
        <div
          v-if="config.showSearch"
          class="search-wrapper"
        >
          <el-input
            v-model="searchText"
            :placeholder="config.searchPlaceholder || '请输入关键词'"
            clearable
            @input="handleSearch"
            @clear="handleSearch"
          >
            <template #prefix>
              <el-icon>
                <Search />
              </el-icon>
            </template>
          </el-input>
        </div>

        <!-- 表格-支持虚拟滚动 -->
        <vxe-table
          ref="tableRef"
          :data="tableData"
          :loading="loading"
          :max-height="config.tableHeight || 300"
          :virtual-y-config="{ enabled: true, gt: 50 }"
          :checkbox-config="checkboxConfig"
          :radio-config="radioConfig"
          :size="config.size || 'mini'"
          :border="config.border !== false"
          :stripe="config.stripe"
          @checkbox-change="handleCheckboxChange"
          @checkbox-all="handleCheckboxAll"
          @radio-change="handleRadioChange"
          class="selector-table"
        >
          <!-- 多选框 -->
          <vxe-column
            v-if="config.multiple"
            type="checkbox"
            width="45"
            align="center"
          />

          <!-- 单选框 -->
          <vxe-column
            v-else
            type="radio"
            width="45"
            align="center"
          />

          <!-- 序号列 -->
          <vxe-column
            v-if="config.showIndex"
            type="seq"
            title="#"
            width="50"
            align="center"
          />

          <!-- 动态列 -->
          <vxe-column
            v-for="column in config.columns"
            :key="column.prop"
            :field="column.prop"
            :title="column.label"
            :width="column.width"
            :min-width="column.minWidth"
            :align="column.align || 'left'"
            :show-overflow="column.showOverflow !== false"
            :formatter="column.formatter"
          >
            <!-- 自定义插槽 -->
            <template
              v-if="column.slot"
              #default="{ row, rowIndex, column: col }"
            >
              <slot
                :name="column.slot"
                :row="row"
                :row-index="rowIndex"
                :column="col"
              />
            </template>
          </vxe-column>
        </vxe-table>

        <!-- 分页 -->
        <div
          v-if="config.pagination && total > 0"
          class="pagination-wrapper"
        >
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :layout="config.pageLayout || 'total, prev, pager, next'"
            :background="config.pageBackground !== false"
            @current-change="handleCurrentChange"
          />
        </div>

        <!-- 空数据提示 -->
        <!-- <div v-if="!loading && tableData.length === 0" class="empty-wrapper">
          <el-empty style="padding: 0 !important;" :description="config.emptyText || '暂无数据'" />
        </div> -->
      </div>
    </template>
  </el-select>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Search } from '@element-plus/icons-vue';
import { request } from '/@/utils/service';

// 组件配置接口
interface TableColumn {
	prop: string;
	label: string;
	width?: number | string;
	minWidth?: number | string;
	align?: 'left' | 'center' | 'right';
	showOverflow?: boolean;
	formatter?: (params: any) => string;
	slot?: string;
}

interface TableSelectorConfig {
	// 基础配置
	multiple?: boolean; // 是否多选，默认false
	clearable?: boolean; // 是否可清空，默认true
	disabled?: boolean; // 是否禁用，默认false
	placeholder?: string; // 占位符
	collapseTags?: boolean; // 多选时是否折叠标签，默认true

	// 表格配置
	columns: TableColumn[]; // 表格列配置
	tableHeight?: number | string; // 表格最大高度，默认300
	size?: 'large' | 'default' | 'small' | 'mini'; // 表格尺寸，默认small
	border?: boolean; // 是否显示边框，默认true
	stripe?: boolean; // 是否斑马纹，默认false
	showIndex?: boolean; // 是否显示序号列，默认true

	// 数据配置
	url?: string; // 接口地址
	method?: 'get' | 'post'; // 请求方法，默认get
	params?: Record<string, any>; // 额外请求参数
	data?: any[]; // 静态数据，如果提供则不通过接口获取
	dataKey?: string; // 数据字段名，默认'data'
	totalKey?: string; // 总数字段名，默认'total'
	labelKey?: string; // 显示字段名，默认'label'
	valueKey?: string; // 值字段名，默认'value'

	// 搜索配置
	showSearch?: boolean; // 是否显示搜索框，默认true
	searchPlaceholder?: string; // 搜索占位符
	searchMode?: 'remote' | 'local'; // 搜索模式：remote(后端搜索) | local(前端搜索)，默认'remote'
	searchKey?: string; // 搜索字段名，默认'search'
	searchFields?: string[]; // 前端搜索的字段列表，默认搜索所有字段

	// 分页配置
	pagination?: boolean; // 是否分页，默认true
	pageSizes?: number[]; // 每页条数选项，默认[10,20,50,100]
	pageLayout?: string; // 分页布局，默认'total, sizes, prev, pager, next'
	pageBackground?: boolean; // 分页背景，默认true

	// 其他配置
	emptyText?: string; // 空数据提示
	autoLoad?: boolean; // 是否自动加载，默认false
	remoteSearch?: boolean; // 是否远程搜索，默认true（已废弃，请使用 searchMode）
}

// 组件Props
const props = defineProps<{
	modelValue: any[] | any | null;
	config: TableSelectorConfig;
}>();

// 组件Emits
const emit = defineEmits<{
	'update:modelValue': [value: any[] | any | null];
	change: [value: any[] | any | null, options: any[] | any | null];
	clear: [];
	search: [searchText: string];
}>();

// 响应式数据
const selectRef = ref();
const tableRef = ref();
const loading = ref(false);
const searchText = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const tableData = ref<any[]>([]);
const originalData = ref<any[]>([]); // 原始数据，用于前端搜索
const selectedData = ref<any[]>([]);

// 计算属性
const selectedLabels = computed({
	get: () => {
		if (!selectedData.value?.length) return config.value.multiple ? [] : '';

		if (config.value.multiple) {
			return selectedData.value.map((item) => getLabelValue(item, config.value.labelKey));
		} else {
			return getLabelValue(selectedData.value[0], config.value.labelKey);
		}
	},
	set: (value) => {
		if (!value || (Array.isArray(value) && value.length === 0)) {
			// 清空操作
			handleClear();
			return;
		}

		if (config.value.multiple && Array.isArray(value)) {
			// 多选模式：处理tag删除
			// 找出被删除的labels（通过比较当前selectedLabels和新的value）
			const currentLabels = selectedLabels.value || [];
			const newLabels = value;

			// 找到被删除的label
			const deletedLabels = currentLabels.filter((label: any) => !newLabels.includes(label));

			if (deletedLabels.length > 0) {
				// 从selectedData中移除对应的数据项
				const labelKey = config.value.labelKey;
				const deletedItems = selectedData.value.filter((item) => {
					const itemLabel = getLabelValue(item, labelKey);
					return deletedLabels.includes(itemLabel);
				});

				selectedData.value = selectedData.value.filter((item) => {
					const itemLabel = getLabelValue(item, labelKey);
					return !deletedLabels.includes(itemLabel);
				});

				// 更新表格选中状态 - 取消选中被删除的行
				deletedItems.forEach((item) => {
					tableRef.value?.setCheckboxRow(item, false);
				});

				// 更新modelValue
				const valueKey = config.value.valueKey;
				const newValues = selectedData.value.map((item) => getValueValue(item, valueKey));
				emit('update:modelValue', newValues);
				emit('change', newValues, selectedData.value);
			}
		}
	},
});

const config = computed(() => {
	const defaultConfig = {
		multiple: false,
		clearable: true,
		disabled: false,
		collapseTags: true,
		tableHeight: 300,
		size: 'mini' as const,
		border: true,
		stripe: false,
		showIndex: true,
		method: 'get' as const,
		dataKey: 'data',
		totalKey: 'total',
		labelKey: 'label',
		valueKey: 'value',
		showSearch: true,
		searchKey: 'search',
		pagination: true,
		pageSizes: [10, 20, 50, 100],
		pageLayout: 'total, prev, pager, next',
		pageBackground: true,
		emptyText: '暂无数据',
		autoLoad: true,
		remoteSearch: true, // 已废弃
		searchMode: 'remote',
		columns: [],
	};

	return { ...defaultConfig, ...props.config };
});

const checkboxConfig = computed(() => ({
	// checkStrictly: true,
	highlight: true,
	reserve: true,
}));

const radioConfig = computed(() => ({
	highlight: true,
}));

// 工具函数
const getLabelValue = (item: any, key?: string) => {
	if (!item) return '';
	const labelKey = key || config.value.labelKey;
	return item[labelKey] || item;
};

const getValueValue = (item: any, key?: string) => {
	if (!item) return null;
	const valueKey = key || config.value.valueKey;
	return item[valueKey] || item;
};

// 数据处理函数
const processResponseData = (response: any) => {
	const dataKey = config.value.dataKey;
	const totalKey = config.value.totalKey;

	let data = response;
	if (dataKey && response[dataKey] !== undefined) {
		data = response[dataKey];
	}

	if (config.value.pagination && totalKey && response[totalKey] !== undefined) {
		total.value = response[totalKey];
	}

	return Array.isArray(data) ? data : [];
};

// 数据加载函数
const fetchData = async (params: Record<string, any> = {}) => {
	// 如果有静态数据，使用静态数据
	if (config.value.data && config.value.data.length > 0) {
		const staticData = config.value.data;
		tableData.value = [...staticData];
		originalData.value = [...staticData];
		total.value = staticData.length;
		return;
	}

	if (!config.value.url) {
		console.warn('MyTableSelector: 未配置接口地址');
		return;
	}

	loading.value = true;
	try {
		const requestParams = {
			[config.value.searchKey]: searchText.value,
			page: currentPage.value,
			limit: pageSize.value,
			...config.value.params,
			...params,
		};

		const response = await request({
			url: config.value.url,
			method: config.value.method,
			[config.value.method === 'get' ? 'params' : 'data']: requestParams,
		});

		const processedData = processResponseData(response);
		tableData.value = processedData;
		originalData.value = [...processedData]; // 保存原始数据用于前端搜索
	} catch (error) {
		console.error('MyTableSelector: 数据加载失败', error);
		ElMessage.error('数据加载失败');
		tableData.value = [];
	} finally {
		loading.value = false;
	}
};

// 事件处理函数
const handleVisibleChange = async (visible: boolean) => {
	if (visible) {
		if (tableData.value.length === 0) {
			// 搜索框置空
			searchText.value = '';
			await fetchData();
		}
		// 回显选中状态
		await nextTick();
		restoreSelection();
	}
};

const handleSearch = async () => {
	currentPage.value = 1;
	const searchMode = config.value.searchMode || (config.value.remoteSearch ? 'remote' : 'local');

	if (searchMode === 'remote') {
		// 使用 nextTick 确保在当前事件循环完成后执行，避免干扰下拉框状态
		await nextTick();
		await fetchData();
	} else {
		// 前端搜索
		performLocalSearch();
	}
};

// 前端搜索实现
const performLocalSearch = () => {
	if (!searchText.value.trim()) {
		// 搜索文本为空，显示所有数据
		tableData.value = [...originalData.value];
		total.value = originalData.value.length;
		return;
	}

	const searchTerm = searchText.value.toLowerCase().trim();
	const searchFields = config.value.searchFields || [];

	const filteredData = originalData.value.filter((item) => {
		if (searchFields.length > 0) {
			// 指定字段搜索
			return searchFields.some((field) => {
				const value = getNestedValue(item, field);
				return value && value.toString().toLowerCase().includes(searchTerm);
			});
		} else {
			// 全字段搜索
			return Object.values(item).some((value) => {
				return value && value.toString().toLowerCase().includes(searchTerm);
			});
		}
	});

	tableData.value = filteredData;
	total.value = filteredData.length;

	// 前端搜索时重置分页到第一页
	if (config.value.pagination && currentPage.value !== 1) {
		currentPage.value = 1;
	}
};

// 获取嵌套对象的属性值
const getNestedValue = (obj: any, path: string): any => {
	return path.split('.').reduce((current, key) => current?.[key], obj);
};

const handleCheckboxChange = ({ records }: any) => {
	selectedData.value = records;
	updateModelValue();
};

const handleCheckboxAll = ({ records }: any) => {
	selectedData.value = records;
	updateModelValue();
};

const handleRadioChange = ({ row }: any) => {
	selectedData.value = row ? [row] : [];
	updateModelValue();

	// 单选模式下，选择后关闭下拉框
	if (!config.value.multiple && selectRef.value) {
		selectRef.value.blur();
	}
};

const handleClear = () => {
	selectedData.value = [];
	tableRef.value?.clearCheckboxRow();
	tableRef.value?.clearRadioRow();
	emit('update:modelValue', config.value.multiple ? [] : null);
	emit('clear');
};

const handleSizeChange = async (size: number) => {
	pageSize.value = size;
	currentPage.value = 1;
	// 使用 nextTick 确保在当前事件循环完成后执行，避免干扰下拉框状态
	await nextTick();
	await fetchData();
};

const handleCurrentChange = async (page: number) => {
	currentPage.value = page;
	// 使用 nextTick 确保在当前事件循环完成后执行，避免干扰下拉框状态
	await nextTick();
	await fetchData();
};

const updateModelValue = () => {
	let value: any;
	let options: any;

	if (config.value.multiple) {
		value = selectedData.value.map((item) => getValueValue(item));
		options = selectedData.value;
	} else {
		value = selectedData.value.length > 0 ? getValueValue(selectedData.value[0]) : null;
		options = selectedData.value.length > 0 ? selectedData.value[0] : null;
	}

	emit('update:modelValue', value);
	emit('change', value, options);
};

// 恢复选中状态
const restoreSelection = () => {
	if (!props.modelValue) return;

	const modelValue = Array.isArray(props.modelValue) ? props.modelValue : [props.modelValue];

	if (modelValue.length === 0) return;

	// 找到对应的数据项
	const matchedItems = originalData.value.filter((item) => {
		const itemValue = getValueValue(item);
		return modelValue.includes(itemValue);
	});

	selectedData.value = matchedItems;

	// 设置表格选中状态
	if (config.value.multiple) {
		tableRef.value?.setCheckboxRow(matchedItems, true);
	} else if (matchedItems.length > 0) {
		tableRef.value?.setRadioRow(matchedItems[0]);
	}
};

// 监听modelValue变化
watch(
	() => props.modelValue,
	(newValue) => {
		if (!newValue || (Array.isArray(newValue) && newValue.length === 0)) {
			selectedData.value = [];
			return;
		}

		// 如果表格数据已加载，立即恢复选中状态
		if (tableData.value.length > 0) {
			restoreSelection();
		}
	},
	{ immediate: true }
);

// 初始化
onMounted(async () => {
	if (config.value.autoLoad) {
		await fetchData();
		await nextTick();
		restoreSelection();
	}
});

// 暴露方法给父组件
defineExpose({
	fetchData,
	clearSelection: handleClear,
	getSelectedData: () => selectedData.value,
	getTableData: () => tableData.value,
});
</script>

<style lang="scss" scoped>
.my-table-selector {
	width: 100%;
}

.selector-content {
	padding: 10px;
	min-width: 400px;
}

.search-wrapper {
	margin-bottom: 10px;

	.el-input {
		width: 100%;
	}
}

.selector-table {
	:deep(.vxe-table--border) {
		border-radius: 4px;
	}
}

.pagination-wrapper {
	margin-top: 10px;
	display: flex;
	justify-content: center;
}

.empty-wrapper {
	// padding: 20px;
}
</style>

<style lang="scss">
.my-table-selector-popper {
	.el-select-dropdown__wrap {
		max-height: none !important;
	}

	.el-select-dropdown__list {
		padding: 0;
	}
}
</style>
