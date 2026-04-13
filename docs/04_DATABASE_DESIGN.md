# 🗄️ 数据库设计 - SoulMatch

> **Phase 1 任务 4/5** | 创建时间：2026-03-12  
> **数据库**: PostgreSQL + Redis

---

## 📊 整体架构

```
┌─────────────────────────────────────────────────────┐
│                    应用层                            │
│  (Node.js/Express API)                              │
└─────────────────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────┐            ┌─────────────────┐
│   PostgreSQL    │            │     Redis       │
│   (主数据库)     │            │   (缓存/会话)    │
│                 │            │                 │
│ - 用户数据      │            │ - 会话 token     │
│ - 问卷答案      │            │ - 匹配度缓存     │
│ - 匹配记录      │            │ - 在线状态       │
│ - 聊天记录      │            │ - 限流计数       │
└─────────────────┘            └─────────────────┘
```

---

## 📋 核心表设计

### 1. 用户表 (users)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 基本信息
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(50) NOT NULL,
    gender VARCHAR(20) NOT NULL,  -- male, female, other
    birth_date DATE NOT NULL,
    
    -- 学校信息（加密存储）
    university_id UUID REFERENCES universities(id),
    major VARCHAR(100),
    degree VARCHAR(50),  -- bachelor, master, phd
    enrollment_year INTEGER,
    
    -- 认证状态
    is_verified BOOLEAN DEFAULT FALSE,
    verification_method VARCHAR(50),  -- xuexin, edu_email
    verified_at TIMESTAMP,
    
    -- 状态
    status VARCHAR(20) DEFAULT 'active',  -- active, suspended, deleted
    last_active_at TIMESTAMP,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_gender ON users(gender);
CREATE INDEX idx_users_birth_date ON users(birth_date);
CREATE INDEX idx_users_university ON users(university_id);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_last_active ON users(last_active_at);
```

### 2. 大学表 (universities)

```sql
CREATE TABLE universities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    name VARCHAR(200) NOT NULL,
    short_name VARCHAR(50),
    
    -- 分类
    type VARCHAR(50),  -- 985, 211, double_first_class, ordinary
    location_city VARCHAR(100),
    location_province VARCHAR(100),
    
    -- 认证配置
    edu_domain VARCHAR(100),  -- 用于 edu 邮箱认证
    
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_universities_name ON universities(name);
CREATE INDEX idx_universities_location ON universities(location_province, location_city);
CREATE INDEX idx_universities_domain ON universities(edu_domain);

-- 初始数据示例
INSERT INTO universities (name, short_name, type, location_city, edu_domain) VALUES
('清华大学', '清华', '985', '北京', 'tsinghua.edu.cn'),
('北京大学', '北大', '985', '北京', 'pku.edu.cn'),
('复旦大学', '复旦', '985', '上海', 'fudan.edu.cn');
```

### 3. 用户价值观表 (user_values)

```sql
CREATE TABLE user_values (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    
    -- 原始答案 (JSONB 便于查询和扩展)
    answers JSONB NOT NULL,  -- {"q1": 3, "q2": 5, ..., "q50": 2}
    
    -- 维度得分 (1.00-5.00)
    life_goals_score DECIMAL(3,2) NOT NULL,
    personality_score DECIMAL(3,2) NOT NULL,
    relationship_score DECIMAL(3,2) NOT NULL,
    interests_score DECIMAL(3,2) NOT NULL,
    lifestyle_score DECIMAL(3,2) NOT NULL,
    
    -- 用户标签 (从答案推断)
    tags TEXT[] DEFAULT '{}',  -- ['事业型', '内向型', '传统型']
    
    -- 权重偏好 (用户可调整)
    weights JSONB DEFAULT '{
        "life_goals": 0.30,
        "personality": 0.25,
        "relationship": 0.25,
        "interests": 0.10,
        "lifestyle": 0.10
    }'::jsonb,
    
    -- 时间戳
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_user_values_tags ON user_values USING GIN(tags);
CREATE INDEX idx_user_values_life_goals ON user_values(life_goals_score);
CREATE INDEX idx_user_values_personality ON user_values(personality_score);

