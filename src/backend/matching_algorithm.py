"""
SoulMatch 匹配算法系统
基于价值观维度的加权相似度计算
"""
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel
from datetime import datetime, date
import math
import os

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


# ============================================
# 数据模型
# ============================================

class UserValues(BaseModel):
    """用户价值观数据"""
    user_id: str
    life_goals_score: float
    personality_score: float
    relationship_score: float
    interests_score: float
    lifestyle_score: float
    tags: List[str] = []
    weights: Dict[str, float] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.weights is None:
            self.weights = {
                "life_goals": 0.30,
                "personality": 0.25,
                "relationship": 0.25,
                "interests": 0.10,
                "lifestyle": 0.10
            }
    
    def to_vector(self) -> Dict[str, float]:
        """转换为向量"""
        return {
            "life_goals": self.life_goals_score,
            "personality": self.personality_score,
            "relationship": self.relationship_score,
            "interests": self.interests_score,
            "lifestyle": self.lifestyle_score
        }


class DimensionCompatibility(BaseModel):
    """维度兼容性"""
    name: str
    score: float  # 0-1
    level: str  # 高度契合，较为契合，etc.
    user_a_score: float
    user_b_score: float


class MatchResult(BaseModel):
    """匹配结果"""
    user_a_id: str
    user_b_id: str
    total_score: float  # 0-1
    dimension_scores: List[DimensionCompatibility]
    match_percentage: int  # 0-100
    tags_common: List[str]
    tags_complementary: List[str]
    icebreaker: str


class Recommendation(BaseModel):
    """推荐用户"""
    user_id: str
    nickname: str
    age: int
    university: Optional[str]
    major: Optional[str]
    tags: List[str]
    match_score: float
    match_analysis: Dict[str, Any]
    icebreaker: str


# ============================================
# 匹配算法服务
# ============================================

