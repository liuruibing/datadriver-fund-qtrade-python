<template>
	<el-dialog v-model="dialogVisible" :title="isEdit ? '编辑股票池' : '新增股票池'" width="500px" :close-on-click-modal="false" @close="handleClose">
		<el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
			<el-form-item label="股票池名称" prop="name">
				<el-input v-model="formData.name" placeholder="请输入股票池名称" clearable />
			</el-form-item>
			<el-form-item label="备注" prop="remark">
				<el-input v-model="formData.remark" placeholder="请输入备注" type="textarea" :rows="3" clearable />
			</el-form-item>
		</el-form>

		<template #footer>
			<el-button @click="handleClose">取消</el-button>
			<el-button type="primary" @click="handleSubmit" :loading="submitLoading">
				{{ isEdit ? '保存' : '创建' }}
			</el-button>
		</template>
	</el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick } from 'vue';
import { ElMessage, ElForm } from 'element-plus';

defineOptions({
	name: 'PoolEditDialog',
});

const emit = defineEmits<{
	confirm: [data: { name: string; remark: string }, isEdit: boolean, editId?: number];
}>();

// 类型定义
type PoolType = {
	id?: number;
	name: string;
	remark?: string;
};

type FormData = {
	name: string;
	remark: string;
};

// 响应式数据
const dialogVisible = ref(false);
const submitLoading = ref(false);
const isEdit = ref(false);
const editId = ref<number | undefined>();

// 表单数据
const formData = reactive<FormData>({
	name: '',
	remark: '',
});

// 表单验证规则
const formRules = {
	name: [
		{ required: true, message: '请输入股票池名称', trigger: 'blur' },
		{ min: 1, max: 50, message: '名称长度在 1 到 50 个字符', trigger: 'blur' },
	],
};

// 表单引用
const formRef = ref<InstanceType<typeof ElForm>>();

// 打开弹窗
const open = (pool?: PoolType) => {
	dialogVisible.value = true;
	isEdit.value = !!pool;
	editId.value = pool?.id;

	// 重置表单
	formData.name = pool?.name || '';
	formData.remark = pool?.remark || '';

	nextTick(() => {
		formRef.value?.clearValidate();
	});
};

// 关闭弹窗
const handleClose = () => {
	dialogVisible.value = false;
	// 重置数据
	isEdit.value = false;
	editId.value = undefined;
	formData.name = '';
	formData.remark = '';
};

// 提交表单
const handleSubmit = async () => {
	if (!formRef.value) return;

	const valid = await formRef.value.validate().catch(() => false);
	if (!valid) return;

	submitLoading.value = true;
	try {
		emit('confirm', { ...formData }, isEdit.value, editId.value);
		handleClose();
	} catch (error) {
		console.error('操作失败:', error);
		ElMessage.error(isEdit.value ? '修改失败' : '创建失败');
	} finally {
		submitLoading.value = false;
	}
};

// 暴露方法给父组件
defineExpose({
	open,
});
</script>

<style scoped>
.el-form-item {
	margin-bottom: 20px;
}
</style>
