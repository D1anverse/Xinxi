<template>
  <div class="profile-view">
    <div class="profile-header">
      <button @click="handleBack" class="back-btn">← 返回</button>
      <h1>我的资料</h1>
      <button @click="handleEdit" class="edit-btn">编辑</button>
    </div>

    <div class="profile-content" v-if="profile">
      <!-- 头像 -->
      <div class="avatar-section">
        <div class="avatar">
          <img :src="profile.profile?.avatar || '/default-avatar.png'" alt="头像" />
        </div>
      </div>

      <!-- 基本信息 -->
      <div class="info-section">
        <div class="info-item">
          <label>昵称</label>
          <span>{{ profile.user?.nickname || '-' }}</span>
        </div>
        <div class="info-item">
          <label>性别</label>
          <span>{{ formatGender(profile.user?.gender) }}</span>
        </div>
        <div class="info-item">
          <label>年龄</label>
          <span>{{ profile.user?.age || '-' }} 岁</span>
        </div>
        <div class="info-item">
          <label>学校</label>
          <span>{{ profile.user?.university || '-' }}</span>
        </div>
        <div class="info-item">
          <label>专业</label>
          <span>{{ profile.user?.major || '-' }}</span>
        </div>
        <div class="info-item">
          <label>城市</label>
          <span>{{ profile.user?.city || '-' }}</span>
        </div>
      </div>

      <!-- 自我介绍 -->
      <div class="bio-section">
        <label>自我介绍</label>
        <p>{{ profile.profile?.bio || '还没有填写自我介绍' }}</p>
      </div>

      <!-- 标签 -->
      <div class="tags-section" v-if="profile.values?.tags?.length > 0">
        <label>我的标签</label>
        <div class="tags-list">
          <span v-for="tag in profile.values.tags" :key="tag" class="tag">{{ tag }}</span>
        </div>
      </div>

      <!-- 问答信息 -->
      <div class="questions-section">
        <h3>价值观维度</h3>
        <div class="dimension-list" v-if="profile.values?.dimensions?.length > 0">
          <div v-for="dim in profile.values.dimensions" :key="dim.name" class="dimension-item">
            <div class="dimension-header">
              <span class="dimension-name">{{ dim.name }}</span>
              <span class="dimension-level">{{ dim.level }}</span>
            </div>
            <div class="dimension-bar">
              <div class="dimension-fill" :style="{ width: dim.percentage + '%' }"></div>
            </div>
          </div>
        </div>
        <p v-else class="no-questions">还没有完成价值观问卷</p>
      </div>
    </div>

    <!-- 加载中 -->
    <div class="loading" v-else>
      <p>加载中...</p>
    </div>

    <!-- 退出登录按钮 -->
    <div class="logout-section">
      <button @click="handleLogout" class="logout-btn">退出登录</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const profile = ref(null)

// 格式化性别显示
const formatGender = (gender) => {
  const map = { male: '男', female: '女', other: '其他' }
  return map[gender] || '-'
}

// 加载用户资料
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
      }
    } else {
      console.error('加载资料失败')
    }
  } catch (error) {
    console.error('加载资料错误:', error)
  }
}

// 编辑资料
const handleEdit = () => {
  router.push('/profile/edit')
}

// 返回主页
const handleBack = () => {
  router.push('/')
}

// 退出登录
const handleLogout = () => {
  router.push('/logout')
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-view {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.back-btn {
  background: none;
  border: none;
  color: #666;
  font-size: 16px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
}

.back-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}

.profile-header h1 {
  font-size: 24px;
  color: #333;
}

.edit-btn {
  padding: 8px 16px;
  background-color: #ff6b6b;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
}

.edit-btn:hover {
  background-color: #ff5252;
}

.avatar-section {
  text-align: center;
  margin-bottom: 30px;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  margin: 0 auto;
  border: 3px solid #ff6b6b;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.info-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item label {
  color: #666;
  font-weight: 500;
}

.info-item span {
  color: #333;
}

.bio-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.bio-section label {
  display: block;
  color: #666;
  font-weight: 500;
  margin-bottom: 10px;
}

.bio-section p {
  color: #333;
  line-height: 1.6;
}

.tags-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tags-section label {
  display: block;
  color: #666;
  font-weight: 500;
  margin-bottom: 12px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
}

.questions-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.questions-section h3 {
  color: #333;
  margin-bottom: 15px;
}

.dimension-item {
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
}

.dimension-item:last-child {
  border-bottom: none;
}

.dimension-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.dimension-name {
  color: #333;
  font-weight: 500;
}

.dimension-level {
  color: #ff6b6b;
  font-size: 13px;
}

.dimension-bar {
  height: 6px;
  background: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
}

.dimension-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff6b6b, #ff8e8e);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.no-questions {
  color: #999;
  text-align: center;
  padding: 20px;
}

.loading {
  text-align: center;
  padding: 50px;
  color: #999;
}

.logout-section {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

.logout-btn {
  width: 100%;
  padding: 14px 24px;
  background: white;
  color: #666;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: #fff5f5;
  border-color: #ff6b6b;
  color: #ff6b6b;
}
</style>
