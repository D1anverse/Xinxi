"""
SoulMatch AI 服务模块
支持 Ollama 本地模型 / Gemini API / 硅基流动 等多种后端
"""
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from openai import OpenAI
import httpx
import os
import json
import logging

logger = logging.getLogger(__name__)

# ============================================
# AI 服务配置
# ============================================

class AIConfig:
    """AI 服务配置"""
    
    # 支持的 AI 提供商
    PROVIDER_OLLAMA = "ollama"
    PROVIDER_GEMINI = "gemini"
    PROVIDER_SILICONFLOW = "siliconflow"
    
    # 默认配置
    DEFAULT_PROVIDER = os.getenv("AI_PROVIDER", PROVIDER_OLLAMA)
    
    # Ollama 配置 (本地部署)
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    
    # Gemini 配置 (Google AI)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # 硅基流动配置 (国内服务商)
    SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
    SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1"
    SILICONFLOW_MODEL = os.getenv("SILICONFLOW_MODEL", "deepseek-ai/DeepSeek-V2.5")
    
    # 请求配置
    REQUEST_TIMEOUT = 60  # 秒
    MAX_TOKENS = 2000
    TEMPERATURE = 0.7


# ============================================
# 请求/响应模型
# ============================================

class ChatSuggestionRequest(BaseModel):
    """聊天建议请求"""
    user_id: str
    user_nickname: str
    user_gender: str = ""
    user_city: str = ""
    user_university: str = ""
    user_bio: str = ""
    user_tags: List[str] = []
    user_personality: str = ""  # 性格描述（外向/内向）
    user_dimension_scores: Dict[str, Optional[float]] = {}  # 价值观维度得分
    target_nickname: str
    target_gender: str = ""
    target_city: str = ""
    target_university: str = ""
    target_bio: str = ""
    target_tags: List[str] = []
    target_personality: str = ""
    target_dimension_scores: Dict[str, Optional[float]] = {}
    common_interests: List[str] = []  # 共同兴趣标签
    chat_history: List[Dict[str, str]] = []  # [{"role": "user"/"assistant", "content": "..."}]


class ChatSuggestionResponse(BaseModel):
    """聊天建议响应"""
    suggestions: List[str]
    reason: str = ""


class TagMatchRequest(BaseModel):
    """标签语义匹配请求"""
    my_tags: List[str]
    candidate_tags: List[str]


class TagMatchResponse(BaseModel):
    """标签语义匹配响应"""
    matches: List[Dict[str, Any]]
    adjusted_score: float = 0.0
    hidden_interests: List[str] = []


class AssistantMessage(BaseModel):
    """助理对话消息"""
    role: Literal["user", "assistant", "system"]
    content: str


class AssistantRequest(BaseModel):
    """AI 助理请求"""
    user_id: str
    user_nickname: str
    user_tags: List[str] = []
    user_values: Dict[str, float] = {}  # 问卷各维度得分
    messages: List[AssistantMessage]
    mode: Literal["chat", "schedule", "search", "advice"] = "chat"


class AssistantResponse(BaseModel):
    """AI 助理响应"""
    response: str
    suggestions: List[str] = []
    action_data: Dict[str, Any] = {}  # 可能的结构化数据（如日程安排）


# ============================================
# AI 服务类
# ============================================

