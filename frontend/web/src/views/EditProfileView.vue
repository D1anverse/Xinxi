<template>
  <div class="edit-profile-view">
    <div class="edit-header">
      <button @click="handleBack" class="back-btn">← 返回</button>
      <h1>编辑资料</h1>
      <button @click="handleSave" class="save-btn" :disabled="saving">
        {{ saving ? '保存中...' : '保存' }}
      </button>
    </div>

    <div class="edit-form" v-if="profile">
      <!-- 头像选择 -->
      <div class="form-section">
        <label>选择头像</label>
        <div class="avatar-grid">
          <div 
            v-for="(avatar, index) in defaultAvatars" 
            :key="index"
            class="avatar-option"
            :class="{ selected: formData.avatar === avatar.url }"
            @click="selectAvatar(avatar.url)"
          >
            <img :src="avatar.url" :alt="`头像${index + 1}`" />
            <div v-if="formData.avatar === avatar.url" class="selected-check">✓</div>
          </div>
        </div>
      </div>

      <!-- 交友目的 -->
      <div class="form-section">
        <label>交友目的</label>
        <div class="purpose-options">
          <label class="purpose-option" :class="{ active: formData.purpose === 'dating' }">
            <input type="radio" v-model="formData.purpose" value="dating" />
            <span class="purpose-icon">💕</span>
            <span class="purpose-text">恋爱</span>
          </label>
          <label class="purpose-option" :class="{ active: formData.purpose === 'friendship' }">
            <input type="radio" v-model="formData.purpose" value="friendship" />
            <span class="purpose-icon">🤝</span>
            <span class="purpose-text">交友</span>
          </label>
          <label class="purpose-option" :class="{ active: formData.purpose === 'both' }">
            <input type="radio" v-model="formData.purpose" value="both" />
            <span class="purpose-icon">💕🤝</span>
            <span class="purpose-text">都可以</span>
          </label>
        </div>
      </div>

      <!-- 基本信息 -->
      <div class="form-section">
        <label>基本信息</label>
        
        <div class="form-item" :class="{ 'has-error': errors.nickname }">
          <span class="form-label">昵称 *</span>
          <input type="text" v-model="formData.nickname" placeholder="请输入昵称（2-20字符）" maxlength="20" @input="clearError('nickname')" />
        </div>

        <div class="form-item" :class="{ 'has-error': errors.gender }">
          <span class="form-label">性别 *</span>
          <select v-model="formData.gender" @change="clearError('gender')">
            <option value="">请选择</option>
            <option value="male">男</option>
            <option value="female">女</option>
            <option value="other">其他</option>
          </select>
        </div>

        <div class="form-item" :class="{ 'has-error': errors.birth_date }">
          <span class="form-label">出生日期 *</span>
          <input type="date" v-model="formData.birth_date" @change="clearError('birth_date')" />
        </div>

        <div class="form-item">
          <span class="form-label">学校</span>
          <input type="text" v-model="formData.university" placeholder="学校" />
        </div>

        <div class="form-item">
          <span class="form-label">专业</span>
          <input type="text" v-model="formData.major" placeholder="专业" />
        </div>

        <div class="form-item">
          <span class="form-label">城市</span>
          <input type="text" v-model="formData.city" placeholder="所在城市" />
        </div>
      </div>

      <!-- 自我介绍 -->
      <div class="form-section">
        <label>自我介绍</label>
        <textarea v-model="formData.bio" placeholder="介绍一下自己吧..." maxlength="500" rows="4"></textarea>
        <span class="char-count">{{ formData.bio?.length || 0 }}/500</span>
      </div>

      <!-- 自定义标签 -->
      <div class="form-section">
        <label>自定义标签</label>
        <p class="section-hint">添加一些标签让别人更了解你</p>
        <div class="tags-input-area">
          <div class="current-tags">
            <span v-for="tag in formData.custom_tags" :key="tag" class="custom-tag">
              {{ tag }}
              <button @click="removeTag(tag)" class="tag-remove">×</button>
            </span>
          </div>
          <div class="tag-input-row">
            <input 
              type="text" 
              v-model="newTag" 
              placeholder="输入标签后按回车添加"
              @keydown.enter.prevent="addTag"
              maxlength="20"
            />
            <button @click="addTag" class="add-tag-btn" :disabled="!newTag.trim()">添加</button>
          </div>
        </div>
        <div class="suggested-tags">
          <span class="suggest-label">推荐标签：</span>
          <button 
            v-for="tag in suggestedTags" 
            :key="tag" 
            class="suggest-tag"
            :disabled="formData.custom_tags.includes(tag)"
            @click="addSuggestedTag(tag)"
          >
            {{ tag }}
          </button>
        </div>
      </div>

      <!-- 偏好设置 -->
      <div class="form-section">
        <label>偏好设置</label>
        
        <div class="form-item">
          <span class="form-label">希望认识</span>
          <select v-model="formData.preferred_gender">
            <option value="any">不限</option>
            <option value="male">男生</option>
            <option value="female">女生</option>
          </select>
        </div>

        <div class="form-item" :class="{ 'has-error': errors.age_range }">
          <span class="form-label">年龄范围</span>
          <div class="age-range">
            <input type="number" v-model.number="formData.min_age" min="18" max="100" placeholder="最小" @input="clearError('age_range')" />
            <span>至</span>
            <input type="number" v-model.number="formData.max_age" min="18" max="100" placeholder="最大" @input="clearError('age_range')" />
          </div>
        </div>
      </div>

      <!-- 可见性设置 -->
      <div class="form-section">
        <label>信息可见性</label>
        
        <div class="toggle-item">
          <span>显示学校</span>
          <input type="checkbox" v-model="formData.show_university" />
        </div>

        <div class="toggle-item">
          <span>显示专业</span>
          <input type="checkbox" v-model="formData.show_major" />
        </div>

        <div class="toggle-item">
          <span>显示年龄</span>
          <input type="checkbox" v-model="formData.show_age" />
        </div>
      </div>
    </div>

    <!-- 加载中 -->
    <div class="loading" v-else>
      <p>加载中...</p>
    </div>

    <!-- 提示 -->
    <div v-if="message" :class="['message', message.type]">
      {{ message.text }}
    </div>

    <!-- 错误详情 -->
    <div v-if="errorDetails.length > 0" class="error-panel">
      <div class="error-title">请修正以下问题：</div>
      <ul>
        <li v-for="(err, index) in errorDetails" :key="index">{{ err }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const profile = ref(null)
const saving = ref(false)
const message = ref(null)
const errors = reactive({})
const errorDetails = ref([])
const hasChanges = ref(false)
const newTag = ref('')

// 默认头像
const defaultAvatars = [
  { id: 1, url: '/avatars/avatar1.svg' },
  { id: 2, url: '/avatars/avatar2.svg' },
  { id: 3, url: '/avatars/avatar3.svg' },
  { id: 4, url: '/avatars/avatar4.svg' }
]

// 推荐标签
const suggestedTags = [
  '游戏', '音乐', '运动', '阅读', '电影', 
  '旅行', '美食', '摄影', '绘画', '编程',
  '健身', '追剧', '动漫', '追星', '撸猫',
  '学习', '社团', '创业', '志愿者', '追星'
]

const formData = reactive({
  nickname: '',
  avatar: '/avatars/avatar1.svg',
  gender: '',
  birth_date: '',
  university: '',
  major: '',
  city: '',
  bio: '',
  purpose: 'dating', // dating, friendship, both
  custom_tags: [],
  preferred_gender: 'any',
  min_age: 18,
  max_age: 35,
  show_university: false,
  show_major: false,
  show_age: true
})

// 选择头像
const selectAvatar = (url) => {
  formData.avatar = url
  hasChanges.value = true
}

// 添加自定义标签
const addTag = () => {
  const tag = newTag.value.trim()
  if (tag && !formData.custom_tags.includes(tag) && formData.custom_tags.length < 10) {
    formData.custom_tags.push(tag)
    newTag.value = ''
    hasChanges.value = true
  }
}

// 添加推荐标签
const addSuggestedTag = (tag) => {
  if (!formData.custom_tags.includes(tag) && formData.custom_tags.length < 10) {
    formData.custom_tags.push(tag)
    hasChanges.value = true
  }
}

// 移除标签
const removeTag = (tag) => {
  const index = formData.custom_tags.indexOf(tag)
  if (index > -1) {
    formData.custom_tags.splice(index, 1)
    hasChanges.value = true
  }
}

// 加载资料
const loadProfile = async () => {
  try {
    const response = await fetch('/api/profile/me', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      if (data.success) {
        profile.value = data.data
        
        // 填充表单
        const user = data.data.user || {}
        const profileInfo = data.data.profile || {}
        
        formData.nickname = user.nickname || ''
        formData.avatar = profileInfo.avatar || '/avatars/avatar1.svg'
        formData.gender = user.gender || ''
        formData.birth_date = user.birth_date || ''
        formData.university = user.university || ''
        formData.major = user.major || ''
        formData.city = user.city || ''
        formData.bio = profileInfo.bio || ''
        formData.purpose = profileInfo.purpose || 'dating'
        formData.custom_tags = profileInfo.custom_tags || []
        
        // 偏好设置
        const prefs = profileInfo.preferences || {}
        formData.preferred_gender = prefs.preferred_gender || 'any'
        formData.min_age = prefs.min_age || 18
        formData.max_age = prefs.max_age || 35
        
        // 可见性设置
        const visibility = profileInfo.visibility || {}
        formData.show_university = visibility.show_university || false
        formData.show_major = visibility.show_major || false
        formData.show_age = visibility.show_age !== false
        
        // 标记已加载
        hasChanges.value = false
      }
    }
  } catch (error) {
    console.error('加载资料失败:', error)
    showMessage('加载资料失败', 'error')
  }
}

// 清除错误
const clearError = (field) => {
  delete errors[field]
  errorDetails.value = errorDetails.value.filter(e => !e.includes(getFieldName(field)))
  hasChanges.value = true
}

// 获取字段中文名
const getFieldName = (field) => {
  const names = {
    nickname: '昵称',
    gender: '性别',
    birth_date: '出生日期',
    age_range: '年龄范围',
    min_age: '最小年龄',
    max_age: '最大年龄'
  }
  return names[field] || field
}

// 表单验证
const validateForm = () => {
  const newErrors = []
  errorDetails.value = []
  
  // 昵称验证
  if (!formData.nickname || formData.nickname.trim().length < 2) {
    errors.nickname = true
    newErrors.push('昵称：长度需要在 2-20 个字符之间')
  } else if (formData.nickname.length > 20) {
    errors.nickname = true
    newErrors.push('昵称：长度不能超过 20 个字符')
  }
  
  // 性别验证
  if (!formData.gender) {
    errors.gender = true
    newErrors.push('性别：请选择性别')
  }
  
  // 出生日期验证
  if (!formData.birth_date) {
    errors.birth_date = true
    newErrors.push('出生日期：请选择出生日期')
  } else {
    const birth = new Date(formData.birth_date)
    const today = new Date()
    let age = today.getFullYear() - birth.getFullYear()
    const monthDiff = today.getMonth() - birth.getMonth()
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--
    }
    
    if (age < 18) {
      errors.birth_date = true
      newErrors.push('出生日期：年龄必须大于等于 18 岁')
    }
  }
  
  // 年龄范围验证
  if (formData.min_age && formData.max_age) {
    if (formData.min_age > formData.max_age) {
      errors.age_range = true
      newErrors.push('年龄范围：最小年龄不能大于最大年龄')
    }
  }
  
  errorDetails.value = newErrors
  return newErrors.length === 0
}

