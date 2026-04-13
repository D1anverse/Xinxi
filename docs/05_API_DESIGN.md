# 🔌 API 接口设计 - SoulMatch

> **Phase 1 任务 5/5** | 创建时间：2026-03-12  
> **框架**: Node.js + Express / FastAPI  
> **认证**: JWT

---

## 📐 API 规范

### 基础信息

- **Base URL**: `https://api.soulmatch.cn/v1`
- **协议**: HTTPS
- **数据格式**: JSON
- **认证方式**: Bearer Token (JWT)

### 响应格式

```json
// 成功响应
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}

// 错误响应
{
  "success": false,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "用户不存在"
  },
  "data": null
}

// 分页响应
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "hasMore": true
    }
  }
}
```

### HTTP 状态码

| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证/Token 过期 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 429 | 请求过于频繁 |
| 500 | 服务器错误 |

---

## 🔐 认证模块 (Auth)

### POST /auth/register

用户注册

```http
POST /auth/register
Content-Type: application/json

{
  "email": "student@tsinghua.edu.cn",
  "password": "SecurePass123!",
  "nickname": "小明",
  "gender": "male",
  "birthDate": "2002-05-15",
  "university": "清华大学",
  "major": "计算机科学",
  "degree": "bachelor",
  "enrollmentYear": 2020
}
```

响应：

```json
{
  "success": true,
  "data": {
    "userId": "uuid",
    "token": "jwt_token",
    "expiresIn": 604800,
    "requiresVerification": true,
    "verificationMethod": "edu_email"
  }
}
```

### POST /auth/login

用户登录

```http
POST /auth/login
Content-Type: application/json

{
  "email": "student@tsinghua.edu.cn",
  "password": "SecurePass123!"
}
```

响应：

```json
{
  "success": true,
  "data": {
    "userId": "uuid",
    "token": "jwt_token",
    "expiresIn": 604800,
    "needsCompleteProfile": false,
    "needsCompleteQuestionnaire": true
  }
}
```

### POST /auth/refresh

刷新 Token

```http
POST /auth/refresh
Authorization: Bearer {token}
```

响应：

```json
{
  "success": true,
  "data": {
    "token": "new_jwt_token",
    "expiresIn": 604800
  }
}
```

### POST /auth/verify

提交学生认证

```http
POST /auth/verify
Authorization: Bearer {token}
Content-Type: application/json

{
  "method": "edu_email",
  "data": {
    "studentId": "2020123456",
    "verificationCode": "ABC123"  // 发送到 edu 邮箱的验证码
  }
}
```

响应：

```json
{
  "success": true,
  "data": {
    "isVerified": true,
    "verifiedAt": "2026-03-12T19:00:00Z"
  }
}
```

---

## 📝 问卷模块 (Questionnaire)

### GET /questionnaire

获取问卷题目

```http
GET /questionnaire
Authorization: Bearer {token}
```

响应：

```json
{
  "success": true,
  "data": {
    "totalQuestions": 50,
    "estimatedTime": 15,
    "modules": [
      {
        "id": "life_goals",
        "name": "人生目标",
        "description": "了解你对未来的规划和期待",
        "questions": [
          {
            "id": "q1",
            "text": "未来 5 年，你最重要的目标是？",
            "options": [
              {"value": 1, "text": "事业有成，在职场上有所成就"},
              {"value": 2, "text": "组建家庭，拥有稳定的婚姻生活"},
              {"value": 3, "text": "继续深造，获得更高学历"},
              {"value": 4, "text": "环游世界，体验不同文化"},
              {"value": 5, "text": "创业成功，实现财务自由"}
            ]
          },
          // ... q2-q10
        ]
      },
      // ... 其他模块
    ]
  }
}
```

### POST /questionnaire/submit

提交问卷答案

```http
POST /questionnaire/submit
Authorization: Bearer {token}
Content-Type: application/json

{
  "answers": {
    "q1": 3,
    "q2": 5,
    // ... q3-q50
  }
}
```

响应：

```json
{
  "success": true,
  "data": {
    "submittedAt": "2026-03-12T19:00:00Z",
    "dimensions": {
      "life_goals": 4.2,
      "personality": 2.8,
      "relationship": 3.5,
      "interests": 4.0,
      "lifestyle": 3.2
    },
    "tags": ["事业型", "内向型"],
    "isComplete": true
  }
}
```

### GET /questionnaire/result

获取问卷结果分析

```http
GET /questionnaire/result
Authorization: Bearer {token}
```

响应：

