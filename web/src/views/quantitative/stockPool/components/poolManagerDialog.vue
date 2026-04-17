<template>
	<el-dialog v-model="dialogVisible" title="股票池管理" width="800px" :close-on-click-modal="false" @close="handleClose">
		<div class="dialog-content">
			<!-- 操作按钮 -->
			<div class="action-buttons">
				<el-button type="primary" @click="handleAdd" icon="Plus" size="small"> 新增 </el-button>
			</div>

			<!-- 股票池类型列表 -->
			<el-table :data="poolTypes" style="width: 100%" height="300" v-loading="loading" size="small" stripe>
				<el-table-column type="index" label="序号" width="60" />
				<el-table-column prop="name" label="股票池名称" min-width="200" show-overflow-tooltip />
				<el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
				<el-table-column label="操作" width="150" fixed="right">
					<template #default="scope">
						<el-button type="text" size="small" @click="handleEdit(scope.row)"> 编辑 </el-button>
						<el-button type="text" size="small" style="color: #f56c6c" @click="handleDelete(scope.row)"> 删除 </el-button>
					</template>
				</el-table-column>
			</el-table>
		</div>

		<!-- 新增/编辑表单弹窗 -->
		<el-dialog v-model="formDialogVisible" :title="isEdit ? '编辑股票池' : '新增股票池'" width="500px" :close-on-click-modal="false">
			<el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px">
				<el-form-item label="池名称" prop="name">
					<el-input v-model="formData.name" placeholder="请输入股票池名称" clearable />
				</el-form-item>
				<el-form-item label="备注" prop="remark">
					<el-input v-model="formData.remark" placeholder="请输入备注" type="textarea" :rows="3" clearable />
				</el-form-item>
			</el-form>

			<template #footer>
				<el-button @click="formDialogVisible = false">取消</el-button>
				<el-button type="primary" @click="handleSubmit" :loading="submitLoading"> 确定 </el-button>
			</template>
		</el-dialog>
	</el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, onMounted } from 'vue';
import { ElMessage, ElMessageBox, ElForm } from 'element-plus';
import { GetPoolTypes, addPoolType, updatePoolType, deletePoolType } from '../api';

defineOptions({
	name: 'PoolManagerDialog',
});

const emit = defineEmits<{
	close: [];
}>();

// 定义类型
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
const formDialogVisible = ref(false);
const loading = ref(false);
const submitLoading = ref(false);
const isEdit = ref(false);
const poolTypes = ref<PoolType[]>([]);
const currentEditId = ref<number | undefined>();

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

onMounted(() => {
	dialogVisible.value = true;
	fetchPoolTypes();
});

// 获取股票池类型列表
const fetchPoolTypes = async () => {
	loading.value = true;
	try {
		// 暂时使用假数据，后续替换为真实API
		poolTypes.value = [
			{ id: 1, name: '股票池1', remark: '默认股票池' },
			{ id: 2, name: '股票池2', remark: '测试股票池' },
			{ id: 3, name: '股票池3', remark: '量化选股池' },
		];
		// const res = await GetPoolTypes({})
		// const { code, data, msg } = res
		// if (code === 2000) {
		//   poolTypes.value = data || []
		// } else {
		//   ElMessage.error(msg)
		//   poolTypes.value = []
		// }
	} catch (error) {
		console.error('获取股票池类型失败:', error);
		poolTypes.value = [];
		ElMessage.error('获取数据失败');
	} finally {
		loading.value = false;
	}
};

// 新增
const handleAdd = () => {
	isEdit.value = false;
	currentEditId.value = undefined;
	formData.name = '';
	formData.remark = '';
	formDialogVisible.value = true;
	nextTick(() => {
		formRef.value?.clearValidate();
	});
};

// 编辑
const handleEdit = (row: PoolType) => {
	isEdit.value = true;
	currentEditId.value = row.id;
	formData.name = row.name;
	formData.remark = row.remark || '';
	formDialogVisible.value = true;
	nextTick(() => {
		formRef.value?.clearValidate();
	});
};

// 删除
const handleDelete = async (row: PoolType) => {
	try {
		await ElMessageBox.confirm(`确定删除股票池"${row.name}"吗？删除后不可恢复！`, '提示', {
			confirmButtonText: '确定',
			cancelButtonText: '取消',
			type: 'warning',
		});

		// 暂时使用假删除逻辑
		poolTypes.value = poolTypes.value.filter((item) => item.id !== row.id);
		ElMessage.success('删除成功');
		// const res = await deletePoolType(row.id!.toString())
		// const { code, msg } = res
		// if (code === 2000) {
		//   ElMessage.success('删除成功')
		//   fetchPoolTypes()
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

// 提交表单
const handleSubmit = async () => {
	if (!formRef.value) return;

	const valid = await formRef.value.validate().catch(() => false);
	if (!valid) return;

	submitLoading.value = true;
	try {
		if (isEdit.value) {
			// 编辑
			// const res = await updatePoolType(currentEditId.value!.toString(), formData)
			// const { code, msg } = res
			// if (code === 2000) {
			//   ElMessage.success('修改成功')
			//   formDialogVisible.value = false
			//   fetchPoolTypes()
			// } else {
			//   ElMessage.error(msg)
			// }

			// 暂时使用假数据更新
			const index = poolTypes.value.findIndex((item) => item.id === currentEditId.value);
			if (index !== -1) {
				poolTypes.value[index] = { ...poolTypes.value[index], ...formData };
				ElMessage.success('修改成功');
				formDialogVisible.value = false;
			}
		} else {
			// 新增
			// const res = await addPoolType(formData)
			// const { code, msg } = res
			// if (code === 2000) {
			//   ElMessage.success('新增成功')
			//   formDialogVisible.value = false
			//   fetchPoolTypes()
			// } else {
			//   ElMessage.error(msg)
			// }

			// 暂时使用假数据新增
			const newId = Math.max(...poolTypes.value.map((item) => item.id || 0)) + 1;
			poolTypes.value.push({
				id: newId,
				name: formData.name,
				remark: formData.remark,
			});
			ElMessage.success('新增成功');
			formDialogVisible.value = false;
		}
	} catch (error) {
		console.error('操作失败:', error);
		ElMessage.error(isEdit.value ? '修改失败' : '新增失败');
	} finally {
		submitLoading.value = false;
	}
};

// 关闭弹窗
const handleClose = () => {
	emit('close');
};
</script>

<style scoped>
.dialog-content {
	padding: 10px 0;
}

.action-buttons {
	margin-bottom: 15px;
	text-align: right;
}

.action-buttons .el-button {
	margin-right: 10px;
}
</style>