class AIService:
    """AI 服务统一接口"""
    
    def __init__(self, provider: str = None):
        self.provider = provider or AIConfig.DEFAULT_PROVIDER
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化 AI 客户端"""
        if self.provider == AIConfig.PROVIDER_OLLAMA:
            # Ollama 使用 OpenAI 兼容接口
            self._client = OpenAI(
                base_url=f"{AIConfig.OLLAMA_BASE_URL}/v1",
                api_key="ollama",  # Ollama 不需要真实 API key
                timeout=AIConfig.REQUEST_TIMEOUT
            )
            self._model = AIConfig.OLLAMA_MODEL
            
        elif self.provider == AIConfig.PROVIDER_GEMINI:
            # Gemini API
            if not AIConfig.GEMINI_API_KEY:
                logger.warning("Gemini API key not configured, falling back to Ollama")
                self.provider = AIConfig.PROVIDER_OLLAMA
                self._initialize_client()
                return
            self._client = OpenAI(
                api_key=AIConfig.GEMINI_API_KEY,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                timeout=AIConfig.REQUEST_TIMEOUT
            )
            self._model = AIConfig.GEMINI_MODEL
            
        elif self.provider == AIConfig.PROVIDER_SILICONFLOW:
            # 硅基流动
            if not AIConfig.SILICONFLOW_API_KEY:
                logger.warning("SiliconFlow API key not configured, falling back to Ollama")
                self.provider = AIConfig.PROVIDER_OLLAMA
                self._initialize_client()
                return
            self._client = OpenAI(
                api_key=AIConfig.SILICONFLOW_API_KEY,
                base_url=AIConfig.SILICONFLOW_BASE_URL,
                timeout=AIConfig.REQUEST_TIMEOUT
            )
            self._model = AIConfig.SILICONFLOW_MODEL
        else:
            raise ValueError(f"Unknown AI provider: {self.provider}")
    
    async def chat(self, messages: List[Dict[str, str]], 
                   system_prompt: str = None,
                   temperature: float = None) -> str:
        """
        通用的聊天接口
        
        Args:
            messages: 对话历史 [{"role": "user"/"assistant"/"system", "content": "..."}]
            system_prompt: 系统提示词
            temperature: 温度参数
            
        Returns:
            AI 回复文本
        """
        # 插入系统提示
        if system_prompt:
            full_messages = [{"role": "system", "content": system_prompt}] + messages
        else:
            full_messages = messages
        
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=full_messages,
                temperature=temperature or AIConfig.TEMPERATURE,
                max_tokens=AIConfig.MAX_TOKENS
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI chat error: {e}")
            raise
    
    # ============================================
    # 核心功能实现
    # ============================================
    
    async def get_chat_suggestions(self, request: ChatSuggestionRequest) -> ChatSuggestionResponse:
        """
        获取聊天建议
        
        根据双方资料、标签、相似度分析和聊天历史，生成个性化的聊天回复建议
        """
        # 构建聊天历史文本
        history_text = ""
        if request.chat_history:
            for msg in request.chat_history[-6:]:  # 最近6条
                role = "你" if msg["role"] == "user" else request.target_nickname
                history_text += f"{role}: {msg['content']}\n"
        
        # 分析共同兴趣和性格特点
        common_interests_text = ""
        if request.common_interests:
            common_interests_text = f"你们有以下共同兴趣：{', '.join(request.common_interests[:5])}"
        
        # 性格匹配分析
        personality_analysis = ""
        if request.user_personality and request.target_personality:
            if request.user_personality == request.target_personality:
                personality_analysis = f"你们都是【{request.user_personality}】，可以找到很多共鸣话题"
            elif ("外向" in request.user_personality and "外向" in request.target_personality) or \
                 ("内向" in request.user_personality and "内向" in request.target_personality):
                personality_analysis = f"你们性格类型相似，都是【{request.user_personality}】，相处会比较自然"
            elif "外向" in request.user_personality and "内向" in request.target_personality:
                personality_analysis = "你是外向型，对方偏内向，可以多倾听对方的想法"
            else:
                personality_analysis = "你是内向型，对方比较外向，可以多主动分享你的想法"
        
        # 构建 prompt
        prompt = f"""你是一个恋爱交友平台的AI助手，根据双方资料和聊天氛围，给出最自然、最能拉近关系的聊天回复建议。

【你的基本信息】
- 昵称: {request.user_nickname}
- 性别: {request.user_gender or '未设置'}
- 城市: {request.user_city or '未设置'}
- 学校: {request.user_university or '未设置'}
- 个人简介: {request.user_bio or '暂无'}
- 性格: {request.user_personality or '未知'}
- 兴趣标签: {', '.join(request.user_tags) if request.user_tags else '暂无'}

【对方基本信息】
- 昵称: {request.target_nickname}
- 性别: {request.target_gender or '未设置'}
- 城市: {request.target_city or '未设置'}
- 学校: {request.target_university or '未设置'}
- 个人简介: {request.target_bio or '暂无'}
- 性格: {request.target_personality or '未知'}
- 兴趣标签: {', '.join(request.target_tags) if request.target_tags else '暂无'}

【相似度分析】
{common_interests_text}
{personality_analysis}

【最近聊天记录】
{history_text or '暂无聊天记录，你们刚开始认识'}

请根据以上信息，给出3条不同风格的回复建议。每条建议不超过30字，要自然口语化，能体现你们之间的共同点：

1. 共同兴趣型: （结合你们共同的{', '.join(request.common_interests[:3]) if request.common_interests else '兴趣爱好'}展开话题）
2. 关心了解型: （表达对对方的关心或好奇）
3. 轻松幽默型: （用轻松的方式延续话题）

