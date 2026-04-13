<template>
  <div class="home-view">
    <header class="header">
      <h1>SoulMatch</h1>
      <nav>
        <!-- 未登录状态：显示登录/注册 -->
        <template v-if="!authStore.isLoggedIn">
          <router-link to="/login">登录</router-link>
          <router-link to="/register" class="btn btn--primary btn--small">注册</router-link>
        </template>
        
        <!-- 已登录状态：显示匹配/聊天/AI助手/我的 -->
        <template v-else>
          <router-link to="/matches">匹配</router-link>
          <router-link to="/chats" class="notification-link">
            聊天
            <span class="badge" v-if="unreadMessagesCount > 0">{{ unreadMessagesCount }}</span>
          </router-link>
          <router-link to="/ai-assistant" class="ai-link">AI助手</router-link>
          <router-link to="/profile">我的</router-link>
        </template>
      </nav>
    </header>
    
    <main class="content">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading">
        <p>加载中...</p>
      </div>
      
      <section class="hero" v-else>
        <h2>找到价值观契合的另一半</h2>
        <p>基于深度匹配算法，为大学生提供认真恋爱交友平台</p>
        
        <!-- 未登录状态：提示登录 -->
        <template v-if="!authStore.isLoggedIn">
          <p class="login-hint">登录后即可开始匹配</p>
          <div class="auth-buttons">
            <router-link to="/login" class="btn btn--primary btn--large">
              登录
            </router-link>
            <router-link to="/register" class="btn btn--outline btn--large">
              注册
            </router-link>
          </div>
        </template>
        
        <!-- 已登录但未完善资料：提示完善资料 -->
        <template v-else-if="!authStore.user">
          <p class="login-hint">请先完善您的个人资料</p>
          <router-link to="/profile" class="btn btn--primary btn--large">
            完善资料
          </router-link>
        </template>
        
        <!-- 已登录且已完善资料：可以开始匹配 -->
        <template v-else>
          <router-link to="/matches" class="btn btn--primary btn--large">
            开始匹配
          </router-link>
        </template>
      </section>
      
      <section class="features">
        <div class="feature-card">
          <h3>🎯 价值观匹配</h3>
          <p>通过 50 道深度问题，了解彼此的人生目标、性格特质和恋爱观念</p>
        </div>
        <div class="feature-card">
          <h3>🎓 学生认证</h3>
          <p>仅限在校大学生，使用 edu 邮箱验证，安全可靠</p>
        </div>
        <div class="feature-card">
          <h3>💕 认真交友</h3>
          <p>每日推荐 5 位高匹配度用户，鼓励深度交流</p>
        </div>
      </section>

      <!-- AI 助手入口 -->
      <section v-if="authStore.isLoggedIn" class="ai-section">
        <div class="ai-card" @click="goToAI">
          <div class="ai-avatar">✨</div>
          <div class="ai-info">
            <h3>AI 私人助理</h3>
            <p>情感咨询 · 约会安排 · 目的地推荐 · 帮你找人</p>
          </div>
          <span class="ai-arrow">→</span>
        </div>
      </section>
    </main>
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
const unreadMessagesCount = ref(0)

onMounted(async () => {
  // 如果已登录但没有用户信息，尝试获取
  if (authStore.isLoggedIn && !authStore.user) {
    await authStore.fetchUserProfile()
  }
  
  // 获取未读消息数量
  if (authStore.isLoggedIn) {
    fetchUnreadMessagesCount()
  }
  
  loading.value = false
})

async function fetchUnreadMessagesCount() {
  try {
    const response = await fetch('/api/chat/conversations', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      const items = data.data?.items || []
      unreadMessagesCount.value = items.reduce((sum, item) => sum + (item.unread_count || 0), 0)
    }
  } catch (err) {
    console.error('获取未读消息数失败:', err)
  }
}

// 监听路由变化，当从聊天页返回首页时刷新未读数
watch(() => route.path, (newPath, oldPath) => {
  if (oldPath && oldPath.startsWith('/chats') && newPath === '/home') {
    fetchUnreadMessagesCount()
  }
})

function goToAI() {
  router.push('/ai-assistant')
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';
.home-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #FFF5F7 0%, #F8F5F2 100%);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  box-shadow: $shadow-sm;
  
  h1 {
    color: $primary-color;
    font-size: 24px;
  }
  
  nav {
    display: flex;
    gap: 16px;
    align-items: center;
    
    a {
      color: $text-color;
      font-weight: 500;
      position: relative;
      
      &:hover {
        color: $primary-color;
      }
      
      &.btn {
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
      }
      
      &.notification-link {
        .badge {
          position: absolute;
          top: -6px;
          right: -10px;
          background: #ff4d4f;
          color: white;
          font-size: 10px;
          padding: 2px 5px;
          border-radius: 8px;
          min-width: 16px;
          text-align: center;
        }
      }
    }
  }
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px 24px;
}

.loading {
  text-align: center;
  padding: 48px;
  color: $text-light;
}

.hero {
  text-align: center;
  padding: 64px 0;
  
  h2 {
    font-size: 36px;
    color: $text-color;
    margin-bottom: 16px;
  }
  
  p {
    font-size: 18px;
    color: $text-light;
    margin-bottom: 32px;
  }
  
  .login-hint {
    font-size: 16px;
    color: $secondary-color;
    margin-bottom: 24px;
  }
  
  .auth-buttons {
    display: flex;
    gap: 16px;
    justify-content: center;
  }
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-top: 48px;
}

.feature-card {
  background: white;
  padding: 32px;
  border-radius: $radius-lg;
  box-shadow: $shadow-md;
  text-align: center;

  h3 {
    font-size: 20px;
    margin-bottom: 12px;
  }

  p {
    color: $text-light;
    line-height: 1.6;
  }
}

.ai-section {
  margin-top: 48px;
}

.ai-card {
  display: flex;
  align-items: center;
  gap: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px 32px;
  border-radius: $radius-lg;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4);
  }

  .ai-avatar {
    width: 60px;
    height: 60px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
  }

  .ai-info {
    flex: 1;

    h3 {
      color: white;
      font-size: 20px;
      margin-bottom: 6px;
    }

    p {
      color: rgba(255, 255, 255, 0.85);
      font-size: 14px;
    }
  }

  .ai-arrow {
    color: white;
    font-size: 24px;
    opacity: 0.8;
  }
}

.header nav .ai-link {
  color: #667eea;
  font-weight: 600;

  &:hover {
    color: #764ba2;
  }
}
</style>
