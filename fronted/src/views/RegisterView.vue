<template>
  <div class="auth-container">
    <h2>注册</h2>
    <form @submit.prevent="register">
      <input v-model="username" placeholder="用户名" required />
      <input v-model="password" type="password" placeholder="密码" required />
      <label>请选择初始偏好（可多选）</label>
      <div class="checkbox-group">
        <label v-for="item in tags" :key="item">
          <input type="checkbox" :value="item" v-model="preferences" />
          {{ item }}
        </label>
      </div>
      <button type="submit">注册</button>
    </form>
    <p>已有账号？<router-link to="/login">前往登录</router-link></p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const preferences = ref([])
const tags = ['安静', '热闹', '咖啡', '文艺', '烧烤', 'KTV']
const router = useRouter()

const register = async () => {
  const res = await axios.post('http://localhost:5000/api/auth/register', {
    username: username.value,
    password: password.value,
    preferences: preferences.value
  })

  if (res.data.code === 200) {
    alert('注册成功！请登录')
    router.push('/login')
  } else {
    alert(res.data.msg)
  }
}
</script>

<style scoped>
.auth-container { max-width: 300px; margin: auto; padding: 40px 10px; }
input, button { display: block; width: 100%; margin: 10px 0; padding: 10px; }
.checkbox-group { display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0; }
</style>
