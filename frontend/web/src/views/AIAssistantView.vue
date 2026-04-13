<template>
  <div class="assistant-view">
    <!-- 头部 -->
    <div class="assistant-header">
      <button @click="handleBack" class="back-btn">
        <span>←</span>
      </button>
      <div class="header-title">
        <span class="ai-icon">✨</span>
        <h1>AI 私人助理</h1>
      </div>
      <div class="header-spacer"></div>
    </div>

    <!-- 功能模式选择 -->
    <div class="mode-selector">
      <button
        v-for="mode in modes"
        :key="mode.id"
        @click="selectMode(mode.id)"
        class="mode-btn"
        :class="{ active: currentMode === mode.id }"
      >
        <span class="mode-icon">{{ mode.icon }}</span>
        <span class="mode-label">{{ mode.label }}</span>
      </button>
    </div>

    <!-- 聊天区域 -->
    <div class="chat-container" ref="chatContainer">
      <div class="messages-list">
        <!-- 欢迎消息 -->
        <div v-if="messages.length === 0" class="welcome-section">
          <div class="welcome-avatar">
            <img src="/avatars/default.svg" alt="AI" @error="handleAvatarError" />
          </div>
          <div class="welcome-message">
            <p class="welcome-title">嗨，{{ userNickname }}！我是你的 SoulMatch AI 助手 ✨</p>
            <p class="welcome-desc">{{ currentModeInfo.description }}</p>
            <div class="quick-actions">
              <button
                v-for="action in currentModeInfo.quickActions"
                :key="action"
                @click="sendQuickMessage(action)"
                class="quick-action-btn"
              >
                {{ action }}
              </button>
            </div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="message-item"
          :class="{ 'ai-message': message.role === 'assistant', 'user-message': message.role === 'user' }"
        >
          <div v-if="message.role === 'assistant'" class="message-avatar">
            <img src="/avatars/default.svg" alt="AI" @error="handleAvatarError" />
          </div>
          <div class="message-content">
            <div class="message-bubble">
              <div v-if="message.isLoading" class="loading-dots">
                <span></span><span></span><span></span>
              </div>
              <div v-else>
                <p v-if="message.isHtml" v-html="message.content"></p>
                <p v-else>{{ message.content }}</p>
                
                <!-- 用户推荐卡片 -->
                <div v-if="message.recommendedUsers && message.recommendedUsers.length > 0" class="recommended-users">
                  <h4>为你推荐的用户 🎯</h4>
                  <div class="user-cards">
                    <div
                      v-for="user in message.recommendedUsers"
                      :key="user.id"
                      class="user-card"
                    >
                      <div class="card-avatar">
                        <img :src="user.avatar || '/default-avatar.png'" :alt="user.nickname" />
                      </div>
                      <div class="card-info">
                        <h5>{{ user.nickname }}</h5>
                        <p class="card-tags">
                          <span v-for="tag in user.tags.slice(0, 3)" :key="tag" class="tag">
                            {{ tag }}
                          </span>
                        </p>
                        <p class="card-match" v-if="user.match_score">
                          匹配度: <strong>{{ Math.round(user.match_score * 100) }}%</strong>
                        </p>
                      </div>
                      <div class="card-actions">
                        <button @click="viewProfile(user.id)" class="view-profile-btn">
                          查看
                        </button>
                        <button @click="startChat(user.id)" class="chat-btn">
                          聊天
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 目的地推荐 -->
                <div v-if="message.destinations" class="destination-list">
                  <div class="dest-header">📍 为你推荐 {{ message.destinations.length }} 个约会地点</div>
                  <div
                    v-for="(dest, index) in message.destinations"
                    :key="index"
                    class="destination-card"
                  >
                    <div class="dest-main">
                      <h5>{{ dest.name }}</h5>
                      <span v-if="dest.price" class="dest-price">{{ dest.price }}</span>
                    </div>
                    <p class="dest-desc">{{ dest.description }}</p>
                    <div class="dest-meta">
                      <span v-if="dest.address" class="dest-address">📍 {{ dest.address }}</span>
                      <span v-if="dest.city" class="dest-city">{{ dest.city }}</span>
                    </div>
                    <div v-if="dest.tags && dest.tags.length" class="dest-tags">
                      <span v-for="tag in dest.tags" :key="tag" class="dest-tag">{{ tag }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="message-time">{{ message.time }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <input
        v-model="inputMessage"
        @keyup.enter="sendMessage"
        type="text"
        :placeholder="currentModeInfo.placeholder"
        class="message-input"
      />
      <button @click="sendMessage" class="send-btn" :disabled="!inputMessage.trim() || isLoading">
        <span v-if="isLoading">...</span>
        <span v-else>发送</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 模式定义
const modes = [
  { id: 'chat', icon: '💬', label: '情感咨询' },
  { id: 'schedule', icon: '📅', label: '日常安排' },
  { id: 'destination', icon: '🌍', label: '目的地' },
  { id: 'search', icon: '🔍', label: '找人' },
  { id: 'advice', icon: '💡', label: '恋爱建议' }
]

const currentMode = ref('chat')

const currentModeInfo = computed(() => {
  const info = {
    chat: {
      description: '你可以和我聊聊感情问题、约会技巧、沟通方法等，我会给你温暖又实用的建议~',
      placeholder: '聊聊你的感情困惑...',
      quickActions: ['怎么开场聊天？', '如何判断对方心意？', '约会去哪好？']
    },
    schedule: {
      description: '我可以帮你规划约会行程、学习计划、运动安排等，让你的生活更有条理~',
      placeholder: '帮我安排一个约会...',
      quickActions: ['周末约会安排', '异地恋怎么维持？', '第一次约会做什么？']
    },
    destination: {
      description: '告诉我你想去的地方类型或活动，我会为你推荐适合的约会目的地~',
      placeholder: '推荐适合约会的地方...',
      quickActions: ['深圳室内约会', '周末周边游', '浪漫餐厅推荐']
    },
    search: {
      description: '你可以描述理想对象的特征，我会帮你找到志同道合的人！',
      placeholder: '帮我找志同道合的人...',
      quickActions: ['喜欢旅行的人', '爱摄影的朋友', '内向型对象']
    },
    advice: {
      description: '作为SoulMatch的AI助手，我可以给你提供专业的恋爱建议和个人成长指导~',
      placeholder: '想听听建议...',
      quickActions: ['提升个人魅力', '增加被喜欢几率', '如何认识新朋友']
    }
  }
  return info[currentMode.value] || info.chat
})

const userNickname = ref('朋友')

// 状态
const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const chatContainer = ref(null)

// 处理头像加载失败
const handleAvatarError = (e) => {
  e.target.src = '/default-avatar.png'
}

// 选择模式
const selectMode = (modeId) => {
  currentMode.value = modeId
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// 获取当前时间
const getCurrentTime = () => {
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
}

// 发送快捷消息
const sendQuickMessage = (text) => {
  inputMessage.value = text
  sendMessage()
}

// 查看用户资料
const viewProfile = (userId) => {
  router.push(`/profile/${userId}`)
}

// 发起聊天
const startChat = (userId) => {
  router.push(`/chat/${userId}`)
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return
  
  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''
  
  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userMessage,
    time: getCurrentTime()
  })
  
  await scrollToBottom()
  isLoading.value = true
  
  // 添加AI加载消息
  const aiMessageIndex = messages.value.length
  messages.value.push({
    role: 'assistant',
    content: '',
    isLoading: true,
    time: getCurrentTime()
  })
  
  try {
    const response = await fetch('/api/ai/assistant', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        mode: currentMode.value,
        message: userMessage
      })
    })
    
    if (response.ok) {
      const data = await response.json()
      if (data.success) {
        messages.value[aiMessageIndex] = {
          role: 'assistant',
          content: data.data.response,
          time: getCurrentTime(),
          recommendedUsers: data.data.recommended_users,
          destinations: data.data.destinations,
          isHtml: data.data.response?.includes('<') || data.data.response?.includes('📍')
        }
      } else {
        messages.value[aiMessageIndex] = {
          role: 'assistant',
          content: '抱歉，我现在有点忙，请稍后再试~',
          time: getCurrentTime()
        }
      }
    } else {
      messages.value[aiMessageIndex] = {
        role: 'assistant',
        content: '抱歉，遇到了点小问题，请稍后再试~',
        time: getCurrentTime()
      }
    }
  } catch (error) {
    console.error('AI 助手请求失败:', error)
    messages.value[aiMessageIndex] = {
      role: 'assistant',
      content: '网络连接有点问题，请检查网络后重试~',
      time: getCurrentTime()
    }
  }
  
  isLoading.value = false
  await scrollToBottom()
}

