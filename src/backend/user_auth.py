"""
SoulMatch 用户认证系统
处理注册、登录、JWT 认证、学生验证
"""
import bcrypt
import jwt
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator
import re
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from config.settings import (
    JWT_SECRET, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE,
    JWT_REFRESH_TOKEN_EXPIRE,  # 新增
    BCRYPT_ROUNDS, PASSWORD_MIN_LENGTH
)


# ============================================
# 数据模型
# ============================================

class RegisterRequest(BaseModel):
    """注册请求"""
    email: EmailStr
    password: str = Field(..., min_length=PASSWORD_MIN_LENGTH)
    nickname: str = Field(..., min_length=2, max_length=50)
    gender: str  # male, female, other
    birth_date: str  # YYYY-MM-DD
    university: Optional[str] = None
    major: Optional[str] = None
    degree: Optional[str] = None  # bachelor, master, phd
    enrollment_year: Optional[int] = None
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < PASSWORD_MIN_LENGTH:
            raise ValueError(f'密码长度至少{PASSWORD_MIN_LENGTH}位')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含小写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v
    
    @field_validator('gender')
    def validate_gender(cls, v):
        if v not in ['male', 'female', 'other']:
            raise ValueError('性别必须是 male, female 或 other')
        return v


class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthResponse(BaseModel):
    """认证响应"""
    user_id: str
    token: str
    expires_in: int
    requires_verification: bool = True
    verification_method: str = "edu_email"
    needs_complete_profile: bool = False
    needs_complete_questionnaire: bool = True


# ============================================
# 密码工具
# ============================================

def hash_password(password: str) -> str:
    """哈希密码"""
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt(BCRYPT_ROUNDS)
    ).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(
        password.encode('utf-8'),
        password_hash.encode('utf-8')
    )


# ============================================
# JWT 工具
# ============================================

def create_access_token(user_id: str, email: str) -> str:
    """创建访问 Token"""
    expire = datetime.utcnow() + JWT_ACCESS_TOKEN_EXPIRE
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """创建刷新 Token"""
    expire = datetime.utcnow() + JWT_REFRESH_TOKEN_EXPIRE
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """解码 Token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def verify_token(token: str) -> Optional[str]:
    """验证 Token 并返回用户 ID"""
    payload = decode_token(token)
    if payload and payload.get("type") == "access":
        return payload.get("sub")
    return None


# ============================================
# 邮箱验证工具
# ============================================

def is_edu_email(email: str) -> bool:
    """检查是否为深圳大学城edu邮箱"""
    edu_domains = [
        'sz.tsinghua.edu.cn',  # 清华深圳研究生院
        'sz.pku.edu.cn',        # 北大深圳研究生院
        'hitsz.edu.cn',         # 哈工大深圳
    ]
    for domain in edu_domains:
        if email.endswith(domain):
            return True
    return False


def extract_university_from_email(email: str) -> Optional[str]:
    """从邮箱提取大学信息"""
    university_map = {
        'sz.tsinghua.edu.cn': '清华大学深圳研究生院',
        'sz.pku.edu.cn': '北京大学深圳研究生院',
        'hitsz.edu.cn': '哈尔滨工业大学深圳',
    }
    for domain, name in university_map.items():
        if email.endswith(domain):
            return name
    return None

   
# ============================================
# 深圳大学城3所院校邮箱域名
# ============================================
SZ_UNIV_DOMAINS = [
    'sz.tsinghua.edu.cn',  # 清华深圳研究生院
    'sz.pku.edu.cn',        # 北大深圳研究生院
    'hitsz.edu.cn',         # 哈工大深圳
]


# ============================================
# 数据库操作
# ============================================

async def db_create_user(user_data: dict) -> str:
    """在数据库中创建用户"""
    from database.db import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO users (
                email, password_hash, nickname, gender, birth_date,
                university_id, major, degree, enrollment_year,
                is_verified, status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            RETURNING id::text
            """,
            user_data['email'],
            user_data['password_hash'],
            user_data['nickname'],
            user_data['gender'],
            user_data['birth_date'],
            user_data.get('university_id'),
            user_data.get('major'),
            user_data.get('degree'),
            user_data.get('enrollment_year'),
            False,
            'active'
        )
        return row['id']