请直接输出3条建议，每条一行，不要加序号，不要加引号。"""
        
        try:
            response_text = await self.chat([{"role": "user", "content": prompt}])
            
            # 解析建议
            suggestions = [s.strip() for s in response_text.split('\n') if s.strip()][:3]
            
            # 生成原因
            reason_parts = []
            if request.common_interests:
                reason_parts.append(f"你们都喜欢{request.common_interests[0]}")
            if request.user_personality and request.target_personality:
                if request.user_personality == request.target_personality:
                    reason_parts.append(f"性格相近（{request.user_personality}）")
            if not reason_parts:
                reason_parts.append("根据聊天氛围生成")
            
            return ChatSuggestionResponse(
                suggestions=suggestions,
                reason="，".join(reason_parts)
            )
        except Exception as e:
            logger.error(f"Get chat suggestions error: {e}")
            return ChatSuggestionResponse(
                suggestions=[
                    f"看你也喜欢{request.common_interests[0] if request.common_interests else 'xxx'}，有机会一起体验呀~",
                    "今天有什么有趣的事吗？最近在忙什么？",
                    "感觉我们还挺有默契的，你觉得呢？"
                ],
                reason="使用默认建议"
            )
    
    async def match_tags(self, request: TagMatchRequest) -> TagMatchResponse:
        """
        智能标签语义匹配
        
        识别不同表达方式但含义相同的标签（如原神=Genshin）
        """
        prompt = f"""你是一个中文标签语义匹配专家。判断以下两组标签中哪些指的是同一事物或同一类别。

用户A标签: {json.dumps(request.my_tags, ensure_ascii=False)}
用户B标签: {json.dumps(request.candidate_tags, ensure_ascii=False)}

请分析并返回匹配结果，输出JSON格式：
{{
    "matches": [
        {{"tag_a": "标签A", "tag_b": "标签B", "category": "所属类别", "confidence": 0.0-1.0}}
    ],
    "hidden_interests": ["发现的潜在共同兴趣列表"]
}}

匹配规则：
- 同一游戏的中英文名或缩写（原神=GenshinImpact, 王者=王者荣耀）
- 同一艺人的不同称呼（周杰伦=Jay Chou=周董=杰倫）
- 同一运动的变体（篮球=NBA, 足球=英超）
- 同类别的兴趣爱好（电影=追剧, 健身=跑步）
- 缩写和全称（LOL=英雄联盟）

只返回confidence >= 0.7的匹配。"""
        
        try:
            response_text = await self.chat([{"role": "user", "content": prompt}])
            
            # 尝试解析 JSON
            # 提取 ```json ... ``` 或直接是 JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                data = json.loads(json_match.group())
                matches = data.get("matches", [])
                hidden = data.get("hidden_interests", [])
                
                # 计算调整后的分数（每多一个匹配 +0.05）
                adjusted = min(1.0, 0.5 + len(matches) * 0.05)
                
                return TagMatchResponse(
                    matches=matches,
                    adjusted_score=adjusted,
                    hidden_interests=hidden
                )
            
            return TagMatchResponse(matches=[], adjusted_score=0.5, hidden_interests=[])
            
        except Exception as e:
            logger.error(f"Tag match error: {e}")
            return TagMatchResponse(matches=[], adjusted_score=0.5, hidden_interests=[])
    
    async def assistant(self, request: AssistantRequest) -> AssistantResponse:
        """
        AI 私人助理
        
        提供情感咨询、日程安排、目的地推荐、用户搜索、恋爱建议等功能
        支持 SoulMatch 交友平台的个性化服务
        """
        # 性格描述映射
        def get_personality_desc(score):
            if not score or score < 1:
                return "未知"
            if score >= 4.5:
                return "非常外向"
            elif score >= 3.5:
                return "比较外向"
            elif score >= 2.5:
                return "中等性格"
            elif score >= 1.5:
                return "比较内向"
            else:
                return "非常内向"
        
        user_personality = get_personality_desc(request.user_values.get("personality", 0))
        
        # 模式定义
        mode_prompts = {
            "chat": f"""你是 SoulMatch 恋爱交友平台的 AI 助手，名字叫"小 SOUL"。
你的性格：友善、温暖、有点俏皮，但很专业。

【你的能力】
1. 情感咨询：帮用户分析感情问题、解读对方心理
2. 聊天陪伴：陪用户聊天、给建议
3. 社交技巧：开场白、约会技巧、沟通方法

【你的风格】
- 语气友善温暖，偶尔俏皮
- 回答问题简洁明了，不啰嗦
- 给出具体可操作的建议
- 可以用 emoji 增添活力