```json
{
  "success": true,
  "data": {
    "dimensions": [
      {
        "name": "人生目标",
        "score": 4.2,
        "level": "高",
        "description": "你非常重视事业发展和人生规划",
        "percentage": 84
      },
      // ... 其他维度
    ],
    "tags": ["事业型", "内向型", "传统型"],
    "summary": "你是一个注重事业发展的人，性格偏内向，在恋爱关系中期待稳定长久的关系..."
  }
}
```

### PUT /questionnaire/weights

调整匹配权重

```http
PUT /questionnaire/weights
Authorization: Bearer {token}
Content-Type: application/json

{
  "weights": {
    "life_goals": 0.35,
    "personality": 0.25,
    "relationship": 0.25,
    "interests": 0.10,
    "lifestyle": 0.05
  }
}
```

响应：

```json
{
  "success": true,
  "data": {
    "weights": { ... },
    "updatedAt": "2026-03-12T19:00:00Z"
  }
}
```

---

## 💕 匹配模块 (Matching)

### GET /matching/daily

获取每日推荐

```http
GET /matching/daily
Authorization: Bearer {token}
```

响应：

```json
{
  "success": true,
  "data": {
    "date": "2026-03-12",
    "totalRecommendations": 5,
    "remainingToday": 3,
    "resetTime": "2026-03-13T00:00:00Z",
    "recommendations": [
      {
        "rank": 1,
        "user": {
          "id": "uuid",
          "nickname": "小雨",
          "avatar": "https://...",
          "age": 20,
          "university": "北京大学",
          "major": "汉语言文学",
          "tags": ["家庭型", "外向型"]
        },
        "matchScore": 0.87,
        "matchAnalysis": {
          "total": 87,
          "dimensions": [
            {"name": "人生目标", "score": 95, "level": "高度契合"},
            {"name": "性格特质", "score": 80, "level": "较为契合"},
            {"name": "恋爱观念", "score": 90, "level": "高度契合"},
            {"name": "兴趣爱好", "score": 70, "level": "中等契合"},
            {"name": "生活方式", "score": 85, "level": "较为契合"}
          ]
        },
        "icebreaker": "你们都提到了对旅行的热爱，可以聊聊去过的地方！",
        "action": null  // liked, skipped, null
      },
      // ... 更多推荐
    ]
  }
}
```

### POST /matching/action

对推荐用户进行操作

```http
POST /matching/action
Authorization: Bearer {token}
Content-Type: application/json

{
  "targetUserId": "uuid",
  "action": "liked"  // liked, skipped
}
```

响应：

```json
{
  "success": true,
  "data": {
    "action": "liked",
    "isMatched": false,  // 是否双向匹配
    "message": "已表达喜欢，等待对方回应"
  }
}
```

### GET /matching/matches

获取匹配列表

```http
GET /matching/matches
Authorization: Bearer {token}
Query: ?status=pending|matched|all&page=1&limit=20
```

响应：

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "matchId": "uuid",
        "user": {
          "id": "uuid",
          "nickname": "小雨",
          "avatar": "https://...",
          "age": 20
        },
        "matchScore": 0.87,
        "matchedAt": "2026-03-12T10:00:00Z",
        "conversationId": "uuid",
        "lastMessage": {
          "content": "你好呀！",
          "senderId": "uuid",
          "createdAt": "2026-03-12T10:05:00Z",
          "isRead": false
        }
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 5,
      "hasMore": false
    }
  }
}
```

### GET /matching/stats

获取匹配统计

```http
GET /matching/stats
Authorization: Bearer {token}
```

响应：

```json
{
  "success": true,
  "data": {
    "totalLikes": 15,
    "totalMatches": 5,
    "pendingLikes": 10,
    "matchRate": 0.33,
    "weeklyStats": {
      "likesReceived": 8,
      "matchesMade": 2
    }
  }
}
```

---

## 💬 聊天模块 (Chat)

### GET /chat/conversations

获取聊天列表

```http
GET /chat/conversations
Authorization: Bearer {token}
Query: ?page=1&limit=20
```

响应：

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "conversationId": "uuid",
        "partner": {
          "id": "uuid",
          "nickname": "小雨",
          "avatar": "https://...",
          "isOnline": true
        },
        "lastMessage": {
          "content": "你好呀！",
          "senderId": "uuid",
          "createdAt": "2026-03-12T10:05:00Z",
          "isRead": false
        },
        "unreadCount": 2,
        "updatedAt": "2026-03-12T10:05:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 5,
      "hasMore": false
    }
  }
}
```

### GET /chat/messages/:conversationId

获取聊天记录

```http
GET /chat/messages/:conversationId
Authorization: Bearer {token}
Query: ?before=timestamp&limit=20
```

响应：

