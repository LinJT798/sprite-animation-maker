#!/bin/bash

echo "🚀 序列帧动画生成器 - 安装脚本"
echo "================================"

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python3"
    exit 1
fi

python_version=$(python3 --version 2>&1)
echo "✓ 检测到 $python_version"

# 检查是否已有虚拟环境
if [ -d "venv" ]; then
    echo "⚠️  检测到已存在的虚拟环境"
    read -p "是否重新创建虚拟环境？(y/N): " recreate
    if [[ $recreate =~ ^[Yy]$ ]]; then
        echo "🗑️  删除旧的虚拟环境..."
        rm -rf venv
    fi
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "✓ 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo ""
echo "📦 升级pip..."
pip install --upgrade pip

# 安装依赖
echo ""
echo "📦 安装项目依赖..."
echo "这可能需要几分钟时间，请耐心等待..."
pip install -r requirements.txt

# 检查tkinter（用于预览器）
echo ""
echo "🔍 检查tkinter模块..."
python -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  警告: tkinter未正确安装"
    echo ""
    echo "解决方案："
    echo "  macOS: brew install python-tk"
    echo "  Ubuntu: sudo apt-get install python3-tk"
    echo "  CentOS: sudo yum install python3-tkinter"
    echo ""
    echo "注意：预览功能需要tkinter支持"
else
    echo "✓ tkinter已安装"
fi

# 创建输出目录
echo ""
echo "📁 创建输出目录结构..."
mkdir -p output/{images,videos,sprites}

# 复制环境变量文件
if [ ! -f ".env" ]; then
    echo ""
    echo "📄 创建.env配置文件..."
    cp .env.example .env
    echo ""
    echo "⚠️  重要：请编辑 .env 文件，填入你的API密钥："
    echo "   - OPENAI_API_KEY: OpenAI的API密钥"
    echo "   - ARK_API_KEY: 火山引擎的API密钥"
    echo ""
else
    echo ""
    echo "✓ .env配置文件已存在"
fi

# 设置脚本执行权限
echo ""
echo "🔧 设置脚本执行权限..."
chmod +x run.sh run_preview.sh

# 创建依赖安装标记
touch .deps_installed

echo ""
echo "✅ 安装完成！"
echo ""
echo "📋 使用说明："
echo "  1. 编辑 .env 文件，填入你的API密钥"
echo "  2. 运行程序："
echo "     方式一: ./run.sh (推荐)"
echo "     方式二: source venv/bin/activate && python main.py"
echo ""
echo "🎮 预览工具："
echo "  动画生成完成后会自动弹出预览窗口"
echo "  也可手动运行: ./run_preview.sh"
echo ""