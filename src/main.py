"""
SoulMatch API Server
大学生恋爱交友平台 - 后端服务
"""
import os
import sys

from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional
import uvicorn

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import (
    APP_NAME, APP_VERSION, DEBUG, CORS_ORIGINS,
    JWT_ACCESS_TOKEN_EXPIRE
)
from backend.user_auth import (
    AuthService, RegisterRequest, LoginRequest, AuthResponse,
    verify_token  # 移除 get_current_user
)
from backend.questionnaire import (
    QuestionnaireService, QuestionnaireResponse,
    SubmitAnswersRequest, QuestionnaireResult
)
from backend.matching_algorithm import (
    MatchingAlgorithm, RecommendationEngine, UserValues, MatchResult
)


# ============================================
# 应用生命周期
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动/关闭"""
    from database.db import get_pool, close_pool
    
    # 启动时
    print(f"🦞 {APP_NAME} v{APP_VERSION} 启动中...")
    print(f"   环境：{'开发' if DEBUG else '生产'}")
    print(f"   数据库：PostgreSQL + Redis")
    print(f"   认证：JWT")
    
    # 初始化数据库连接池
    try:
        pool = await get_pool()
        print(f"   ✅ 数据库连接池已初始化")
    except Exception as e:
        print(f"   ⚠️  数据库连接失败: {e}")
        print(f"   继续启动，但部分功能可能不可用")
    
    yield
    
    # 关闭时
    print(f"🦞 {APP_NAME} 关闭中...")
    await close_pool()
    print(f"   ✅ 数据库连接池已关闭")


# ============================================
# FastAPI 应用
# ============================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="大学生恋爱交友平台 - 基于价值观匹配的深度社交",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全
security = HTTPBearer()

# 服务实例
auth_service = AuthService()
questionnaire_service = QuestionnaireService()
matching_algorithm = MatchingAlgorithm()
recommendation_engine = RecommendationEngine(matching_algorithm)


# ============================================
# 依赖注入
# ============================================

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """获取当前用户 ID"""
    token = credentials.credentials
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


# ============================================
# 健康检查
# ============================================

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION
    }


# ============================================
# 认证模块
# ============================================

@app.post("/api/auth/register", response_model=AuthResponse, tags=["认证"])
async def register(request: RegisterRequest):
    """用户注册"""
    try:
        return await auth_service.register(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/api/auth/login", response_model=AuthResponse, tags=["认证"])
async def login(request: LoginRequest):
    """用户登录"""
    try:
        return await auth_service.login(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@app.get("/api/auth/me", tags=["认证"])
async def get_me(user_id: str = Depends(get_current_user_id)):
    """获取当前用户信息"""
    user_info = await auth_service.get_user_info(user_id)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return {"success": True, "data": user_info}


# ============================================
# 问卷模块
# ============================================

@app.get("/api/questionnaire", response_model=QuestionnaireResponse, tags=["问卷"])
async def get_questionnaire():
    """获取问卷题目"""
    return questionnaire_service.get_questionnaire()


@app.post("/api/questionnaire/submit", tags=["问卷"])
async def submit_questionnaire(
    request: SubmitAnswersRequest,
    user_id: str = Depends(get_current_user_id)
):
    """提交问卷答案"""
    if not request.validate_answers():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="答案不完整或无效"
        )
    
    result = questionnaire_service.submit_answers(request.answers)
    
    # 计算各维度得分
    scores = {}
    for dim_key, (_, question_ids) in questionnaire_service.DIMENSION_MAP.items():
        total = 0
        count = 0
        for qid in question_ids:
            if qid in request.answers:
                total += request.answers[qid]
                count += 1
        scores[dim_key] = round(total / count, 2) if count > 0 else 0.0
    
    # 保存到数据库
    await questionnaire_service.save_user_values(
        user_id, request.answers, scores, result.tags
    )
    
    return {
        "success": True,
        "data": {
            "submitted_at": result.submitted_at,
            "dimensions": [
                {
                    "name": d.name,
                    "score": d.score,
                    "level": d.level,
                    "percentage": d.percentage
                }
                for d in result.dimensions
            ],
            "tags": result.tags,
            "summary": result.summary
        }
    }


@app.get("/api/questionnaire/result", tags=["问卷"])
async def get_questionnaire_result(user_id: str = Depends(get_current_user_id)):
    """获取问卷结果"""
    values = await questionnaire_service.get_user_values(user_id)
    if not values:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="问卷未完成"
        )
    
    # 构建维度得分
    dimensions = [
        {
            "name": "人生目标",
            "score": float(values['life_goals_score']),
            "level": questionnaire_service.get_score_level(float(values['life_goals_score'])),
            "percentage": int(float(values['life_goals_score']) * 20)
        },
        {
            "name": "性格特质",
            "score": float(values['personality_score']),
            "level": questionnaire_service.get_score_level(float(values['personality_score'])),
            "percentage": int(float(values['personality_score']) * 20)
        },
        {
            "name": "恋爱观念",
            "score": float(values['relationship_score']),
            "level": questionnaire_service.get_score_level(float(values['relationship_score'])),
            "percentage": int(float(values['relationship_score']) * 20)
        },
        {
            "name": "兴趣爱好",
            "score": float(values['interests_score']),
            "level": questionnaire_service.get_score_level(float(values['interests_score'])),
            "percentage": int(float(values['interests_score']) * 20)
        },
        {
            "name": "生活方式",
            "score": float(values['lifestyle_score']),
            "level": questionnaire_service.get_score_level(float(values['lifestyle_score'])),
            "percentage": int(float(values['lifestyle_score']) * 20)
        }
    ]
    
    return {
        "success": True,
        "data": {
            "completed_at": str(values['completed_at']),
            "dimensions": dimensions,
            "tags": list(values['tags']) if values['tags'] else [],
            "weights": questionnaire_service.get_default_weights()
        }
    }


# ============================================
# 匹配模块
# ============================================

async def get_candidates_from_db(user_id: str, gender: str = None) -> list:
    """从数据库获取候选用户"""
    from database.db import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        # 获取当前用户信息用于过滤
        current_user = await conn.fetchrow(
            "SELECT gender, birth_date, university_id FROM users WHERE id = $1::uuid",
            user_id
        )
        
        # 查询已完成问卷的其他用户（排除自己）
        query = """
            SELECT u.id::text, u.nickname, u.gender, u.birth_date, 
                   u.major, univ.name as university_name,
                   uv.life_goals_score, uv.personality_score, 
                   uv.relationship_score, uv.interests_score, 
                   uv.lifestyle_score, uv.tags
            FROM users u
            INNER JOIN user_values uv ON u.id = uv.user_id
            LEFT JOIN universities univ ON u.university_id = univ.id
            WHERE u.id != $1::uuid 
              AND u.status = 'active'
              AND uv.completed_at IS NOT NULL
        """
        params = [user_id]
        
        # 如果指定了性别过滤
        if gender:
            query += " AND u.gender = $" + str(len(params) + 1)
            params.append(gender)
        
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]


@app.get("/api/matching/daily", tags=["匹配"])
async def get_daily_recommendations(
    user_id: str = Depends(get_current_user_id)
):
    """获取每日推荐"""
    from database.db import get_pool
    from datetime import date, datetime
    import json
    
    pool = await get_pool()
    
    # 获取当前用户的价值观
    user_values = await questionnaire_service.get_user_values(user_id)
    if not user_values:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先完成问卷"
        )
    
    # 构建用户价值观对象
    current_values = UserValues(
        user_id=user_id,
        life_goals_score=float(user_values['life_goals_score']),
        personality_score=float(user_values['personality_score']),
        relationship_score=float(user_values['relationship_score']),
        interests_score=float(user_values['interests_score']),
        lifestyle_score=float(user_values['lifestyle_score']),
        tags=list(user_values['tags']) if user_values['tags'] else []
    )
    
    # 获取今日已推荐的用户ID（排除）
    today = date.today()
    async with pool.acquire() as conn:
        already_shown = await conn.fetch(
            """
            SELECT recommended_user_id::text FROM daily_recommendations 
            WHERE user_id = $1::uuid AND recommendation_date = $2
            """,
            user_id, today
        )
        shown_ids = [r['recommended_user_id'] for r in already_shown]
    
    # 获取候选用户
    candidates_data = await get_candidates_from_db(user_id)
    
    # 过滤掉已展示的用户
    candidates_data = [c for c in candidates_data if c['id'] not in shown_ids]
    
    # 使用匹配算法计算推荐
    recommendations = []
    for candidate in candidates_data:
        candidate_values = UserValues(
            user_id=candidate['id'],
            life_goals_score=float(candidate['life_goals_score']),
            personality_score=float(candidate['personality_score']),
            relationship_score=float(candidate['relationship_score']),
            interests_score=float(candidate['interests_score']),
            lifestyle_score=float(candidate['lifestyle_score']),
            tags=list(candidate['tags']) if candidate['tags'] else []
        )
        
        match_result = matching_algorithm.calculate_match(current_values, candidate_values)
        
        # 计算年龄
        birth_date = candidate['birth_date']
        if birth_date:
            age = (date.today() - birth_date).days // 365
        else:
            age = 0
        
        recommendations.append({
            "user_id": candidate['id'],
            "nickname": candidate['nickname'],
            "age": age,
            "university": candidate.get('university_name'),
            "major": candidate.get('major'),
            "tags": list(candidate['tags']) if candidate['tags'] else [],
            "match_score": match_result.match_percentage,
            "match_analysis": {
                "dimensions": [
                    {"name": d.name, "score": d.score, "level": d.level}
                    for d in match_result.dimension_scores
                ],
                "common_tags": match_result.tags_common,
                "complementary_tags": match_result.tags_complementary
            },
            "icebreaker": match_result.icebreaker
        })
    
    # 按匹配度排序，取前5个
    recommendations.sort(key=lambda x: x['match_score'], reverse=True)
    top_recommendations = recommendations[:5]
    
    # 保存推荐记录
    async with pool.acquire() as conn:
        for rank, rec in enumerate(top_recommendations, 1):
            await conn.execute(
                """
                INSERT INTO daily_recommendations 
                    (user_id, recommended_user_id, match_score, recommendation_date, recommendation_rank)
                VALUES ($1::uuid, $2::uuid, $3, $4, $5)
                ON CONFLICT (user_id, recommended_user_id, recommendation_date) DO NOTHING
                """,
                user_id, rec['user_id'], rec['match_score'] / 100, today, rank
            )
    
    return {
        "success": True,
        "data": {
            "date": str(today),
            "total_recommendations": len(top_recommendations),
            "remaining_today": len(candidates_data) - len(top_recommendations),
            "reset_time": str(datetime.combine(today, datetime.min.time()).replace(hour=0)) + "Z",
            "recommendations": top_recommendations
        }
    }


@app.post("/api/matching/action", tags=["匹配"])
async def do_matching_action(
    action: dict,
    user_id: str = Depends(get_current_user_id)
):
    """对推荐用户进行操作 (liked/skipped)"""
    from database.db import get_pool
    from datetime import date
    
    target_user_id = action.get("targetUserId")
    user_action = action.get("action")
    
    if not target_user_id or user_action not in ["liked", "skipped"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的操作"
        )
    
    pool = await get_pool()
    today = date.today()
    is_matched = False
    
    async with pool.acquire() as conn:
        # 更新推荐记录
        await conn.execute(
            """
            UPDATE daily_recommendations 
            SET user_action = $1, action_at = CURRENT_TIMESTAMP
            WHERE user_id = $2::uuid AND recommended_user_id = $3::uuid 
                  AND recommendation_date = $4
            """,
            user_action, user_id, target_user_id, today
        )
        
        # 检查是否匹配（对方也喜欢我）
        if user_action == "liked":
            # 检查是否有匹配记录
            existing_record = await conn.fetchrow(
                """
                SELECT id, user_a_action, user_b_action FROM match_records 
                WHERE (user_a_id = $1::uuid AND user_b_id = $2::uuid)
                   OR (user_a_id = $2::uuid AND user_b_id = $1::uuid)
                LIMIT 1
                """,
                user_id, target_user_id
            )
            
            if existing_record:
                # 更新当前用户的操作
                record_id = existing_record['id']
                user_a_action = existing_record['user_a_action']
                user_b_action = existing_record['user_b_action']
                
                # 确定当前用户是 A 还是 B
                record = await conn.fetchrow(
                    "SELECT user_a_id::text, user_b_id::text FROM match_records WHERE id = $1::uuid",
                    record_id
                )
                
                if record['user_a_id'] == user_id:
                    await conn.execute(
                        "UPDATE match_records SET user_a_action = $1, user_a_action_at = CURRENT_TIMESTAMP WHERE id = $2::uuid",
                        user_action, record_id
                    )
                    other_action = user_b_action
                else:
                    await conn.execute(
                        "UPDATE match_records SET user_b_action = $1, user_b_action_at = CURRENT_TIMESTAMP WHERE id = $2::uuid",
                        user_action, record_id
                    )
                    other_action = user_a_action
                
                # 如果双方都喜欢，则匹配成功
                if other_action == "liked":
                    is_matched = True
                    await conn.execute(
                        "UPDATE match_records SET is_matched = true, matched_at = CURRENT_TIMESTAMP WHERE id = $1::uuid",
                        record_id
                    )
                    # 创建会话
                    await conn.execute(
                        """
                        INSERT INTO conversations (match_record_id, user_a_id, user_b_id, last_message_at)
                        VALUES ($1::uuid, $2::uuid, $3::uuid, CURRENT_TIMESTAMP)
                        ON CONFLICT DO NOTHING
                        """,
                        record_id, 
                        record['user_a_id'] if record['user_a_id'] != user_id else record['user_b_id'],
                        user_id
                    )
            else:
                # 创建新的匹配记录（当前用户为A）
                await conn.execute(
                    """
                    INSERT INTO match_records (user_a_id, user_b_id, user_a_action, user_a_action_at, total_score, dimension_scores)
                    VALUES ($1::uuid, $2::uuid, $3, CURRENT_TIMESTAMP, 0.5, '[]'::jsonb)
                    """,
                    user_id, target_user_id, user_action
                )
    
    return {
        "success": True,
        "data": {
            "action": user_action,
            "is_matched": is_matched,
            "message": "恭喜匹配成功！" if is_matched else ("已表达喜欢，等待对方回应" if user_action == "liked" else "已跳过")
        }
    }


@app.get("/api/matching/skipped", tags=["匹配"])
async def get_skipped_users(
    user_id: str = Depends(get_current_user_id)
):
    """获取最近3天内跳过的用户"""
    from database.db import get_pool
    
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT dr.id::text, dr.action_at as skipped_at,
                   u.id::text as user_id, u.nickname, u.gender, u.birth_date,
                   univ.name as university_name,
                   dr.match_score, uv.tags, pr.custom_tags
            FROM daily_recommendations dr
            JOIN users u ON dr.recommended_user_id = u.id
            LEFT JOIN universities univ ON u.university_id = univ.id
            LEFT JOIN user_values uv ON u.id = uv.user_id
            LEFT JOIN user_profiles pr ON u.id = pr.user_id
            WHERE dr.user_id = $1::uuid 
              AND dr.user_action = 'skipped'
              AND dr.action_at >= CURRENT_TIMESTAMP - INTERVAL '3 days'
            ORDER BY dr.action_at DESC
            """,
            user_id
        )
        
        items = []
        from datetime import date
        for row in rows:
            birth_date = row['birth_date']
            age = (date.today() - birth_date).days // 365 if birth_date else 0
            
            # 合并标签
            all_tags = list(set(
                (list(row['tags']) if row['tags'] else []) +
                (list(row['custom_tags']) if row['custom_tags'] else [])
            ))
            
            items.append({
                "id": row['id'],
                "user_id": row['user_id'],
                "nickname": row['nickname'],
                "age": age,
                "university": row['university_name'],
                "tags": all_tags,
                "matchScore": int(float(row['match_score']) * 100) if row['match_score'] else 0,
                "skipped_at": str(row['skipped_at']) if row['skipped_at'] else None
            })
    
    return {
        "success": True,
        "data": {
            "items": items
        }
    }


