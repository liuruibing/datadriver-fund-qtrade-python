# 分型生成笔时是否考虑“跳空/缺口”？

结论先说：**当前这套 Python 实现（`czsc/py/analyze.py` 的 `remove_include` / `check_fx` / `check_fxs` / `check_bi`）在“分型→笔”的判定过程中，没有显式引入你描述的“缺口可以弥补K线数量不足”的规则**。成笔门槛主要仍然是“无包含K线根数”与“端点区间不包含”等硬条件。

下面是我逐段对照代码得出的原因。

---

## 1. 数据预处理：去包含并不识别缺口能量

无包含K线序列 `bars_ubi` 的生成发生在 `CZSC.update` 里，通过 `remove_include(k1, k2, k3)` 合并包含关系（`czsc/py/analyze.py:271-285`）。

`remove_include` 的判断逻辑是：

- 只在 `k2` 与 `k3` 存在包含关系时合并（`czsc/py/analyze.py:48` 的高低区间包含判断）
- 合并后的 `high/low/dt` 由趋势方向（Up/Down）与 max/min 组合决定（`czsc/py/analyze.py:50-58`）

**这里完全没有检测 “gap/缺口（上一根 high < 下一根 low 或上一根 low > 下一根 high）” 的分支**，也没有把缺口作为任何“强度/能量”指标写入 `NewBar.cache` 或其它结构中供后续成笔使用。

---

## 2. 分型识别：`check_fx` 只用三根K的高低关系，不关心跳空

分型识别 `check_fx(k1, k2, k3)`（`czsc/py/analyze.py:80-107`）使用的是典型 3K 形态判定：

- 顶：`k1.high < k2.high > k3.high` 且 `k1.low < k2.low > k3.low`
- 底：`k1.low > k2.low < k3.low` 且 `k1.high > k2.high < k3.high`

这套逻辑**不会单独检查 k1 与 k2、k2 与 k3 是否存在缺口**；即使存在明显跳空，它也只会作为 `high/low` 数值的一部分影响分型是否成立，而不会触发“分型能量增强/可放宽根数”的特殊规则。

---

## 3. 成笔判定：`check_bi` 的“根数门槛”只看 `len(bars_a)`，没有缺口豁免

`check_bi(bars)`（`czsc/py/analyze.py:138-178`）成笔的核心门槛是：

1) `ab_include` 必须为 False（端点分型的高低区间不能互相包含；`czsc/py/analyze.py:170-173`）
2) `len(bars_a) >= min_bi_len`（`min_bi_len` 默认 6；`czsc/py/analyze.py:144` 与 `czsc/envs.py:37-40`）

其中 `bars_a` 是按时间截取的无包含K线片段（`czsc/py/analyze.py:166`）。

**这里没有任何类似：**

- “如果顶底分型之间存在缺口，则允许 `len(bars_a)` 小于 `min_bi_len`”
- “如果存在缺口，则最小根数可以降到 4”
- “即使顶底分型之间没有独立K线，只要缺口存在也可成笔”

也就是说，你给出的“新笔定义（缺口宽容）”在当前实现里**没有落地**。

---

## 4. 回滚/延伸机制同样不涉及缺口

`CZSC.__update_bi` 的“破坏→撤销→回并 bars 重算”（`czsc/py/analyze.py:245-253`）触发条件是：

- Up 笔被后续 `bars_ubi[-1].high` 创新高破坏
- Down 笔被后续 `bars_ubi[-1].low` 创新低破坏

它也没有把“缺口”作为加速确认/缩短根数/提前完成/避免回滚的条件。

---

## 5. 对你提到的“新笔缺口宽容”的对照结论

你给的规则要点是：

- 若顶分型与底分型之间存在明显跳空缺口（`prev.high < next.low` 或 `prev.low > next.high`）
- 则缺口能量可弥补根数不足
- 甚至“没有独立K线/只有4根K线”也可成笔

对照本库实现：

- **缺口不会在去包含阶段被标注或保留为单独事件**
- **分型识别不会因为缺口而额外“加权”**
- **成笔门槛不会因为缺口而放宽 `min_bi_len`**

所以严格回答：**目前没有考虑你描述的“跳空豁免成笔”规则。**

---

## 6. 如果要支持该规则，最自然的落点在哪？

仅给一个实现落点建议，便于你后续自行改造（不在本文直接改代码）：

### 6.1 在 `check_bi` 里放宽根数门槛

在判断 `(len(bars_a) >= min_bi_len)` 前，加入“是否存在缺口”的检测，例如：

- 在 `bars_a` 或 `fx_a.elements + fx_b.elements` 覆盖的区间里查找任意相邻两根 `NewBar`：
  - 上跳空：`prev.high < next.low`
  - 下跳空：`prev.low > next.high`

若存在缺口，则允许更小的最小根数（例如降到 4，或你定义的阈值）。

### 6.2 注意：这里的“缺口检测”应基于 RawBar 还是 NewBar？

本库成笔用的是无包含K线（`NewBar`），但 `NewBar` 是合并过的，缺口可能被合并/弱化。

如果你要严格按“原始K线缺口”定义，最好在检测时使用：

- `NewBar.raw_bars`（见 `czsc/py/objects.py` 的 `NewBar.raw_bars` 属性）

否则只在 `NewBar` 上判缺口，可能漏掉某些原始级别缺口。

