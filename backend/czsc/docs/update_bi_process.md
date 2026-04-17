# `CZSC.__update_bi` 详细过程说明（含“首笔处理 / 成笔 / 延伸回滚”）

本文基于当前仓库代码，对 `CZSC.__update_bi(self)`（`czsc/py/analyze.py`）的执行流程做“逐步、可对照源码”的说明，并解释它为什么会出现“笔会延伸、甚至被撤销重算”的行为。

> 背景：`CZSC.update` 每来一根 `RawBar`，都会先生成/更新无包含K线序列 `self.bars_ubi`，然后调用 `self.__update_bi()` 用 `bars_ubi` 去确认笔并维护 `self.bi_list`。

---

## 0. 相关对象与约定

- `self.bars_raw`: 原始K线序列（`RawBar`）
- `self.bars_ubi`: 无包含K线序列（`NewBar`），用于找分型/笔；作者称“未完成笔的无包含K线序列”
- `self.bi_list`: 已确认的笔列表（`BI`）
- 分型识别：`check_fxs(bars_ubi)` 返回 `FX` 列表（按时间扫描得到）
- 成笔识别：`check_bi(bars_ubi)` 返回 `(bi_or_none, remaining_bars_ubi)`

`__update_bi` 的核心职责是：

1) 尝试在 `self.bars_ubi` 上生成新笔并 append 到 `self.bi_list`
2) 若后续行情“破坏”了最后一笔的端点，则撤销最后一笔并把K线回并进 `self.bars_ubi`，等待下一次 update 重算

---

## 1. 入口检查：无包含K线不足 3 根直接返回

```python
bars_ubi = self.bars_ubi
if len(bars_ubi) < 3:
    return
```

原因：分型/笔都依赖 3K 分型确认（至少需要 3 根无包含K线）。

---

## 2. 分支 A：`self.bi_list` 为空时，走“首笔”特殊处理

### 2.1 先找分型序列；找不到分型直接返回

```python
fxs = check_fxs(bars_ubi)
if not fxs:
    return
```

此时还没任何笔，函数只是在“等待第一笔的起点分型出现”。

### 2.2 选择首笔起点 `fx_a`：在同类分型里取“更极值”的那个

源码逻辑（简化描述）：

1) 先取 `fx_a = fxs[0]`（最早出现的分型）
2) 把所有与 `fx_a` 同类（同为顶/同为底）的分型取出来：`fxs_a`
3) 在 `fxs_a` 里做“极值替换”：
   - 若是底分型：遇到更低的 `fx.low` 就用它替换 `fx_a`
   - 若是顶分型：遇到更高的 `fx.high` 就用它替换 `fx_a`

这一步的直觉含义是：

- 首笔起点尽量用“更极值的同类分型”作为起点，避免从一个不够极值的早期分型开始，导致后续频繁回滚。

### 2.3 把 `bars_ubi` 裁剪到 `fx_a` 的左K开始

```python
bars_ubi = [x for x in bars_ubi if x.dt >= fx_a.elements[0].dt]
```

注意 `fx_a.elements` 是构成分型的三根无包含K线 `[k1, k2, k3]`，这里取的是 `k1.dt`（左K）。

裁剪的含义：

- 首笔开始之前的无包含K线对后续成笔已经没有意义，丢掉以缩短窗口、减少噪声。

### 2.4 调用 `check_bi` 尝试生成第一笔；写回 `self.bars_ubi` 并返回

```python
bi, bars_ubi_ = check_bi(bars_ubi)
if isinstance(bi, BI):
    self.bi_list.append(bi)
self.bars_ubi = bars_ubi_
return
```

重要点：

- 走首笔分支时，函数在这里就 `return` 了；**首笔不会在同一轮里做“破坏回滚检查”**（回滚会在后续 update 的正常分支里发生）。

---

## 3. 分支 B：已有笔时，正常增量更新

当 `self.bi_list` 非空时，流程是：

### 3.1 可选的 verbose 日志

当 `self.verbose` 为 True 且 `bars_ubi` 很长（>100），会输出“未完成笔延伸数量”的日志。这只是观测，不影响逻辑。

### 3.2 先尝试“再生成一笔”

```python
bi, bars_ubi_ = check_bi(bars_ubi)
self.bars_ubi = bars_ubi_
if isinstance(bi, BI):
    self.bi_list.append(bi)
```

