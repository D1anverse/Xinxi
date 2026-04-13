<template>
  <div class="questionnaire-view">
    <header class="header">
      <div class="header-content">
        <button v-if="!completed" @click="handleBack" class="back-btn">← 返回</button>
        <div class="progress-info">
          <span>价值观评估</span>
          <span>{{ currentQuestion + 1 }} / {{ totalQuestions }}</span>
        </div>
      </div>
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: progressPercentage + '%' }"
        ></div>
      </div>
    </header>
    
    <main class="content">
      <div v-if="!completed" class="question-card">
        <h2 class="question-text">{{ currentQuestionData.question }}</h2>
        
        <div class="options">
          <button
            v-for="(option, index) in currentQuestionData.options"
            :key="index"
            @click="selectAnswer(index + 1)"
            class="option-btn"
            :class="{ selected: answers[currentQuestionData.id] === index + 1 }"
          >
            {{ option }}
          </button>
        </div>
        
        <div class="dimension-tag">
          {{ getDimensionName(currentQuestionData.dimension) }}
        </div>
      </div>
      
      <div v-else class="complete-card">
        <div class="success-icon">✅</div>
        <h2>问卷完成！</h2>
        <p>感谢你的认真填写</p>
        
        <div class="summary-card">
          <h3>你的价值观标签</h3>
          <div class="tags">
            <span class="tag" v-for="tag in userTags" :key="tag">{{ tag }}</span>
          </div>
        </div>
        
        <div class="dimension-scores">
          <h3>维度得分</h3>
          <div class="score-item" v-for="(score, dim) in dimensionScores" :key="dim">
            <span class="dimension-name">{{ getDimensionName(dim) }}</span>
            <div class="score-bar">
              <div class="score-fill" :style="{ width: score + '%' }"></div>
            </div>
            <span class="score-value">{{ score }}%</span>
          </div>
        </div>
        
        <button @click="goToMatches" class="btn btn--primary btn--large btn--block">
          查看匹配推荐
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const hasChanges = ref(false)
const isSubmitting = ref(false)

