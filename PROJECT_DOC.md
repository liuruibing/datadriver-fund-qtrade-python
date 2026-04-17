# DataDriver Fund QTrade Python - 量化交易平台

## 项目概述

本项目是一套基于 **Django + Vue3** 的量化交易管理系统，采用前后端分离架构。项目基于 dvadmin3 开源框架进行二次开发，专注于股票量化交易领域，支持选股、择时、回测、缠论分析等功能。

## 技术架构

### 后端技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Django | 4.2.14 | Python Web 框架 |
| Django REST Framework | 3.15.2 | RESTful API 框架 |
| Channels | 4.1.0 | WebSocket 支持 |
| Celery | - | 异步任务队列 |
| MySQL | - | 主数据库 |
| Redis | - | 缓存与消息队列 |

### 前端技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | 3.4.38 | 渐进式前端框架 |
| TypeScript | 4.9.4 | JavaScript 超集 |
| Element Plus | 2.8.0 | UI 组件库 |
| Vite | 5.4.1 | 构建工具 |
| Pinia | 2.0.28 | 状态管理 |
| Fast-Crud | 1.21.2 | CRUD 快速开发 |

### 数据分析与量化库

- **czsc**: 缠中说禅技术分析工具
- **tushare**: 金融数据接口
- **pandas/numpy**: 数据处理
- **scikit-learn**: 机器学习
- **TA-Lib/pandas-ta**: 技术指标
- **backtesting**: 回测框架

## 项目结构

```
datadriver-fund-qtrade-python/
├── backend/                    # Django 后端
│   ├── application/           # 应用配置
│   │   ├── settings.py        # Django 配置
│   │   ├── asgi.py            # ASGI 配置
│   │   ├── celery.py          # Celery 配置
│   │   ├── sse_views.py       # SSE 视图
│   │   └── ws_routing.py      # WebSocket 路由
│   ├── conf/                  # 项目配置
│   │   └── env.py             # 环境变量配置
│   ├── dvadmin/               # 核心业务模块
│   │   ├── system/            # 系统管理模块
│   │   │   ├── models.py      # 系统模型
│   │   │   ├── views/        # 视图接口
│   │   │   └── urls.py        # 路由配置
│   │   ├── selection/         # 量化选股模块
│   │   │   ├── models.py      # 数据模型
│   │   │   ├── views/        # 视图接口
│   │   │   ├── tasks.py      # 异步任务
│   │   │   └── urls.py       # 路由配置
│   │   └── utils/             # 工具函数
│   ├── czsc/                  # 缠论分析库
│   ├── plugins/               # 插件目录
│   ├── static/                # 静态资源
│   ├── templates/             # 模板文件
│   ├── requirements.txt      # Python 依赖
│   ├── main.py               # 主入口
│   ├── run.sh                # Linux 启动脚本
│   └── run_start.sh          # 生产环境启动脚本
│
├── web/                       # Vue3 前端
│   ├── src/
│   │   ├── api/              # API 接口
│   │   ├── components/       # 公共组件
│   │   ├── layout/           # 布局组件
│   │   ├── router/           # 路由配置
│   │   ├── stores/           # Pinia 状态
│   │   ├── utils/            # 工具函数
│   │   ├── views/            # 页面视图
│   │   │   ├── system/       # 系统管理页面
│   │   │   ├── quantitative/ # 量化交易页面
│   │   │   │   ├── backtest/      # 回测分析
│   │   │   │   ├── chanlun/       # 缠论分析
│   │   │   │   ├── firmBargain/   # 固收交易
│   │   │   │   ├── simulationFund/# 模拟基金
│   │   │   │   ├── stockList/     # 股票列表
│   │   │   │   └── stockPool/     # 股票池
│   │   │   └── AI/            # AI 分析页面
│   │   ├── i18n/             # 国际化
│   │   └── theme/            # 主题配置
│   ├── package.json          # NPM 依赖
│   ├── vite.config.ts        # Vite 配置
│   └── tsconfig.json         # TS 配置
│
├── docker-compose.yml         # Docker 编排
├── init.sh                    # 初始化脚本
└── README.md                  # 项目说明
```

## 核心功能模块

### 1. 系统管理 (dvadmin/system)

- **用户管理**: 用户增删改查、权限分配
- **角色管理**: 角色权限控制
- **部门管理**: 组织架构管理
- **菜单管理**: 动态菜单配置
- **API 白名单**: 接口访问控制
- **操作日志**: 系统操作记录
- **登录日志**: 登录历史追踪