@app.get("/api/matching/matches", tags=["匹配"])
async def get_matches(
    status: str = "all",
    page: int = 1,
    limit: int = 20,
    user_id: str = Depends(get_current_user_id)
):
    """获取匹配列表"""
    from database.db import get_pool
    
    pool = await get_pool()
    offset = (page - 1) * limit
    
    async with pool.acquire() as conn:
        # 构建查询
        where_clause = "(user_a_id = $1::uuid OR user_b_id = $1::uuid) AND is_matched = true"
        
        if status == "new":
            where_clause += " AND matched_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'"
        
        # 获取总数
        count_row = await conn.fetchrow(
            f"SELECT COUNT(*) as total FROM match_records WHERE {where_clause}",
            user_id
        )
        total = count_row['total']
        
        # 获取匹配列表
        rows = await conn.fetch(
            f"""
            SELECT mr.id::text, mr.total_score, mr.matched_at,
                   CASE WHEN mr.user_a_id = $1::uuid THEN mr.user_b_id ELSE mr.user_a_id END as matched_user_id
            FROM match_records mr
            WHERE {where_clause}
            ORDER BY mr.matched_at DESC
            LIMIT $2 OFFSET $3
            """,
            user_id, limit, offset
        )
        
        items = []
        for row in rows:
            # 获取匹配用户信息
            matched_user = await conn.fetchrow(
                """
                SELECT u.id::text, u.nickname, u.gender, u.birth_date, u.major,
                       univ.name as university_name, uv.tags
                FROM users u
                LEFT JOIN universities univ ON u.university_id = univ.id
                LEFT JOIN user_values uv ON u.id = uv.user_id
                WHERE u.id = $1::uuid
                """,
                row['matched_user_id']
            )
            
            if matched_user:
                from datetime import date
                birth_date = matched_user['birth_date']
                age = (date.today() - birth_date).days // 365 if birth_date else 0
                
                items.append({
                    "match_id": row['id'],
                    "user_id": matched_user['id'],
                    "nickname": matched_user['nickname'],
                    "gender": matched_user['gender'],
                    "age": age,
                    "university": matched_user.get('university_name'),
                    "major": matched_user.get('major'),
                    "tags": list(matched_user['tags']) if matched_user['tags'] else [],
                    "match_score": int(float(row['total_score']) * 100) if row['total_score'] else 0,
                    "matched_at": str(row['matched_at']) if row['matched_at'] else None
                })
    
    return {
        "success": True,
        "data": {
            "items": items,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "hasMore": offset + len(items) < total
            }
        }
    }


