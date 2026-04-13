# 🧮 匹配算法设计 - SoulMatch

> **Phase 1 任务 3/5** | 创建时间：2026-03-12  
> **核心理念**: 价值观匹配，而非外表筛选

---

## 🎯 算法目标

1. **精准匹配** - 找到价值观契合的潜在伴侣
2. **可解释性** - 用户能理解"为什么匹配"
3. **可调节性** - 用户可调整各维度权重
4. **公平性** - 双向匹配，避免单向骚扰
5. **效率** - 在大量用户中快速找到最优匹配

---

## 📊 用户向量表示

### 基础向量结构

每个用户完成问卷后，生成一个 50 维的原始向量：

```
User = [q1, q2, q3, ..., q50]
其中 qi ∈ {1, 2, 3, 4, 5} (对应选项 A-E)
```

### 维度聚合向量

将 50 题聚合为 5 个维度得分：

```
User_Dimensions = {
  "life_goals":     [q1, q2, ..., q10],    // 人生目标 (10 题)
  "personality":    [q11, q12, ..., q20],  // 性格特质 (10 题)
  "relationship":   [q21, q22, ..., q30],  // 恋爱观念 (10 题)
  "interests":      [q31, q32, ..., q40],  // 兴趣爱好 (10 题)
  "lifestyle":      [q41, q42, ..., q50]   // 生活方式 (10 题)
}
```

### 维度得分计算

每个维度计算平均分（1-5 分）：

```python
def calculate_dimension_score(questions):
    return sum(questions) / len(questions)

# 示例
user_a = {
  "life_goals": 4.2,      # 偏向事业型
  "personality": 2.8,     # 偏内向
  "relationship": 3.5,    # 中等传统
  "interests": 4.0,       # 活跃型
  "lifestyle": 3.2        # 规律作息
}
```

---

## 🧮 相似度计算

### 1. 维度相似度（归一化欧氏距离）

对于每个维度，计算两个用户的相似度：

```python
def dimension_similarity(score_a, score_b, max_diff=4):
    """
    计算单个维度的相似度
    score_a, score_b: 两个用户在该维度的得分 (1-5)
    max_diff: 最大可能分差 (5-1=4)
    返回：0-1 之间的相似度，1 表示完全相同
    """
    diff = abs(score_a - score_b)
    similarity = 1 - (diff / max_diff)
    return similarity

# 示例
# 用户 A 人生目标得分 4.2，用户 B 得分 4.0
similarity = 1 - (|4.2 - 4.0| / 4) = 1 - 0.05 = 0.95 (95% 相似)
```

### 2. 加权总匹配度

根据用户设定的权重，计算总匹配度：

```python
def calculate_match_score(user_a, user_b, weights=None):
    """
    计算两个用户的总匹配度
    weights: 各维度权重，默认使用基础权重
    """
    if weights is None:
        weights = {
            "life_goals": 0.30,      # 30%
            "personality": 0.25,     # 25%
            "relationship": 0.25,    # 25%
            "interests": 0.10,       # 10%
            "lifestyle": 0.10        # 10%
        }
    
    total_score = 0
    for dimension in weights:
        sim = dimension_similarity(
            user_a[dimension], 
            user_b[dimension]
        )
        total_score += sim * weights[dimension]
    
    return total_score  # 0-1 之间

# 示例
# 维度相似度：life_goals=0.95, personality=0.80, relationship=0.90, interests=0.70, lifestyle=0.85
# 匹配度 = 0.95*0.30 + 0.80*0.25 + 0.90*0.25 + 0.70*0.10 + 0.85*0.10
#        = 0.285 + 0.20 + 0.225 + 0.07 + 0.085
#        = 0.865 (86.5%)
```

### 3. 余弦相似度（备选方案）

对于更精细的匹配，可使用余弦相似度：

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def cosine_similarity_score(user_a_vector, user_b_vector):
    """
    使用余弦相似度计算 50 维向量的相似性
    返回：0-1 之间的相似度
    """
    a = np.array(user_a_vector).reshape(1, -1)
    b = np.array(user_b_vector).reshape(1, -1)
    similarity = cosine_similarity(a, b)[0][0]
    # 余弦相似度范围 -1 到 1，转换为 0-1
    return (similarity + 1) / 2
