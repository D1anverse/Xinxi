<template>
  <div class="notifications-view">
    <header class="header">
      <button @click="handleBack" class="back-btn">← 返回</button>
      <h1>消息通知</h1>
      <div class="header-right">
        <span class="badge" v-if="unreadCount > 0">{{ unreadCount }}</span>
      </div>
    </header>
    
    <main class="content">
      <div class="tabs">
        <button 
          :class="{ active: activeTab === 'requests' }" 
          @click="activeTab = 'requests'"
        >
          待处理 <span class="tab-badge" v-if="pendingCount > 0">{{ pendingCount }}</span>
        </button>
        <button 
          :class="{ active: activeTab === 'accepted' }"
          @click="activeTab = 'accepted'"
        >
          已同意
        </button>
      </div>
      
      <div class="loading-state" v-if="loading">
        <p>加载中...</p>
      </div>
      
      <div class="empty-state" v-if="!loading && notifications.length === 0">
        <div class="empty-icon">💌</div>
        <p v-if="activeTab === 'requests'">暂无待处理的请求</p>
        <p v-else>暂无已同意的好友</p>
      </div>
      
      <div class="notification-list" v-if="!loading && notifications.length > 0">
        <div 
          v-for="item in notifications" 
          :key="item.id"
          class="notification-item"
          :class="{ unread: !item.is_read }"
        >
          <div class="avatar">
            <div class="avatar-placeholder">{{ item.nickname[0] }}</div>
          </div>
          
          <div class="info">
            <div class="header-row">
              <h3>{{ item.nickname }}</h3>
              <span class="action-badge" :class="item.action">{{ item.actionText }}</span>
            </div>
            <p class="detail">{{ item.university }} · {{ item.age }}岁</p>
            <p class="match-info">匹配度 {{ item.matchScore }}%</p>
            <p class="time">{{ formatTime(item.created_at) }}</p>
          </div>
          
          <div class="actions" v-if="item.status === 'pending'">
            <button @click="acceptRequest(item)" class="btn btn--primary btn--small">
              同意
            </button>
            <button @click="declineRequest(item)" class="btn btn--outline btn--small">
              忽略
            </button>
          </div>
          
          <div class="actions" v-else-if="item.status === 'accepted'">
            <button @click="startChat(item)" class="btn btn--primary btn--small">
              聊天
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const notifications = ref([])
const activeTab = ref('requests')

onMounted(async () => {
  // 进入页面就标记已读
  await markAllRead()
  await loadNotifications()
})

const pendingCount = computed(() => 
  notifications.value.filter(n => n.status === 'pending').length
)

const unreadCount = computed(() => 
  notifications.value.filter(n => n.status === 'pending').length
)

async function markAllRead() {
  try {
    const token = authStore.token
    await fetch('/api/notifications/mark-read', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  } catch (err) {
    console.error('标记已读失败:', err)
  }
}

async function loadNotifications() {
  try {
    loading.value = true
    const token = authStore.token
    const response = await fetch('/api/notifications', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) throw new Error('获取通知失败')
    
    const data = await response.json()
    notifications.value = data.data?.items || []
  } catch (err) {
    console.error('获取通知失败:', err)
  } finally {
    loading.value = false
  }
}

async function acceptRequest(item) {
  try {
    const token = authStore.token
    const response = await fetch('/api/notifications/accept', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ notification_id: item.id })
    })
    
    const data = await response.json()
    if (data.success) {
      item.status = 'accepted'
      alert('已同意！可以开始聊天了')
    }
  } catch (err) {
    alert('操作失败')
  }
}

async function declineRequest(item) {
  try {
    const token = authStore.token
    await fetch('/api/notifications/decline', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ notification_id: item.id })
    })
    notifications.value = notifications.value.filter(n => n.id !== item.id)
  } catch (err) {
    alert('操作失败')
  }
}

function startChat(item) {
  router.push(`/chat/${item.user_id}`)
}

function handleBack() {
  router.back()
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  return date.toLocaleDateString()
}
</script>

<style scoped lang="scss">
.notifications-view {
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
  
  .header-right {
    width: 60px;
    display: flex;
    justify-content: flex-end;
  }
  
  .badge {
    background: #ff4d4f;
    color: white;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 12px;
  }
}

.content {
  max-width: 600px;
  margin: 0 auto;
  padding: 16px;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  
  button {
    flex: 1;
    padding: 12px;
    border: none;
    background: white;
    border-radius: 8px;
    font-size: 14px;
    cursor: pointer;
    
    &.active {
      background: #ff6b6b;
      color: white;
    }
    
    .tab-badge {
      display: inline-block;
      margin-left: 4px;
      padding: 2px 6px;
      background: rgba(255,255,255,0.3);
      border-radius: 8px;
      font-size: 12px;
    }
  }
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

.notification-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notification-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  
  &.unread {
    border-left: 3px solid #ff6b6b;
  }
  
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
    
    .header-row {
      display: flex;
      align-items: center;
      gap: 8px;
      
      h3 {
        font-size: 16px;
        color: #333;
      }
      
      .action-badge {
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        
        &.liked {
          background: #fff2f0;
          color: #ff4d4f;
        }
        
        &.friendship {
          background: #f0f5ff;
          color: #1890ff;
        }
      }
    }
    
    .detail {
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
      margin-top: 4px;
    }
  }
  
  .actions {
    display: flex;
    flex-direction: column;
    gap: 8px;
    
    .btn--small {
      padding: 8px 16px;
      font-size: 13px;
    }
  }
}
</style>