# ============================================
# 通知模块 - 获取收到的喜欢/交友请求
# ============================================

@app.get("/api/notifications", tags=["通知"])
async def get_notifications(user_id: str = Depends(get_current_user_id)):
    """获取通知列表（收到的喜欢/交友请求）"""
    from database.db import get_pool
    
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        # 获取当前用户作为 user_b 时的请求（即收到的请求）
        rows = await conn.fetch(
            """
            SELECT mr.id::text, mr.user_a_id::text as from_user_id, mr.user_a_action, 
                   mr.user_a_action_at as created_at, mr.total_score,
                   u.nickname, u.gender, u.birth_date, u.major,
                   univ.name as university_name, uv.tags,
                   pr.custom_tags
            FROM match_records mr
            JOIN users u ON mr.user_a_id = u.id
            LEFT JOIN universities univ ON u.university_id = univ.id
            LEFT JOIN user_values uv ON u.id = uv.user_id
            LEFT JOIN user_profiles pr ON u.id = pr.user_id
            WHERE mr.user_b_id = $1::uuid 
              AND mr.user_a_action IN ('liked', 'friendship')
              AND mr.user_a_action_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
            ORDER BY mr.user_a_action_at DESC
            """,
            user_id
        )

        items = []
        from datetime import date
        for row in rows:
            birth_date = row['birth_date']
            age = (date.today() - birth_date).days // 365 if birth_date else 0

            # 合并标签（问卷标签 + 自定义标签）
            all_tags = list(set(
                (list(row['tags']) if row['tags'] else []) +
                (list(row['custom_tags']) if row['custom_tags'] else [])
            ))

            items.append({
                "id": row['id'],
                "user_id": row['from_user_id'],
                "nickname": row['nickname'],
                "gender": row['gender'],
                "age": age,
                "university": row['university_name'],
                "major": row['major'],
                "tags": all_tags,
                "match_score": int(float(row['total_score']) * 100) if row['total_score'] else 0,
                "action": row['user_a_action'],
                "actionText": "喜欢了你" if row['user_a_action'] == 'liked' else "想和你交友",
                "status": "pending",
                "created_at": str(row['created_at']) if row['created_at'] else None,
                "is_read": True  # 暂时设为已读，后续可扩展
            })
    
    return {
        "success": True,
        "data": {
            "items": items,
            "total": len(items)
        }
    }