```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": "uuid",
        "senderId": "uuid",
        "sender": {
          "id": "uuid",
          "nickname": "小雨"
        },
        "content": "你好呀！",
        "type": "text",
        "createdAt": "2026-03-12T10:05:00Z",
        "isRead": true
      }
    ],
    "hasMore": true,
    "nextBefore": "2026-03-12T10:00:00Z"
  }
}
```

### POST /chat/messages

发送消息

```http
POST /chat/messages
Authorization: Bearer {token}
Content-Type: application/json

{
  "conversationId": "uuid",
  "content": "你好，很高兴认识你！",
  "type": "text"  // text, image
}
```

响应：

```json
{
  "success": true,
  "data": {
    "messageId": "uuid",
    "content": "你好，很高兴认识你！",
    "createdAt": "2026-03-12T19:00:00Z"
  }
}
```

### POST /chat/read

标记消息已读

```http
POST /chat/read
Authorization: Bearer {token}
Content-Type: application/json

{
  "conversationId": "uuid",
  "messageIds": ["uuid1", "uuid2"]
}
```

响应：

```json
{
  "success": true,
  "data": {
    "markedCount": 2
  }
}
```

---

## 👤 用户资料模块 (Profile)

### GET /profile/me

获取自己的资料

```http
GET /profile/me
Authorization: Bearer {token}
```

响应：

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "student@tsinghua.edu.cn",
      "nickname": "小明",
      "gender": "male",
      "birthDate": "2002-05-15",
      "age": 23,
      "university": "清华大学",
      "major": "计算机科学",
      "degree": "bachelor",
      "isVerified": true
    },
    "profile": {
      "avatar": "https://...",
      "bio": "热爱编程和旅行",
      "preferredGender": "female",
      "minAge": 20,
      "maxAge": 25,
      "showUniversity": false,
      "showMajor": false,
      "showAge": true
    },
    "values": {
      "dimensions": { ... },
      "tags": ["事业型", "内向型"],
      "weights": { ... }
    }
  }
}
```

### PUT /profile/me

更新自己的资料

```http
PUT /profile/me
Authorization: Bearer {token}
Content-Type: application/json

{
  "nickname": "小明",
  "bio": "热爱编程和旅行",
  "avatar": "https://...",
  "preferences": {
    "preferredGender": "female",
    "minAge": 20,
    "maxAge": 25,
    "showUniversity": false
  }
}
```

响应：

```json
{
  "success": true,
  "data": {
    "updatedAt": "2026-03-12T19:00:00Z"
  }
}
```

### GET /profile/:userId

查看他人资料

```http
GET /profile/:userId
Authorization: Bearer {token}
```

响应：

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "nickname": "小雨",
      "avatar": "https://...",
      "age": 20,
      "university": "北京大学",  // 根据隐私设置可能隐藏
      "major": "汉语言文学",
      "isVerified": true
    },
    "profile": {
      "bio": "喜欢阅读和旅行",
      "tags": ["家庭型", "外向型"]
    },
    "values": {
      "dimensions": [
        {"name": "人生目标", "score": 4.0, "percentage": 80},
        // ...
      ],
      "compatibility": {
        "totalScore": 0.87,
        "dimensions": [...]
      }
    },
    "relationship": {
      "isMatched": false,
      "hasLiked": true,
      "canMessage": false
    }
  }
}
```

---

## 🚨 举报与反馈模块 (Report)

### POST /report/user

举报用户

```http
POST /report/user
Authorization: Bearer {token}
Content-Type: application/json

{
  "reportedUserId": "uuid",
  "reason": "harassment",  // harassment, fake_profile, spam, inappropriate
  "description": "该用户发送不当消息",
  "evidence": {
    "conversationId": "uuid",
    "messageIds": ["uuid1", "uuid2"]
  }
}
```

响应：

```json
{
  "success": true,
  "data": {
    "reportId": "uuid",
    "status": "pending",
    "createdAt": "2026-03-12T19:00:00Z"
  }
}
```

### POST /report/feedback

提交反馈

```http
POST /report/feedback
Authorization: Bearer {token}
Content-Type: application/json

{
  "type": "bug",  // bug, suggestion, other
  "title": "匹配页面显示异常",
  "description": "详细描述...",
  "screenshots": ["https://..."]
}
```

响应：

```json
{
  "success": true,
  "data": {
    "feedbackId": "uuid",
    "createdAt": "2026-03-12T19:00:00Z"
  }
}
```

---

## 🔔 通知模块 (Notification)

### GET /notifications

获取通知列表

```http
GET /notifications
Authorization: Bearer {token}
Query: ?type=all|match|message|system&page=1&limit=20
```

