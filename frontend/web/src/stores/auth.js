import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_BASE = '/api'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  const needsQuestionnaire = ref(true) // 新用户默认需要填写问卷
  
  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const isAuthenticated = computed(() => !!user.value)
  
  // API 实例
  const api = axios.create({
    baseURL: API_BASE,
    headers: {
      'Content-Type': 'application/json'
    }
  })
  
  // 请求拦截器
  api.interceptors.request.use(config => {
    if (token.value) {
      config.headers.Authorization = `Bearer ${token.value}`
    }
    return config
  })
  
  // 方法
  async function login(email, password) {
    try {
      const response = await api.post('/auth/login', { email, password })
      const data = response.data
      
      token.value = data.token
      user.value = {
        user_id: data.user_id,
        needs_complete_profile: data.needs_complete_profile,
        needs_complete_questionnaire: data.needs_complete_questionnaire
      }
      needsQuestionnaire.value = data.needs_complete_questionnaire
      
      localStorage.setItem('token', data.token)
      
      return { 
        success: true, 
        needsCompleteProfile: data.needs_complete_profile,
        needsCompleteQuestionnaire: data.needs_complete_questionnaire
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || '登录失败' 
      }
    }
  }
  
  async function register(userData) {
    try {
      const response = await api.post('/auth/register', userData)
      // 检查响应是否有数据
      if (!response.data) {
        return { success: false, error: '服务器返回空响应，请检查后端服务' }
      }
      return { success: true, data: response.data }
    } catch (error) {
      // 优先使用后端返回的详细错误信息
      if (error.response?.data?.detail) {
        // 后端返回的是 FastAPI 的 ValidationError，格式是数组
        const details = error.response.data.detail
        if (Array.isArray(details)) {
          // 格式化 Pydantic 验证错误
          const errorMessages = details.map(err => {
            const field = err.loc?.join('.') || '字段'
            return `${field}: ${err.msg}`
          })
          return { success: false, error: errorMessages.join('\n') }
        }
        return { success: false, error: details }
      }
      
      // 网络错误
      if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
        return { success: false, error: '无法连接到服务器，请确保后端服务已启动' }
      }
      
      // 响应解析错误
      if (error.message.includes('JSON') || error.message.includes('Unexpected')) {
        return { success: false, error: '服务器响应异常，请检查后端服务是否正常运行' }
      }
      
      // 其他错误
      return { 
        success: false, 
        error: error.response?.data?.message || error.message || '注册失败' 
      }
    }
  }
  
  async function logout() {
    token.value = ''
    user.value = null
    needsQuestionnaire.value = true
    localStorage.removeItem('token')
  }
  
  async function fetchUserProfile() {
    if (!token.value) return
    
    try {
      const response = await api.get('/profile/me')
      if (response.data.success) {
        user.value = response.data.data
        // 检查是否需要填写问卷
        const values = response.data.data.values
        needsQuestionnaire.value = !values || !values.tags || values.tags.length === 0
      }
      return user.value
    } catch (error) {
      console.error('获取用户信息失败:', error)
      return null
    }
  }
  
  async function checkQuestionnaireStatus() {
    if (!token.value) return false
    
    try {
      const response = await api.get('/questionnaire/result')
      // 如果返回 404 说明没有问卷结果
      needsQuestionnaire.value = response.status === 404 || !response.data.success
      return needsQuestionnaire.value
    } catch (error) {
      needsQuestionnaire.value = true
      return true
    }
  }
  
  return {
    // 状态
    token,
    user,
    needsQuestionnaire,
    isLoggedIn,
    isAuthenticated,
    // 方法
    login,
    register,
    logout,
    fetchUserProfile,
    checkQuestionnaireStatus
  }
})