@app.post("/api/notifications/accept", tags=["通知"])
async def accept_notification(request: dict, user_id: str = Depends(get_current_user_id)):
    """同意对方的请求"""
    from database.db import get_pool
    
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        # 获取匹配记录
        match_row = await conn.fetchrow(
            """
            SELECT * FROM match_records WHERE id = $1::uuid AND user_b_id = $2::uuid
            """,
            request.get('notification_id'), user_id
        )
        
        if not match_row:
            raise HTTPException(status_code=404, detail="通知不存在")
        
        # 获取对方信息
        other_user = await conn.fetchrow(
            "SELECT nickname FROM users WHERE id = $1::uuid",
            match_row['user_a_id']
        )
        
        # 更新当前用户的回应
        action = 'liked' if match_row['user_a_action'] == 'liked' else 'friendship'
        await conn.execute(
            """
            UPDATE match_records 
            SET user_b_action = $1, user_b_action_at = CURRENT_TIMESTAMP
            WHERE id = $2::uuid
            """,
            action, request.get('notification_id')
        )
        
        # 检查是否双向喜欢/交友，更新匹配状态
        updated_row = await conn.fetchrow(
            "SELECT * FROM match_records WHERE id = $1::uuid",
            request.get('notification_id')
        )
        
        if updated_row['user_a_action'] in ['liked', 'friendship'] and \
           updated_row['user_b_action'] in ['liked', 'friendship']:
            
            # 创建会话
            await conn.execute(
                """
                INSERT INTO conversations (match_record_id, user_a_id, user_b_id)
                VALUES ($1::uuid, $2::uuid, $3::uuid)
                ON CONFLICT (match_record_id) DO NOTHING
                """,
                request.get('notification_id'),
                updated_row['user_a_id'],
                updated_row['user_b_id']
            )
            
            return {
                "success": True,
                "data": {
                    "matched": True,
                    "conversation_id": None,
                    "message": f"已和{other_user['nickname']}匹配成功！"
                }
            }
        
        return {
            "success": True,
            "data": {
                "matched": False,
                "message": "已回应"
            }
        }


@app.post("/api/notifications/decline", tags=["通知"])
async def decline_notification(request: dict, user_id: str = Depends(get_current_user_id)):
    """忽略/拒绝请求"""
    from database.db import get_pool
    
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE match_records 
            SET user_b_action = 'ignored', user_b_action_at = CURRENT_TIMESTAMP
            WHERE id = $1::uuid AND user_b_id = $2::uuid
            """,
            request.get('notification_id'), user_id
        )
    
    return {"success": True}


@app.post("/api/notifications/mark-read", tags=["通知"])
async def mark_notifications_read(user_id: str = Depends(get_current_user_id)):
    """标记所有通知为已读"""
    from database.db import get_pool
    
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE match_records 
            SET user_b_action = COALESCE(NULLIF(user_b_action, 'pending'), user_b_action),
                user_b_action_at = COALESCE(user_b_action_at, CURRENT_TIMESTAMP)
            WHERE user_b_id = $1::uuid 
              AND user_a_action IN ('liked', 'friendship')
              AND (user_b_action IS NULL OR user_b_action = 'pending')
            """,
            user_id
        )
    
    return {"success": True}


# ============================================
# 聊天模块
# ============================================

@app.get("/api/chat/conversations", tags=["聊天"])
async def get_conversations(
    page: int = 1,
    limit: int = 20,
    user_id: str = Depends(get_current_user_id)
):
    """获取聊天列表"""
    from database.db import get_pool
    
    pool = await get_pool()
    offset = (page - 1) * limit
    
    async with pool.acquire() as conn:
        # 获取总数
        count_row = await conn.fetchrow(
            """
            SELECT COUNT(*) as total FROM conversations 
            WHERE user_a_id = $1::uuid OR user_b_id = $1::uuid
            """,
            user_id
        )
        total = count_row['total']
        
        # 获取会话列表
        rows = await conn.fetch(
            """
            SELECT c.id::text, c.last_message_at, c.created_at,
                   CASE WHEN c.user_a_id = $1::uuid THEN c.user_b_id ELSE c.user_a_id END as other_user_id,
                   m.content as last_message, m.created_at as message_time
            FROM conversations c
            LEFT JOIN LATERAL (
                SELECT content, created_at FROM messages 
                WHERE conversation_id = c.id 
                ORDER BY created_at DESC LIMIT 1
            ) m ON true
            WHERE c.user_a_id = $1::uuid OR c.user_b_id = $1::uuid
            ORDER BY COALESCE(c.last_message_at, c.created_at) DESC
            LIMIT $2 OFFSET $3
            """,
            user_id, limit, offset
        )
        
        items = []
        for row in rows:
            # 获取对方用户信息（包含头像）
            other_user = await conn.fetchrow(
                """
                SELECT u.id::text, u.nickname, u.gender, u.birth_date,
                       univ.name as university_name,
                       pr.avatar_url
                FROM users u
                LEFT JOIN universities univ ON u.university_id = univ.id
                LEFT JOIN user_profiles pr ON u.id = pr.user_id
                WHERE u.id = $1::uuid
                """,
                row['other_user_id']
            )
            
            if other_user:
                from datetime import date
                birth_date = other_user['birth_date']
                age = (date.today() - birth_date).days // 365 if birth_date else 0
                
                # 获取未读消息数
                unread_row = await conn.fetchrow(
                    """
                    SELECT COUNT(*) as unread FROM messages 
                    WHERE conversation_id = $1::uuid AND sender_id != $2::uuid AND is_read = false
                    """,
                    row['id'], user_id
                )
                
                items.append({
                    "conversation_id": row['id'],
                    "user_id": other_user['id'],
                    "nickname": other_user['nickname'],
                    "gender": other_user['gender'],
                    "age": age,
                    "university": other_user.get('university_name'),
                    "avatar": other_user.get('avatar_url') or '/avatars/default.svg',
                    "last_message": row['last_message'],
                    "last_message_at": str(row['message_time']) if row['message_time'] else None,
                    "unread_count": unread_row['unread'] if unread_row else 0
                })
    
    return {
        "success": True,
        "data": {
            "items": items,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "hasMore": offset + len(items) < total
            }
        }
    }