// 执行保存
const saveProfile = async () => {
  saving.value = true
  errorDetails.value = []
  
  try {
    const response = await fetch('/api/profile/me', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        nickname: formData.nickname,
        gender: formData.gender,
        birth_date: formData.birth_date,
        city: formData.city,
        university: formData.university,
        avatar: formData.avatar,
        bio: formData.bio,
        major: formData.major,
        purpose: formData.purpose,
        custom_tags: formData.custom_tags,
        preferred_gender: formData.preferred_gender,
        min_age: formData.min_age,
        max_age: formData.max_age,
        preferred_locations: [],
        show_university: formData.show_university,
        show_major: formData.show_major,
        show_age: formData.show_age
      })
    })

    const data = await response.json()
    
    if (data.success) {
      hasChanges.value = false
      return { success: true }
    } else {
      const backendErrors = parseBackendError(data)
      errorDetails.value = backendErrors
      return { success: false, error: backendErrors.join('；') }
    }
  } catch (error) {
    console.error('保存失败:', error)
    return { success: false, error: '网络错误，请检查连接后重试' }
  } finally {
    saving.value = false
  }
}

// 解析后端错误
const parseBackendError = (data) => {
  const errors = []
  
  if (data.detail) {
    if (Array.isArray(data.detail)) {
      data.detail.forEach(err => {
        const field = err.loc?.slice(1).join('.') || '未知字段'
        errors.push(`${field}：${err.msg}`)
      })
    } else {
      errors.push(data.detail)
    }
  }
  
  if (data.message) {
    errors.push(data.message)
  }
  
  return errors.length > 0 ? errors : ['保存失败，请重试']
}