// 50 道价值观问题（简化版示例）
const questions = [
  // 人生目标维度
  { id: 1, dimension: 'life_goals', question: '未来 5 年，你更看重什么？', options: ['事业发展', '家庭幸福', '个人成长', '财务自由'] },
  { id: 2, dimension: 'life_goals', question: '你理想的居住城市是？', options: ['一线城市', '二线城市', '家乡', '海外'] },
  { id: 3, dimension: 'life_goals', question: '对于孩子，你的态度是？', options: ['一定要', '可以考虑', '不要', '没想好'] },
  { id: 4, dimension: 'life_goals', question: '你如何定义成功？', options: ['事业成就', '家庭美满', '内心满足', '社会贡献'] },
  { id: 5, dimension: 'life_goals', question: '你希望的工作状态是？', options: ['稳定安逸', '挑战高薪', '自由灵活', '创业打拼'] },
  { id: 6, dimension: 'life_goals', question: '退休后你理想的生活是？', options: ['环游世界', '含饴弄孙', '继续工作', '培养爱好'] },
  { id: 7, dimension: 'life_goals', question: '你对物质生活的期待是？', options: ['简约朴素', '舒适即可', '品质生活', '奢华享受'] },
  { id: 8, dimension: 'life_goals', question: '你更看重伴侣的什么特质？', options: ['上进心', '责任心', '温柔体贴', '聪明才智'] },
  { id: 9, dimension: 'life_goals', question: '面对人生重大决策，你通常会？', options: ['听从内心', '参考家人意见', '理性分析', '随遇而安'] },
  { id: 10, dimension: 'life_goals', question: '你理想的生活节奏是？', options: ['忙碌充实', '张弛有度', '悠闲自在', '规律稳定'] },
  
  // 性格特质维度
  { id: 11, dimension: 'personality', question: '在社交场合，你通常是？', options: ['活跃气氛', '安静倾听', '观察思考', '看情况'] },
  { id: 12, dimension: 'personality', question: '做决定时，你更依赖？', options: ['逻辑分析', '直觉感受', '他人建议', '经验教训'] },
  { id: 13, dimension: 'personality', question: '面对压力，你的反应是？', options: ['积极应对', '寻求支持', '独自消化', '暂时逃避'] },
  { id: 14, dimension: 'personality', question: '你更喜欢什么样的周末？', options: ['朋友聚会', '宅家休息', '户外活动', '学习充电'] },
  { id: 15, dimension: 'personality', question: '遇到分歧时，你会？', options: ['直接沟通', '委婉表达', '暂时回避', '妥协让步'] },
  { id: 16, dimension: 'personality', question: '你觉得自己是？', options: ['外向开朗', '内向沉稳', '外冷内热', '多变灵活'] },
  { id: 17, dimension: 'personality', question: '对于新事物，你的态度是？', options: ['乐于尝试', '谨慎评估', '保持距离', '看兴趣'] },
  { id: 18, dimension: 'personality', question: '你更擅长？', options: ['表达沟通', '逻辑思考', '创意想象', '执行落地'] },
  { id: 19, dimension: 'personality', question: '情绪低落时，你会？', options: ['找人倾诉', '独自调节', '运动发泄', '转移注意力'] },
  { id: 20, dimension: 'personality', question: '你喜欢的沟通方式是？', options: ['面对面', '微信文字', '语音电话', '视频通话'] },
  
  // 恋爱观念维度
  { id: 21, dimension: 'love_values', question: '你期待的恋爱关系是？', options: ['相互独立', '亲密无间', '亦师亦友', '激情浪漫'] },
  { id: 22, dimension: 'love_values', question: '对于 AA 制，你的态度是？', options: ['完全 AA', '轮流请客', '男方多付', '看情况'] },
  { id: 23, dimension: 'love_values', question: '恋爱中你最看重？', options: ['信任', '理解', '陪伴', '成长'] },
  { id: 24, dimension: 'love_values', question: '你能接受的异地恋时长是？', options: ['不能接受', '半年内', '一年内', '无所谓'] },
  { id: 25, dimension: 'love_values', question: '对于伴侣的异性朋友，你的态度是？', options: ['完全信任', '适度干涉', '明确界限', '不能接受'] },
  { id: 26, dimension: 'love_values', question: '你希望的相处模式是？', options: ['天天见面', '定期约会', '各自忙碌', '随缘相聚'] },
  { id: 27, dimension: 'love_values', question: '吵架后，你希望？', options: ['立刻沟通', '冷静后再谈', '等对方道歉', '自然和好'] },
  { id: 28, dimension: 'love_values', question: '对于结婚，你的态度是？', options: ['必须结婚', '可以接受', '看情况', '不婚主义'] },
  { id: 29, dimension: 'love_values', question: '你如何看待仪式感？', options: ['非常重要', '比较重要', '可有可无', '太麻烦'] },
  { id: 30, dimension: 'love_values', question: '恋爱中需要个人空间吗？', options: ['非常需要', '适度需要', '不太需要', '完全不需要'] },
  
  // 兴趣爱好维度
  { id: 31, dimension: 'hobbies', question: '你最喜欢的休闲方式是？', options: ['看电影', '读书', '运动', '游戏'] },
  { id: 32, dimension: 'hobbies', question: '你喜欢的音乐类型是？', options: ['流行', '古典', '摇滚', '电子'] },
  { id: 33, dimension: 'hobbies', question: '假期你更喜欢？', options: ['旅行探索', '宅家休息', '学习提升', '社交聚会'] },
  { id: 34, dimension: 'hobbies', question: '你喜欢的运动类型是？', options: ['球类运动', '健身', '跑步', '不太运动'] },
  { id: 35, dimension: 'hobbies', question: '对于美食，你的态度是？', options: ['探店达人', '自己做饭', '外卖即可', '不挑剔'] },
  { id: 36, dimension: 'hobbies', question: '你喜欢的电影类型是？', options: ['喜剧', '爱情', '科幻', '悬疑'] },
  { id: 37, dimension: 'hobbies', question: '你有收藏爱好吗？', options: ['有', '没有', '曾经有', '想培养'] },
  { id: 38, dimension: 'hobbies', question: '你喜欢的艺术形式是？', options: ['绘画', '音乐', '文学', '影视'] },
  { id: 39, dimension: 'hobbies', question: '对于宠物，你的态度是？', options: ['非常喜欢', '比较喜欢', '一般', '不太喜欢'] },
  { id: 40, dimension: 'hobbies', question: '你喜欢的季节是？', options: ['春', '夏', '秋', '冬'] },
  
  // 生活方式维度
  { id: 41, dimension: 'lifestyle', question: '你的作息习惯是？', options: ['早睡早起', '正常作息', '偶尔熬夜', '夜猫子'] },
  { id: 42, dimension: 'lifestyle', question: '你的消费观念是？', options: ['节俭为主', '理性消费', '品质优先', '享受当下'] },
  { id: 43, dimension: 'lifestyle', question: '对于家务，你的态度是？', options: ['共同分担', '各负责各的', '请人打扫', '不太在意'] },
  { id: 44, dimension: 'lifestyle', question: '你喜欢的社交频率是？', options: ['经常聚会', '适度社交', '少量精交', '独处为主'] },
  { id: 45, dimension: 'lifestyle', question: '对于健康，你的态度是？', options: ['非常重视', '比较重视', '一般', '不太在意'] },
  { id: 46, dimension: 'lifestyle', question: '你习惯的沟通时间是？', options: ['早上', '中午', '晚上', '深夜'] },
  { id: 47, dimension: 'lifestyle', question: '对于手机使用，你是？', options: ['重度用户', '中度用户', '轻度用户', '极简主义'] },
  { id: 48, dimension: 'lifestyle', question: '你喜欢的居住环境是？', options: ['繁华市区', '安静社区', '自然环境', '便利交通'] },
  { id: 49, dimension: 'lifestyle', question: '对于新鲜事物，你的接受度是？', options: ['很快接受', '慢慢适应', '保持观望', '比较保守'] },
  { id: 50, dimension: 'lifestyle', question: '你理想的生活状态是？', options: ['稳定规律', '充满变化', '简单平淡', '精彩丰富'] }
]

