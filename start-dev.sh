#!/bin/bash
# SoulMatch 快速启动脚本 (开发环境)

set -e

echo "🦞 SoulMatch 快速启动脚本"
echo "========================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3"
    exit 1
fi
echo "✅ Python: $(python3 --version)"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误：未找到 Node.js"
    exit 1
fi
echo "✅ Node.js: $(node --version)"

# 检查依赖
echo ""
echo "📦 检查依赖..."

# Python 依赖
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt
echo "✅ Python 依赖已安装"

# Node.js 依赖
if [ ! -d "frontend/web/node_modules" ]; then
    echo "安装前端依赖..."
    cd frontend/web
    npm install --silent
    cd ../..
fi
echo "✅ 前端依赖已安装"

# 设置环境变量
echo ""
echo "⚙️  配置环境变量..."
export DATABASE_URL="sqlite:///./soulmatch.db"
export REDIS_URL="redis://localhost:6379/0"
export JWT_SECRET="dev-secret-key-change-in-production"
export DEBUG=true
echo "✅ 环境变量已配置"

# 启动服务
echo ""
echo "🚀 启动服务..."
echo ""
echo "后端服务：http://localhost:8000"
echo "API 文档：http://localhost:8000/docs"
echo "前端服务：http://localhost:3000"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 启动后端 (后台)
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端 (后台)
cd frontend/web
npm run dev &
FRONTEND_PID=$!
cd ../..

# 等待退出信号
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; echo '👋 服务已停止'; exit 0" SIGINT SIGTERM

# 保持脚本运行
wait