-- 注释
COMMENT ON COLUMN user_values.answers IS '50 道题的原始答案，格式：{q1: 1-5, q2: 1-5, ...}';
COMMENT ON COLUMN user_values.tags IS '从答案推断的标签：事业型/家庭型/内向型/外向型/传统型/开放型';
```

### 4. 用户资料表 (user_profiles)

```sql
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    
    -- 展示信息
    avatar_url VARCHAR(500),
    bio TEXT,  -- 自我介绍
    
    -- 偏好设置
    preferred_gender VARCHAR(20) NOT NULL,  -- male, female, any
    min_age INTEGER NOT NULL,
    max_age INTEGER NOT NULL,
    preferred_locations TEXT[],  -- 期望城市列表
    
    -- 可见性设置
    show_university BOOLEAN DEFAULT FALSE,
    show_major BOOLEAN DEFAULT FALSE,
    show_age BOOLEAN DEFAULT TRUE,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_user_profiles_gender ON user_profiles(preferred_gender);
CREATE INDEX idx_user_profiles_age_range ON user_profiles(min_age, max_age);
```

### 5. 匹配记录表 (match_records)

```sql
CREATE TABLE match_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 双方用户
    user_a_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_b_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 匹配度详情
    total_score DECIMAL(5,4) NOT NULL,  -- 0.0000-1.0000
    dimension_scores JSONB NOT NULL,  -- {"life_goals": 0.95, "personality": 0.80, ...}
    
    -- 用户操作
    user_a_action VARCHAR(20),  -- liked, skipped, pending
    user_b_action VARCHAR(20),
    user_a_action_at TIMESTAMP,
    user_b_action_at TIMESTAMP,
    
    -- 匹配状态
    is_matched BOOLEAN DEFAULT FALSE,
    matched_at TIMESTAMP,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_match_user_a ON match_records(user_a_id);
CREATE INDEX idx_match_user_b ON match_records(user_b_id);
CREATE INDEX idx_match_is_matched ON match_records(is_matched) WHERE is_matched = true;
CREATE INDEX idx_match_created ON match_records(created_at);

-- 约束：确保 user_a_id < user_b_id 避免重复
ALTER TABLE match_records ADD CONSTRAINT chk_user_order 
    CHECK (user_a_id < user_b_id);
CREATE UNIQUE INDEX idx_match_unique_pair 
    ON match_records(user_a_id, user_b_id);
```

### 6. 每日推荐表 (daily_recommendations)

```sql
CREATE TABLE daily_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recommended_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 推荐信息
    match_score DECIMAL(5,4) NOT NULL,
    recommendation_date DATE NOT NULL,
    recommendation_rank INTEGER NOT NULL,  -- 1-5
    
    -- 用户操作
    user_action VARCHAR(20),  -- liked, skipped, pending, viewed
    action_at TIMESTAMP,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 唯一约束：每天每个用户只能被推荐给同一人一次
    UNIQUE(user_id, recommended_user_id, recommendation_date)
);

-- 索引
CREATE INDEX idx_daily_rec_user_date ON daily_recommendations(user_id, recommendation_date);
CREATE INDEX idx_daily_rec_date ON daily_recommendations(recommendation_date);
CREATE INDEX idx_daily_rec_action ON daily_recommendations(user_action);

