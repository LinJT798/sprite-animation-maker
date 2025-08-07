#!/bin/bash

# 使用主虚拟环境运行预览器
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "错误: 找不到虚拟环境。请先运行安装脚本。"
    exit 1
fi

# 运行预览器
if [ "$1" ]; then
    python preview.py "$1"
else
    python preview.py
fi