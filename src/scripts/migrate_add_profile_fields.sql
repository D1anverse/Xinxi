-- 迁移脚本：为 user_profiles 添加新字段
-- 执行日期: 2026-04-13

-- 添加交友目的字段
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS purpose VARCHAR(20) DEFAULT 'dating';

-- 添加自定义标签字段
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS custom_tags TEXT[] DEFAULT '{}';

-- 验证字段已添加
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'user_profiles' 
AND column_name IN ('purpose', 'custom_tags');
