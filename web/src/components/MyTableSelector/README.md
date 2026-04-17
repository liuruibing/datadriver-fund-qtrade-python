# MyTableSelector 下拉表格选择组件

基于 `el-select` 和 `vxe-table` 封装的强大下拉表格选择组件，支持单选、多选、分页、搜索等功能。

## 功能特性

- ✅ 支持单选和多选模式
- ✅ 支持清空选择
- ✅ 编辑时自动回显选中状态
- ✅ 支持分页和不分页
- ✅ 可配置查询接口路径
- ✅ 表头完全可配置
- ✅ v-model 支持自定义 key
- ✅ 内置搜索功能
- ✅ 支持远程和本地搜索
- ✅ 丰富的样式配置

## 基础用法

### 单选模式

```vue
<template>
  <my-table-selector
    v-model="selectedValue"
    :config="config"
    @change="handleChange"
  />
</template>

<script setup>
import { ref } from 'vue'
import MyTableSelector from '@/components/MyTableSelector/index.vue'

const selectedValue = ref(null)

const config = {
  multiple: false, // 单选（选择后自动关闭下拉框）
  url: '/api/users',
  columns: [
    { prop: 'name', label: '姓名', width: 120 },
    { prop: 'email', label: '邮箱', width: 200 },
    { prop: 'department', label: '部门', width: 150 }
  ],
  labelKey: 'name',
  valueKey: 'id'
}

const handleChange = (value, options) => {
  console.log('选中值:', value)
  console.log('选中选项:', options)
}
</script>
```

### 多选模式

```vue
<template>
  <my-table-selector
    v-model="selectedValues"
    :config="config"
    @change="handleChange"
  />
</template>

<script setup>
import { ref } from 'vue'

const selectedValues = ref([])

const config = {
  multiple: true, // 多选
  collapseTags: true,
  url: '/api/roles',
  columns: [
    { prop: 'roleName', label: '角色名称', width: 150 },
    { prop: 'description', label: '描述', minWidth: 200 }
  ],
  labelKey: 'roleName',
  valueKey: 'roleId'
}
</script>
```

## 配置选项

### TableSelectorConfig 接口

```typescript
interface TableSelectorConfig {
  // 基础配置
  multiple?: boolean           // 是否多选，默认 false（单选模式选择后自动关闭下拉框）
  clearable?: boolean          // 是否可清空，默认 true
  disabled?: boolean           // 是否禁用，默认 false
  placeholder?: string         // 占位符
  collapseTags?: boolean       // 多选时是否折叠标签，默认 true

  // 表格配置
  columns: TableColumn[]       // 表格列配置（必需）
  tableHeight?: number | string // 表格最大高度，默认 300
  size?: 'large' | 'default' | 'small' // 表格尺寸，默认 'small'
  border?: boolean             // 是否显示边框，默认 true
  stripe?: boolean             // 是否斑马纹，默认 false
  showIndex?: boolean          // 是否显示序号列，默认 true

  // 数据配置
  url?: string                 // 接口地址
  method?: 'get' | 'post'      // 请求方法，默认 'get'
  params?: Record<string, any> // 额外请求参数
  data?: any[]                 // 静态数据，如果提供则不通过接口获取
  dataKey?: string             // 数据字段名，默认 'data'
  totalKey?: string            // 总数字段名，默认 'total'
  labelKey?: string            // 显示字段名，默认 'label'
  valueKey?: string            // 值字段名，默认 'value'

  // 搜索配置
  showSearch?: boolean         // 是否显示搜索框，默认 true
  searchPlaceholder?: string   // 搜索占位符
  searchMode?: 'remote' | 'local' // 搜索模式：remote(后端搜索) | local(前端搜索)，默认 'remote'
  searchKey?: string           // 搜索字段名，默认 'search'
  searchFields?: string[]      // 前端搜索的字段列表，默认搜索所有字段

  // 分页配置
  pagination?: boolean         // 是否分页，默认 true
  pageSizes?: number[]         // 每页条数选项，默认 [10,20,50,100]
  pageLayout?: string          // 分页布局，默认 'total, sizes, prev, pager, next'
  pageBackground?: boolean     // 分页背景，默认 true

  // 其他配置
  emptyText?: string           // 空数据提示
  autoLoad?: boolean           // 是否自动加载，默认 false
  remoteSearch?: boolean       // 是否远程搜索，默认 true
}
```

### TableColumn 接口

```typescript
interface TableColumn {
  prop: string                    // 字段名（必需）
  label: string                   // 显示标签（必需）
  width?: number | string         // 列宽度
  minWidth?: number | string      // 最小宽度
  align?: 'left' | 'center' | 'right' // 对齐方式，默认 'left'
  showOverflow?: boolean          // 是否显示省略号，默认 true
  formatter?: (params: any) => string // 格式化函数
  slot?: string                   // 自定义插槽名
}
```