【用户信息】
- 昵称: {request.user_nickname}
- 性格: {user_personality}
- 兴趣标签: {', '.join(request.user_tags) if request.user_tags else '暂无'}
- 价值观特点: {'追求稳定关系' if request.user_values.get('relationship', 0) > 3 else '享受单身时光'}

请根据用户的问题给出温暖、实用的回答。""",

            "schedule": """你是 SoulMatch 的约会规划助手"小 SOUL"。

【你的能力】
1. 约会安排：帮用户规划完美的约会行程
2. 学习计划：制定学习目标和计划
3. 运动安排：制定健身、运动计划
4. 异地恋维持：给出维系异地恋的建议

【输出格式建议】
- 简洁的回复
- 可选包含日程JSON：{{"type": "schedule", "items": [{{"time": "时间", "activity": "活动", "note": "备注"}}]}}

请帮用户规划具体的日程安排，要有创意和实用性！""",

            "destination": """你是 SoulMatch 的约会目的地推荐专家"小 SOUL"。

【你的能力】
根据用户的约会需求推荐合适的地点：
1. 室内约会：咖啡厅、桌游店、密室逃脱、电玩城...
2. 户外活动：公园、爬山、骑行、海边...
3. 文艺场所：博物馆、美术馆、书店、展览...
4. 美食探索：特色餐厅、小吃街、夜市...
5. 娱乐活动：演唱会、电影、戏剧、游戏厅...

【推荐格式】
- 地点名称
- 推荐理由（为什么适合约会）
- 适合的人群/场景
- 小贴士

请给出3-5个创意又实用的约会地点推荐！""",

            "search": """你是 SoulMatch 的智能红娘助手"小 SOUL"。

【你的能力】
理解用户描述的理想对象特征，帮用户找到志同道合的人。

【用户正在寻找】
- 志同道合的伙伴
- 有共同兴趣的朋友
- 潜在的恋爱对象

请根据用户描述，分析他们想要寻找什么类型的人，并给出建议。注意：数据库会根据标签自动匹配合适的用户，你可以给出更好的搜索建议。""",

            "advice": """你是 SoulMatch 的专业恋爱顾问"小 SOUL"。

【你可以提供】
1. 恋爱建议：如何开始、如何推进、如何表白
2. 个人成长：提升魅力、增加自信
3. 社交拓展：如何认识新朋友、扩大社交圈
4. 自我认知：了解自己的恋爱风格和需求

【你的态度】
- 专业但不刻板
- 真诚有温度
- 给出的建议要实用、可操作
- 尊重用户的个性和选择

请给用户真诚、实用的建议！"""
        }
        
        system_prompt = mode_prompts.get(request.mode, mode_prompts["chat"])
        
        # 添加用户上下文
        context = f"""

【当前用户信息】
- 昵称: {request.user_nickname}
- 性格: {user_personality}
- 兴趣标签: {', '.join(request.user_tags[:8]) if request.user_tags else '暂无'}
- 人生目标得分: {request.user_values.get('life_goals', 0):.1f}/5.0
- 关系观得分: {request.user_values.get('relationship', 0):.1f}/5.0
- 兴趣爱好得分: {request.user_values.get('interests', 0):.1f}/5.0
- 生活方式得分: {request.user_values.get('lifestyle', 0):.1f}/5.0

请根据用户的个人特点给出个性化的建议！"""

        messages = [{"role": "system", "content": system_prompt + context}]
        messages += [{"role": m.role, "content": m.content} for m in request.messages]
        
        try:
            response_text = await self.chat(messages)
            
            # 尝试提取结构化数据
            action_data = {}
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                try:
                    action_data = json.loads(json_match.group())
                except:
                    pass
            
            return AssistantResponse(
                response=response_text,
                action_data=action_data
            )
        except Exception as e:
            logger.error(f"Assistant error: {e}")
            return AssistantResponse(
                response="抱歉，小 SOUL 暂时有点困了，请稍后再试~ 🌙",
                suggestions=["换个问题试试？", "稍后再来找我聊天吧~"]
            )


# ============================================
# 单例模式
# ============================================

_ai_service_instance: Optional[AIService] = None

def get_ai_service(provider: str = None) -> AIService:
    """获取 AI 服务单例"""
    global _ai_service_instance
    if _ai_service_instance is None or (provider and _ai_service_instance.provider != provider):
        _ai_service_instance = AIService(provider)
    return _ai_service_instance