// 保存
const handleSave = async () => {
  if (!validateForm()) {
    return
  }

  const result = await saveProfile()
  
  if (result.success) {
    alert('保存成功！')
    await authStore.fetchUserProfile()
    router.back()
  } else {
    showMessage(result.error, 'error')
  }
}

// 返回（带自动保存）
const handleBack = async () => {
  if (!hasChanges.value) {
    router.back()
    return
  }
  
  const confirmSave = confirm('有未保存的更改，是否保存？')
  
  if (confirmSave) {
    if (!validateForm()) {
      showMessage('请修正表单中的错误', 'error')
      return
    }
    
    const result = await saveProfile()
    if (result.success) {
      alert('已保存！')
      await authStore.fetchUserProfile()
      router.back()
    } else {
      showMessage(result.error, 'error')
      return
    }
  } else {
    router.back()
  }
}

// 监听表单变化
watch(formData, () => {
  hasChanges.value = true
}, { deep: true })

onMounted(() => {
  loadProfile()
})
</script>

<style scoped lang="scss">
.edit-profile-view {
  padding: 16px;
  max-width: 600px;
  margin: 0 auto;
  min-height: 100vh;
  background: #f8f8f8;
}

.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 12px 0;
  background: white;
  border-radius: 12px;
  padding: 12px 16px;
}