async def db_get_user_by_email(email: str) -> Optional[dict]:
    """通过邮箱从数据库获取用户"""
    from database.db import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT u.id::text, u.email, u.password_hash, u.nickname, u.gender,
                   u.birth_date, u.university_id, u.major, u.degree,
                   u.enrollment_year, u.is_verified, u.status,
                   univ.name as university_name
            FROM users u
            LEFT JOIN universities univ ON u.university_id = univ.id
            WHERE u.email = $1
            """,
            email
        )
        if row:
            return dict(row)
        return None


async def db_get_user_by_id(user_id: str) -> Optional[dict]:
    """通过ID从数据库获取用户"""
    from database.db import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT u.id::text, u.email, u.password_hash, u.nickname, u.gender,
                   u.birth_date, u.university_id, u.major, u.degree,
                   u.enrollment_year, u.is_verified, u.status,
                   univ.name as university_name
            FROM users u
            LEFT JOIN universities univ ON u.university_id = univ.id
            WHERE u.id = $1::uuid
            """,
            user_id
        )
        if row:
            return dict(row)
        return None


async def db_get_university_by_domain(domain: str) -> Optional[dict]:
    """通过域名获取大学"""
    from database.db import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id::text, name FROM universities WHERE edu_domain = $1 AND is_active = true",
            domain
        )
        if row:
            return dict(row)
        return None


# ============================================
# 认证服务
# ============================================

class AuthService:
    """认证服务"""
    
    def __init__(self, database=None):
        self.db = database  # 保留兼容，但不再使用
    
    def _extract_domain(self, email: str) -> Optional[str]:
        """从邮箱提取域名"""
        if '@' in email:
            return email.split('@')[1]
        return None
    
    def is_valid_email(self, email: str) -> bool:
        """检查是否为深圳大学城有效邮箱"""
        domain = self._extract_domain(email)
        return domain in SZ_UNIV_DOMAINS
    
    async def register(self, request: RegisterRequest) -> AuthResponse:
        """用户注册"""
        # 检查邮箱是否已存在
        existing = await db_get_user_by_email(request.email)
        if existing:
            raise ValueError("邮箱已被注册")
        
        # 验证邮箱域名
        if not self.is_valid_email(request.email):
            raise ValueError("请使用深圳大学城院校邮箱注册（sz.tsinghua.edu.cn, sz.pku.edu.cn, hitsz.edu.cn）")
        
        # 获取大学信息
        domain = self._extract_domain(request.email)
        university_id = None
        university_name = None
        if domain:
            univ = await db_get_university_by_domain(domain)
            if univ:
                university_id = univ['id']
                university_name = univ['name']
        
        # 处理 birth_date 转换
        birth_date_val = request.birth_date
        if isinstance(birth_date_val, str):
            birth_date_val = datetime.strptime(birth_date_val, "%Y-%m-%d").date()
        
        # 创建用户
        user_data = {
            'email': request.email,
            'password_hash': hash_password(request.password),
            'nickname': request.nickname,
            'gender': request.gender,
            'birth_date': birth_date_val,
            'university_id': university_id,
            'major': request.major,
            'degree': request.degree,
            'enrollment_year': request.enrollment_year,
        }
        
        user_id = await db_create_user(user_data)
        
        # 创建 Token
        access_token = create_access_token(user_id, request.email)
        
        # 深圳大学城edu邮箱自动验证通过
        return AuthResponse(
            user_id=user_id,
            token=access_token,
            expires_in=int(JWT_ACCESS_TOKEN_EXPIRE.total_seconds()),
            requires_verification=False,  # edu邮箱自动验证
            verification_method="edu_email",
            needs_complete_profile=True,
            needs_complete_questionnaire=True
        )
    
    async def login(self, request: LoginRequest) -> AuthResponse:
        """用户登录"""
        # 查找用户
        user = await db_get_user_by_email(request.email)
        if not user:
            raise ValueError("邮箱或密码错误")
        
        # 验证密码
        if not verify_password(request.password, user['password_hash']):
            raise ValueError("邮箱或密码错误")
        
        # 检查状态
        if user.get('status') != 'active':
            raise ValueError("账号已被禁用")
        
        # 创建 Token
        access_token = create_access_token(user['id'], user['email'])
        
        # 检查是否需要完善资料
        needs_profile = not user.get('university_id')
        needs_questionnaire = True  # 假设都需要完成问卷
        
        return AuthResponse(
            user_id=user['id'],
            token=access_token,
            expires_in=int(JWT_ACCESS_TOKEN_EXPIRE.total_seconds()),
            requires_verification=not user.get('is_verified', False),
            verification_method="edu_email",
            needs_complete_profile=needs_profile,
            needs_complete_questionnaire=needs_questionnaire
        )
    
    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """刷新 Token"""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        user_id = payload.get("sub")
        user = await db_get_user_by_id(user_id)
        if not user or user.get('status') != 'active':
            return None
        
        return create_access_token(user_id, user['email'])
    
    async def verify_email(self, user_id: str, verification_code: str) -> bool:
        """验证邮箱 (简化版 - 实际应发送验证码)"""
        user = await db_get_user_by_id(user_id)
        if not user:
            return False
        
        # 简化：任何 6 位验证码都通过 (实际应验证)
        if len(verification_code) == 6 and verification_code.isdigit():
            from database.db import get_pool
            pool = await get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE users SET
                        is_verified = true,
                        verified_at = CURRENT_TIMESTAMP,
                        verification_method = 'edu_email'
                    WHERE id = $1::uuid
                    """,
                    user_id
                )
            return True
        return False
    
    async def get_user_info(self, user_id: str) -> Optional[Dict]:
        """获取用户信息"""
        user = await db_get_user_by_id(user_id)
        if user:
            # 计算年龄
            age = None
            if user.get('birth_date'):
                today = date.today()
                birth = user['birth_date']
                age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            
            return {
                'id': user['id'],
                'email': user['email'],
                'nickname': user['nickname'],
                'gender': user['gender'],
                'birth_date': str(user['birth_date']) if user.get('birth_date') else None,
                'age': age,
                'city': user.get('city'),
                'university': user.get('university_name'),
                'major': user.get('major'),
                'is_verified': user.get('is_verified', False),
                'created_at': str(user.get('created_at', datetime.utcnow()))
            }
        return None


# ============================================
# FastAPI 路由 (待集成)
# ============================================

"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer()
auth_service = AuthService()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    token = credentials.credentials
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期"
        )
    return user_id

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    try:
        return auth_service.register(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    try:
        return auth_service.login(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    new_token = auth_service.refresh_token(refresh_token)
    if not new_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token 无效"
        )
    return {"access_token": new_token, "token_type": "bearer"}

@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user)):
    user_info = auth_service.get_user_info(user_id)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return {"success": True, "data": user_info}
"""


