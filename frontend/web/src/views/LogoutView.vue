<template>
  <div class="logout-view">
    <div class="logout-card">
      <div class="icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
          <polyline points="16 17 21 12 16 7"></polyline>
          <line x1="21" y1="12" x2="9" y2="12"></line>
        </svg>
      </div>
      <h1>确定要退出登录吗？</h1>
      <p>退出后将返回登录页面</p>
      
      <div class="actions">
        <button @click="handleLogout" class="confirm-btn">确认退出</button>
        <button @click="handleCancel" class="cancel-btn">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

onMounted(() => {
  // 如果未登录，直接跳转
  if (!authStore.isLoggedIn) {
    router.replace('/login')
  }
})

const handleLogout = async () => {
  await authStore.logout()
  alert('已成功退出登录')
  router.replace('/login')
}

const handleCancel = () => {
  router.back()
}
</script>

<style scoped lang="scss">
.logout-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #FFF5F7 0%, #F8F5F2 100%);
  padding: 20px;
}

.logout-card {
  background: white;
  border-radius: 20px;
  padding: 48px 32px;
  text-align: center;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  max-width: 360px;
  width: 100%;

  .icon {
    margin-bottom: 24px;
    
    svg {
      color: #ff6b6b;
    }
  }

  h1 {
    font-size: 22px;
    color: #333;
    margin-bottom: 12px;
  }

  p {
    color: #888;
    font-size: 14px;
    margin-bottom: 32px;
  }
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.confirm-btn {
  width: 100%;
  padding: 14px 24px;
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
  }

  &:active {
    transform: translateY(0);
  }
}

.cancel-btn {
  width: 100%;
  padding: 14px 24px;
  background: white;
  color: #666;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: #f5f5f5;
    border-color: #ccc;
  }
}
</style>
