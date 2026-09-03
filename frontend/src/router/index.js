import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  { path: '/login', name: 'login', component: () => import('../views/LoginView.vue') },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/map',
    children: [
      { path: 'map', name: 'map', component: () => import('../views/MapView.vue') },
      { path: 'level/:id', name: 'quiz', component: () => import('../views/QuizView.vue') },
      { path: 'wrongbook', name: 'wrongbook', component: () => import('../views/WrongbookView.vue') },
      { path: 'stats', name: 'stats', component: () => import('../views/StatsView.vue') },
      { path: 'admin/chapters', name: 'admin-chapters', component: () => import('../views/admin/AdminChapters.vue'), meta: { admin: true } },
      { path: 'admin/levels', name: 'admin-levels', component: () => import('../views/admin/AdminLevels.vue'), meta: { admin: true } },
      { path: 'admin/questions', name: 'admin-questions', component: () => import('../views/admin/AdminQuestions.vue'), meta: { admin: true } },
      { path: 'admin/users', name: 'admin-users', component: () => import('../views/admin/AdminUsers.vue'), meta: { admin: true } }
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/map' }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const store = useUserStore()
  if (to.name !== 'login' && !store.isLogin) return { name: 'login' }
  if (to.name === 'login' && store.isLogin) return { name: 'map' }
  if (to.meta.admin && !store.isAdmin) return { name: 'map' }
  return true
})

export default router
