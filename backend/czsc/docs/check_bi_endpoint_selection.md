# `check_bi` 如何选择笔端点：为什么它倾向于“取极值端点”

本文把 `check_bi(bars: List[NewBar], **kwargs)`（`czsc/py/analyze.py:138`）里“从分型连成笔”的端点选择过程拆开讲清楚，重点解释：

- 起点 `fx_a` 怎么选
- 终点 `fx_b` 怎么从“所有候选分型”里筛出并取极值
- 为什么这会更容易形成“更长的笔”（相对一些库按“最近可成笔端点”递推，会拆成多笔）

---

## 1. 输入与前置：`fxs` 从哪里来

`check_bi` 的输入 `bars` 要求是无包含K线（`NewBar` 列表）。函数首先调用：

- `fxs = check_fxs(bars)`（`czsc/py/analyze.py:145`）

`check_fxs` 会在 `bars` 上用 3K 规则扫描分型（`check_fx`，`czsc/py/analyze.py:80`），得到一个按时间顺序排列的 `FX` 列表 `fxs`。

如果分型少于 2 个，直接返回“没找到笔”：

- `if len(fxs) < 2: return None, bars`（`czsc/py/analyze.py:146-147`）

---

## 2. 起点 `fx_a` 的选择：总是用 `fxs[0]`

`fx_a` 取的是 `fxs` 序列的第一个分型：

- `fx_a = fxs[0]`（`czsc/py/analyze.py:149`）

也就是说，在给定的 `bars` 窗口内，它默认把“最早出现的分型”当作本次尝试成笔的起点。

补充：在 `CZSC.__update_bi` 里，“第一笔”会对 `fx_a` 做一次额外处理：在同类分型里取更极值的那个再开始（`czsc/py/analyze.py:223-229`）。但 **`check_bi` 本身**并没有做“起点极值替换”，就是直接用 `fxs[0]`。

---

## 3. 终点 `fx_b` 的候选集合：只看“相反分型 + 时间在后”

### 3.1 情况 A：起点是底分型（向上笔）

当 `fx_a.mark == Mark.D`（底分型）时：

- `direction = Direction.Up`（`czsc/py/analyze.py:150-151`）
- 候选终点分型集合是：**所有后续顶分型**，并且满足两个条件：
  1) `x.dt > fx_a.dt`：时间在起点之后
  2) `x.fx > fx_a.fx`

代码是：

```python
fxs_b = (x for x in fxs if x.mark == Mark.G and x.dt > fx_a.dt and x.fx > fx_a.fx)
```

（`czsc/py/analyze.py:152`）

注意：对于顶分型 `Mark.G`，`FX.fx` 在 `check_fx` 中被设置为 `high`（`czsc/py/analyze.py:99-101`）；对于底分型 `Mark.D`，`FX.fx` 被设置为 `low`（`czsc/py/analyze.py:103-105`）。所以这里的 `x.fx > fx_a.fx` 实际是：

- `顶分型的 high > 起点底分型的 low`

在正常行情下几乎恒成立（除非出现极端异常数据/跨品种拼接/数据错误）。这意味着：**“候选集合”基本等价于“起点之后出现过的全部顶分型”**，筛选约束很弱。

### 3.2 情况 B：起点是顶分型（向下笔）

当 `fx_a.mark == Mark.G`（顶分型）时：

- `direction = Direction.Down`（`czsc/py/analyze.py:155-156`）
- 候选终点分型集合是：**所有后续底分型**，并且满足：
  1) `x.dt > fx_a.dt`
  2) `x.fx < fx_a.fx`

代码是：

```python
fxs_b = (x for x in fxs if x.mark == Mark.D and x.dt > fx_a.dt and x.fx < fx_a.fx)
```

（`czsc/py/analyze.py:157`）

这里 `x.fx` 对底分型是 `low`，`fx_a.fx` 对顶分型是 `high`，所以 `x.fx < fx_a.fx` 实际是：

- `底分型的 low < 起点顶分型的 high`

