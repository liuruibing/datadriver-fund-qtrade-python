# `check_bi` 里“窗口能看到多久之后的顶分型？”

你问的“窗口可以看到多久之后的顶分型”，在这个库里其实取决于：`check_bi` 这一轮被喂进去的 `bars`（无包含K线序列）到底覆盖了多长的时间范围。

下面把分析过程讲清楚，并给出一个精确结论：**在一次 `check_bi(bars)` 调用内，`fx_b` 的候选顶分型最多只能来自 `bars` 序列里“倒数第二根”之前（因为分型需要右侧一根确认），而不是无限向后。**

相关代码：

- `check_bi` 选终点：`czsc/py/analyze.py:149-176`
- 分型扫描：`check_fxs`：`czsc/py/analyze.py:126-135`
- 分型定义（3K确认）：`check_fx`：`czsc/py/analyze.py:99-107`
- `bars_ubi` 如何截断/保留：`CZSC.__update_bi` 与 `check_bi` 返回的 `bars_b`（`czsc/py/analyze.py:167`）

---

## 1. “窗口”是什么：`check_bi` 的窗口 = 它拿到的 `bars` 列表

`check_bi` 并不知道“未来”，它只在当前传入的 `bars` 里找分型并连笔：

1) 先用 `fxs = check_fxs(bars)` 扫描分型（`czsc/py/analyze.py:145`）
2) 再在 `fxs` 里找 `fx_a`（起点）和 `fx_b`（终点）（`czsc/py/analyze.py:149-158`）

因此，**它能“看到”的最远顶分型，不是一个固定的 K 数或时间长度，而是由 `bars` 的尾部在哪里决定**。

---

## 2. `fxs` 最远能包含到哪一个分型？（分型确认导致的硬上限）

`check_fxs` 是这样扫分型的（`czsc/py/analyze.py:126-129`）：

- 对每个 `i`，用 `(bars[i-1], bars[i], bars[i+1])` 调用 `check_fx`

这意味着：

- 想识别以 `bars[i]` 为“分型中间K”的分型，必须存在 `bars[i+1]`（右侧一根）来确认
- 因此，在长度为 `N` 的 `bars` 里，`i` 最大只能取到 `N-2`

结论（很关键）：

- **`fxs` 里最后一个可能出现的分型，其中心K最多只能是 `bars[-2]`**  
  等价于：`fx.dt` 最多到 `bars[-2].dt`（分型中心K的时间）

所以在一次 `check_bi(bars)` 调用里：

- “窗口”能看到的最远顶分型（或底分型）——最多是**倒数第二根无包含K线**所对应的分型，而不是 `bars[-1]`。

---

## 3. 那 `fx_b` 最远能被选到哪里？

当起点 `fx_a` 为底分型时（向上笔），代码是：

```python
fxs_b = (x for x in fxs if x.mark == Mark.G and x.dt > fx_a.dt and x.fx > fx_a.fx)
fx_b = max(fxs_b, key=lambda fx: fx.high, default=None)
```

（`czsc/py/analyze.py:152-154`）

这里的 `fx_b` 必然来自 `fxs`，而 `fxs` 的最远分型中心最多到 `bars[-2]`。因此：

- **`fx_b.dt`（终点分型中心的时间）最多到 `bars[-2].dt`**

但注意 `check_bi` 在截取本笔 bars 时，会用到 `fx_b.elements[2].dt`（终点分型右K，`czsc/py/analyze.py:166`）。由于 `fx_b.elements = [k1, k2, k3]`（`check_fx` 构造的三根K），所以：

- `fx_b.elements[2]` 就是 “确认分型的右侧那根K”
- 若 `fx_b` 的中心K是 `bars[-2]`，那么 `fx_b.elements[2]` 正好是 `bars[-1]`

因此同一轮里：

- `fx_b` 作为分型（中心）最远到 `bars[-2]`
- 但这笔的 `bars_a` 截取可以延伸到 `bars[-1]`（因为用的是 `fx_b.elements[2].dt`）

---

## 4. 在 `CZSC` 的在线更新里，“bars 窗口”通常有多长？

上面的结论都是“给定一次 `check_bi(bars)` 调用”。那实际在这个库里谁在喂 `bars`？

在 `CZSC.__update_bi` 中，每次都用当前 `self.bars_ubi` 去调用 `check_bi`（`czsc/py/analyze.py:240`）：

- `bars_ubi` 是“当前未完成笔的无包含K线序列”
- 当一笔被确认时，`check_bi` 返回的 `bars_b` 会被写回 `self.bars_ubi`（`czsc/py/analyze.py:241`）

而 `bars_b` 的定义是（`czsc/py/analyze.py:167`）：

- 从终点分型的左K开始保留：`x.dt >= fx_b.elements[0].dt`

所以在线过程中，“窗口”大致表现为：

1) 未成笔时：`bars_ubi` 会随着新K线不断增长，窗口越来越长
2) 一旦成笔：窗口会被截断到终点分型左K附近（保留重叠），然后继续增长
3) 若触发回滚（突破最后一笔极值）：窗口会被“向前扩展”（把撤销那笔的 bars 大部分并回去），然后继续增长

因此你问“能看到多久之后的顶分型”：

- 在在线更新语境下，它能看到的“之后”就是：**从 `bars_ubi` 起点到当前最新K线为止**（但顶分型中心最多到倒数第二根）
- 没有一个固定的“只看后面 X 根”的上限；窗口会随着行情推进而扩大或被截断/回滚重构

---

## 5. 为什么这会导致“很长的笔”？

把第 2/3/4 节合起来：

- 只要 `bars_ubi` 在某一轮里很长（尤其是在趋势延伸、回滚反复发生时）
- `check_bi` 就会在这一长窗口里收集到大量后续顶分型
- 然后用 `max(high)` 直接挑最高的那个作为 `fx_b`

于是：

- 终点会被推到窗口里“最高顶分型”处（时间也往后推）
- 笔就会显著拉长，并可能吞掉其它实现会拆开的中间结构

---

## 6. 最精确的一句话答案

在一次 `check_bi(bars)` 调用中：

- `fx_b` 能看到（能被选取为终点的）最远顶分型，其分型中心最多只能到 `bars[-2]`（倒数第二根无包含K线），因为分型需要右侧一根确认；但该笔的 bars 截取可以延伸到 `bars[-1]`（作为确认分型的右K）。

在 `CZSC` 的在线更新中：

- `bars` 就是当前的 `bars_ubi`，窗口长度不是常量，会随 update 增长、随成笔截断、随回滚被扩展；所以“能看到多久之后”本质上取决于此刻 `bars_ubi` 覆盖到哪一天/哪一根K线。

