# PyCharm 断点条件：为什么 `fx_a.dt==Timestamp('2026-01-15 15:00:00')` 不生效、以及正确写法

你遇到的现象（“条件断点写了但还是每个分型都停一次”）在 PyCharm 里最常见的原因有两个：

1) **条件表达式在当前作用域里报错**（例如 `Timestamp` 未定义 / `fx_a` 在该行尚未赋值），PyCharm 会把它当成“条件求值失败”，从而仍然中断（并在调试器里提示 *Condition evaluation exception* 之类信息）。
2) **你把断点打在 `fx_a = fxs[0]` 这一行**：PyCharm 在执行该行之前就会先判断条件，此时 `fx_a` 还不存在，条件必然报 `NameError`，导致“每次都停”。

结合你给的代码片段，以上两点都可能发生：

- `czsc/py/analyze.py` 并没有 `from pandas import Timestamp` 或 `import pandas as pd`，所以条件里的 `Timestamp(...)` **很可能 NameError**；
- 若断点位置正好在 `fx_a = fxs[0]`，那么 `fx_a.dt` 也会 **NameError**。

另外还有一个“看起来像不生效”的常见原因：

- `fx_a.dt` 在这个项目里是 `datetime.datetime`（见 `czsc/py/objects.py` 的 `FX.dt: datetime`），而你拿 `pandas.Timestamp` 去比对，类型不同、时区/微秒不同，都可能让 `==` 永远为 False（不过这种情况一般是“永远不停”，不是“每次都停”）。

---

## 1) 正确的断点位置（先保证 `fx_a` 已赋值）

在 `check_bi` 里建议把断点打在 **`fx_a` 已经存在的行**，例如：

- `if fx_a.mark == Mark.D:` 这一行

而不要打在：

- `fx_a = fxs[0]` 这一行（因为条件在执行赋值前求值）

---

## 2) PyCharm 设置“条件断点”的入口

方法 A（最常用）：

1. 在代码左侧 gutter 点一下，打一个普通断点（红点）
2. 右键红点 -> `More` / `Edit Breakpoint...`（不同版本文字略有差异）
3. 在 `Condition` 输入条件表达式
4. 确保没有勾选会导致总是停下来的选项（比如你本意不是要 log-only，但把 suspend 留着也没问题——只要条件能正常返回 False 就不会停）

方法 B（统一管理）：

- `Run` -> `View Breakpoints...`（macOS 常见快捷键 `Cmd+Shift+F8`）
- 在列表里选中对应断点，设置 `Condition` / `Log message` / `Remove` / `Disable`

---

## 3) 推荐的条件写法（不依赖 pandas / 不依赖 import）

### 写法 1：用字符串比较（最稳、最少依赖）

```python
fx_a.dt.strftime("%Y-%m-%d %H:%M:%S") == "2026-01-15 15:00:00"
```

优点：不需要 `Timestamp`、不需要 `datetime` 名字在作用域里存在。

### 写法 2：用 `datetime`（注意要能拿到 `datetime` 名字）

如果你希望用真正的时间对象比较，且当前作用域没有 `datetime`，可以在条件里用 `__import__`：

```python
fx_a.dt == __import__("datetime").datetime(2026, 1, 15, 15, 0, 0)
```

如果你确认当前文件/帧里已经有 `datetime`（例如文件顶部 `from datetime import datetime`），也可以写：

```python
fx_a.dt == datetime(2026, 1, 15, 15, 0, 0)
```

### 写法 3：忽略微秒（避免“明明同一秒但不相等”）

```python
fx_a.dt.replace(microsecond=0) == __import__("datetime").datetime(2026, 1, 15, 15, 0, 0)
```

或范围判断（也能规避时区/微秒干扰）：

```python
dt0 = __import__("datetime").datetime(2026, 1, 15, 15, 0, 0)
fx_a.dt >= dt0 and fx_a.dt < dt0 + __import__("datetime").timedelta(seconds=1)
```

（注意：在断点 Condition 里最好写成一行，或确保 PyCharm 支持多语句；不同版本对多行支持不一致。）

---

## 4) 如何确认“条件到底有没有报错”

当条件表达式里有 `NameError` / `AttributeError` 等异常时，PyCharm 往往会：

- 仍然停在断点处
- 在调试器界面或 Breakpoints 面板里提示类似：
  - `Condition evaluation exception`
  - `NameError: name 'Timestamp' is not defined`

排查建议：

1) 先把条件改成最简单的 `False`，确认不会停（验证你编辑的是正确断点）
2) 再改成 `fx_a is None` 这类不依赖额外名字的表达式，确认条件可被正常求值
3) 最后换成上面推荐的 `strftime(...) == "..."` 或 `__import__("datetime")...` 写法

---

## 5) 针对你这条条件的“最可能正确版本”

如果你想在 `check_bi` 里只在那个底分型停下，最省事的条件通常是：

```python
fx_a.mark.name == "D" and fx_a.dt.strftime("%Y-%m-%d %H:%M:%S") == "2026-01-15 15:00:00"
```

或者（不依赖 `mark.name`，如果 `Mark.D` 也在作用域里可用）：

```python
fx_a.mark == Mark.D and fx_a.dt.strftime("%Y-%m-%d %H:%M:%S") == "2026-01-15 15:00:00"
```

并且断点应打在 `fx_a = fxs[0]` **之后**的行，例如 `if fx_a.mark == Mark.D:`。