### 2. 量化选股 (dvadmin/selection)

#### 数据模型

| 模型名 | 说明 |
|--------|------|
| StockBasic | 股票基本信息 |
| DailyMarket | 每日行情数据 |
| DailyBasic | 每日指标数据 |
| Top10Floatholders | 十大流通股东 |
| SwIndustry | 申万行业分类 |
| IdxTa | 指数技术指标 |
| StockAnalysis | 股票分析结果 |
| UserStockWatch | 用户关注股票 |

#### 功能视图

- **base_data**: 基础数据管理
- **stock_selection**: 股票筛选
- **tangle**: 缠论分析
- **chanlun**: 缠中说禅
- **backtest**: 回测分析
- **tradingview**: 行情图表

### 3. 量化分析功能 (前端)

| 模块 | 功能描述 |
|------|----------|
| 股票列表 | 股票行情浏览、筛选 |
| 股票池 | 自选股票池管理 |
| 缠论分析 | 笔、线段、中枢分析 |
| 回测分析 | 策略回测与绩效评估 |
| 模拟基金 | 模拟盘管理 |
| 固收交易 | 固定收益交易 |

## 数据库配置

```python
# backend/conf/env.py

# MySQL 配置
DATABASE_ENGINE = "django.db.backends.mysql"
DATABASE_NAME = 'django-vue3-admin'
DATABASE_HOST = '192.168.1.207'
DATABASE_PORT = 3306
DATABASE_USER = "datadriver"
DATABASE_PASSWORD = 'datadriver'

# Redis 配置
REDIS_HOST = '192.168.1.206'
REDIS_PASSWORD = 'datadriver'
REDIS_DB = 11
CELERY_BROKER_DB = 12
```

## 环境搭建

### 后端

```bash
# 1. 创建虚拟环境
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据库
python manage.py migrate

# 4. 初始化数据
python manage.py init

# 5. 启动服务
python manage.py runserver 0.0.0.0:8000

# 或使用启动脚本
bash run.sh
```

### 前端

```bash
# 1. 安装依赖
cd web
npm install

# 2. 开发模式
npm run dev

# 3. 构建生产版本
npm run build
```

### Docker 部署

```bash
# 使用 docker-compose 启动
docker-compose up -d
```

## API 接口概览

### 系统管理

- `/api/system/user/` - 用户管理
- `/api/system/role/` - 角色管理
- `/api/system/dept/` - 部门管理
- `/api/system/menu/` - 菜单管理
- `/api/system/login/` - 登录接口
- `/api/system/log/` - 日志接口

### 量化选股

- `/api/selection/stock/` - 股票数据
- `/api/selection/analysis/` - 股票分析
- `/api/selection/backtest/` - 回测接口
- `/api/selection/chanlun/` - 缠论接口

## 主要特性

1. **前后端分离**: 完全分离的开发模式，前端 SPA 应用
2. **RBAC 权限**: 基于角色的权限控制，精确到按钮级别
3. **动态菜单**: 支持动态配置菜单和权限
4. **WebSocket**: 支持实时行情推送
5. **SSE**: 支持服务器推送事件
6. **异步任务**: Celery 处理耗时任务
7. **数据可视化**: ECharts 图表展示

## 目录说明

| 目录 | 用途 |
|------|------|
| backend/application | Django 应用配置 |
| backend/dvadmin | 业务逻辑模块 |
| backend/czsc | 缠论分析库 |
| web/src/views/quantitative | 量化交易前端页面 |
| backend/logs | 日志文件目录 |

## 依赖版本

### 核心依赖

```
Django==4.2.14
djangorestframework==3.15.2
django-cors-headers==4.4.0
djangorestframework_simplejwt==5.4.0
channels==4.1.0
django-celery-beat
```

### 数据处理

```
pandas
numpy
scikit-learn
tushare
pandas-ta
matplotlib
seaborn
```

### 量化相关

```
czsc (缠中说禅)
rs_czsc
ccxt (交易所接口)
pyecharts
lightweight-charts
lightgbm
optuna
```

## 注意事项

1. 数据库使用 MySQL，需提前创建数据库
2. Redis 用于缓存和 Celery 消息队列
3. 前端开发需要 Node.js >= 16.0.0
4. 生产环境建议使用 Gunicorn + Nginx 部署
5. 缠论分析依赖 czsc 库，需正确安装

## 许可证

MIT License - 详见 LICENSE 文件