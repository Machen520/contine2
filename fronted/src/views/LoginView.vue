<template>
  <div class="auth-container">
    <h2>登录</h2>
    <form @submit.prevent="login">
      <input v-model="username" placeholder="用户名" required />
      <input v-model="password" type="password" placeholder="密码" required />
      <button type="submit">登录</button>
    </form>
    <p>还没有账号？<router-link to="/register">前往注册</router-link></p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const router = useRouter()

const login = async () => {
  const res = await axios.post('http://localhost:5000/api/auth/login', {
    username: username.value,
    password: password.value
  }, { withCredentials: true })

  if (res.data.code === 200) {
    localStorage.setItem('user_id', res.data.user_id)
    alert('登录成功！')
    router.push('/')
  } else {
    alert(res.data.msg)
  }
}
</script>

<style scoped>
.auth-container { max-width: 300px; margin: auto; padding: 40px 10px; }
input, button { display: block; width: 100%; margin: 10px 0; padding: 10px; }
</style>
