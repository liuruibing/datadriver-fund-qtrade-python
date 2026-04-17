#!/bin/bash
cd "$(dirname "$0")"

# 1. 净化环境：强制清理可能干扰虚拟环境路径的全局变量
unset PYTHONPATH
unset PYTHONHOME

# 2. 核心路径：指定你要求的那个“最全”的 venv 路径
PY_BIN="/datadriver/upload/wars/venv/bin/python"

# 3. 运行配置
RUN_PORT=${2:-7090}
RUN_HOST=0.0.0.0
RUN_WORKERS=4

# 4. 强制释放端口
echo "[INFO] Cleaning up port $RUN_PORT..."
lsof -t -i:$RUN_PORT | xargs kill -9 2>/dev/null
sleep 1

# 5. 启动 Celery (使用指定的独立 venv)
echo "[INFO] Starting Celery..."
pkill -f "celery.*application.celery"
nohup $PY_BIN -m celery -A application.celery worker -B --loglevel=info > celery_worker.log 2>&1 &

# 6. 启动 Web 项目 (使用指定的独立 venv)
echo "[INFO] Starting web service on port $RUN_PORT..."
export CZSC_USE_PYTHON="1"
nohup $PY_BIN -m uvicorn application.asgi:application \
    --host $RUN_HOST \
    --port $RUN_PORT \
    --workers $RUN_WORKERS \
    --access-log \
    > server.log 2>&1 &

echo "--------------------------------------------------------"
echo "服务已成功启动！"
echo "- 指定 venv: $PY_BIN"
echo "- 监听端口: $RUN_PORT"
echo "--------------------------------------------------------"
