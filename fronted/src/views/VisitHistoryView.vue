<template>
  <div class="history-page">
    <h2>我的访问记录</h2>
    <ul class="history-list">
      <li v-for="item in historyList" :key="item.visit_time" @click="focusOnMap(item)">
        <b>{{ item.name }}</b>（{{ item.category || '未知分类' }}）
        <br />
        <small>{{ item.visit_time }}</small>
      </li>
    </ul>
    <p v-if="!historyList.length">暂无访问记录</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const historyList = ref([])
const router = useRouter()

onMounted(async () => {
  const res = await axios.get('http://localhost:5000/api/user/history/list', {
    withCredentials: true
  })

  if (res.data.code === 200) {
    historyList.value = res.data.data
  } else if (res.data.code === 401) {
    alert('请先登录')
    router.push('/login')
  }
})

// 可选扩展：点击后聚焦到地图
function focusOnMap(item) {
  localStorage.setItem('focus_poi', JSON.stringify(item))
  router.push('/')
}
</script>

<style scoped>
.history-page {
  max-width: 600px;
  margin: auto;
  padding: 20px;
}
.history-list li {
  border-bottom: 1px solid #eee;
  padding: 10px 0;
  cursor: pointer;
}
.history-list li:hover {
  background: #f6f9ff;
}
</style>
