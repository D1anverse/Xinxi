-- SoulMatch 数据库初始化脚本
-- PostgreSQL + pgcrypto + pg_cron

-- 启用扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_cron";

-- ============================================
-- 1. 大学表 (universities)
-- ============================================
CREATE TABLE IF NOT EXISTS universities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    short_name VARCHAR(50),
    type VARCHAR(50),  -- 985, 211, double_first_class, ordinary
    location_city VARCHAR(100),
    location_province VARCHAR(100),
    edu_domain VARCHAR(100),  -- 用于 edu 邮箱认证
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_universities_name ON universities(name);
CREATE INDEX IF NOT EXISTS idx_universities_domain ON universities(edu_domain);

-- 深圳大学城3所院校初始数据
INSERT INTO universities (name, short_name, type, location_city, edu_domain) VALUES
('清华大学深圳研究生院', '清华深圳', '985', '深圳', 'sz.tsinghua.edu.cn'),
('北京大学深圳研究生院', '北大深圳', '985', '深圳', 'sz.pku.edu.cn'),
('哈尔滨工业大学深圳', '哈工大深圳', '985', '深圳', 'hitsz.edu.cn')
ON CONFLICT DO NOTHING;

-- ============================================
-- 2. 用户表 (users)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 基本信息
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(50) NOT NULL,
    gender VARCHAR(20) NOT NULL,  -- male, female, other
    birth_date DATE NOT NULL,
    city VARCHAR(100),  -- 所在城市
    
    -- 学校信息
    university_id UUID REFERENCES universities(id),
    major VARCHAR(100),
    degree VARCHAR(50),  -- bachelor, master, phd
    enrollment_year INTEGER,
    
    -- 认证状态
    is_verified BOOLEAN DEFAULT FALSE,
    verification_method VARCHAR(50),
    verified_at TIMESTAMP,
    
    -- 状态
    status VARCHAR(20) DEFAULT 'active',  -- active, suspended, deleted
    last_active_at TIMESTAMP,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_gender ON users(gender);
CREATE INDEX IF NOT EXISTS idx_users_university ON users(university_id);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

-- ============================================
-- 3. 用户价值观表 (user_values)
-- ============================================
CREATE TABLE IF NOT EXISTS user_values (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    
    -- 原始答案
    answers JSONB NOT NULL,
    
    -- 维度得分 (1.00-5.00)
    life_goals_score DECIMAL(3,2) NOT NULL,
    personality_score DECIMAL(3,2) NOT NULL,
    relationship_score DECIMAL(3,2) NOT NULL,
    interests_score DECIMAL(3,2) NOT NULL,
    lifestyle_score DECIMAL(3,2) NOT NULL,
    
    -- 用户标签
    tags TEXT[] DEFAULT '{}',
    
    -- 权重偏好
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

CREATE INDEX IF NOT EXISTS idx_user_values_tags ON user_values USING GIN(tags);

-- ============================================
-- 4. 用户资料表 (user_profiles)
-- ============================================
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    
    -- 展示信息
    avatar_url VARCHAR(500),
    bio TEXT,
    
    -- 交友目的: dating, friendship, both
    purpose VARCHAR(20) DEFAULT 'dating',
    
    -- 自定义标签
    custom_tags TEXT[] DEFAULT '{}',
    
    -- 偏好设置
    preferred_gender VARCHAR(20) NOT NULL DEFAULT 'any',
    min_age INTEGER NOT NULL DEFAULT 18,
    max_age INTEGER NOT NULL DEFAULT 35,
    preferred_locations TEXT[],
    
    -- 可见性设置
    show_university BOOLEAN DEFAULT FALSE,
    show_major BOOLEAN DEFAULT FALSE,
    show_age BOOLEAN DEFAULT TRUE,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 5. 匹配记录表 (match_records)
-- ============================================
CREATE TABLE IF NOT EXISTS match_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    user_a_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_b_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 匹配度详情
    total_score DECIMAL(5,4) NOT NULL,
    dimension_scores JSONB NOT NULL,
    
    -- 用户操作
    user_a_action VARCHAR(20),
    user_b_action VARCHAR(20),
    user_a_action_at TIMESTAMP,
    user_b_action_at TIMESTAMP,
    
    -- 匹配状态
    is_matched BOOLEAN DEFAULT FALSE,
    matched_at TIMESTAMP,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 约束
    CONSTRAINT chk_user_order CHECK (user_a_id < user_b_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_match_unique_pair ON match_records(user_a_id, user_b_id);
CREATE INDEX IF NOT EXISTS idx_match_is_matched ON match_records(is_matched) WHERE is_matched = true;

-- ============================================
-- 6. 每日推荐表 (daily_recommendations)
-- ============================================
CREATE TABLE IF NOT EXISTS daily_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recommended_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    match_score DECIMAL(5,4) NOT NULL,
    recommendation_date DATE NOT NULL,
    recommendation_rank INTEGER NOT NULL,
    
    user_action VARCHAR(20),
    action_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, recommended_user_id, recommendation_date)
);

CREATE INDEX IF NOT EXISTS idx_daily_rec_user_date ON daily_recommendations(user_id, recommendation_date);

-- ============================================
-- 7. 聊天会话表 (conversations)
-- ============================================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    match_record_id UUID UNIQUE REFERENCES match_records(id),
    
    user_a_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_b_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    status VARCHAR(20) DEFAULT 'active',
    last_message_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_conv_user_order CHECK (user_a_id < user_b_id)
);

CREATE INDEX IF NOT EXISTS idx_conversations_user_a ON conversations(user_a_id);
CREATE INDEX IF NOT EXISTS idx_conversations_last_message ON conversations(last_message_at DESC);

-- ============================================
-- 8. 消息表 (messages)
-- ============================================
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',
    
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_unread ON messages(conversation_id, is_read) WHERE is_read = FALSE;

-- ============================================
-- 9. 举报表 (reports)
-- ============================================
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    reporter_id UUID NOT NULL REFERENCES users(id),
    reported_user_id UUID NOT NULL REFERENCES users(id),
    
    reason VARCHAR(50) NOT NULL,
    description TEXT,
    
    conversation_id UUID REFERENCES conversations(id),
    message_id UUID REFERENCES messages(id),
    
    status VARCHAR(20) DEFAULT 'pending',
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP,
    resolution VARCHAR(200),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);

-- ============================================
-- 10. 认证记录表 (verifications)
-- ============================================
CREATE TABLE IF NOT EXISTS verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    method VARCHAR(50) NOT NULL,
    verification_data JSONB,
    
    status VARCHAR(20) DEFAULT 'pending',
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_verifications_user ON verifications(user_id);
CREATE INDEX IF NOT EXISTS idx_verifications_status ON verifications(status);

-- ============================================
-- 定时清理任务
-- ============================================
SELECT cron.schedule(
    'cleanup-old-recommendations',
    '0 3 * * *',
    $$DELETE FROM daily_recommendations WHERE recommendation_date < CURRENT_DATE - INTERVAL '30 days'$$
);
