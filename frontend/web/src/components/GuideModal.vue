<template>
  <div v-if="visible" class="modal-overlay" @click.self="handleCancel">
    <div class="modal-content">
      <div class="modal-icon">{{ icon }}</div>
      <h2>{{ title }}</h2>
      <p>{{ message }}</p>
      
      <div class="modal-actions">
        <button 
          v-if="showCancel" 
          class="btn btn--outline" 
          @click="handleCancel"
        >
          {{ cancelText }}
        </button>
        <button 
          class="btn btn--primary" 
          @click="handleConfirm"
        >
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '提示'
  },
  message: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: '📝'
  },
  confirmText: {
    type: String,
    default: '确定'
  },
  cancelText: {
    type: String,
    default: '取消'
  },
  showCancel: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['confirm', 'cancel', 'update:visible'])

const handleConfirm = () => {
  emit('confirm')
  emit('update:visible', false)
}

const handleCancel = () => {
  emit('cancel')
  emit('update:visible', false)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 32px;
  max-width: 400px;
  width: 90%;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.modal-content h2 {
  color: #333;
  font-size: 20px;
  margin-bottom: 12px;
}

.modal-content p {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 24px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.modal-actions button {
  flex: 1;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn--primary {
  background: #FF6B8A;
  color: white;
  border: none;
}

.btn--primary:hover {
  background: #ff5280;
}

.btn--outline {
  background: white;
  color: #666;
  border: 1px solid #ddd;
}

.btn--outline:hover {
  border-color: #FF6B8A;
  color: #FF6B8A;
}
</style>