// 返回
const handleBack = () => {
  router.back()
}

// 初始化
onMounted(async () => {
  // 获取用户信息
  if (authStore.user?.nickname) {
    userNickname.value = authStore.user.nickname
  } else {
    await authStore.fetchUserProfile()
    if (authStore.user?.nickname) {
      userNickname.value = authStore.user.nickname
    }
  }
})
</script>

<style scoped>
.assistant-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.assistant-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.back-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: #f0f0f0;
  border-radius: 50%;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #e0e0e0;
  transform: scale(1.05);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-title h1 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.ai-icon {
  font-size: 24px;
}

.header-spacer {
  width: 40px;
}

.mode-selector {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.9);
  overflow-x: auto;
  scrollbar-width: none;
}

.mode-selector::-webkit-scrollbar {
  display: none;
}

.mode-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  border: 2px solid transparent;
  background: #f5f5f5;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 60px;
}

.mode-btn:hover {
  background: #e8e8e8;
}

.mode-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}

.mode-icon {
  font-size: 20px;
}

.mode-label {
  font-size: 11px;
  white-space: nowrap;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.welcome-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px;
  text-align: center;
}

.welcome-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
}

.welcome-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.welcome-message {
  max-width: 300px;
}

.welcome-title {
  font-size: 18px;
  font-weight: 600;
  color: white;
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.welcome-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 20px;
  line-height: 1.5;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.quick-action-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 20px;
  font-size: 13px;
  color: #667eea;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.quick-action-btn:hover {
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  display: flex;
  gap: 10px;
  max-width: 85%;
}

