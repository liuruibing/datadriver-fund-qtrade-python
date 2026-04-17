<!--
 * @Description: 交易分析弹窗
 * @Author: 
 * @Date: 2025-12-05 10:25:41
 * @LastEditors: Please set LastEditors
 * @LastEditTime: 2025-12-18 16:43:13
-->
<template>
  <el-dialog
    v-model="dialogVisible"
    title="添加股票"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
    >
      <!-- <el-form-item
        label="选择股票"
        prop="stockCode"
      >
        <el-select-v2
          v-model="formData.stockCode"
          :options="tsCodeList"
          placeholder="请选择"
          filterable
          multiple
          collapse-tags
          collapse-tags-tooltip
          :max-collapse-tags="10"
          clearable
        />
      </el-form-item> -->
      <el-form-item
        label="选择股票"
        prop="stockCode"
      >
        <my-table-selector
          v-model="formData.stockCode"
          :config="config"
          @change="handleChange"
        />
      </el-form-item>
      <el-form-item
        label="备注"
        prop="remark"
      >
        <el-input
          v-model="formData.remark"
          placeholder="请输入备注"
          type="textarea"
          :rows="2"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button
        type="primary"
        @click="handleSubmit"
        :loading="submitLoading"
      >确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import { ElForm } from 'element-plus';
import _ from 'lodash';
import { GetBaseInfo } from '../../chanlun/api';
import MyTableSelector from '/@/components/MyTableSelector/index.vue';

const config = {
	multiple: true, // 单选
	url: '/api/selection/stock-base/',
	params: {
		type: 'ts_code_list',
	},
	columns: [
		{ prop: 'symbol', label: '股票代码', minWidth: 100 },
		{ prop: 'name', label: '股票名称', minWidth: 120 },
		{ prop: 'industry', label: '行业', minWidth: 120 }
	],
	labelKey: 'name',
	valueKey: 'symbol',
	showIndex: false,
	searchMode: 'local',
	searchPlaceholder: '股票代码/股票名称',
	pagination: false,
};

const handleChange = (value: any, options: any) => {
	console.log('选中值:', value);
	console.log('选中选项:', options);
};

onMounted(() => {
	dialogVisible.value = true;
	// getTsCodeList();
});

const props = defineProps<{
	poolId: any;
}>();

const emit = defineEmits<{
	'update:visible': [value: boolean];
	close: [];
}>();

const dialogVisible = ref(false);
const formRef = ref<InstanceType<typeof ElForm>>();
const formData = ref<any>({
	stockCode: [],
	remark: '',
});
const formRules = {
	stockCode: [{ required: true, message: '请选择股票', trigger: 'change' }],
};
const tsCodeList = ref<any[]>([]);

const getTsCodeList = async () => {
	const res = await GetBaseInfo({ type: 'ts_code_list' });
	const { code, data, msg } = res;
	if (code === 2000 && data) {
		let list = data || [];
		tsCodeList.value = list.map((item: any) => ({ value: item.ts_code, label: `${item.ts_code} | ${item.name}` }));
	}
};

const handleClose = () => {
	dialogVisible.value = false;
	emit('close');
};

const submitLoading = ref(false);
const handleSubmit = async () => {
	if (!formRef.value) return;
	const valid = await formRef.value.validate().catch(() => false);
	if (!valid) return;
	submitLoading.value = true;
	const params = {
		poolId: props.poolId,
		stockCode: formData.value.stockCode,
		remark: formData.value.remark,
	};
	console.log(params);
	setTimeout(() => {
		submitLoading.value = false;
		emit('close');
	}, 1000);
};
</script>

<style scoped lang="scss"></style>
