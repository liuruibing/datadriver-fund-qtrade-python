#!/bin/bash

# 获取当前脚本所在目录
cd "$(dirname "$0")"

# 1. 精准杀掉占用 7090 端口的进程，防止重启冲突
# (这是最可靠的方式，因为它直接解决端口监听问题)
lsof -t -i:7090 | xargs kill -9 2>/dev/null

# 兜底：如果端口未占用，但也想按文件名清理残留进程
# pkill -9 -f "python main.py" 2>/dev/null

sleep 2

# 2. 激活虚拟环境 (如果存在)
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Warning: venv not found, using system python."
fi

# 3. 设置必要的环境变量
export CZSC_USE_PYTHON="1"

# 4. 后台静默启动项目，并将日志写入 server.log
nohup python main.py > server.log 2>&1 &

echo "--------------------------------------------------------"
echo "服务已在后台启动 (监听端口: 7090)"
echo "你可以运行以下命令查看日志："
echo "tail -f server.log"
echo "--------------------------------------------------------"