```

---

## 🎚️ 用户权重调节

允许用户调整各维度权重，体现个人偏好：

### 默认权重

| 维度 | 默认权重 | 可调范围 |
|------|---------|---------|
| 人生目标 | 30% | 10% - 50% |
| 性格特质 | 25% | 10% - 40% |
| 恋爱观念 | 25% | 10% - 40% |
| 兴趣爱好 | 10% | 5% - 25% |
| 生活方式 | 10% | 5% - 25% |

### 权重调节 UI

```
请拖动滑块调整各维度重要性：

人生目标 ████████░░ 30% [━━━━━●━━━━━]
性格特质 ██████░░░░ 25% [━━━━━●━━━━━]
恋爱观念 ██████░░░░ 25% [━━━━━●━━━━━]
兴趣爱好 ███░░░░░░░ 10% [━━━━━●━━━━━]
生活方式 ███░░░░░░░ 10% [━━━━━●━━━━━]

总和必须为 100%
```

### 权重归一化

```python
def normalize_weights(raw_weights):
    """
    确保权重总和为 1
    """
    total = sum(raw_weights.values())
    return {k: v/total for k, v in raw_weights.items()}
```

---

## 🔍 匹配流程

### 整体流程

```
1. 用户完成问卷 → 生成价值观向量
   ↓
2. 筛选候选池（基础条件）
   - 性别偏好
   - 年龄范围
   - 学校类型（可选）
   - 地理位置
   ↓
3. 计算匹配度
   - 遍历候选池
   - 计算加权匹配度
   ↓
4. 排序与过滤
   - 按匹配度降序
   - 排除已看过/跳过的人
   - 排除已匹配的人
   ↓
5. 每日推荐 Top 5
   - 选择前 5 名
   - 确保多样性（避免过于相似）
   ↓
6. 用户操作
   - 喜欢 → 等待对方回应
   - 跳过 → 不再推荐
   - 双向喜欢 → 匹配成功，开启聊天
```

### 伪代码实现

```python
class MatchingEngine:
    def __init__(self, db):
        self.db = db
    
    def get_daily_recommendations(self, user_id, limit=5):
        """获取每日推荐"""
        user = self.db.get_user(user_id)
        
        # 1. 获取候选池
        candidates = self.db.get_candidates(
            gender=user.preferred_gender,
            age_range=user.preferred_age_range,
            exclude_viewed=user.viewed_profiles,
            exclude_matched=user.matched_profiles
        )
        
        # 2. 计算匹配度
        scored_candidates = []
        for candidate in candidates:
            score = self.calculate_match_score(user, candidate)
            scored_candidates.append((candidate, score))
        
        # 3. 排序
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # 4. 选择 Top N，确保多样性
        recommendations = self.ensure_diversity(
            scored_candidates[:limit*2],  # 先取多一些
            limit=limit
        )
        
        return recommendations
    
    def ensure_diversity(self, candidates, limit):
        """
        确保推荐结果有一定多样性
        避免推荐的 5 个人都高度相似
        """
        if len(candidates) <= limit:
            return [c[0] for c in candidates]
        
        selected = []
        selected_scores = []
        
        for candidate, score in candidates:
            if len(selected) >= limit:
                break
            
            # 检查与已选候选人的相似度
            is_similar = False
            for prev_score in selected_scores:
                if abs(score - prev_score) < 0.05:  # 匹配度太接近
                    is_similar = True
                    break
            
            if not is_similar or len(selected) < limit // 2:
                selected.append(candidate)
                selected_scores.append(score)
        
        # 如果多样性筛选后不够，补充剩余的
        while len(selected) < limit and candidates:
            candidate = candidates[len(selected)]
            if candidate[0] not in selected:
                selected.append(candidate[0])
        
        return selected
```

---

## 📈 匹配度解释

为了让用户理解匹配结果，提供详细的匹配分析：

### 匹配报告示例

```
💕 你们有 87% 的匹配度！

【高度契合】人生目标 (95%)
  你们都重视事业发展，对未来有相似规划

【较为契合】恋爱观念 (90%)
  都期待认真的关系，沟通方式相似