这一步做了两件事：

1) 用当前 `bars_ubi` 尝试确认一笔（可能成功也可能失败）
2) 无论成功与否，都把 `bars_ubi` 更新为 `check_bi` 返回的“剩余未成笔K线序列”

其中 `check_bi` 的返回策略是：

- 成笔成功：返回 `bars_b = [x for x in bars if x.dt >= fx_b.elements[0].dt]`（从终点分型的左K起保留，形成与下一轮窗口的重叠）
- 成笔失败：返回原 `bars` 不变

所以从效果上看，`self.bars_ubi` 会呈现：

- 未成笔时逐渐变长
- 一旦成笔就被截断到“终点分型左K附近”，但保留重叠以保证分型识别连续性

---

## 4. “破坏 / 回滚 / 重算窗口回并”：最后一笔端点被突破就撤销

这是 `__update_bi` 最关键、也最容易让人困惑的部分。

### 4.1 触发条件：后续行情突破了最后一笔的极值

源码条件（语义化翻译）：

- 若最后一笔是向上笔（Up），但当前 `bars_ubi` 的最新K线 `bars_ubi[-1].high` **超过了**最后一笔的 `high`  
  => 认为最后一笔终点不再成立，需要撤销
- 若最后一笔是向下笔（Down），但 `bars_ubi[-1].low` **跌破了**最后一笔的 `low`  
  => 同理撤销

注意：这里用的是“最新无包含K线”与“最后一笔的极值”比较，不要求形成新的相反分型。

### 4.2 撤销动作：pop 最后一笔 + 回并 K线窗口

```python
self.bars_ubi = last_bi.bars[:-2] + [x for x in bars_ubi if x.dt >= last_bi.bars[-2].dt]
self.bi_list.pop(-1)
```

拆解为两步：

1) `self.bi_list.pop(-1)`：把最后一笔直接丢弃
2) 重新构造 `self.bars_ubi`：
   - `last_bi.bars[:-2]`：取被撤销那一笔的大部分 bars 放回（丢掉尾部 2 根）
   - 再拼上“当前 bars_ubi 从 `last_bi.bars[-2].dt` 开始的部分”，形成一个带重叠的回退窗口

作者注释强调“必须是 -2，因为最后一根无包含K线有可能是未完成的”，并且承认“这里容易出错，多一根K线就可能导致错误”。

这段逻辑的工程意图是：

- 避免把可能仍在变化的最后一根无包含K线当成稳定历史（因为 `CZSC.update` 支持同一 `dt` 的 bar 被更新）
- 回退时保留一定重叠，确保下一轮 `check_fxs/check_bi` 有足够上下文重新确认分型与端点

### 4.3 为什么回滚后不会立刻重算？

`__update_bi` 在回滚之后没有再次调用 `check_bi`，而是直接结束本轮执行。

因此你在图上可能观察到：

- 先出现一笔
- 后面某根K线创新高/新低后，那笔被撤销（消失或端点变化）
- 再过几根K线（下一轮/多轮 update）后，重新生成一根“更长/不同端点”的笔

---

## 5. `__update_bi` 的“行为特征”总结（帮助你对图形结果建立预期）

1) **首笔起点更偏向极值分型**：首笔在同类分型里先做极值替换，再开始找笔。
2) **成笔后窗口会被截断但保留重叠**：终点分型左K起保留，保证分型识别连续。
3) **最后一笔不是不可变的**：只要后续价格突破它的极值，就会被撤销并回并窗口，等待重算。
4) **“延伸”是通过“撤销重算”实现的**：这会放大 `check_bi` 的端点选择策略对笔长度的影响（特别是当 `check_bi` 倾向于在较长窗口里选极值端点时）。

---

## 6. 我对这套实现的评价（工程角度）

- 优点：在线计算简单、实现成本低；能在趋势延伸时自动修正最后一笔端点，不至于“死板锁死”。
- 风险点：回滚拼接使用 `bars[:-2]` 属于经验性截断，作者自己也提示“容易出错”；在一些边界场景可能出现“多一根K线导致端点变化异常”的问题。
- 结果风格：这套“撤销重算”的延伸方式，会倾向于让最后一笔在延伸段变得更长（尤其当 `check_bi` 在候选里取极值端点时）。