.edit-header h1 {
  font-size: 18px;
  color: #333;
}

.back-btn {
  background: none;
  border: none;
  color: #666;
  font-size: 16px;
  cursor: pointer;
  padding: 8px;
}

.save-btn {
  background: #ff6b6b;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
}

.save-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-section {
  background: white;
  border-radius: 12px;
  padding: 16px;
}

.form-section > label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
  font-size: 15px;
}

.section-hint {
  font-size: 13px;
  color: #999;
  margin-bottom: 12px;
  margin-top: -8px;
}

// 头像选择
.avatar-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.avatar-option {
  position: relative;
  aspect-ratio: 1;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  border: 3px solid transparent;
  transition: all 0.2s;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  &:hover {
    border-color: #ffb3b3;
  }
  
  &.selected {
    border-color: #ff6b6b;
  }
}

.selected-check {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 22px;
  height: 22px;
  background: #ff6b6b;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
}

// 交友目的
.purpose-options {
  display: flex;
  gap: 12px;
}

.purpose-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 8px;
  border: 2px solid #eee;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  
  input {
    display: none;
  }
  
  .purpose-icon {
    font-size: 28px;
    margin-bottom: 6px;
  }
  
  .purpose-text {
    font-size: 14px;
    color: #666;
  }
  
  &:hover {
    border-color: #ffb3b3;
  }
  
  &.active {
    border-color: #ff6b6b;
    background: #fff5f5;
    
    .purpose-text {
      color: #ff6b6b;
      font-weight: 500;
    }
  }
}

.form-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.form-item:last-child {
  margin-bottom: 0;
}

.form-item.has-error input,
.form-item.has-error select {
  border-color: #f44336;
  background-color: #fff8f8;
}

.form-label {
  width: 70px;
  color: #666;
  font-size: 14px;
  flex-shrink: 0;
}

.form-item input[type="text"],
.form-item input[type="number"],
.form-item input[type="date"],
.form-item select,
textarea {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
}

.form-item input:focus,
.form-item select:focus,
textarea:focus {
  border-color: #ff6b6b;
}

textarea {
  width: 100%;
  resize: vertical;
  font-family: inherit;
}

.char-count {
  display: block;
  text-align: right;
  color: #999;
  font-size: 12px;
  margin-top: 4px;
}

.age-range {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.age-range input {
  width: 60px;
  text-align: center;
}

.age-range span {
  color: #666;
}

// 自定义标签
.tags-input-area {
  margin-bottom: 12px;
}

.current-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
  min-height: 32px;
}

.custom-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
  color: white;
  border-radius: 16px;
  font-size: 13px;
}

.tag-remove {
  background: none;
  border: none;
  color: white;
  font-size: 16px;
  cursor: pointer;
  padding: 0;
  margin-left: 2px;
  opacity: 0.8;
  
  &:hover {
    opacity: 1;
  }
}

.tag-input-row {
  display: flex;
  gap: 8px;
  
  input {
    flex: 1;
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 14px;
    outline: none;
    
    &:focus {
      border-color: #ff6b6b;
    }
  }
}

.add-tag-btn {
  padding: 10px 16px;
  background: #ff6b6b;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
}

.suggested-tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.suggest-label {
  font-size: 13px;
  color: #999;
}

.suggest-tag {
  padding: 4px 12px;
  background: #f5f5f5;
  color: #666;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover:not(:disabled) {
    background: #ffebeb;
    border-color: #ff6b6b;
    color: #ff6b6b;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.toggle-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;
}

.toggle-item:last-child {
  border-bottom: none;
}

.toggle-item span {
  color: #333;
  font-size: 14px;
}

.toggle-item input[type="checkbox"] {
  width: 20px;
  height: 20px;
  accent-color: #ff6b6b;
}

.loading {
  text-align: center;
  padding: 50px;
  color: #999;
}

.message {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  z-index: 1000;
  background: #333;
  color: white;
}

.error-panel {
  background: #fff3f3;
  border: 1px solid #ffcdd2;
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}

.error-title {
  color: #c62828;
  font-weight: 600;
  margin-bottom: 8px;
}

.error-panel ul {
  margin: 0;
  padding-left: 20px;
}

.error-panel li {
  color: #d32f2f;
  font-size: 14px;
  margin-bottom: 4px;
}
</style>
