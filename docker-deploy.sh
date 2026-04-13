#!/bin/bash
# SoulMatch Docker 一键部署脚本
# 自动安装 Docker 并部署应用

set -e

echo "🦞 SoulMatch Docker 一键部署"
echo "=============================="
echo ""

# 检查是否已安装 Docker
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "✅ Docker 已安装"
    docker --version
    docker-compose --version
else
    echo "📦 正在安装 Docker..."
    
    # 检测操作系统
    if [ -f /etc/debian_version ]; then
        echo "检测到 Debian/Ubuntu 系统"
        
        # 卸载旧版本
        sudo apt-get remove -y docker docker-engine docker.io containerd runc || true
        
        # 安装必要工具
        sudo apt-get update
        sudo apt-get install -y \
            apt-transport-https \
            ca-certificates \
            curl \
            gnupg \
            lsb-release
        
        # 添加 Docker GPG 密钥
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        
        # 设置稳定版仓库
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
          $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # 安装 Docker Engine
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        
        # 启动 Docker
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # 添加用户到 docker 组 (可选，避免每次都用 sudo)
        if groups $USER | grep -q docker; then
            echo "✅ 用户已在 docker 组中"
        else
            echo "ℹ️  将用户添加到 docker 组 (需要重新登录生效)"
            sudo usermod -aG docker $USER
        fi
        
    elif [ -f /etc/redhat-release ]; then
        echo "检测到 CentOS/RHEL 系统"
        
        # 安装 Docker
        sudo yum install -y yum-utils
        sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        sudo systemctl start docker
        sudo systemctl enable docker
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "检测到 macOS 系统"
        echo "请手动安装 Docker Desktop:"
        echo "https://docs.docker.com/desktop/install/mac-install/"
        exit 1
        
    else
        echo "❌ 不支持的操作系统，请手动安装 Docker"
        echo "https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    echo ""
    echo "✅ Docker 安装完成"
    docker --version
    docker compose version
fi

echo ""
echo "📁 准备部署文件..."

# 检查项目目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查必要文件
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 错误：未找到 docker-compose.yml"
    exit 1
fi

if [ ! -f "Dockerfile.backend" ]; then
    echo "❌ 错误：未找到 Dockerfile.backend"
    exit 1
fi

echo ""
echo "🔧 配置环境变量..."

# 创建 .env 文件
if [ ! -f ".env" ]; then
    cat > .env << EOF
# SoulMatch 环境变量配置

# JWT 密钥 (生产环境请修改)
JWT_SECRET=$(openssl rand -hex 32)

# 数据库配置
DATABASE_URL=sqlite:///./soulmatch.db

# Redis 配置
REDIS_URL=redis://redis:6379/0

# 应用配置
DEBUG=false
CORS_ORIGINS=["http://localhost","http://127.0.0.1"]

# 端口配置
BACKEND_PORT=8000
FRONTEND_PORT=3000
EOF
    echo "✅ 已创建 .env 文件"
else
    echo "✅ .env 文件已存在"
fi

echo ""
echo "🚀 构建并启动服务..."

# 构建镜像
docker compose build

# 启动服务
docker compose up -d

echo ""
echo "⏳ 等待服务启动..."
sleep 5

echo ""
echo "📊 服务状态:"
docker compose ps

echo ""
echo "✅ 部署完成!"
echo ""
echo "🌐 访问地址:"
echo "   前端：http://localhost:3000"
echo "   后端 API: http://localhost:8000"
echo "   API 文档：http://localhost:8000/docs"
echo ""
echo "📝 常用命令:"
echo "   查看日志：docker compose logs -f"
echo "   停止服务：docker compose down"
echo "   重启服务：docker compose restart"
echo "   重新构建：docker compose build --no-cache"
echo ""
