<template>
  <div class="matches-view">
    <header class="header">
      <div class="header-content">
        <button @click="handleBack" class="back-btn">← 返回</button>
        <div class="header-text">
          <h1>每日推荐</h1>
          <p class="subtitle">基于价值观匹配的智能推荐</p>
        </div>
        <button @click="goToSkipped" class="skipped-btn">
          跳过列表
        </button>
      </div>
    </header>
    
    <main class="content">
      <div class="match-count" v-if="!loading && matches.length > 0">
        今日剩余推荐：<strong>{{ remainingCount }}</strong> / 5
      </div>
      
      <div class="loading-state" v-if="loading">
        <div class="loading-icon">💕</div>
        <p>正在获取每日推荐...</p>
      </div>
      
      <div class="error-state" v-if="error && !loading">
        <div class="error-icon">⚠️</div>
        <p>{{ error }}</p>
        <button @click="loadDailyRecommendations" class="btn btn--primary">
          重试
        </button>
      </div>
      
      <div class="match-cards" v-if="!loading && !error && matches.length > 0">
        <div 
          v-for="(match, index) in matches" 
          :key="match.userId"
          class="match-card"
          :class="{ active: currentIndex === index }"
          @click="currentIndex = index"
        >
          <div class="avatar">
            <div class="avatar-placeholder">{{ match.nickname[0] }}</div>
          </div>
          
          <div class="info">
            <h2>{{ match.nickname }}, {{ match.age }}</h2>
            <p class="university">{{ match.university }}</p>
            
            <div class="match-score">
              <div class="score-circle" :style="getScoreStyle(match.matchScore)">
                <span>{{ match.matchScore }}%</span>
              </div>
              <span class="score-label">匹配度</span>
            </div>
            
            <div class="tags">
              <span class="tag" v-for="tag in match.tags" :key="tag">{{ tag }}</span>
            </div>
            
            <div class="common-dimensions">
              <h4>契合维度</h4>
              <div class="dimension-list">
                <div class="dimension-item" v-for="dim in match.commonDimensions" :key="dim.name">
                  <span>{{ dim.name }}</span>
                  <span class="score">{{ dim.score }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="actions" v-if="!loading && !error && matches.length > 0">
        <button @click="skipCurrent" class="btn btn--outline btn--large">
          ❌ 跳过
        </button>
        <button @click="likeCurrent" class="btn btn--primary btn--large">
          💕 喜欢
        </button>
      </div>
      
      <div class="empty-state" v-if="!loading && !error && matches.length === 0">
        <div class="empty-icon">🎯</div>
        <h3>今日推荐已用完</h3>
        <p>明天再来查看新的推荐吧</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const currentIndex = ref(0)
const remainingCount = ref(5)
const matches = ref([])
const loading = ref(true)
const error = ref(null)
const skippedCount = ref(0)

onMounted(async () => {
  await Promise.all([
    loadDailyRecommendations(),
    loadSkippedCount()
  ])
})

async function loadSkippedCount() {
  try {
    const token = authStore.token
    const response = await fetch('/api/matching/skipped', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      const data = await response.json()
      skippedCount.value = data.data?.items?.length || 0
    }
  } catch (err) {
    console.error('获取跳过数量失败:', err)
  }
}

function goToSkipped() {
  router.push('/skipped')
}

async function loadDailyRecommendations() {
  try {
    loading.value = true
    error.value = null
    
    const token = authStore.token
    if (!token) {
      router.push('/login')
      return
    }
    
    const response = await fetch('/api/matching/daily', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      if (response.status === 401) {
        authStore.logout()
        router.push('/login')
        return
      }
      const data = await response.json()
      throw new Error(data.detail || '获取推荐失败')
    }
    
    const data = await response.json()
    
    // API 返回格式：{ success: true, data: { recommendations: [...] } }
    const recommendations = data.data?.recommendations || data.recommendations || []
    
    if (recommendations.length > 0) {
      matches.value = recommendations.map(rec => ({
        userId: rec.user_id,
        nickname: rec.nickname,
        age: rec.age,
        university: rec.university,
        major: rec.major,
        matchScore: Math.round(rec.match_score),  // 后端已返回百分比值
        tags: rec.tags || [],
        commonDimensions: (rec.match_analysis?.dimensions || rec.match_analysis?.dimension_scores || []).map(d => ({
          name: d.name,
          score: Math.round(d.score * 100)  // 维度分数也转换为百分比
        }))
      }))
      remainingCount.value = data.data?.remaining_today || matches.value.length
    } else {
      matches.value = []
    }
  } catch (err) {
    console.error('获取推荐失败:', err)
    error.value = err.message
    matches.value = []
  } finally {
    loading.value = false
  }
}

function getScoreStyle(score) {
  const color = score >= 90 ? '#52C41A' : score >= 80 ? '#1890FF' : '#FAAD14'
  const circumference = 2 * Math.PI * 40
  const offset = circumference - (score / 100) * circumference
  
  return {
    stroke: color,
    strokeDashoffset: offset,
    color: color
  }
}

async function skipCurrent() {
  if (matches.value.length === 0) return
  
  const currentMatch = matches.value[currentIndex.value]
  
  try {
    const token = authStore.token
    await fetch('/api/matching/action', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        targetUserId: currentMatch.userId,
        action: 'skipped'
      })
    })
  } catch (err) {
    console.error('跳过失败:', err)
  }
  
  if (currentIndex.value < matches.value.length - 1) {
    currentIndex.value++
    remainingCount.value--
  } else {
    matches.value = []
  }
}