【中等契合】性格特质 (80%)
  你偏内向，他偏外向，可以互补

【需要磨合】兴趣爱好 (70%)
  兴趣有所不同，但可以互相分享

【中等契合】生活方式 (85%)
  作息时间相近，生活习惯相似

💡 破冰建议：
  你们都提到了对旅行的热爱，可以聊聊去过的地方！
```

### 生成匹配解释

```python
def generate_match_explanation(user_a, user_b, match_score):
    """生成匹配度解释"""
    dimensions = {
        "life_goals": "人生目标",
        "personality": "性格特质",
        "relationship": "恋爱观念",
        "interests": "兴趣爱好",
        "lifestyle": "生活方式"
    }
    
    explanation = {
        "total_score": match_score,
        "dimensions": []
    }
    
    for dim, name in dimensions.items():
        sim = dimension_similarity(user_a[dim], user_b[dim])
        level = get_similarity_level(sim)  # 高度契合/较为契合/中等/需要磨合
        explanation["dimensions"].append({
            "name": name,
            "score": sim,
            "level": level,
            "description": generate_dimension_description(dim, user_a, user_b)
        })
    
    return explanation

def get_similarity_level(score):
    if score >= 0.9:
        return "高度契合"
    elif score >= 0.75:
        return "较为契合"
    elif score >= 0.6:
        return "中等契合"
    else:
        return "需要磨合"
```

---

## 🎯 特殊匹配策略

### 1. 互补匹配

某些维度上，差异可能是好事（如性格内向 + 外向）：

```python
def calculate_complementary_score(dim, score_a, score_b):
    """
    对于某些维度，计算互补得分而非相似得分
    """
    if dim == "personality":
        # 内向 + 外向可能互补
        # 假设 1-2 为内向，4-5 为外向
        if (score_a <= 2 and score_b >= 4) or (score_a >= 4 and score_b <= 2):
            return 0.9  # 互补加分
        elif (score_a <= 2 and score_b <= 2) or (score_a >= 4 and score_b >= 4):
            return 0.6  # 都内向或都外向，可能缺乏互补
        else:
            return 0.75  # 中等
    
    # 其他维度默认用相似度
    return dimension_similarity(score_a, score_b)
```

### 2. 硬性过滤条件

某些条件必须匹配，否则直接排除：

```python
HARD_FILTERS = {
    "gender_preference": True,      # 性别偏好必须匹配
    "age_range": True,              # 年龄必须在范围内
    "relationship_type": True,      # 恋爱类型（认真/随意）
    "has_children_preference": True # 对要孩子的态度
}

def apply_hard_filters(user, candidate):
    """应用硬性过滤"""
    # 性别偏好
    if user.preferred_gender != candidate.gender:
        return False
    
    # 年龄范围
    if not (user.min_age <= candidate.age <= user.max_age):
        return False
    
    # 恋爱类型（从问卷中推断）
    if user.relationship_type != candidate.relationship_type:
        return False
    
    return True
```

### 3. 协同过滤（后期优化）

基于用户行为优化推荐：

```python
def collaborative_filtering(user_id, viewed_profiles, liked_profiles):
    """
    基于相似用户的行为进行推荐
    后期用户量足够时使用
    """
    # 1. 找到相似用户
    similar_users = find_similar_users(user_id)
    
    # 2. 收集相似用户喜欢的人
    liked_by_similar = aggregate_likes(similar_users)
    
    # 3. 排除已看过的
    recommendations = filter_viewed(liked_by_similar, viewed_profiles)
    
    return recommendations
