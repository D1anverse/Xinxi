#!/bin/bash
# SoulMatch Docker 镜像导入和部署脚本
# 用于在目标服务器上部署已打包的镜像

set -e

echo "🦞 SoulMatch 镜像导入和部署"
echo "============================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法：$0 <打包文件.tar.gz> [部署目录]"
    echo ""
    echo "示例:"
    echo "  $0 soulmatch-20260312_231200.tar.gz"
    echo "  $0 soulmatch-20260312_231200.tar.gz /opt/soulmatch"
    exit 1
fi

PACKAGE_FILE="$1"
DEPLOY_DIR="${2:-./soulmatch-deploy}"

# 检查文件是否存在
if [ ! -f "${PACKAGE_FILE}" ]; then
    echo -e "${RED}❌ 错误：文件不存在：${PACKAGE_FILE}${NC}"
    exit 1
fi

# 检查 Docker
echo "🔍 检查 Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到 Docker${NC}"
    echo ""
    echo "请先安装 Docker:"
    echo "  curl -fsSL https://get.docker.com | sh"
    echo "  sudo usermod -aG docker $USER"
    echo "  # 需要重新登录生效"
    exit 1
fi
echo -e "${GREEN}✅ Docker: $(docker --version)${NC}"

if ! command -v docker compose &> /dev/null; then
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        echo -e "${RED}❌ 错误：未找到 docker compose 或 docker-compose${NC}"
        exit 1
    fi
else
    COMPOSE_CMD="docker compose"
fi
echo -e "${GREEN}✅ Compose: ${COMPOSE_CMD}${NC}"

# 解压文件
echo ""
echo "📦 解压部署包..."
mkdir -p "${DEPLOY_DIR}"
tar -xzf "${PACKAGE_FILE}" -C "${DEPLOY_DIR}"
echo -e "${GREEN}✅ 解压完成：${DEPLOY_DIR}${NC}"

# 找到解压后的目录
PACKAGE_DIR=$(find "${DEPLOY_DIR}" -maxdepth 1 -type d -name "soulmatch-*" | head -1)

if [ -z "${PACKAGE_DIR}" ]; then
    echo -e "${RED}❌ 错误：未找到部署包目录${NC}"
    exit 1
fi

echo "📁 部署包目录：${PACKAGE_DIR}"

# 加载镜像
echo ""
echo "📦 加载 Docker 镜像..."

if [ -f "${PACKAGE_DIR}/load-images.sh" ]; then
    bash "${PACKAGE_DIR}/load-images.sh"
else
    echo "加载后端镜像..."
    docker load -i "${PACKAGE_DIR}/images/backend.tar"
    
    echo "加载前端镜像..."
    docker load -i "${PACKAGE_DIR}/images/frontend.tar"
    
    echo "加载 Redis 镜像..."
    docker load -i "${PACKAGE_DIR}/images/redis.tar"
fi

echo -e "${GREEN}✅ 镜像加载完成${NC}"

# 显示可用镜像
echo ""
echo "📊 可用镜像:"
docker images | grep soulmatch
docker images | grep redis:6-alpine

# 配置环境变量
echo ""
echo "⚙️  配置环境变量..."

PROJECT_DIR="${PACKAGE_DIR}/project"
cd "${PROJECT_DIR}"

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ 已创建 .env 文件${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  提示：请编辑 .env 文件修改配置${NC}"
        echo "   特别是 JWT_SECRET (生产环境必须修改)"
    else
        cat > .env << ENV
JWT_SECRET=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///./soulmatch.db
REDIS_URL=redis://redis:6379/0
DEBUG=false
BACKEND_PORT=8000
FRONTEND_PORT=3000
ENV
        echo -e "${GREEN}✅ 已生成 .env 文件${NC}"
    fi
else
    echo -e "${GREEN}✅ .env 文件已存在${NC}"
fi

# 检查端口占用
echo ""
echo "🔍 检查端口占用..."

check_port() {
    local port=$1
    if command -v lsof &> /dev/null; then
        if lsof -i :${port} &> /dev/null; then
            echo -e "${YELLOW}⚠️  警告：端口 ${port} 被占用${NC}"
            return 1
        fi
    elif command -v ss &> /dev/null; then
        if ss -tuln | grep -q ":${port} "; then
            echo -e "${YELLOW}⚠️  警告：端口 ${port} 被占用${NC}"
            return 1
        fi
    fi
    return 0
}

PORT_CHANGED=false
if ! check_port 8000; then
    echo "   自动修改后端端口为 8001"
    sed -i 's/BACKEND_PORT=8000/BACKEND_PORT=8001/' .env
    PORT_CHANGED=true
fi

if ! check_port 3000; then
    echo "   自动修改前端端口为 3001"
    sed -i 's/FRONTEND_PORT=3000/FRONTEND_PORT=3001/' .env
    PORT_CHANGED=true
fi

if [ "${PORT_CHANGED}" = true ]; then
    echo -e "${GREEN}✅ 端口配置已调整${NC}"
fi

# 启动服务
echo ""
echo "🚀 启动服务..."
${COMPOSE_CMD} up -d

# 等待服务启动
echo ""
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo ""
echo "📊 服务状态:"
${COMPOSE_CMD} ps

# 获取访问地址
echo ""
echo "🌐 访问地址:"

# 从 .env 读取端口
BACKEND_PORT=$(grep BACKEND_PORT .env | cut -d'=' -f2)
FRONTEND_PORT=$(grep FRONTEND_PORT .env | cut -d'=' -f2)

echo "   前端：http://localhost:${FRONTEND_PORT}"
echo "   后端 API: http://localhost:${BACKEND_PORT}"
echo "   API 文档：http://localhost:${BACKEND_PORT}/docs"

# 健康检查
echo ""
echo "🏥 健康检查..."

sleep 3
if curl -s -o /dev/null -w "%{http_code}" "http://localhost:${BACKEND_PORT}/health" | grep -q "200"; then
    echo -e "${GREEN}✅ 后端服务正常${NC}"
else
    echo -e "${YELLOW}⚠️  后端服务可能未完全启动，请稍后检查${NC}"
fi

echo ""
echo "=================================="
echo -e "${GREEN}✅ 部署完成！${NC}"
echo "=================================="
echo ""
echo "📝 常用命令:"
echo ""
echo "   查看日志：cd ${PROJECT_DIR} && ${COMPOSE_CMD} logs -f"
echo "   停止服务：cd ${PROJECT_DIR} && ${COMPOSE_CMD} down"
echo "   重启服务：cd ${PROJECT_DIR} && ${COMPOSE_CMD} restart"
echo "   查看状态：cd ${PROJECT_DIR} && ${COMPOSE_CMD} ps"
echo ""
echo "📂 部署目录：${PROJECT_DIR}"
echo ""