@app.get("/api/chat/conversation/{other_user_id}", tags=["聊天"])
async def get_conversation_by_user(
    other_user_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """通过用户ID获取会话ID"""
    from database.db import get_pool
    
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        # 查找当前用户与指定用户之间的会话
        conv = await conn.fetchrow(
            """
            SELECT id::text FROM conversations 
            WHERE (user_a_id = $1::uuid AND user_b_id = $2::uuid)
               OR (user_a_id = $2::uuid AND user_b_id = $1::uuid)
            """,
            user_id, other_user_id
        )
        
        if not conv:
            return {
                "success": False,
                "error": "会话不存在"
            }
        
        return {
            "success": True,
            "data": {
                "conversation_id": conv['id']
            }
        }


@app.get("/api/user/{user_id}", tags=["用户"])
async def get_user_profile(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """获取其他用户的基本信息"""
    from database.db import get_pool
    from datetime import date
    
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        # 获取用户基本信息
        user_row = await conn.fetchrow(
            """
            SELECT u.id::text, u.nickname, u.gender, u.birth_date, u.major,
                   univ.name as university_name,
                   pr.avatar_url, pr.bio, pr.custom_tags
            FROM users u
            LEFT JOIN universities univ ON u.university_id = univ.id
            LEFT JOIN user_profiles pr ON u.id = pr.user_id
            WHERE u.id = $1::uuid
            """,
            user_id
        )
        
        if not user_row:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        birth_date = user_row['birth_date']
        age = (date.today() - birth_date).days // 365 if birth_date else 0
        
        return {
            "id": user_row['id'],
            "nickname": user_row['nickname'],
            "gender": user_row['gender'],
            "age": age,
            "university": user_row['university_name'],
            "major": user_row['major'],
            "avatar": user_row['avatar_url'] or '/avatars/default.svg',
            "bio": user_row['bio'],
            "tags": list(user_row['custom_tags']) if user_row['custom_tags'] else []
        }


@app.get("/api/chat/messages/{conversation_id}", tags=["聊天"])
async def get_messages(
    conversation_id: str,
    before: Optional[str] = None,
    limit: int = 20,
    user_id: str = Depends(get_current_user_id)
):
    """获取聊天记录"""
    from database.db import get_pool
    from datetime import datetime
    
    pool = await get_pool()
    
    # 验证用户是否有权限访问此会话
    async with pool.acquire() as conn:
        conv = await conn.fetchrow(
            """
            SELECT id FROM conversations 
            WHERE id = $1::uuid AND (user_a_id = $2::uuid OR user_b_id = $2::uuid)
            """,
            conversation_id, user_id
        )
        
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此会话"
            )
        
        # 构建查询
        query = """
            SELECT m.id::text, m.sender_id::text, m.content, m.message_type,
                   m.is_read, m.created_at,
                   u.nickname as sender_nickname
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.conversation_id = $1::uuid
        """
        params = [conversation_id]
        
        if before:
            query += " AND m.created_at < $2"
            params.append(before)
        
        query += " ORDER BY m.created_at DESC LIMIT $" + str(len(params) + 1)
        params.append(limit)
        
        rows = await conn.fetch(query, *params)
        
        # 标记消息为已读
        await conn.execute(
            """
            UPDATE messages SET is_read = true, read_at = CURRENT_TIMESTAMP
            WHERE conversation_id = $1::uuid AND sender_id != $2::uuid AND is_read = false
            """,
            conversation_id, user_id
        )
        
        # 更新会话最后消息时间
        if rows:
            await conn.execute(
                "UPDATE conversations SET last_message_at = $1::timestamp WHERE id = $2::uuid",
                rows[0]['created_at'], conversation_id
            )
        
        messages = [
            {
                "message_id": row['id'],
                "sender_id": row['sender_id'],
                "sender_nickname": row['sender_nickname'],
                "content": row['content'],
                "type": row['message_type'],
                "is_mine": row['sender_id'] == user_id,
                "created_at": str(row['created_at'])
            }
            for row in reversed(rows)  # 按时间正序
        ]
    
    return {
        "success": True,
        "data": {
            "messages": messages,
            "hasMore": len(rows) == limit
        }
    }


@app.post("/api/chat/messages", tags=["聊天"])
async def send_message(
    message: dict,
    user_id: str = Depends(get_current_user_id)
):
    """发送消息"""
    from database.db import get_pool
    
    conversation_id = message.get("conversationId")
    content = message.get("content")
    message_type = message.get("type", "text")
    
    if not conversation_id or not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少必要参数"
        )
    
    if len(content) > 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="消息内容过长"
        )
    
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        # 验证用户是否有权限发送消息
        conv = await conn.fetchrow(
            """
            SELECT id FROM conversations 
            WHERE id = $1::uuid AND (user_a_id = $2::uuid OR user_b_id = $2::uuid)
            """,
            conversation_id, user_id
        )
        
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权在此会话发送消息"
            )
        
        # 插入消息
        row = await conn.fetchrow(
            """
            INSERT INTO messages (conversation_id, sender_id, content, message_type)
            VALUES ($1::uuid, $2::uuid, $3, $4)
            RETURNING id::text, created_at
            """,
            conversation_id, user_id, content, message_type
        )
        
        # 更新会话最后消息时间
        await conn.execute(
            "UPDATE conversations SET last_message_at = $1::timestamp WHERE id = $2::uuid",
            row['created_at'], conversation_id
        )
    
    return {
        "success": True,
        "data": {
            "message_id": row['id'],
            "content": content,
            "created_at": str(row['created_at'])
        }
    }


# ============================================
# AI 模块
# ============================================

@app.get("/api/ai/health", tags=["AI"])
async def ai_health_check():
    """AI 服务健康检查"""
    from backend.ai_service import get_ai_service, AIConfig
    import httpx
    
    status = {
        "provider": AIConfig.DEFAULT_PROVIDER,
        "models": {}
    }
    
    # 检查 Ollama 连接
    if AIConfig.DEFAULT_PROVIDER == AIConfig.PROVIDER_OLLAMA:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{AIConfig.OLLAMA_BASE_URL}/api/tags", timeout=5)
                if resp.status_code == 200:
                    models = resp.json().get("models", [])
                    status["models"]["ollama"] = {
                        "available": True,
                        "models": [m.get("name") for m in models]
                    }
                else:
                    status["models"]["ollama"] = {"available": False, "error": resp.text}
        except Exception as e:
            status["models"]["ollama"] = {"available": False, "error": str(e)}
    
    return {"success": True, "data": status}


