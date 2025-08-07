@echo off

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python3
    pause
    exit /b 1
)

REM 创建虚拟环境（如果不存在）
if not exist venv (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖（如果需要）
if not exist .deps_installed (
    echo 安装依赖包...
    pip install -r requirements.txt
    echo. > .deps_installed
)

REM 检查.env文件
if not exist .env (
    echo 警告: 未找到.env文件
    echo 请复制 .env.example 为 .env 并填入你的API密钥
    copy .env.example .env
    echo 已创建 .env 文件，请编辑后重新运行
    pause
    exit /b 1
)

REM 运行主程序
echo 启动序列帧动画生成器...
python main.py
pause