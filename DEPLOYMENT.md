# SoulMatch 部署指南

> 大学生恋爱交友平台 - 完整部署文档  
> 更新时间：2026-03-12

---

## 📋 目录

1. [环境要求](#环境要求)
2. [后端部署](#后端部署)
3. [前端部署](#前端部署)
4. [数据库配置](#数据库配置)
5. [运行测试](#运行测试)
6. [生产部署](#生产部署)
7. [常见问题](#常见问题)

---

## 🔧 环境要求

### 系统要求
- **操作系统**: Linux / macOS / Windows (WSL2)
- **Python**: 3.9+
- **Node.js**: 18+
- **PostgreSQL**: 14+
- **Redis**: 6+

### 硬件要求
- **开发环境**: 2GB RAM, 10GB 存储
- **生产环境**: 4GB RAM, 20GB 存储

---

## 🚀 快速开始 (开发环境)

### 1. 克隆项目

```bash
cd /home/moyue/.openclaw/workspace/dating-app
```

### 2. 启动后端

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 设置环境变量
export DATABASE_URL="sqlite:///./soulmatch.db"
export REDIS_URL="redis://localhost:6379/0"
export JWT_SECRET="your-dev-secret-key-change-in-production"
export DEBUG=true

# 启动后端服务
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端运行在：http://localhost:8000  
API 文档：http://localhost:8000/docs

### 3. 启动前端

```bash
# 新终端窗口
cd frontend/web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在：http://localhost:3000

---

## 📦 后端详细部署

### 1. 安装依赖

```bash
cd dating-app
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# .env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/soulmatch

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# JWT 配置
JWT_SECRET=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
DEBUG=true
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]

# 邮件配置 (用于学生邮箱验证)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@example.com
SMTP_PASSWORD=your-password
```

### 3. 初始化数据库

```bash
# 使用 SQLite (开发环境)
# 自动创建，无需手动操作

# 使用 PostgreSQL (生产环境)
createdb soulmatch
psql -d soulmatch -f src/database/schema.sql
```

### 4. 启动服务

```bash
# 开发模式 (自动重载)
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式 (多进程)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. 验证后端

```bash
# 检查健康状态
curl http://localhost:8000/health

# 访问 API 文档
# 浏览器打开：http://localhost:8000/docs
```

---

## 💻 前端详细部署

### 1. 安装 Node.js

```bash
# 检查 Node.js 版本
node -v  # 应该 >= 18
npm -v
```

### 2. 安装依赖

```bash
cd dating-app/frontend/web
npm install
```

### 3. 配置环境变量

创建 `.env` 文件：

```bash
# frontend/web/.env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=SoulMatch
VITE_APP_VERSION=0.1.0
```

### 4. 启动开发服务器

```bash
npm run dev
```

访问：http://localhost:3000

### 5. 构建生产版本

```bash
npm run build

# 预览生产构建
npm run preview
```

构建输出在 `dist/` 目录

---

## 🗄️ 数据库配置

### SQLite (开发环境)

```bash
# 自动创建，无需配置
# 数据库文件：dating-app/src/soulmatch.db
```

### PostgreSQL (生产环境)

```bash
# 1. 安装 PostgreSQL
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql

# 2. 创建数据库
sudo -u postgres psql
CREATE DATABASE soulmatch;
CREATE USER soulmatch_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE soulmatch TO soulmatch_user;
\q

# 3. 初始化 Schema
psql -U soulmatch_user -d soulmatch -f src/database/schema.sql
```

### Redis (缓存)

```bash
# 1. 安装 Redis
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis

# 2. 启动 Redis
sudo systemctl start redis

# 3. 验证
redis-cli ping  # 应该返回 PONG
```

---

## 🧪 运行测试

### 后端测试

```bash
cd src

# 运行所有测试
pytest

# 运行单个模块测试
pytest backend/test_user_auth.py -v

# 查看测试覆盖率
pytest --cov=backend
```

### 前端测试

```bash
cd frontend/web

# 运行测试 (需要配置)
npm test

# E2E 测试 (需要配置 Playwright)
npm run test:e2e
```

---

## 🌐 生产部署

### Docker 部署 (推荐)

#### 1. 创建 Dockerfile (后端)

```dockerfile
# dating-app/Dockerfile.backend
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### 2. 创建 Dockerfile (前端)

```dockerfile
# dating-app/Dockerfile.frontend
FROM node:18-alpine AS builder

WORKDIR /app
COPY frontend/web/package*.json ./
RUN npm ci
COPY frontend/web/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### 3. Docker Compose

```yaml
# dating-app/docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      - DATABASE_URL=postgresql://soulmatch:password@db:5432/soulmatch
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET=${JWT_SECRET}
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=soulmatch
      - POSTGRES_USER=soulmatch
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### 4. 启动服务

```bash
cd dating-app
docker-compose up -d
```

访问：
- 前端：http://localhost
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

---

## ☁️ 云服务器部署

### 1. 准备服务器

- **推荐配置**: 2 核 4GB, 40GB SSD
- **系统**: Ubuntu 22.04 LTS
- **开放端口**: 80, 443, 22

### 2. 安装依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要软件
sudo apt install -y python3-pip python3-venv nodejs npm postgresql redis-server nginx git

# 安装 Docker (可选)
curl -fsSL https://get.docker.com | sh
```

### 3. 部署代码

```bash
# 克隆项目
cd /var/www
git clone <your-repo-url> soulmatch
cd soulmatch

# 或者使用 SCP 上传
# scp -r dating-app user@server:/var/www/soulmatch
```

### 4. 配置 Nginx

```nginx
# /etc/nginx/sites-available/soulmatch
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/soulmatch/frontend/web/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API 文档
    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_set_header Host $host;
    }
}
```

```bash
# 启用配置
sudo ln -s /etc/nginx/sites-available/soulmatch /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. 配置 Systemd 服务

```ini
# /etc/systemd/system/soulmatch-backend.service
[Unit]
Description=SoulMatch Backend
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/soulmatch/src
Environment="PATH=/var/www/soulmatch/venv/bin"
ExecStart=/var/www/soulmatch/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启用服务
sudo systemctl daemon-reload
sudo systemctl enable soulmatch-backend
sudo systemctl start soulmatch-backend
sudo systemctl status soulmatch-backend
```

### 6. 配置 HTTPS (Let's Encrypt)

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## 🔍 常见问题

### 1. 后端启动失败

**问题**: `ModuleNotFoundError: No module named 'xxx'`

**解决**:
```bash
pip install -r requirements.txt
# 或者
source venv/bin/activate  # 如果使用虚拟环境
```

### 2. 数据库连接失败

**问题**: `could not connect to server`

**解决**:
```bash
# 检查 PostgreSQL 是否运行
sudo systemctl status postgresql

# 启动 PostgreSQL
sudo systemctl start postgresql

# 检查连接
psql -U postgres -h localhost -d soulmatch
```

### 3. 前端跨域错误

**问题**: `Access to XMLHttpRequest has been blocked by CORS policy`

**解决**:
- 确保后端配置了正确的 CORS_ORIGINS
- 检查前端请求的 API 地址是否正确

### 4. 端口被占用

**问题**: `Address already in use`

**解决**:
```bash
# 查找占用端口的进程
lsof -i :8000
lsof -i :3000

# 杀死进程
kill -9 <PID>

# 或者修改配置使用其他端口
```

### 5. 教育邮箱验证失败

**问题**: 注册时提示邮箱格式错误

**解决**:
- 开发环境可修改验证逻辑允许非 edu 邮箱
- 生产环境确保 SMTP 配置正确

---

## 📊 监控与日志

### 查看后端日志

```bash
# Systemd 服务日志
sudo journalctl -u soulmatch-backend -f

# Docker 日志
docker-compose logs -f backend
```

### 查看 Nginx 日志

```bash
# 访问日志
sudo tail -f /var/log/nginx/access.log

# 错误日志
sudo tail -f /var/log/nginx/error.log
```

---

## 📝 部署检查清单

### 开发环境
- [ ] Python 依赖安装
- [ ] Node.js 依赖安装
- [ ] 环境变量配置
- [ ] 后端启动成功
- [ ] 前端启动成功
- [ ] API 文档可访问

### 生产环境
- [ ] 服务器配置完成
- [ ] 数据库初始化
- [ ] Redis 配置完成
- [ ] Nginx 配置完成
- [ ] HTTPS 证书配置
- [ ] Systemd 服务配置
- [ ] 监控日志配置
- [ ] 备份策略配置

---

_最后更新：2026-03-12 23:08_ 🦞
