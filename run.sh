#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 确保虚拟环境存在
if [ ! -d "venv" ]; then
    echo "⚠️  未找到虚拟环境，请先运行安装脚本："
    echo "   ./install.sh"
    exit 1
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 检查依赖是否已安装
if [ ! -f ".deps_installed" ]; then
    echo "⚠️  依赖未安装，正在安装..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        touch .deps_installed
    else
        echo "❌ 依赖安装失败，请检查网络连接"
        exit 1
    fi
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "❌ 错误: 未找到.env配置文件"
    echo "请复制 .env.example 为 .env 并填入你的API密钥："
    echo "   cp .env.example .env"
    exit 1
fi

# 验证API密钥
if grep -q "YOUR_OPENAI_API_KEY" .env || grep -q "YOUR_ARK_API_KEY" .env; then
    echo "⚠️  警告: 请编辑 .env 文件并填入真实的API密钥"
    echo ""
    read -p "是否继续运行？(y/N): " continue_run
    if [[ ! $continue_run =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 运行主程序
echo ""
echo "🎬 启动序列帧动画生成器..."
echo "================================"
python main.py