.message-item.user-message {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-item.ai-message {
  align-self: flex-start;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.5;
}

.ai-message .message-bubble {
  background: white;
  color: #333;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.user-message .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.message-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  padding: 0 4px;
}

.user-message .message-time {
  text-align: right;
}

.loading-dots {
  display: flex;
  gap: 4px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  background: #667eea;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* 用户推荐卡片 */
.recommended-users {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.recommended-users h4 {
  font-size: 14px;
  color: #667eea;
  margin-bottom: 12px;
}

.user-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f8f8;
  border-radius: 12px;
}

.card-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
}

.card-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-info {
  flex: 1;
}

.card-info h5 {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.card-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 4px;
}

.tag {
  padding: 2px 8px;
  background: #e8e8ff;
  color: #667eea;
  border-radius: 10px;
  font-size: 11px;
}

.card-match {
  font-size: 12px;
  color: #666;
}

.card-match strong {
  color: #667eea;
}

.view-profile-btn {
  padding: 6px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 12px;
  cursor: pointer;
}

.card-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.chat-btn {
  padding: 6px 12px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 12px;
  cursor: pointer;
}

/* 目的地推荐 */
.destination-list {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dest-header {
  font-size: 13px;
  color: #667eea;
  font-weight: 500;
  margin-bottom: 4px;
}

.destination-card {
  padding: 14px;
  background: linear-gradient(135deg, #f8f8ff 0%, #f0f0ff 100%);
  border-radius: 14px;
  text-align: left;
  border: 1px solid #e8e8ff;
  transition: all 0.2s;
}

.destination-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.dest-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.destination-card h5 {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.dest-price {
  font-size: 12px;
  color: #ff6b6b;
  font-weight: 500;
  background: #fff0f0;
  padding: 2px 8px;
  border-radius: 8px;
}

.dest-desc {
  font-size: 13px;
  color: #666;
  line-height: 1.4;
  margin-bottom: 8px;
}

.dest-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #999;
  margin-bottom: 8px;
}

.dest-address {
  display: flex;
  align-items: center;
  gap: 2px;
}

.dest-city {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 6px;
}

.dest-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.dest-tag {
  padding: 3px 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
  font-size: 11px;
}

/* 输入区域 */
.input-area {
  display: flex;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.95);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.message-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e8e8e8;
  border-radius: 24px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.message-input:focus {
  border-color: #667eea;
}

.send-btn {
  padding: 10px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