```

---

## 📊 数据库设计（匹配相关）

### 用户价值观表

```sql
CREATE TABLE user_values (
    user_id UUID PRIMARY KEY,
    
    -- 原始答案 (JSON)
    answers JSONB,  -- {q1: 3, q2: 5, ...}
    
    -- 维度得分
    life_goals_score DECIMAL(3,2),      -- 1.00-5.00
    personality_score DECIMAL(3,2),
    relationship_score DECIMAL(3,2),
    interests_score DECIMAL(3,2),
    lifestyle_score DECIMAL(3,2),
    
    -- 用户权重偏好
    weights JSONB,  -- {life_goals: 0.30, ...}
    
    -- 标签
    tags TEXT[],    -- [事业型，内向型，传统型]
    
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 匹配记录表

```sql
CREATE TABLE match_records (
    id UUID PRIMARY KEY,
    user_a_id UUID,
    user_b_id UUID,
    
    -- 匹配度详情
    total_score DECIMAL(5,4),  -- 0.0000-1.0000
    dimension_scores JSONB,    -- {life_goals: 0.95, ...}
    
    -- 用户操作
    user_a_action VARCHAR(20),  -- liked/skipped/pending
    user_b_action VARCHAR(20),
    
    -- 状态
    is_matched BOOLEAN,
    matched_at TIMESTAMP,
    
    created_at TIMESTAMP
);

CREATE INDEX idx_match_user_a ON match_records(user_a_id);
CREATE INDEX idx_match_user_b ON match_records(user_b_id);
CREATE INDEX idx_matched ON match_records(is_matched) WHERE is_matched = true;
```

### 每日推荐表

```sql
CREATE TABLE daily_recommendations (
    id UUID PRIMARY KEY,
    user_id UUID,
    recommended_user_id UUID,
    
    match_score DECIMAL(5,4),
    recommendation_date DATE,
    
    user_action VARCHAR(20),  -- liked/skipped/pending
    action_at TIMESTAMP,
    
    UNIQUE(user_id, recommended_user_id, recommendation_date)
);
```

---

## ⚡ 性能优化

### 1. 预计算匹配度

对于活跃用户，预计算与潜在候选人的匹配度：

```python
def precompute_matches(user_id):
    """
    后台任务：预计算匹配度
    每天凌晨运行
    """
    user = get_user(user_id)
    candidates = get_potential_candidates(user)
    
    for candidate in candidates:
        score = calculate_match_score(user, candidate)
        cache_match_score(user_id, candidate.id, score)
```

### 2. 缓存策略

```python
# Redis 缓存
# Key: match_score:{user_id}:{candidate_id}
# TTL: 24 小时

def get_cached_match_score(user_id, candidate_id):
    cached = redis.get(f"match_score:{user_id}:{candidate_id}")
    if cached:
        return float(cached)
    return None

def cache_match_score(user_id, candidate_id, score):
    redis.setex(
        f"match_score:{user_id}:{candidate_id}",
        86400,  # 24 小时
        score
    )
```

### 3. 分批计算

对于大量候选人，分批计算避免超时：

```python
def batch_calculate_matches(user_id, batch_size=100):
    candidates = get_all_candidates(user_id)
    
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i+batch_size]
        scores = []
        for candidate in batch:
            score = calculate_match_score(user, candidate)
            scores.append((candidate, score))
        
        # 保存结果
        save_batch_scores(user_id, batch, scores)
        
        # 避免过载
        time.sleep(0.1)
```

---

## 🧪 测试与验证

### 单元测试

```python
def test_dimension_similarity():
    assert dimension_similarity(3.0, 3.0) == 1.0
    assert dimension_similarity(1.0, 5.0) == 0.0
    assert dimension_similarity(2.0, 3.0) == 0.75
    assert dimension_similarity(4.5, 5.0) == 0.875

def test_match_score():
    user_a = {"life_goals": 4.0, "personality": 3.0, ...}
    user_b = {"life_goals": 4.0, "personality": 3.0, ...}
    score = calculate_match_score(user_a, user_b)
    assert score == 1.0  # 完全相同

def test_weight_normalization():
    raw = {"life_goals": 30, "personality": 25, ...}
    normalized = normalize_weights(raw)
    assert sum(normalized.values()) == 1.0
```

### A/B 测试

```python
# 测试不同权重配置的效果
# A 组：默认权重
# B 组：用户自定义权重
# 指标：匹配后聊天率、7 日留存率
```

---

## ⏭️ 下一步

1. ✅ 用户画像定义
2. ✅ 价值观问卷设计
3. ✅ 匹配算法设计
4. ⬜ 数据库设计
5. ⬜ API 接口设计

---

_文档状态：✅ 完成_  
_创建时间：2026-03-12 19:16_
