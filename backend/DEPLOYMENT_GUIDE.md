# CZSC 后端部署脚本 (`deploy_demo.sh`) 执行逻辑说明文档

本文档详细说明了 `backend/deploy_demo.sh` 脚本的执行流程和核心逻辑，旨在帮助开发者理解自动化部署过程。

---

## 脚本设计原则
- **安全性**：使用 `set -e`，任何一步执行失败都会立即停止脚本。
- **独立性**：通过 Python 虚拟环境（Virtual Environment）隔离依赖，避免污染全局环境。
- **本地化**：强制安装项目目录下的 `czsc` 修改版，而非从远程 PyPI 下载。

---

## 执行步骤详解

### 1. 环境检查 (Environment Check)
- **目标**：确保系统中存在指定的 Python 版本。
- **逻辑**：
  - 检查变量 `PYTHON_BIN`（当前设定为 `python3.12`）是否在系统 PATH 中。
  - 如果找不到 Python 3.12，脚本将打印错误并异常退出。
  - 打印当前使用的 Python 版本号。

### 2. 虚拟环境初始化 (VENV Setup)
- **目标**：建立隔离的 Python 运行环境。
- **逻辑**：
  - 检查是否存在名为 `venv` 的目录。
  - 如果不存在，则运行 `$PYTHON_BIN -m venv venv` 创建新环境。
  - **核心操作**：执行 `source venv/bin/activate` 激活环境，后续的所有 `pip` 命令都将作用于此环境。

### 3. 清理并安装标准依赖 (Dependency Handling)
- **目标**：清空可能冲突的旧包并安装基础库。
- **逻辑**：
  - **卸载**：主动卸载 `czsc` 和 `rs_czsc`。这是为了确保之后安装的是本地最新代码，而不是旧的残留版本。
  - **按需安装**：读取 `requirements.txt` 文件，批量安装项目运行所需的第三方库（如 Django, Pandas 等）。

### 4. 安装本地修改版 CZSC (Local Install)
- **目标**：将项目中的 `czsc` 文件夹安装为系统级包。
- **逻辑**：
  - 检查当前目录下是否存在 `czsc` 文件夹。
  - 执行 `pip install --force-reinstall --no-cache-dir .`。
  - **意义**：这一步会调用项目根目录下的 `setup.py`，将本地的策略引擎代码安装到 `venv` 中。使用 `--no-cache-dir` 是为了防止使用旧的编译缓存。

### 4.1 & 4.2 验证与 Web 依赖补偿
- **目标**：确保关键组件没有遗漏。
- **逻辑**：
  - **冲突检查**：再次确认 `rs_czsc`（Rust加速版）已被移除，以免干扰 Python 版逻辑。
  - **关键库强制检查**：检查 `SQLAlchemy` 是否存在，若丢失则自动补装特定版本 (`2.0.36`)。
  - **Web 依赖全家桶**：脚本内置了一个列表 `WEB_DEPS`（包含 uvicorn, celery, djangorestframework 等），循环检查每一个包，发现缺失则通过 `pip` 自动补齐。

### 5. 完成汇报与启动指引
- **目标**：告知用户部署状态及如何启动。
- **逻辑**：
  - 打印核心包的安装版本汇总 (`czsc`, `SQLAlchemy`, `uvicorn`)。
  - **环境变量声明**：特别提醒用户设置 `export CZSC_USE_PYTHON="1"`，这是为了让系统强制使用纯 Python 逻辑。
  - 给出准确的启动命令。

---

## 如何运行

### macOS / Linux
在 `backend` 目录下执行：
```bash
bash deploy_demo.sh
```

### Windows
在 `backend` 目录下，双击运行 `deploy_windows.bat` 或在 CMD 中执行：
```cmd
deploy_windows.bat
```

## 启动服务
部署成功后，按以下顺序操作：

### macOS / Linux
1. `source venv/bin/activate`
2. `export CZSC_USE_PYTHON="1"`
3. `python main.py`

### Windows
1. `venv\Scripts\activate`
2. `set CZSC_USE_PYTHON=1`
3. `python main.py`
