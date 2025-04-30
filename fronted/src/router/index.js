import { createRouter, createWebHistory } from 'vue-router'
import MapView from '@/views/MapView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import PreferenceView from '@/views/PreferenceView.vue'
import VisitHistoryView from '@/views/VisitHistoryView.vue'
import UserInfoView from '@/views/UserInfoView.vue'

const routes = [
  { path: '/', name: 'Map', component: MapView },
  { path: '/login', name: 'Login', component: LoginView },
  { path: '/register', name: 'Register', component: RegisterView },
  { path: '/preferences', name: 'Preferences', component: PreferenceView },
  { path: '/history', name: 'History', component: VisitHistoryView },
  { path: '/user', name: 'UserInfo', component: UserInfoView }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
