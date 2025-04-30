<template>
  <div class="poi-card" @click="onClick">
    <h3>{{ poi.name }}</h3>
    <p v-if="poi.description">{{ poi.description }}</p>
    <p v-if="poi.category">分类：{{ poi.category }}</p>
    <p v-if="poi.reason">推荐理由：{{ poi.reason }}</p>
    <p>评分：{{ poi.rating ? poi.rating.toFixed(1) : '暂无评分' }} ⭐</p>
    <p v-if="poi.distance !== undefined">距离：{{ poi.distance.toFixed(2) }} km</p>

    <!-- 打分模块 -->
    <div class="rating-bar">
      <span>我要打分：</span>
      <select v-model="selectedRating" @change="submitRating">
        <option disabled selected value>请选择</option>
        <option v-for="star in [5,4,3,2,1]" :key="star" :value="star">{{ star }} 星</option>
      </select>
    </div>

    <!-- 评论模块 -->
    <div class="comment-bar">
      <textarea v-model="newComment" placeholder="请输入你的评论..." rows="2"></textarea>
      <button @click="submitComment">提交评论</button>
    </div>

    <!-- 评论列表展示 -->
    <div v-if="comments.length > 0" class="comment-list">
      <h4>最新评论：</h4>
      <div v-for="(comment, index) in comments" :key="index" class="comment-item">
        <p>{{ comment.content }}</p>
        <small>时间：{{ comment.created_at }}</small>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// eslint-disable-next-line no-undef
const props = defineProps({
  poi: Object,
  onClick: Function
})

const selectedRating = ref()
const newComment = ref('')
const comments = ref([])

const submitRating = async () => {
  if (!selectedRating.value) return
  try {
    const res = await axios.post('http://localhost:5000/api/poi/rate', {
      poi_id: props.poi.id,
      rating: selectedRating.value
    }, { withCredentials: true })

    if (res.data.code === 200) {
      alert('打分成功！新评分：' + res.data.new_rating + ' ⭐️')
      location.reload() // 简单版，刷新页面查看新评分
    } else {
      alert('打分失败：' + res.data.msg)
    }
  } catch (e) {
    console.error('提交打分失败', e)
    alert('提交失败，请检查网络')
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) {
    alert('评论内容不能为空')
    return
  }
  try {
    const res = await axios.post('http://localhost:5000/api/poi/comment', {
      user_id: localStorage.getItem('user_id'),  // ✅ 用localStorage里拿user_id
      poi_id: props.poi.id,
      content: newComment.value
    }, { withCredentials: true })

    if (res.data.code === 200) {
      alert('评论成功！')
      newComment.value = ''
      loadComments()
    } else {
      alert('评论失败：' + res.data.msg)
    }
  } catch (e) {
    console.error('提交评论失败', e)
    alert('提交失败，请检查网络')
  }
}

const loadComments = async () => {
  try {
    const res = await axios.get(`http://localhost:5000/api/poi/comments?poi_id=${props.poi.id}`, {
      withCredentials: true
    })
    if (res.data.code === 200) {
      comments.value = res.data.data
    }
  } catch (e) {
    console.error('加载评论失败', e)
  }
}

onMounted(() => {
  loadComments()
})
</script>

<style scoped>
.poi-card {
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 12px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  transition: box-shadow 0.3s;
  cursor: pointer;
}
.poi-card:hover {
  box-shadow: 0 4px 10px rgba(0,0,0,0.2);
}
h3 {
  margin: 0 0 8px;
}
p {
  margin: 4px 0;
  font-size: 14px;
  color: #555;
}
.rating-bar {
  margin-top: 10px;
  font-size: 14px;
}
.rating-bar select {
  margin-left: 5px;
  padding: 3px 8px;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.comment-bar {
  margin-top: 10px;
}
.comment-bar textarea {
  width: 100%;
  padding: 5px;
  margin-bottom: 6px;
  border-radius: 6px;
  border: 1px solid #ccc;
}
.comment-bar button {
  padding: 5px 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.comment-bar button:hover {
  background-color: #45a049;
}

.comment-list {
  margin-top: 12px;
  background: #f9f9f9;
  padding: 10px;
  border-radius: 6px;
}
.comment-item {
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid #ddd;
}
</style>