class MatchingAlgorithm:
    """匹配算法服务"""
    
    # 维度名称映射
    DIMENSION_NAMES = {
        "life_goals": "人生目标",
        "personality": "性格特质",
        "relationship": "恋爱观念",
        "interests": "兴趣爱好",
        "lifestyle": "生活方式"
    }
    
    # 相似度等级
    SIMILARITY_LEVELS = [
        (0.90, "高度契合"),
        (0.80, "较为契合"),
        (0.70, "中等契合"),
        (0.60, "一般契合"),
        (0.00, "契合度较低")
    ]
    
    def calculate_dimension_similarity(
        self,
        score_a: float,
        score_b: float,
        max_diff: float = 4.0
    ) -> float:
        """
        计算单个维度的相似度
        
        使用归一化的绝对差值：similarity = 1 - (|a - b| / max_diff)
        分数范围 1-5，最大差值为 4
        """
        diff = abs(score_a - score_b)
        similarity = 1 - (diff / max_diff)
        return round(max(0, min(1, similarity)), 4)
    
    def get_similarity_level(self, score: float) -> str:
        """根据相似度分数返回等级描述"""
        for threshold, level in self.SIMILARITY_LEVELS:
            if score >= threshold:
                return level
        return self.SIMILARITY_LEVELS[-1][1]
    
    def calculate_weighted_similarity(
        self,
        values_a: UserValues,
        values_b: UserValues
    ) -> Tuple[float, List[DimensionCompatibility], float]:
        """
        计算加权相似度

        返回：(总分，各维度兼容性列表，tag匹配分数)
        """
        vector_a = values_a.to_vector()
        vector_b = values_b.to_vector()

        # 使用用户 A 的权重（实际中可取平均或各自权重）
        weights = values_a.weights or self._default_weights()

        total_score = 0.0
        dimension_scores = []

        for dim_key, dim_name in self.DIMENSION_NAMES.items():
            score_a = vector_a.get(dim_key, 0)
            score_b = vector_b.get(dim_key, 0)

            # 计算维度相似度
            similarity = self.calculate_dimension_similarity(score_a, score_b)

            # 应用权重
            weight = weights.get(dim_key, 0.20)
            weighted_score = similarity * weight
            total_score += weighted_score

            dimension_scores.append(DimensionCompatibility(
                name=dim_name,
                score=similarity,
                level=self.get_similarity_level(similarity),
                user_a_score=score_a,
                user_b_score=score_b
            ))

        # 计算 tag 匹配分数（0-1）
        tag_score = self.calculate_tag_similarity(values_a.tags, values_b.tags)

        # tag 匹配分数加成（权重0.15，即15%）
        # 共同标签越多，匹配度加成越高
        tag_boost = tag_score * 0.15

        return round(total_score, 4), dimension_scores, tag_score
    
    def _default_weights(self) -> Dict[str, float]:
        """默认权重"""
        return {
            "life_goals": 0.30,
            "personality": 0.25,
            "relationship": 0.25,
            "interests": 0.10,
            "lifestyle": 0.10
        }

    def calculate_tag_similarity(self, tags_a: List[str], tags_b: List[str]) -> float:
        """
        计算 tag 匹配分数（0-1）
        使用 Jaccard 相似度：交集 / 并集
        """
        if not tags_a or not tags_b:
            return 0.0

        set_a = set(tags_a)
        set_b = set(tags_b)

        intersection = len(set_a & set_b)
        union = len(set_a | set_b)

        if union == 0:
            return 0.0

        return intersection / union

    def find_common_tags(self, tags_a: List[str], tags_b: List[str]) -> List[str]:
        """找出共同标签"""
        return list(set(tags_a) & set(tags_b))
    
    def find_complementary_tags(self, tags_a: List[str], tags_b: List[str]) -> List[str]:
        """找出互补标签（简化版）"""
        # 内向 + 外向 是互补
        complementary_pairs = [
            ("内向型", "外向型"),
            ("事业型", "家庭型"),
            ("理性型", "感性型")
        ]
        
        complementary = []
        for tag_a, tag_b in complementary_pairs:
            if (tag_a in tags_a and tag_b in tags_b) or \
               (tag_b in tags_a and tag_a in tags_b):
                complementary.append(f"{tag_a}+{tag_b}")
        
        return complementary
    
    def generate_icebreaker(
        self,
        values_a: UserValues,
        values_b: UserValues,
        common_tags: List[str],
        dimension_scores: List[DimensionCompatibility]
    ) -> str:
        """生成破冰话题"""
        icebreakers = []
        
        # 基于共同标签
        tag_topics = {
            "事业型": "你们都很注重事业发展，可以聊聊各自的职业规划！",
            "家庭型": "你们都重视家庭，可以分享对理想家庭生活的期待～",
            "内向型": "看起来你们都比较内向，或许都享受安静的时光？",
            "外向型": "你们都很外向，一定有很多有趣的社交故事！",
            "传统型": "你们对恋爱关系都有传统的期待，这很难得～",
            "开放型": "你们都很开放包容，应该能聊很多有趣的话题！",
            "理性型": "你们都是理性思考型，讨论问题一定很有深度！",
            "感性型": "你们都很感性，一定能理解彼此的情感世界～"
        }
        
        for tag in common_tags[:2]:
            if tag in tag_topics:
                icebreakers.append(tag_topics[tag])
        
        # 基于高契合维度
        high_compat = [d for d in dimension_scores if d.score >= 0.85]
        if high_compat:
            dim = high_compat[0]
            icebreakers.append(
                f"你们在{dim.name}方面非常契合，这很难得！"
            )
        
        # 默认破冰
        if not icebreakers:
            icebreakers = [
                "基于你们的价值观匹配，相信会有很多共同话题！",
                "看起来你们有很多可以聊的，开始对话吧～"
            ]
        
        return icebreakers[0]
    
    def calculate_match(
        self,
        values_a: UserValues,
        values_b: UserValues
    ) -> MatchResult:
        """计算两个用户的匹配度"""
        base_score, dimension_scores, tag_score = self.calculate_weighted_similarity(
            values_a, values_b
        )

        # 最终分数 = 基础分数 + tag 匹配加成
        # tag 匹配加成最多 15 分（100% tag 匹配时）
        tag_boost = tag_score * 0.15
        total_score = min(base_score + tag_boost, 1.0)  # 最高不超过 1.0

        common_tags = self.find_common_tags(values_a.tags, values_b.tags)
        complementary_tags = self.find_complementary_tags(
            values_a.tags, values_b.tags
        )

        icebreaker = self.generate_icebreaker(
            values_a, values_b, common_tags, dimension_scores
        )

        return MatchResult(
            user_a_id=values_a.user_id,
            user_b_id=values_b.user_id,
            total_score=round(total_score, 4),
            dimension_scores=dimension_scores,
            match_percentage=int(total_score * 100),
            tags_common=common_tags,
            tags_complementary=complementary_tags,
            icebreaker=icebreaker
        )


