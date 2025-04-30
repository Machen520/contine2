<template>
  <nav class="navbar">
    <div class="nav-left">
      <router-link class="nav-logo" to="/">🏠 POI 推荐系统</router-link>
    </div>

    <div class="nav-right">
      <router-link to="/" class="nav-item">地图查询</router-link>
      <router-link to="/history" class="nav-item" v-if="userId">访问记录</router-link>
      <router-link to="/preferences" class="nav-item" v-if="userId">偏好设置</router-link>

      <template v-if="!userId">
        <router-link to="/login" class="nav-item">登录</router-link>
        <router-link to="/register" class="nav-item">注册</router-link>
      </template>

      <template v-else>
        <router-link to="/user" class="nav-item">欢迎您，{{ username }}</router-link>
        <button @click="logout" class="nav-item logout-btn">退出</button>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const userId = ref(null)
const username = ref('')
const router = useRouter()

onMounted(async () => {
  userId.value = localStorage.getItem('user_id')
  if (userId.value) {
    const res = await axios.get('http://localhost:5000/api/auth/userinfo', { withCredentials: true })
    if (res.data.code === 200) {
      username.value = res.data.username
    }
  }
})

const logout = async () => {
  await axios.post('http://localhost:5000/api/auth/logout', {}, { withCredentials: true })
  localStorage.removeItem('user_id')
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #409eff;
  color: white;
  padding: 10px 20px;
  font-size: 16px;
}
.nav-logo {
  font-weight: bold;
  color: white;
  text-decoration: none;
}
.nav-right {
  display: flex;
  gap: 15px;
}
.nav-item {
  color: white;
  text-decoration: none;
}
.logout-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
}
.logout-btn:hover {
  text-decoration: underline;
}
</style>
