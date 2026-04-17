@echo off
:: 设置字符集为 UTF-8 防止中文乱码导致崩溃
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ==========================================
echo    CZSC Windows Version Deployment Script
echo ==========================================

:: 1. 环境检查
echo [1/5] Checking Python Environment...

:: 优先检查 python 命令，再检查 python3
set PYTHON_BIN=python
%PYTHON_BIN% --version >nul 2>&1
if %errorlevel% neq 0 (
    set PYTHON_BIN=python3
    %PYTHON_BIN% --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] 未找到 Python 命令，请确认 Python 已安装并勾选了 "Add Python to PATH"。
        echo [ERROR] Python not found. Please ensure Python is installed and added to PATH.
        pause
        exit /b 1
    )
)

echo Using Python: 
%PYTHON_BIN% --version

:: 2. 虚拟环境设置
set VENV_DIR=venv
if not exist "%VENV_DIR%" (
    echo [2/5] Creating virtual environment (%VENV_DIR%)...
    %PYTHON_BIN% -m venv %VENV_DIR%
)

echo Activating virtual environment...
:: 检查 Scripts 目录是否存在
if exist "%VENV_DIR%\Scripts\activate.bat" (
    call %VENV_DIR%\Scripts\activate.bat
) else (
    echo [ERROR] 虚拟环境激活脚本不存在: %VENV_DIR%\Scripts\activate.bat
    pause
    exit /b 1
)

:: 3. 安装依赖
echo [3/5] Handling Dependencies...
echo Uninstalling existing czsc/rs_czsc (if any)...
pip uninstall czsc rs_czsc -y >nul 2>&1

if exist "requirements.txt" (
    echo Installing requirements from requirements.txt...
    :: 使用清华源加速
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
) else (
    echo Warning: requirements.txt not found.
)

:: 4. 安装本地修改版 CZSC
echo [4/5] Installing Local Modified CZSC...
if exist "czsc" (
    echo Found local czsc package. Installing...
    pip install --force-reinstall --no-cache-dir .
) else (
    echo [ERROR] 找不到 czsc 文件夹，请确认你在 backend 目录下运行此脚本。
    echo [ERROR] czsc directory not found!
    pause
    exit /b 1
)

:: 4.1 校验
echo [4.1/5] Verifying Installation...
pip show SQLAlchemy >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: SQLAlchemy not found. Installing...
    pip install SQLAlchemy==2.0.36
)

:: 5. 完成
echo [5/5] Setup Complete.
echo.
echo ==========================================
echo IMPORTANT: To run the application on Windows:
echo 1. venv\Scripts\activate
echo 2. set CZSC_USE_PYTHON=1
echo 3. python main.py
echo ==========================================
echo.
echo Deployment successful!
echo 按任意键退出...
pause
