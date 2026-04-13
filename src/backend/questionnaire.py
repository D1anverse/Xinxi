"""
SoulMatch 价值观问卷系统
处理问卷题目、答案提交、维度计算、标签生成
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


# ============================================
# 问卷题目数据
# ============================================

QUESTIONNAIRE_MODULES = [
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
            {
                "id": "q2",
                "text": "你理想的生活状态是？",
                "options": [
                    {"value": 1, "text": "忙碌充实，每天都有新挑战"},
                    {"value": 2, "text": "规律稳定，工作生活平衡"},
                    {"value": 3, "text": "自由自在，不受约束"},
                    {"value": 4, "text": "温馨家庭，陪伴家人"},
                    {"value": 5, "text": "社会影响力，帮助他人"}
                ]
            },
            {
                "id": "q3",
                "text": "你对成功的定义是？",
                "options": [
                    {"value": 1, "text": "职位高、收入高"},
                    {"value": 2, "text": "家庭幸福、身体健康"},
                    {"value": 3, "text": "实现个人价值"},
                    {"value": 4, "text": "被他人认可和尊重"},
                    {"value": 5, "text": "有足够的自由时间"}
                ]
            },
            {
                "id": "q4",
                "text": "你希望在未来定居在哪里？",
                "options": [
                    {"value": 1, "text": "一线城市（北上广深）"},
                    {"value": 2, "text": "新一线/二线城市"},
                    {"value": 3, "text": "家乡或熟悉的城市"},
                    {"value": 4, "text": "海外"},
                    {"value": 5, "text": "不确定，随遇而安"}
                ]
            },
            {
                "id": "q5",
                "text": "你对生育的看法是？",
                "options": [
                    {"value": 1, "text": "一定要孩子，越多越好"},
                    {"value": 2, "text": "要 1-2 个孩子"},
                    {"value": 3, "text": "看情况，顺其自然"},
                    {"value": 4, "text": "不太想要孩子"},
                    {"value": 5, "text": "坚决丁克"}
                ]
            },
            {
                "id": "q6",
                "text": "你更看重伴侣的哪个方面？",
                "options": [
                    {"value": 1, "text": "事业心和上进心"},
                    {"value": 2, "text": "性格和价值观"},
                    {"value": 3, "text": "外貌和气质"},
                    {"value": 4, "text": "经济条件"},
                    {"value": 5, "text": "家庭背景"}
                ]
            },
            {
                "id": "q7",
                "text": "你愿意为事业牺牲个人时间吗？",
                "options": [
                    {"value": 1, "text": "非常愿意，事业优先"},
                    {"value": 2, "text": "比较愿意"},
                    {"value": 3, "text": "适度平衡"},
                    {"value": 4, "text": "不太愿意"},
                    {"value": 5, "text": "完全不愿意，生活优先"}
                ]
            },
            {
                "id": "q8",
                "text": "你对物质生活的期待是？",
                "options": [
                    {"value": 1, "text": "追求高品质，享受当下"},
                    {"value": 2, "text": "适度消费，注重性价比"},
                    {"value": 3, "text": "节俭为主，储蓄优先"},
                    {"value": 4, "text": "极简主义，少即是多"},
                    {"value": 5, "text": "无所谓，够用就行"}
                ]
            },
            {
                "id": "q9",
                "text": "你期待的工作模式是？",
                "options": [
                    {"value": 1, "text": "稳定编制（公务员/事业单位）"},
                    {"value": 2, "text": "大型企业"},
                    {"value": 3, "text": "创业公司"},
                    {"value": 4, "text": "自由职业"},
                    {"value": 5, "text": "自己创业"}
                ]
            },
            {
                "id": "q10",
                "text": "你对退休生活的规划是？",
                "options": [
                    {"value": 1, "text": "继续工作，发挥余热"},
                    {"value": 2, "text": "环游世界"},
                    {"value": 3, "text": "含饴弄孙，享受天伦"},
                    {"value": 4, "text": "培养兴趣爱好"},
                    {"value": 5, "text": "没想过"}
                ]
            }
        ]
    },
    {
        "id": "personality",
        "name": "性格特质",
        "description": "了解你的性格特点和社交偏好",
        "questions": [
            {
                "id": "q11",
                "text": "在社交场合中，你通常是？",
                "options": [
                    {"value": 1, "text": "活跃气氛的中心"},
                    {"value": 2, "text": "积极参与但不主导"},
                    {"value": 3, "text": "安静倾听"},
                    {"value": 4, "text": "只和熟悉的人交流"},
                    {"value": 5, "text": "尽量避开社交"}
                ]
            },
            {
                "id": "q12",
                "text": "你做决定时更依赖？",
                "options": [
                    {"value": 1, "text": "逻辑和分析"},
                    {"value": 2, "text": "直觉和感受"},
                    {"value": 3, "text": "他人建议"},
                    {"value": 4, "text": "过往经验"},
                    {"value": 5, "text": "随机应变"}
                ]
            },
            {
                "id": "q13",
                "text": "面对压力时，你会？",
                "options": [
                    {"value": 1, "text": "积极面对，寻找解决方案"},
                    {"value": 2, "text": "先冷静分析"},
                    {"value": 3, "text": "寻求他人帮助"},
                    {"value": 4, "text": "暂时逃避"},
                    {"value": 5, "text": "情绪化反应"}
                ]
            },
            {
                "id": "q14",
                "text": "你更喜欢什么样的周末？",
                "options": [
                    {"value": 1, "text": "和朋友聚会"},
                    {"value": 2, "text": "参加有趣的活动"},
                    {"value": 3, "text": "宅在家里"},
                    {"value": 4, "text": "一个人安静做事"},
                    {"value": 5, "text": "陪伴家人"}
                ]
            },
            {
                "id": "q15",
                "text": "你觉得自己是？",
                "options": [
                    {"value": 1, "text": "非常外向"},
                    {"value": 2, "text": "偏外向"},
                    {"value": 3, "text": "中间型"},
                    {"value": 4, "text": "偏内向"},
                    {"value": 5, "text": "非常内向"}
                ]
            },
            {
                "id": "q16",
                "text": "你处理冲突的方式是？",
                "options": [
                    {"value": 1, "text": "直接沟通，当场解决"},
                    {"value": 2, "text": "冷静后再谈"},
                    {"value": 3, "text": "妥协退让"},
                    {"value": 4, "text": "避免冲突"},
                    {"value": 5, "text": "坚持己见"}
                ]
            },
            {
                "id": "q17",
                "text": "你更倾向于？",
                "options": [
                    {"value": 1, "text": "计划周全"},
                    {"value": 2, "text": "有大致计划"},
                    {"value": 3, "text": "随性而为"},
                    {"value": 4, "text": "喜欢惊喜"},
                    {"value": 5, "text": "看心情"}
                ]
            },
            {
                "id": "q18",
                "text": "你对新事物的态度是？",
                "options": [
                    {"value": 1, "text": "非常开放，主动尝试"},
                    {"value": 2, "text": "比较开放"},
                    {"value": 3, "text": "谨慎观望"},
                    {"value": 4, "text": "不太感兴趣"},
                    {"value": 5, "text": " prefer 熟悉的事物"}
                ]
            },
            {
                "id": "q19",
                "text": "你表达情感的方式是？",
                "options": [
                    {"value": 1, "text": "直接表达"},
                    {"value": 2, "text": "适度表达"},
                    {"value": 3, "text": "含蓄暗示"},
                    {"value": 4, "text": "通过行动"},
                    {"value": 5, "text": "很少表达"}
                ]
            },
            {
                "id": "q20",
                "text": "你更需要什么样的个人空间？",
                "options": [
                    {"value": 1, "text": "完全独立的空间"},
                    {"value": 2, "text": "大部分时间独处"},
                    {"value": 3, "text": "适度独处"},
                    {"value": 4, "text": "偶尔独处"},
                    {"value": 5, "text": "不喜欢独处"}
                ]
            }
        ]
    },
    {
        "id": "relationship",
        "name": "恋爱观念",
        "description": "了解你对恋爱关系的期待",
        "questions": [
            {
                "id": "q21",
                "text": "你期待的恋爱关系是？",
                "options": [
                    {"value": 1, "text": "以结婚为目的"},
                    {"value": 2, "text": "认真交往，看发展"},
                    {"value": 3, "text": "享受当下"},
                    {"value": 4, "text": "先从朋友做起"},
                    {"value": 5, "text": "不确定"}
                ]
            },
            {
                "id": "q22",
                "text": "你理想的相处模式是？",
                "options": [
                    {"value": 1, "text": "形影不离"},
                    {"value": 2, "text": "经常见面"},
                    {"value": 3, "text": "适度距离"},
                    {"value": 4, "text": "各自独立"},
                    {"value": 5, "text": "聚少离多也可以"}
                ]
            },
            {
                "id": "q23",
                "text": "你对异地恋的态度是？",
                "options": [
                    {"value": 1, "text": "完全接受"},
                    {"value": 2, "text": "可以接受短期"},
                    {"value": 3, "text": "看情况"},
                    {"value": 4, "text": "不太接受"},
                    {"value": 5, "text": "坚决不接受"}
                ]
            },
            {
                "id": "q24",
                "text": "你认为恋爱中最重要的是？",
                "options": [
                    {"value": 1, "text": "信任"},
                    {"value": 2, "text": "沟通"},
                    {"value": 3, "text": "理解"},
                    {"value": 4, "text": "陪伴"},
                    {"value": 5, "text": "激情"}
                ]
            },
            {
                "id": "q25",
                "text": "你希望多久和伴侣沟通一次？",
                "options": [
                    {"value": 1, "text": "随时保持联系"},
                    {"value": 2, "text": "每天固定时间"},
                    {"value": 3, "text": "有事才联系"},
                    {"value": 4, "text": "几天一次"},
                    {"value": 5, "text": "看心情"}
                ]
            },
            {
                "id": "q26",
                "text": "你对伴侣查看手机的态度是？",
                "options": [
                    {"value": 1, "text": "完全开放"},
                    {"value": 2, "text": "可以看但要先说"},
                    {"value": 3, "text": "不建议但不反对"},
                    {"value": 4, "text": "不太愿意"},
                    {"value": 5, "text": "坚决反对"}
                ]
            },
            {
                "id": "q27",
                "text": "恋爱中的开销你倾向于？",
                "options": [
                    {"value": 1, "text": "AA 制"},
                    {"value": 2, "text": "轮流付款"},
                    {"value": 3, "text": "谁方便谁付"},
                    {"value": 4, "text": "男方多承担"},
                    {"value": 5, "text": "建立共同基金"}
                ]
            },
            {
                "id": "q28",
                "text": "你期待多久见一次面？",
                "options": [
                    {"value": 1, "text": "每天都想见"},
                    {"value": 2, "text": "一周 3-4 次"},
                    {"value": 3, "text": "一周 1-2 次"},
                    {"value": 4, "text": "两周一次"},
                    {"value": 5, "text": "一个月一次也可以"}
                ]
            },
            {
                "id": "q29",
                "text": "你对婚前同居的态度是？",
                "options": [
                    {"value": 1, "text": "非常支持，有必要"},
                    {"value": 2, "text": "比较支持"},
                    {"value": 3, "text": "中立"},
                    {"value": 4, "text": "不太支持"},
                    {"value": 5, "text": "坚决反对"}
                ]
            },
            {
                "id": "q30",
                "text": "你如何处理恋爱中的矛盾？",
                "options": [
                    {"value": 1, "text": "当天解决，不过夜"},
                    {"value": 2, "text": "冷静后再沟通"},
                    {"value": 3, "text": "等对方先开口"},
                    {"value": 4, "text": "冷战一段时间"},
                    {"value": 5, "text": "寻求第三方帮助"}
                ]
            }
        ]
    },
    {
        "id": "interests",
        "name": "兴趣爱好",
        "description": "了解你的兴趣和生活方式",
        "questions": [
            {
                "id": "q31",
                "text": "你最喜欢的休闲活动是？",
                "options": [
                    {"value": 1, "text": "运动健身"},
                    {"value": 2, "text": "阅读学习"},
                    {"value": 3, "text": "看电影/剧集"},
                    {"value": 4, "text": "游戏"},
                    {"value": 5, "text": "社交聚会"}
                ]
            },
            {
                "id": "q32",
                "text": "你对音乐的兴趣是？",
                "options": [
                    {"value": 1, "text": "非常热爱，经常听"},
                    {"value": 2, "text": "比较喜欢"},
                    {"value": 3, "text": "一般"},
                    {"value": 4, "text": "偶尔听"},
                    {"value": 5, "text": "不太感兴趣"}
                ]
            },
            {
                "id": "q33",
                "text": "你喜欢的旅行方式是？",
                "options": [
                    {"value": 1, "text": "背包穷游"},
                    {"value": 2, "text": "自由行"},
                    {"value": 3, "text": "跟团游"},
                    {"value": 4, "text": "度假村休闲"},
                    {"value": 5, "text": "不太喜欢旅行"}
                ]
            },
            {
                "id": "q34",
                "text": "你对美食的态度是？",
                "options": [
                    {"value": 1, "text": "美食家，喜欢探店"},
                    {"value": 2, "text": "喜欢尝试新餐厅"},
                    {"value": 3, "text": "偶尔外出就餐"},
                    {"value": 4, "text": "更喜欢自己做饭"},
                    {"value": 5, "text": "随便，吃饱就行"}
                ]
            },
            {
                "id": "q35",
                "text": "你的运动频率是？",
                "options": [
                    {"value": 1, "text": "每天运动"},
                    {"value": 2, "text": "一周 3-4 次"},
                    {"value": 3, "text": "一周 1-2 次"},
                    {"value": 4, "text": "偶尔运动"},
                    {"value": 5, "text": "几乎不运动"}
                ]
            },
            {
                "id": "q36",
                "text": "你更喜欢什么类型的电影？",
                "options": [
                    {"value": 1, "text": "商业大片"},
                    {"value": 2, "text": "文艺片"},
                    {"value": 3, "text": "纪录片"},
                    {"value": 4, "text": "动画片"},
                    {"value": 5, "text": "不太看电影"}
                ]
            },
            {
                "id": "q37",
                "text": "你的阅读习惯是？",
                "options": [
                    {"value": 1, "text": "每天阅读"},
                    {"value": 2, "text": "一周几本书"},
                    {"value": 3, "text": "一月几本书"},
                    {"value": 4, "text": "偶尔阅读"},
                    {"value": 5, "text": "几乎不读书"}
                ]
            },
            {
                "id": "q38",
                "text": "你对艺术展览的兴趣是？",
                "options": [
                    {"value": 1, "text": "经常去看"},
                    {"value": 2, "text": "有兴趣但很少去"},
                    {"value": 3, "text": "一般"},
                    {"value": 4, "text": "不太感兴趣"},
                    {"value": 5, "text": "完全没兴趣"}
                ]
            },
            {
                "id": "q39",
                "text": "你喜欢的社交活动是？",
                "options": [
                    {"value": 1, "text": "大型派对"},
                    {"value": 2, "text": "小型聚会"},
                    {"value": 3, "text": "一对一聊天"},
                    {"value": 4, "text": "线上社交"},
                    {"value": 5, "text": "不太喜欢社交"}
                ]
            },
            {
                "id": "q40",
                "text": "你的游戏习惯是？",
                "options": [
                    {"value": 1, "text": "重度玩家"},
                    {"value": 2, "text": "经常玩"},
                    {"value": 3, "text": "偶尔玩"},
                    {"value": 4, "text": "很少玩"},
                    {"value": 5, "text": "不玩游戏"}
                ]
            }
        ]
    },
    {
        "id": "lifestyle",
        "name": "生活方式",
        "description": "了解你的日常生活习惯",
        "questions": [
            {
                "id": "q41",
                "text": "你的作息时间是？",
                "options": [
                    {"value": 1, "text": "早睡早起（6 点前起）"},
                    {"value": 2, "text": "正常作息（7-8 点起）"},
                    {"value": 3, "text": "晚睡晚起（9 点后起）"},
                    {"value": 4, "text": "熬夜党（凌晨睡）"},
                    {"value": 5, "text": "不规律"}
                ]
            },
            {
                "id": "q42",
                "text": "你的消费观念是？",
                "options": [
                    {"value": 1, "text": "节俭储蓄"},
                    {"value": 2, "text": "理性消费"},
                    {"value": 3, "text": "适度享受"},
                    {"value": 4, "text": "及时行乐"},
                    {"value": 5, "text": "月光族"}
                ]
            },
            {
                "id": "q43",
                "text": "你的饮食习惯是？",
                "options": [
                    {"value": 1, "text": "健康饮食，自己做饭"},
                    {"value": 2, "text": "注意营养搭配"},
                    {"value": 3, "text": "正常饮食"},
                    {"value": 4, "text": "喜欢外卖"},
                    {"value": 5, "text": "不规律"}
                ]
            },
            {
                "id": "q44",
                "text": "你对抽烟的态度是？",
                "options": [
                    {"value": 1, "text": "完全不能接受"},
                    {"value": 2, "text": "可以接受但不喜欢"},
                    {"value": 3, "text": "无所谓"},
                    {"value": 4, "text": "可以接受"},
                    {"value": 5, "text": "自己也抽"}
                ]
            },
            {
                "id": "q45",
                "text": "你对喝酒的态度是？",
                "options": [
                    {"value": 1, "text": "完全不能接受"},
                    {"value": 2, "text": "可以接受但不喜欢"},
                    {"value": 3, "text": "社交场合可以"},
                    {"value": 4, "text": "偶尔小酌"},
                    {"value": 5, "text": "经常喝酒"}
                ]
            },
            {
                "id": "q46",
                "text": "你的卫生习惯是？",
                "options": [
                    {"value": 1, "text": "非常爱干净"},
                    {"value": 2, "text": "比较爱干净"},
                    {"value": 3, "text": "正常"},
                    {"value": 4, "text": "不太讲究"},
                    {"value": 5, "text": "比较随意"}
                ]
            },
            {
                "id": "q47",
                "text": "你对宠物的态度是？",
                "options": [
                    {"value": 1, "text": "非常喜欢，一定要养"},
                    {"value": 2, "text": "喜欢，可以养"},
                    {"value": 3, "text": "无所谓"},
                    {"value": 4, "text": "不太喜欢"},
                    {"value": 5, "text": "完全不能接受"}
                ]
            },
            {
                "id": "q48",
                "text": "你的家务分工观念是？",
                "options": [
                    {"value": 1, "text": "完全 AA"},
                    {"value": 2, "text": "按擅长分工"},
                    {"value": 3, "text": "轮流做"},
                    {"value": 4, "text": "女方多做"},
                    {"value": 5, "text": "男方多做"}
                ]
            },
            {
                "id": "q49",
                "text": "你对网络社交的依赖度是？",
                "options": [
                    {"value": 1, "text": "重度依赖"},
                    {"value": 2, "text": "比较依赖"},
                    {"value": 3, "text": "适度使用"},
                    {"value": 4, "text": "较少使用"},
                    {"value": 5, "text": "几乎不用"}
                ]
            },
            {
                "id": "q50",
                "text": "你理想的生活节奏是？",
                "options": [
                    {"value": 1, "text": "快节奏，充满挑战"},
                    {"value": 2, "text": "较快但有规律"},
                    {"value": 3, "text": "适中平衡"},
                    {"value": 4, "text": "慢节奏，悠闲"},
                    {"value": 5, "text": "极简，低欲望"}
                ]
            }
        ]
    }
]


# ============================================
# 数据模型
# ============================================

class QuestionnaireResponse(BaseModel):
    """问卷响应"""
    total_questions: int = 50
    estimated_time: int = 15  # 分钟
    modules: List[Dict[str, Any]]


class SubmitAnswersRequest(BaseModel):
    """提交答案请求"""
    answers: Dict[str, int] = Field(..., description="题目 ID 到答案的映射")
    
    def validate_answers(self) -> bool:
        """验证答案完整性"""
        # 检查是否回答了所有问题
        all_question_ids = []
        for module in QUESTIONNAIRE_MODULES:
            for q in module['questions']:
                all_question_ids.append(q['id'])
        
        for qid in all_question_ids:
            if qid not in self.answers:
                return False
            if not (1 <= self.answers[qid] <= 5):
                return False
        return True


class DimensionScore(BaseModel):
    """维度得分"""
    name: str
    score: float
    level: str
    description: str
    percentage: int


class QuestionnaireResult(BaseModel):
    """问卷结果"""
    dimensions: List[DimensionScore]
    tags: List[str]
    summary: str
    submitted_at: str


# ============================================
# 问卷服务
# ============================================

class QuestionnaireService:
    """问卷服务"""
    
    # 维度映射
    DIMENSION_MAP = {
        'life_goals': ('人生目标', [f'q{i}' for i in range(1, 11)]),
        'personality': ('性格特质', [f'q{i}' for i in range(11, 21)]),
        'relationship': ('恋爱观念', [f'q{i}' for i in range(21, 31)]),
        'interests': ('兴趣爱好', [f'q{i}' for i in range(31, 41)]),
        'lifestyle': ('生活方式', [f'q{i}' for i in range(41, 51)])
    }
    
    # 标签规则（调整阈值，更容易生成标签）
    TAG_RULES = {
        '事业型': lambda scores: scores['life_goals'] >= 3.0,
        '家庭型': lambda scores: scores['relationship'] >= 3.0,
        '内向型': lambda scores: scores['personality'] >= 3.5,
        '外向型': lambda scores: scores['personality'] <= 3.5,
        '传统型': lambda scores: scores['relationship'] >= 3.5,
        '开放型': lambda scores: scores['lifestyle'] <= 3.0,
        '理性型': lambda scores: scores['personality'] >= 2.5,
        '感性型': lambda scores: scores['lifestyle'] >= 3.5,
    }
    
    def get_questionnaire(self) -> QuestionnaireResponse:
        """获取问卷题目"""
        return QuestionnaireResponse(
            total_questions=50,
            estimated_time=15,
            modules=QUESTIONNAIRE_MODULES
        )
    
    def calculate_dimension_score(self, answers: Dict[str, int], dimension: str) -> float:
        """计算维度得分"""
        _, question_ids = self.DIMENSION_MAP.get(dimension, ('', []))
        if not question_ids:
            return 0.0
        
        total = 0
        count = 0
        for qid in question_ids:
            if qid in answers:
                # 注意：某些题目可能需要反向计分，这里简化处理
                total += answers[qid]
                count += 1
        
        return round(total / count, 2) if count > 0 else 0.0
    
    def get_score_level(self, score: float) -> str:
        """根据得分返回等级"""
        if score >= 4.5:
            return "很高"
        elif score >= 4.0:
            return "高"
        elif score >= 3.5:
            return "较高"
        elif score >= 3.0:
            return "中等"
        elif score >= 2.5:
            return "较低"
        elif score >= 2.0:
            return "低"
        else:
            return "很低"
    
    def get_score_description(self, dimension: str, score: float) -> str:
        """根据维度和得分返回描述"""
        descriptions = {
            'life_goals': {
                'high': '你非常重视事业发展和人生规划，有明确的目标和追求',
                'medium': '你对人生有一定规划，但更注重平衡',
                'low': '你更随性，不太喜欢严格的规划'
            },
            'personality': {
                'high': '你性格偏内向，喜欢独处和深度思考',
                'medium': '你性格平衡，能适应不同社交场合',
                'low': '你性格外向，喜欢社交和热闹'
            },
            'relationship': {
                'high': '你对恋爱关系比较传统，期待稳定长久',
                'medium': '你对恋爱关系态度适中',
                'low': '你对恋爱关系比较开放，注重自由'
            },
            'interests': {
                'high': '你有广泛的兴趣爱好，生活丰富多彩',
                'medium': '你有一些固定的兴趣爱好',
                'low': '你对兴趣爱好不太在意'
            },
            'lifestyle': {
                'high': '你生活习惯规律，注重健康和生活品质',
                'medium': '你的生活方式比较平衡',
                'low': '你生活方式随意，不太拘泥于规律'
            }
        }
        
        dim_desc = descriptions.get(dimension, {})
        if score >= 3.5:
            return dim_desc.get('high', '')
        elif score >= 2.5:
            return dim_desc.get('medium', '')
        else:
            return dim_desc.get('low', '')
    
    def generate_tags(self, scores: Dict[str, float]) -> List[str]:
        """根据得分生成标签"""
        tags = []
        for tag, rule in self.TAG_RULES.items():
            try:
                if rule(scores):
                    tags.append(tag)
            except:
                pass
        return tags[:5]  # 最多 5 个标签
    
    def generate_summary(self, scores: Dict[str, float], tags: List[str]) -> str:
        """生成个人总结"""
        summaries = []
        
        if scores.get('life_goals', 0) >= 4.0:
            summaries.append("你是一个注重事业发展的人")
        elif scores.get('life_goals', 0) <= 2.5:
            summaries.append("你更享受当下的生活")
        
        if scores.get('personality', 0) >= 4.0:
            summaries.append("性格偏内向")
        elif scores.get('personality', 0) <= 2.5:
            summaries.append("性格外向")
        
        if scores.get('relationship', 0) >= 4.0:
            summaries.append("在恋爱关系中期待稳定")
        
        if summaries:
            return "，".join(summaries[:3]) + "。"
        return "你是一个独特的人，有自己的生活方式和价值观。"
    
    def submit_answers(self, answers: Dict[str, int]) -> QuestionnaireResult:
        """提交答案并计算结果"""
        # 计算各维度得分
        scores = {}
        dimensions = []
        
        for dim_key, (dim_name, _) in self.DIMENSION_MAP.items():
            score = self.calculate_dimension_score(answers, dim_key)
            scores[dim_key] = score
            
            dimensions.append(DimensionScore(
                name=dim_name,
                score=score,
                level=self.get_score_level(score),
                description=self.get_score_description(dim_key, score),
                percentage=int(score * 20)  # 转换为百分比
            ))
        
        # 生成标签和总结
        tags = self.generate_tags(scores)
        summary = self.generate_summary(scores, tags)
        
        return QuestionnaireResult(
            dimensions=dimensions,
            tags=tags,
            summary=summary,
            submitted_at=datetime.utcnow().isoformat()
        )
    
    async def save_user_values(self, user_id: str, answers: Dict[str, int], scores: Dict[str, float], tags: List[str]) -> bool:
        """保存用户价值观到数据库"""
        import json
        from database.db import get_pool
        from datetime import datetime
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO user_values (
                    user_id, answers, 
                    life_goals_score, personality_score, relationship_score,
                    interests_score, lifestyle_score,
                    tags, completed_at
                ) VALUES ($1::uuid, $2::jsonb, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (user_id) DO UPDATE SET
                    answers = EXCLUDED.answers,
                    life_goals_score = EXCLUDED.life_goals_score,
                    personality_score = EXCLUDED.personality_score,
                    relationship_score = EXCLUDED.relationship_score,
                    interests_score = EXCLUDED.interests_score,
                    lifestyle_score = EXCLUDED.lifestyle_score,
                    tags = EXCLUDED.tags,
                    completed_at = COALESCE(user_values.completed_at, CURRENT_TIMESTAMP),
                    updated_at = CURRENT_TIMESTAMP
                """,
                user_id,
                json.dumps(answers),
                scores.get('life_goals', 0),
                scores.get('personality', 0),
                scores.get('relationship', 0),
                scores.get('interests', 0),
                scores.get('lifestyle', 0),
                tags,
                datetime.utcnow()
            )
            return True
    
    async def get_user_values(self, user_id: str) -> Optional[Dict]:
        """从数据库获取用户价值观"""
        from database.db import get_pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT answers, life_goals_score, personality_score,
                       relationship_score, interests_score, lifestyle_score,
                       tags, completed_at
                FROM user_values
                WHERE user_id = $1::uuid
                """,
                user_id
            )
            if row:
                return dict(row)
            return None
    
    def get_default_weights(self) -> Dict[str, float]:
        """获取默认权重"""
        return {
            "life_goals": 0.30,
            "personality": 0.25,
            "relationship": 0.25,
            "interests": 0.10,
            "lifestyle": 0.10
        }


# ============================================
# 测试代码
# ============================================

if __name__ == "__main__":
    print("🦞 SoulMatch 价值观问卷系统测试")
    print("=" * 50)
    
    service = QuestionnaireService()
    
    # 测试获取问卷
    print("\n1️⃣ 获取问卷结构...")
    questionnaire = service.get_questionnaire()
    print(f"   ✅ 题目总数：{questionnaire.total_questions}")
    print(f"   ⏱️  预计时间：{questionnaire.estimated_time}分钟")
    print(f"   📚 模块数：{len(questionnaire.modules)}")
    
    # 测试提交答案（模拟）
    print("\n2️⃣ 模拟提交答案...")
    mock_answers = {}
    for i in range(1, 51):
        mock_answers[f'q{i}'] = (i % 5) + 1  # 1-5 循环
    
    result = service.submit_answers(mock_answers)
    print(f"   ✅ 提交成功！")
    print(f"   📊 维度得分:")
    for dim in result.dimensions:
        print(f"      - {dim.name}: {dim.score} ({dim.level})")
    print(f"   🏷️  标签：{result.tags}")
    print(f"   📝 总结：{result.summary}")
    
    print("\n" + "=" * 50)
    print("✅ 问卷系统测试完成！")
