# SoulMatch Backend - 后端开发

大学生恋爱交友平台后端服务

## 📁 项目结构

```
dating-app/
├── src/
│   ├── main.py                 # FastAPI 主应用
│   ├── backend/
│   │   ├── user_auth.py        # 用户认证系统
│   │   ├── questionnaire.py    # 价值观问卷系统
│   │   └── matching_algorithm.py  # 匹配算法
│   ├── config/
│   │   └── settings.py         # 配置管理
│   └── database/
│       └── schema.sql          # 数据库 Schema
├── docs/                       # 设计文档
├── memory/                     # 开发日志
├── scripts/                    # 脚本
├── requirements.txt            # Python 依赖
└── PROJECT_PLAN.md             # 项目计划
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd dating-app
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# .env 文件
DATABASE_URL=postgresql://user:pass@localhost:5432/soulmatch
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-super-secret-key
DEBUG=true
```

### 3. 初始化数据库

```bash
psql -U postgres -d soulmatch -f src/database/schema.sql
```

### 4. 启动服务

```bash
# 开发模式
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📡 API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔑 核心模块

### 用户认证 (user_auth.py)

- 用户注册/登录
- JWT Token 管理
- 学生邮箱验证
- 密码加密 (bcrypt)

```python
from backend.user_auth import AuthService, RegisterRequest

auth = AuthService()
response = auth.register(RegisterRequest(
    email="student@tsinghua.edu.cn",
    password="SecurePass123!",
    nickname="小明",
    gender="male",
    birth_date="2002-05-15"
))
```

### 问卷系统 (questionnaire.py)

- 50 道价值观题目
- 5 个维度评估
- 自动标签生成
- 个性化总结

```python
from backend.questionnaire import QuestionnaireService

service = QuestionnaireService()
result = service.submit_answers({"q1": 3, "q2": 5, ...})
# 返回维度得分、标签、总结
```

### 匹配算法 (matching_algorithm.py)

- 加权相似度计算
- 维度兼容性分析
- 破冰话题生成
- 每日推荐引擎

```python
from backend.matching_algorithm import MatchingAlgorithm, UserValues

algo = MatchingAlgorithm()
match = algo.calculate_match(user_a_values, user_b_values)
print(f"匹配度：{match.match_percentage}%")
```

## 🗄️ 数据库

### PostgreSQL 表

| 表名 | 说明 |
|------|------|
| users | 用户基本信息 |
| universities | 大学列表 |
| user_values | 价值观得分 |
| user_profiles | 用户资料 |
| match_records | 匹配记录 |
| daily_recommendations | 每日推荐 |
| conversations | 聊天会话 |
| messages | 消息 |
| reports | 举报 |
| verifications | 认证记录 |

### Redis 缓存

- 会话管理
- 在线状态
- 匹配度缓存
- 限流计数

## 🔒 安全

- 密码 bcrypt 加密 (12 轮)
- JWT Token 认证
- CORS 配置
- 请求限流
- SQL 注入防护 (参数化查询)

## 🧪 测试

```bash
# 运行单元测试
pytest tests/

# 测试单个模块
python src/backend/user_auth.py
python src/backend/questionnaire.py
python src/backend/matching_algorithm.py
```

## 📊 Phase 2 进度

| 任务 | 状态 | 文件 |
|------|------|------|
| 用户系统 | ✅ 完成 | `user_auth.py` |
| 问卷系统 | ✅ 完成 | `questionnaire.py` |
| 匹配算法 | ✅ 完成 | `matching_algorithm.py` |
| 数据库设计 | ✅ 完成 | `schema.sql` |
| API 主应用 | ✅ 完成 | `main.py` |

**Phase 2 完成度**: 5/5 (100%) ✅

## ⏭️ 下一步

Phase 3: 前端基础开发

- [ ] 技术选型 (React/Vue/小程序)
- [ ] 项目脚手架
- [ ] 问卷 UI 实现
- [ ] 个人资料页
- [ ] 匹配结果页

## 📝 开发日志

### 2026-03-12 19:51

Phase 2 后端基础开发完成！

**完成内容**:
- ✅ 用户认证系统 (注册/登录/JWT)
- ✅ 价值观问卷系统 (50 题/5 维度)
- ✅ 匹配算法 (加权相似度)
- ✅ 数据库 Schema (10 张表)
- ✅ FastAPI 主应用

**代码统计**:
- `user_auth.py`: ~400 行
- `questionnaire.py`: ~750 行
- `matching_algorithm.py`: ~350 行
- `main.py`: ~300 行
- `schema.sql`: ~300 行

**总计**: ~2100 行代码

---

_最后更新：2026-03-12 19:51_ 🦞