响应：

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "uuid",
        "type": "match",
        "title": "新的匹配！",
        "content": "你和小雨匹配成功了",
        "data": {
          "userId": "uuid",
          "conversationId": "uuid"
        },
        "isRead": false,
        "createdAt": "2026-03-12T10:00:00Z"
      }
    ],
    "unreadCount": 3,
    "pagination": { ... }
  }
}
```

### POST /notifications/read

标记通知已读

```http
POST /notifications/read
Authorization: Bearer {token}
Content-Type: application/json

{
  "notificationIds": ["uuid1", "uuid2"]
}
```

---

## 📊 统计模块 (Analytics)

### GET /analytics/personal

获取个人统计

```http
GET /analytics/personal
Authorization: Bearer {token}
Query: ?period=week|month
```

响应：

```json
{
  "success": true,
  "data": {
    "period": "week",
    "stats": {
      "profileViews": 25,
      "likesReceived": 8,
      "likesGiven": 12,
      "matchesMade": 3,
      "messagesSent": 45,
      "messagesReceived": 38
    },
    "trends": [
      {"date": "2026-03-06", "matches": 0},
      {"date": "2026-03-07", "matches": 1},
      // ...
    ]
  }
}
```

---

## ⚙️ 管理后台 API (Admin)

### GET /admin/users

获取用户列表

```http
GET /admin/users
Authorization: Bearer {admin_token}
Query: ?status=all|active|suspended&page=1&limit=50
```

### POST /admin/users/:id/suspend

封禁用户

```http
POST /admin/users/:id/suspend
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "reason": "违反社区规范",
  "duration": 7  // 天数，0 表示永久
}
```

### GET /admin/reports

获取举报列表

```http
GET /admin/reports
Authorization: Bearer {admin_token}
Query: ?status=pending&priority=high
```

### POST /admin/reports/:id/resolve

处理举报

```http
POST /admin/reports/:id/resolve
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "action": "warn",  // warn, suspend, ban, dismiss
  "resolution": "已警告用户"
}
```

---

## 🔒 安全与限流

### 认证中间件

```javascript
// JWT 验证中间件
app.use('/api/v1/*', (req, res, next) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ error: { code: 'UNAUTHORIZED', message: '未认证' } });
  }
  
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.userId = decoded.userId;
    next();
  } catch (e) {
    return res.status(401).json({ error: { code: 'TOKEN_EXPIRED', message: 'Token 已过期' } });
  }
});
```

### 限流配置

```javascript
// 使用 express-rate-limit
const rateLimit = require('express-rate-limit');

// 通用限流
const generalLimiter = rateLimit({
  windowMs: 60 * 1000,  // 1 分钟
  max: 100  // 最多 100 次请求
});

// 滑动操作限流
const swipeLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 20  // 每分钟最多滑动 20 次
});

// 消息限流
const messageLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 10  // 每分钟最多发送 10 条消息
});
```

---

## 🧪 错误码定义

```javascript
const ERROR_CODES = {
  // 认证相关
  'UNAUTHORIZED': '未认证',
  'TOKEN_EXPIRED': 'Token 已过期',
  'INVALID_CREDENTIALS': '邮箱或密码错误',
  'USER_NOT_FOUND': '用户不存在',
  'EMAIL_EXISTS': '邮箱已被注册',
  
  // 问卷相关
  'QUESTIONNAIRE_NOT_COMPLETED': '问卷未完成',
  'INVALID_ANSWER': '答案无效',
  
  // 匹配相关
  'NO_MORE_RECOMMENDATIONS': '今日推荐已用完',
  'CANNOT_LIKE_SELF': '不能喜欢自己',
  'ALREADY_LIKED': '已操作过',
  
  // 聊天相关
  'CONVERSATION_NOT_FOUND': '会话不存在',
  'CANNOT_MESSAGE': '无法发送消息（未匹配）',
  'MESSAGE_TOO_LONG': '消息过长',
  
  // 举报相关
  'REPORT_SUBMITTED': '举报已提交',
  'INVALID_REPORT': '举报信息无效',
  
  // 系统相关
  'RATE_LIMITED': '请求过于频繁',
  'SERVER_ERROR': '服务器错误',
  'MAINTENANCE': '系统维护中'
};
```

---

## ⏭️ Phase 1 完成清单

- [x] 用户画像定义
- [x] 价值观问卷设计
- [x] 匹配算法设计
- [x] 数据库设计
- [x] API 接口设计

**Phase 1 完成！准备进入 Phase 2: 后端基础开发** 🎉

---

_文档状态：✅ 完成_  
_创建时间：2026-03-12 19:16_