-- 每日清理：删除 30 天前的数据
-- CREATE EVENT 或使用 pg_cron
```

### 7. 聊天会话表 (conversations)

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联的匹配记录
    match_record_id UUID UNIQUE REFERENCES match_records(id),
    
    -- 参与者
    user_a_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_b_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 状态
    status VARCHAR(20) DEFAULT 'active',  -- active, archived, blocked
    last_message_at TIMESTAMP,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_conversations_user_a ON conversations(user_a_id);
CREATE INDEX idx_conversations_user_b ON conversations(user_b_id);
CREATE INDEX idx_conversations_last_message ON conversations(last_message_at DESC);

-- 约束
ALTER TABLE conversations ADD CONSTRAINT chk_user_order 
    CHECK (user_a_id < user_b_id);
```

### 8. 消息表 (messages)

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 消息内容
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',  -- text, image, system
    
    -- 状态
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_sender ON messages(sender_id);
CREATE INDEX idx_messages_created ON messages(created_at);
CREATE INDEX idx_messages_unread ON messages(conversation_id, is_read) WHERE is_read = FALSE;

-- 分区（可选，消息量大时）
-- ALTER TABLE messages PARTITION BY RANGE (created_at);
```

### 9. 举报表 (reports)

```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    reporter_id UUID NOT NULL REFERENCES users(id),
    reported_user_id UUID NOT NULL REFERENCES users(id),
    
    -- 举报原因
    reason VARCHAR(50) NOT NULL,  -- harassment, fake_profile, spam, inappropriate
    description TEXT,
    
    -- 相关记录
    conversation_id UUID REFERENCES conversations(id),
    message_id UUID REFERENCES messages(id),
    
    -- 处理状态
    status VARCHAR(20) DEFAULT 'pending',  -- pending, reviewed, resolved, rejected
    reviewed_by UUID REFERENCES users(id),  -- 管理员
    reviewed_at TIMESTAMP,
    resolution VARCHAR(200),
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_reports_reporter ON reports(reporter_id);
CREATE INDEX idx_reports_reported ON reports(reported_user_id);
CREATE INDEX idx_reports_status ON reports(status);
```

### 10. 认证记录表 (verifications)

```sql
CREATE TABLE verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 认证方式
    method VARCHAR(50) NOT NULL,  -- xuexin, edu_email, student_card
    
    -- 认证信息（加密）
    verification_data JSONB,  -- {student_id: xxx, school: xxx}
    
    -- 状态
    status VARCHAR(20) DEFAULT 'pending',  -- pending, approved, rejected
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_verifications_user ON verifications(user_id);
CREATE INDEX idx_verifications_status ON verifications(status);
```

---

## 🔴 Redis 设计

### Key 命名规范

```
soulmatch:{type}:{identifier}
```

### 1. 会话管理

```
# Key: soulmatch:session:{user_id}
# TTL: 7 天
{
  "token": "jwt_token",
  "created_at": 1710259200,
  "expires_at": 1710864000,
  "device": "iOS"
}
```

### 2. 在线状态

```
# Key: soulmatch:online:{user_id}
# TTL: 5 分钟（心跳续期）
# Value: "online" 或 JSON

# 使用 Redis Set 存储在线用户
# Key: soulmatch:online:users
# Members: [user_id_1, user_id_2, ...]
```

### 3. 匹配度缓存

```
# Key: soulmatch:match:{user_a_id}:{user_b_id}
# TTL: 24 小时
# Value: 0.8650 (匹配度分数)
```

### 4. 每日推荐缓存

```
# Key: soulmatch:daily:{user_id}:{date}
# TTL: 24 小时
# Value: JSON 数组 [user_id_1, user_id_2, ...]
```

### 5. 限流计数

```
# Key: soulmatch:ratelimit:{action}:{user_id}
# TTL: 60 秒
# Value: 计数

# 示例：
# soulmatch:ratelimit:swipe:user_123 -> 15 (限制 20 次/分钟)
# soulmatch:ratelimit:message:user_123 -> 5 (限制 10 次/分钟)
```

### 6. 用户标签缓存

```
# Key: soulmatch:tags:{user_id}
# TTL: 1 小时
# Value: JSON 数组 ["事业型", "内向型", "传统型"]
```

---

## 🔐 安全设计

### 1. 敏感数据加密

```sql
-- 使用 pgcrypto 扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 加密示例
INSERT INTO users (email, password_hash, ...) VALUES
  (pgp_sym_encrypt('user@email.com', 'encryption_key'), ...);

