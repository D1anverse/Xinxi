<template>
  <div class="register-view">
    <div class="register-container">
      <h1>加入 SoulMatch</h1>
      <p class="subtitle">开启你的认真恋爱之旅</p>
      
      <form @submit.prevent="handleRegister" class="register-form">
        <!-- 错误提示 -->
        <div v-if="errorMessage" class="error-alert">
          <div class="error-content">
            <span class="error-icon">⚠️</span>
            <div class="error-text">
              <strong>注册失败</strong>
              <pre>{{ errorMessage }}</pre>
            </div>
          </div>
          <button type="button" class="close-btn" @click="errorMessage = ''">×</button>
        </div>
        
        <div class="form-group">
          <label for="email">学校邮箱</label>
          <input 
            type="email" 
            id="email" 
            v-model="form.email" 
            placeholder="example@university.edu.cn"
            required
          />
          <small class="hint">仅支持 edu.cn 教育邮箱注册</small>
        </div>
        
        <div class="form-group">
          <label for="nickname">昵称</label>
          <input 
            type="text" 
            id="nickname" 
            v-model="form.nickname" 
            placeholder="如何称呼你"
            maxlength="20"
            required
          />
        </div>
        
        <div class="form-group">
          <label>性别</label>
          <div class="gender-selector">
            <label class="radio-card">
              <input type="radio" v-model="form.gender" value="male" required />
              <span>👨 男生</span>
            </label>
            <label class="radio-card">
              <input type="radio" v-model="form.gender" value="female" required />
              <span>👩 女生</span>
            </label>
          </div>
        </div>
        
        <div class="form-group">
          <label for="birthDate">出生日期</label>
          <input 
            type="date" 
            id="birthDate" 
            v-model="form.birthDate" 
            required
          />
        </div>
        
        <div class="form-group">
          <label for="university">学校</label>
          <input 
            type="text" 
            id="university" 
            v-model="form.university" 
            placeholder="请输入学校全称"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="form.password" 
            placeholder="至少 8 位，包含字母和数字"
            minlength="8"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input 
            type="password" 
            id="confirmPassword" 
            v-model="form.confirmPassword" 
            placeholder="再次输入密码"
            required
          />
        </div>
        
        <div class="form-group checkbox-group">
          <label>
            <input type="checkbox" v-model="form.agreeTerms" required />
            我已阅读并同意
            <a href="#" target="_blank">用户协议</a>
            和
            <a href="#" target="_blank">隐私政策</a>
          </label>
        </div>
        
        <button type="submit" class="btn btn--primary btn--block btn--large" :disabled="loading">
          {{ loading ? '注册中...' : '开始注册' }}
        </button>
      </form>
      
      <p class="login-link">
        已有账号？
        <router-link to="/login">立即登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const errorMessage = ref('')

const form = reactive({
  email: '',
  nickname: '',
  gender: '',
  birthDate: '',
  university: '',
  password: '',
  confirmPassword: '',
  agreeTerms: false
})

async function handleRegister() {
  // 清除之前的错误
  errorMessage.value = ''
  
  // 验证必填项
  if (!form.email || !form.nickname || !form.gender || !form.birthDate || 
      !form.university || !form.password || !form.confirmPassword) {
    errorMessage.value = '请填写所有必填项'
    return
  }
  
  // 验证密码
  if (form.password !== form.confirmPassword) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }
  
  // 验证教育邮箱
  if (!form.email.endsWith('.edu.cn')) {
    errorMessage.value = '请使用教育邮箱 (.edu.cn) 注册'
    return
  }
  
  // 验证年龄
  const birthDate = new Date(form.birthDate)
  const today = new Date()
  const age = today.getFullYear() - birthDate.getFullYear()
  
  if (age < 18) {
    errorMessage.value = '抱歉，未满 18 岁不能注册'
    return
  }
  
  // 验证服务条款
  if (!form.agreeTerms) {
    errorMessage.value = '请阅读并同意用户协议和隐私政策'
    return
  }
  
  loading.value = true
  
  try {
    // 先注册
    const result = await authStore.register({
      email: form.email,
      nickname: form.nickname,
      gender: form.gender,
      birth_date: form.birthDate,
      university: form.university,
      password: form.password
    })
    
    if (!result.success) {
      errorMessage.value = result.error
      return
    }
    
    // 注册成功后自动登录
    const loginResult = await authStore.login(form.email, form.password)
    
    if (loginResult.success) {
      // 清除弹窗显示标记
      localStorage.removeItem('questionnaire_modal_shown')
      alert('注册成功！欢迎加入 SoulMatch')
      // 注册后直接跳转到问卷页面
      router.push('/questionnaire')
    } else {
      // 登录失败，跳转到登录页
      alert('注册成功！请登录')
      router.push('/login')
    }
  } catch (error) {
    errorMessage.value = '注册失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.register-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #FFF5F7 0%, #F8F5F2 100%);
  padding: 24px;
}

.register-container {
  width: 100%;
  max-width: 480px;
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

.register-form {
  .form-group {
    margin-bottom: 20px;
    
    label {
      display: block;
      margin-bottom: 8px;
      color: $text-color;
      font-weight: 500;
    }
    
    input[type="text"],
    input[type="email"],
    input[type="password"],
    input[type="date"] {
      width: 100%;
      padding: 12px 16px;
      border: 1px solid $border-color;
      border-radius: $radius-md;
      font-size: 14px;
      
      &:focus {
        border-color: $primary-color;
      }
    }
    
    .hint {
      display: block;
      margin-top: 4px;
      font-size: 12px;
      color: $text-light;
    }
  }
}

.error-alert {
  background: #FFF2F0;
  border: 1px solid #FFccc7;
  border-radius: $radius-md;
  padding: 16px;
  margin-bottom: 24px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  
  .error-content {
    flex: 1;
    display: flex;
    gap: 12px;
    
    .error-icon {
      font-size: 20px;
    }
    
    .error-text {
      flex: 1;
      
      strong {
        display: block;
        color: #F5222D;
        margin-bottom: 8px;
      }
      
      pre {
        margin: 0;
        font-size: 14px;
        color: #8c8c8c;
        white-space: pre-wrap;
        font-family: inherit;
        line-height: 1.6;
      }
    }
  }
  
  .close-btn {
    background: none;
    border: none;
    font-size: 24px;
    color: #8c8c8c;
    cursor: pointer;
    padding: 0;
    line-height: 1;
    
    &:hover {
      color: #F5222D;
    }
  }
}

.gender-selector {
  display: flex;
  gap: 16px;
  
  .radio-card {
    flex: 1;
    display: flex;
    align-items: center;
    padding: 12px;
    border: 1px solid $border-color;
    border-radius: $radius-md;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:has(input:checked) {
      border-color: $primary-color;
      background-color: rgba($primary-color, 0.05);
    }
    
    input {
      margin-right: 8px;
    }
  }
}

.checkbox-group {
  label {
    display: flex;
    align-items: flex-start;
    font-weight: normal;
    font-size: 14px;
    
    input {
      margin-top: 4px;
      margin-right: 8px;
    }
    
    a {
      color: $primary-color;
      text-decoration: underline;
    }
  }
}

.login-link {
  text-align: center;
  margin-top: 24px;
  color: $text-light;
  
  a {
    color: $primary-color;
    font-weight: 500;
  }
}
</style>
