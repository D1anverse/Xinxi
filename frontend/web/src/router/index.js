import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/HomeView.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue')
  },
  {
    path: '/questionnaire',
    name: 'Questionnaire',
    component: () => import('@/views/QuestionnaireView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile/edit',
    name: 'EditProfile',
    component: () => import('@/views/EditProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/matches',
    name: 'Matches',
    component: () => import('@/views/MatchesView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chat/:userId',
    name: 'Chat',
    component: () => import('@/views/ChatView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/logout',
    name: 'Logout',
    component: () => import('@/views/LogoutView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: () => import('@/views/NotificationsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/skipped',
    name: 'Skipped',
    component: () => import('@/views/SkippedView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chats',
    name: 'ChatList',
    component: () => import('@/views/ChatListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ai-assistant',
    name: 'AIAssistant',
    component: () => import('@/views/AIAssistantView.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 如果页面需要登录
  if (to.meta.requiresAuth) {
    if (!authStore.isLoggedIn) {
      // 未登录，跳转到登录页，并记录目标页面
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    
    // 已登录但没有用户信息，尝试获取
    if (!authStore.user) {
      await authStore.fetchUserProfile()
    }
    
    // 仅在首次访问匹配页面时检查问卷状态（仅一次）
    if (to.name === 'Matches' && authStore.needsQuestionnaire) {
      const hasCompleted = await authStore.checkQuestionnaireStatus()
      if (hasCompleted) {
        authStore.needsQuestionnaire = false
      } else {
        // 用户取消后，标记为已询问过，不再重复弹
        authStore.needsQuestionnaire = false
      }
    }
  }
  
  // 如果已登录，访问登录/注册页则跳转到首页
  if (to.name === 'Login' && authStore.isLoggedIn) {
    next('/home')
    return
  }
  
  if (to.name === 'Register' && authStore.isLoggedIn) {
    next('/home')
    return
  }
  
  next()
})

export default router
