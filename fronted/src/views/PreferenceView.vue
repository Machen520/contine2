<template>
  <div class="auth-container">
    <h2>偏好设置</h2>
    <form @submit.prevent="savePreferences">
      <div class="checkbox-group">
        <label v-for="item in tags" :key="item">
          <input type="checkbox" :value="item" v-model="preferences" />
          {{ item }}
        </label>
      </div>
      <button type="submit">保存偏好</button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const preferences = ref([])
const tags = ['安静', '热闹', '咖啡', '文艺', '烧烤', 'KTV']

onMounted(async () => {
  const userId = localStorage.getItem('user_id')
  if (!userId) return alert('请先登录')
  // 可添加用户偏好预加载
})

const savePreferences = async () => {
  const res = await axios.post('http://localhost:5000/api/user/preferences', {
    preferences: preferences.value
  }, { withCredentials: true })

  if (res.data.code === 200) {
    alert('保存成功！推荐已同步更新')
  } else {
    alert(res.data.msg)
  }
}
</script>

<style scoped>
.auth-container { max-width: 300px; margin: auto; padding: 40px 10px; }
.checkbox-group { display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0; }
</style>
