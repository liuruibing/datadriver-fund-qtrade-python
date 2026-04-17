<!--
 * @Description: 交易分析弹窗
 * @Author: 
 * @Date: 2025-12-05 10:25:41
 * @LastEditors: Please set LastEditors
 * @LastEditTime: 2025-12-11 09:44:14
-->
<template>
	<el-dialog v-model="dialogVisible" title="添加股票" width="600px" :close-on-click-modal="false" @close="handleClose">
		<el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
			<el-form-item label="股票代码|名称" prop="stockCode">
				<div style="display: flex; align-items: center; width: 100%">
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
					<!-- <el-button
            type="primary"
            plain
          >从股票池选择</el-button> -->
				</div>
			</el-form-item>
		</el-form>
		<template #footer>
			<el-button @click="handleClose">取消</el-button>
			<el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
		</template>
	</el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import { ElForm } from 'element-plus';
import _ from 'lodash';
import { GetBaseInfo } from '../../chanlun/api';
import { GetDictionaryById } from '/@/api/common';

onMounted(() => {
	dialogVisible.value = true;
	getTsCodeList();
	getDictionary();
});

const getDictionary = async () => {
	const res = await GetDictionaryById(50);
};

const emit = defineEmits<{
	'update:visible': [value: boolean];
	close: [];
}>();

const dialogVisible = ref(false);
const formRef = ref<InstanceType<typeof ElForm>>();
const formData = ref<any>({
	stockCode: [],
});
const formRules = {
	stockCode: [{ required: true, message: '请选择', trigger: 'change' }],
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
	setTimeout(() => {
		submitLoading.value = false;
		emit('close');
	}, 1000);
};
</script>

<style scoped lang="scss"></style>
