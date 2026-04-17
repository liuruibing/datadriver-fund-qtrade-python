<template>
  <div class="example-container">
    <h2>MyTableSelector 使用示例</h2>

    <!-- 单选示例 -->
    <div class="example-section">
      <h3>单选模式</h3>
      <p>选中值: {{ singleValue }}</p>
      <my-table-selector
        v-model="singleValue"
        :config="singleConfig"
        @change="handleSingleChange"
      />
    </div>

    <!-- 多选示例 -->
    <div class="example-section">
      <h3>多选模式</h3>
      <p>选中值: {{ multipleValue }}</p>
      <my-table-selector
        v-model="multipleValue"
        :config="multipleConfig"
        @change="handleMultipleChange"
      />
    </div>

    <!-- 静态数据示例 -->
    <div class="example-section">
      <h3>静态数据（不分页）</h3>
      <p>选中值: {{ staticValue }}</p>
      <my-table-selector
        v-model="staticValue"
        :config="staticConfig"
        @change="handleStaticChange"
      />
    </div>

    <!-- 前端搜索示例 -->
    <div class="example-section">
      <h3>前端搜索（静态数据）</h3>
      <p>选中值: {{ localSearchValue }}</p>
      <my-table-selector
        v-model="localSearchValue"
        :config="localSearchConfig"
        @change="handleLocalSearchChange"
      />
    </div>

    <!-- 自定义列格式化示例 -->
    <div class="example-section">
      <h3>自定义列格式化</h3>
      <p>选中值: {{ formatValue }}</p>
      <my-table-selector
        v-model="formatValue"
        :config="formatConfig"
        @change="handleFormatChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import MyTableSelector from './index.vue'

// 单选示例
const singleValue = ref(null)
const singleConfig = {
  multiple: false, // 单选模式，选择后自动关闭下拉框
  placeholder: '请选择用户',
  url: '/api/mock/users', // 模拟接口
  columns: [
    { prop: 'name', label: '姓名', width: 120 },
    { prop: 'email', label: '邮箱', width: 200 },
    { prop: 'department', label: '部门', width: 150 }
  ],
  labelKey: 'name',
  valueKey: 'id',
  pagination: true,
  showSearch: true
}

const handleSingleChange = (value: any, options: any) => {
  console.log('单选改变:', { value, options })
}

// 多选示例
const multipleValue = ref([])
const multipleConfig = {
  multiple: true,
  collapseTags: true,
  placeholder: '请选择角色',
  url: '/api/mock/roles', // 模拟接口
  columns: [
    { prop: 'roleName', label: '角色名称', width: 150 },
    { prop: 'description', label: '描述', minWidth: 200 },
    { prop: 'level', label: '等级', width: 80 }
  ],
  labelKey: 'roleName',
  valueKey: 'roleId',
  pagination: true,
  showSearch: true
}

const handleMultipleChange = (value: any[], options: any[]) => {
  console.log('多选改变:', { value, options })
}

// 静态数据示例
const staticValue = ref(null)
const staticConfig = {
  multiple: false, // 单选模式，选择后自动关闭下拉框
  pagination: false, // 不分页
  showSearch: false, // 不显示搜索
  columns: [
    { prop: 'name', label: '姓名', width: 120 },
    { prop: 'age', label: '年龄', width: 80 },
    { prop: 'city', label: '城市', width: 120 }
  ],
  labelKey: 'name',
  valueKey: 'id',
  // 静态数据
  data: [
    { id: 1, name: '张三', age: 25, city: '北京' },
    { id: 2, name: '李四', age: 30, city: '上海' },
    { id: 3, name: '王五', age: 28, city: '广州' },
    { id: 4, name: '赵六', age: 32, city: '深圳' },
    { id: 5, name: '孙七', age: 27, city: '杭州' }
  ]
}

const handleStaticChange = (value: any, options: any) => {
  console.log('静态数据改变:', { value, options })
}

// 前端搜索示例
const localSearchValue = ref(null)
const localSearchConfig = {
  multiple: false, // 单选模式，选择后自动关闭下拉框
  pagination: false, // 前端搜索通常不分页
  searchMode: 'local', // 前端搜索
  searchFields: ['name', 'email', 'department'], // 指定搜索字段
  columns: [
    { prop: 'name', label: '姓名', width: 120 },
    { prop: 'email', label: '邮箱', width: 200 },
    { prop: 'department', label: '部门', width: 150 }
  ],
  labelKey: 'name',
  valueKey: 'id',
  data: [
    { id: 1, name: '张三', email: 'zhangsan@company.com', department: '技术部' },
    { id: 2, name: '李四', email: 'lisi@company.com', department: '销售部' },
    { id: 3, name: '王五', email: 'wangwu@company.com', department: '财务部' },
    { id: 4, name: '赵六', email: 'zhaoliu@company.com', department: '人事部' },
    { id: 5, name: '孙七', email: 'sunqi@company.com', department: '技术部' },
    { id: 6, name: '周八', email: 'zhouba@company.com', department: '销售部' }
  ]
}

const handleLocalSearchChange = (value: any, options: any) => {
  console.log('前端搜索数据改变:', { value, options })
}

// 自定义格式化示例
const formatValue = ref(null)
const formatConfig = {
  multiple: false, // 单选模式，选择后自动关闭下拉框
  pagination: false,
  showSearch: false,
  columns: [
    { prop: 'name', label: '姓名', width: 120 },
    { prop: 'status', label: '状态', width: 100, formatter: ({ cellValue }: any) => {
      return cellValue === 1 ? '✅ 启用' : '❌ 禁用'
    }},
    { prop: 'createTime', label: '创建时间', width: 180, formatter: ({ cellValue }: any) => {
      return new Date(cellValue).toLocaleString('zh-CN')
    }},
    { prop: 'score', label: '分数', width: 80, formatter: ({ cellValue }: any) => {
      return `${cellValue}分`
    }}
  ],
  labelKey: 'name',
  valueKey: 'id',
  data: [
    { id: 1, name: '张三', status: 1, createTime: '2024-01-15T10:30:00', score: 95 },
    { id: 2, name: '李四', status: 0, createTime: '2024-02-20T14:20:00', score: 87 },
    { id: 3, name: '王五', status: 1, createTime: '2024-03-10T09:15:00', score: 92 }
  ]
}

const handleFormatChange = (value: any, options: any) => {
  console.log('格式化数据改变:', { value, options })
}
</script>

<style scoped>
.example-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.example-section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.example-section h3 {
  margin: 0 0 15px 0;
  color: #303133;
}

.example-section p {
  margin: 10px 0 15px 0;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-family: monospace;
  color: #606266;
}
</style>
