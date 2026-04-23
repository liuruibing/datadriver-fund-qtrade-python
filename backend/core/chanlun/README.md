# chanlun core 模块说明

这个目录用于承接 chanlun 模块的公共能力，把原先散落在 `backend/ZS_sig.py`、`backend/BS_sig.py`、`backend/dvadmin/selection/views/chanlun.py`、`backend/dvadmin/selection/views/tradingview.py` 里的核心逻辑按职责收口。

目标有两个：

1. 普通 chanlun 接口继续保持原有核心算法口径，核心买卖点和中枢逻辑仍然以 `ZS_sig.py`、`BS_sig.py` 为准。
2. AI 分析能力单独隔离，继续走 `ZS_sig_ai.py`，避免和普通接口算法混在一起。


## 当前算法路由

### 普通 history / TradingView 接口

- 中枢：`core.chanlun.zhongshu`
- 买卖点：`core.chanlun.signals`
- 兼容导出：`backend/ZS_sig.py`
- 信号式买卖点函数：`core.chanlun.bs_signals`
- 兼容导出：`backend/BS_sig.py`

说明：

- `backend/ZS_sig.py` 和 `backend/BS_sig.py` 现在是兼容壳，外部 import 不需要改。
- 真正实现已经迁到了 `backend/core/chanlun/`。
- 普通 `history` 返回的 `mmds` 历史买卖点，当前走的是 `find_B1 / find_B2 / find_B3 / find_S1 / find_S2 / find_S3` 这一套，也就是原 `ZS_sig.py` 的历史点位算法。
- `BS_sig.py` 里的 `cxt_*` 函数是“信号式”算法输出，保留不变，但它不是 TradingView `mmds` 历史点位数组的直接生成器。

### AI 分析接口

- AI 专用算法入口：`core.chanlun.ai_algorithms`
- 实际实现来源：`backend/ZS_sig_ai.py`

说明：

- `ZS_sig_ai.py` 保持单独存在。
- AI 使用的线段、类二买卖点、高周期补充信号等增强逻辑不混入普通 history 接口。


## 各文件含义

### `__init__.py`

包入口说明文件，主要用于标记这是一个独立的 core 模块包。

### `runtime.py`

运行时初始化层。

作用：

- 统一处理本地 `czsc` 路径注入
- 设置 `CZSC_USE_PYTHON`
- 避免每个模块重复写一遍运行时初始化代码

### `utils.py`

基础通用工具函数。

主要包含：

- `dt_to_str`：时间转字符串
- `dt_to_ts`：时间转 TradingView 秒级时间戳
- `normalize_ts_code`：股票代码标准化
- `json_safe`：把 numpy、NaN、datetime 等转成可 JSON 序列化对象
- `get_ts_freq`：czsc 周期到数据库周期映射
- `parse_bool`：布尔参数解析
- `resolution_to_freq`：TradingView resolution 到 `czsc.Freq` 的映射

### `data.py`

数据访问和 K 线清洗层。

主要包含：

- `create_stock_kline_engine`：创建 `stock_kline` 数据库连接
- `read_stock_kline`：读取指定股票和周期 K 线
- `clean_kline_df`：K 线数据清洗
- `aggregate_daily_kline`：日线聚合生成季线/年线
- `aggregate_kline_by_rule`：按 pandas rule 做通用聚合

### `zhongshu.py`

普通缠论中枢主算法。

主要包含：

- `get_zs_seq`
- `check_down_trend`
- `check_up_trend`
- `get_relevant_zss`
- `get_entry_BI`
- `get_next_zs`

来源：

- 从原 `backend/ZS_sig.py` 迁移出来的中枢相关逻辑

### `beichi.py`

背驰判断逻辑。

主要包含：

- `check_beichi`

来源：

- 从原 `backend/ZS_sig.py` 迁移出来

备注：

- 这里保留了已修复的 MACD 参数顺序：`fast=12, slow=26, signal=9`

### `signals.py`

普通历史买卖点主算法。

主要包含：

- `find_B1`
- `find_B2`
- `find_B3`
- `find_S1`
- `find_S2`
- `find_S3`

来源：

- 从原 `backend/ZS_sig.py` 迁移出来的历史买卖点算法

### `bs_signals.py`

信号式买卖点算法。

主要包含：

- `cxt_first_buy_V260101`
- `cxt_first_sell_V260101`
- `cxt_second_bs_V260101`
- `cxt_third_bs_V260101`

来源：

- 从原 `backend/BS_sig.py` 迁移出来

说明：

- 这套函数更偏向“当前信号判断”
- 不是 TradingView `history.mmds` 历史点位数组的直接输出器

### `legacy_utils.py`

兼容历史算法需要的工具函数导出层。

主要作用：

- 统一导出原本分散依赖的 `czsc.utils.sig` 相关函数
- 让 `ZS_sig.py` 兼容壳和迁移后的算法文件都能稳定引用

### `algorithms.py`

普通 chanlun 算法门面层。

主要作用：

- 暴露普通接口使用的稳定入口
- 统一组合 `zhongshu.py`、`signals.py`、`bs_signals.py`

主要包含：

- `calculate_main_bs_points`
- `get_zs_seq`
- `cxt_first_buy_V260101`
- `cxt_first_sell_V260101`
- `cxt_second_bs_V260101`
- `cxt_third_bs_V260101`

### `ai_algorithms.py`

AI 算法门面层。

主要作用：

- 单独桥接 `ZS_sig_ai.py`
- 保持 AI 分析功能独立

### `history_response.py`

TradingView history 返回结构构建器。

主要作用：

- 统一拼装 `t/o/h/l/c/v`
- 统一拼装 `bis`
- 统一拼装 `bi_zss`
- 统一拼装 `mmds`
- 统一简单 fallback 响应

这样 `chanlun.py` 和 `tradingview.py` 就不用各自维护一套相似的 response 组装代码。

### `regression_guard.py`

轻量级回归护栏。

主要作用：

- 校验普通 history 返回结构不变
- 校验关键字段存在
- 校验主算法来源和 AI 算法来源没有串线

当前会检查：

- `core.chanlun.algorithms.get_zs_seq` 来源应为 `core.chanlun.zhongshu`
- `core.chanlun.ai_algorithms.get_zs_seq` 来源应为 `ZS_sig_ai`


## 对外兼容关系

### `backend/ZS_sig.py`

现在是兼容导出层，继续保留旧 import 方式，例如：

```python
from ZS_sig import get_zs_seq, find_B1
```

不会断。

### `backend/BS_sig.py`

现在也是兼容导出层，继续保留旧 import 方式，例如：

```python
from BS_sig import cxt_first_buy_V260101
```

不会断。


## 当前建议

后续继续优化时，优先改 `backend/core/chanlun/` 下的实现，不要再回到根目录大文件里直接堆逻辑。根目录的 `ZS_sig.py`、`BS_sig.py` 更适合作为兼容入口保留。
