<template>
  <div class="chat-view">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <button @click="handleBack" class="back-btn">
        <span>←</span>
      </button>
      <div class="user-info">
        <div class="user-avatar">
          <img :src="chatUser.avatar || '/default-avatar.png'" alt="头像" />
        </div>
        <div class="user-details">
          <h2>{{ chatUser.nickname }}</h2>
          <span class="online-status" :class="{ online: chatUser.online }">
            {{ chatUser.online ? '在线' : '离线' }}
          </span>
        </div>
      </div>
    </div>

    <!-- 消息列表 -->
    <div class="messages-container" ref="messagesContainer">
      <div class="messages-list">
        <div
          v-for="message in messages"
          :key="message.id"
          class="message-item"
          :class="{ 'my-message': message.isMine }"
        >
          <div class="message-avatar" v-if="!message.isMine">
            <img :src="chatUser.avatar || '/default-avatar.png'" alt="头像" />
          </div>
          <div class="message-content">
            <div class="message-bubble">
              {{ message.content }}
            </div>
            <div class="message-time">
              {{ formatTime(message.createdAt) }}
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="messages.length === 0" class="empty-state">
          <p>还没有消息</p>
          <p class="hint">发送第一条消息打个招呼吧！💕</p>
        </div>
      </div>
    </div>

    <!-- AI 建议区域 -->
    <div v-if="aiSuggestions.length > 0" class="ai-suggestions">
      <div class="ai-suggestions-header">
        <span>💡 AI 建议回复</span>
        <button @click="clearAiSuggestions" class="close-btn">×</button>
      </div>
      <div class="suggestion-list">
        <button
          v-for="(suggestion, index) in aiSuggestions"
          :key="index"
          @click="useSuggestion(suggestion)"
          class="suggestion-item"
        >
          {{ suggestion }}
        </button>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <button
        @click="getAiSuggestion"
        class="ai-btn"
        :disabled="loadingAiSuggestion"
        :class="{ loading: loadingAiSuggestion }"
      >
        {{ loadingAiSuggestion ? '🤔' : '💡' }}
      </button>
      <input
        v-model="newMessage"
        @keyup.enter="sendMessage"
        type="text"
        placeholder="输入消息..."
        class="message-input"
      />
      <button @click="sendMessage" class="send-btn" :disabled="!newMessage.trim()">
        <span>发送</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const messagesContainer = ref(null)
const newMessage = ref('')
const messages = ref([])
const chatUser = ref({
  nickname: '加载中...',
  avatar: '',
  online: false
})
const conversationId = ref(null)
const aiSuggestions = ref([])
const loadingAiSuggestion = ref(false)

let pollTimer = null
let lastMessageTime = null

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  if (isNaN(date.getTime())) return ''
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  
  return `${date.getMonth() + 1}/${date.getDate()}`
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 获取会话ID
const getConversationId = async () => {
  try {
    const response = await fetch(`/api/chat/conversation/${route.params.userId}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      if (data.success) {
        conversationId.value = data.data.conversation_id
        return data.data.conversation_id
      }
    }
    return null
  } catch (error) {
    console.error('获取会话ID失败:', error)
    return null
  }
}

// 加载聊天记录
const loadMessages = async () => {
  // 先获取会话ID
  const convId = await getConversationId()
  if (!convId) return
  
  try {
    const response = await fetch(`/api/chat/messages/${convId}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      const backendMessages = data.data?.messages || []
      
      // 转换后端字段名为前端字段名
      const newMessages = backendMessages.map(msg => ({
        id: msg.message_id,
        senderId: msg.sender_id,
        content: msg.content,
        isMine: msg.is_mine,
        createdAt: msg.created_at
      }))
      
      // 更新最后消息时间用于轮询
      if (newMessages.length > 0) {
        lastMessageTime = newMessages[newMessages.length - 1].createdAt
      }
      
      // 合并消息，避免重复
      const existingIds = new Set(messages.value.map(m => m.id))
      newMessages.forEach(msg => {
        if (!existingIds.has(msg.id)) {
          messages.value.push(msg)
        }
      })
      
      // 按时间排序
      messages.value.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt))
      await scrollToBottom()
    }
  } catch (error) {
    console.error('加载消息失败:', error)
  }
}

// 轮询获取新消息
const startPolling = () => {
  pollTimer = setInterval(() => {
    if (conversationId.value) {
      loadMessages()
    }
  }, 3000) // 每3秒轮询一次
}

// 停止轮询
const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