# ============================================
# 测试代码
# ============================================

if __name__ == "__main__":
    print("🦞 SoulMatch 用户认证系统测试")
    print("=" * 50)
    
    auth = AuthService()
    
    # 测试注册
    print("\n1️⃣ 测试注册...")
    try:
        register_req = RegisterRequest(
            email="test@sz.tsinghua.edu.cn",
            password="TestPass123",
            nickname="测试用户",
            gender="male",
            birth_date="2002-05-15",
            university="清华大学深圳研究生院",
            major="计算机科学",
            degree="bachelor",
            enrollment_year=2020
        )
        response = auth.register(register_req)
        print(f"   ✅ 注册成功！用户 ID: {response.user_id}")
        print(f"   📧 需要验证：{response.requires_verification}")
        print(f"   📝 需要完善问卷：{response.needs_complete_questionnaire}")
    except Exception as e:
        print(f"   ❌ 注册失败：{e}")
    
    # 测试登录
    print("\n2️⃣ 测试登录...")
    try:
        login_req = LoginRequest(
            email="test@sz.tsinghua.edu.cn",
            password="TestPass123"
        )
        response = auth.login(login_req)
        print(f"   ✅ 登录成功！用户 ID: {response.user_id}")
    except Exception as e:
        print(f"   ❌ 登录失败：{e}")
    
    # 测试 Token 验证
    print("\n3️⃣ 测试 Token 验证...")
    token = response.token
    user_id = verify_token(token)
    if user_id:
        print(f"   ✅ Token 有效！用户 ID: {user_id}")
    else:
        print(f"   ❌ Token 无效")
    
    print("\n" + "=" * 50)
    print("✅ 用户认证系统测试完成！")