const currentQuestion = ref(0)
const answers = ref({})
const completed = ref(false)

const totalQuestions = questions.length
const currentQuestionData = computed(() => questions[currentQuestion.value])
const progressPercentage = computed(() => ((currentQuestion.value + 1) / totalQuestions) * 100)

const dimensionScores = computed(() => {
  const scores = { life_goals: 0, personality: 0, love_values: 0, hobbies: 0, lifestyle: 0 }
  const counts = { life_goals: 0, personality: 0, love_values: 0, hobbies: 0, lifestyle: 0 }
  
  questions.forEach(q => {
    const answer = answers.value[q.id]
    if (answer) {
      scores[q.dimension] += answer
      counts[q.dimension] += 1
    }
  })
  
  const result = {}
  Object.keys(scores).forEach(key => {
    result[key] = counts[key] > 0 ? Math.round((scores[key] / (counts[key] * 4)) * 100) : 0
  })
  
  return result
})

const userTags = computed(() => {
  const tags = []
  const scores = dimensionScores.value
  
  if (scores.life_goals >= 70) tags.push('目标明确')
  if (scores.personality >= 70) tags.push('外向开朗')
  if (scores.love_values >= 70) tags.push('重视感情')
  if (scores.hobbies >= 70) tags.push('兴趣广泛')
  if (scores.lifestyle >= 70) tags.push('规律生活')
  
  return tags.length > 0 ? tags : ['独特魅力']
})

function selectAnswer(answer) {
  const questionId = questions[currentQuestion.value].id
  answers.value[questionId] = answer
  hasChanges.value = true
  
  // 检查是否回答了所有问题
  const answeredCount = Object.keys(answers.value).length
  
  if (currentQuestion.value < totalQuestions - 1) {
    currentQuestion.value++
  } else if (answeredCount === totalQuestions) {
    // 问卷完成，提交到后端
    submitQuestionnaire()
  } else {
    // 还有未回答的问题
    alert('请回答所有问题')
  }
}

async function submitQuestionnaire() {
  try {
    isSubmitting.value = true
    const token = localStorage.getItem('token')
    if (!token) {
      alert('请先登录')
      router.push('/login')
      return
    }
    
    // 转换答案格式：{1: 3, 2: 5, ...} -> {q1: 3, q2: 5, ...}
    const answersFormatted = {}
    for (const [key, value] of Object.entries(answers.value)) {
      answersFormatted[`q${key}`] = value
    }
    
    const response = await fetch('/api/questionnaire/submit', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        answers: answersFormatted
      })
    })
    
    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || '提交失败')
    }
    
    // 提交成功，显示完成页面
    completed.value = true
    hasChanges.value = false
  } catch (error) {
    console.error('提交问卷失败:', error)
    alert('提交失败，请重试: ' + error.message)
    // 允许用户重新答题
    currentQuestion.value = 0
    answers.value = {}
  } finally {
    isSubmitting.value = false
  }
}

