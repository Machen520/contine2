<template>
  <div class="user-info-page">
    <h2>欢迎您，{{ username }}</h2>
    <ul class="nav-links">
      <li><router-link to="/preferences">🛠 修改偏好设置</router-link></li>
      <li><router-link to="/history">📜 查看访问记录</router-link></li>
    </ul>
    <button @click="logout">退出登录</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const username = ref('')
const router = useRouter()

onMounted(async () => {
  const res = await axios.get('http://localhost:5000/api/auth/userinfo', {
    withCredentials: true
  })
  if (res.data.code === 200) {
    username.value = res.data.username
  } else {
    alert('您尚未登录')
    router.push('/login')
  }
})

const logout = async () => {
  await axios.post('http://localhost:5000/api/auth/logout', {}, {
    withCredentials: true
  })
  localStorage.removeItem('user_id')
  alert('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.user-info-page {
  max-width: 400px;
  margin: auto;
  padding: 40px 10px;
  text-align: center;
}
.nav-links {
  list-style: none;
  padding: 0;
  margin: 20px 0;
}
.nav-links li {
  margin: 10px 0;
}
button {
  padding: 10px 20px;
  border: none;
  background: #e74c3c;
  color: white;
  border-radius: 8px;
  cursor: pointer;
}
</style>
