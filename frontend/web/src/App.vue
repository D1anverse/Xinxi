<template>
  <div id="app">
    <router-view />
    
    <!-- 问卷引导弹窗 -->
    <GuideModal
      v-model:visible="showQuestionnaireModal"
      title="完成价值观问卷"
      message="为了给你推荐最匹配的伙伴，请先完成我们的价值观问卷。问卷包含50道题目，大约需要5-10分钟。"
      icon="📝"
      confirm-text="立即填写"
      cancel-text="稍后再说"
      @confirm="goToQuestionnaire"
      @cancel="goHome"
    />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import GuideModal from '@/components/GuideModal.vue'

const router = useRouter()
const authStore = useAuthStore()

const showQuestionnaireModal = ref(false)

onMounted(async () => {
  // 检查是否需要填写问卷
  await checkQuestionnaire()
})

// 监听路由变化，检查问卷状态
watch(() => router.currentRoute.value.path, async (newPath) => {
  // 如果用户已登录且在首页，检查问卷状态
  if (authStore.isLoggedIn && newPath === '/home') {
    await checkQuestionnaire()
  }
})

async function checkQuestionnaire() {
  // 已登录但还未检查过问卷状态
  if (authStore.isLoggedIn) {
    // 尝试获取用户资料来判断是否需要填写问卷
    const profile = await authStore.fetchUserProfile()
    
    if (profile && profile.values) {
      const hasValues = profile.values.tags && profile.values.tags.length > 0
      authStore.needsQuestionnaire = !hasValues
    }
    
    // 如果需要填写问卷且用户还没有看到弹窗
    if (authStore.needsQuestionnaire) {
      // 检查是否已经显示过（通过 localStorage 标记）
      const hasSeenModal = localStorage.getItem('questionnaire_modal_shown')
      if (!hasSeenModal) {
        showQuestionnaireModal.value = true
        localStorage.setItem('questionnaire_modal_shown', 'true')
      }
    }
  }
}

function goToQuestionnaire() {
  router.push('/questionnaire')
}

function goHome() {
  router.push('/home')
}
</script>

<style>
#app {
  width: 100%;
  height: 100vh;
}
</style>
