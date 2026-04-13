"""
SoulMatch 后端配置文件
"""
import os
from datetime import timedelta

# ============================================
# 基础配置
# ============================================
APP_NAME = "SoulMatch"
APP_VERSION = "0.1.0"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# ============================================
# 数据库配置
# ============================================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://soulmatch_user:secure_password@localhost:5432/soulmatch"
)
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "10"))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))

# ============================================
# Redis 配置
# ============================================
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_TTL_SESSION = 604800  # 7 天
REDIS_TTL_ONLINE = 300  # 5 分钟
REDIS_TTL_MATCH_CACHE = 86400  # 24 小时

# ============================================
# JWT 配置
# ============================================
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE = timedelta(days=7)
JWT_REFRESH_TOKEN_EXPIRE = timedelta(days=30)

# ============================================
# 安全配置
# ============================================
BCRYPT_ROUNDS = 12
PASSWORD_MIN_LENGTH = 8
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "change-this-in-production-32chars!")

# ============================================
# 限流配置
# ============================================
RATE_LIMIT_GENERAL = 100  # 每分钟请求数
RATE_LIMIT_SWIPE = 20  # 每分钟滑动次数
RATE_LIMIT_MESSAGE = 10  # 每分钟消息数

# ============================================
# 匹配配置
# ============================================
DAILY_RECOMMENDATIONS_COUNT = 5  # 每日推荐人数
MATCH_MIN_SCORE = 0.60  # 最低匹配度阈值

# ============================================
# 文件存储配置
# ============================================
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "./uploads")
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

# ============================================
# CORS 配置
# ============================================
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173"
).split(",")

# ============================================
# 日志配置
# ============================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================
# AI 服务配置
# ============================================
AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama")  # ollama / gemini / siliconflow
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
AI_REQUEST_TIMEOUT = 60  # 秒
AI_MAX_TOKENS = 2000
AI_TEMPERATURE = 0.7