同样几乎恒成立，因此候选集合基本等价于“起点之后出现过的全部底分型”。

---

## 4. 终点 `fx_b` 的选取：在候选集合里“取极值”（不是取最近）

这一点是你观察到“长笔”的核心原因：**它不是找“最近一个能成笔的相反分型”，而是在所有候选里直接取极值分型**。

### 4.1 向上笔：取 `high` 最大的顶分型

当起点为底分型时：

- `fx_b = max(fxs_b, key=lambda fx: fx.high, default=None)`（`czsc/py/analyze.py:153`）

含义是：

1) 把“起点之后的所有顶分型”都拿出来
2) 在这些顶分型中，挑 `high` 最大的那个作为终点

所以只要窗口里后面还出现过更高的顶分型，终点就会被推到更后、更高的位置。

### 4.2 向下笔：取 `low` 最小的底分型

当起点为顶分型时：

- `fx_b = min(fxs_b, key=lambda fx: fx.low, default=None)`（`czsc/py/analyze.py:158`）

含义是：

1) 把“起点之后的所有底分型”都拿出来
2) 在这些底分型中，挑 `low` 最小的那个作为终点

窗口里只要出现过更低的底分型，终点就会继续被推后。

### 4.3 候选为空时：本次无法成笔

如果 `fx_b is None`（候选集合为空），则直接：

- `return None, bars`（`czsc/py/analyze.py:163-164`）

这会导致“等更多K线/更多分型出现后再试”。

---

## 5. 端点选定后，笔的 bars 范围与“重叠保留”

终点 `fx_b` 选出来后，`check_bi` 用 `fx_a` 和 `fx_b` 的分型三根K来截取 `bars`：

1) 本笔 bars（`bars_a`）：从起点分型的左K开始，到终点分型的右K结束

- `bars_a = [x for x in bars if fx_a.elements[0].dt <= x.dt <= fx_b.elements[2].dt]`（`czsc/py/analyze.py:166`）

2) 剩余 bars（`bars_b`）：从终点分型的左K开始保留（用于下次继续找笔）

- `bars_b = [x for x in bars if x.dt >= fx_b.elements[0].dt]`（`czsc/py/analyze.py:167`）

这意味着：即使一笔“完成”，也会把终点分型三根K里的前两根时间段保留在 `bars_ubi` 中，形成与下一轮窗口的重叠，便于后续分型识别与（在 `__update_bi` 里）发生突破时撤销回滚重算。

---

## 6. 为什么“取极值端点”会吞掉中间的几笔（直观例子）

假设在某个 `bars` 窗口里，分型序列（按时间）大致如下：

```
D1 (low=10)
G1 (high=12)
D2 (low=11)
G2 (high=15)
D3 (low=13)
G3 (high=14)
```

如果 `fx_a = D1`：

- 候选顶分型是 `{G1, G2, G3}`（基本都会被纳入候选）
- `check_bi` 会取 `high` 最大的顶分型作为终点：`fx_b = G2 (high=15)`

于是这一笔会直接连成：

- `D1 -> G2`

而很多“递推式”的实现更可能先确认：

- `D1 -> G1`（第一笔）
- 再在后续形成 `G1 -> D2`、`D2 -> G2` ...

在本库里，这些中间结构不一定消失（取决于后续 `min_bi_len`、`ab_include`、回滚等门槛），但**端点选择策略本身**就天然倾向于把窗口里的同向波段“压缩成更少的笔”。

---

## 7. 小结：这一步“取极值端点”与你看到的“长笔”之间的关系

- `check_bi` 对终点的选择是“在候选集合里取极值”，而不是“取最近可成笔端点”。  
- 候选集合的过滤条件（`x.fx > fx_a.fx` / `x.fx < fx_a.fx`）在大多数数据上很弱，因此候选集合往往很大。  
- 当窗口变长、候选分型变多时，“取极值”就更容易把终点推到更后，从而产生更长的笔，并吞掉其它库会拆出来的中间几笔结构。