async function likeCurrent() {
  if (matches.value.length === 0) return
  
  const currentMatch = matches.value[currentIndex.value]
  
  try {
    const token = authStore.token
    const response = await fetch('/api/matching/action', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        targetUserId: currentMatch.userId,
        action: 'liked'
      })
    })
    
    const data = await response.json()
    
    // API 返回格式：{ success: true, data: { is_matched: true/false, message: '...' } }
    if (data.data?.is_matched) {
      alert(`💕 匹配成功！你们可以开始聊天了`)
      router.push(`/chat/${currentMatch.userId}`)
    } else {
      alert(data.data?.message || '已发送喜欢，等待对方回应')
    }
  } catch (err) {
    console.error('喜欢失败:', err)
    alert('操作失败，请重试')
    return
  }
  
  if (currentIndex.value < matches.value.length - 1) {
    currentIndex.value++
    remainingCount.value--
  } else {
    matches.value = []
  }
}

// 返回
function handleBack() {
  router.push('/')
}
</script>

<style scoped lang="scss">
.matches-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #FFF5F7 0%, #F8F5F2 100%);
}

.header {
  padding: 24px;
  background: white;
  box-shadow: $shadow-sm;
  
  .header-content {
    display: flex;
    align-items: flex-start;
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
  
  .skipped-btn {
    background: #f5f5f5;
    border: none;
    color: #666;
    font-size: 13px;
    cursor: pointer;
    padding: 6px 12px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 4px;
    
    .count {
      background: #ff6b6b;
      color: white;
      padding: 2px 6px;
      border-radius: 8px;
      font-size: 11px;
    }
    
    &:hover {
      background: #eee;
    }
  }
  
  .header-text {
    flex: 1;
    text-align: center;
  }
  
  h1 {
    color: $primary-color;
    font-size: 28px;
    margin-bottom: 8px;
  }
  
  .subtitle {
    color: $text-light;
    font-size: 14px;
  }
}

.content {
  max-width: 600px;
  margin: 0 auto;
  padding: 24px;
}

.match-count {
  text-align: center;
  margin-bottom: 24px;
  color: $text-light;
  
  strong {
    color: $primary-color;
    font-size: 20px;
  }
}

.match-cards {
  position: relative;
  min-height: 500px;
}

.match-card {
  background: white;
  border-radius: $radius-xl;
  padding: 32px;
  box-shadow: $shadow-md;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:not(.active) {
    opacity: 0.5;
    transform: scale(0.95);
  }
  
  &.active {
    opacity: 1;
    transform: scale(1);
  }
  
  .avatar {
    display: flex;
    justify-content: center;
    margin-bottom: 24px;
    
    .avatar-placeholder {
      width: 120px;
      height: 120px;
      border-radius: 50%;
      background: linear-gradient(135deg, $primary-color, $secondary-color);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 48px;
      color: white;
      font-weight: bold;
    }
  }
  
  .info {
    text-align: center;
    
    h2 {
      font-size: 24px;
      margin-bottom: 4px;
    }
    
    .university {
      color: $text-light;
      margin-bottom: 16px;
    }
    
    .match-score {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-bottom: 20px;
      
      .score-circle {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        border: 8px solid $border-color;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: bold;
        transition: all 0.3s ease;
      }
      
      .score-label {
        margin-top: 8px;
        color: $text-light;
        font-size: 14px;
      }
    }
    
    .tags {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: center;
      margin-bottom: 24px;
      
      .tag {
        padding: 6px 12px;
        background: rgba($primary-color, 0.1);
        color: $primary-color;
        border-radius: 16px;
        font-size: 13px;
      }
    }
    
    .common-dimensions {
      text-align: left;
      padding: 20px;
      background: rgba($secondary-color, 0.05);
      border-radius: $radius-md;
      
      h4 {
        margin-bottom: 12px;
        color: $text-color;
      }
      
      .dimension-list {
        .dimension-item {
          display: flex;
          justify-content: space-between;
          padding: 8px 0;
          border-bottom: 1px solid rgba($border-color, 0.5);
          
          &:last-child {
            border-bottom: none;
          }
          
          .score {
            color: $primary-color;
            font-weight: 500;
          }
        }
      }
    }
  }
}

.actions {
  display: flex;
  gap: 16px;
  margin-top: 32px;
  
  button {
    flex: 1;
  }
}

.empty-state {
  text-align: center;
  padding: 64px 32px;
  background: white;
  border-radius: $radius-xl;
  box-shadow: $shadow-md;
  
  .empty-icon {
    font-size: 64px;
    margin-bottom: 16px;
  }
  
  h3 {
    font-size: 20px;
    margin-bottom: 8px;
  }
  
  p {
    color: $text-light;
  }
}

.loading-state,
.error-state {
  text-align: center;
  padding: 64px 32px;
  background: white;
  border-radius: $radius-xl;
  box-shadow: $shadow-md;
  
  .loading-icon,
  .error-icon {
    font-size: 64px;
    margin-bottom: 16px;
    animation: pulse 2s infinite;
  }
  
  p {
    color: $text-light;
    margin-bottom: 16px;
  }
}

.error-state {
  .error-icon {
    animation: none;
  }
  
  button {
    margin-top: 8px;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