@app.post("/api/ai/chat-suggestion", tags=["AI"])
async def get_chat_suggestion(
    request_data: dict,
    user_id: str = Depends(get_current_user_id)
):
    """获取聊天建议 - 基于双方资料、标签和聊天历史生成个性化建议"""
    from backend.ai_service import ChatSuggestionRequest, get_ai_service
    from database.db import get_pool
    
    target_user_id = request_data.get("targetUserId")
    chat_history = request_data.get("chatHistory", [])
    
    if not target_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少目标用户ID"
        )
    
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        # 获取当前用户完整信息
        current_user = await conn.fetchrow(
            """
            SELECT 
                u.nickname, 
                u.gender,
                u.city,
                u.university_id,
                univ.name as university_name,
                univ.short_name as university_short,
                uv.tags, 
                uv.personality_score,
                uv.life_goals_score,
                uv.relationship_score,
                uv.interests_score,
                uv.lifestyle_score,
                up.bio,
                up.custom_tags
            FROM users u
            LEFT JOIN universities univ ON u.university_id = univ.id
            LEFT JOIN user_values uv ON u.id = uv.user_id
            LEFT JOIN user_profiles up ON u.id = up.user_id
            WHERE u.id = $1::uuid
            """,
            user_id
        )
        
        # 获取目标用户完整信息
        target_user = await conn.fetchrow(
            """
            SELECT 
                u.nickname, 
                u.gender,
                u.city,
                u.university_id,
                univ.name as university_name,
                univ.short_name as university_short,
                uv.tags, 
                uv.personality_score,
                uv.life_goals_score,
                uv.relationship_score,
                uv.interests_score,
                uv.lifestyle_score,
                up.bio,
                up.custom_tags
            FROM users u
            LEFT JOIN universities univ ON u.university_id = univ.id
            LEFT JOIN user_values uv ON u.id = uv.user_id
            LEFT JOIN user_profiles up ON u.id = up.user_id
            WHERE u.id = $1::uuid
            """,
            target_user_id
        )
        
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="目标用户不存在"
            )
        
        # 计算共同标签（只读操作）
        user_tags = set(current_user['tags'] or []) | set(current_user['custom_tags'] or [])
        target_tags = set(target_user['tags'] or []) | set(target_user['custom_tags'] or [])
        common_tags = user_tags & target_tags
        common_tags_list = list(common_tags)[:10]  # 最多取10个
        
        # 性格描述映射
        personality_map = {
            (4.0, 5.0): "非常外向",
            (3.0, 4.0): "比较外向",
            (2.0, 3.0): "中等性格",
            (1.0, 2.0): "比较内向",
            (0.0, 1.0): "非常内向"
        }
        
        def get_personality_desc(score):
            if not score:
                return "未知"
            for (low, high), desc in personality_map.items():
                if low <= float(score) < high:
                    return desc
            return "未知"
        
        user_personality = get_personality_desc(current_user['personality_score'])
        target_personality = get_personality_desc(target_user['personality_score'])
        
        # 构建请求
        ai_request = ChatSuggestionRequest(
            user_id=user_id,
            user_nickname=current_user['nickname'] if current_user else "我",
            user_gender=current_user.get('gender', ''),
            user_city=current_user.get('city', ''),
            user_university=current_user.get('university_short') or current_user.get('university_name', ''),
            user_bio=current_user.get('bio', ''),
            user_tags=list(user_tags),
            user_personality=user_personality,
            user_dimension_scores={
                'life_goals': float(current_user['life_goals_score']) if current_user['life_goals_score'] else None,
                'relationship': float(current_user['relationship_score']) if current_user['relationship_score'] else None,
                'interests': float(current_user['interests_score']) if current_user['interests_score'] else None,
                'lifestyle': float(current_user['lifestyle_score']) if current_user['lifestyle_score'] else None,
            },
            target_nickname=target_user['nickname'] if target_user else "对方",
            target_gender=target_user.get('gender', ''),
            target_city=target_user.get('city', ''),
            target_university=target_user.get('university_short') or target_user.get('university_name', ''),
            target_bio=target_user.get('bio', ''),
            target_tags=list(target_tags),
            target_personality=target_personality,
            target_dimension_scores={
                'life_goals': float(target_user['life_goals_score']) if target_user['life_goals_score'] else None,
                'relationship': float(target_user['relationship_score']) if target_user['relationship_score'] else None,
                'interests': float(target_user['interests_score']) if target_user['interests_score'] else None,
                'lifestyle': float(target_user['lifestyle_score']) if target_user['lifestyle_score'] else None,
            },
            common_interests=common_tags_list,
            chat_history=chat_history
        )
        
        # 调用 AI 服务
        ai_service = get_ai_service()
        result = await ai_service.get_chat_suggestions(ai_request)
        
        return {
            "success": True,
            "data": {
                "suggestions": result.suggestions,
                "reason": result.reason,
                "common_interests": common_tags_list,
                "personality_match": {
                    "you": user_personality,
                    "target": target_personality
                }
            }
        }


@app.post("/api/ai/match-tags", tags=["AI"])
async def match_tags(
    request_data: dict,
    user_id: str = Depends(get_current_user_id)
):
    """智能标签语义匹配"""
    from backend.ai_service import TagMatchRequest, get_ai_service
    
    my_tags = request_data.get("myTags", [])
    candidate_tags = request_data.get("candidateTags", [])
    
    if not my_tags or not candidate_tags:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少标签数据"
        )
    
    ai_request = TagMatchRequest(
        my_tags=my_tags,
        candidate_tags=candidate_tags
    )
    
    ai_service = get_ai_service()
    result = await ai_service.match_tags(ai_request)
    
    return {
        "success": True,
        "data": {
            "matches": result.matches,
            "adjustedScore": result.adjusted_score,
            "hiddenInterests": result.hidden_interests
        }
    }


