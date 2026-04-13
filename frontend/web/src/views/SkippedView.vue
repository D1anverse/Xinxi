<template>
  <div class="skipped-view">
    <header class="header">
      <button @click="handleBack" class="back-btn">← 返回</button>
      <h1>最近跳过</h1>
      <span class="subtitle">3天内</span>
    </header>
    
    <main class="content">
      <div class="loading-state" v-if="loading">
        <p>加载中...</p>
      </div>
      
      <div class="empty-state" v-if="!loading && skippedUsers.length === 0">
        <div class="empty-icon">👀</div>
        <p>暂无跳过的用户</p>
      </div>
      
      <div class="user-list" v-if="!loading && skippedUsers.length > 0">
        <div 
          v-for="item in skippedUsers" 
          :key="item.id"
          class="user-item"
        >
          <div class="avatar">
            <div class="avatar-placeholder">{{ item.nickname[0] }}</div>
          </div>
          
          <div class="info">
            <h3>{{ item.nickname }}, {{ item.age }}</h3>
            <p class="university">{{ item.university }}</p>
            <p class="match-info">匹配度 {{ item.matchScore }}%</p>
            <p class="time">跳过于 {{ formatTime(item.skipped_at) }}</p>
          </div>
          
          <div class="actions">
            <button @click="likeUser(item)" class="btn btn--primary btn--small">
              💕 喜欢
            </button>
          </div>
        </div>
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

const loading = ref(true)
const skippedUsers = ref([])

onMounted(async () => {
  await loadSkippedUsers()
})

async function loadSkippedUsers() {
  try {
    loading.value = true
    const token = authStore.token
    const response = await fetch('/api/matching/skipped', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) throw new Error('获取失败')
    
    const data = await response.json()
    skippedUsers.value = data.data?.items || []
  } catch (err) {
    console.error('获取跳过列表失败:', err)
  } finally {
    loading.value = false
  }
}

async function likeUser(item) {
  try {
    const token = authStore.token
    const response = await fetch('/api/matching/action', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        targetUserId: item.user_id,
        action: 'liked'
      })
    })
    
    const data = await response.json()
    
    if (data.data?.is_matched) {
      alert(`💕 匹配成功！`)
      router.push(`/chat/${item.user_id}`)
    } else {
      alert('已发送喜欢')
      // 从列表移除
      skippedUsers.value = skippedUsers.value.filter(u => u.id !== item.id)
    }
  } catch (err) {
    alert('操作失败')
  }
}

function handleBack() {
  router.back()
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${Math.floor(diff / 86400000)}天前`
}
</script>

<style scoped lang="scss">
.skipped-view {
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  
  .back-btn {
    background: none;
    border: none;
    color: #666;
    font-size: 16px;
    cursor: pointer;
  }
  
  h1 {
    flex: 1;
    text-align: center;
    font-size: 18px;
    color: #333;
  }
  
  .subtitle {
    font-size: 12px;
    color: #999;
  }
}

.content {
  max-width: 600px;
  margin: 0 auto;
  padding: 16px;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 48px;
  background: white;
  border-radius: 12px;
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: 12px;
  }
  
  p {
    color: #999;
  }
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  
  .avatar {
    .avatar-placeholder {
      width: 50px;
      height: 50px;
      border-radius: 50%;
      background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 20px;
      font-weight: bold;
    }
  }
  
  .info {
    flex: 1;
    
    h3 {
      font-size: 16px;
      color: #333;
    }
    
    .university {
      font-size: 13px;
      color: #666;
      margin: 4px 0;
    }
    
    .match-info {
      font-size: 13px;
      color: #52c41a;
    }
    
    .time {
      font-size: 12px;
      color: #999;
    }
  }
  
  .actions {
    .btn--small {
      padding: 8px 16px;
      font-size: 13px;
    }
  }
}
</style>