## 高级用法

### 自定义列格式化

```javascript
const config = {
  columns: [
    {
      prop: 'status',
      label: '状态',
      width: 100,
      formatter: ({ cellValue }) => {
        return cellValue === 1 ? '启用' : '禁用'
      }
    },
    {
      prop: 'createTime',
      label: '创建时间',
      width: 180,
      formatter: ({ cellValue }) => {
        return new Date(cellValue).toLocaleString()
      }
    }
  ]
}
```

### 自定义插槽

```vue
<template>
  <my-table-selector v-model="value" :config="config">
    <!-- 自定义操作列 -->
    <template #actions="{ row, rowIndex }">
      <el-button size="small" @click="edit(row)">编辑</el-button>
      <el-button size="small" type="danger" @click="delete(row)">删除</el-button>
    </template>
  </my-table-selector>
</template>

<script setup>
const config = {
  columns: [
    { prop: 'name', label: '姓名', width: 120 },
    { prop: 'actions', label: '操作', width: 150, slot: 'actions' }
  ]
}
</script>
```

### 静态数据源

```javascript
const config = {
  pagination: false, // 不分页
  columns: [
    { prop: 'name', label: '姓名', width: 120 },
    { prop: 'age', label: '年龄', width: 80 }
  ],
  data: [ // 静态数据
    { id: 1, name: '张三', age: 25 },
    { id: 2, name: '李四', age: 30 }
  ]
}
```

### 后端搜索配置

```javascript
const config = {
  url: '/api/search',
  searchMode: 'remote', // 后端搜索
  searchKey: 'keyword', // 搜索参数名
  params: { // 额外参数
    type: 'user'
  }
}
```

### 前端搜索配置

```javascript
const config = {
  url: '/api/users',
  searchMode: 'local', // 前端搜索
  searchFields: ['name', 'email'], // 指定搜索字段，默认搜索所有字段
}
```

### 静态数据 + 前端搜索

```javascript
const config = {
  searchMode: 'local', // 前端搜索
  data: [ // 静态数据
    { id: 1, name: '张三', email: 'zhangsan@example.com' },
    { id: 2, name: '李四', email: 'lisi@example.com' }
  ]
}
```

## 事件说明

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | (value, options) | 选择值改变时触发 |
| clear | - | 清空选择时触发 |
| search | (searchText) | 搜索时触发 |

## 方法说明

通过 `ref` 可以调用以下方法：

| 方法名 | 参数 | 返回值 | 说明 |
|--------|------|--------|------|
| fetchData | (params?) | Promise | 重新加载数据 |
| clearSelection | - | - | 清空选择 |
| getSelectedData | - | Array | 获取选中的数据 |
| getTableData | - | Array | 获取表格数据 |

```vue
<template>
  <my-table-selector ref="selectorRef" v-model="value" :config="config" />
  <el-button @click="refresh">刷新</el-button>
</template>

<script setup>
import { ref } from 'vue'

const selectorRef = ref()

const refresh = () => {
  selectorRef.value?.fetchData()
}
</script>
```

## 注意事项

1. `columns` 配置是必需的，至少需要配置一列
2. `labelKey` 和 `valueKey` 用于指定显示字段和值字段
3. 分页模式下，接口需要返回 `total` 字段表示总条数
4. **后端搜索**时会自动添加搜索参数到请求中
5. **前端搜索**时支持指定搜索字段，不指定则搜索所有字段
6. 组件会自动处理选中状态的回显，无需手动设置
7. **单选模式**：选择选项后会自动关闭下拉框，提升用户体验
8. **多选模式**：需要手动点击其他地方或再次点击下拉框来关闭
9. **静态数据**：当提供 `data` 配置时，不需要配置 `url`，组件将使用静态数据
10. **前端搜索**适用于小数据集，后端搜索适用于大数据集
11. **分页操作**：改变每页条数或切换页面时，下拉框会保持打开状态，方便用户继续选择
12. **事件处理**：所有可能触发数据重新加载的操作都使用了异步处理，确保不会意外关闭下拉框
13. **多选tag删除**：支持点击tag叉号删除单个选项，表格选中状态会同步更新

## 常见问题

**Q: 如何实现本地搜索？**

A: 设置 `remoteSearch: false`，监听 `search` 事件自行处理搜索逻辑。

**Q: 如何自定义请求参数？**

A: 使用 `params` 配置项添加额外参数。

**Q: 如何处理大数据量？**

A: 启用分页模式，合理设置 `pageSizes` 和 `tableHeight`。

**Q: 如何自定义样式？**

A: 可以通过 CSS 变量或深度选择器自定义样式。
