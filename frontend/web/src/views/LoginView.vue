<template>
  <div class="login-view">
    <div class="login-container">
      <h1>SoulMatch</h1>
      <p class="subtitle">大学生恋爱交友平台</p>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <!-- 错误提示 -->
        <div v-if="errorMessage" class="error-alert">
          <span class="error-icon">⚠️</span>
          <span>{{ errorMessage }}</span>
        </div>
        
        <div class="form-group">
          <label for="email">邮箱</label>
          <input 
            type="email" 
            id="email" 
            v-model="email" 
            placeholder="请输入学校邮箱"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            placeholder="请输入密码"
            required
          />
        </div>
        
        <button type="submit" class="btn btn--primary btn--block btn--large">
          登录
        </button>
      </form>
      
      <p class="register-link">
        还没有账号？
        <router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const errorMessage = ref('')

async function handleLogin() {
  errorMessage.value = ''
  const result = await authStore.login(email.value, password.value)
  
  if (result.success) {
    // 清除弹窗显示标记，允许重新显示
    localStorage.removeItem('questionnaire_modal_shown')
    
    // 如果有重定向参数，跳转到目标页面
    const redirect = route.query.redirect
    if (redirect) {
      router.push(redirect)
      return
    }
    
    // 检查用户是否已完成问卷
    const hasCompletedQuestionnaire = await authStore.checkQuestionnaireStatus()
    if (!hasCompletedQuestionnaire) {
      // 已完成问卷，跳转到首页
      router.push('/home')
    } else {
      // 未完成问卷，跳转到问卷页面
      router.push('/questionnaire')
    }
  } else {
    errorMessage.value = result.error
  }
}
</script>

<style scoped lang="scss">
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #FFF5F7 0%, #F8F5F2 100%);
}

.login-container {
  width: 100%;
  max-width: 400px;
  padding: 48px 32px;
  background: white;
  border-radius: $radius-xl;
  box-shadow: $shadow-lg;
  
  h1 {
    text-align: center;
    color: $primary-color;
    font-size: 32px;
    margin-bottom: 8px;
  }
  
  .subtitle {
    text-align: center;
    color: $text-light;
    margin-bottom: 32px;
  }
}

.error-alert {
  background: #FFF2F0;
  border: 1px solid #FFccc7;
  border-radius: $radius-md;
  padding: 12px 16px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #F5222D;
  font-size: 14px;
  
  .error-icon {
    font-size: 16px;
  }
}

.login-form {
  .form-group {
    margin-bottom: 24px;
    
    label {
      display: block;
      margin-bottom: 8px;
      color: $text-color;
      font-weight: 500;
    }
    
    input {
      width: 100%;
      padding: 12px 16px;
      border: 1px solid $border-color;
      border-radius: $radius-md;
      font-size: 14px;
      
      &:focus {
        border-color: $primary-color;
      }
    }
  }
}

.register-link {
  text-align: center;
  margin-top: 24px;
  color: $text-light;
  
  a {
    color: $primary-color;
    font-weight: 500;
  }
}
</style>