// 加载用户信息
const loadUserInfo = async () => {
  try {
    const response = await fetch(`/api/user/${route.params.userId}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    if (response.ok) {
      chatUser.value = await response.json()
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

// 连接 WebSocket
const connectWebSocket = () => {
  const wsUrl = `ws://localhost:5000/ws/chat?token=${authStore.token}&userId=${route.params.userId}`
  
  ws = new WebSocket(wsUrl)
  
  ws.onopen = () => {
    console.log('WebSocket 连接成功')
  }
  
  ws.onmessage = (event) => {
    const message = JSON.parse(event.data)
    messages.value.push({
      id: message.id,
      content: message.content,
      isMine: message.senderId === authStore.userId,
      createdAt: message.createdAt
    })
    scrollToBottom()
  }
  
  ws.onclose = () => {
    console.log('WebSocket 连接关闭')
    // 自动重连
    reconnectTimer = setTimeout(() => {
      if (authStore.isLoggedIn) {
        connectWebSocket()
      }
    }, 3000)
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket 错误:', error)
  }
}

// 发送消息
const sendMessage = async () => {
  if (!newMessage.value.trim()) return
  if (!conversationId.value) {
    console.error('会话ID不存在')
    return
  }
  
  const content = newMessage.value.trim()
  const messageData = {
    conversationId: conversationId.value,
    content: content
  }
  
  // 通过 HTTP 发送
  try {
    const response = await fetch('/api/chat/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify(messageData)
    })
    if (!response.ok) {
      console.error('发送消息失败')
    } else {
      // 发送成功后，触发一次立即加载获取最新消息
      await loadMessages()
    }
  } catch (error) {
    console.error('发送消息失败:', error)
  }
  
  newMessage.value = ''
}

// 返回
const handleBack = () => {
  router.push('/chats')
}

// 获取 AI 聊天建议
const getAiSuggestion = async () => {
  if (loadingAiSuggestion.value) return

  loadingAiSuggestion.value = true
  aiSuggestions.value = []

  try {
    // 转换消息历史为 API 格式
    const chatHistory = messages.value.map(msg => ({
      role: msg.isMine ? 'user' : 'assistant',
      content: msg.content
    }))

    const response = await fetch('/api/ai/chat-suggestion', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        targetUserId: route.params.userId,
        chatHistory: chatHistory
      })
    })

    if (response.ok) {
      const data = await response.json()
      if (data.success && data.data.suggestions) {
        aiSuggestions.value = data.data.suggestions
      }
    }
  } catch (error) {
    console.error('获取 AI 建议失败:', error)
  } finally {
    loadingAiSuggestion.value = false
  }
}

// 使用 AI 建议
const useSuggestion = (suggestion) => {
  newMessage.value = suggestion
  aiSuggestions.value = []
  // 自动聚焦输入框
  document.querySelector('.message-input')?.focus()
}

// 清除 AI 建议
const clearAiSuggestions = () => {
  aiSuggestions.value = []
}

onMounted(async () => {
  await loadUserInfo()
  await loadMessages()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

/* 头部 */
.chat-header {
  display: flex;
  align-items: center;
  padding: 15px;
  background: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.back-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  font-size: 24px;
  color: #333;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-info {
  display: flex;
  align-items: center;
  flex: 1;
  margin-left: 10px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 12px;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-details h2 {
  font-size: 16px;
  color: #333;
  margin: 0 0 4px 0;
}

.online-status {
  font-size: 12px;
  color: #999;
}

.online-status.online {
  color: #4caf50;
}

/* 消息区域 */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.messages-list {
  display: flex;
  flex-direction: column;
}

.message-item {
  display: flex;
  margin-bottom: 15px;
}

.message-item.my-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 10px;
}

.message-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-content {
  max-width: 70%;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 15px;
  line-height: 1.4;
  word-wrap: break-word;
}

.message-item:not(.my-message) .message-bubble {
  background: #fff;
  color: #333;
  border-bottom-left-radius: 4px;
}

.message-item.my-message .message-bubble {
  background: #ff6b6b;
  color: white;
  border-bottom-right-radius: 4px;
}

.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
  text-align: right;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.empty-state .hint {
  font-size: 14px;
  margin-top: 10px;
}

/* 输入区域 */
.input-area {
  display: flex;
  padding: 15px;
  background: #fff;
  border-top: 1px solid #e0e0e0;
}

.message-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 24px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.message-input:focus {
  border-color: #ff6b6b;
}

.send-btn {
  margin-left: 10px;
  padding: 12px 24px;
  background: #ff6b6b;
  color: white;
  border: none;
  border-radius: 24px;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #ff5252;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* AI 按钮 */
.ai-btn {
  width: 44px;
  height: 44px;
  border: none;
  background: #f0f0f0;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  margin-right: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.ai-btn:hover:not(:disabled) {
  background: #e0e0e0;
  transform: scale(1.05);
}

.ai-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.ai-btn.loading {
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

/* AI 建议区域 */
.ai-suggestions {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 12px 15px;
  margin: 0 15px 10px 15px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.ai-suggestions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  font-size: 13px;
  margin-bottom: 10px;
}

.ai-suggestions-header span {
  font-weight: 500;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.suggestion-item {
  background: rgba(255, 255, 255, 0.95);
  border: none;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.suggestion-item:hover {
  background: white;
  transform: translateX(4px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}
</style>
