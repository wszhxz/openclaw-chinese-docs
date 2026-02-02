#!/bin/bash
# 设置 LibreTranslate 环境的脚本

set -e

echo "设置 LibreTranslate 环境..."

# 检查是否安装了 Python3
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3"
    exit 1
fi

# 检查是否安装了 pip
if ! command -v pip3 &> /dev/null; then
    echo "错误: 未找到 pip3"
    exit 1
fi

# 创建虚拟环境
echo "创建 Python 虚拟环境..."
python3 -m venv libretranslate_env

# 激活虚拟环境
source libretranslate_env/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装 LibreTranslate
echo "安装 LibreTranslate..."
pip install libretranslate

echo "LibreTranslate 已安装完成!"
echo "要启动 LibreTranslate 服务器，请运行:"
echo "  source libretranslate_env/bin/activate"
echo "  libretranslate --host 0.0.0.0 --port 5000"
echo ""
echo "或者使用 Docker 方式 (推荐):"
echo "  docker run -d -p 5000:5000 libretranslate/libretranslate:latest"