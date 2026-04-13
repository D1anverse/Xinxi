# SoulMatch Docker 一键部署指南

> 无需手动配置，一键启动完整服务  
> 更新时间：2026-03-12

---

## 🚀 快速开始

### 一键部署命令

```bash
cd /home/moyue/.openclaw/workspace/dating-app
./docker-deploy.sh
```

脚本会自动：
1. ✅ 检测并安装 Docker
2. ✅ 配置环境变量
3. ✅ 构建 Docker 镜像
4. ✅ 启动所有服务

---

## 📋 部署后访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| **前端** | http://localhost:3000 | 用户界面 |
| **后端 API** | http://localhost:8000 | API 服务 |
| **API 文档** | http://localhost:8000/docs | Swagger UI |
| **Redis** | localhost:6379 | 缓存服务 |

---

## 🔧 手动部署步骤

### 1. 安装 Docker

#### Ubuntu/Debian

```bash
# 添加 Docker 仓库
curl -fsSL https://get.docker.com | sh

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 添加用户到 docker 组 (避免使用 sudo)
sudo usermod -aG docker $USER
# 需要重新登录生效
```

#### CentOS/RHEL

```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker
```

#### macOS

下载 Docker Desktop: https://docs.docker.com/desktop/install/mac-install/

#### Windows

下载 Docker Desktop: https://docs.docker.com/desktop/install/windows-install/

### 2. 验证安装

```bash
docker --version
docker compose version
```

### 3. 配置环境变量

```bash
cd dating-app
cp .env.example .env

# 编辑 .env 文件，修改 JWT_SECRET 等配置
nano .env
```

### 4. 启动服务

```bash
# 构建并启动
docker compose up -d

# 或分开执行
docker compose build
docker compose up -d
```

### 5. 查看状态

```bash
# 查看运行状态
docker compose ps

# 查看日志
docker compose logs -f

# 查看后端日志
docker compose logs backend

# 查看前端日志
docker compose logs frontend
```

---

## 🛠️ 常用 Docker 命令

### 服务管理

```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 重启服务
docker compose restart

# 重新构建
docker compose build --no-cache

# 查看日志
docker compose logs -f

# 查看特定服务日志
docker compose logs backend
```

### 进入容器

```bash
# 进入后端容器
docker compose exec backend bash

# 进入前端容器
docker compose exec frontend sh

# 进入 Redis 容器
docker compose exec redis redis-cli
```

### 数据管理

```bash
# 查看数据卷
docker volume ls

# 备份数据
docker run --rm -v dating-app_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz /data

# 恢复数据
docker run --rm -v dating-app_redis_data:/data -v $(pwd):/backup alpine tar xzf /backup/redis-backup.tar.gz -C /
```

### 清理

```bash
# 停止并删除所有容器
docker compose down

# 删除数据卷 (谨慎使用)
docker compose down -v

# 删除所有镜像
docker compose down --rmi all

# 清理未使用的资源
docker system prune -a
```

---

## 📊 Docker 架构

```
┌─────────────────────────────────────────────────┐
│                  Docker Compose                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌─────────────┐    ┌─────────────┐            │
│  │   Frontend  │───▶│   Backend   │            │
│  │  (Nginx)    │    │  (FastAPI)  │            │
│  │  Port:3000  │    │  Port:8000  │            │
│  └─────────────┘    └──────┬──────┘            │
│                            │                    │
│                            ▼                    │
│                     ┌─────────────┐            │
│                     │    Redis    │            │
│                     │  Port:6379  │            │
│                     └─────────────┘            │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## 🗄️ 数据持久化

### 数据卷

| 数据卷 | 用途 | 路径 |
|--------|------|------|
| `redis_data` | Redis 数据 | `/var/lib/docker/volumes/dating-app_redis_data` |
| `soulmatch_data` | SQLite 数据库 | `./soulmatch_data/` |

### 使用 PostgreSQL (可选)

修改 `docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=soulmatch
      - POSTGRES_USER=soulmatch
      - POSTGRES_PASSWORD=your-password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

修改 `.env`:
```bash
DATABASE_URL=postgresql://soulmatch:your-password@db:5432/soulmatch
```

---

## 🔒 生产环境配置

### 1. 修改环境变量

```bash
# .env
JWT_SECRET=<生成一个强随机密钥>
DEBUG=false
CORS_ORIGINS=["https://your-domain.com"]
```

### 2. 配置 HTTPS

使用 Nginx 反向代理：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

### 3. 配置防火墙

```bash
# 只开放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 🐛 故障排查

### 服务启动失败

```bash
# 查看详细日志
docker compose logs backend

# 检查端口占用
sudo lsof -i :8000
sudo lsof -i :3000

# 重新构建
docker compose build --no-cache
docker compose up -d
```

### 数据库连接失败

```bash
# 检查数据库文件
ls -la soulmatch_data/

# 进入容器检查
docker compose exec backend python3 -c "import sqlite3; print(sqlite3.connect('data/soulmatch.db').execute('SELECT 1').fetchone())"
```

### 前端无法访问后端

```bash
# 检查 CORS 配置
docker compose logs backend | grep CORS

# 测试 API
curl http://localhost:8000/health
```

---

## 📈 性能优化

### 1. 增加后端 worker 数量

修改 `Dockerfile.backend`:
```dockerfile
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2. 启用 Redis 缓存

确保 Redis 服务运行：
```bash
docker compose ps redis
```

### 3. 配置 Nginx 缓存

修改 `frontend/web/nginx.conf`:
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## 📝 部署检查清单

- [ ] Docker 已安装
- [ ] .env 文件已配置
- [ ] JWT_SECRET 已修改 (生产环境)
- [ ] 服务已启动 (`docker compose ps`)
- [ ] 前端可访问 (http://localhost:3000)
- [ ] API 可访问 (http://localhost:8000/docs)
- [ ] 日志正常 (`docker compose logs`)

---

_最后更新：2026-03-12 23:11_ 🦞
