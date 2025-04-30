<template>
  <div class="map-page">
    <div id="mapContainer" class="map"></div>
    <div class="recommend-panel">
      <div class="controls">
        <button class="query-btn" @click="handleQuery">📍 查询当前位置推荐</button>

        <select v-model="searchRadius" class="control-select">
          <option value="1000">1公里</option>
          <option value="3000">3公里</option>
          <option value="5000">5公里</option>
          <option value="10000">10公里</option>
          <option value="20000">20公里</option>
        </select>

        <select v-model="selectedCategory" class="control-select">
          <option value="全部">全部</option>
          <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
        </select>

        <select v-model="sortBy" class="control-select">
          <option value="score">评分优先</option>
          <option value="distance">距离优先</option>
        </select>

        <input v-model="filterKeyword" placeholder="关键词搜索…" class="filter-input" />
      </div>

      <POICard
        v-for="poi in filteredPOIs"
        :key="poi.id"
        :poi="poi"
        :onClick="() => handleCardClick(poi)"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import axios from 'axios'
import POICard from '@/components/POICard.vue'

const map = ref(null)
const markers = ref([])
const poiList = ref([])
const categories = ref([''])
const selectedCategory = ref('全部')
const sortBy = ref('score')
const filterKeyword = ref('')
const searchRadius = ref(5000)

let lastLat = null
let lastLng = null
let moveTimer = null
let locationMarker = null
let isClickingPOICard = false  // 🔥 标记
const infoWindow = ref(null)

const setUserLocationMarker = (lng, lat) => {
  if (locationMarker) locationMarker.setMap(null)
  locationMarker = new window.AMap.Marker({
    position: [lng, lat],
    map: map.value,
    icon: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png',
    anchor: 'center',
    offset: new window.AMap.Pixel(0, 0)
  })
}

const updateMapMarkers = (pois, options = { fitView: false }) => {
  markers.value.forEach(m => m.marker.setMap(null))
  markers.value = []

  pois.forEach(poi => {
    const marker = new window.AMap.Marker({
      position: [poi.lng, poi.lat],
      map: map.value,
      title: poi.name,
      icon: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_r.png'
    })

    marker.on('click', () => {
      if (!infoWindow.value) {
        infoWindow.value = new window.AMap.InfoWindow({ offset: new window.AMap.Pixel(0, -30) })
      }
      infoWindow.value.setContent(`<b>${poi.name}</b><br/>${poi.description || '暂无'}<br/><i>${poi.reason}</i>`)
      infoWindow.value.open(map.value, marker.getPosition())
    })

    markers.value.push({ poiId: poi.id, marker })
  })

  if (options.fitView && markers.value.length > 0) {
    const allMarkerObjs = markers.value.map(m => m.marker)
    map.value.setFitView(allMarkerObjs, true, [60, 60, 60, 60])
  }
}

const handleQuery = () => {
  const geolocation = new window.AMap.Geolocation({
    enableHighAccuracy: true,
    timeout: 8000
  })

  geolocation.getCurrentPosition((status, result) => {
    if (status === 'complete') {
      const lat = result.position.lat
      const lng = result.position.lng
      lastLat = lat
      lastLng = lng

      map.value.setCenter([lng, lat])
      setUserLocationMarker(lng, lat)

      fetchAndUpdatePOIs(lat, lng, true)  // 初次查询时fitView
    } else {
      alert('定位失败，使用默认位置')
      const defaultLat = 41.79890
      const defaultLng = 123.35021
      lastLat = defaultLat
      lastLng = defaultLng

      map.value.setCenter([defaultLng, defaultLat])
      setUserLocationMarker(defaultLng, defaultLat)

      fetchAndUpdatePOIs(defaultLat, defaultLng, true)
    }
  })
}

const fetchAndUpdatePOIs = async (lat, lng, fitView = false) => {
  const { data } = await axios.post('http://localhost:5000/api/poi/recommend', {
    user_id: localStorage.getItem('user_id'),
    latitude: lat,
    longitude: lng,
    radius: searchRadius.value
  })

  if (data.code === 200) {
    poiList.value = data.data
    updateMapMarkers(filteredPOIs.value, { fitView })
  }
}

const handleCardClick = (poi) => {
  isClickingPOICard = true

  const target = markers.value.find(m => m.poiId === poi.id)
  if (target) {
    map.value.setZoomAndCenter(17, [poi.lng, poi.lat])
    if (!infoWindow.value) {
      infoWindow.value = new window.AMap.InfoWindow({ offset: new window.AMap.Pixel(0, -30) })
    }
    infoWindow.value.setContent(`<b>${poi.name}</b><br/>${poi.description || '暂无'}<br/><i>${poi.reason}</i>`)
    infoWindow.value.open(map.value, target.marker.getPosition())
  }

  setTimeout(() => {
    isClickingPOICard = false
  }, 2000)
}

const filteredPOIs = computed(() => {
  const keyword = filterKeyword.value.trim().toLowerCase()
  return poiList.value
    .filter(poi => {
      const matchCategory =
        selectedCategory.value === '全部' ||
        (poi.category && poi.category === selectedCategory.value)
      const matchKeyword =
        (poi.name && poi.name.toLowerCase().includes(keyword)) ||
        (poi.description && poi.description.toLowerCase().includes(keyword)) ||
        (poi.reason && poi.reason.toLowerCase().includes(keyword))
      return matchCategory && matchKeyword
    })
    .sort((a, b) => {
      return sortBy.value === 'score' ? b.score - a.score : a.distance - b.distance
    })
})

watch(filteredPOIs, (newList) => {
  updateMapMarkers(newList, { fitView: false })
})

onMounted(async () => {
  const catRes = await axios.get('http://localhost:5000/api/poi/categories')
  if (catRes.data.code === 200) {
    categories.value = catRes.data.data
  }

  AMapLoader.load({
    key: process.env.VUE_APP_AMAP_KEY,
    version: '2.0',
    plugins: ['AMap.Geolocation']
  }).then((amap) => {
    map.value = new amap.Map('mapContainer', {
      resizeEnable: true,
      zoom: 15
    })

    map.value.on('zoomend', () => {
      if (locationMarker) {
        locationMarker.setPosition([lastLng, lastLat])
      }
    })

    map.value.on('moveend', () => {
      if (isClickingPOICard) {
        console.log('点击POI卡片时，不触发moveend刷新')
        return
      }
      clearTimeout(moveTimer)
      moveTimer = setTimeout(() => {
        const center = map.value.getCenter()
        fetchAndUpdatePOIs(center.lat, center.lng, false)  // 移动后刷新但不fitView
      }, 500)
    })

    handleQuery()
  })
})
</script>

<style scoped>
.map-page {
  display: flex;
  height: 100vh;
}
.map {
  flex: 2;
}
.recommend-panel {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
  background-color: #f9f9f9;
}
.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 12px;
  align-items: center;
}
.query-btn {
  background: #4CAF50;
  color: white;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.query-btn:hover {
  background: #45a049;
}
.control-select {
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
  flex: none;
}
.filter-input {
  padding: 6px;
  border-radius: 6px;
  border: 1px solid #ccc;
  flex-grow: 1;
}
</style>