@app.post("/api/ai/assistant", tags=["AI"])
async def ai_assistant(
    request_data: dict,
    user_id: str = Depends(get_current_user_id)
):
    """
    AI 私人助理 - 支持多种模式
    
    Modes:
    - chat: 情感咨询/日常聊天
    - schedule: 约会/日程安排
    - destination: 目的地推荐
    - search: 寻找志同道合的人
    - advice: 恋爱建议
    """
    from backend.ai_service import AssistantRequest, AssistantMessage, get_ai_service
    from database.db import get_pool
    import json
    
    # 支持单条消息或多条消息
    single_message = request_data.get("message", "")
    messages = request_data.get("messages", [])
    mode = request_data.get("mode", "chat")
    
    # 获取用户完整信息
    pool = await get_pool()
    async with pool.acquire() as conn:
        user_info = await conn.fetchrow(
            """
            SELECT u.nickname, u.gender, u.city, u.birth_date,
                   uv.tags, uv.personality_score,
                   uv.life_goals_score, uv.relationship_score, 
                   uv.interests_score, uv.lifestyle_score,
                   up.bio, up.custom_tags, up.preferred_gender
            FROM users u
            LEFT JOIN user_values uv ON u.id = uv.user_id
            LEFT JOIN user_profiles up ON u.id = up.user_id
            WHERE u.id = $1::uuid
            """,
            user_id
        )
    
    user_tags = set(list(user_info['tags'] or []) + list(user_info['custom_tags'] or []))
    
    # 处理搜索模式
    recommended_users = []
    destinations = []
    
    if mode == "search" and single_message:
        # 解析用户想要寻找的类型
        search_prompt = f"""分析用户的交友需求，提取关键标签。

用户输入: {single_message}

请返回一个JSON格式的搜索条件：
{{
    "search_tags": ["标签1", "标签2"],
    "preferred_gender": "male/female/any",
    "description": "用户需求的简要描述"
}}

只返回JSON，不要其他内容。"""
        
        try:
            ai_service = get_ai_service()
            analysis = await ai_service.chat([{"role": "user", "content": search_prompt}])
            
            # 解析JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', analysis)
            if json_match:
                search_params = json.loads(json_match.group())
                search_tags = search_params.get("search_tags", [])
                preferred_gender = search_params.get("preferred_gender", "any")
                description = search_params.get("description", "")
                
                # 查询匹配的用户
                gender_filter = ""
                if preferred_gender == "male":
                    gender_filter = "AND u.gender = 'male'"
                elif preferred_gender == "female":
                    gender_filter = "AND u.gender = 'female'"
                
                # 构建标签搜索条件
                tag_conditions = ""
                if search_tags:
                    tag_placeholders = []
                    for i, tag in enumerate(search_tags[:5]):
                        tag_placeholders.append(f"${i+2}")
                    tag_conditions = f"AND (uv.tags && ARRAY[{', '.join(tag_placeholders)}]::text[] OR up.custom_tags && ARRAY[{', '.join(tag_placeholders)}]::text[])"
                
                query = f"""
                    SELECT DISTINCT u.id, u.nickname, u.gender, u.city,
                           COALESCE(uv.tags, '{{}}') as tags,
                           COALESCE(up.custom_tags, '{{}}') as custom_tags,
                           COALESCE(up.bio, '') as bio,
                           up.avatar_url,
                           -- 计算匹配分数
                           (
                               CASE WHEN uv.tags && $2::text[] THEN 0.3 ELSE 0 END +
                               CASE WHEN up.custom_tags && $2::text[] THEN 0.2 ELSE 0 END +
                               CASE WHEN u.gender = $3 THEN 0.2 ELSE 0 END +
                               CASE WHEN u.city IS NOT NULL THEN 0.1 ELSE 0 END +
                               COALESCE(uv.interests_score, 3.0) / 25.0
                           ) as match_score
                    FROM users u
                    LEFT JOIN user_values uv ON u.id = uv.user_id
                    LEFT JOIN user_profiles up ON u.id = up.user_id
                    WHERE u.id != $1::uuid
                      AND u.status = 'active'
                      {gender_filter}
                      {tag_conditions}
                    ORDER BY match_score DESC
                    LIMIT 5
                """
                
                params = [user_id, search_tags, preferred_gender if preferred_gender != "any" else None]
                search_results = await conn.fetch(query, *params)
                
                for r in search_results:
                    user_all_tags = list(set(list(r['tags'] or []) + list(r['custom_tags'] or [])))
                    recommended_users.append({
                        "id": str(r['id']),
                        "nickname": r['nickname'],
                        "gender": r['gender'],
                        "city": r['city'],
                        "tags": user_all_tags[:5],
                        "bio": r['bio'][:100] if r['bio'] else "",
                        "avatar": r['avatar_url'],
                        "match_score": float(r['match_score']) if r['match_score'] else 0
                    })
                
                # 如果没有找到结果，使用AI生成回复
                if not recommended_users:
                    pass  # 继续用AI回复
                    
        except Exception as e:
            print(f"Search error: {e}")
    
    elif mode == "destination" and single_message:
        # 目的地推荐模式 - 使用本地数据库
        from backend.destination_database import search_destinations, get_destinations
        
        user_city = user_info.get('city') if user_info else None
        
        # 从消息中提取关键词进行搜索
        destinations = search_destinations(single_message, city=user_city, limit=6)
        
        # 如果用户城市有特定推荐，优先展示
        if not destinations and user_city:
            # 尝试用通用关键词搜索
            destinations = search_destinations("约会", city=user_city, limit=6)
        
        # 如果还是没有结果，返回该城市的所有地点
        if not destinations:
            all_places = get_destinations(city=user_city)[:6]
            for p in all_places:
                p_copy = p.copy()
                p_copy["description"] = p_copy.pop("tips", "")
                p_copy["tags"] = [p_copy.pop("type", "")]
                destinations.append(p_copy)
    
    # 构建消息列表（支持单条消息）
    if single_message and not messages:
        assistant_messages = [AssistantMessage(role="user", content=single_message)]
    else:
        assistant_messages = [
            AssistantMessage(role=m["role"], content=m["content"])
            for m in messages
        ]
    
    # 构建请求
    ai_request = AssistantRequest(
        user_id=user_id,
        user_nickname=user_info['nickname'] if user_info else "用户",
        user_tags=list(user_tags),
        user_values={
            "life_goals": float(user_info['life_goals_score']) if user_info and user_info['life_goals_score'] else 0,
            "personality": float(user_info['personality_score']) if user_info and user_info['personality_score'] else 0,
            "relationship": float(user_info['relationship_score']) if user_info and user_info['relationship_score'] else 0,
            "interests": float(user_info['interests_score']) if user_info and user_info['interests_score'] else 0,
            "lifestyle": float(user_info['lifestyle_score']) if user_info and user_info['lifestyle_score'] else 0,
        },
        messages=assistant_messages,
        mode=mode
    )
    
    # 调用 AI 服务
    ai_service = get_ai_service()
    result = await ai_service.assistant(ai_request)
    
    # 如果是搜索模式且没有推荐用户，添加默认回复
    if mode == "search" and not recommended_users and result.response:
        recommended_users = []
    
    # 格式化目的地数据
    formatted_destinations = []
    for d in destinations:
        formatted_destinations.append({
            "name": d.get("name", ""),
            "description": d.get("tips", d.get("description", "")),
            "address": d.get("address", d.get("city", "")),
            "price": d.get("price", ""),
            "tags": [d.get("type", "")] if d.get("type") else [],
            "city": d.get("city", "")
        })
    
    return {
        "success": True,
        "data": {
            "response": result.response,
            "suggestions": result.suggestions,
            "actionData": result.action_data,
            "recommended_users": recommended_users,
            "destinations": formatted_destinations
        }
    }


# ============================================
# 用户资料模块
# ============================================

@app.get("/api/profile/me", tags=["资料"])
async def get_my_profile(user_id: str = Depends(get_current_user_id)):
    """获取自己的资料"""
    from database.db import get_pool
    
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        # 获取用户基本信息
        user_info = await auth_service.get_user_info(user_id)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 获取用户资料（向后兼容，检查列是否存在）
        try:
            profile_row = await conn.fetchrow(
                """
                SELECT avatar_url, bio, 
                       COALESCE(purpose, 'dating') as purpose,
                       COALESCE(custom_tags, '{}') as custom_tags,
                       preferred_gender, min_age, max_age,
                       preferred_locations, show_university, show_major, show_age
                FROM user_profiles WHERE user_id = $1::uuid
                """,
                user_id
            )
        except Exception:
            # 如果新列不存在，使用旧查询
            profile_row = await conn.fetchrow(
                """
                SELECT avatar_url, bio, preferred_gender, min_age, max_age,
                       preferred_locations, show_university, show_major, show_age
                FROM user_profiles WHERE user_id = $1::uuid
                """,
                user_id
            )
        
        profile_data = {
            "avatar": profile_row['avatar_url'] if profile_row else None,
            "bio": profile_row['bio'] if profile_row else None,
            "purpose": profile_row['purpose'] if profile_row else 'dating',
            "custom_tags": list(profile_row['custom_tags']) if profile_row and profile_row['custom_tags'] else [],
            "preferences": {
                "preferred_gender": profile_row['preferred_gender'] if profile_row else 'any',
                "min_age": profile_row['min_age'] if profile_row else 18,
                "max_age": profile_row['max_age'] if profile_row else 35,
                "preferred_locations": list(profile_row['preferred_locations']) if profile_row and profile_row['preferred_locations'] else [],
            } if profile_row else {},
            "visibility": {
                "show_university": profile_row['show_university'] if profile_row else False,
                "show_major": profile_row['show_major'] if profile_row else False,
                "show_age": profile_row['show_age'] if profile_row else True,
            } if profile_row else {}
        }
    
    # 获取问卷结果
    values = await questionnaire_service.get_user_values(user_id)
    values_data = {
        "dimensions": [],
        "tags": [],
        "weights": questionnaire_service.get_default_weights()
    }
    
    if values:
        values_data = {
            "dimensions": [
                {
                    "name": "人生目标",
                    "score": float(values['life_goals_score']),
                    "level": questionnaire_service.get_score_level(float(values['life_goals_score'])),
                    "percentage": int(float(values['life_goals_score']) * 20)
                },
                {
                    "name": "性格特质",
                    "score": float(values['personality_score']),
                    "level": questionnaire_service.get_score_level(float(values['personality_score'])),
                    "percentage": int(float(values['personality_score']) * 20)
                },
                {
                    "name": "恋爱观念",
                    "score": float(values['relationship_score']),
                    "level": questionnaire_service.get_score_level(float(values['relationship_score'])),
                    "percentage": int(float(values['relationship_score']) * 20)
                },
                {
                    "name": "兴趣爱好",
                    "score": float(values['interests_score']),
                    "level": questionnaire_service.get_score_level(float(values['interests_score'])),
                    "percentage": int(float(values['interests_score']) * 20)
                },
                {
                    "name": "生活方式",
                    "score": float(values['lifestyle_score']),
                    "level": questionnaire_service.get_score_level(float(values['lifestyle_score'])),
                    "percentage": int(float(values['lifestyle_score']) * 20)
                }
            ],
            "tags": list(values['tags']) if values['tags'] else [],
            "weights": questionnaire_service.get_default_weights()
        }
    
    return {
        "success": True,
        "data": {
            "user": user_info,
            "profile": profile_data,
            "values": values_data
        }
    }


