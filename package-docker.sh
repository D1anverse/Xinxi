#!/bin/bash
# SoulMatch Docker 镜像打包脚本
# 用于将完整应用打包为可迁移的 tar 文件

set -e

echo "🦞 SoulMatch Docker 镜像打包工具"
echo "=================================="
echo ""

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/docker-images"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="soulmatch-${TIMESTAMP}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker
echo "🔍 检查 Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到 Docker${NC}"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✅ Docker: $(docker --version)${NC}"

if ! command -v docker compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  警告：未找到 docker compose 插件${NC}"
    echo "尝试使用 docker-compose..."
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

# 创建输出目录
echo ""
echo "📁 创建输出目录..."
mkdir -p "${OUTPUT_DIR}/${PACKAGE_NAME}"
echo -e "${GREEN}✅ 输出目录：${OUTPUT_DIR}/${PACKAGE_NAME}${NC}"

# 进入项目目录
cd "${SCRIPT_DIR}"

# 构建镜像
echo ""
echo "🔨 构建 Docker 镜像..."

# 构建后端镜像
echo "   构建后端镜像..."
docker build -t soulmatch-backend:latest -f Dockerfile.backend .

# 构建前端镜像
echo "   构建前端镜像..."
docker build -t soulmatch-frontend:latest -f frontend/web/Dockerfile frontend/web/

# 拉取 Redis 镜像
echo "   准备 Redis 镜像..."
docker pull redis:6-alpine

echo -e "${GREEN}✅ 镜像构建完成${NC}"

# 列出镜像
echo ""
echo "📊 镜像列表:"
docker images | grep soulmatch
docker images | grep redis:6-alpine

# 保存镜像
echo ""
echo "💾 保存镜像为 tar 文件..."

# 保存后端镜像
echo "   保存后端镜像..."
docker save soulmatch-backend:latest -o "${OUTPUT_DIR}/${PACKAGE_NAME}/backend.tar"

# 保存前端镜像
echo "   保存前端镜像..."
docker save soulmatch-frontend:latest -o "${OUTPUT_DIR}/${PACKAGE_NAME}/frontend.tar"

# 保存 Redis 镜像
echo "   保存 Redis 镜像..."
docker save redis:6-alpine -o "${OUTPUT_DIR}/${PACKAGE_NAME}/redis.tar"

echo -e "${GREEN}✅ 镜像保存完成${NC}"

# 复制项目文件
echo ""
echo "📋 复制项目文件..."

# 创建项目文件目录
mkdir -p "${OUTPUT_DIR}/${PACKAGE_NAME}/project"

# 复制必要文件
cp -r src/ "${OUTPUT_DIR}/${PACKAGE_NAME}/project/"
cp -r frontend/ "${OUTPUT_DIR}/${PACKAGE_NAME}/project/"
cp docker-compose.yml "${OUTPUT_DIR}/${PACKAGE_NAME}/project/"
cp Dockerfile.backend "${OUTPUT_DIR}/${PACKAGE_NAME}/project/"
cp requirements.txt "${OUTPUT_DIR}/${PACKAGE_NAME}/project/"
cp .env.example "${OUTPUT_DIR}/${PACKAGE_NAME}/project/.env"
cp -r scripts/ "${OUTPUT_DIR}/${PACKAGE_NAME}/project/" 2>/dev/null || true

# 创建部署脚本
cat > "${OUTPUT_DIR}/${PACKAGE_NAME}/project/deploy.sh" << 'DEPLOY_SCRIPT'
#!/bin/bash
# SoulMatch 快速部署脚本

set -e

echo "🦞 SoulMatch 快速部署"
echo "====================="
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 错误：未找到 Docker"
    echo "请先安装 Docker"
    exit 1
fi

# 加载镜像
echo "📦 加载 Docker 镜像..."
docker load -i images/backend.tar
docker load -i images/frontend.tar
docker load -i images/redis.tar

# 配置环境变量
echo "⚙️  配置环境变量..."
if [ ! -f ".env" ]; then
    cp .env .env
    echo "✅ 已创建 .env 文件"
fi

# 启动服务
echo "🚀 启动服务..."
docker compose up -d

echo ""
echo "✅ 部署完成!"
echo ""
echo "🌐 访问地址:"
echo "   前端：http://localhost:3000"
echo "   后端：http://localhost:8000"
echo "   API 文档：http://localhost:8000/docs"
echo ""

# 查看状态
docker compose ps
DEPLOY_SCRIPT

chmod +x "${OUTPUT_DIR}/${PACKAGE_NAME}/project/deploy.sh"

# 创建 README
cat > "${OUTPUT_DIR}/${PACKAGE_NAME}/README.md" << README
# SoulMatch 离线部署包