function getDimensionName(dimension) {
  const names = {
    life_goals: '人生目标',
    personality: '性格特质',
    love_values: '恋爱观念',
    hobbies: '兴趣爱好',
    lifestyle: '生活方式'
  }
  return names[dimension] || dimension
}

function goToMatches() {
  router.push('/matches')
}

// 返回（带自动保存提示）
function handleBack() {
  if (hasChanges.value) {
    const confirmLeave = confirm('有未提交的答案，确定要返回吗？')
    if (!confirmLeave) return
  }
  router.back()
}

// 页面加载时设置状态
onMounted(() => {
  hasChanges.value = Object.keys(answers.value).length > 0
})
</script>

<style scoped lang="scss">
.questionnaire-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #FFF5F7 0%, #F8F5F2 100%);
}

.header {
  padding: 24px;
  background: white;
  box-shadow: $shadow-sm;
  
  .header-content {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
  }
  
  .back-btn {
    background: none;
    border: none;
    color: #666;
    font-size: 16px;
    cursor: pointer;
    padding: 8px 12px;
    margin-right: 12px;
    border-radius: 8px;
    
    &:hover {
      background: rgba(0, 0, 0, 0.05);
    }
  }
  
  .progress-info {
    flex: 1;
    display: flex;
    justify-content: space-between;
    font-weight: 500;
  }
  
  .progress-bar {
    height: 8px;
    background: $border-color;
    border-radius: 4px;
    overflow: hidden;
    
    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, $primary-color, $secondary-color);
      transition: width 0.3s ease;
    }
  }
}

.content {
  max-width: 600px;
  margin: 0 auto;
  padding: 32px 24px;
}

.question-card {
  background: white;
  border-radius: $radius-xl;
  padding: 40px 32px;
  box-shadow: $shadow-md;
  
  .question-text {
    font-size: 22px;
    margin-bottom: 32px;
    line-height: 1.5;
  }
  
  .options {
    display: flex;
    flex-direction: column;
    gap: 12px;
    
    .option-btn {
      padding: 16px 20px;
      border: 2px solid $border-color;
      border-radius: $radius-md;
      background: white;
      text-align: left;
      font-size: 16px;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        border-color: $primary-color;
        background: rgba($primary-color, 0.05);
      }
      
      &.selected {
        border-color: $primary-color;
        background: $primary-color;
        color: white;
      }
    }
  }
  
  .dimension-tag {
    margin-top: 32px;
    padding: 8px 16px;
    background: rgba($secondary-color, 0.1);
    color: $secondary-color;
    border-radius: 20px;
    display: inline-block;
    font-size: 14px;
  }
}

.complete-card {
  text-align: center;
  background: white;
  border-radius: $radius-xl;
  padding: 48px 32px;
  box-shadow: $shadow-md;
  
  .success-icon {
    font-size: 64px;
    margin-bottom: 16px;
  }
  
  h2 {
    font-size: 28px;
    margin-bottom: 8px;
  }
  
  > p {
    color: $text-light;
    margin-bottom: 32px;
  }
  
  .summary-card {
    margin-bottom: 32px;
    padding: 24px;
    background: rgba($primary-color, 0.05);
    border-radius: $radius-lg;
    
    h3 {
      margin-bottom: 16px;
    }
    
    .tags {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: center;
      
      .tag {
        padding: 8px 16px;
        background: $primary-color;
        color: white;
        border-radius: 20px;
        font-size: 14px;
      }
    }
  }
  
  .dimension-scores {
    margin-bottom: 32px;
    text-align: left;
    
    h3 {
      margin-bottom: 16px;
    }
    
    .score-item {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;
      
      .dimension-name {
        width: 80px;
        font-size: 14px;
      }
      
      .score-bar {
        flex: 1;
        height: 8px;
        background: $border-color;
        border-radius: 4px;
        overflow: hidden;
        
        .score-fill {
          height: 100%;
          background: linear-gradient(90deg, $primary-color, $secondary-color);
        }
      }
      
      .score-value {
        width: 40px;
        text-align: right;
        font-weight: 500;
      }
    }
  }
}
</style>