-- 解密查询
SELECT pgp_sym_decrypt(email, 'encryption_key') FROM users WHERE ...;
```

### 2. 密码存储

```python
# 使用 bcrypt
import bcrypt

# 哈希
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))

# 验证
bcrypt.checkpw(password.encode(), password_hash)
```

### 3. 数据脱敏

```sql
-- 视图：对外展示时隐藏敏感信息
CREATE VIEW user_public AS
SELECT 
    id,
    nickname,
    avatar_url,
    bio,
    -- 隐藏学校和专业
    CASE WHEN show_university THEN u.name ELSE NULL END as university,
    CASE WHEN show_major THEN up.major ELSE NULL END as major,
    CASE WHEN show_age THEN EXTRACT(YEAR FROM AGE(birth_date)) ELSE NULL END as age
FROM users u
JOIN user_profiles up ON u.id = up.user_id
LEFT JOIN universities uni ON u.university_id = uni.id;
```

---

## 📈 性能优化

### 1. 连接池配置

```python
# PostgreSQL 连接池
from psycopg2 import pool

connection_pool = pool.SimpleConnectionPool(
    1, 20,  # 最小/最大连接数
    host="localhost",
    database="soulmatch",
    user="soulmatch_user",
    password="xxx"
)
```

### 2. 查询优化

```sql
-- 使用 EXPLAIN ANALYZE 分析慢查询
EXPLAIN ANALYZE
SELECT * FROM match_records
WHERE user_a_id = 'xxx' AND is_matched = true;

-- 添加覆盖索引
CREATE INDEX idx_match_covering 
    ON match_records(user_a_id, is_matched) 
    INCLUDE (user_b_id, total_score);
```

### 3. 分页查询

```sql
-- 使用 keyset pagination 而非 offset
SELECT * FROM messages
WHERE conversation_id = 'xxx' AND created_at < '2026-03-12'
ORDER BY created_at DESC
LIMIT 20;
```

---

## 🗑️ 数据清理策略

### 定时清理任务

```sql
-- 使用 pg_cron 扩展
SELECT cron.schedule(
    'cleanup-old-recommendations',
    '0 3 * * *',  -- 每天凌晨 3 点
    $$DELETE FROM daily_recommendations WHERE recommendation_date < CURRENT_DATE - INTERVAL '30 days'$$
);

SELECT cron.schedule(
    'cleanup-inactive-users',
    '0 4 * * 0',  -- 每周日凌晨 4 点
    $$UPDATE users SET status = 'inactive' WHERE last_active_at < CURRENT_TIMESTAMP - INTERVAL '90 days'$$
);
```

---

## 📊 数据库初始化脚本

```sql
-- 1. 创建数据库
CREATE DATABASE soulmatch;
CREATE USER soulmatch_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE soulmatch TO soulmatch_user;

-- 2. 启用扩展
\c soulmatch
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_cron";

-- 3. 创建表（按依赖顺序）
-- universities -> users -> user_values/user_profiles -> match_records -> ...

-- 4. 创建索引
-- （见各表定义）

-- 5. 初始数据
INSERT INTO universities (name, short_name, type, location_city, edu_domain) VALUES
('清华大学', '清华', '985', '北京', 'tsinghua.edu.cn'),
('北京大学', '北大', '985', '北京', 'pku.edu.cn'),
-- ... 更多大学
```

---

## ⏭️ 下一步

1. ✅ 用户画像定义
2. ✅ 价值观问卷设计
3. ✅ 匹配算法设计
4. ✅ 数据库设计
5. ⬜ API 接口设计

---

_文档状态：✅ 完成_  
_创建时间：2026-03-12 19:16_