生成时间：$(date '+%Y-%m-%d %H:%M:%S')

## 📦 包含内容

- Docker 镜像 (backend, frontend, redis)
- 项目源代码
- 部署脚本

## 🚀 快速部署

### 1. 安装 Docker

目标服务器需要安装 Docker 和 Docker Compose:

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 需要重新登录生效
```

### 2. 上传部署包

```bash
# 将整个 ${PACKAGE_NAME} 目录上传到目标服务器
scp -r ${PACKAGE_NAME} user@target-server:/path/to/deploy/
```

### 3. 执行部署

```bash
cd /path/to/deploy/${PACKAGE_NAME}/project
./deploy.sh
```

## 📊 访问地址

- **前端**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 🔧 常用命令

```bash
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 停止服务
docker compose down

# 重启服务
docker compose restart
```

## 📝 配置说明

编辑 \`.env\` 文件修改配置:

```bash
# JWT 密钥 (生产环境必须修改)
JWT_SECRET=your-secret-key

# 端口配置
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

## 🐛 故障排查

### 镜像加载失败
```bash
# 手动加载镜像
docker load -i images/backend.tar
docker load -i images/frontend.tar
docker load -i images/redis.tar
```

### 端口被占用
修改 \`.env\` 文件中的端口配置:
```bash
BACKEND_PORT=8001
FRONTEND_PORT=3001
```

---

_部署包生成时间：$(date '+%Y-%m-%d %H:%M:%S')_
README

# 创建镜像加载脚本
mkdir -p "${OUTPUT_DIR}/${PACKAGE_NAME}/images"
mv "${OUTPUT_DIR}/${PACKAGE_NAME}/backend.tar" "${OUTPUT_DIR}/${PACKAGE_NAME}/images/"
mv "${OUTPUT_DIR}/${PACKAGE_NAME}/frontend.tar" "${OUTPUT_DIR}/${PACKAGE_NAME}/images/"
mv "${OUTPUT_DIR}/${PACKAGE_NAME}/redis.tar" "${OUTPUT_DIR}/${PACKAGE_NAME}/images/"

# 创建镜像加载脚本
cat > "${OUTPUT_DIR}/${PACKAGE_NAME}/load-images.sh" << 'LOAD_SCRIPT'
#!/bin/bash
# 镜像加载脚本

echo "📦 加载 Docker 镜像..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

docker load -i "${SCRIPT_DIR}/images/backend.tar"
docker load -i "${SCRIPT_DIR}/images/frontend.tar"
docker load -i "${SCRIPT_DIR}/images/redis.tar"

echo "✅ 镜像加载完成"
echo ""
echo "可用镜像:"
docker images | grep soulmatch
docker images | grep redis
LOAD_SCRIPT

chmod +x "${OUTPUT_DIR}/${PACKAGE_NAME}/load-images.sh"

# 计算大小
echo ""
echo "📊 打包统计:"
PACKAGE_SIZE=$(du -sh "${OUTPUT_DIR}/${PACKAGE_NAME}" | cut -f1)
echo "   总大小：${PACKAGE_SIZE}"
echo "   后端镜像：$(du -sh "${OUTPUT_DIR}/${PACKAGE_NAME}/images/backend.tar" | cut -f1)"
echo "   前端镜像：$(du -sh "${OUTPUT_DIR}/${PACKAGE_NAME}/images/frontend.tar" | cut -f1)"
echo "   Redis 镜像：$(du -sh "${OUTPUT_DIR}/${PACKAGE_NAME}/images/redis.tar" | cut -f1)"

# 压缩打包
echo ""
echo "📦 压缩打包..."
cd "${OUTPUT_DIR}"
tar -czf "${PACKAGE_NAME}.tar.gz" "${PACKAGE_NAME}"
echo -e "${GREEN}✅ 压缩完成${NC}"

# 显示最终信息
echo ""
echo "=================================="
echo -e "${GREEN}✅ 打包完成！${NC}"
echo "=================================="
echo ""
echo "📦 打包文件：${OUTPUT_DIR}/${PACKAGE_NAME}.tar.gz"
echo "📊 文件大小：$(du -sh "${OUTPUT_DIR}/${PACKAGE_NAME}.tar.gz" | cut -f1)"
echo ""
echo "🚀 迁移部署步骤:"
echo ""
echo "1. 上传到目标服务器:"
echo "   scp ${OUTPUT_DIR}/${PACKAGE_NAME}.tar.gz user@target-server:/path/to/"
echo ""
echo "2. 解压:"
echo "   tar -xzf ${PACKAGE_NAME}.tar.gz"
echo "   cd ${PACKAGE_NAME}/project"
echo ""
echo "3. 部署:"
echo "   ./deploy.sh"
echo ""
echo "=================================="
echo ""