class RecommendationEngine:
    """推荐引擎"""
    
    def __init__(self, matching_algorithm: MatchingAlgorithm = None):
        self.algorithm = matching_algorithm or MatchingAlgorithm()
        self.user_pool: Dict[str, UserValues] = {}
    
    def add_user(self, values: UserValues):
        """添加用户到池子"""
        self.user_pool[values.user_id] = values
    
    def get_candidate_pool(
        self,
        user_id: str,
        gender_preference: str,
        age_range: Tuple[int, int],
        exclude_ids: List[str] = None
    ) -> List[UserValues]:
        """
        获取候选池
        
        实际应用中应从数据库查询并过滤
        """
        exclude = set(exclude_ids or [])
        exclude.add(user_id)
        
        candidates = []
        for uid, values in self.user_pool.items():
            if uid in exclude:
                continue
            # 这里简化，实际应过滤性别、年龄等
            candidates.append(values)
        
        return candidates
    
    def generate_daily_recommendations(
        self,
        user_values: UserValues,
        candidates: List[UserValues],
        limit: int = 5
    ) -> List[Tuple[UserValues, MatchResult]]:
        """
        生成每日推荐
        
        返回：[(候选用户，匹配结果), ...]
        """
        scored_candidates = []
        
        for candidate in candidates:
            match = self.algorithm.calculate_match(user_values, candidate)
            scored_candidates.append((candidate, match))
        
        # 按匹配度排序
        scored_candidates.sort(key=lambda x: x[1].total_score, reverse=True)
        
        return scored_candidates[:limit]


# ============================================
# 余弦相似度实现（可选）
# ============================================

def cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    """
    计算余弦相似度
    
    cos(θ) = (A·B) / (||A|| × ||B||)
    """
    keys = set(vec_a.keys()) | set(vec_b.keys())
    
    dot_product = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in keys)
    norm_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    norm_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return round(dot_product / (norm_a * norm_b), 4)


# ============================================
# 测试代码
# ============================================

if __name__ == "__main__":
    print("🦞 SoulMatch 匹配算法测试")
    print("=" * 50)
    
    algorithm = MatchingAlgorithm()
    
    # 创建测试用户
    print("\n1️⃣ 创建测试用户...")
    user_a = UserValues(
        user_id="user_001",
        life_goals_score=4.2,
        personality_score=2.8,
        relationship_score=3.5,
        interests_score=4.0,
        lifestyle_score=3.2,
        tags=["事业型", "外向型"]
    )
    
    user_b = UserValues(
        user_id="user_002",
        life_goals_score=4.0,
        personality_score=3.0,
        relationship_score=3.8,
        interests_score=3.5,
        lifestyle_score=3.0,
        tags=["事业型", "内向型"]
    )
    
    user_c = UserValues(
        user_id="user_003",
        life_goals_score=2.5,
        personality_score=4.5,
        relationship_score=2.0,
        interests_score=3.0,
        lifestyle_score=4.0,
        tags=["家庭型", "内向型"]
    )
    
    print(f"   ✅ 用户 A: {user_a.tags}")
    print(f"   ✅ 用户 B: {user_b.tags}")
    print(f"   ✅ 用户 C: {user_c.tags}")
    
    # 测试匹配计算
    print("\n2️⃣ 计算用户 A 和 B 的匹配度...")
    match_ab = algorithm.calculate_match(user_a, user_b)
    print(f"   📊 总匹配度：{match_ab.match_percentage}%")
    print(f"   📊 各维度:")
    for dim in match_ab.dimension_scores:
        print(f"      - {dim.name}: {dim.score:.2f} ({dim.level})")
    print(f"   🏷️  共同标签：{match_ab.tags_common}")
    print(f"   💬 破冰话题：{match_ab.icebreaker}")
    
    print("\n3️⃣ 计算用户 A 和 C 的匹配度...")
    match_ac = algorithm.calculate_match(user_a, user_c)
    print(f"   📊 总匹配度：{match_ac.match_percentage}%")
    print(f"   🏷️  共同标签：{match_ac.tags_common}")
    print(f"   🏷️  互补标签：{match_ac.tags_complementary}")
    
    # 测试推荐引擎
    print("\n4️⃣ 测试推荐引擎...")
    engine = RecommendationEngine(algorithm)
    engine.add_user(user_a)
    engine.add_user(user_b)
    engine.add_user(user_c)
    
    recommendations = engine.generate_daily_recommendations(
        user_a,
        engine.get_candidate_pool("user_001", "any", (18, 35)),
        limit=2
    )
    
    print(f"   📋 为用户 A 推荐:")
    for candidate, match in recommendations:
        print(f"      - {candidate.user_id}: {match.match_percentage}% 匹配")
    
    # 测试余弦相似度
    print("\n5️⃣ 测试余弦相似度...")
    vec_a = user_a.to_vector()
    vec_b = user_b.to_vector()
    cosine_sim = cosine_similarity(vec_a, vec_b)
    print(f"   📐 余弦相似度：{cosine_sim:.4f}")
    
    print("\n" + "=" * 50)
    print("✅ 匹配算法测试完成！")
