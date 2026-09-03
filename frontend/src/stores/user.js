import { defineStore } from 'pinia'
import http from '../api/http'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('lq_token') || '',
    user: JSON.parse(localStorage.getItem('lq_user') || 'null')
  }),
  getters: {
    isLogin: (s) => !!s.token,
    isAdmin: (s) => s.user?.role === 'admin'
  },
  actions: {
    saveAuth(data) {
      this.token = data.token
      this.user = data.user
      localStorage.setItem('lq_token', data.token)
      localStorage.setItem('lq_user', JSON.stringify(data.user))
    },
    sendCode(email) {
      return http.post('/auth/send-code', { email })
    },
    async register(email, password, code) {
      const data = await http.post('/auth/register', { email, password, code })
      this.saveAuth(data)
    },
    async login(email, password) {
      const data = await http.post('/auth/login', { email, password })
      this.saveAuth(data)
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('lq_token')
      localStorage.removeItem('lq_user')
    }
  }
})