@app.put("/api/profile/me", tags=["资料"])
async def update_my_profile(
    profile: dict,
    user_id: str = Depends(get_current_user_id)
):
    """更新自己的资料"""
    from database.db import get_pool
    from datetime import datetime
    
    pool = await get_pool()
    
    # 提取用户基本信息和资料信息
    nickname = profile.get("nickname")
    gender = profile.get("gender")
    birth_date = profile.get("birth_date")
    city = profile.get("city")
    university = profile.get("university")
    major = profile.get("major")
    avatar_url = profile.get("avatar")
    bio = profile.get("bio")
    
    # 交友目的
    purpose = profile.get("purpose", "dating")
    
    # 自定义标签
    custom_tags = profile.get("custom_tags", [])
    
    # 偏好设置
    preferred_gender = profile.get("preferred_gender", "any")
    min_age = profile.get("min_age", 18)
    max_age = profile.get("max_age", 35)
    preferred_locations = profile.get("preferred_locations", [])
    
    # 可见性设置
    show_university = profile.get("show_university", False)
    show_major = profile.get("show_major", False)
    show_age = profile.get("show_age", True)
    
    async with pool.acquire() as conn:
        # 更新用户基本信息
        user_update_fields = []
        user_params = [user_id]
        param_idx = 2
        
        if nickname:
            user_update_fields.append(f"nickname = ${param_idx}")
            user_params.append(nickname)
            param_idx += 1
        
        if gender:
            user_update_fields.append(f"gender = ${param_idx}")
            user_params.append(gender)
            param_idx += 1
        
        if birth_date:
            # 将字符串转换为日期对象
            if isinstance(birth_date, str):
                birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
            user_update_fields.append(f"birth_date = ${param_idx}")
            user_params.append(birth_date)
            param_idx += 1
        
        if city:
            user_update_fields.append(f"city = ${param_idx}")
            user_params.append(city)
            param_idx += 1
        
        if major:
            user_update_fields.append(f"major = ${param_idx}")
            user_params.append(major)
            param_idx += 1
        
        if university:
            # 根据大学名称查找 university_id
            univ_row = await conn.fetchrow(
                "SELECT id FROM universities WHERE name = $1",
                university
            )
            if univ_row:
                user_update_fields.append(f"university_id = ${param_idx}")
                user_params.append(univ_row['id'])
                param_idx += 1
        
        if user_update_fields:
            await conn.execute(
                f"UPDATE users SET {', '.join(user_update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = $1::uuid",
                *user_params
            )
        
        # 更新或创建用户资料（向后兼容）
        try:
            await conn.execute(
                """
                INSERT INTO user_profiles (
                    user_id, avatar_url, bio, purpose, custom_tags,
                    preferred_gender, min_age, max_age,
                    preferred_locations, show_university, show_major, show_age
                ) VALUES ($1::uuid, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                ON CONFLICT (user_id) DO UPDATE SET
                    avatar_url = COALESCE(EXCLUDED.avatar_url, user_profiles.avatar_url),
                    bio = COALESCE(EXCLUDED.bio, user_profiles.bio),
                    purpose = COALESCE(EXCLUDED.purpose, user_profiles.purpose),
                    custom_tags = COALESCE(EXCLUDED.custom_tags, user_profiles.custom_tags),
                    preferred_gender = COALESCE(EXCLUDED.preferred_gender, user_profiles.preferred_gender),
                    min_age = COALESCE(EXCLUDED.min_age, user_profiles.min_age),
                    max_age = COALESCE(EXCLUDED.max_age, user_profiles.max_age),
                    preferred_locations = COALESCE(EXCLUDED.preferred_locations, user_profiles.preferred_locations),
                    show_university = COALESCE(EXCLUDED.show_university, user_profiles.show_university),
                    show_major = COALESCE(EXCLUDED.show_major, user_profiles.show_major),
                    show_age = COALESCE(EXCLUDED.show_age, user_profiles.show_age),
                    updated_at = CURRENT_TIMESTAMP
                """,
                user_id, avatar_url, bio, purpose, custom_tags,
                preferred_gender, min_age, max_age,
                preferred_locations, show_university, show_major, show_age
            )
        except Exception:
            # 如果新列不存在，使用旧版 SQL
            await conn.execute(
                """
                INSERT INTO user_profiles (
                    user_id, avatar_url, bio,
                    preferred_gender, min_age, max_age,
                    preferred_locations, show_university, show_major, show_age
                ) VALUES ($1::uuid, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (user_id) DO UPDATE SET
                    avatar_url = COALESCE(EXCLUDED.avatar_url, user_profiles.avatar_url),
                    bio = COALESCE(EXCLUDED.bio, user_profiles.bio),
                    preferred_gender = COALESCE(EXCLUDED.preferred_gender, user_profiles.preferred_gender),
                    min_age = COALESCE(EXCLUDED.min_age, user_profiles.min_age),
                    max_age = COALESCE(EXCLUDED.max_age, user_profiles.max_age),
                    preferred_locations = COALESCE(EXCLUDED.preferred_locations, user_profiles.preferred_locations),
                    show_university = COALESCE(EXCLUDED.show_university, user_profiles.show_university),
                    show_major = COALESCE(EXCLUDED.show_major, user_profiles.show_major),
                    show_age = COALESCE(EXCLUDED.show_age, user_profiles.show_age),
                    updated_at = CURRENT_TIMESTAMP
                """,
                user_id, avatar_url, bio,
                preferred_gender, min_age, max_age,
                preferred_locations, show_university, show_major, show_age
            )
    
    return {
        "success": True,
        "data": {
            "updated_at": datetime.utcnow().isoformat()
        }
    }


# ============================================
# 主程序入口
# ============================================

if __name__ == "__main__":
    print("🦞 SoulMatch API Server")
    print("=" * 50)
    print(f"服务名称：{APP_NAME}")
    print(f"版本：{APP_VERSION}")
    print(f"环境：{'开发' if DEBUG else '生产'}")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG
    )
