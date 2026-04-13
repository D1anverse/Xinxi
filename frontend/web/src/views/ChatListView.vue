<template>
  <div class="chat-list-view">
    <header class="header">
      <button @click="handleBack" class="back-btn">← 返回</button>
      <h1>聊天消息</h1>
      <div class="header-right"></div>
    </header>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="conversations.length === 0" class="empty-state">
      <div class="empty-icon">💬</div>
      <p>暂无聊天消息</p>
      <p class="hint">匹配成功后即可开始聊天</p>
    </div>

    <!-- 聊天列表 -->
    <div v-else class="conversation-list">
      <div 
        v-for="item in conversations" 
        :key="item.conversation_id"
        class="conversation-item"
        @click="goToChat(item)"
      >
        <div class="avatar">
          <img :src="item.avatar || '/avatars/default.svg'" alt="头像" />
        </div>
        <div class="conversation-content">
          <div class="conversation-header">
            <h3>{{ item.nickname }}</h3>
            <span class="time">{{ formatTime(item.last_message_at) }}</span>
          </div>
          <p class="last-message">{{ item.last_message || '暂无消息' }}</p>
        </div>
        <div class="unread-badge" v-if="item.unread_count > 0">
          {{ item.unread_count > 99 ? '99+' : item.unread_count }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const conversations = ref([])

const handleBack = () => {
  router.push('/home')
}

const goToChat = (item) => {
  router.push(`/chat/${item.user_id}`)
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  
  return `${date.getMonth() + 1}/${date.getDate()}`
}

const loadConversations = async () => {
  try {
    loading.value = true
    const token = authStore.token
    const response = await fetch('/api/chat/conversations', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) throw new Error('获取聊天列表失败')
    
    const data = await response.json()
    conversations.value = data.data?.items || []
  } catch (err) {
    console.error('加载聊天列表失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadConversations()
})

// 监听路由变化，当从聊天页返回时刷新
watch(() => route.path, (newPath, oldPath) => {
  if (oldPath && oldPath.startsWith('/chat/') && newPath === '/chats') {
    loadConversations()
  }
})
</script>

<style scoped lang="scss">
.chat-list-view {
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 10;
  
  h1 {
    font-size: 18px;
    color: #333;
    margin: 0;
  }
  
  .back-btn {
    background: none;
    border: none;
    font-size: 18px;
    color: #333;
    cursor: pointer;
    padding: 8px;
    margin-left: -8px;
  }
  
  .header-right {
    width: 50px;
  }
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #f0f0f0;
    border-top-color: #ff6b6b;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  
  p {
    margin-top: 16px;
    color: #999;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  
  .empty-icon {
    font-size: 64px;
    margin-bottom: 16px;
  }
  
  p {
    color: #666;
    font-size: 16px;
    margin: 0;
  }
  
  .hint {
    margin-top: 8px !important;
    color: #999;
    font-size: 14px !important;
  }
}

.conversation-list {
  padding: 8px 0;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background: white;
  cursor: pointer;
  transition: background 0.2s;
  
  &:active {
    background: #f5f5f5;
  }
  
  .avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    overflow: hidden;
    margin-right: 12px;
    flex-shrink: 0;
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
  
  .conversation-content {
    flex: 1;
    min-width: 0;
    
    .conversation-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      h3 {
        font-size: 16px;
        color: #333;
        margin: 0;
        font-weight: 500;
      }
      
      .time {
        font-size: 12px;
        color: #999;
      }
    }
    
    .last-message {
      margin: 4px 0 0 0;
      font-size: 14px;
      color: #999;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }
  
  .unread-badge {
    min-width: 20px;
    height: 20px;
    background: #ff6b6b;
    color: white;
    font-size: 12px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 6px;
    margin-left: 8px;
  }
}
</style>
