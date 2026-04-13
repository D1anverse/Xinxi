# SoulMatch Docker 镜像打包指南

> 将完整应用打包为可迁移的 Docker 镜像包  
> 更新时间：2026-03-12

---

## 📦 快速打包

### 执行打包脚本

```bash
cd /home/moyue/.openclaw/workspace/dating-app
./package-docker.sh
```

脚本会自动：
1. ✅ 检查 Docker 环境
2. ✅ 构建 Docker 镜像 (backend, frontend, redis)
3. ✅ 保存镜像为 tar 文件
4. ✅ 复制项目源代码
5. ✅ 创建部署脚本
6. ✅ 压缩为 tar.gz 包

---

## 📊 输出文件

打包完成后生成：

```
dating-app/docker-images/
└── soulmatch-YYYYMMDD_HHMMSS/
    ├── images/
    │   ├── backend.tar      # 后端镜像 (~200MB)
    │   ├── frontend.tar     # 前端镜像 (~150MB)
    │   └── redis.tar        # Redis 镜像 (~30MB)
    ├── project/
    │   ├── src/             # 后端源代码
    │   ├── frontend/        # 前端源代码
    │   ├── docker-compose.yml
    │   ├── Dockerfile.backend
    │   ├── requirements.txt
    │   ├── .env             # 环境配置
    │   └── deploy.sh        # 部署脚本
    ├── load-images.sh       # 镜像加载脚本
    └── README.md            # 部署说明

打包文件：soulmatch-YYYYMMDD_HHMMSS.tar.gz (~380MB)
```

---

## 🚀 迁移部署

### 步骤 1: 上传打包文件

```bash
# 方法 1: 使用 scp
scp docker-images/soulmatch-20260312_231200.tar.gz user@target-server:/opt/

# 方法 2: 使用 rsync
rsync -avz docker-images/soulmatch-20260312_231200.tar.gz user@target-server:/opt/

# 方法 3: 手动复制 (U 盘等)
```

### 步骤 2: 在目标服务器部署

```bash
# SSH 登录目标服务器
ssh user@target-server

# 进入部署目录
cd /opt/

# 执行部署脚本
./deploy-package.sh soulmatch-20260312_231200.tar.gz

# 或者指定部署目录
./deploy-package.sh soulmatch-20260312_231200.tar.gz /opt/soulmatch
```

部署脚本会自动：
1. ✅ 检查 Docker 环境
2. ✅ 解压部署包
3. ✅ 加载 Docker 镜像
4. ✅ 配置环境变量
5. ✅ 检查端口占用
6. ✅ 启动服务

---

## 📋 手动部署步骤

如果不想使用自动脚本，可以手动操作：

### 1. 解压部署包

```bash
tar -xzf soulmatch-20260312_231200.tar.gz
cd soulmatch-20260312_231200/project
```

### 2. 加载镜像

```bash
# 使用加载脚本
../load-images.sh

# 或手动加载
docker load -i ../images/backend.tar
docker load -i ../images/frontend.tar
docker load -i ../images/redis.tar
```

### 3. 配置环境

```bash
# 复制环境配置
cp .env.example .env

# 编辑配置 (必须修改 JWT_SECRET)
nano .env
```

### 4. 启动服务

```bash
docker compose up -d
```

### 5. 检查状态

```bash
docker compose ps
docker compose logs -f
```

---

## 🔧 配置说明

### 环境变量 (.env)

```bash
# JWT 密钥 (生产环境必须修改！)
JWT_SECRET=your-super-secret-key-min-32-chars

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
```

### 端口映射

| 服务 | 容器端口 | 主机端口 | 可修改 |
|------|---------|---------|--------|
| 前端 | 80 | 3000 | ✅ |
| 后端 | 8000 | 8000 | ✅ |
| Redis | 6379 | 不暴露 | ❌ |

---

## 🐛 常见问题

### 1. Docker 未安装

**解决**:
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# 需要重新登录

# CentOS/RHEL
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
```

### 2. 端口被占用

**现象**: 部署时提示端口被占用

**解决**:
```bash
# 查看占用端口的进程
sudo lsof -i :8000
sudo lsof -i :3000

# 杀死进程
sudo kill -9 <PID>

# 或者修改 .env 中的端口
BACKEND_PORT=8001
FRONTEND_PORT=3001
```

### 3. 镜像加载失败

**现象**: `docker load` 报错

**解决**:
```bash
# 检查文件完整性
ls -lh images/*.tar

# 重新加载
docker load -i images/backend.tar

# 如果文件损坏，需要重新打包
```

### 4. 服务启动失败

**解决**:
```bash
# 查看详细日志
docker compose logs backend
docker compose logs frontend

# 检查配置
docker compose config

# 重新构建
docker compose down
docker compose up -d --force-recreate
```

### 5. 跨平台迁移问题

**现象**: Linux 打包，Windows 部署 (或反之)

**解决**:
- Docker 镜像本身是跨平台的
- 确保路径分隔符正确 (使用 `/` 而非 `\`)
- 确保换行符正确 (使用 LF 而非 CRLF)
- 建议在相同操作系统间迁移

---

## 📊 镜像大小优化

### 当前镜像大小

| 镜像 | 大小 | 说明 |
|------|------|------|
| backend | ~200MB | Python + FastAPI + 依赖 |
| frontend | ~150MB | Nginx + Vue 构建产物 |
| redis | ~30MB | Redis 6 Alpine |
| **总计** | **~380MB** | 压缩后 |

### 优化建议

1. **使用多阶段构建** (前端已实现)
2. **使用 Alpine 基础镜像** (后端已使用 slim)
3. **清理缓存**
   ```dockerfile
   RUN apt-get clean && rm -rf /var/lib/apt/lists/*
   ```
4. **删除不必要文件**
   ```dockerfile
   RUN rm -rf /tmp/* /root/.cache
   ```

---

## 🔒 生产环境安全

### 1. 修改默认密钥

```bash
# 生成强随机密钥
openssl rand -hex 32

# 更新 .env
JWT_SECRET=<生成的密钥>
```

### 2. 配置防火墙

```bash
# 只开放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. 启用 HTTPS

使用 Nginx 反向代理 + Let's Encrypt:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

---

## 📈 部署检查清单

### 打包前
- [ ] 代码已提交到版本控制
- [ ] 所有测试通过
- [ ] Dockerfile 配置正确
- [ ] .env.example 包含所有必需变量

### 部署前
- [ ] Docker 已安装
- [ ] 端口未被占用
- [ ] 防火墙已配置
- [ ] JWT_SECRET 已修改

### 部署后
- [ ] 服务正常运行 (`docker compose ps`)
- [ ] 前端可访问
- [ ] API 文档可访问
- [ ] 日志正常 (`docker compose logs`)

---

## 📝 脚本说明

### package-docker.sh

**用途**: 打包 Docker 镜像和项目代码

**选项**:
- 无参数，自动打包到 `docker-images/` 目录

**输出**:
- `soulmatch-YYYYMMDD_HHMMSS.tar.gz`

### deploy-package.sh

**用途**: 在目标服务器部署打包的镜像

**用法**:
```bash
./deploy-package.sh <打包文件.tar.gz> [部署目录]
```

**参数**:
- `<打包文件.tar.gz>`: 必需，打包文件路径
- `[部署目录]`: 可选，默认为当前目录

---

_最后更新：2026-03-12 23:12_ 🦞
