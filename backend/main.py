import multiprocessing
import os
import sys

root_path = os.getcwd()
sys.path.append(root_path)
import uvicorn
from application.settings import LOGGING

if __name__ == '__main__':
    multiprocessing.freeze_support()
    
    # 强制设置环境变量
    os.environ["CZSC_USE_PYTHON"] = "1"
    
    workers = 4
    if os.sys.platform.startswith('win'):
        # Windows操作系统
        workers = None
    
    # 使用 7090 端口以匹配当前环境配置
    uvicorn.run("application.asgi:application", reload=False, host="0.0.0.0", port=7090, workers=workers,
                log_config=LOGGING)
